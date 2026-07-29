from typing import Dict, List, Optional
import json
import os
from paths import resource_path
from . import _options_shared as _shared

_make_options = _shared.make_options
_make_option_map = _shared.make_option_map
_make_label_map = _shared.make_label_map
_label_to_value = _shared.label_to_value
_labels_to_values = _shared.labels_to_values
_localize_text = _shared.localize_text
_get_option_pairs = _shared.get_option_pairs

DEFAULT_STYLE = (
    "(masterpiece, best quality), late-1980s to early-2000s Japanese mecha OVA or theatrical key visual, "
    "real-robot anime aesthetic, hand-drawn cel animation still, hand-painted cel shading, "
    "flat color fills, hard-edged shadow shapes, clean lineart, crisp forms, "
    "limited palette, subtle color banding, minimal gradients, bold graphic silhouettes, "
    "utilitarian military sci-fi design, realistic 90s facial proportions, restrained eye highlights, "
    "cinematic composition, analog texture."
)

DEFAULT_BACKGROUND = "simple pure white background, flat white background, isolated on white."
DEFAULT_MOOD = (
    "(film grain:1.3), muted colors, vintage OVA atmosphere, hand-painted cel look, "
    "matte finish, clean paint layers, subtle cel misregistration, analog video texture, "
    "no oily or glossy look, no modern anime sheen, no oversized eyes, no soft glow, "
    "no 3d, no cgi, no photorealism, no digital painting look, no painterly brushwork, "
    "no thick paint, no heavy impasto, no soft focus, no depth of field."
)

STYLE_CONFIG_PATH = resource_path("character_style.json")
OPTIONS_CONFIG_PATH = resource_path("character_options.json")


def _load_style_config() -> Dict[str, str]:
    if not os.path.exists(STYLE_CONFIG_PATH):
        return {
            "style": DEFAULT_STYLE,
            "background": DEFAULT_BACKGROUND,
            "mood": DEFAULT_MOOD,
            "artists": [],
        }
    try:
        with open(STYLE_CONFIG_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return {
            "style": str(data.get("style", DEFAULT_STYLE)).strip() or DEFAULT_STYLE,
            "background": str(data.get("background", DEFAULT_BACKGROUND)).strip() or DEFAULT_BACKGROUND,
            "mood": str(data.get("mood", DEFAULT_MOOD)).strip() or DEFAULT_MOOD,
            "artists": list(data.get("artists", [])) if isinstance(data.get("artists", []), list) else [],
        }
    except (OSError, json.JSONDecodeError, TypeError):
        return {
            "style": DEFAULT_STYLE,
            "background": DEFAULT_BACKGROUND,
            "mood": DEFAULT_MOOD,
            "artists": [],
        }

def _age_to_descriptor(age_value: Optional[int]) -> Optional[str]:
    if age_value is None:
        return None
    try:
        age = int(age_value)
    except (TypeError, ValueError):
        return None
    if age <= 12:
        return "child"
    if age <= 17:
        return "teenager"
    if age <= 25:
        return "young adult"
    if age <= 39:
        return "adult"
    if age <= 49:
        return "middle-aged adult"
    return "mature adult"


def get_age_descriptor(age_value: Optional[int]) -> Optional[str]:
    return _age_to_descriptor(age_value)


def _color_to_descriptor(hex_color: str) -> str:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        return hex_color
    try:
        r = int(value[0:2], 16) / 255.0
        g = int(value[2:4], 16) / 255.0
        b = int(value[4:6], 16) / 255.0
    except ValueError:
        return hex_color

    max_c = max(r, g, b)
    min_c = min(r, g, b)
    v = max_c
    s = 0.0 if max_c == 0 else (max_c - min_c) / max_c

    if s < 0.12:
        if v > 0.9:
            return "white"
        if v < 0.2:
            return "black"
        return "gray"

    hue = 0.0
    if max_c == r:
        hue = (g - b) / (max_c - min_c)
    elif max_c == g:
        hue = 2.0 + (b - r) / (max_c - min_c)
    else:
        hue = 4.0 + (r - g) / (max_c - min_c)
    hue *= 60.0
    if hue < 0:
        hue += 360.0

    if hue < 20 or hue >= 340:
        base = "red"
    elif hue < 50:
        base = "orange"
    elif hue < 70:
        base = "yellow"
    elif hue < 160:
        base = "green"
    elif hue < 200:
        base = "cyan"
    elif hue < 250:
        base = "blue"
    elif hue < 290:
        base = "purple"
    else:
        base = "magenta"

    if v >= 0.8:
        tone = "light"
    elif v <= 0.35:
        tone = "dark"
    else:
        tone = "mid"

    if tone == "mid":
        return base
    return f"{tone} {base}"


def _colors_to_palette_text(colors: List[str]) -> Optional[str]:
    if not colors:
        return None
    descriptors = [_color_to_descriptor(c) for c in colors]
    return ", ".join(descriptors)


def _parse_artist_entries(raw) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    if not isinstance(raw, list):
        return entries
    for item in raw:
        if isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            work = item.get("work", "")
        else:
            name = str(item).strip()
            work = ""
        if name:
            entries.append({"name": name, "work": work})
    return entries


def get_artist_options(lang: str = "en") -> List[str]:
    cfg = _load_style_config()
    entries = _parse_artist_entries(cfg.get("artists", []))
    options = []
    label_prefix = "代表作" if lang == "zh" else "Works"
    for entry in entries:
        name = entry["name"]
        work = _localize_text(entry.get("work", ""), lang)
        if work:
            options.append(f"{name}（{label_prefix}：{work}）")
        else:
            options.append(name)
    return options


def get_artist_label_map(lang: str = "en") -> Dict[str, str]:
    cfg = _load_style_config()
    entries = _parse_artist_entries(cfg.get("artists", []))
    mapping: Dict[str, str] = {}
    label_prefix = "代表作" if lang == "zh" else "Works"
    for entry in entries:
        name = entry["name"]
        work = _localize_text(entry.get("work", ""), lang)
        label = f"{name}（{label_prefix}：{work}）" if work else name
        mapping[label] = name
    return mapping


def _load_options_config() -> Dict[str, List]:
    return _shared.load_options_config(OPTIONS_CONFIG_PATH)


def _merge_option_pairs(*pair_lists: List[tuple]) -> List[tuple]:
    seen = set()
    merged: List[tuple] = []
    for pairs in pair_lists:
        for en, zh in pairs:
            if en in seen:
                continue
            seen.add(en)
            merged.append((en, zh))
    return merged


GENDER_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("Male", "男性"),
    ("Female", "女性"),
    ("Androgynous", "中性"),
    ("Non-binary", "非二元"),
]
AGE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("Young adult", "青年"),
    ("Adult", "成年人"),
    ("Mature adult", "成熟成年人"),
]
FRAMING_OPTION_PAIRS = [
    ("head-and-shoulders portrait", "头像到肩部"),
    ("bust portrait", "胸像"),
    ("half body portrait", "半身"),
    ("three-quarter body portrait", "四分之三身"),
    ("full body portrait", "全身"),
]
ASPECT_RATIO_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("1:1 square", "1:1 方形"),
    ("2:3 portrait", "2:3 竖幅"),
    ("3:4 portrait", "3:4 竖幅"),
    ("9:16 vertical", "9:16 竖屏"),
    ("16:9 widescreen", "16:9 宽屏"),
]
EXPRESSION_OPTION_PAIRS = [
    ("serious expression", "严肃"),
    ("calm expression", "冷静"),
    ("focused expression", "专注"),
    ("confident expression", "自信"),
]
GAZE_OPTION_PAIRS = [
    ("looking at camera", "直视镜头"),
    ("looking slightly off-camera", "略微偏离镜头"),
    ("looking to the side", "侧视"),
]
APPEARANCE_OPTION_PAIRS = [
    ("sharp jawline", "清晰下颌线"),
    ("defined cheekbones", "高颧骨"),
    ("subtle freckles", "浅雀斑"),
    ("beauty mark", "美人痣"),
    ("brow slit", "眉间划痕"),
    ("dark eye circles", "眼下阴影"),
    ("soft blush", "微红腮"),
    ("sharp eyeliner", "锐利眼线"),
    ("glossy lips", "光泽唇彩"),
    ("scar across cheek", "脸颊疤痕"),
    ("nose bridge bandage", "鼻梁贴"),
    ("stern eyebrows", "浓眉"),
    ("hardened eyes", "坚毅眼神"),
    ("asymmetrical bangs", "不对称刘海"),
    ("messy fringe", "凌乱刘海"),
    ("heterochromia", "异色瞳"),
]
BODY_TYPE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("slim build", "纤细"),
    ("athletic build", "运动型"),
    ("lean build", "精瘦"),
    ("muscular build", "肌肉型"),
    ("stocky build", "壮实"),
    ("curvy build", "曲线明显"),
]
SKIN_TONE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("fair skin tone", "白皙肤色"),
    ("light skin tone", "浅肤色"),
    ("medium skin tone", "中等肤色"),
    ("tan skin tone", "小麦肤色"),
    ("dark skin tone", "深肤色"),
    ("deep skin tone", "黝黑肤色"),
]
HAIR_COLOR_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("black", "黑色"),
    ("dark brown", "深棕色"),
    ("brown", "棕色"),
    ("blonde", "金色"),
    ("silver", "银色"),
    ("white", "白色"),
    ("red", "红色"),
    ("blue", "蓝色"),
    ("green", "绿色"),
    ("purple", "紫色"),
]
HAIR_STYLE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("short cropped", "超短发"),
    ("pixie cut", "精灵短发"),
    ("short layered", "短层次"),
    ("bob cut", "波波头"),
    ("slicked back", "后梳"),
    ("long straight", "长直发"),
    ("long wavy", "长卷发"),
    ("twin tails", "双马尾"),
    ("high ponytail", "高马尾"),
    ("low ponytail", "低马尾"),
    ("braided", "编发"),
    ("half-up", "半扎发"),
    ("hime cut", "姬发式"),
    ("wolf cut", "狼尾"),
    ("undercut", "两侧剃短"),
    ("shaved sides", "侧剃"),
]
HAIR_STYLE_OPTION_PAIRS_MALE = [
    ("Unspecified", "未指定"),
    ("short cropped", "超短发"),
    ("short layered", "短层次"),
    ("slicked back", "后梳"),
    ("undercut", "两侧剃短"),
    ("shaved sides", "侧剃"),
    ("wolf cut", "狼尾"),
    ("pixie cut", "精灵短发"),
    ("bob cut", "波波头"),
]
HAIR_STYLE_OPTION_PAIRS_FEMALE = [
    ("Unspecified", "未指定"),
    ("pixie cut", "精灵短发"),
    ("bob cut", "波波头"),
    ("long straight", "长直发"),
    ("long wavy", "长卷发"),
    ("twin tails", "双马尾"),
    ("high ponytail", "高马尾"),
    ("low ponytail", "低马尾"),
    ("braided", "编发"),
    ("half-up", "半扎发"),
    ("hime cut", "姬发式"),
    ("wolf cut", "狼尾"),
]
HAIR_STYLE_OPTION_PAIRS_NEUTRAL = [
    ("Unspecified", "未指定"),
    ("short cropped", "超短发"),
    ("short layered", "短层次"),
    ("slicked back", "后梳"),
    ("bob cut", "波波头"),
    ("pixie cut", "精灵短发"),
    ("wolf cut", "狼尾"),
    ("undercut", "两侧剃短"),
    ("shaved sides", "侧剃"),
]
BANGS_PRESENCE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("with bangs", "有刘海"),
    ("no bangs", "无刘海"),
]
BANGS_STYLE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("straight bangs", "齐刘海"),
    ("side-swept bangs", "侧分刘海"),
    ("wispy bangs", "轻薄刘海"),
    ("choppy bangs", "碎刘海"),
    ("curtain bangs", "八字刘海"),
    ("baby bangs", "眉上刘海"),
]
FACE_SHAPE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("oval face", "椭圆脸"),
    ("round face", "圆脸"),
    ("square jawline", "方下颌"),
    ("heart-shaped face", "心形脸"),
    ("long face", "长脸"),
]
EYE_SIZE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("large eyes", "大眼"),
    ("medium eyes", "中等眼"),
    ("narrow eyes", "细长眼"),
]
NOSE_SIZE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("small nose", "小鼻"),
    ("refined nose", "精致鼻"),
    ("prominent nose", "高挺鼻"),
]
MOUTH_SHAPE_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("thin lips", "薄唇"),
    ("balanced lips", "标准唇"),
    ("full lips", "厚唇"),
    ("subtle smile", "微笑唇"),
]
CHEEK_FULLNESS_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("soft cheeks", "柔和脸颊"),
    ("defined cheekbones", "清晰颧骨"),
    ("hollow cheeks", "凹陷脸颊"),
]
JAW_WIDTH_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("narrow jaw", "窄下颌"),
    ("balanced jaw", "标准下颌"),
    ("wide jaw", "宽下颌"),
]
EYE_COLOR_OPTION_PAIRS = [
    ("Unspecified", "未指定"),
    ("brown", "棕色"),
    ("blue", "蓝色"),
    ("green", "绿色"),
    ("hazel", "榛色"),
    ("amber", "琥珀色"),
    ("gray", "灰色"),
    ("red (cybernetic glow)", "红色（义眼发光）"),
]
CLOTHING_HINT_OPTION_PAIRS = [
    ("plain neutral garment", "素色中性服装"),
    ("military uniform", "军装"),
    ("flight suit", "飞行服"),
    ("casual clothing", "便装"),
    ("school uniform", "校服"),
    ("formal attire", "正装"),
    ("work coveralls", "工装"),
]

OPTIONS_CONFIG = _load_options_config()
GENDER_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "gender_options", GENDER_OPTION_PAIRS)
AGE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "age_options", AGE_OPTION_PAIRS)
FRAMING_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "framing_options", FRAMING_OPTION_PAIRS)
ASPECT_RATIO_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "aspect_ratio_options", ASPECT_RATIO_OPTION_PAIRS)
EXPRESSION_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "expression_options", EXPRESSION_OPTION_PAIRS)
GAZE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "gaze_options", GAZE_OPTION_PAIRS)
APPEARANCE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "appearance_features", APPEARANCE_OPTION_PAIRS)
BODY_TYPE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "body_type_options", BODY_TYPE_OPTION_PAIRS)
SKIN_TONE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "skin_tone_options", SKIN_TONE_OPTION_PAIRS)
HAIR_COLOR_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "hair_color_options", HAIR_COLOR_OPTION_PAIRS)
HAIR_STYLE_OPTION_PAIRS_MALE = _get_option_pairs(OPTIONS_CONFIG, "hair_style_options_male", HAIR_STYLE_OPTION_PAIRS_MALE)
HAIR_STYLE_OPTION_PAIRS_FEMALE = _get_option_pairs(OPTIONS_CONFIG, "hair_style_options_female", HAIR_STYLE_OPTION_PAIRS_FEMALE)
HAIR_STYLE_OPTION_PAIRS_NEUTRAL = _get_option_pairs(OPTIONS_CONFIG, "hair_style_options_neutral", HAIR_STYLE_OPTION_PAIRS_NEUTRAL)
HAIR_STYLE_OPTION_PAIRS = _merge_option_pairs(
    HAIR_STYLE_OPTION_PAIRS_MALE,
    HAIR_STYLE_OPTION_PAIRS_FEMALE,
    HAIR_STYLE_OPTION_PAIRS_NEUTRAL,
)
HAIR_STYLE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "hair_style_options", HAIR_STYLE_OPTION_PAIRS)
BANGS_PRESENCE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "bangs_presence_options", BANGS_PRESENCE_OPTION_PAIRS)
BANGS_STYLE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "bangs_style_options", BANGS_STYLE_OPTION_PAIRS)
FACE_SHAPE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "face_shape_options", FACE_SHAPE_OPTION_PAIRS)
EYE_SIZE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "eye_size_options", EYE_SIZE_OPTION_PAIRS)
NOSE_SIZE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "nose_size_options", NOSE_SIZE_OPTION_PAIRS)
MOUTH_SHAPE_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "mouth_shape_options", MOUTH_SHAPE_OPTION_PAIRS)
CHEEK_FULLNESS_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "cheek_fullness_options", CHEEK_FULLNESS_OPTION_PAIRS)
JAW_WIDTH_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "jaw_width_options", JAW_WIDTH_OPTION_PAIRS)
EYE_COLOR_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "eye_color_options", EYE_COLOR_OPTION_PAIRS)
CLOTHING_HINT_OPTION_PAIRS = _get_option_pairs(OPTIONS_CONFIG, "clothing_hint_options", CLOTHING_HINT_OPTION_PAIRS)

def get_clothing_hint_options(lang: str = "en") -> List[str]:
    return _make_options(CLOTHING_HINT_OPTION_PAIRS, lang)


def get_gender_options(lang: str = "en") -> List[str]:
    return _make_options(GENDER_OPTION_PAIRS, lang)


def get_gender_label_map(lang: str = "en") -> Dict[str, str]:
    return _make_option_map(GENDER_OPTION_PAIRS, lang)


def get_age_options(lang: str = "en") -> List[str]:
    return _make_options(AGE_OPTION_PAIRS, lang)


def get_framing_options(lang: str = "en") -> List[str]:
    return _make_options(FRAMING_OPTION_PAIRS, lang)


def get_aspect_ratio_options(lang: str = "en") -> List[str]:
    return _make_options(ASPECT_RATIO_OPTION_PAIRS, lang)


def get_expression_options(lang: str = "en") -> List[str]:
    return _make_options(EXPRESSION_OPTION_PAIRS, lang)


def get_gaze_options(lang: str = "en") -> List[str]:
    return _make_options(GAZE_OPTION_PAIRS, lang)


def get_appearance_options(lang: str = "en") -> List[str]:
    return _make_options(APPEARANCE_OPTION_PAIRS, lang)


def get_body_type_options(lang: str = "en") -> List[str]:
    return _make_options(BODY_TYPE_OPTION_PAIRS, lang)


def get_skin_tone_options(lang: str = "en") -> List[str]:
    return _make_options(SKIN_TONE_OPTION_PAIRS, lang)


def get_hair_color_options(lang: str = "en") -> List[str]:
    return _make_options(HAIR_COLOR_OPTION_PAIRS, lang)


def get_hair_style_options(lang: str = "en") -> List[str]:
    return _make_options(HAIR_STYLE_OPTION_PAIRS, lang)


def get_hair_style_options_by_gender(lang: str = "en") -> Dict[str, List[str]]:
    return {
        "male": _make_options(HAIR_STYLE_OPTION_PAIRS_MALE, lang),
        "female": _make_options(HAIR_STYLE_OPTION_PAIRS_FEMALE, lang),
        "neutral": _make_options(HAIR_STYLE_OPTION_PAIRS_NEUTRAL, lang),
    }


def get_hair_style_label_map(lang: str = "en") -> Dict[str, str]:
    return _make_option_map(HAIR_STYLE_OPTION_PAIRS, lang)


def get_bangs_presence_options(lang: str = "en") -> List[str]:
    return _make_options(BANGS_PRESENCE_OPTION_PAIRS, lang)


def get_bangs_style_options(lang: str = "en") -> List[str]:
    return _make_options(BANGS_STYLE_OPTION_PAIRS, lang)


def get_bangs_style_label_map(lang: str = "en") -> Dict[str, str]:
    return _make_option_map(BANGS_STYLE_OPTION_PAIRS, lang)


def get_face_shape_options(lang: str = "en") -> List[str]:
    return _make_options(FACE_SHAPE_OPTION_PAIRS, lang)


def get_eye_size_options(lang: str = "en") -> List[str]:
    return _make_options(EYE_SIZE_OPTION_PAIRS, lang)


def get_nose_size_options(lang: str = "en") -> List[str]:
    return _make_options(NOSE_SIZE_OPTION_PAIRS, lang)


def get_mouth_shape_options(lang: str = "en") -> List[str]:
    return _make_options(MOUTH_SHAPE_OPTION_PAIRS, lang)


def get_cheek_fullness_options(lang: str = "en") -> List[str]:
    return _make_options(CHEEK_FULLNESS_OPTION_PAIRS, lang)


def get_jaw_width_options(lang: str = "en") -> List[str]:
    return _make_options(JAW_WIDTH_OPTION_PAIRS, lang)


def get_eye_color_options(lang: str = "en") -> List[str]:
    return _make_options(EYE_COLOR_OPTION_PAIRS, lang)




def _format_subject(
    framing: str,
    gender: Optional[str],
    age: Optional[str],
    body_type: Optional[str],
    clothing_hint: Optional[str],
    expression: str,
    gaze: str,
    appearance_features: List[str],
    skin_tone: Optional[str],
    hair_style: Optional[str],
    hair_color: Optional[str],
    hair_colors: List[str],
    hair_bangs_presence: Optional[str],
    hair_bangs_style: Optional[str],
    face_shape: Optional[str],
    eye_size: Optional[str],
    nose_size: Optional[str],
    mouth_shape: Optional[str],
    cheek_fullness: Optional[str],
    jaw_width: Optional[str],
    eye_color: Optional[str],
) -> str:
    descriptors = []
    if age and age != "Unspecified":
        descriptors.append(age.lower())
    if gender and gender != "Unspecified":
        descriptors.append(gender.lower())
    if body_type and body_type != "Unspecified":
        descriptors.append(body_type.lower())

    descriptor_str = " ".join(descriptors)
    if descriptor_str:
        subject = f"a {descriptor_str} character"
    else:
        subject = "a character"

    features = list(appearance_features)
    if skin_tone and skin_tone != "Unspecified":
        features.append(skin_tone)
    hair_palette = _colors_to_palette_text(hair_colors)
    if hair_style and hair_style != "Unspecified":
        if hair_color and hair_color != "Unspecified":
            if hair_palette:
                features.append(f"{hair_style} hair dyed in {hair_palette} tones")
            else:
                features.append(f"{hair_style} {hair_color} hair")
        else:
            if hair_palette:
                features.append(f"{hair_style} hair dyed in {hair_palette} tones")
            else:
                features.append(f"{hair_style} hair")
    elif hair_color and hair_color != "Unspecified":
        if hair_palette:
            features.append(f"hair dyed in {hair_palette} tones")
        else:
            features.append(f"{hair_color} hair")
    elif hair_palette:
        features.append(f"hair dyed in {hair_palette} tones")
    if hair_bangs_presence and hair_bangs_presence != "Unspecified":
        features.append(hair_bangs_presence)
    if hair_bangs_style and hair_bangs_style != "Unspecified":
        features.append(hair_bangs_style)
    if face_shape and face_shape != "Unspecified":
        features.append(face_shape)
    if eye_size and eye_size != "Unspecified":
        features.append(eye_size)
    if nose_size and nose_size != "Unspecified":
        features.append(nose_size)
    if mouth_shape and mouth_shape != "Unspecified":
        features.append(mouth_shape)
    if cheek_fullness and cheek_fullness != "Unspecified":
        features.append(cheek_fullness)
    if jaw_width and jaw_width != "Unspecified":
        features.append(jaw_width)
    if eye_color and eye_color != "Unspecified":
        features.append(f"{eye_color} eyes")

    feature_text = ""
    if features:
        feature_text = " with " + ", ".join(features)

    clothing_text = f"wearing a {clothing_hint}" if clothing_hint else "wearing a plain neutral garment"

    return f"{framing}, {subject} {clothing_text}{feature_text}, {expression}, {gaze}."


def generate_character_prompt(
    gender: str,
    age: int,
    framing: str,
    aspect_ratio: str,
    expression: str,
    gaze: str,
    appearance_features: List[str],
    body_type: str,
    skin_tone: str,
    hair_style: str,
    hair_color: str,
    hair_colors: List[str],
    hair_bangs_presence: str,
    hair_bangs_style: str,
    face_shape: str,
    eye_size: str,
    nose_size: str,
    mouth_shape: str,
    cheek_fullness: str,
    jaw_width: str,
    eye_color: str,
    clothing_hint: str,
    artists: List[str],
    lang: str = "en",
    extra_modifiers: str = "",
    include_style: bool = True,
    include_background: bool = True,
    include_mood: bool = True,
    include_extra_modifiers: bool = True,
) -> str:
    gender_value = _label_to_value(gender, _make_option_map(GENDER_OPTION_PAIRS, lang))
    age_value = _age_to_descriptor(age)
    framing_value = _label_to_value(framing, _make_option_map(FRAMING_OPTION_PAIRS, lang))
    aspect_ratio_value = _label_to_value(aspect_ratio, _make_option_map(ASPECT_RATIO_OPTION_PAIRS, lang))
    expression_value = _label_to_value(expression, _make_option_map(EXPRESSION_OPTION_PAIRS, lang))
    gaze_value = _label_to_value(gaze, _make_option_map(GAZE_OPTION_PAIRS, lang))
    body_type_value = _label_to_value(body_type, _make_option_map(BODY_TYPE_OPTION_PAIRS, lang))
    skin_tone_value = _label_to_value(skin_tone, _make_option_map(SKIN_TONE_OPTION_PAIRS, lang))
    hair_style_value = _label_to_value(hair_style, _make_option_map(HAIR_STYLE_OPTION_PAIRS, lang))
    hair_color_value = _label_to_value(hair_color, _make_option_map(HAIR_COLOR_OPTION_PAIRS, lang))
    bangs_presence_value = _label_to_value(hair_bangs_presence, _make_option_map(BANGS_PRESENCE_OPTION_PAIRS, lang))
    bangs_style_value = _label_to_value(hair_bangs_style, _make_option_map(BANGS_STYLE_OPTION_PAIRS, lang))
    face_shape_value = _label_to_value(face_shape, _make_option_map(FACE_SHAPE_OPTION_PAIRS, lang))
    eye_size_value = _label_to_value(eye_size, _make_option_map(EYE_SIZE_OPTION_PAIRS, lang))
    nose_size_value = _label_to_value(nose_size, _make_option_map(NOSE_SIZE_OPTION_PAIRS, lang))
    mouth_shape_value = _label_to_value(mouth_shape, _make_option_map(MOUTH_SHAPE_OPTION_PAIRS, lang))
    cheek_fullness_value = _label_to_value(cheek_fullness, _make_option_map(CHEEK_FULLNESS_OPTION_PAIRS, lang))
    jaw_width_value = _label_to_value(jaw_width, _make_option_map(JAW_WIDTH_OPTION_PAIRS, lang))
    eye_color_value = _label_to_value(eye_color, _make_option_map(EYE_COLOR_OPTION_PAIRS, lang))
    clothing_hint_value = _label_to_value(clothing_hint, _make_option_map(CLOTHING_HINT_OPTION_PAIRS, lang))

    appearance_values = _labels_to_values(appearance_features, _make_option_map(APPEARANCE_OPTION_PAIRS, lang))

    subject_line = _format_subject(
        framing=framing_value,
        gender=gender_value,
        age=age_value,
        body_type=body_type_value,
        clothing_hint=clothing_hint_value,
        expression=expression_value,
        gaze=gaze_value,
        appearance_features=appearance_values,
        skin_tone=skin_tone_value,
        hair_style=hair_style_value,
        hair_color=hair_color_value,
        hair_colors=hair_colors,
        hair_bangs_presence=bangs_presence_value,
        hair_bangs_style=bangs_style_value,
        face_shape=face_shape_value,
        eye_size=eye_size_value,
        nose_size=nose_size_value,
        mouth_shape=mouth_shape_value,
        cheek_fullness=cheek_fullness_value,
        jaw_width=jaw_width_value,
        eye_color=eye_color_value,
    )

    ratio_line = ""
    if aspect_ratio_value and aspect_ratio_value != "Unspecified":
        ratio_line = f"aspect ratio {aspect_ratio_value.split()[0]}."

    extra_line = extra_modifiers.strip() if include_extra_modifiers else ""

    parts = [subject_line]
    if ratio_line:
        parts.extend(["", ratio_line])
    style_cfg = _load_style_config()
    if include_style:
        style_line = style_cfg["style"]
        if artists:
            artist_text = ", ".join([a.strip() for a in artists if a.strip()])
            if artist_text:
                style_line = (
                    f"{style_line} strongly in the style of {artist_text}, "
                    f"character design and lineart influenced by {artist_text}."
                )
        parts = [style_line, ""] + parts
    if include_background:
        parts.extend(["", style_cfg["background"]])
    if include_mood:
        parts.extend(["", style_cfg["mood"]])
    if extra_line:
        parts.extend(["", extra_line])

    return "\n".join(parts).strip() + "\n"
