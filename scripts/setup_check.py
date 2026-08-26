#!/usr/bin/env python3
'''依赖检查脚本 - 验证所需工具是否已安装'''

import subprocess
import shutil
import sys
import json
import os


def check_command(cmd: str, version_flag: str = '--version') -> dict:
    '''检查命令是否可用'''
    path = shutil.which(cmd)
    if not path:
        return {'installed': False, 'command': cmd}

    try:
        result = subprocess.run([cmd, version_flag],
                                capture_output=True, text=True, timeout=5)
        version = result.stdout.strip() or result.stderr.strip()
        # 取第一行
        version = version.split('\n')[0][:100]
        return {'installed': True, 'command': cmd, 'path': path, 'version': version}
    except Exception:
        return {'installed': True, 'command': cmd, 'path': path, 'version': 'unknown'}


def check_python_package(package: str) -> dict:
    '''检查 Python 包是否已安装'''
    try:
        __import__(package)
        return {'installed': True, 'package': package}
    except ImportError:
        return {'installed': False, 'package': package}


def check_yt_dlp() -> dict:
    '''yt-dlp 可能以 python -m yt_dlp 形式存在'''
    result = check_command('yt-dlp', '--version')
    if result['installed']:
        return result
    try:
        __import__('yt_dlp')
        return {'installed': True, 'command': 'python -m yt_dlp', 'path': 'python', 'version': 'installed as python module'}
    except ImportError:
        return {'installed': False, 'command': 'yt-dlp'}


def main():
    results = {
        'commands': {},
        'python_packages': {},
        'all_ok': True,
        'missing': []
    }

    # 必需的命令行工具
    print('=== 视频总结 Skill 依赖检查 ===\n')

    print('必需的命令行工具:')
    ytdlp = check_yt_dlp()
    results['commands']['yt-dlp'] = ytdlp
    status = 'OK' if ytdlp['installed'] else 'MISSING'
    print('  yt-dlp: ' + status)
    if ytdlp.get('version'):
        print('    版本: ' + ytdlp['version'])
    if not ytdlp['installed']:
        results['all_ok'] = False
        results['missing'].append('yt-dlp')

    ffmpeg = check_command('ffmpeg', '-version')
    results['commands']['ffmpeg'] = ffmpeg
    status = 'OK' if ffmpeg['installed'] else 'MISSING'
    print('  ffmpeg: ' + status)
    if ffmpeg.get('version'):
        print('    版本: ' + ffmpeg['version'])
    if not ffmpeg['installed']:
        results['all_ok'] = False
        results['missing'].append('ffmpeg')

    print('\n可选的命令行工具:')
    ffprobe = check_command('ffprobe', '-version')
    results['commands']['ffprobe'] = ffprobe
    print('  ffprobe: ' + ('OK' if ffprobe['installed'] else '未安装'))

    # 必需的 Python 包
    print('\n必需的 Python 包:')
    for pkg in ['openai']:
        result = check_python_package(pkg)
        results['python_packages'][pkg] = result
        status = 'OK' if result['installed'] else 'MISSING'
        print('  ' + pkg + ': ' + status)
        if not result['installed']:
            results['all_ok'] = False
            results['missing'].append('python:' + pkg)

    print('\n可选的 Python 包 (本地转录):')
    for pkg in ['whisper']:
        result = check_python_package(pkg)
        results['python_packages'][pkg] = result
        print('  ' + pkg + ': ' + ('已安装' if result['installed'] else '未安装'))

    # 检查环境变量
    print('\n环境变量:')
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        print('  OPENAI_API_KEY: 已设置 (' + api_key[:8] + '...)')
        results['openai_api_key'] = True
    else:
        print('  OPENAI_API_KEY: 未设置 (Whisper API 需要)')
        results['openai_api_key'] = False

    # 总结
    print('\n=== 检查结果 ===')
    if results['all_ok']:
        print('所有必需依赖已安装!')
    else:
        print('缺少以下依赖: ' + ', '.join(results['missing']))
        print('\n安装命令 (Windows):')
        if 'yt-dlp' in results['missing']:
            print('  pip install yt-dlp')
        if 'ffmpeg' in results['missing']:
            print('  winget install ffmpeg   # 或到 https://ffmpeg.org 下载')
        if 'python:openai' in results['missing']:
            print('  pip install openai      # Whisper API 转录（可选，本地转录无需）')

    if not results['openai_api_key']:
        print('\n提示: 如果要使用 Whisper API 转录，请设置 OPENAI_API_KEY 环境变量。')

    # 输出 JSON 结果
    print('\n' + json.dumps(results, indent=2, ensure_ascii=False))

    sys.exit(0 if results['all_ok'] else 1)


if __name__ == '__main__':
    main()