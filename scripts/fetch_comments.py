#!/usr/bin/env python3
'''抓取 B站视频热门评论（公开接口，通常无需登录；数据较密集时可能触发风控）'''

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/124.0.0.0 Safari/537.36'
)

VIEW_API = 'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
REPLY_API = 'https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=1&pn={pn}&ps={ps}'


def make_opener(cookies_file=None):
    '''构造 urllib opener，可选附带 Netscape 格式 cookies.txt'''
    if not cookies_file or not Path(cookies_file).exists():
        return urllib.request.build_opener()

    import http.cookiejar
    jar = http.cookiejar.MozillaCookieJar(cookies_file)
    jar.load(ignore_discard=True, ignore_expires=True)
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def fetch_json(url, opener):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    with opener.open(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))


def get_video_info(bvid, opener):
    '''通过 web-interface/view 接口获取 aid / title / owner'''
    data = fetch_json(VIEW_API.format(bvid=bvid), opener)
    if data.get('code') != 0:
        raise RuntimeError('获取视频信息失败(code=%s): %s' % (data.get('code'), data.get('message')))
    d = data['data']
    return {
        'aid': d.get('aid'),
        'title': d.get('title', '未知'),
        'owner': (d.get('owner') or {}).get('name', '未知'),
        'view_count': d.get('stat', {}).get('view', 0)
    }


def format_time(ts):
    '''Unix 时间戳 -> YYYY-MM-DD'''
    try:
        return time.strftime('%Y-%m-%d', time.localtime(int(ts)))
    except (TypeError, ValueError):
        return '未知'


def fetch_hot_comments(aid, opener, limit=20):
    '''抓取热门评论（sort=1），返回评论列表'''
    pn = 1
    ps = min(limit, 20)
    collected = []

    while len(collected) < limit:
        url = REPLY_API.format(aid=aid, pn=pn, ps=ps)
        data = fetch_json(url, opener)
        if data.get('code') != 0:
            raise RuntimeError('评论接口返回错误(code=%s): %s' % (data.get('code'), data.get('message')))

        replies = (data.get('data') or {}).get('replies') or []
        if not replies:
            break

        for r in replies:
            member = r.get('member') or {}
            collected.append({
                'uname': member.get('uname', '匿名'),
                'like': int(r.get('like') or 0),
                'rcount': int(r.get('rcount') or 0),
                'ctime': format_time(r.get('ctime')),
                'message': (r.get('content') or {}).get('message', '')
            })
            if len(collected) >= limit:
                break

        pn += 1
        time.sleep(0.5)  # 温和限速，避免触发风控

    return collected


def build_markdown(video, comments):
    lines = []
    lines.append('# B站热门评论')
    lines.append('')
    lines.append('- **视频**：' + video['title'])
    lines.append('- **UP主**：' + video['owner'])
    lines.append('- **播放量**：' + str(video.get('view_count', 0)))
    lines.append('- **评论数**：' + str(len(comments)))
    lines.append('')
    lines.append('## 热评 Top ' + str(len(comments)))
    lines.append('')

    if not comments:
        lines.append('（该视频暂无公开评论）')
        lines.append('')
        return '\n'.join(lines)

    for i, c in enumerate(comments, 1):
        lines.append(str(i) + '. **' + c['uname'] + '**'
                     + '（赞 ' + str(c['like'])
                     + ' · 回复 ' + str(c['rcount'])
                     + ' · ' + c['ctime'] + '）')
        lines.append('')
        lines.append('   > ' + c['message'].replace('\n', '\n   > '))
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='抓取 B站热门评论')
    parser.add_argument('--url', help='B站视频链接（bilibili.com 或 b23.tv）')
    parser.add_argument('--bvid', help='BV 号（如 BV1xx411c7BF）')
    parser.add_argument('--input-dir', help='已有下载输出目录（自动读取 bvid）')
    parser.add_argument('--cookies', help='Netscape 格式 cookies.txt（可选，风控时使用）')
    parser.add_argument('--limit', type=int, default=20, help='抓取热评数量（默认 20）')
    parser.add_argument('--output', help='输出 Markdown 文件路径（缺省打印到终端）')

    args = parser.parse_args()

    bvid = args.bvid
    if not bvid and args.url:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from utils import extract_video_id
        video_id = extract_video_id(args.url)
        if video_id and video_id.startswith('BV'):
            bvid = video_id
        else:
            print('无法从 URL 解析 BV 号: ' + args.url, file=sys.stderr)
            sys.exit(1)

    if not bvid and args.input_dir:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from utils import get_bilibili_ids
        ids = get_bilibili_ids(args.input_dir)
        if ids and ids.get('bvid'):
            bvid = ids['bvid']
        else:
            print('输入目录中未找到 bvid，请用 --url 或 --bvid 指定。', file=sys.stderr)
            sys.exit(1)

    if not bvid:
        parser.error('请提供 --url / --bvid / --input-dir 之一')

    try:
        opener = make_opener(args.cookies)
        video = get_video_info(bvid, opener)
        print('已获取视频: ' + video['title'] + '（UP主: ' + video['owner'] + '）', file=sys.stderr)
        comments = fetch_hot_comments(video['aid'], opener, limit=args.limit)
        md = build_markdown(video, comments)

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            Path(args.output).write_text(md, encoding='utf-8')
            print('评论已保存: ' + args.output)
        else:
            print(md)

    except Exception as e:
        print('抓取失败: ' + str(e), file=sys.stderr)
        print('提示：若提示风控/需要登录，可稍后重试，或用 --cookies 提供 cookies.txt。', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()