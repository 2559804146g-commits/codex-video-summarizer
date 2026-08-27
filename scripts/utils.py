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


def format_duration(seconds) -> str:
    '''格式化时长'''
    seconds = int(seconds or 0)
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
        'duration_seconds': int(info.get('duration') or 0),
        'uploader': info.get('uploader', '未知'),
        'upload_date': info.get('upload_date', '未知'),
        'view_count': int(info.get('view_count') or 0),
        'description': info.get('description', '')[:500],  # 截取前 500 字符
        'platform': detect_video_platform(info.get('webpage_url', ''))
    }


def to_int(value):
    '''安全转 int，失败返回 0'''
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def compute_engagement_metrics(view_count, like_count, coin_count,
                               favorite_count, share_count, danmaku_count,
                               reply_count) -> dict:
    '''
    根据互动原始值计算转化率

    - 各互动量原始值（播放/点赞/投币/收藏/分享/弹幕/评论）
    - 各转化率（占播放量的比例，如赞播比）
    - total_interactions 互动总量、interaction_rate 综合互动率
    播放量为 0 时转化率为 None。
    '''
    view_count = to_int(view_count)
    like_count = to_int(like_count)
    coin_count = to_int(coin_count)
    favorite_count = to_int(favorite_count)
    share_count = to_int(share_count)
    danmaku_count = to_int(danmaku_count)
    reply_count = to_int(reply_count)

    def ratio(part, total):
        if total <= 0:
            return None
        return round(part / total, 4)

    total_interactions = (like_count + coin_count + favorite_count
                          + share_count + danmaku_count + reply_count)

    return {
        'view_count': view_count,
        'like_count': like_count,
        'coin_count': coin_count,
        'favorite_count': favorite_count,
        'share_count': share_count,
        'danmaku_count': danmaku_count,
        'reply_count': reply_count,
        'like_view_ratio': ratio(like_count, view_count),
        'coin_view_ratio': ratio(coin_count, view_count),
        'favorite_view_ratio': ratio(favorite_count, view_count),
        'share_view_ratio': ratio(share_count, view_count),
        'comment_view_ratio': ratio(reply_count, view_count),
        'danmaku_view_ratio': ratio(danmaku_count, view_count),
        'total_interactions': total_interactions,
        'interaction_rate': ratio(total_interactions, view_count)
    }


def get_engagement_metrics(directory: str) -> dict:
    '''从 info.json 读取互动数据并计算转化率'''
    info = get_video_info(directory)
    if not info:
        return None

    return compute_engagement_metrics(
        info.get('view_count'),
        info.get('like_count'),
        info.get('coin_count'),
        info.get('favorite_count'),
        info.get('share_count'),
        info.get('danmaku_count'),
        info.get('reply_count', info.get('comment_count'))
    )


def get_bilibili_ids(directory: str) -> dict:
    '''从 info.json 提取 B站视频的 aid / bvid / cid（用于评论接口）'''
    info = get_video_info(directory)
    if not info:
        return None

    raw_id = info.get('id')
    bvid = info.get('bvid')
    if not bvid:
        # yt-dlp 的 B站 info.json 中 id 字段就是 BV 号
        if isinstance(raw_id, str) and raw_id.startswith('BV'):
            bvid = raw_id
        else:
            extracted = extract_video_id(info.get('webpage_url', ''))
            if extracted and extracted.startswith('BV'):
                bvid = extracted

    aid = None
    if isinstance(raw_id, int):
        aid = raw_id

    return {
        'aid': aid,
        'bvid': bvid,
        'cid': info.get('cid')
    }


BILIBILI_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/124.0.0.0 Safari/537.36'
)


def fetch_bilibili_stat(bvid: str, timeout: int = 15) -> dict:
    '''
    通过 B站公开接口获取完整互动统计（含投币/收藏/分享/弹幕）

    返回 stat 数字 + aid/bvid/cid；失败返回 None。
    '''
    import urllib.request
    url = 'https://api.bilibili.com/x/web-interface/view?bvid=' + bvid
    req = urllib.request.Request(url, headers={'User-Agent': BILIBILI_USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

    if data.get('code') != 0:
        return None

    d = data.get('data') or {}
    stat = d.get('stat') or {}
    return {
        'view_count': stat.get('view'),
        'like_count': stat.get('like'),
        'coin_count': stat.get('coin'),
        'favorite_count': stat.get('favorite'),
        'share_count': stat.get('share'),
        'danmaku_count': stat.get('danmaku'),
        'reply_count': stat.get('reply'),
        'aid': d.get('aid'),
        'bvid': d.get('bvid'),
        'cid': d.get('cid')
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