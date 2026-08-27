---
name: video-summarizer
description: 下载并总结 YouTube 和 B站（bilibili）视频内容。支持提取官方/AI 字幕、Whisper 语音转文字、生成结构化总结、方法归纳、互动数据卡、B站热评抓取、美妆爆款脚本拆解和基于视频内容的问答。抖音视频分析请配合专门的抖音研究 skill（如 daily-research）。当用户提供视频链接、要求总结视频、归纳视频方法、拆解爆款脚本或基于视频内容提问时自动触发。Cross-platform video download and summary skill for YouTube and Bilibili (Codex, Windows/macOS/Linux).
---

# 视频下载与总结工具（Video Summarizer）

适配 Codex 的视频总结 Skill，支持 Windows / macOS / Linux：下载并总结 YouTube 和 B站（bilibili）视频内容。

## 功能概述

1. **视频下载**：支持 YouTube 和 B站（bilibili.com）
2. **字幕提取**：优先获取官方字幕 / CC 字幕 / B站 AI 字幕
3. **语音转文字**：无字幕时使用 Whisper（本地或 API）转录
4. **内容分析**：总结、方法归纳、问答
5. **互动数据卡**：播放/点赞/投币/收藏/分享/弹幕/评论 + 转化率（B站）
6. **B站热评抓取**：热门评论 TOP 列表（公开接口）
7. **爆款拆解**：美妆等品类爆款视频脚本结构拆解模板

## 脚本位置

所有脚本都在本 skill 根目录的 `scripts/` 下（SKILL.md 所在目录即 skill 根目录，下文用 `{skillDir}` 表示）。
Windows 下用 `python` 命令（不是 `python3`）。

## 工作流程

### 步骤 1：依赖检查

先运行依赖检查脚本确认环境：

```bash
python {skillDir}/scripts/setup_check.py
```

缺失依赖时提示用户安装（Windows）：
- `pip install yt-dlp`（视频下载必需）
- ffmpeg（音频处理；Windows 可用 `winget install ffmpeg`）
- `pip install openai`（可选，Whisper API 转录，需要密钥）
- `pip install faster-whisper`（推荐，本地转录，无需 API key，CPU 可跑）
- `pip install openai-whisper`（可选，本地转录备选，依赖 torch 体积较大）

### 抖音链接注意（重要）

抖音视频的无水印下载、互动数据和评论获取与 B站/YouTube 机制不同（反爬、风控严），本 skill 的 yt-dlp 脚本对抖音支持不稳定。遇到抖音链接时：
1. 若环境已安装专门的抖音研究 skill（如 daily-research / konglong-research），直接走它的链路：下载+转写口播、TikHub 免费接口或浏览器登录态拉数据与评论、出研究卡片；
2. 转写文本拿到后，仍用 references/beauty_breakdown_template.md 做美妆爆款拆解（维度通用）；
3. 榜单/趋势数据用抖音官方工具：热点宝、巨量算数；
4. 不要用 download.py 硬下抖音链接，失败时改走上面的抖音链路。

### 步骤 2：下载视频 / 提取字幕

根据用户提供的 URL 执行下载：

```bash
python {skillDir}/scripts/download.py --url 'VIDEO_URL' --output '{skillDir}/output'
```

B站视频如需登录才能获取字幕，使用本机浏览器 cookies（Edge 用户用 edge）：

```bash
python {skillDir}/scripts/download.py --url 'VIDEO_URL' --output '{skillDir}/output' --cookies-from-browser edge
```

支持的浏览器：chrome, firefox, edge, safari, brave, opera, vivaldi。

### 步骤 3：提取字幕文本

```bash
python {skillDir}/scripts/extract_subtitles.py --input-dir '{skillDir}/output' --output '{skillDir}/output/transcript.txt'
```

### 步骤 4：语音转文字（无字幕时）

Whisper API 转录（需设置 OPENAI_API_KEY 环境变量）：

```bash
python {skillDir}/scripts/transcribe.py --input-dir '{skillDir}/output' --output '{skillDir}/output/transcript.txt' --timestamps
```

本地转录（无需 API key，推荐 faster-whisper）：

```bash
python {skillDir}/scripts/transcribe.py --input-dir '{skillDir}/output' --output '{skillDir}/output/transcript.txt' --local --model small --timestamps
```

**注意**：始终使用 `--timestamps` 参数，以便在总结中引用具体时间点。

### 步骤 5：生成互动数据卡（B站，可选但推荐）

下载时会自动保存 `*.info.json`，包含播放/点赞/投币/收藏/分享/弹幕/评论数据：

```bash
python {skillDir}/scripts/data_card.py --input-dir '{skillDir}/output' --output '{skillDir}/output/data_card.md'
```

数据卡包含原始互动数据 + 转化率（赞播比、投币比、收藏比、分享比、评论比、综合互动率）。B站视频会自动通过公开接口补全投币/收藏/分享/弹幕，做爆款分析时是重要的数据佐证。

### 步骤 6：抓取 B站热评（可选）

```bash
python {skillDir}/scripts/fetch_comments.py --url 'VIDEO_URL' --output '{skillDir}/output/comments.md'
```

也可以直接复用已下载的目录（自动读取 bvid）：

```bash
python {skillDir}/scripts/fetch_comments.py --input-dir '{skillDir}/output' --output '{skillDir}/output/comments.md'
```

公开接口通常无需登录；如触发风控，可稍后重试或提供 `--cookies cookies.txt`。

### 步骤 7：内容分析

用 Read 工具读取 `{skillDir}/output/transcript.txt`、`data_card.md`、`comments.md` 的内容，再根据用户需求分析。
分析类型与模板见 `references/prompt_templates.md`，平台注意事项见 `references/platform_notes.md`。

## 分析类型

### 1. 视频总结
- 视频主题和核心观点
- 主要内容分段概述
- 关键信息和数据
- 结论和要点

### 2. 方法归纳
- 识别视频中介绍的方法/技巧
- 整理为清晰的步骤列表
- 标注注意事项和前提条件

### 3. 问答模式
- 定位相关内容段落
- 提供准确的回答
- 引用视频中的原话（如适用）

### 4. 爆款脚本拆解（美妆/带货品类）

用户说「拆解这条美妆爆款」或「分析这条视频为什么爆」时，按以下流程：

1. 先跑步骤 2-6（下载 → 转录 → 数据卡 → 热评），拿到完整素材
2. 用 Read 读取 transcript.txt / data_card.md / comments.md
3. 按 `references/beauty_breakdown_template.md` 的结构逐项分析：
   - 前 3 秒钩子类型与原文
   - 痛点引入方式
   - 主体结构时间轴分段
   - 成分/功效话术
   - 产品植入方式（硬广 vs 种草）与植入点
   - 节奏情绪曲线、停留点设计
   - 结尾 CTA
   - 封面标题策略
   - 互动数据佐证（高互动点与脚本内容对应）
   - 可复用套路提炼 + 结论
4. 输出完整的拆解报告（Markdown）

## 自动保存总结

**重要**：完成分析后，必须将总结保存为 Markdown 文件。

保存位置：`~/video-summaries/`（Windows 为 `C:\Users\<用户名>\video-summaries\`）。可用环境变量 `VIDEO_SUMMARY_DIR` 覆盖。

文件命名格式：`YYYY-视频标题简述.md`

### Markdown 总结模板

```markdown
# 视频标题

> **视频来源**: [平台] - [频道名]
> **总结时间**: YYYY-MM-DD

---

## 核心观点
[一句话概括视频核心]

---

## 主要内容

### 一、[主题1] [时间戳范围]
- 要点1
- 要点2

### 二、[主题2] [时间戳范围]
- 要点1
- 要点2

---

## 关键要点/方法清单
- [ ] 要点1
- [ ] 要点2

---

*总结生成于 Codex Video Summarizer*
```

## 输出文件说明

下载完成后，`{skillDir}/output/` 目录将包含：
- `*.info.json` - 视频元信息（标题、描述、互动数据等）
- `*.srt` 或 `*.vtt` - 字幕文件（如有）
- `*.m4a` 或 `*.mp3` - 音频文件（用于转录）
- `transcript.txt` - 最终的文本转录
- `data_card.md` - 互动数据卡（步骤 5 生成）
- `comments.md` - B站热评（步骤 6 生成）

## 错误处理

- 视频无法下载 → 检查 URL 是否有效、是否地区限制或触发风控
- B站需要登录 → 使用 `--cookies-from-browser edge`
- Whisper API 调用失败 → 检查 OPENAI_API_KEY，或改用本地模式
- 音频文件过大 → 脚本会自动分段处理
- YouTube 在部分地区需要代理
- 热评接口风控/报错 → 稍后重试，或用 `--cookies cookies.txt`

## 清理

分析完成后，清理临时文件：

```bash
python {skillDir}/scripts/clean_output.py
```

## 示例用法

- 总结这个视频 https://www.youtube.com/watch?v=xxxxx
- 帮我归纳这个 B站教程的方法 https://www.bilibili.com/video/BVxxxxx
- 这个视频讲了什么？[URL]
- 视频里提到了哪些步骤？[URL]
- 拆解这条美妆爆款 https://www.bilibili.com/video/BVxxxxx
- 分析这条视频为什么爆，脚本结构是什么 [URL]
- 生成这个视频的数据卡和热评 [URL]