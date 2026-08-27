# 使用说明（User Guide）

本 Skill 用于在 Codex 中快速总结 YouTube / B站视频：自动下载音频和字幕，必要时本地转写，最后生成结构化总结。升级版额外支持互动数据卡、B站热评抓取和美妆爆款脚本拆解。

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
- 拆解这条美妆爆款 [链接]（推荐给编导/内容岗作业）
- 生成这个视频的数据卡和热评 [链接]

Skill 会自动执行：
1. 下载音频和字幕（yt-dlp）
2. 有字幕 → 提取文本；无字幕 → 本地 Whisper 转写
3. 生成 Markdown 总结并自动保存（数据卡 / 热评 / 拆解按需生成）

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

## 四、互动数据卡（B站）

下载后会自动保存 `output/*.info.json`，包含播放/点赞/投币/收藏/分享/弹幕/评论数据。生成数据卡：

```powershell
python scripts/data_card.py --input-dir output --output output/data_card.md
```

数据卡含原始互动量 + 转化率：赞播比、投币比、收藏比、分享比、评论比、综合互动率。B站视频会自动通过公开接口补全投币/收藏/分享/弹幕。
用途：判断爆款「爆在哪」——收藏高说明工具性强，评论高说明话题性强，赞播比高说明内容质量被认可。

## 五、B站热评抓取

```powershell
python scripts/fetch_comments.py --input-dir output --output output/comments.md
```

或直接用链接：

```powershell
python scripts/fetch_comments.py --url 'https://www.bilibili.com/video/BVxxxxx' --output output/comments.md
```

公开接口通常无需登录。若提示风控，稍等再试，或导出 cookies.txt 后加 `--cookies cookies.txt`。

## 六、美妆爆款拆解（编导/内容岗）

面试编导、分析美妆爆款脚本时的推荐流程。先对 Codex 说：

```
拆解这条美妆爆款 https://www.bilibili.com/video/BVxxxxx
```

Skill 会自动完成：下载 → 转录 → 数据卡 → 热评 → 按 `references/beauty_breakdown_template.md` 拆解输出报告。

拆解报告包含：

- 前 3 秒钩子：反常识断言 / 痛点直击 / 悬念提问 / 结果展示
- 痛点引入：目标人群、情绪词、场景共鸣
- 主体结构：按时间轴分段，标注情绪强度
- 成分功效话术：成分名、浓度数字、作用机理、是否合规
- 产品植入：硬广 vs 软种草、植入位置、价格锚点
- 节奏情绪曲线：停留点、反转、弹幕密集处
- 结尾 CTA：关注 / 收藏 / 评论区 / 购物车
- 封面标题策略：大字文案、前后对比、标题套路
- 互动数据佐证：高互动点与脚本内容对应
- 可复用套路：脚本模板、话术金句、落地动作

## 七、B站视频需要登录怎么办

B站部分视频（高清画质、字幕）需要登录：

- 读取浏览器登录态：`--cookies-from-browser edge`（支持 chrome/firefox/edge/safari/brave/opera/vivaldi）
- 注意：**浏览器开着时可能读不到 cookie**，会报 `Could not copy Chrome cookie database`。关掉浏览器重试，或手动导出 cookies.txt 后用 `--cookies` 参数

## 八、常见问题

| 问题 | 解决办法 |
|------|----------|
| 说「总结视频」没反应 | 确认 Skill 已安装，并且是安装后新开的会话 |
| 下载失败 | 检查链接是否有效、网络能否访问该平台 |
| 转写结果不准 | 换更大模型（`--model small` 或 `medium`），中文加 `--language zh` |
| 转写很慢 | 用更小模型，或换 GPU 机器 |
| YouTube 打不开 | 需要代理 |
| 热评抓取失败/风控 | 稍后重试，或用 `--cookies cookies.txt` |

## 九、检查环境是否就绪

```powershell
python scripts/setup_check.py
```

输出 `all_ok: true` 即环境正常。

## 十、卸载

删除 Skill 目录即可：

```powershell
Remove-Item -Recurse -Force ~\.codex\skills\video-summarizer
```

---

*遇到问题可查看 [README.md](README.md) 或到仓库提交 Issue。*