#!/usr/bin/env python3
'''一键安装本 Skill 到 Codex 的 skills 目录（Windows / macOS / Linux）。

用法: python install.py
'''

import shutil
from pathlib import Path


def main():
    src = Path(__file__).resolve().parent
    dest = Path.home() / '.codex' / 'skills' / 'video-summarizer'

    print('源目录: ' + str(src))
    print('目标目录: ' + str(dest))

    if src == dest:
        print('已经在目标位置，无需复制。')
        return

    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns('.git', 'output', '__pycache__')
    )
    print('安装完成。新开的 Codex 会话即可使用 video-summarizer skill。')

    out = src / 'output'
    if out.exists():
        print('提示: 源目录中存在 output 临时文件，可用 scripts/clean_output.py 清理。')


if __name__ == '__main__':
    main()