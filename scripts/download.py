#!/usr/bin/env python3
'''视频下载脚本 - 支持 YouTube 和 B站，使用 yt-dlp 下载视频/音频和字幕'''

import argparse
import shutil
import subprocess
import sys
import os
import json
from pathlib import Path


def detect_platform(url: str) -> str:
    '''检测视频平台'''
    url = url.lower()
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'bilibili.com' in url or 'b23.tv' in url:
        return 'bilibili'
    else:
        return 'unknown'


def build_yt_dlp_command() -> list:
    '''解析 yt-dlp 调用方式：优先 PATH 中的 yt-dlp，否则回退到 python -m yt_dlp'''
    exe = shutil.which('yt-dlp')
    if exe:
        return [exe]
    # Windows 下 pip 安装后有时不在 PATH
    return [sys.executable, '-m', 'yt_dlp']


def download_video(url: str, output_dir: str, cookies_file: str = None,
                   cookies_from_browser: str = None, audio_only: bool = True) -> dict:
    '''
    下载视频/音频和字幕

    Returns:
        dict: 包含下载结果信息的字典
    '''
    platform = detect_platform(url)
    output_template = os.path.join(output_dir, '%(id)s.%(ext)s')

    # 基础命令
    cmd = build_yt_dlp_command()
    cmd.extend([
        '--no-playlist',               # 只下载单个视频，避免误入播放列表
        '--write-info-json',            # 保存视频信息
        '--write-subs',                 # 下载字幕
        '--write-auto-subs',            # 下载自动生成的字幕
        '--sub-langs', 'zh.*,zh-Hans,zh-Hant,en.*,en',  # 字幕语言优先级
        '--convert-subs', 'srt',        # 转换为 SRT 格式
        '-o', output_template,
    ])

    # 音频模式
    if audio_only:
        cmd.extend([
            '-x',                       # 提取音频
            '--audio-format', 'm4a',    # 音频格式
            '--audio-quality', '0',     # 最佳音质
        ])

    # Cookies 处理
    if cookies_from_browser:
        cmd.extend(['--cookies-from-browser', cookies_from_browser])
    elif cookies_file and os.path.exists(cookies_file):
        cmd.extend(['--cookies', cookies_file])

    # B站特殊处理
    if platform == 'bilibili':
        # 排除弹幕，只要字幕
        cmd[cmd.index('--sub-langs') + 1] = 'all,-danmaku'

    cmd.append(url)

    print('执行命令: ' + ' '.join(cmd))

    # 执行下载
    result = subprocess.run(cmd, capture_output=True, text=True)

    # 解析结果
    output_info = {
        'platform': platform,
        'success': result.returncode == 0,
        'output_dir': output_dir,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'files': []
    }

    # 查找生成的文件
    if result.returncode == 0:
        output_info['files'] = [str(f) for f in Path(output_dir).glob('*') if f.is_file()]

    return output_info


def main():
    parser = argparse.ArgumentParser(description='下载视频/音频和字幕')
    parser.add_argument('--url', required=True, help='视频 URL')
    parser.add_argument('--output', required=True, help='输出目录')
    parser.add_argument('--cookies', help='Cookies 文件路径')
    parser.add_argument('--cookies-from-browser', help='从浏览器读取 cookies (chrome/firefox/edge/safari/brave/opera/vivaldi)')
    parser.add_argument('--video', action='store_true', help='下载视频而非仅音频')

    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.output, exist_ok=True)

    result = download_video(
        url=args.url,
        output_dir=args.output,
        cookies_file=args.cookies,
        cookies_from_browser=args.cookies_from_browser,
        audio_only=not args.video
    )

    # 输出结果
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))

    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()