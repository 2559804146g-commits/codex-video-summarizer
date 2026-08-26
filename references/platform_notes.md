# 平台特殊说明

## B站 (bilibili.com)

### 访问限制
- 1080P 及以上清晰度需要登录
- 部分视频有地区限制
- 连续下载可能触发风控

### 字幕类型
- **人工字幕**：由 UP 主或官方添加
- **AI 字幕**：B站自动生成（中文）
- **弹幕**：不是字幕，下载时用 `--sub-langs all,-danmaku` 排除

### Cookies 获取方法

**方式 1：从浏览器自动读取（推荐）**

Windows / 跨平台：

```bash
python scripts/download.py --url 'URL' --output output --cookies-from-browser edge
```

支持的浏览器：chrome, firefox, edge, safari, brave, opera, vivaldi

**方式 2：手动导出 cookies 文件**

1. 在浏览器中登录 B站
2. 安装 Get cookies.txt 扩展（Chrome/Edge 均可）
3. 导出 cookies 到 `assets/cookies/bilibili.txt`
4. 使用：`--cookies 'assets/cookies/bilibili.txt'`

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| no video formats found | 更换 IP 或等待一段时间 |
| 字幕下载失败 | 视频可能没有字幕，改用 Whisper 转录 |
| 需要登录 | 使用 --cookies-from-browser 参数 |
| Cookie 数据库被锁定 | 关闭浏览器后重试，或手动导出 cookies.txt |
| 下载速度慢 | B站限流，建议使用 --limit-rate 参数 |

---

## YouTube

### 访问要求
- 大部分视频无需登录
- 年龄限制视频需要 cookies
- 部分地区可能需要代理

### 字幕类型
- **CC 字幕**：社区贡献或官方添加（质量最高）
- **自动字幕**：YouTube 自动生成（可能有错误）

### 语言优先级
默认下载顺序：
1. zh-Hans（简体中文）
2. zh-Hant（繁体中文）
3. zh（中文）
4. en（英文）

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| Video unavailable | 检查 URL 是否正确，或视频已被删除 |
| 无字幕 | 使用 Whisper 转录 |
| 下载失败 | 更新 yt-dlp：`pip install -U yt-dlp` |

---

## 通用建议

### 字幕质量判断
1. **人工字幕** > **AI 字幕** > **自动字幕**
2. 检查字幕文件名，带 `.zh` 或 `.en` 后缀的通常是人工字幕
3. 如果字幕错误太多，考虑用 Whisper 重新转录

### 音频转录建议
1. 优先使用 Whisper API（速度快、质量高）
2. 长视频（超过 1 小时）考虑使用本地模型节省 API 费用
3. 中文内容建议指定 `--language zh` 提高准确率

### 清理临时文件
分析完成后清理 output 目录：

```bash
python scripts/clean_output.py
```