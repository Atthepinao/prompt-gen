# Nanobanana 系列模型 × 90年代日本动画赛璐璐风格提示词调研报告

> 调研日期：2026-04-28  
> 调研范围：NanoBanana / NanoBanana 2 / NanoBanana Pro（即 Google Gemini 2.5 Flash Image 模型）  
> 研究方向：90年代日本动画赛璐璐手绘风格角色生成提示词

---

## 一、背景说明

NanoBanana 系列模型是 Google Gemini 2.5 Flash Image（或早期的 Gemini 2.0 Flash Image）模型的社区昵称，并非独立的第三方扩散模型（如 Stable Diffusion 的 LoRA/Checkpoint），而是基于 Gemini 多模态推理引擎的原生生图能力。

与 Stable Diffusion 等扩散模型不同，NanoBanana Pro 的核心优势在于：
- 支持自然语言段落叙述，理解"意图"而非简单匹配标签
- 支持 JSON 结构化提示词，字段化定义各视觉维度
- 支持最多 14 张参考图，可指定每张图的参考维度（姿势 / 风格 / 背景）
- 内置角色一致性能力，适合角色资产批量产出

---

## 二、关键发现：90年代赛璐璐风格的核心提示关键词

### 2.1 视觉签名关键词（重要性排序）

这些是经过社区验证，最能精准触发 90 年代赛璐璐感的词汇，缺少任何一类都会导致结果向现代动画风格漂移：

| 维度 | 关键词（英文） | 说明 |
|------|--------------|------|
| **赛璐璐上色** | `cel-shaded with visible paint edge between light and shadow` | **最关键**，定义明暗过渡的硬边缘，缺失此标签会导致现代平滑渐变 |
| **线条质感** | `slightly thick hand-drawn linework with natural weight variation` | 模拟手绘墨线的粗细变化，区别于数字矢量线条 |
| **色彩风格** | `limited color palette, muted warm tones, vintage color grading` | 年代感限定色盘，避免现代饱和度过高 |
| **质感叠加** | `soft film grain texture, VHS analog noise` | 胶片/磁带颗粒感，模拟赛璐璐扫描质感 |
| **高光处理** | `hard-edge flat highlights on hair and eyes` | 眼睛和发丝的块状硬边高光，区别于现代柔和高光 |
| **画幅比例** | `4:3 aspect ratio` | 90 年代 CRT 广播比例，立刻锁定年代感 |
| **色彩轻微偏色** | `slight warm color cast, oversaturated warm tones` | 模拟 VHS 录制或早期数码采集的色偏 |

> **来源说明**：关键词有效性经 Kalon.ai、Medium、Civitai 社区等多源交叉验证。Kalon.ai 明确指出："`cel-shaded with visible paint edge`是区分真实90年代风格与加了滤镜的现代动画的最重要标签，定义了这个年代的视觉签名。"

---

## 三、可直接使用的提示词模板（分场景）

### 3.1 通用角色立绘（全身）

**来源：** https://www.kalon.ai/templates/90s-anime-prompts 和 https://medium.com/technology-hits/how-to-create-anime-art-in-nano-banana-pro-with-real-prompts-ffb440699081

```
best quality, masterpiece, 1990s anime style, 1girl, sharp angular facial features, large detailed eyes with multi-layered highlight reflections, slightly thick hand-drawn linework with natural weight variation, cel-shaded skin with visible paint edge between light and shadow zones, warm slightly muted color palette with limited saturation, hair rendered in blocky color sections with hard-edge highlights, soft film grain texture across entire frame, slight warm color cast, upper body composition, simple gradient background in warm tone, vintage anime production quality, nostalgic atmosphere, high resolution.
```

**负面提示词（建议同步添加）：**
```
modern anime style, digital art, clean vector lines, smooth gradient shading, 3D render, photorealistic
```

---

### 3.2 VHS 截图风格（场景感强）

**来源：** https://www.kalon.ai/templates/90s-anime-prompts

```
best quality, masterpiece, 90s anime VHS screencap, 1girl looking over shoulder, mid-conversation expression with mouth slightly open, slightly soft focus as if captured from analog video, visible horizontal scan lines at low opacity, subtle color bleed at high-contrast edges, warm oversaturated color cast, slight image softness simulating VHS resolution loss, 4:3 aspect ratio matching CRT television format, cel-shaded with flat color zones, thick hand-drawn outlines.
```

---

### 3.3 特定类型角色（魔法少女 / 90s TV 截图感）

**来源：** https://docs.mew.design/blog/gemini-nano-banana-pro-manga-prompts/

```
90s anime TV screenshot, a magical girl transforming, she has long flowing blonde hair with twin tails and large emerald green eyes, wearing a frilly pink dress with ribbons, soft pastel colors, vintage film grain, glowing ribbon effects, cel-shaded, starry background, nostalgic aesthetic.
```

---

### 3.4 赛博朋克 / 机师类角色（写实背景+赛璐璐角色）

**来源：** https://imaginewithrashid.com/23-gemini-nano-banana-pro-prompts-for-different-cartoon-styles/

```
Create a retro 90s anime style screenshot. The scene features a female pilot looking out a window at a rainy neon city. The image must include a VHS film grain effect, hand-painted background textures, and distinct high-contrast white highlights on the hair and eyes, using a muted color palette in a 4:3 aspect ratio.
```

---

### 3.5 角色设定图（Character Sheet）

**来源：** https://docs.mew.design/blog/gemini-nano-banana-pro-manga-prompts/ 和 https://civitai.com/articles/19327/nanobanana-prompting-guide

```
Anime character reference sheet showing front view, side view, and back view of [角色描述], flat colors, white background, clean line art, 1990s anime style, cel-shaded, thick outlines, limited color palette, vintage anime production quality. Include a close-up face expression chart at the bottom: happy, neutral, angry, surprised.
```

**角色描述示例（可替换方括号部分）：**
```
a teenage girl with short dark hair and large amber eyes, wearing a high school sailor uniform with red ribbon, carrying a worn schoolbag
```

---

### 3.6 JSON 结构化提示词格式（适用于最精细控制）

**来源：** https://zhuanlan.zhihu.com/p/1946483329441439808（知乎：Nano Banana 官方 Prompt 提示词教程）

JSON 格式是 NanoBanana Pro 官方推荐的提示词方式，能对各维度精确定义：

```json
{
  "shot": "full body portrait, slight upward angle, centered composition",
  "subject": "a 17-year-old anime girl with short dark hair, large expressive eyes with blocky white highlight, wearing school uniform",
  "environment": "simple gradient warm-tone background, no detailed scenery",
  "lighting": "flat ambient light with hard cel-shaded shadows, single directional light source from upper left",
  "camera": "equivalent to 85mm portrait lens, slight soft focus on edges",
  "color grade": "muted warm palette, limited saturation, slight warm color cast",
  "style": "1990s vintage Japanese anime, cel-shaded with hard paint edges, hand-drawn thick ink outlines with natural weight variation, film grain overlay",
  "quality": "vintage anime production quality, masterpiece",
  "negatives": "modern anime, digital clean lines, smooth gradients, 3D render, photorealistic"
}
```

---

## 四、进阶技巧

### 4.1 不要只写"90s anime"

社区测试（Kalon.ai 明确指出）：仅加入 `90s anime` 标签，结果只会产生轻微色彩偏移和颗粒感，**不会触发赛璐璐明暗边界、手绘线条等结构性视觉特征**。必须叠加 Section 2.1 中的关键词才能达到稳定效果。

### 4.2 迭代修改优于推倒重来

NanoBanana Pro 支持迭代描述指令：
- `"保持其他不变，把角色头发改成红色"`
- `"整体很好，给背景加上更强的胶片颗粒感"`
- `"线条再粗一些，更接近手绘墨线效果"`

### 4.3 使用参考图明确风格

当你有目标风格的参考帧（如某个动画截图），可以上传参考图并注明：

```
使用图A的角色设计风格，生成图B姿势的角色。风格：1990s cel-shaded anime。
```

NanoBanana Pro 支持最多 14 张参考图，每张图可单独指定用途。

### 4.4 写段落，而非堆标签

NanoBanana Pro 拥有强语言推理能力，**叙事性的自然语言描述**往往优于 Stable Diffusion 风格的"tag soup"写法：

❌ 不推荐（标签堆砌）：
```
1girl, anime, 90s, cel, retro, film grain, school uniform, brown hair
```

✅ 推荐（叙事描述）：
```
A 1990s Japanese anime-style portrait of a teenage girl in a sailor school uniform. She has short brown hair with a blocky white highlight, large expressive eyes with multi-layered reflections. The art style uses thick hand-drawn ink outlines, flat cel-shaded colors with visible hard edges between light and shadow, a muted warm color palette, and soft film grain texture throughout.
```

---

## 五、社区资源索引（含 90s 赛璐璐相关内容）

| 资源名称 | 类型 | 说明 | 链接 |
|---------|------|------|------|
| Kalon.ai 90s Anime Prompts | 模板库 | 最完整的 90s 赛璐璐提示词解析，含参数说明 | https://www.kalon.ai/templates/90s-anime-prompts |
| Civitai: Nano-Banana Prompting Guide | 社区指南 | 角色一致性、漫画版面、角色设定图模板 | https://civitai.com/articles/19327/nanobanana-prompting-guide |
| Civitai: Best Nano-Banana Use Cases | 社区用例 | 含角色一致性、风格迁移实际案例 | https://civitai.com/articles/18827/the-best-nano-banana-use-cases-with-prompts |
| Mew Design Docs: Manga Prompts | 提示词合集 | 含角色设定图、90s TV 截图等20+模板 | https://docs.mew.design/blog/gemini-nano-banana-pro-manga-prompts/ |
| ImagineWithRashid: 23 Cartoon Styles | 提示词合集 | 含明确的 retro 90s anime 风格提示词 | https://imaginewithrashid.com/23-gemini-nano-banana-pro-prompts-for-different-cartoon-styles/ |
| Medium: How to Create Anime Art | 教程 | 含完整的 90s 全身立绘提示词，分析各参数作用 | https://medium.com/technology-hits/how-to-create-anime-art-in-nano-banana-pro-with-real-prompts-ffb440699081 |
| GitHub: ZeroLu/awesome-nanobanana-pro | 提示词库 | 社区精选提示词，含多种动漫风格 | https://github.com/ZeroLu/awesome-nanobanana-pro |
| GitHub: YouMind-OpenLab 10000+ prompts | 提示词库 | 万级提示词库，多语言，含 16 语言分类 | https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts |
| GitHub: jau123 trending prompts | 热门提示词 | 来自 X/Twitter 的 1300+ 热门提示词，按互动排名 | https://github.com/jau123/nanobanana-trending-prompts |
| NanoBanana.im Blog: 43+ Best Prompts | 博客 | 含赛璐璐贴纸、卡通风格提示词 | https://nanobanana.im/blog/30-best-nano-banana-prompts-2025 |
| Civitai: NanoBanana-Anime-Style LoRA | 模型 | 将 NanoBanana Pro 风格蒸馏为 SD LoRA，可用于扩散模型流程 | https://civitai.com/models/2175780/nanobanana-anime-style |
| Dev.to: Nano-Banana Pro Prompting Guide | 官方指南 | Google AI 官方提示词策略文档 | https://dev.to/googleai/nano-banana-pro-prompting-guide-strategies-1h9n |
| 知乎：Nano Banana 官方 Prompt 教程 | 中文教程 | 含 JSON 结构格式、官方赛璐璐示例 | https://zhuanlan.zhihu.com/p/1946483329441439808 |
| 知乎：1000 个 Nano Banana Pro 提示词 | 中文合集 | 大规模提示词合集，含二次元风格 | https://zhuanlan.zhihu.com/p/1978947025841189918 |
| 知乎：疯传的像素级拆解提示词 | 角色设定图 | 角色设定图 + 服装拆解结构化写法 | https://zhuanlan.zhihu.com/p/1979513925860086705 |

---

## 六、结论与建议

### 核心问题诊断

目前角色资产生成不稳定，很可能是由于提示词只使用了泛化的年代标签（如 `90s anime`），而**没有针对赛璐璐生产工艺的具体视觉特征**进行细化描述。

### 建议优先尝试的改进方向

1. **必加组合**：`cel-shaded with visible paint edge` + `slightly thick hand-drawn linework with natural weight variation` + `limited warm muted color palette` + `4:3 aspect ratio`

2. **质感叠加**：`soft film grain texture` + `slight warm color cast`（模拟 VHS/胶片质感）

3. **明确排除现代风格**：在负面提示词中加入 `modern anime, smooth gradients, clean vector lines, digital art`

4. **切换到叙事段落**：将角色描述改写为完整的叙事段落，而非关键词堆叠

5. **角色一致性**：上传角色参考图，并明确说明 `使用此图的角色设计，保持服装和面部特征一致`

### 参考评价最高的单条提示词（来自 Kalon.ai）

```
best quality, masterpiece, 1990s anime style, 1girl, sharp angular facial features, large detailed eyes with multi-layered highlight reflections, slightly thick hand-drawn linework with natural weight variation, cel-shaded skin with visible paint edge between light and shadow zones, warm slightly muted color palette with limited saturation, hair rendered in blocky color sections with hard-edge highlights, soft film grain texture across entire frame, slight warm color cast, upper body composition, simple gradient background in warm tone, vintage anime production quality, nostalgic atmosphere, high resolution.
```

来源页面：https://www.kalon.ai/templates/90s-anime-prompts

---

*报告整理自：Kalon.ai、Civitai、docs.mew.design、imaginewithrashid.com、Medium、GitHub 社区、知乎专栏等多个公开来源。*
