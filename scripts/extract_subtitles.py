#!/usr/bin/env python3
'''字幕提取脚本 - 从 SRT/VTT/JSON 提取纯文本'''

import argparse
import re
import json
import sys
from pathlib import Path


def parse_srt(content: str) -> str:
    '''解析 SRT 格式字幕'''
    lines = []
    for block in content.strip().split('\n\n'):
        block_lines = block.strip().split('\n')
        if len(block_lines) >= 3:
            # 跳过序号和时间戳，取文本内容
            text_lines = block_lines[2:]
            text = ' '.join(text_lines)
            # 移除 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)
            if text.strip():
                lines.append(text.strip())
    return '\n'.join(lines)


def parse_vtt(content: str) -> str:
    '''解析 VTT 格式字幕'''
    lines = []
    # 跳过 WEBVTT 头部
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)

    for block in content.strip().split('\n\n'):
        block_lines = block.strip().split('\n')
        for line in block_lines:
            # 跳过时间戳行
            if '-->' in line or re.match(r'^\d+$', line.strip()):
                continue
            # 移除 HTML 标签和 VTT 样式标记
            text = re.sub(r'<[^>]+>', '', line)
            text = re.sub(r'\{[^}]+\}', '', text)
            if text.strip():
                lines.append(text.strip())
    return '\n'.join(lines)


def parse_json_subtitle(content: str) -> str:
    '''解析 JSON 格式字幕（B站格式）'''
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return ''

    lines = []

    # 尝试不同的 JSON 结构
    if isinstance(data, dict):
        if 'body' in data:
            for item in data['body']:
                if isinstance(item, dict) and 'content' in item:
                    lines.append(item['content'])
        elif 'subtitles' in data:
            for item in data['subtitles']:
                if isinstance(item, dict) and 'content' in item:
                    lines.append(item['content'])
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and 'content' in item:
                lines.append(item['content'])
            elif isinstance(item, str):
                lines.append(item)

    return '\n'.join(lines)


def find_subtitle_files(directory: str) -> list:
    '''在目录中查找字幕文件'''
    path = Path(directory)
    patterns = ['*.srt', '*.vtt', '*.json']

    files = []
    for pattern in patterns:
        for f in path.glob(pattern):
            # 排除 info.json 文件
            if not f.name.endswith('.info.json'):
                files.append(f)

    return sorted(files)


def extract_subtitles(input_dir: str, output_path: str) -> dict:
    '''从目录中提取字幕文本'''
    subtitle_files = find_subtitle_files(input_dir)

    if not subtitle_files:
        return {'success': False, 'error': '未找到字幕文件', 'files_checked': input_dir}

    # 优先使用中文字幕
    selected_file = None
    for f in subtitle_files:
        name = f.name.lower()
        if 'zh' in name or 'chinese' in name or 'chs' in name or 'cht' in name:
            selected_file = f
            break

    # 如果没有中文字幕，使用第一个找到的
    if selected_file is None:
        selected_file = subtitle_files[0]

    print('使用字幕文件: ' + str(selected_file))

    content = selected_file.read_text(encoding='utf-8', errors='ignore')
    suffix = selected_file.suffix.lower()

    if suffix == '.srt':
        text = parse_srt(content)
    elif suffix == '.vtt':
        text = parse_vtt(content)
    elif suffix == '.json':
        text = parse_json_subtitle(content)
    else:
        return {'success': False, 'error': '不支持的字幕格式: ' + suffix}

    if not text.strip():
        return {'success': False, 'error': '字幕文件为空或解析失败'}

    # 写入输出文件
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8')

    return {
        'success': True,
        'input': str(selected_file),
        'output': str(output),
        'char_count': len(text),
        'line_count': len(text.split('\n'))
    }


def main():
    parser = argparse.ArgumentParser(description='从字幕文件提取纯文本')
    parser.add_argument('--input-dir', required=True, help='包含字幕文件的目录')
    parser.add_argument('--output', required=True, help='输出文本文件路径')

    args = parser.parse_args()
    result = extract_subtitles(args.input_dir, args.output)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()