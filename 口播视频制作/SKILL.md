# 口播视频制作

## 核心定位

把一篇文章/口播稿，配上语音克隆的口播音频，用 HyperFrames 制作动画画面，最终合成 MP4 视频。

**一句话**：文章 → 口播稿 → 克隆语音音频 → 动画画面 → MP4 视频。

---

## 依赖环境

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| **HyperFrames** | HTML + GSAP 动画 → 帧截图 → 视频 | npm install -g hyperframes |
| **小米 MiMo TTS API** | 语音克隆合成 | 需要 API Key |
| **FFmpeg** | 帧图片 + 音频 → MP4 | 系统自带或单独安装 |

---

## 输入与输出

**输入：**
- 一篇文章/口播稿（文字）
- 一段用户自己的录音（作为音色参考，wav 格式）

**输出：**
- MP4 视频（1920×1080，30fps）
- 口播稿（文字）

---

## 初始化（一次性）

首次使用时需要配置 TTS：

1. 询问用户选择 TTS 模型（默认小米 MiMo TTS）
2. 让用户提供 API Key 和 API URL
3. 让用户提供一段自己的录音文件（wav 格式，作为音色参考）
4. 记录配置，后续不需要重复设置

配置信息保存在项目目录的 `tts-config.json` 中：

```json
{
  "provider": "mimo",
  "api_base_url": "https://token-plan-cn.xiaomimimo.com/v1",
  "api_key": "tp-xxx",
  "model": "mimo-v2.5-tts-voiceclone",
  "reference_audio": "录音文件路径"
}
```

---

## 完整流程

### Step 1：口播稿准备

1. 用户提供原始文章/口播稿
2. Agent 根据需求决定是否压缩精简（**压缩是可选项**，不是必经步骤）
3. 将口播稿落盘为 `script.md`

**Checkpoint — 用户校对：**
- 展示口播稿给用户确认
- 用户校对修改后，才能进入下一步
- **未经用户确认，禁止进入 Step 2**

### Step 2：语音合成

1. 将口播稿按段落分段（灵活处理，自然段落或按内容主题分段）
2. 读取 `tts-config.json` 获取 TTS 配置
3. 逐段调用小米 MiMo TTS API 生成音频
4. 可选：每段配情绪指令（放在 user 消息中，自然语言描述语调/情绪）
5. 将所有分段音频拼接成完整 wav

**小米 MiMo TTS API 调用方式：**

```python
# 请求格式
POST {api_base_url}/chat/completions
Headers:
  Authorization: Bearer {api_key}
  Content-Type: application/json

Body:
{
  "model": "mimo-v2.5-tts-voiceclone",
  "messages": [
    {"role": "user", "content": "情绪/语调指令（可选）"},
    {"role": "assistant", "content": "要合成的文本"}
  ],
  "stream": false,
  "audio": {
    "format": "wav",
    "voice": "data:audio/wav;base64,{参考音频的base64编码}"
  }
}
```

**情绪指令示例：**

```python
INSTRUCTIONS = [
    "用自信、从容、温暖的语调开场，语速适中偏慢，声音沉稳有力量",
    "语速适中，重点词句稍作停顿，传达出重量感",
    "节奏明快一些，列举数据时语气肯定有力",
    "前半段沉稳有力，后半段语气加重、放慢，传达坚定感",
    "语气轻松实用，像在分享踩坑后的好方法",
    "真诚、坚定地收尾，最后一句语气上扬、温暖",
]
```

### Step 3：画面制作（依赖 HyperFrames）

1. 根据口播稿内容，设计 HTML + GSAP 动画页面
2. 画面内容与口播稿内容基本同步
3. 使用 HyperFrames 渲染出帧序列图片

**HyperFrames 渲染流程：**

```bash
# 创建项目
npx hyperframes init ./my-video --template=1920x1080

# 渲染视频
npx hyperframes render --output renders/video.mp4
```

**画面设计原则：**
- 每个内容段落对应一个画面场景
- 用 GSAP 动画让文字/图形逐步出现
- 风格统一（配色、字体、布局一致）
- 字号要大（标题 >= 80px，正文 >= 32px）
- 留白充足，画面不要塞满

### Step 4：合成视频（依赖 FFmpeg）

1. 用 FFmpeg 将帧序列图片 + 音频合并成 MP4
2. 验证视频质量
3. 交付 MP4 视频 + 口播稿

**FFmpeg 命令：**

```bash
ffmpeg -framerate 30 \
  -i frames/frame_%06d.jpg \
  -i narration.wav \
  -c:v libx264 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest -y \
  output.mp4
```

---

## 生存铁律

### 铁律 1：用户校对口播稿
- 口播稿必须经过用户校对确认后才能进入语音合成
- 未经确认，禁止调用 TTS API

### 铁律 2：画面内容与口播同步
- 画面展示的内容必须与当前口播的段落对应
- 不允许画面和口播讲的是完全不同的东西

### 铁律 3：先检查依赖
- 首次使用前检查：HyperFrames、FFmpeg 是否可用
- 检查 TTS 配置是否完整
- 缺少依赖时提供安装指引

### 铁律 4：中间文件管理
- 分段音频、帧图片等中间文件放在工作目录
- 最终 MP4 和口播稿放在用户指定的输出目录
- 不要把临时文件混在输出目录里

---

## 常见问题

**Q: 音频和画面不同步怎么办？**
A: 先生成音频，再根据音频时长调整画面动画的节奏。HyperFrames 的 duration 参数要与音频时长匹配。

**Q: 情绪指令没效果怎么办？**
A: 情绪指令放在 messages 的 user 角色中，用自然语言描述。如果效果不好，尝试更具体的指令（比如指定语速、停顿位置）。

**Q: 视频画质不好怎么办？**
A: HyperFrames 渲染时用 --quality high 参数。FFmpeg 编码时用 -crf 18（数值越小画质越高，默认 23）。

**Q: 口播稿太长怎么办？**
A: 先压缩精简到目标时长（中文约 4 字/秒）。压缩是可选项，根据需求决定。
