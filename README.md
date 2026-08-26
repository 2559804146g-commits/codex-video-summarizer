# Codex Video Summarizer（视频下载与总结 Skill）

> 基于 [video-summarizer-skill](https://github.com/nothinginterested/video-summarizer-skill)（MIT）适配：面向 Codex，跨平台（重点支持 Windows）。

下载并总结 YouTube 和 B站视频内容的 Codex Skill：提取官方/AI 字幕，或 Whisper 语音转文字，生成结构化总结、方法归纳与问答。

## 功能特点

- 多平台支持：YouTube、哔哩哔哩（B站）
- 智能字幕提取：优先官方字幕 / CC 字幕 / B站 AI 字幕
- 语音转文字：Whisper（本地或 API）转录，带时间戳
- 结构化总结：自动生成 Markdown 视频总结
- 问答支持：基于视频内容问答

## 安装（Codex）

### 1. 安装依赖

```powershell
pip install yt-dlp
pip install openai            # 可选：Whisper API 转录
pip install openai-whisper    # 可选：本地转录（体积较大）
```

还需要 ffmpeg：Windows 可用 `winget install ffmpeg`，macOS 可用 `brew install ffmpeg`，Linux 用系统包管理器安装。

### 2. 安装 Skill

将本仓库复制到 Codex 的 skills 目录：

- Windows：`C:\Users\<用户名>\.codex\skills\video-summarizer`
- macOS / Linux：`~/.codex/skills/video-summarizer`

一键安装（本仓库自带脚本，自动复制到正确位置）：

```powershell
python install.py
```

安装后新开的 Codex 会话即可识别该 Skill。

### 3. 配置环境变量（可选）

Whisper API 转录需要 `OPENAI_API_KEY` 环境变量。

## 使用方法

在 Codex 中直接输入：

- 总结这个视频 https://www.bilibili.com/video/BVxxxxx
- 帮我归纳这个 B站教程的方法 https://www.bilibili.com/video/BVxxxxx
- 这个视频讲了什么？https://www.youtube.com/watch?v=xxxxx

自动流程：
1. 下载字幕/音频（yt-dlp）
2. 提取或转录文本
3. 生成结构化总结

## 目录结构

```
codex-video-summarizer/
├── SKILL.md              # Skill 核心定义
├── README.md             # 说明文档
├── LICENSE               # MIT 许可证
├── install.py            # 一键安装脚本
├── scripts/
│   ├── download.py       # 视频/字幕下载
│   ├── extract_subtitles.py  # 字幕解析
│   ├── transcribe.py     # Whisper 转录
│   ├── setup_check.py    # 依赖检查
│   ├── clean_output.py   # 跨平台清理
│   └── utils.py          # 工具函数
├── references/
│   ├── prompt_templates.md   # 总结模板
│   └── platform_notes.md     # 平台说明
└── output/               # 临时输出（已忽略）
```

## B站登录问题

B站部分视频（高清、部分字幕）需要登录：

- 方案 1：自动读取浏览器 cookies（Edge 用 edge）

```powershell
python scripts/download.py --url 'URL' --output output --cookies-from-browser edge
```

支持的浏览器：chrome, firefox, edge, safari, brave, opera, vivaldi

- 方案 2：手动导出 cookies.txt，使用 `--cookies` 参数

## 自定义总结存储位置

默认保存到 `~/video-summaries/`，可用环境变量 `VIDEO_SUMMARY_DIR` 覆盖。

## 与上游的差异

- 适配 Codex：SKILL.md 使用 Codex frontmatter
- Windows 支持：python 代替 python3，跨平台清理脚本
- 修复 b23.tv 短链接视频 ID 提取
- 下载脚本自动回退到 python -m yt_dlp
- 新增 install.py 一键安装到 Codex skills 目录
- 新增 scripts/clean_output.py 跨平台清理

## 依赖说明

| 依赖 | 用途 | 必需 |
|------|------|------|
| yt-dlp | 视频/字幕下载 | 是 |
| ffmpeg | 音频处理 | 是 |
| openai | Whisper API | 可选 |
| openai-whisper | 本地转录 | 可选 |

## License

MIT