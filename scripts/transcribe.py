#!/usr/bin/env python3
'''语音转文字脚本 - 支持 OpenAI Whisper API、faster-whisper（本地，推荐）和 openai-whisper（本地）'''

import argparse
import os
import json
import sys
from pathlib import Path


def find_audio_files(directory: str) -> list:
    '''在目录中查找音频文件'''
    path = Path(directory)
    patterns = ['*.m4a', '*.mp3', '*.wav', '*.webm', '*.opus', '*.ogg']

    files = []
    for pattern in patterns:
        files.extend(path.glob(pattern))

    return sorted(files)


def get_file_size_mb(file_path: str) -> float:
    '''获取文件大小（MB）'''
    return os.path.getsize(file_path) / (1024 * 1024)


def split_audio(input_path: str, output_dir: str, max_size_mb: int = 24) -> list:
    '''
    将大音频文件分割成小段
    OpenAI Whisper API 限制 25MB
    '''
    import subprocess

    file_size = get_file_size_mb(input_path)

    if file_size <= max_size_mb:
        return [input_path]

    print('音频文件 %.1fMB 超过限制，正在分割...' % file_size)

    # 使用 ffmpeg 分割
    # 估算每段时长（假设 128kbps）
    duration_per_chunk = int(max_size_mb * 8 / 0.128)  # 秒

    output_pattern = os.path.join(output_dir, 'chunk_%03d.m4a')

    cmd = [
        'ffmpeg', '-i', input_path,
        '-f', 'segment',
        '-segment_time', str(duration_per_chunk),
        '-c', 'copy',
        output_pattern,
        '-y'
    ]

    subprocess.run(cmd, capture_output=True)

    chunks = sorted(Path(output_dir).glob('chunk_*.m4a'))
    return [str(c) for c in chunks]


def transcribe_with_api(audio_path: str, api_key: str, language: str = None) -> str:
    '''使用 OpenAI Whisper API 转录（需要 OPENAI_API_KEY）'''
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError('请安装 openai 包: pip install openai')

    client = OpenAI(api_key=api_key)

    with open(audio_path, 'rb') as audio_file:
        kwargs = {
            'model': 'whisper-1',
            'file': audio_file,
            'response_format': 'text'
        }
        if language:
            kwargs['language'] = language

        transcript = client.audio.transcriptions.create(**kwargs)

    return transcript


def format_timestamp(seconds: float) -> str:
    '''将秒数转换为 MM:SS 格式'''
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return '%02d:%02d' % (minutes, secs)


def transcribe_faster_whisper(audio_path: str, model: str, timestamps: bool, language: str) -> str:
    '''使用 faster-whisper 本地转录（无需 API key，CPU 即可，推荐）'''
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError('请安装 faster-whisper 包: pip install faster-whisper')

    print('加载 faster-whisper 模型: ' + model + ' （首次运行会自动下载）')
    model_obj = WhisperModel(model, device='cpu', compute_type='int8')

    print('转录音频: ' + audio_path)
    kwargs = {'vad_filter': True}
    if language:
        kwargs['language'] = language
    segments, info = model_obj.transcribe(audio_path, **kwargs)

    if timestamps:
        # 输出带时间戳的格式
        lines = []
        for seg in segments:
            ts = format_timestamp(seg.start)
            text = seg.text.strip()
            if text:
                lines.append('[' + ts + '] ' + text)
        return '\n'.join(lines)
    else:
        return ' '.join(seg.text.strip() for seg in segments)


def transcribe_openai_whisper(audio_path: str, model: str, timestamps: bool) -> str:
    '''使用 openai-whisper 本地转录（无需 API key，依赖 torch）'''
    try:
        import whisper
    except ImportError:
        raise ImportError('请安装 openai-whisper 包: pip install openai-whisper')

    print('加载 Whisper 模型: ' + model)
    model_obj = whisper.load_model(model)

    print('转录音频: ' + audio_path)
    result = model_obj.transcribe(audio_path)

    if timestamps and 'segments' in result:
        # 输出带时间戳的格式
        lines = []
        for seg in result['segments']:
            ts = format_timestamp(seg['start'])
            text = seg['text'].strip()
            if text:
                lines.append('[' + ts + '] ' + text)
        return '\n'.join(lines)
    else:
        return result['text']


def transcribe_with_local(audio_path: str, model: str, timestamps: bool,
                          language: str = None, engine: str = 'auto') -> str:
    '''
    本地转录：auto 模式优先使用 faster-whisper，其次 openai-whisper
    '''
    if engine == 'faster-whisper':
        return transcribe_faster_whisper(audio_path, model, timestamps, language)

    if engine == 'whisper':
        return transcribe_openai_whisper(audio_path, model, timestamps)

    # auto：优先 faster-whisper（无需 torch，体积小、CPU 快）
    try:
        return transcribe_faster_whisper(audio_path, model, timestamps, language)
    except ImportError:
        pass

    try:
        return transcribe_openai_whisper(audio_path, model, timestamps)
    except ImportError:
        raise ImportError('未安装本地转录引擎。推荐安装: pip install faster-whisper（无需 OpenAI key）')


def transcribe(input_dir: str, output_path: str, api_key: str = None,
               local: bool = False, model: str = 'small', language: str = None,
               timestamps: bool = False, engine: str = 'auto') -> dict:
    '''
    转录音频文件

    Args:
        input_dir: 包含音频文件的目录
        output_path: 输出文本路径
        api_key: OpenAI API key（API 模式需要）
        local: 是否使用本地模型
        model: 本地模型名称
        language: 语言代码（可选）
        timestamps: 是否输出时间戳
        engine: 本地引擎 auto/faster-whisper/whisper
    '''
    audio_files = find_audio_files(input_dir)

    if not audio_files:
        return {'success': False, 'error': '未找到音频文件，目录: ' + input_dir}

    # 使用第一个音频文件
    audio_path = audio_files[0]
    print('使用音频文件: ' + str(audio_path))

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    transcripts = []

    try:
        if local:
            # 本地模式（无需 OpenAI key）
            text = transcribe_with_local(str(audio_path), model, timestamps,
                                         language=language, engine=engine)
            transcripts.append(text)
        else:
            # API 模式
            if not api_key:
                api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                return {'success': False, 'error': 'OPENAI_API_KEY 未设置。没有密钥时请使用 --local 参数（本地转写，无需密钥）'}

            # 检查是否需要分割
            chunks = split_audio(str(audio_path), str(output_dir))

            for i, chunk in enumerate(chunks):
                print('转录片段 %d/%d: %s' % (i + 1, len(chunks), chunk))
                text = transcribe_with_api(chunk, api_key, language)
                transcripts.append(text)

            # 清理临时分割文件
            for chunk in chunks:
                if 'chunk_' in chunk:
                    try:
                        os.remove(chunk)
                    except OSError:
                        pass

        # 合并转录结果
        full_text = '\n'.join(transcripts)

        # 写入输出文件
        Path(output_path).write_text(full_text, encoding='utf-8')

        return {
            'success': True,
            'input': str(audio_path),
            'output': output_path,
            'char_count': len(full_text),
            'mode': 'local' if local else 'api',
            'engine': engine if local else 'api'
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='语音转文字（无需 OpenAI key 时使用 --local）')
    parser.add_argument('--input-dir', required=True, help='包含音频文件的目录')
    parser.add_argument('--output', required=True, help='输出文本文件路径')
    parser.add_argument('--api-key', help='OpenAI API key')
    parser.add_argument('--local', action='store_true', help='使用本地模型（无需 API key）')
    parser.add_argument('--model', default='small', help='本地模型名称 (tiny/base/small/medium/large-v3/turbo)')
    parser.add_argument('--language', help='语言代码（如 zh, en）')
    parser.add_argument('--timestamps', action='store_true', help='输出带时间戳的格式')
    parser.add_argument('--engine', default='auto', choices=['auto', 'faster-whisper', 'whisper'],
                        help='本地引擎：auto 自动选择（推荐 faster-whisper）')

    args = parser.parse_args()

    result = transcribe(
        input_dir=args.input_dir,
        output_path=args.output,
        api_key=args.api_key,
        local=args.local,
        model=args.model,
        language=args.language,
        timestamps=args.timestamps,
        engine=args.engine
    )

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()