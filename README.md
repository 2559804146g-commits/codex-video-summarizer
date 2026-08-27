# Codex Video Summarizer（视频下载与总结 Skill）

> 基于 [video-summarizer-skill](https://github.com/nothinginterested/video-summarizer-skill)（MIT）适配：面向 Codex，跨平台（重点支持 Windows）。

下载并总结 YouTube 和 B站视频内容的 Codex Skill：提取官方/AI 字幕，或 Whisper 语音转文字，生成结构化总结、方法归纳与问答；支持互动数据卡、B站热评抓取和美妆爆款脚本拆解。

> 📖 **详细使用说明见 [USAGE.md](USAGE.md)**（安装、触发方式、无密钥转写、美妆拆解、常见问题）

## 功能特点

- 多平台支持：YouTube、哔哩哔哩（B站）
- 智能字幕提取：优先官方字幕 / CC 字幕 / B站 AI 字幕
- 语音转文字：Whisper（本地或 API）转录，带时间戳，无需 OpenAI 密钥
- 结构化总结：自动生成 Markdown 视频总结
- 问答支持：基于视频内容问答
- 互动数据卡：播放/点赞/投币/收藏/分享/弹幕/评论 + 转化率（赞播比等）
- B站热评抓取：公开接口获取热门评论 TOP
- 爆款拆解：美妆等品类爆款视频脚本结构拆解模板（面试编导/内容岗可用）

## 安装（Codex）

### 1. 安装依赖

```powershell
pip install yt-dlp
pip install faster-whisper    # 推荐：本地转录，无需 API key，CPU 可跑
pip install openai            # 可选：Whisper API 转录（需要密钥）
pip install openai-whisper    # 可选：本地转录备选（依赖 torch 体积较大）
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

没有 OpenAI 密钥时，本地转录（--local + faster-whisper）即可，完全不需要密钥。

Whisper API 转录需要 `OPENAI_API_KEY` 环境变量。

## 使用方法

在 Codex 中直接输入：

- 总结这个视频 https://www.bilibili.com/video/BVxxxxx
- 帮我归纳这个 B站教程的方法 https://www.bilibili.com/video/BVxxxxx
- 这个视频讲了什么？https://www.youtube.com/watch?v=xxxxx
- 拆解这条美妆爆款 https://www.bilibili.com/video/BVxxxxx（自动生成数据卡+热评+脚本拆解）
- 分析这条视频为什么爆，脚本结构是什么 [链接]

自动流程：
1. 下载字幕/音频（yt-dlp）
2. 提取或转录文本
3. 生成结构化总结 / 数据卡 / 热评 / 爆款拆解

## 目录结构

```
codex-video-summarizer/
├── SKILL.md              # Skill 核心定义
├── README.md             # 说明文档
├── USAGE.md              # 详细使用说明
├── LICENSE               # MIT 许可证
├── install.py            # 一键安装脚本
├── scripts/
│   ├── download.py       # 视频/字幕下载
│   ├── extract_subtitles.py  # 字幕解析
│   ├── transcribe.py     # Whisper 转录（本地无需密钥）
│   ├── data_card.py      # 互动数据卡（新增）
│   ├── fetch_comments.py # B站热评抓取（新增）
│   ├── setup_check.py    # 依赖检查
│   ├── clean_output.py   # 跨平台清理
│   └── utils.py          # 工具函数（含转化率计算）
├── references/
│   ├── prompt_templates.md       # 总结模板
│   ├── platform_notes.md         # 平台说明
│   └── beauty_breakdown_template.md  # 美妆爆款拆解模板（新增）
└── output/               # 临时输出（已忽略）
```

## 进阶：美妆爆款拆解

适合面试编导/内容岗位的作业或日常对标分析：

```powershell
# 1. 下载 + 转录 + 数据卡 + 热评
python scripts/download.py --url 'URL' --output output
python scripts/transcribe.py --input-dir output --output output/transcript.txt --local --model small --timestamps
python scripts/data_card.py --input-dir output --output output/data_card.md
python scripts/fetch_comments.py --input-dir output --output output/comments.md

# 2. 让 Codex 按模板拆解
# 说：拆解这条美妆爆款，参考 references/beauty_breakdown_template.md
```

拆解维度：前 3 秒钩子、痛点引入、成分功效话术、产品植入点（硬广 vs 种草）、节奏情绪曲线、结尾 CTA、封面标题策略、互动数据佐证、可复用套路。

## B站登录问题

B站部分视频（高清、部分字幕）需要登录：

- 方案 1：自动读取浏览器 cookies（Edge 用 edge）

```powershell
python scripts/download.py --url 'URL' --output output --cookies-from-browser edge
```

支持的浏览器：chrome, firefox, edge, safari, brave, opera, vivaldi

注意：浏览器正在运行时，cookie 数据库可能被锁定导致读取失败，请先关闭浏览器重试，或改用方案 2。

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
- 新增互动数据卡与转化率计算（utils.get_engagement_metrics + scripts/data_card.py）
- 新增 B站热评抓取（scripts/fetch_comments.py，公开接口）
- 新增美妆爆款拆解模板（references/beauty_breakdown_template.md）

## 依赖说明

| 依赖 | 用途 | 必需 |
|------|------|------|
| yt-dlp | 视频/字幕下载 | 是 |
| ffmpeg | 音频处理 | 是 |
| faster-whisper | 本地转录（推荐，无需密钥） | 可选 |
| openai | Whisper API（需要密钥） | 可选 |
| openai-whisper | 本地转录（备选） | 可选 |

## License

MIT