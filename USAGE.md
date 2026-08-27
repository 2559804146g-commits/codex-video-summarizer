# 使用说明（User Guide）

本 Skill 用于在 Codex 中快速总结 YouTube / B站视频：自动下载音频和字幕，必要时本地转写，最后生成结构化总结。

## 一、快速开始

### 1. 安装依赖

```powershell
pip install yt-dlp
pip install faster-whisper
```

需要 ffmpeg：Windows 用 `winget install ffmpeg`，macOS 用 `brew install ffmpeg`，Linux 用系统包管理器安装。

### 2. 安装 Skill

在仓库目录执行：

```powershell
python install.py
```

或者手动把整个仓库复制到 `C:\Users\<用户名>\.codex\skills\video-summarizer`（macOS / Linux 为 `~/.codex/skills/video-summarizer`）。

### 3. 新开一个 Codex 会话

安装后需要**新开的会话**才能识别该 Skill。

## 二、在 Codex 中使用

直接对 Codex 说一句话，附上视频链接即可：

- 总结这个视频 https://www.bilibili.com/video/BVxxxxxxxxxx
- 帮我归纳这个 B站教程的方法 https://www.bilibili.com/video/BVxxxxxxxxxx
- 这个视频讲了什么？https://www.youtube.com/watch?v=xxxxx
- 视频里提到了哪些步骤？[链接]

Skill 会自动执行：
1. 下载音频和字幕（yt-dlp）
2. 有字幕 → 提取文本；无字幕 → 本地 Whisper 转写
3. 生成 Markdown 总结并自动保存

### 总结保存位置

默认 `~/video-summaries/`（Windows 为 `C:\Users\<用户名>\video-summaries\`）。
可用环境变量 `VIDEO_SUMMARY_DIR` 修改保存目录。

## 三、没有 OpenAI 密钥怎么转写

本地转写完全免费、无需任何密钥。首次运行时 faster-whisper 会自动下载模型（约 75MB 到 1.5GB，取决于模型大小），之后离线可用。

| 模型 | 体积 | 速度 | 中文精度 |
|------|------|------|----------|
| tiny | ~75MB | 最快 | 一般 |
| base | ~145MB | 快 | 尚可 |
| small | ~484MB | 中等 | 推荐 |
| medium | ~1.5GB | 较慢 | 更好 |

手动指定模型和语言：

```powershell
python scripts/transcribe.py --input-dir output --output output/transcript.txt --local --model small --language zh --timestamps
```

## 四、B站视频需要登录怎么办

B站部分视频（高清画质、字幕）需要登录：

- 读取浏览器登录态：`--cookies-from-browser edge`（支持 chrome/firefox/edge/safari/brave/opera/vivaldi）
- 注意：**浏览器开着时可能读不到 cookie**，会报 `Could not copy Chrome cookie database`。关掉浏览器重试，或手动导出 cookies.txt 后用 `--cookies` 参数

## 五、常见问题

| 问题 | 解决办法 |
|------|----------|
| 说「总结视频」没反应 | 确认 Skill 已安装，并且是安装后新开的会话 |
| 下载失败 | 检查链接是否有效、网络能否访问该平台 |
| 转写结果不准 | 换更大模型（`--model small` 或 `medium`），中文加 `--language zh` |
| 转写很慢 | 用更小模型，或换 GPU 机器 |
| YouTube 打不开 | 需要代理 |

## 六、检查环境是否就绪

```powershell
python scripts/setup_check.py
```

输出 `all_ok: true` 即环境正常。

## 七、卸载

删除 Skill 目录即可：

```powershell
Remove-Item -Recurse -Force ~\.codex\skills\video-summarizer
```

---

*遇到问题可查看 [README.md](README.md) 或到仓库提交 Issue。*