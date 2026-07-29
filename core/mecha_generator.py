"""Mecha (mobile suit / real-robot) prompt generator.

Generates a 2x2 four-view reference sheet prompt for a complete bare-frame mecha.
Reuses ComponentGenerator's layout / view protocol / art style helpers, but defines
its own subject description with class silhouette + designer signature.

Mecha are produced WITHOUT external equipment so the user can later compose them
with weapon / shield / etc. components rendered from prompt_generator.
"""
import json
import random
from typing import Dict, List, Optional

from paths import resource_path
from . import prompt_generator as pg


DESIGNERS_PATH = resource_path("mecha_designers.json")


def load_designers() -> List[Dict]:
    try:
        with open(DESIGNERS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return list(data.get("designers", []))
        if isinstance(data, list):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return []


DESIGNERS = load_designers()


def _designer_in_scope(d: Dict, scope: str) -> bool:
    """A designer with no scope field defaults to mecha-only (back-compat)."""
    scopes = d.get("scope")
    if not scopes:
        return scope == "mecha"
    return scope in scopes


def filter_designers(scope: str = "mecha") -> List[Dict]:
    return [d for d in DESIGNERS if _designer_in_scope(d, scope)]


def get_designer_names(scope: str = "mecha") -> List[str]:
    return [d["name"] for d in filter_designers(scope)]


def _localize_field(field, lang: str) -> str:
    if isinstance(field, dict):
        return field.get(lang) or field.get("en", "")
    return str(field) if field else ""


def get_designer_label_map(lang: str = "en", scope: str = "mecha") -> Dict[str, str]:
    """label -> name. Label includes designer's stylistic tendency + canonical works
    for picker disambiguation. Tendency comes first (broader category), works second
    (concrete reference)."""
    mapping: Dict[str, str] = {}
    works_prefix = "代表作" if lang == "zh" else "Works"
    for d in filter_designers(scope):
        name = d["name"]
        tendency = _localize_field(d.get("tendency", ""), lang)
        works = _localize_field(d.get("work", ""), lang)
        parts = []
        if tendency:
            parts.append(tendency)
        if works:
            parts.append(f"{works_prefix}：{works}")
        suffix = "；".join(parts) if lang == "zh" else "; ".join(parts)
        label = f"{name}（{suffix}）" if suffix else name
        mapping[label] = name
    return mapping


def get_designer_options(lang: str = "en", scope: str = "mecha") -> List[str]:
    return list(get_designer_label_map(lang, scope).keys())


def get_designer_by_name(name: str) -> Optional[Dict]:
    for d in DESIGNERS:
        if d["name"] == name:
            return d
    return None


# =============================================================================
# Five abstract control axes
# =============================================================================
# Each axis is a list of (key, en_label, zh_label, prompt_text) tuples. The key
# is what's stored / passed around; the labels drive the UI; the prompt_text is
# what gets woven into the subject description.
#
# All descriptions are deliberately abstract — describing form and function, not
# naming canonical shapes from any specific franchise.

# Axis 1 — Sensor Module (head)
# Tuple format: (key, en_label, zh_label, prompt_text, hint_dict)
# hint_dict provides a short user-facing description for the UI tooltip.
SENSOR_MODULES = [
    ("low_wedge",
     "Low rounded wedge",
     "低矮圆弧楔形",
     "compact armored sensor module shaped like a low rounded wedge, with a horizontal recessed optical band and small grille intakes on the cheek faces",
     {"en": "Low rounded head with a horizontal optical band and side intake grilles. Reads as a workhorse police / utility cap.",
      "zh": "低矮圆弧形头，正面一条横向光带开口，两侧脸颊有进气格栅。像警用 / 工程机的低矮头部。"}),
    ("recessed_block",
     "Recessed angular block",
     "凹陷棱角方块",
     "small angular sensor block recessed deep into the upper torso, almost flush with the shoulders, with two narrow forward-facing slit apertures",
     {"en": "Tiny squared block sunk into the upper torso, almost flush with the shoulders. No protruding head — armored-suit feel.",
      "zh": "一个小方块嵌入胸甲上沿，几乎与肩膀齐平，前面两条窄缝。没有突出的头，装甲服 / Power Suit 风格。"}),
    ("tall_mast",
     "Tall stepped sensor mast",
     "高耸阶梯传感塔",
     "tall narrow upright sensor mast with a stepped cylindrical housing, a single circular forward optic, and small radial vents around the base",
     {"en": "Tall thin stepped cylindrical tower with a single round front optic. Looks like a comms / radar mast.",
      "zh": "又高又窄的圆柱塔，分阶梯叠起来，正面就一颗圆形大眼。像通讯 / 雷达塔的瘦高比例。"}),
    ("wide_three_aperture",
     "Wide three-aperture module",
     "三孔宽幅模组",
     "low wide armored sensor module with three small forward apertures arranged horizontally and a hinged maintenance hatch on top",
     {"en": "Wide low head with THREE small forward apertures (not two), and a hinged top hatch. Industrial / equipment feel.",
      "zh": "横向较宽的矮头，前面横排三个小孔（不是两眼），上面有保养盖板。工业设备感。"}),
    ("faceted_helm",
     "Faceted geometric helm",
     "棱面几何头盔",
     "geometric faceted sensor housing made of flat trapezoidal plates, with one larger central aperture set behind a recessed cowl",
     {"en": "All flat trapezoidal facets, one big central optic recessed behind a cowl. Stealth-fighter angular feel.",
      "zh": "全部由平的梯形面拼成，正中一个较大的光学件藏在凹陷罩后。隐身战机般的棱面硬角感。"}),
    ("asymmetric_cluster",
     "Asymmetric sensor cluster",
     "非对称传感簇",
     "asymmetric sensor cluster with one large forward optic on one side and a smaller secondary array on the other, no symmetric facial features",
     {"en": "ONE side has a big optic, the OTHER side has a small array. Deliberately not symmetric — no face.",
      "zh": "一边一颗大眼，另一边一组小传感器阵列。完全不对称，没有左右对称的「脸」。"}),
    ("smooth_band",
     "Smooth wraparound band",
     "光滑环带式",
     "smooth rounded armored cap with a single horizontal aperture band wrapping around the front, no protruding antennas",
     {"en": "Smooth rounded cap with one horizontal band wrapping around the front. No antennas, no spikes.",
      "zh": "圆滑的弧形罩，正面一圈横向开口绕一周。没有任何天线突出。"}),
    ("twin_barrel_optics",
     "Twin barrel optics",
     "双筒光学头",
     "boxy industrial sensor housing with two cylindrical optic barrels protruding forward like lens hoods, mounted on a short reinforced neck collar",
     {"en": "Boxy head with TWO cylindrical lens barrels sticking forward like a binocular pair. Heavy industrial cam-mount.",
      "zh": "方形头部前突两根圆柱镜筒，像双筒望远镜，脖子粗短。重工业相机支架感。"}),
    ("vertical_blade",
     "Vertical sensor blade",
     "立式传感刀片",
     "narrow vertical sensor blade with a top-mounted cluster of small forward optics and side-mounted micro-thruster verniers",
     {"en": "Narrow vertical blade-shaped head, optic cluster at the top, side micro-thrusters. Tall thin recon profile.",
      "zh": "又窄又竖的扁平片状头，顶部一簇小光学件，两侧有微推。瘦窄的侦察机剪影。"}),
    ("slatted_visor",
     "Slatted visor pod",
     "百叶护罩感应荚",
     "minimal sensor pod recessed behind a slatted armor visor, optics not directly visible, with grille vents along the upper edge",
     {"en": "Optics HIDDEN behind horizontal slat visor — you can't see the eyes. Closed-helm assault feel.",
      "zh": "整个头部被横向百叶板罩住，看不到眼睛，光学件藏在百叶缝隙后。封闭式头盔的突击机感。"}),
]

# Axis 2 — Surface Treatment
SURFACE_TREATMENTS = [
    ("double_layer_floating",
     "Double-layer floating panels",
     "双层悬浮装甲",
     "double-layered floating panel armor — thin outer plates suspended 2-3mm above a darker inner frame, with slot vents and small bolt heads visible at the seams",
     {"en": "Thin outer plates floating slightly above a darker inner frame. Modern refined feel.",
      "zh": "薄外层装甲板悬浮在深色内框架之上 2-3mm，缝隙处露出排气口和螺栓。现代精致感。"}),
    ("welded_single_layer",
     "Single-layer welded plate",
     "单层焊接装甲",
     "single-layer thick welded plate armor with visible weld seams and overlapping plate edges, low panel-line density, factory-stamped feel",
     {"en": "Single thick layer with visible weld seams. Quantity-production stamped-out feel.",
      "zh": "单层厚装甲板，可见焊缝和叠合板边，分线少。工厂量产冲压感。"}),
    ("exposed_inner_frame",
     "Exposed inner frame",
     "外露内骨架",
     "armor plates float over a clearly visible exposed inner mechanical frame at all major joints — gaps between armor plates reveal cabling and structural pistons underneath",
     {"en": "Armor plates leave gaps that show cables and pistons of the inner frame underneath.",
      "zh": "装甲板之间露出缝隙，能看见下面的内骨架、线缆和结构活塞。"}),
    ("ceramic_monocoque",
     "Smooth ceramic monocoque",
     "陶瓷整体外壳",
     "smooth seamless ceramic-finish monocoque shell, almost no visible panel lines, soft beveled edges, matte glossy finish that reads as continuous molded armor",
     {"en": "Smooth seamless shell, almost NO panel lines. Continuous molded ceramic surface.",
      "zh": "整体光滑无缝外壳，几乎看不到分线。陶瓷质感的整体浇铸感。"}),
    ("riveted_industrial",
     "Riveted industrial plating",
     "工业铆钉拼装",
     "riveted industrial plating with dense rows of large bolt heads at every plate seam, thick overlapping plate edges, brutally functional appearance",
     {"en": "Dense rows of big rivets along every seam. Brutally functional shipyard feel.",
      "zh": "每条接缝都是密集的大铆钉行，厚重叠合板边。粗野的造船厂功能感。"}),
    ("organic_exoshell",
     "Organic exoshell",
     "有机外骨壳",
     "overlapping organic-feeling armor segments that read as exoskeleton restraints rather than mecha shell, sinewy contours, no rigid panel-line grid",
     {"en": "Armor reads as biological exoskeleton restraints. Sinewy curves, no rigid panel grid.",
      "zh": "装甲像生物外骨骼束缚带，肌肉感的曲线，没有刚性分线网格。"}),
    ("layered_greeble",
     "Layered greeble strata",
     "多层叠加细节",
     "dense layered greeble strata — multiple strata of armor plates, recessed grilles, exposed mechanical struts, conduit clusters stacked across the surface",
     {"en": "Many layers of plates / grilles / struts / conduits stacked over each other. Maximum tech density.",
      "zh": "多层装甲板、格栅、机械支柱、管线簇层层叠加。最大化的硬表面细节密度。"}),
    ("flush_stealth",
     "Flush faceted stealth",
     "齐平棱面隐身",
     "flush faceted radar-absorbent paneling with precision-cut edges, minimal visible fasteners, recessed vents, no protruding greebles",
     {"en": "Flat faceted plates flush together, recessed vents, almost no visible fasteners or protrusions.",
      "zh": "平整的多面体板齐平拼接，凹陷排气口，几乎看不到突出件或紧固件。"}),
]

# Axis 3 — Shoulder Armor Form
SHOULDER_FORMS = [
    ("cylindrical_pauldron",
     "Cylindrical wrap pauldron",
     "圆筒包肩",
     "cylindrical wrap-around pauldrons fully enclosing the shoulder joint, smooth curved exterior with a single inset trim line",
     {"en": "Smooth round can-shaped shoulders fully wrapping the joint. Classic grunt-suit shoulder.",
      "zh": "圆筒形肩甲完全包住肩关节，光滑弧面外形。经典量产机肩部。"}),
    ("spiked_pauldron",
     "Spiked / studded pauldron",
     "尖刺 / 钉肩甲",
     "spiked or studded pauldrons with prominent forward-projecting spikes or rows of bolt-stud protrusions",
     {"en": "Forward-projecting spikes or rows of stud protrusions. Aggressive close-combat feel.",
      "zh": "肩甲上有向前突出的尖刺或成排的铆钉突起。近战 / 攻击性强的感觉。"}),
    ("flat_thin_plates",
     "Flat thin plate pauldron",
     "平板薄肩甲",
     "flat thin armor plates that lie close to the shoulder profile, low silhouette, minimal volume",
     {"en": "Thin flat plates close to the body. Low-profile, minimal shoulder volume.",
      "zh": "贴身的薄平板装甲，肩部体积很小。低剪影，简洁。"}),
    ("stepped_stack",
     "Stepped stacked pauldron",
     "阶梯堆叠肩甲",
     "stepped stacked pauldrons made of two or three discrete armor plates layered like roof tiles",
     {"en": "Two or three plates stacked like roof tiles. Layered stepped silhouette.",
      "zh": "两到三层装甲板像屋瓦那样阶梯叠放。层次分明的剪影。"}),
    ("hinged_double_layer",
     "Hinged double-layer pauldron",
     "翻盖双层肩甲",
     "hinged double-layer pauldrons with an outer cover plate that visually appears to swing open over an inner reinforced shoulder block",
     {"en": "Outer cover plate looks like it swings open over an inner block. Mechanical 'opening' feel.",
      "zh": "外层有一片像翻盖那样的装甲板覆盖在内层加固块上。带机械「能掀开」的视觉感。"}),
    ("ammo_block",
     "Ammo / supply block",
     "弹仓 / 物资块",
     "shoulder-integrated supply block — flat boxy ammo or coolant container forming the shoulder mass, with access hatches and grip handles visible",
     {"en": "Shoulders are flat boxy supply containers with hatches and handles. Logistics-machine feel.",
      "zh": "肩部是方形弹药 / 冷却剂储存箱，可见检修盖板和把手。后勤运输机感。"}),
    ("vernier_cluster_shoulder",
     "Vernier cluster pauldron",
     "微推力簇肩甲",
     "vernier-thruster-cluster pauldrons — the shoulder mass is composed of multiple small thruster nozzles arranged in a clover or hex pattern around a central core",
     {"en": "Shoulders ARE thruster clusters — multiple small nozzles in clover/hex around a core.",
      "zh": "肩甲本身就是一簇小型推进器，多个喷口呈梅花 / 六边形排列。"}),
    ("asymmetric_one_heavy",
     "Asymmetric — one heavy",
     "非对称 · 单边加强",
     "asymmetric arrangement — one shoulder is significantly more massive and reinforced than the other, the lighter shoulder carries a flat shield-style plate",
     {"en": "ONE shoulder is much bigger and reinforced; the OTHER is a thin shield plate. Custom-build feel.",
      "zh": "一边肩甲明显更厚重加固，另一边是薄盾板。改装定制机的感觉。"}),
    ("flared_aero_fairing",
     "Flared aero fairing",
     "外扩气动整流",
     "swept aerodynamic shoulder fairings that flare outward and back, integrated smoothly into the upper torso",
     {"en": "Swept aero fairings flare outward and rearward, blending into the torso. Aerospace feel.",
      "zh": "向外向后掠的气动整流肩甲，平滑融入躯干。飞行系机型感。"}),
    ("minimal_joint_only",
     "Minimal joint cap only",
     "极简关节罩",
     "minimal armor that covers only the shoulder ball joint itself, leaving the upper arm largely exposed",
     {"en": "Just a small cap over the joint ball — upper arm is mostly exposed. Lightweight stripped-down feel.",
      "zh": "仅在肩关节球处加一个小罩，上臂大部分裸露。轻量化、骨架外露感。"}),
]

# Axis 4 — Propulsion Style
PROPULSION_STYLES = [
    ("oversized_backpack_cluster",
     "Oversized backpack cluster",
     "超大型背包簇",
     "oversized rear backpack thruster cluster taller than the sensor module, housing four to six main thruster nozzles in a clover or hex array",
     {"en": "Massive rear backpack with 4-6 main nozzles. Backpack TALLER than the head — space-combat type.",
      "zh": "硕大的背包推进器，4-6 个主喷口呈梅花 / 六边形排列。背包高度超过头部，纯太空战类型。"}),
    ("winged_aux_thrusters",
     "Winged auxiliary thrusters",
     "翼状辅助推进",
     "wing-like auxiliary thruster arms that extend rearward from the upper back, each terminating in a large directional thruster nozzle",
     {"en": "Wing-like auxiliary thruster arms extending rearward, each ending in a directional nozzle.",
      "zh": "从背部向后伸出翼状的辅助推进臂，每根臂端有一个可转向大喷口。"}),
    ("integrated_skirt",
     "Integrated skirt thrusters",
     "裙甲集成喷口",
     "thrusters fully integrated into the lower skirt and calf armor, no oversized backpack — propulsion is hidden inside the silhouette and only the nozzle openings are visible",
     {"en": "Thrusters HIDDEN inside the skirt and calves — no big backpack. Clean low-profile silhouette.",
      "zh": "推进器完全藏在裙甲和小腿装甲里，没有大背包。剪影干净简洁。"}),
    ("rocket_cluster_dense",
     "Dense rocket nozzle cluster",
     "密集火箭喷口簇",
     "a dense cluster of small rocket-engine nozzles ringing the lower back and skirt, plus secondary nozzles on the calves and forearms",
     {"en": "MANY small rocket nozzles ringing the lower back, skirt, calves, forearms. Dense thruster grid.",
      "zh": "下背、裙甲、小腿、前臂上密布大量小型火箭喷口。喷口密度极高。"}),
    ("twin_large_main",
     "Twin large main bells",
     "双大型主喷",
     "two single oversized main thruster bells dominating the back, plus a few small reaction-control verniers — heavy, blunt, atmospheric-bias propulsion",
     {"en": "Just TWO huge main thruster bells on the back. Blunt and heavy — atmospheric-bias.",
      "zh": "背后只有两个超大主喷管。粗野厚重，偏向大气层内。"}),
    ("ground_dominant_minimal",
     "Minimal ground-walker",
     "地面型 · 极简推进",
     "minimal propulsion — only small reaction-control verniers, no large thruster bells, no oversized backpack — designed for terrestrial walking, not space flight",
     {"en": "Almost no propulsion — just tiny RCS verniers. Pure ground walker, NOT a space mecha.",
      "zh": "几乎没有推进系统，只有小型姿态控制喷口。纯地面行走机型，不能太空作战。"}),
    ("convertible_engine_legs",
     "Convertible engine-legs",
     "可变形腿部引擎",
     "leg modules clearly shaped as engine nacelles with afterburner rings at the heels, plus a folded aerodynamic backpack — propulsion doubles as travel-mode engines",
     {"en": "Legs ARE engine nacelles with afterburner rings at heels. Doubles as travel-mode propulsion.",
      "zh": "腿部本身就是引擎短舱，后跟有加力燃烧环。腿同时作为变形态的推进引擎。"}),
    ("multi_nozzle_strata",
     "Multi-nozzle strata",
     "多层喷口阵",
     "multi-nozzle thruster arrays in clover or hex patterns, layered in multiple strata across the back and shoulders, suggesting extreme high-G maneuvering capability",
     {"en": "Multiple strata of clover/hex thruster arrays stacked on back and shoulders. Extreme maneuverability.",
      "zh": "背部、肩部分多层叠加梅花 / 六边形喷口阵列。暗示极限高 G 机动能力。"}),
]

# Axis 5 — Paint Scheme (the FORMAT of the colorway, not the colors themselves)
PAINT_SCHEMES = [
    ("hero_tricolor",
     "Hero tricolor blocking",
     "英雄三色分块",
     "hero-style tricolor blocking — primary color across the chest and limbs, secondary accent color on shoulders and key panels, tertiary highlight color on small detail strips. Clean color separation along armor seams",
     {"en": "Three colors in clean blocks — primary body, secondary shoulders, tertiary detail strips. Hero unit feel.",
      "zh": "三色清晰分区：主色身体、辅色肩部、点缀色小细节。英雄机的标志性涂装。"}),
    ("monochrome_military",
     "Monochrome military",
     "单色军用",
     "single flat military color (olive drab, naval grey, or desert tan) across the entire body, with only minor stencil markings and unit numbers as visual interest",
     {"en": "ONE flat military color (olive / grey / sand) over the whole body. Just stencil markings for variation.",
      "zh": "全身单一军用色（橄榄绿 / 海军灰 / 沙色），仅以模板印字编号点缀。"}),
    ("two_tone_high_contrast",
     "Two-tone high contrast",
     "双色高对比",
     "two-tone high contrast — light upper body, dark lower body (or vice versa), strong horizontal color break at the waist line, no tertiary accent",
     {"en": "Two strongly contrasting colors split at the waist (e.g., light top / dark bottom). Bold horizontal break.",
      "zh": "两种强对比色在腰部分隔（例如上浅下深）。强烈的横向色块切分。"}),
    ("warning_stripes",
     "Solid + warning stripes",
     "纯色加警示条",
     "solid base color with bright hazard warning stripes on moving parts, joint covers, and weapon mounts — caution yellow / red / orange high-visibility accents",
     {"en": "Solid body color with bright hazard stripes (yellow/red/orange) on joints and moving parts.",
      "zh": "底色为纯色，关节、活动件、武器挂载点上画有黄 / 红 / 橙的醒目警示条。"}),
    ("gradient_fade",
     "Gradient fade",
     "渐变过渡",
     "gradient fade transitioning between two colors across the body — for example dark at the extremities fading to light at the core, or warm at the top fading to cool at the bottom",
     {"en": "Smooth color gradient across the body (e.g., dark extremities fading to light core).",
      "zh": "全身有平滑色彩渐变（例如四肢深色渐变到躯干浅色）。"}),
    ("weathered_field_use",
     "Weathered field-use",
     "重度战损做旧",
     "heavily weathered field-use finish — chipped paint along all corners, oil streaks running down panels, scorch marks around exhaust ports, hand-painted unit markings, dust accumulation in recesses",
     {"en": "Heavy weathering — chipped paint, oil streaks, scorch marks, dust in recesses. Lived-in field veteran feel.",
      "zh": "厚重的战损做旧效果 —— 边角掉漆、油渍流痕、喷口烧灼、凹陷积灰。久经沙场感。"}),
]


# Build lookup helpers for each axis. Each entry is a 5-tuple:
# (key, en_label, zh_label, prompt_text, hint_dict)
def _unpack(entry):
    """Tolerate legacy 4-tuples (no hint) and new 5-tuples."""
    if len(entry) == 5:
        return entry
    key, en, zh, prompt = entry
    return key, en, zh, prompt, {"en": "", "zh": ""}


def _axis_to_dict(axis: List[tuple]) -> Dict[str, Dict]:
    out = {}
    for entry in axis:
        key, en, zh, prompt, hint = _unpack(entry)
        out[key] = {"en": en, "zh": zh, "prompt": prompt, "hint": hint}
    return out


SENSOR_MODULES_MAP = _axis_to_dict(SENSOR_MODULES)
SURFACE_TREATMENTS_MAP = _axis_to_dict(SURFACE_TREATMENTS)
SHOULDER_FORMS_MAP = _axis_to_dict(SHOULDER_FORMS)
PROPULSION_STYLES_MAP = _axis_to_dict(PROPULSION_STYLES)
PAINT_SCHEMES_MAP = _axis_to_dict(PAINT_SCHEMES)


def _axis_options(axis: List[tuple], lang: str, auto_label_en: str, auto_label_zh: str) -> List[str]:
    """Returns picker labels with 'Auto' first."""
    auto = auto_label_zh if lang == "zh" else auto_label_en
    out = [auto]
    for entry in axis:
        _key, en, zh, _prompt, _hint = _unpack(entry)
        if lang == "zh":
            out.append(f"{zh} ({en})")
        else:
            out.append(en)
    return out


def _axis_label_to_key(axis: List[tuple], lang: str, auto_label_en: str, auto_label_zh: str) -> Dict[str, Optional[str]]:
    """Reverse map: label -> key (or None for Auto)."""
    auto = auto_label_zh if lang == "zh" else auto_label_en
    mapping: Dict[str, Optional[str]] = {auto: None}
    for entry in axis:
        key, en, zh, _prompt, _hint = _unpack(entry)
        label = f"{zh} ({en})" if lang == "zh" else en
        mapping[label] = key
    return mapping


def _axis_hints(axis: List[tuple], lang: str, auto_label_en: str, auto_label_zh: str,
                auto_hint_en: str, auto_hint_zh: str) -> Dict[str, str]:
    """label -> hint string (empty if no hint). Auto label gets the auto-hint."""
    auto = auto_label_zh if lang == "zh" else auto_label_en
    auto_hint = auto_hint_zh if lang == "zh" else auto_hint_en
    out: Dict[str, str] = {auto: auto_hint}
    for entry in axis:
        _key, en, zh, _prompt, hint = _unpack(entry)
        label = f"{zh} ({en})" if lang == "zh" else en
        text = hint.get(lang) or hint.get("en", "") if isinstance(hint, dict) else ""
        out[label] = text
    return out


_AUTO_EN = "Auto (random / by designer)"
_AUTO_ZH = "自动（随机 / 由设计师决定）"
_AUTO_HINT_EN = "Random pick when no designer is selected; deferred to designer signature when one is selected."
_AUTO_HINT_ZH = "未选机设师时随机抽取；选了机设师则交给机设师的签名风格决定。"


def get_sensor_module_options(lang: str = "en") -> List[str]:
    return _axis_options(SENSOR_MODULES, lang, _AUTO_EN, _AUTO_ZH)


def get_sensor_module_label_map(lang: str = "en") -> Dict[str, Optional[str]]:
    return _axis_label_to_key(SENSOR_MODULES, lang, _AUTO_EN, _AUTO_ZH)


def get_sensor_module_hints(lang: str = "en") -> Dict[str, str]:
    return _axis_hints(SENSOR_MODULES, lang, _AUTO_EN, _AUTO_ZH, _AUTO_HINT_EN, _AUTO_HINT_ZH)


def get_surface_treatment_options(lang: str = "en") -> List[str]:
    return _axis_options(SURFACE_TREATMENTS, lang, _AUTO_EN, _AUTO_ZH)


def get_surface_treatment_label_map(lang: str = "en") -> Dict[str, Optional[str]]:
    return _axis_label_to_key(SURFACE_TREATMENTS, lang, _AUTO_EN, _AUTO_ZH)


def get_surface_treatment_hints(lang: str = "en") -> Dict[str, str]:
    return _axis_hints(SURFACE_TREATMENTS, lang, _AUTO_EN, _AUTO_ZH, _AUTO_HINT_EN, _AUTO_HINT_ZH)


def get_shoulder_form_options(lang: str = "en") -> List[str]:
    return _axis_options(SHOULDER_FORMS, lang, _AUTO_EN, _AUTO_ZH)


def get_shoulder_form_label_map(lang: str = "en") -> Dict[str, Optional[str]]:
    return _axis_label_to_key(SHOULDER_FORMS, lang, _AUTO_EN, _AUTO_ZH)


def get_shoulder_form_hints(lang: str = "en") -> Dict[str, str]:
    return _axis_hints(SHOULDER_FORMS, lang, _AUTO_EN, _AUTO_ZH, _AUTO_HINT_EN, _AUTO_HINT_ZH)


def get_propulsion_style_options(lang: str = "en") -> List[str]:
    return _axis_options(PROPULSION_STYLES, lang, _AUTO_EN, _AUTO_ZH)


def get_propulsion_style_label_map(lang: str = "en") -> Dict[str, Optional[str]]:
    return _axis_label_to_key(PROPULSION_STYLES, lang, _AUTO_EN, _AUTO_ZH)


def get_propulsion_style_hints(lang: str = "en") -> Dict[str, str]:
    return _axis_hints(PROPULSION_STYLES, lang, _AUTO_EN, _AUTO_ZH, _AUTO_HINT_EN, _AUTO_HINT_ZH)


def get_paint_scheme_options(lang: str = "en") -> List[str]:
    return _axis_options(PAINT_SCHEMES, lang, _AUTO_EN, _AUTO_ZH)


def get_paint_scheme_label_map(lang: str = "en") -> Dict[str, Optional[str]]:
    return _axis_label_to_key(PAINT_SCHEMES, lang, _AUTO_EN, _AUTO_ZH)


def get_paint_scheme_hints(lang: str = "en") -> Dict[str, str]:
    return _axis_hints(PAINT_SCHEMES, lang, _AUTO_EN, _AUTO_ZH, _AUTO_HINT_EN, _AUTO_HINT_ZH)


# Back-compat: keep HEAD_STYLES alias pointing at sensor module prompt texts for
# the legacy auto-pick path.
HEAD_STYLES = [item[3] for item in SENSOR_MODULES]

# --- Mecha subcategory definitions ---
# Each subcategory keeps its OWN distinctive silhouette and features so the
# results across categories feel genuinely different — avoiding the
# Zaku/GM-hybrid trap where every output looks like a Federation grunt suit.

MECHA_SUBCATEGORIES: Dict[str, Dict] = {
    "Generalist": {
        "flavor": "general-purpose piloted bipedal combat machine",
        "silhouette_pool": [
            "balanced upright bipedal frame, head-to-body ratio around 1:7.5, neutral squared shoulders, slightly tapered torso, straight legs in a planted stance",
            "modern slim combat-machine proportions with long shins, short thighs, narrow waist segment, no decorative ornamentation",
            "lean upright frame with a squared chest segment, simple banded waist joint, and pillar-shaped legs with reinforced shins",
        ],
        "features_pool": [
            "double-layered chest plate with thin outer panels floating slightly above a darker inner frame",
            "simple segmented waist joint with a single horizontal armor band",
            "twin small maneuvering thruster ports at the small of the back",
            "flat trapezoidal forearm covers with edge venting slots",
            "shoulder-mounted equipment hardpoint sockets",
            "neutral attachment sockets on shoulders, back, and hips for mission-specific external loadouts",
        ],
    },
    "Heavy Assault": {
        "flavor": "heavy assault piloted combat machine",
        "silhouette_pool": [
            "barrel-chested heavyweight frame with oversized pauldrons, broad squared hips, planted column-like legs, the sensor module sunk low between the shoulders",
            "stocky bunker-grade proportions (head-to-body 1:6.5), oversized multi-layer chest armor, hip-mounted utility blocks, reinforced gauntlet forearms",
            "siege-grade walker silhouette with a low wide stance, one shoulder noticeably larger than the other carrying a heavy reinforced weapon mount cradle",
        ],
        "features_pool": [
            "asymmetric pauldron arrangement — one shoulder thicker and reinforced, the other flatter and shield-like",
            "multi-layer chest armor with prominent intake grilles along the upper edge",
            "reinforced wide leg armor with bolted-on knee guards",
            "exposed segmented coolant lines running along the neck and inner waist",
            "secondary lower armor skirt with reinforced hardpoint clamps for external supply containers",
            "reinforced gauntlet forearms with integrated muzzle ports",
            "twin large reactor exhaust vents on the upper back, no flight-style verniers",
        ],
    },
    "Sniper-Recon": {
        "flavor": "long-range marksman / reconnaissance piloted combat machine",
        "silhouette_pool": [
            "tall lean predator-stance frame (head-to-body 1:8), hunched forward, bent knees, narrow shoulders, elongated forward-jutting sensor module",
            "slim minimalist marksman frame with extended shins, narrow torso, low-profile shoulders, and an extended forward sensor module",
            "low-crouch silhouette with a forward-leaning torso, planted bracing leg posture, and a single shoulder-mounted long-range sensor mast",
        ],
        "features_pool": [
            "shoulder-mounted long-range sensor mast with a multi-element forward optical array",
            "slim lightweight armor panels, no oversized pauldrons",
            "elongated forward sensor module with a wraparound horizontal optic band",
            "narrow reinforced forearm bracing struts for recoil control",
            "low-profile leg stabilizer fins, no oversized thruster nozzles",
            "dorsal communications whip antenna mast",
            "single forearm-mounted spotter optics package",
        ],
    },
    "High-Mobility": {
        "flavor": "high-mobility space-combat piloted machine",
        "silhouette_pool": [
            "slim frame with an oversized rear backpack thruster cluster taller than the sensor module, layered apron skirt armor concealing leg-mounted verniers, swept shoulder fairings",
            "lightweight rapid-strike frame (head-to-body 1:7) with conformal vernier ports ringing every joint, slim limbs, and a streamlined low-drag sensor module",
            "ace-custom strike silhouette with a low-drag forward profile, slim limbs, and a dense distribution of small reaction-control thrusters across the entire frame",
        ],
        "features_pool": [
            "oversized backpack housing four to six main thruster nozzles in a clover or hex array",
            "shoulder vernier thruster pods with hinged covers",
            "layered apron-style skirt armor concealing leg-mounted verniers",
            "calf-mounted secondary thruster nozzles",
            "reaction-control vernier clusters ringing the forearms and elbows",
            "streamlined low-drag sensor module with a forward-canted profile",
            "swept aerodynamic shoulder fairings",
        ],
    },
    "Worker": {
        "flavor": "civilian / industrial labor piloted machine",
        "silhouette_pool": [
            "stocky human-scale operator frame (head-to-body 1:6) — wide hips, short stout legs, broad chest, hunched-forward operator stance, reads as heavy construction equipment with a pilot inside",
            "blocky utility frame with an exposed structural truss along the spine, oversized industrial manipulator arms, open windowed cockpit cage on the chest",
            "dockyard-class labor machine silhouette with one arm replaced by a fixed industrial tool, asymmetric counterweight block on the lower back, planted stabilizer legs",
        ],
        "features_pool": [
            "oversized industrial manipulator claws or hydraulic grippers in place of hands",
            "exposed hydraulic piston joints at elbows, knees, and ankles",
            "windowed cockpit canopy on the chest with hinge and latches",
            "civilian hazard-stripe paint markings and warning placards",
            "rotating beacon lights on the shoulders",
            "rear counterweight block on the lower back",
            "external tool attachment rails on the forearms — no weapon hardpoints",
        ],
    },
    "Variable": {
        "flavor": "convertible / dual-mode piloted machine that can reconfigure between a bipedal stance and a streamlined high-speed travel mode",
        "silhouette_pool": [
            "convertible humanoid (head-to-body 1:7) with a forward-pointing aerodynamic prow integrated into the chest, folded wing-like aero panels stowed against the back, leg modules that double as engine nacelles, visible transformation seams at the hips and shoulders",
            "convertible frame with prominent rotation joint mechanisms at hips and shoulders, conformal hardpoints on the wing roots, and a sensor module that retracts into the upper torso in travel mode",
            "convertible heavy-attacker silhouette with a chest-mounted forward prow, oversized leg engine nacelles, and folded aerodynamic panels stowed against the back",
        ],
        "features_pool": [
            "forward aerodynamic prow integrated into the chest plate",
            "folded aerodynamic wing-panels stowed against the back",
            "visible transformation rotation joint mechanisms at hips and shoulders",
            "integrated leg thruster nacelles that double as travel-mode engines",
            "sensor module that retracts into the upper torso in travel mode",
            "wing-root hardpoints for conformal external stores",
            "reaction-control vernier strips along the wing leading edges",
        ],
    },
}


def _pick_silhouette(spec: Dict) -> str:
    """Backwards-compatible silhouette picker — prefer pool, fall back to legacy field."""
    pool = spec.get("silhouette_pool")
    if pool:
        return random.choice(pool)
    return spec.get("silhouette", "humanoid mecha frame")


def _pick_head_style() -> str:
    return random.choice(HEAD_STYLES)


MECHA_VARIANTS = ["Standard", "Space-Type", "Sky-Type", "Ground-Type", "Prototype"]


def _variant_descriptor(variation: Optional[str]) -> str:
    if not variation or variation == "Standard":
        return ""
    if variation == "Space-Type":
        return ("STRUCTURAL VARIANT: Space-type configuration — additional vernier "
                "thruster clusters on the limbs and back, no atmospheric stabilizers.")
    if variation == "Sky-Type":
        return ("STRUCTURAL VARIANT: Atmospheric high-altitude configuration — "
                "added aerodynamic stabilizer fins, intake ducts on the chest, "
                "swept aerodynamic shoulder fairings.")
    if variation == "Ground-Type":
        return ("STRUCTURAL VARIANT: Ground combat configuration — heavy reinforced "
                "leg armor for terrestrial weight bearing, exposed cooling intakes, "
                "no large vernier thrusters, optional shoulder ammo storage.")
    if variation == "Prototype":
        return ("STRUCTURAL VARIANT: Prototype configuration — exposed internal "
                "framework visible at certain joints, test-bed sensor packages "
                "bolted on, partially unpainted primer panels.")
    return ""


# --- OpenAI / GPT-image prose vocabulary -------------------------------------
# These mirror the variant / subcategory data above but in plain prose, for the
# labeled-section GPT-image template (no FORBIDDEN/LOCKED uppercase blocks).

_OPENAI_VARIANT_ADJ = {
    "Standard":    "production-model",
    "Space-Type":  "space-type",
    "Sky-Type":    "atmospheric-type",
    "Ground-Type": "ground-type",
    "Prototype":   "prototype",
}

_OPENAI_VARIANT_FEELING = {
    "Standard":    "clean finished production-model feeling, no unpainted panels",
    "Space-Type":  "space-type configuration feeling, extra vernier thruster clusters on the limbs and back, no atmospheric stabilizers",
    "Sky-Type":    "atmospheric high-altitude feeling, aerodynamic stabilizer fins and chest intake ducts, swept shoulder fairings",
    "Ground-Type": "ground-combat feeling, heavy reinforced leg armor and exposed cooling intakes, no large vernier thrusters",
    "Prototype":   "prototype test-unit feeling, exposed but believable joint mechanics, partially unpainted primer panels",
}

_OPENAI_SUBCAT_SILHOUETTE_ADJ = {
    "Generalist":    "balanced, clean, readable",
    "Heavy Assault": "heavy, broad-shouldered, planted",
    "Sniper-Recon":  "tall, lean, forward-leaning",
    "High-Mobility": "lean, slender, agile",
    "Worker":        "stocky, industrial, utilitarian",
    "Variable":      "convertible, aerodynamic, streamlined",
}


class MechaGenerator(pg.ComponentGenerator):
    def __init__(
        self,
        tier: pg.Tier,
        subcategory: str,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        manufacturer_data: Optional[Dict] = None,
        variation: Optional[str] = None,
        designers: Optional[List[Dict]] = None,
        sensor_module_key: Optional[str] = None,
        surface_treatment_key: Optional[str] = None,
        shoulder_form_key: Optional[str] = None,
        propulsion_style_key: Optional[str] = None,
        paint_scheme_key: Optional[str] = None,
    ):
        # Reuse the WEAPON enum slot purely so the base class is happy; the
        # category label is overridden in generate_full_prompt.
        super().__init__(
            tier,
            pg.ComponentType.WEAPON,
            subcategory,
            primary_color,
            secondary_color,
            manufacturer_data,
            variation,
        )
        self.designers = designers or []
        self.sensor_module_key = sensor_module_key
        self.surface_treatment_key = surface_treatment_key
        self.shoulder_form_key = shoulder_form_key
        self.propulsion_style_key = propulsion_style_key
        self.paint_scheme_key = paint_scheme_key

    # --- Mecha-specific negative prompt ---
    def _get_mecha_negative_prompt(self) -> str:
        # Forbidden visual elements are described purely as FORMS, never by
        # franchise name — naming a franchise (even negatively) anchors the
        # model to it.
        return ("**MECHA-SPECIFIC FORBIDDEN ELEMENTS:**\n"
                "- The machine must be depicted in BARE-FRAME state — NO held weapons, "
                "NO rifles, NO swords, NO shields, NO external missile pods, NO detachable "
                "equipment backpacks.\n"
                "- NO super-deformed (SD) or chibi proportions. Realistic plausible mechanical proportions only.\n"
                "- NO pilot figure visible outside the cockpit.\n"
                "- NO ground / scenery / cockpit interior — only the machine itself.\n"
                "- NO panel-line annotation, NO callout text, NO scale-figure silhouette next to the machine.\n"
                "- NO grid borders or panel separator lines drawn between the four views.\n"
                "- FORBIDDEN FORMS — avoid these specific shapes regardless of context:\n"
                "  * NO forehead-mounted 'V'-shaped fin antenna or any variation thereof on the sensor module\n"
                "  * NO single horizontal slit-eye visor on a turret-style cylindrical head\n"
                "  * NO segmented exposed corrugated tube/pipe loops at the neck or waist\n"
                "  * NO cross-shaped or 'plus'-shaped facial visor patterns\n"
                "  * NO twin small antenna prongs sprouting symmetrically from the top of the sensor module\n"
                "  * NO exposed humanoid 'face' features (lips, nose, mouth, eyebrows) on the sensor module — it is a sensor housing, not a face\n"
                "  * The sensor module / head MUST read as a piece of armored equipment, NOT as a stylized humanoid face")

    def _designer_signature_line(self) -> str:
        if not self.designers:
            return ""
        names = ", ".join(d["name"] for d in self.designers)
        sigs = "  ".join(d.get("signature", "").strip() for d in self.designers if d.get("signature"))
        sigs = sigs.strip()
        line = (f"DESIGNER SIGNATURE — DRIVE THE SILHOUETTE FROM THIS: "
                f"This machine is designed by {names}, and the entire silhouette, sensor "
                f"module shape, and surface treatment must follow that designer's distinctive "
                f"visual vocabulary as described below. Let the designer's signature dominate "
                f"every form decision.\n"
                f"Designer vocabulary: {sigs}")
        return line

    def _resolve_axis(self, key: Optional[str], axis_map: Dict[str, Dict],
                      auto_pool: List[tuple]) -> Optional[str]:
        """If a key is locked, return its prompt text. If unlocked (None) and no
        designer is dominating, randomly pick from the pool. If unlocked and a
        designer IS picked, return None — let the designer signature dominate."""
        if key:
            entry = axis_map.get(key)
            if entry:
                return entry["prompt"]
            return None
        if self.designers:
            return None
        return random.choice(auto_pool)[3]

    def generate_subject_description(self) -> str:
        spec = MECHA_SUBCATEGORIES.get(self.subcategory)
        if not spec:
            spec = MECHA_SUBCATEGORIES["Generalist"]

        tier_data = self.get_tier_data()
        tier_adj = tier_data["adjectives"][0]
        tier_secondary = tier_data["adjectives"][1] if len(tier_data["adjectives"]) > 1 else tier_adj
        design_lang = self._get_design_language()

        flavor = spec["flavor"]
        silhouette = _pick_silhouette(spec)
        pool = list(spec["features_pool"])
        features = random.sample(pool, min(4, len(pool)))
        feature_prose = "; ".join(features)

        designer_line = self._designer_signature_line()
        variant_line = _variant_descriptor(self.variation)

        # Resolve the five control axes. Locked values always emit; Auto values
        # only emit when no designer is picked (so designer signatures stay in
        # charge). Locked values ALWAYS override designer signature on that axis,
        # because a locked value is a deliberate user choice.
        sensor_text = self._resolve_axis(self.sensor_module_key, SENSOR_MODULES_MAP, SENSOR_MODULES)
        surface_text = self._resolve_axis(self.surface_treatment_key, SURFACE_TREATMENTS_MAP, SURFACE_TREATMENTS)
        shoulder_text = self._resolve_axis(self.shoulder_form_key, SHOULDER_FORMS_MAP, SHOULDER_FORMS)
        propulsion_text = self._resolve_axis(self.propulsion_style_key, PROPULSION_STYLES_MAP, PROPULSION_STYLES)
        paint_text = self._resolve_axis(self.paint_scheme_key, PAINT_SCHEMES_MAP, PAINT_SCHEMES)

        # Locked axes get a stronger override prefix
        def _axis_line(label: str, text: Optional[str], locked: bool) -> Optional[str]:
            if not text:
                return None
            if locked:
                return f"{label} (LOCKED — must follow exactly): {text}."
            return f"{label}: {text}."

        sensor_line = _axis_line("Sensor module / head treatment", sensor_text,
                                 locked=bool(self.sensor_module_key))
        surface_line = _axis_line("Surface treatment", surface_text,
                                  locked=bool(self.surface_treatment_key))
        shoulder_line = _axis_line("Shoulder armor form", shoulder_text,
                                   locked=bool(self.shoulder_form_key))
        propulsion_line = _axis_line("Propulsion configuration", propulsion_text,
                                     locked=bool(self.propulsion_style_key))
        paint_line = _axis_line("Paint scheme format", paint_text,
                                locked=bool(self.paint_scheme_key))

        lines = [
            f"SUBJECT DESCRIPTION ({tier_adj} {flavor}):",
            (f"This is a complete bare-frame piloted bipedal combat machine — a {tier_secondary} "
             f"{flavor}. The machine is shown WITHOUT any weapons or external equipment "
             "so its base airframe is fully visible."),
            f"Silhouette: {silhouette}.",
        ]
        for line in (sensor_line, shoulder_line, surface_line, propulsion_line, paint_line):
            if line:
                lines.append(line)
        if designer_line:
            lines.append(designer_line)
        lines.append(f"Design language: {design_lang}")
        if variant_line:
            lines.append(variant_line)
        lines.append(
            "Visible structural features (drawn as part of the geometry, NOT labeled "
            f"with text): {feature_prose}."
        )
        return "\n".join(lines)

    # --- OpenAI / GPT-image colour resolution ---
    def _openai_palette(self) -> tuple:
        """Returns (color_word, subject_colors, palette_line) for the GPT-image
        template. Mecha has no per-unit colour picker, so the default is the
        validated white-dominant prototype palette; manufacturer or explicit
        colours override it."""
        if self.manufacturer_data and self.manufacturer_data.get("color_palette"):
            pal = self.manufacturer_data["color_palette"].rstrip(".")
            color_word = pal.split(",")[0].split()[0].lower()
            subject = (f"armored in {pal.lower()}, with small restrained accent "
                       "colors on sensor details and dark graphite joints")
            return color_word, subject, pal
        if self.primary_color and self.secondary_color:
            p, s = self.primary_color, self.secondary_color
            subject = (f"{p} primary armor, subtle {s} panel breaks, small restrained "
                       "accent colors on sensor details and dark graphite joints")
            palette_line = (f"{p} dominant, {s} secondary panels, dark graphite inner "
                            "frame, small muted accent sensors only")
            return p.lower(), subject, palette_line
        subject = ("white primary armor, subtle cool gray panel breaks, small restrained "
                   "accent colors such as muted red sensor details and dark graphite joints")
        palette_line = ("white dominant, cool gray mechanical joints, dark graphite inner "
                        "frame, small muted red or amber sensors only")
        return "white", subject, palette_line

    def _assemble_openai(self) -> str:
        """Labeled-section prose prompt for GPT-image / reasoning-enhanced models."""
        spec = MECHA_SUBCATEGORIES.get(self.subcategory, MECHA_SUBCATEGORIES["Generalist"])
        tier_adj = self.get_tier_data()["adjectives"][0]

        variant = self.variation or "Standard"
        variant_adj = _OPENAI_VARIANT_ADJ.get(variant, "production-model")
        variant_feeling = _OPENAI_VARIANT_FEELING.get(variant, "")
        sil_adj = _OPENAI_SUBCAT_SILHOUETTE_ADJ.get(self.subcategory, "clean, readable")

        color_word, subject_colors, palette_line = self._openai_palette()

        # Designer attribution / signature
        if self.designers:
            names = ", ".join(d["name"] for d in self.designers)
            designer_phrase = f"the top mechanical designer {names}"
            sigs = " ".join(d.get("signature", "").strip()
                            for d in self.designers if d.get("signature")).strip()
            designer_clause = (f", following the design vocabulary of {names}"
                               + (f" ({sigs})" if sigs else ""))
        else:
            designer_phrase = "a top mechanical designer"
            designer_clause = ""

        # Subcategory silhouette + features (shared data layer)
        silhouette = _pick_silhouette(spec)
        pool = list(spec["features_pool"])
        features = random.sample(pool, min(4, len(pool)))
        feature_prose = "; ".join(features)

        # Five control axes — prose only, no LOCKED/uppercase for OpenAI.
        sensor_text = self._resolve_axis(self.sensor_module_key, SENSOR_MODULES_MAP, SENSOR_MODULES)
        surface_text = self._resolve_axis(self.surface_treatment_key, SURFACE_TREATMENTS_MAP, SURFACE_TREATMENTS)
        shoulder_text = self._resolve_axis(self.shoulder_form_key, SHOULDER_FORMS_MAP, SHOULDER_FORMS)
        propulsion_text = self._resolve_axis(self.propulsion_style_key, PROPULSION_STYLES_MAP, PROPULSION_STYLES)
        paint_text = self._resolve_axis(self.paint_scheme_key, PAINT_SCHEMES_MAP, PAINT_SCHEMES)

        subject_axis = "; ".join(t for t in (sensor_text, shoulder_text, propulsion_text) if t)

        subject_bits = [
            "one original humanoid mecha, consistent design across all views",
            subject_colors,
            variant_feeling,
            f"{'an' if tier_adj[:1].lower() in 'aeiou' else 'a'} {tier_adj} "
            f"{spec['flavor']} with a {sil_adj} silhouette",
            silhouette,
            feature_prose,
        ]
        if subject_axis:
            subject_bits.append(subject_axis)
        if designer_clause:
            subject_bits.append(designer_clause.lstrip(", "))
        subject_line = "; ".join(b for b in subject_bits if b)

        palette_full = palette_line
        if paint_text:
            palette_full = f"{palette_line}; paint applied as {paint_text}"

        materials = ("painted anime armor plating, fine panel lines, vents, verniers, "
                     "cables, sensor blocks, mechanical knees and elbows, plausible layered armor")
        if surface_text:
            materials = f"{materials}; {surface_text}"

        constraints = (
            "four views must describe the same design; pure white background; no logos; "
            "no readable text; no pilot; no weapons held in hands; no external equipment "
            "or detachable backpacks; bare-frame state only; no scenery; no watermark; "
            f"keep the silhouette {sil_adj} and clearly readable; avoid bulky superhero "
            "proportions, modern glossy 3D render style, excessive greebles, battle damage, "
            "and painterly backgrounds"
        )

        sections = [
            "Use case: stylized-concept",
            "Asset type: mecha concept art asset sheet, preview image",
            (f"Primary request: Design a {color_word}-dominant {variant_adj} mecha with a "
             f"{sil_adj} silhouette, as if created by {designer_phrase} for a 1990s "
             "Japanese OVA animation."),
            "Scene/backdrop: pure white seamless background, no environment, no shadows, no gradients.",
            f"Subject: {subject_line}.",
            ("Style/medium: anime cel hand-painted mechanical design sheet, 1990s OVA look, "
             "clean ink lines, limited color palette, flat cel shading, hand-drawn production "
             "art texture, crisp but not photorealistic."),
            ("Composition/framing: a clean 2x2 four-panel layout on one image, equal spacing "
             "and scale, showing the same mecha in front view, side view, top view, and "
             "orthographic three-quarter view; each view fully visible, centered, with generous "
             "white margin; technical model-sheet clarity without written labels."),
            "Lighting/mood: neutral studio-like cel shading, minimal highlights, no dramatic lighting.",
            f"Color palette: {palette_full}.",
            f"Materials/textures: {materials}.",
            f"Constraints: {constraints}.",
        ]
        return "\n".join(sections) + "\n"

    def generate_full_prompt(self, backend: str = "gemini") -> str:
        if backend == "openai":
            return self._assemble_openai()

        tier_adj = self.get_tier_data()["adjectives"][0]
        spec = MECHA_SUBCATEGORIES.get(self.subcategory, MECHA_SUBCATEGORIES["Generalist"])
        flavor = spec["flavor"]

        subject_name = f"{tier_adj} {self.subcategory} {flavor}"
        if self.manufacturer_data:
            subject_name = f"{self.manufacturer_data['name']} {subject_name}"
        if self.variation and self.variation != "Standard":
            subject_name += f" ({self.variation})"
        if self.designers:
            subject_name += f" — designed by {', '.join(d['name'] for d in self.designers)}"

        header = (f"# \n\n`A 2x2 grid illustration (NO TEXT, NO LABELS, NO ARROWS, "
                  f"NO PANEL SEPARATOR LINES) showing 4 views of a BARE-FRAME piloted bipedal combat machine: {subject_name}.")

        return f"""{header}

{self._get_layout_criteria()}

{self._get_negative_prompt()}

{self._get_mecha_negative_prompt()}

{self.generate_subject_description()}

{self._get_view_protocol()}

{self._get_art_style()}`
"""


# --- UI helpers ---

SUBCATEGORY_ZH_MAP = {
    "Generalist": "通用机",
    "Heavy Assault": "重型突击",
    "Sniper-Recon": "狙击 / 侦察",
    "High-Mobility": "高机动",
    "Worker": "工程机",
    "Variable": "可变形",
}

VARIANT_ZH_MAP = {
    "Standard": "标准",
    "Space-Type": "太空型",
    "Sky-Type": "大气型",
    "Ground-Type": "地面型",
    "Prototype": "原型机",
}

TIER_ZH_MAP = {
    "TIER_1_CIVILIAN": "一阶 · 民用",
    "TIER_2_INDUSTRIAL": "二阶 · 工业",
    "TIER_3_MILITARY": "三阶 · 军用",
    "TIER_4_ELITE": "四阶 · 精英",
    "TIER_5_LEGENDARY": "五阶 · 传说",
}


def _bilingual(key: str, zh_map: Dict[str, str], lang: str) -> str:
    if lang != "zh":
        return key
    zh = zh_map.get(key)
    return f"{zh} ({key})" if zh else key


def get_subcategory_list() -> List[str]:
    return list(MECHA_SUBCATEGORIES.keys())


def get_subcategory_options(lang: str = "en") -> List[str]:
    return [_bilingual(k, SUBCATEGORY_ZH_MAP, lang) for k in MECHA_SUBCATEGORIES.keys()]


def get_subcategory_label_map(lang: str = "en") -> Dict[str, str]:
    return {_bilingual(k, SUBCATEGORY_ZH_MAP, lang): k for k in MECHA_SUBCATEGORIES.keys()}


def get_variant_list() -> List[str]:
    return list(MECHA_VARIANTS)


def get_variant_options(lang: str = "en") -> List[str]:
    return [_bilingual(k, VARIANT_ZH_MAP, lang) for k in MECHA_VARIANTS]


def get_variant_label_map(lang: str = "en") -> Dict[str, str]:
    return {_bilingual(k, VARIANT_ZH_MAP, lang): k for k in MECHA_VARIANTS}


def get_tier_options(lang: str = "en") -> List[str]:
    keys = [t.name for t in pg.Tier]
    return [_bilingual(k, TIER_ZH_MAP, lang) for k in keys]


def get_tier_label_map(lang: str = "en") -> Dict[str, str]:
    keys = [t.name for t in pg.Tier]
    return {_bilingual(k, TIER_ZH_MAP, lang): k for k in keys}


def generate_mecha_prompt_by_strings(
    tier_name: str,
    subcategory: str,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    manufacturer_name: Optional[str] = None,
    variation_name: Optional[str] = None,
    designer_names: Optional[List[str]] = None,
    sensor_module_key: Optional[str] = None,
    surface_treatment_key: Optional[str] = None,
    shoulder_form_key: Optional[str] = None,
    propulsion_style_key: Optional[str] = None,
    paint_scheme_key: Optional[str] = None,
    backend: str = "gemini",
) -> str:
    try:
        tier = pg.Tier[tier_name]
    except KeyError:
        return "Error: Invalid Tier"

    if subcategory not in MECHA_SUBCATEGORIES:
        return f"Error: Unknown mecha subcategory '{subcategory}'"

    manufacturer_data = None
    if manufacturer_name and manufacturer_name not in (None, "None", "None / Generic"):
        manufacturer_data = pg.get_manufacturer_by_name(manufacturer_name)

    designers = []
    for n in designer_names or []:
        d = get_designer_by_name(n)
        if d:
            designers.append(d)

    gen = MechaGenerator(
        tier=tier,
        subcategory=subcategory,
        primary_color=primary_color,
        secondary_color=secondary_color,
        manufacturer_data=manufacturer_data,
        variation=variation_name,
        designers=designers,
        sensor_module_key=sensor_module_key,
        surface_treatment_key=surface_treatment_key,
        shoulder_form_key=shoulder_form_key,
        propulsion_style_key=propulsion_style_key,
        paint_scheme_key=paint_scheme_key,
    )
    return gen.generate_full_prompt(backend=backend)


if __name__ == "__main__":
    out = generate_mecha_prompt_by_strings(
        "TIER_3_MILITARY",
        "Heavy Assault",
        manufacturer_name="Titan Heavy Industries",
        variation_name="Ground-Type",
        designer_names=["Kanetake Ebikawa"],
    )
    print(out)
