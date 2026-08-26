#!/usr/bin/env python3
'''共用工具函数'''

import re
import json
from pathlib import Path


def detect_video_platform(url: str) -> str:
    '''检测视频平台'''
    url = url.lower()
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'bilibili.com' in url or 'b23.tv' in url:
        return 'bilibili'
    else:
        return 'unknown'


def extract_video_id(url: str) -> str:
    '''从 URL 提取视频 ID（支持 b23.tv 短链接）'''
    platform = detect_video_platform(url)

    if platform == 'youtube':
        # youtube.com/watch?v=VIDEO_ID
        match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        # youtu.be/VIDEO_ID
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)

    elif platform == 'bilibili':
        # bilibili.com/video/BVxxx
        match = re.search(r'/video/(BV[a-zA-Z0-9]+)', url)
        if match:
            return match.group(1)
        # bilibili.com/video/avxxx
        match = re.search(r'/video/av(\d+)', url)
        if match:
            return 'av' + match.group(1)
        # b23.tv 短链接：路径最后一段通常是 BV id 或纯数字 av 号
        match = re.search(r'b23\.tv/([A-Za-z0-9]+)', url)
        if match:
            candidate = match.group(1)
            if candidate.startswith('BV'):
                return candidate
            if candidate.isdigit():
                return 'av' + candidate

    return None


def find_subtitle_files(directory: str) -> list:
    '''在目录中查找字幕文件'''
    path = Path(directory)
    patterns = ['*.srt', '*.vtt', '*.json', '*.ass']

    files = []
    for pattern in patterns:
        for f in path.glob(pattern):
            # 排除 info.json 文件
            if not f.name.endswith('.info.json'):
                files.append(f)

    return sorted(files)


def find_audio_files(directory: str) -> list:
    '''在目录中查找音频文件'''
    path = Path(directory)
    patterns = ['*.m4a', '*.mp3', '*.wav', '*.webm', '*.opus', '*.ogg']

    files = []
    for pattern in patterns:
        files.extend(path.glob(pattern))

    return sorted(files)


def get_video_info(directory: str) -> dict:
    '''读取视频信息文件'''
    path = Path(directory)
    info_files = list(path.glob('*.info.json'))

    if not info_files:
        return None

    with open(info_files[0], 'r', encoding='utf-8') as f:
        return json.load(f)


def format_duration(seconds: int) -> str:
    '''格式化时长'''
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return '%d:%02d:%02d' % (hours, minutes, secs)
    else:
        return '%d:%02d' % (minutes, secs)


def get_video_metadata(directory: str) -> dict:
    '''获取视频元数据摘要'''
    info = get_video_info(directory)
    if not info:
        return None

    return {
        'title': info.get('title', '未知'),
        'duration': format_duration(info.get('duration', 0)),
        'duration_seconds': info.get('duration', 0),
        'uploader': info.get('uploader', '未知'),
        'upload_date': info.get('upload_date', '未知'),
        'view_count': info.get('view_count', 0),
        'description': info.get('description', '')[:500],  # 截取前 500 字符
        'platform': detect_video_platform(info.get('webpage_url', ''))
    }


if __name__ == '__main__':
    # 测试
    test_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtu.be/dQw4w9WgXcQ',
        'https://www.bilibili.com/video/BV1xx411c7BF',
        'https://b23.tv/BV1xx411c7BF',
        'https://b23.tv/123456'
    ]

    for url in test_urls:
        print('URL: ' + url)
        print('  平台: ' + detect_video_platform(url))
        print('  ID: ' + str(extract_video_id(url)))
        print()