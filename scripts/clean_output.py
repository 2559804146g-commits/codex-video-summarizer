#!/usr/bin/env python3
'''跨平台清理脚本：删除本 skill 的 output 临时目录'''

import shutil
from pathlib import Path


def main():
    base = Path(__file__).resolve().parent.parent
    out = base / 'output'
    if out.exists():
        shutil.rmtree(out)
        print('已清理: ' + str(out))
    else:
        print('输出目录不存在，无需清理: ' + str(out))


if __name__ == '__main__':
    main()