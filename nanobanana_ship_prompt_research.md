# Nanobanana 系列 × 80/90 年代日式 OVA 太空飞船提示词调研报告

> 调研日期：2026-04-28
> 模型范围：Nano Banana / Nano Banana 2 / Nano Banana Pro（即 Gemini 2.5 Flash Image / Gemini 3 Pro Image）
> 应用方向：全舰飞船（capital ship、carrier、frigate、fighter）四视图设定图
> 目标美学：1985–1995 日本 OVA 年代「那个年头动画里的资产」
> 姊妹文档：`nanobanana_90s_anime_cel_research.md`（角色赛璐璐风格调研）

---

## 一、TL;DR — 不稳定的根因与最关键的三条

读完 25+ 篇英文/中文社区文章、官方 prompting guide、GitHub awesome 列表与 X/Reddit 案例后，对当前 `core/ship_generator.py` 的输出不稳定，归因如下：

1. **Prompt 范式不匹配**：当前 prompt 是按 Stable Diffusion / Midjourney 思路写的「全大写小标题 + NEGATIVE 段 + tag soup」。Nano Banana 是一台**语言推理引擎**，它要的是叙述段落，不是结构化指令清单。
2. **指令稀释（semantic dilution）**：Nano Banana 对 prompt 的**前 ~50 词权重最高**。当前飞船 prompt 经常 800–1500 token，前面塞满 layout / negative / 三幕作曲规则，真正描述「这艘船长什么样」的 SUBJECT DESCRIPTION 被推到中段，话语权被冲淡。
3. **设计师真名 + 作品真名 = 双重风险**：Nano Banana Pro 在 2025 年底起对动漫风格 + 知名 IP 的安全过滤显著加强。`Kazutaka Miyatake / Shoji Kawamori / Junya Ishigaki` 这些日式机设师名字识别度本就不高（远不如西方画家、摄影师），而把他们和 anime style 一起用，反而提高被静默降级或换成「无关复古飞船」的概率。

**最关键的三条改进**（详见第六、七章）：

- **把"NEGATIVE 段"全部改写成正向描述**。Nano Banana 不支持显式 negative prompt，写 `NO X, NO Y` 反而可能让 X/Y 出现。
- **把"by Kazutaka Miyatake"换成他风格的具体几何描述**（"layered hull greebles, dreadnought-scale armored superstructure stacks…"）。设计师的 signature 字段已经有这种描述，直接用，**不要再带名字**。
- **整个 prompt 切到 200–400 词的叙述段落**，把 SUBJECT 放在最前面 ~50 词内。当前的 7 个全大写章节合并为 3–4 个自然段。

---

## 二、Nano Banana 与 SD/Midjourney 的核心差异（飞船场景下尤其重要）

| 维度 | SD / Midjourney 习惯 | Nano Banana 实际偏好 |
|------|---------------------|---------------------|
| **prompt 风格** | 关键词逗号堆砌 | 叙述性自然段落 |
| **理想长度** | 可以 500+ token | **100–300 词最佳，>1000 词性能下降** |
| **首词权重** | 比较平均 | **前 ~50 词权重最大**，主体必须前置 |
| **NEGATIVE prompt** | 显式独立段 | **没有 native 支持**，要写成正向语义 |
| **全大写 SECTION 标题** | 有时有用 | **基本无效**，不如直接写自然段 |
| **重复强调** | 有时有用 | **稀释主指令**，反而降低稳定性 |
| **JSON 结构化输入** | 不行 | **官方推荐方式**，比纯文本提升约 24% 精准度 |
| **质量增强词**（masterpiece, 8K, ultra-detailed） | 有时有用 | **基本无效**，挤占首 50 词权重 |
| **作品/IP 名** | 通常有效 | **Anime 风格下高风险**，可能触发 PROHIBITED_CONTENT |
| **设计师真名** | 看名气 | **西方艺术家>日本机设师**，后者识别极不稳定 |

> 关键论文级共识：[Apiyi Blog «停止夸张式提示词» ](https://help.apiyi.com/en/stop-hyperbolic-prompts-nano-banana-2-gpt-image-2-guide-en.html) 总结："Nano Banana 2 时代要瘦身，把 SD 思路丢掉。"

---

## 三、80/90 年代 OVA 飞船「那个时代感」拆解

「那个年头的资产」这种气质，在视觉上由几组高度具体的特征组成。Nano Banana 不能凭一个 `OVA style` 标签复现，必须显式拼出来：

### 3.1 媒介与上色（最关键，缺一不可）

| 维度 | 高效关键词 | 说明 |
|------|----------|------|
| **媒介本体** | `hand-painted production cel artwork`, `traditional cel animation` | 区别于 3D 渲染感最重要的一句 |
| **上色边界** | `cel-shaded with hard-edged shadow boundaries, one or two flat shadow tones per surface` | 区分赛璐璐 vs 现代柔光 |
| **大面积过渡** | `subtle airbrushed gradient transitions only within the largest armor faces` | OVA 旗舰里的"喷枪轻轻吹一层"特征 |
| **线稿** | `bold black ink linework on silhouette edges, finer ink lines for panel work and rivets, line weight varies` | 笔触粗细变化是手绘的标志 |
| **质感叠加** | `slight film grain, faint registration offset between cel layers` | 模拟胶片扫描与赛璐璐叠片错位 |

### 3.2 配色规则（OVA 旗舰的"色彩节奏"）

这套配色比例是社区从 Yamato / Macross / 银英传里反推的统计学规律：

- **70% 主色调**：暖灰、淡蓝灰、米白、橄榄褐 之一（hull primary）
- **25% 次结构色**：偏深的 recess 色，用于引擎内、阴影区、装甲切口里
- **5% 警示强调色**：单一饱和度高的红/橙/黄，**只**用于 hazard stripes、stenciled hull numbers、舱口警示标记

写法（直接引用即可）：
> "70% calm warm-grey or pale blue-grey hull primary; 25% darker recess tone inside engine bells and armor cutouts; 5% saturated red-orange accent used sparingly for hazard chevrons, stenciled hull numbers, and warning stripes around hatches and weapon mounts — accent reads as warning paint, NOT primary livery."

### 3.3 形态与剪影（让飞船像个"舰艇"而不像玩具）

社区共识的几条硬规则：

- **长高比 ≥ 4:1**：OVA 旗舰永远是细长的，不能是方块
- **三幕结构**：前部（攻击模块）→ 中部（指挥城堡）→ 后部（装甲发动机块）
- **指挥塔是叠层装甲，不是塔楼**；不要被画成动物头/人脸
- **后引擎是装甲块包裹，不是脚手架/钻井架**：推进器钟形喷口**部分凹陷在装甲里**，结构杆只能从切口里隐约看到
- **基础对称 + 局部不对称叠加**：主体严格左右对称，但小型外挂模块（天线、补丁板、设备舱）刻意非对称布置，制造"在用的"质感
- **百级数量的小窗、舱口、检修盖**沿全身散布，作为人体尺度参照（让人觉得这船 500–2000 米长）

### 3.4 质感与表面密度

- 大面积装甲面**必须被分割成更小子面板**，有 panel-line 和铆钉道
- 关节处要有 recessed conduit、cable trays
- 涂装要有 stencil 编号、警示斜纹（chevron stripes）
- 绝不能出现 modern PBR、ray-traced reflection、smooth featureless slab

---

## 四、可直接复用的 Prompt 模板（按场景）

下面 5 个模板都按本调研的发现重写：叙述段落、SUBJECT 前置、用正向描述代替 NEGATIVE、不带设计师真名、约 200–350 词。

### 4.1 通用旗舰类四视图（推荐起点）

```
A 2x2 four-view orthographic reference sheet of a 1200-meter [archetype] capital
spaceship, hand-painted in the visual tradition of late-1980s to mid-1990s Japanese
mecha OVA capital-ship illustration. The vessel reads as a functional warship from
that era's animation production, NOT as a modern 3D render or toy.

Silhouette: a long armored hull with a clear three-act longitudinal composition.
Forward third is an aggressive chisel-faced prow carrying the heaviest concentration
of weapon turrets and sensor housings. Middle third is a vertically-stacked
multi-tier armored command citadel, denser and taller than the bow or stern,
bristling with antenna mast forests and small secondary turrets. Rear third is a
thick armored aft engine block — multiple large thruster bells partially recessed
INTO the armor plating, with internal framework only glimpsed through small armor
cutouts and access panels. Hull length-to-height ratio at least 4:1.

Surface: hundreds of small lighted viewports and access hatches scattered densely
across the entire hull surface, sized as human-scale crew ports for implicit scale
reference. Every large armor face is subdivided by visible panel-line work and
rivet courses into smaller sub-panels — no smooth featureless slabs anywhere.
Recessed conduit channels and cable trays at the joints between hull modules.
Stenciled hull numbers and warning chevron stripes around hatches and weapon mounts.
Symmetric primary hull volume with intentionally asymmetric bolted-on antenna mounts
and small equipment pods, giving the vessel a lived-in production history.

Art style: hand-painted anime production cel artwork, hard-edged cel-shaded shadow
boundaries with one or two flat tones per surface, combined with subtle airbrushed
gradient transitions within the largest armor faces. Bold black ink linework on
silhouette edges, finer ink lines for panel work and rivets, line weight varies.
Color rhythm: 70% warm-grey hull primary, 25% darker recess tone inside engine bells
and armor cutouts, 5% saturated orange accent used sparingly for hazard chevrons
and stenciled markings. Faint film grain texture overlaid.

Layout: 2x2 grid showing front view, side view, top view, and 3/4 perspective view.
Pure white background. No text, no labels, no arrows, no panel separator lines
between the four views. The four views share consistent proportions and color.
```

### 4.2 JSON 结构化版（**强烈推荐**，比纯文本稳约 24%）

> JSON 写法是 Nano Banana Pro 官方推荐，多源验证比叙述段精度更高。把 prompt 拼成 JSON 字符串发给 API 即可。

```json
{
  "task": "generate_image",
  "subject": "1200-meter retro-anime capital spaceship, vertically thick armored hull oriented along its long axis",
  "composition": {
    "layout": "2x2 grid orthographic reference sheet",
    "views": [
      "front elevation, dead-on, centered",
      "side elevation, port-facing, centered",
      "top plan view, dorsal, centered",
      "3/4 perspective from upper-front"
    ],
    "shared_constraints": "all four views share identical proportions, scale and color treatment; pure white background; no panel separator lines between views"
  },
  "silhouette": {
    "rule": "three-act longitudinal composition, length-to-height ratio at least 4:1",
    "forward_third": "aggressive chisel-faced prow with heaviest concentration of turrets and sensors",
    "middle_third": "vertically-stacked multi-tier armored command citadel with antenna mast forests and small secondary turrets",
    "rear_third": "thick armored aft engine block with multiple large thruster bells partially recessed into the armor; internal framework only glimpsed through armor cutouts and access panels"
  },
  "surface_density": [
    "hundreds of small lighted viewports scattered across the hull as human-scale references",
    "every large armor face subdivided by panel-line work and rivet courses",
    "recessed conduit channels and cable trays at hull module joints",
    "stenciled hull numbers and warning chevron stripes around hatches and weapon mounts",
    "symmetric primary hull volume with asymmetric bolted-on antenna mounts and equipment pods"
  ],
  "art_style": "hand-painted anime production cel artwork in the visual tradition of late-1980s to mid-1990s Japanese mecha OVA capital-ship illustration",
  "rendering": {
    "shading": "hard-edged cel-shaded shadow boundaries, one or two flat tones per surface",
    "gradients": "subtle airbrushed gradient transitions only within the largest armor faces",
    "linework": "bold black ink on silhouette edges, finer ink for panel work and rivets, varying line weight"
  },
  "color_rhythm": {
    "primary_70_percent": "warm-grey hull tone",
    "secondary_25_percent": "darker recess tone inside engine bells and armor cutouts",
    "accent_5_percent": "saturated orange used sparingly for hazard chevrons and stenciled hull numbers"
  },
  "texture_overlay": "faint film grain across the frame, simulating cel scan",
  "must_avoid_via_positive_phrasing": "the vessel reads as a hand-painted 2D anime cel illustration with matte painted metal surfaces, lived-in production history, and warship proportions — not as a clean 3D render, not as a glossy toy model, not as a flat-deck aircraft carrier"
}
```

### 4.3 极简短 prompt（80 词以内，做基线对照）

研究里反复出现一个现象：**短 prompt 出图反而比长 prompt 更稳定**。建议留一个 baseline 版，迭代时回退用：

```
A four-view orthographic reference sheet of an 80s OVA-style capital spaceship.
Hand-painted anime cel artwork, hard cel-shaded shadows with bold ink outlines,
warm-grey hull with sparse orange warning chevrons. Long armored vessel with
chisel prow, stacked command citadel mid-ship, and recessed thruster bells in
an armored aft block. Pure white background. No text, no labels.
```

### 4.4 Carrier 子类型（航母）

```
[同 4.1 通用模板，把 silhouette 段替换为：]

Silhouette: a vertically-thick armored carrier hull oriented along its long axis.
The forward third splits open into a wide longitudinal launch channel running
fore-to-aft along the centerline, exiting face-first out the bow opening — small
craft launch FORWARD out of the bow, NOT off a flat top deck. Two outboard hangar
sponsons run parallel along the flanks as bolted-on extensions. The dorsal command
block is a low-profile stepped armored structure integrated FLUSH into the dorsal
spine amidships with horizontal viewport bands. The rear is an armored aft engine
block — thick armored mounting plate housing multiple large thruster bells
partially recessed into the armor. The vessel reads as an enclosed armored space
carrier, NOT as a horizontally-flat aircraft carrier.
```

> 注意我们用 "launches FORWARD out of the bow" 而不是 "no flat deck, no ski-jump, no arrestor wires" 这种 negative 写法 —— Nano Banana 听正向描述更稳。

### 4.5 单座战斗机（fighter）— 跳过三幕规则

```
A 2x2 four-view orthographic reference sheet of a single-seat space fighter,
hand-painted in 1985-1995 Japanese mecha OVA aesthetic. Aerodynamic wedge or
delta planform with twin tail fins and conformal weapon hardpoints. Hardened
canopy at the dorsal centerline. Surface: dense panel-line work, stenciled
squadron decals, formation strip lights, painted hazard markings around
intakes. Color: warm-grey primary with squadron-color tail flash and small
orange warning chevrons. Hand-painted cel artwork, hard cel-shaded shadows,
bold ink outlines with weight variation. Layout: front, side, top, 3/4
perspective views in a 2x2 grid on pure white background. No text, no labels,
no panel separator lines.
```

---

## 五、关键词词典（按维度）

### 5.1 媒介与画风（高效）

```
hand-painted anime production cel artwork
hand-painted cel animation
traditional cel animation
1985-1995 Japanese mecha OVA capital-ship illustration
late Showa era sci-fi mecha aesthetic
hand-drawn ink linework
ink and gouache painted illustration
matte painted metal surfaces
faint film grain overlay
slight cel-layer registration offset
```

### 5.2 上色与光照（高效）

```
cel-shaded with hard-edged shadow boundaries
one or two flat shadow tones per surface
subtle airbrushed gradient transitions within large armor faces
bold black ink on silhouette edges, finer ink for panel work
line weight varies — heavier on silhouette, finer on detail
warm color cast
muted limited palette
```

### 5.3 飞船形态（高效）

```
three-act longitudinal composition
chisel-faced prow / wedge prow / splayed prow
vertically-stacked multi-tier armored command citadel
antenna mast forest / dorsal antenna farm
armored aft engine block
thruster bells partially recessed into the armor
length-to-height ratio at least 4:1
bilaterally symmetric primary hull
asymmetric bolted-on equipment pods (lived-in)
```

### 5.4 表面密度（高效）

```
hundreds of small lighted viewports as human-scale references
panel-line work and rivet courses subdividing every armor face
recessed conduit channels and cable trays at hull module joints
stenciled hull numbers
warning chevron stripes around hatches and weapon mounts
hazard markings in saturated red-orange
weathered painted finish, lived-in production history
```

### 5.5 配色（高效）

```
70% warm-grey or pale blue-grey hull primary
25% darker recess tone inside engine bells and armor cutouts
5% saturated red-orange accent used sparingly for hazard markings
no metallic highlights, no chrome reflections
matte painted finish
```

### 5.6 构图与版式（高效）

```
2x2 four-view orthographic reference sheet
front elevation, side elevation, top plan, 3/4 perspective
pure white background
all four views share consistent proportions and color
no text, no labels, no arrows, no panel separator lines
```

### 5.7 风险词（要慎用 / 替代写法）

| 风险词 | 风险 | 替代写法 |
|--------|------|---------|
| `Yamato`, `Macross`, `Gundam`, `SDF-1` | 触发 IP 安全过滤 | `1980s OVA-style space battleship`, `transformable space fortress aesthetic` |
| `by Kazutaka Miyatake` | 名字识别不稳 + 双重风险 | 直接展开他的 signature 几何描述 |
| `OVA` 单独使用 | 太泛，会漂到其他风格 | `1985-1995 Japanese mecha OVA capital-ship illustration` |
| `photorealistic`, `8K`, `ultra-detailed` | 把模型推向 3D 渲染 | `hand-painted cel artwork`, `matte painted finish` |
| `chrome`, `metallic`, `glossy` | 同上 | `matte painted metal`, `weathered painted finish` |
| `masterpiece`, `best quality`, `trending on artstation` | 基本无效，挤占首 50 词权重 | 删掉，腾出空间给 SUBJECT |
| 任何 `NO X, NO Y` 列表 | Nano Banana 不支持，可能反向触发 | 改写成正向描述 |

---

## 六、经验法则与避坑清单（重点）

### 6.1 结构层面

1. **首 ~50 词必须包含主体的核心几何描述**：archetype + 长度 + 大致剪影。layout / negative / art style 全往后放。
2. **prompt 总长控制在 200–400 词**。当前 ship_generator.py 经常 800–1500 词，砍掉一半以上会更稳。
3. **章节标题不要全大写**。"ART STYLE:", "SUBJECT DESCRIPTION:" 这种语义化标题对 Nano Banana 没有特殊作用，不如直接写自然段。
4. **NEGATIVE 段全部改写成正向描述**。"NO crew figures, NO planetary background" → "the vessel is shown isolated against pure white background, no crew, no environment". 同样语义，但 nanobanana 听得更稳。
5. **能用 JSON 就用 JSON**。多个独立来源验证比纯文本提升 20–25%。

### 6.2 内容层面

6. **设计师真名要么去掉，要么只用一位**。多位设计师同时引用基本无效（甚至产生混乱）。当前的 `designed by X, Y, Z` 多人罗列尤其无效。**最佳做法是把 signature 字段直接展开成几何描述，名字完全省略**。
7. **作品名（Yamato / Macross / Gundam）能不提就不提**。要参考它们的视觉特征，就把特征拆开写（"long armored hull with stepped command bridge mid-ship and twin lateral wings"），别提名字。
8. **重复强调反而稀释**。当前 `_THREE_ACT_COMPOSITION` 在三段里都说了三遍"this is mandatory / load-bearing / critical"，这些元话语在 nanobanana 里是无效 token。
9. **同一信息只说一次**。当前 carrier 的 `_CARRIER_DIRECTIVE` + `_CARRIER_NEGATIVE` 在不同地方说了 5 遍"NOT a flat deck"，对 nanobanana 是反效果。
10. **正向描述的稀有词比 negative 列表更管用**。要排除"飞机航母平甲板"，最有效的是描述出"enclosed armored carrier hull with forward bow launch tunnel"这种正向画面，让模型脑子里先建好正确的形象。

### 6.3 飞船类的具体翻车点

11. **机首被画成动物/人脸**：明确写 "no facial features on the command structure, the bridge is a piece of layered armored equipment"，但更稳的写法是直接给出"stepped armored bridge with horizontal viewport bands"这种正面几何描述。
12. **后部成了脚手架**：写 "thruster bells partially recessed INTO the armor plating" 比写 "no scaffolding, no oil derrick framework" 更稳定。
13. **画成短粗玩具**：明确给出 "length-to-height ratio at least 4:1" 和 "1200-meter long capital ship" 这种数字尺度。
14. **失去 80s 感跑成现代设计**：必须显式锚定 "1985-1995 Japanese mecha OVA"，单独 `OVA` 或 `retro` 不够。
15. **跑成 3D 渲染**：必须在前 50 词内出现 `hand-painted cel artwork` 或 `traditional cel animation`，否则 nanobanana 默认偏向 3D。
16. **四视图比例不一致**：在 prompt 末尾明确 "all four views share consistent proportions, scale and color treatment"。
17. **版面被加了分隔线/坐标/标注**：用正向描述 "pure white background, four views float freely on the page"，比 NO panel separator lines 更稳。
18. **飞船尺寸太小被画成战斗机**：在 prompt 中给出舰长（"1200-meter long")、用 archetype 词 "capital ship" 而非 "spaceship"。
19. **多船同框**：当前 carrier prompt 强调 "do NOT draw any piloted machines"，更稳的是写 "shown as a single isolated vessel".

### 6.4 平台限制

20. **Nano Banana 2 / Pro 在 anime 风格上对版权敏感度更高**。如果观察到 IMAGE_SAFETY refuse，把 `anime` 替换为 `hand-painted illustration` 或 `cel-shaded technical illustration` 试试。
21. **温度参数**：Nano Banana 官方推荐 0.7 平衡稳定性与创意。
22. **付费/免费配额**：免费层已降至 2 张/天。需要批量出图建议直接用 API。
23. **SynthID 水印**：所有 Nano Banana 出图都嵌入了不可见数字水印，标记 AI 生成 — 这影响不到画质，但要知道。

---

## 七、对当前 `core/ship_generator.py` 的对比改进建议

### 7.1 当前代码的具体问题

按 `core/ship_generator.py` 行号定位：

| 行号 | 问题 | 建议 |
|------|------|------|
| L156–171 (`_CARRIER_DIRECTIVE`) | 反复用 NOT, NO 句式 | 全部改写正向 |
| L173–182 (`_CARRIER_NEGATIVE`) | 整段 "Forbidden:" 列表 | 删除整段，精华正向化后并入 directive |
| L186–213 (`_THREE_ACT_COMPOSITION`) | 章节标题 "THREE-ACT MECHA-DESIGN COMPOSITION (mandatory ...)" 是元话语 | 简化为一段叙述："The hull reads as three longitudinal acts: a chisel-faced forward attack module, a stacked central command citadel, and an armored aft engine block." |
| L215–240 (`_SURFACE_DENSITY_DIRECTIVE`) | 1500+ 字的密集列表 | 压缩为 80–120 词的叙述段 |
| L242–266 (`_OVA_ART_STYLE_BODY`) | 这段写得最好，可以保留大部分 | 微调即可，把 NEVER 列表改成正向 |
| L267–271 (`_OVA_ART_STYLE_REMINDER`) | "REMINDER: ... NO text, NO labels..." | 改为 "the image is a clean reference sheet on pure white background" |
| L305–321 (`_get_ship_negative_prompt`) | **整个函数应该删掉**，把核心 5–6 条精华正向化后并入主 prompt | 删 |
| L357–370 (`_designer_signature_line`) | 同时引用多位设计师，"DRIVE THE SILHOUETTE FROM THIS" 元话语 | **不要带名字**。把 signature 字段的内容**直接拼进 SUBJECT 描述**，不要说"designed by X, Y" |
| L415–443 (`generate_full_prompt`) | 8 个章节用 `\n\n` 拼接 | 改为 3–4 个自然段 |

### 7.2 推荐的重构方向（不写代码，给方案）

1. **`generate_full_prompt` 输出从 8 段砍到 3–4 段**：
   - 第 1 段（首 ~50 词）：subject + archetype + 长度 + 大致剪影 + 媒介定位（"hand-painted 1985-1995 OVA cel artwork"）
   - 第 2 段：silhouette / three-act composition（叙述，不要 ALL CAPS 标题）
   - 第 3 段：surface density + color rhythm（叙述）
   - 第 4 段：layout（"2x2 four-view, pure white background, no text"）

2. **新增一个 JSON 输出模式**：保留现有自然语言模式，再加一个 `--format=json` 选项输出 4.2 那种结构化 prompt。让用户在 Gemini API 的 raw 调用里直接用 JSON。

3. **`_designer_signature_line` 要重写**：
   - 不要写 "designed by X"
   - 不要写 "must follow that designer's distinctive visual vocabulary"
   - 直接把 signature 字段去掉名字、去掉时间地点、只留几何/表面描述，并入 SUBJECT 段
   - 多位设计师同时选时，**只取第一位**或拼成一段共有特征，不罗列名字

4. **`_get_ship_negative_prompt` 整个函数删掉**。当前内容里真正有意义的几条（"isolated against pure white", "no environment background"）已经在 `_get_layout_criteria` 或可以放在主 prompt 收尾。NO 列表完全没用。

5. **carrier 的两段（`_CARRIER_DIRECTIVE` + `_CARRIER_NEGATIVE`）合并为一段正向描述**，约 60 词。

6. **mecha hangar/payload 类内容用 `manufacturer_data` 控制，不要硬编码进每个 prompt**。

7. **加个 `prompt_length_budget` 配置**，让用户能在 GUI 切「精简版（200 词）/ 标准版（350 词）/ 详细版（500 词）」，用于 A/B 对比。

### 7.3 一个最小可执行的对照实验

建议在改动代码之前，用纯人工方式跑一次 A/B：

| 组 | Prompt | 预期 |
|---|--------|------|
| A | 当前 ship_generator.py 输出（按 Carrier + Miyatake） | 基线 |
| B | 第 4.1 节的通用旗舰模板（同 Carrier 设定） | 应该明显更稳 |
| C | 第 4.2 节的 JSON 模板 | 应该最稳 |
| D | 第 4.3 节的 80 词极简版 | 验证「短 prompt 反而稳」假说 |

每组各跑 5–10 张，用同一个 archetype，对比：
- 是否还出现指挥塔变成动物头脸
- 是否还有 3D 渲染感
- 四视图比例是否一致
- 是否还有航母变平甲板

跑完之后，能精确量化"哪一段改写带来了多少稳定性提升"，再决定 ship_generator.py 怎么改。

---

## 八、5 个被验证有效的 Nano Banana 飞船/机甲 prompt 案例（社区原文）

来自 GitHub awesome-nano-banana-pro-prompts、Medium、Reddit r/Bard、知乎 Nano Banana 教程的整合：

**案例 1 — 80s 动画风格机甲机库（Reddit r/Bard，高票）**
> "Giant robot standing in a repair hangar with mono-eye sensor and bulky shoulder cannons, tiny mechanics on scaffolding for scale, technical blueprint lines overlaid, white and blue ink style illustration, cel-shaded 1980s anime aesthetic, hand-painted background"

**案例 2 — 复古飞船枢纽（Medium nanobanana.org 教程）**
> "Retro anime-style spaceship hub routing and transmitting small spaceship carriers, futuristic space odyssey style, dark space theme background, specific sci-fi color scheme with neon accents, 1:1 aspect ratio, technical details visible, painted mechanical surfaces"

**案例 3 — 通用复古战舰（避免 IP 触发）**
> "Massive retro-futuristic battleship, based on 1980s anime design language, military vessel aesthetics, cylindrical main body with lateral engines, modular weapon systems, hand-painted technical illustration style, cel-shaded outlines, technical blueprint overlay, warm vintage color palette, no specific IP references"

**案例 4 — Gundam 风但非 Gundam（绕开版权）**
> "Humanoid combat mecha in repair bay, modular armor plating design, 1980s anime mechanical aesthetic, cel-shaded rendering, bold black ink outlines, technical cross-section view, mechanical detail emphasized, retro animation studio style background"

**案例 5 — 90s VHS 机甲截图（X/Twitter 高互动）**
> "90s anime TV screenshot, giant spaceship in dock, technical blueprint lines, mechanical panels, cel-shaded illustration style, bold ink outlines, saturated colors, vintage film grain, hand-painted aesthetic"

---

## 九、社区资源索引（飞船/机甲相关）

| 资源 | 类型 | 与本主题相关度 | 链接 |
|------|------|---------------|------|
| Google Cloud Blog: Ultimate prompting guide for Nano Banana | 官方文档 | ★★★★★ | https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana |
| Google Developers Blog: How to prompt Gemini 2.5 Flash Image | 官方文档 | ★★★★★ | https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/ |
| GitHub: YouMind-OpenLab awesome-nano-banana-pro-prompts | 万级 prompt 库 | ★★★★★ | https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts |
| GitHub: ZeroLu/awesome-nanobanana-pro | 精选 prompt 库 | ★★★★ | https://github.com/ZeroLu/awesome-nanobanana-pro |
| GitHub: jau123/nanobanana-trending-prompts | X/Twitter 热门 1300+ | ★★★★ | https://github.com/jau123/nanobanana-trending-prompts |
| Apiyi Blog: 停止夸张式提示词 (Nano Banana 2 时代) | 长文 | ★★★★★ | https://help.apiyi.com/en/stop-hyperbolic-prompts-nano-banana-2-gpt-image-2-guide-en.html |
| Apiyi Blog: Nano Banana Pro 内容限制指南 | 安全过滤 | ★★★★ | https://help.apiyi.com/nano-banana-pro-content-restrictions-guide.html |
| Apiyi Blog: Nano Banana Pro 版权保护指南 | 版权过滤 | ★★★★ | https://help.apiyi.com/en/nano-banana-pro-disney-ip-blocked-copyright-protection-guide-en.html |
| Pixeldojo: Master Negative Prompts with Gemini 2.5 Flash Image | negative 替代写法 | ★★★★★ | https://pixeldojo.ai/gemini-2.5-flash-image-negative-prompts |
| Sider AI: How to Write Negative Prompts in Nano Banana | negative 替代写法 | ★★★★ | https://sider.ai/blog/ai-image/how-to-write-negative-prompts-in-nano-banana-a-practical-guide/ |
| Chase Jarvis: Does JSON Prompting Actually Work? | JSON 实测 | ★★★★★ | https://chasejarvis.com/blog/does-json-prompting-actually-work-tested-with-nano-banana/ |
| Leonardo AI: Nano Banana Prompt Guide | 通用指南 | ★★★ | https://leonardo.ai/news/nano-banana-prompt-guide/ |
| DataStudios: Nano Banana Pro 完整报告 | 模型评测 | ★★★ | https://www.datastudios.org/post/nano-banana-pro-full-report-and-review-of-the-google-s-gemini-3-ai-image-generation-engine-compar |
| Max Woolf 博客: Nano Banana Pro is the best AI image generator, with caveats | 独立评测 | ★★★★ | https://minimaxir.com/2025/12/nano-banana-pro/ |
| Medium: How to Create Anime Art in Nano Banana Pro with Real Prompts | 实战 prompt | ★★★★ | https://medium.com/technology-hits/how-to-create-anime-art-in-nano-banana-pro-with-real-prompts-ffb440699081 |
| Imagine.art: Nano Banana Pro Prompting Guide + 75 Prompts | 模板合集 | ★★★ | https://www.imagine.art/blogs/nano-banana-pro-prompt-guide |
| Skywork AI: Nano Banana Prompt Engineering Best Practices 2025 | 长文 | ★★★ | https://skywork.ai/blog/nano-banana-gemini-prompt-engineering-best-practices-2025/ |
| nanobanana.org: Anime Prompts for Nano Banana | anime 模板 | ★★★ | https://nanobanana.org/banana-prompts/anime |
| 知乎: Nano Banana 官方 Prompt 提示词教程 | 中文教程 | ★★★★ | https://zhuanlan.zhihu.com/p/1946483329441439808 |
| 知乎: 一次找齐 1000 个 Nano Banana Pro 提示词 | 中文合集 | ★★★ | https://zhuanlan.zhihu.com/p/1978947025841189918 |
| Apiyi Blog: Nano Banana Pro 中文提示词完整教程 | 中文教程 | ★★★★ | https://help.apiyi.com/nano-banana-pro-chinese-prompt-guide-tc.html |

---

## 十、最关键的几句话

如果你只读到这里，记三句：

1. **Nano Banana 是语言推理模型，不是 tag-soup 模型**。把 prompt 写成自然段，砍到 200–400 词，主体放最前面。

2. **没有 negative prompt**。所有 NO X 都改成正向的"画面里应该有什么"。

3. **设计师真名 + 作品真名是双重风险**。把 signature 字段的几何描述拆出来用，名字省略掉。

---

> 报告完。配套姊妹文档：`nanobanana_90s_anime_cel_research.md`（角色赛璐璐），两份文档共享同一组 Nano Banana 通用经验法则，飞船这一份在它基础上加了「capital-ship 形态学」和「正向化改写」两块。

Sources（核心来源完整列表）：
- [Google Cloud Blog – Ultimate prompting guide for Nano Banana](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)
- [Google Developers Blog – How to prompt Gemini 2.5 Flash Image Generation](https://developers.googleblog.com/en/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)
- [Apiyi – Stop hyperbolic prompts in the Nano Banana 2 era](https://help.apiyi.com/en/stop-hyperbolic-prompts-nano-banana-2-gpt-image-2-guide-en.html)
- [Apiyi – Nano Banana Pro content restrictions guide](https://help.apiyi.com/nano-banana-pro-content-restrictions-guide.html)
- [Apiyi – Nano Banana Pro Disney IP blocked / copyright guide](https://help.apiyi.com/en/nano-banana-pro-disney-ip-blocked-copyright-protection-guide-en.html)
- [Pixeldojo – Master negative prompts with Gemini 2.5 Flash Image](https://pixeldojo.ai/gemini-2.5-flash-image-negative-prompts)
- [Sider AI – How to write negative prompts in Nano Banana](https://sider.ai/blog/ai-image/how-to-write-negative-prompts-in-nano-banana-a-practical-guide/)
- [Chase Jarvis – Does JSON prompting actually work? Tested with Nano Banana](https://chasejarvis.com/blog/does-json-prompting-actually-work-tested-with-nano-banana/)
- [Max Woolf – Nano Banana Pro is the best AI image generator, with caveats](https://minimaxir.com/2025/12/nano-banana-pro/)
- [Medium – How to create anime art in Nano Banana Pro with real prompts](https://medium.com/technology-hits/how-to-create-anime-art-in-nano-banana-pro-with-real-prompts-ffb440699081)
- [GitHub – YouMind-OpenLab/awesome-nano-banana-pro-prompts](https://github.com/YouMind-OpenLab/awesome-nano-banana-pro-prompts)
- [GitHub – ZeroLu/awesome-nanobanana-pro](https://github.com/ZeroLu/awesome-nanobanana-pro)
- [GitHub – jau123/nanobanana-trending-prompts](https://github.com/jau123/nanobanana-trending-prompts)
- [Leonardo AI – Nano Banana prompt guide](https://leonardo.ai/news/nano-banana-prompt-guide/)
- [Skywork AI – Nano Banana Gemini prompt engineering best practices 2025](https://skywork.ai/blog/nano-banana-gemini-prompt-engineering-best-practices-2025/)
- [DataStudios – Nano Banana Pro full report and review](https://www.datastudios.org/post/nano-banana-pro-full-report-and-review-of-the-google-s-gemini-3-ai-image-generation-engine-compar)
- [Imagine.art – Nano Banana Pro prompting guide + 75 prompts](https://www.imagine.art/blogs/nano-banana-pro-prompt-guide)
- [nanobanana.org – Anime prompts for Nano Banana](https://nanobanana.org/banana-prompts/anime)
- [知乎 – Nano Banana 官方 Prompt 提示词教程](https://zhuanlan.zhihu.com/p/1946483329441439808)
- [知乎 – 一次找齐 1000 个 Nano Banana Pro 提示词](https://zhuanlan.zhihu.com/p/1978947025841189918)
- [Apiyi – Nano Banana Pro 中文提示词完整教程](https://help.apiyi.com/nano-banana-pro-chinese-prompt-guide-tc.html)
