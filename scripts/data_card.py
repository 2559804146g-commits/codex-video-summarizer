#!/usr/bin/env python3
'''生成视频数据卡：从 info.json 读取播放/互动数据并计算转化率，输出 Markdown'''

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import (get_video_info, get_engagement_metrics,
                   compute_engagement_metrics, fetch_bilibili_stat,
                   format_duration, detect_video_platform)


def format_number(value):
    '''将数字格式化为 万/亿'''
    if value is None:
        return 'N/A'
    value = float(value)
    if value >= 100000000:
        return '%.2f亿' % (value / 100000000)
    if value >= 10000:
        return '%.1f万' % (value / 10000)
    return '%.0f' % value


def format_ratio(value):
    '''将比率格式化为百分比'''
    if value is None:
        return 'N/A'
    return '%.2f%%' % (value * 100)


def format_upload_date(value):
    '''YYYYMMDD -> YYYY-MM-DD'''
    if not value or value == '未知':
        return '未知'
    value = str(value)
    if len(value) == 8 and value.isdigit():
        return '%s-%s-%s' % (value[:4], value[4:6], value[6:8])
    return value


def enrich_bilibili_metrics(info, metrics):
    '''B站 info.json 缺少投币/收藏/分享/弹幕时，用公开接口补全'''
    raw_id = info.get('id')
    bvid = info.get('bvid')
    if not bvid and isinstance(raw_id, str) and raw_id.startswith('BV'):
        bvid = raw_id
    if not bvid:
        return metrics

    stat = fetch_bilibili_stat(bvid)
    if not stat:
        return metrics

    return compute_engagement_metrics(
        stat.get('view_count'),
        stat.get('like_count'),
        stat.get('coin_count'),
        stat.get('favorite_count'),
        stat.get('share_count'),
        stat.get('danmaku_count'),
        stat.get('reply_count')
    )


def build_data_card(directory, enrich=True):
    '''生成数据卡 Markdown 文本，找不到 info.json 时返回 None'''
    info = get_video_info(directory)
    if not info:
        return None

    metrics = get_engagement_metrics(directory)
    if metrics is None:
        return None

    enriched = False
    if enrich:
        platform = detect_video_platform(info.get('webpage_url', ''))
        if platform == 'bilibili':
            new_metrics = enrich_bilibili_metrics(info, metrics)
            if new_metrics != metrics:
                metrics = new_metrics
                enriched = True

    lines = []
    lines.append('# 视频数据卡')
    lines.append('')
    lines.append('> 由 codex-video-summarizer 生成（数据来源：yt-dlp info.json'
                 + (' + B站公开接口' if enriched else '') + '）')
    lines.append('')
    lines.append('## 基本信息')
    lines.append('')
    lines.append('- **标题**：' + str(info.get('title', '未知')))
    lines.append('- **UP主/频道**：' + str(info.get('uploader', '未知')))
    lines.append('- **发布时间**：' + format_upload_date(info.get('upload_date', '未知')))
    lines.append('- **时长**：' + format_duration(info.get('duration', 0)))
    lines.append('- **平台**：' + str(info.get('extractor_key', info.get('webpage_url', '未知'))))
    lines.append('')

    lines.append('## 互动数据')
    lines.append('')
    lines.append('| 指标 | 数值 |')
    lines.append('|------|------|')
    lines.append('| 播放量 | ' + format_number(metrics['view_count'])
                 + '（' + str(metrics['view_count']) + '） |')
    lines.append('| 点赞 | ' + format_number(metrics['like_count']) + ' |')
    lines.append('| 投币 | ' + format_number(metrics['coin_count']) + ' |')
    lines.append('| 收藏 | ' + format_number(metrics['favorite_count']) + ' |')
    lines.append('| 分享 | ' + format_number(metrics['share_count']) + ' |')
    lines.append('| 弹幕 | ' + format_number(metrics['danmaku_count']) + ' |')
    lines.append('| 评论 | ' + format_number(metrics['reply_count']) + ' |')
    lines.append('| 互动总量 | ' + format_number(metrics['total_interactions']) + ' |')
    lines.append('')

    lines.append('## 转化率（占播放量）')
    lines.append('')
    lines.append('| 指标 | 比率 | 参考值 |')
    lines.append('|------|------|--------|')
    lines.append('| 赞播比 | ' + format_ratio(metrics['like_view_ratio'])
                 + ' | 视频号/短视频通常 >5%，长视频 2-5% |')
    lines.append('| 投币比 | ' + format_ratio(metrics['coin_view_ratio'])
                 + ' | 优质干货通常 >1% |')
    lines.append('| 收藏比 | ' + format_ratio(metrics['favorite_view_ratio'])
                 + ' | 收藏高说明工具属性强 |')
    lines.append('| 分享比 | ' + format_ratio(metrics['share_view_ratio'])
                 + ' | 分享高说明社交传播强 |')
    lines.append('| 评论比 | ' + format_ratio(metrics['comment_view_ratio'])
                 + ' | 评论高说明争议/话题性强 |')
    lines.append('| 弹幕比 | ' + format_ratio(metrics['danmaku_view_ratio'])
                 + ' | B站互动氛围指标 |')
    lines.append('| 综合互动率 | ' + format_ratio(metrics['interaction_rate'])
                 + ' | 越高说明内容粘性越强 |')
    lines.append('')

    desc = info.get('description', '')
    if desc:
        lines.append('## 简介/描述')
        lines.append('')
        lines.append(str(desc)[:500])
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='生成视频数据卡（互动数据 + 转化率）')
    parser.add_argument('--input-dir', required=True, help='包含 info.json 的输出目录')
    parser.add_argument('--output', help='输出 Markdown 文件路径（缺省打印到终端）')
    parser.add_argument('--no-enrich', action='store_true',
                        help='关闭 B站公开接口补全（默认自动补全投币/收藏/分享/弹幕）')

    args = parser.parse_args()

    card = build_data_card(args.input_dir, enrich=not args.no_enrich)
    if card is None:
        print('未找到 info.json，请先运行下载脚本。', file=sys.stderr)
        sys.exit(1)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(card, encoding='utf-8')
        print('数据卡已保存: ' + args.output)
    else:
        print(card)


if __name__ == '__main__':
    main()