"""Batch-generate Arrokoth character portraits from the roster markdown.

This script is intentionally separate from the GUI save paths. It reads the
character art-spec table, builds one portrait prompt per character, and writes
images plus a JSONL manifest into a caller-provided output directory.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import gemini_service as gs  # noqa: E402
import character_generator as cg  # noqa: E402
import core.openai_service as oi  # noqa: E402
from core import library  # noqa: E402
from core.translation_service import TranslationManager  # noqa: E402
from paths import migrate_legacy_file  # noqa: E402


DEFAULT_ROSTER = Path(
    r"D:\Git\2d_space_project\docs\Worldbuilding\07_Arrokoth_Demo_Character_Roster.md"
)
DEFAULT_OUTDIR = ROOT / "batch_outputs" / "arrokoth_portrait_pilot"


@dataclass
class CharacterSpec:
    name: str
    priority: str
    age_temperament: str
    silhouette: str
    outfit: str
    portrait_marks: str
    seed_id: str = ""
    prompt_name: str = ""


def _read_config() -> dict:
    path = migrate_legacy_file("config.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _split_md_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|") or not line.endswith("|"):
        return []
    return [cell.strip() for cell in line.strip("|").split("|")]


def _iter_table_rows(markdown: str, heading: str) -> Iterable[list[str]]:
    lines = markdown.splitlines()
    in_section = False
    for line in lines:
        if line.startswith("## "):
            in_section = line.strip() == f"## {heading}"
            continue
        if not in_section:
            continue
        if line.startswith("## "):
            break
        row = _split_md_row(line)
        if row:
            yield row


def _parse_art_specs(markdown: str) -> list[CharacterSpec]:
    rows = list(_iter_table_rows(markdown, "角色美术规格"))
    specs: list[CharacterSpec] = []
    for row in rows:
        if len(row) < 6:
            continue
        if row[0] == "角色" or set(row[0]) <= {"-", ":"}:
            continue
        specs.append(
            CharacterSpec(
                name=row[0],
                priority=row[1],
                age_temperament=row[2],
                silhouette=row[3],
                outfit=row[4],
                portrait_marks=row[5],
            )
        )
    return specs


def _parse_roster_seed_ids(markdown: str) -> dict[str, str]:
    rows = list(_iter_table_rows(markdown, "角色名册"))
    ids: dict[str, str] = {}
    for row in rows:
        if len(row) < 8:
            continue
        if row[0] == "seed_id" or set(row[0]) <= {"-", ":"}:
            continue
        seed = row[0].strip("` ")
        name = row[2].strip()
        if seed and name:
            ids[name] = seed
    return ids


def load_character_specs(roster_path: Path) -> list[CharacterSpec]:
    markdown = roster_path.read_text(encoding="utf-8")
    specs = _parse_art_specs(markdown)
    seed_ids = _parse_roster_seed_ids(markdown)
    for spec in specs:
        spec.seed_id = seed_ids.get(spec.name, "")
        spec.prompt_name = _name_from_seed_id(spec.seed_id) or spec.name
    return specs


def _name_from_seed_id(seed_id: str) -> str:
    if not seed_id:
        return ""
    parts = seed_id.strip("` ").split("_")
    if len(parts) < 4:
        return ""
    return " ".join(part.capitalize() for part in parts[3:] if part)


def slugify(text: str) -> str:
    if not text:
        return "character"
    slug = re.sub(r"[^A-Za-z0-9_\-]+", "_", text).strip("_")
    return slug or uuid.uuid5(uuid.NAMESPACE_DNS, text).hex[:12]


def _infer_gender(name: str) -> str:
    female_names = {
        "克里斯蒂娜", "佐伊", "席尔瓦", "玛拉", "比特莉丝", "萨莉", "埃琳娜",
        "凯伦", "杰西卡", "惠", "霞", "罗莎琳德", "萨曼莎",
    }
    if any(part in name for part in female_names):
        return "Female"
    male_names = {
        "凯德", "格雷", "奥伦", "艾格", "霍尔特", "卡缪", "兰治", "布尔",
        "奈恩", "利欧", "马利克", "洛克", "伊拉", "沃斯", "尼科",
    }
    if any(part in name for part in male_names):
        return "Male"
    return "Unspecified"


def _infer_age(spec: CharacterSpec) -> int:
    text = spec.age_temperament
    match = re.search(r"(\d{2})\s*(?:左右|初|中|后半|后段)?", text)
    if match:
        return max(10, min(60, int(match.group(1))))
    if "20 初" in text or "20 左右" in text:
        return 22
    if "20 中" in text:
        return 25
    if "20 后" in text:
        return 28
    if "30 初" in text:
        return 32
    if "30 中" in text:
        return 35
    if "30 后" in text:
        return 38
    if "40 初" in text:
        return 42
    if "40 中" in text:
        return 45
    if "40 后" in text:
        return 48
    if "50 后" in text:
        return 58
    if "50" in text:
        return 50
    return 35


def _infer_body_type(spec: CharacterSpec) -> str:
    text = spec.silhouette
    if any(k in text for k in ("高大强壮", "体格惊人", "肌肉")):
        return "muscular build"
    if any(k in text for k in ("矮壮", "厚肩", "宽肩", "壮", "厚重")):
        return "stocky build"
    if any(k in text for k in ("轻快结实", "结实", "精瘦")):
        return "athletic build"
    if any(k in text for k in ("偏瘦", "瘦长", "消瘦", "纤细", "清瘦")):
        return "slim build"
    return "Unspecified"


def _infer_clothing_hint(spec: CharacterSpec) -> str:
    text = spec.outfit
    if any(k in text for k in ("制服", "联邦", "军用", "安保")):
        return "military uniform"
    if any(k in text for k in ("飞行", "航行")):
        return "flight suit"
    if any(k in text for k in ("工服", "工装", "矿工", "背带", "防火", "防静电")):
        return "work coveralls"
    if any(k in text for k in ("西装", "正式", "长外套", "商会")):
        return "formal attire"
    if any(k in text for k in ("学生", "退学")):
        return "school uniform"
    if any(k in text for k in ("便装", "兜帽")):
        return "casual clothing"
    return "plain neutral garment"


def _infer_expression(spec: CharacterSpec) -> str:
    text = spec.age_temperament + spec.portrait_marks
    if any(k in text for k in ("自信", "挑衅")):
        return "confident expression"
    if any(k in text for k in ("专注", "锋利", "精确")):
        return "focused expression"
    if any(k in text for k in ("冷静", "克制", "稳定", "理性")):
        return "calm expression"
    return "serious expression"


def _infer_gaze(spec: CharacterSpec) -> str:
    text = spec.portrait_marks
    if any(k in text for k in ("侧视", "侧后", "不正视")):
        return "looking to the side"
    if any(k in text for k in ("直视", "稳定直视")):
        return "looking at camera"
    return "looking slightly off-camera"


def _infer_features(spec: CharacterSpec) -> list[str]:
    text = spec.portrait_marks + spec.age_temperament
    features: list[str] = []
    if "眼下阴影" in text or "缺睡眠" in text or "眼袋" in text:
        features.append("dark eye circles")
    if any(k in text for k in ("伤", "疤", "烫痕")):
        features.append("scar across cheek")
    if any(k in text for k in ("胡茬", "胡子")):
        features.append("stern eyebrows")
    if any(k in text for k in ("坚毅", "冷硬", "锐利", "挑衅", "清醒")):
        features.append("hardened eyes")
    if any(k in text for k in ("乱发", "凌乱", "风吹乱")):
        features.append("messy fringe")
    return features


def translate_specs_for_prompt(specs: list[CharacterSpec], enabled: bool = True) -> list[CharacterSpec]:
    if not enabled:
        return specs
    texts: list[str] = []
    for spec in specs:
        texts.extend([spec.age_temperament, spec.silhouette, spec.outfit, spec.portrait_marks])

    translated = TranslationManager().translate_list(texts, max_workers=2)
    translated_specs: list[CharacterSpec] = []
    cursor = 0
    for spec in specs:
        translated_specs.append(
            CharacterSpec(
                name=spec.name,
                priority=spec.priority,
                age_temperament=translated[cursor],
                silhouette=translated[cursor + 1],
                outfit=translated[cursor + 2],
                portrait_marks=translated[cursor + 3],
                seed_id=spec.seed_id,
                prompt_name=spec.prompt_name,
            )
        )
        cursor += 4
    return translated_specs


def _clean_translation(text: str) -> str:
    replacements = {
        "technophobic": "technically meticulous",
        "Technophobic": "Technically meticulous",
        "border captain": "frontier captain",
        "Federal": "Federation",
        "Federation old-style inner layer suit repair vest over": "old Federation inner suit with a repair vest over it",
        "Federation old-style inner layer suit outer cover repair vest": "old Federation inner suit with a repair vest over it",
        "The second half of 30": "Late 30s",
        "standing like he can take apart the equipment": "standing as if she could disassemble equipment",
    }
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = re.sub(r"\.+", ".", cleaned)
    return cleaned


def _sentence_fragment(text: str) -> str:
    return _clean_translation(text).strip().rstrip(". ")


def build_prompt(spec: CharacterSpec, backend: str = "gemini", inference_spec: CharacterSpec | None = None) -> str:
    source = inference_spec or spec
    extra = (
        f"Original character identity anchor: {spec.prompt_name or spec.name}; do not render written name text. "
        f"Arrokoth outer-solar-system frontier RPG portrait. "
        f"Age and temperament notes: {_sentence_fragment(spec.age_temperament)}. "
        f"Body silhouette and posture notes: {_sentence_fragment(spec.silhouette)}. "
        f"Clothing and equipment must include: {_sentence_fragment(spec.outfit)}. "
        f"Portrait recognition marks must include: {_sentence_fragment(spec.portrait_marks)}. "
        "One person only, clean readable face, mature non-cute character design, "
        "practical worn frontier clothing, no logo, no caption, no UI."
    )
    return cg.generate_character_prompt(
        gender=_infer_gender(source.name),
        age=_infer_age(source),
        framing="bust portrait",
        aspect_ratio="1:1 square",
        expression=_infer_expression(source),
        gaze=_infer_gaze(source),
        appearance_features=_infer_features(source),
        body_type=_infer_body_type(source),
        skin_tone="Unspecified",
        hair_style="Unspecified",
        hair_color="Unspecified",
        hair_colors=[],
        hair_bangs_presence="Unspecified",
        hair_bangs_style="Unspecified",
        face_shape="Unspecified",
        eye_size="Unspecified",
        nose_size="Unspecified",
        mouth_shape="Unspecified",
        cheek_fullness="Unspecified",
        jaw_width="Unspecified",
        eye_color="Unspecified",
        clothing_hint=_infer_clothing_hint(source),
        artists=[],
        lang="en",
        extra_modifiers=extra,
        include_style=True,
        include_background=True,
        include_mood=True,
        include_extra_modifiers=True,
        backend=backend,
    )


def _provider_from_config(config: dict, requested: str) -> str:
    if requested != "auto":
        return requested
    return "openai" if config.get("api_provider") == "OpenAI" else "gemini"


def _generate_image(prompt: str, provider: str, config: dict) -> tuple[bytes, str | None]:
    if provider == "openai":
        return oi.generate_image_bytes(
            prompt,
            api_key=config.get("openai_api_key", ""),
            model=config.get("openai_model") or oi.DEFAULT_MODEL,
            base_url=config.get("openai_base_url") or oi.DEFAULT_BASE_URL,
            size=config.get("openai_image_size") or "1024x1024",
            quality=config.get("openai_image_quality") or "auto",
        )
    return gs.generate_image_bytes(
        prompt,
        api_key=config.get("gemini_api_key", ""),
        model=config.get("gemini_model") or gs.DEFAULT_MODEL,
        text_last=True,
    )


def _extension_for_mime(mime: str | None) -> str:
    if not mime:
        return ".png"
    if mime == "image/jpeg":
        return ".jpg"
    if mime == "image/png":
        return ".png"
    if mime == "image/webp":
        return ".webp"
    return mimetypes.guess_extension(mime) or ".png"


def _write_manifest_line(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def run(args: argparse.Namespace) -> int:
    config = _read_config()
    provider = _provider_from_config(config, args.provider)
    outdir = Path(args.output_dir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    manifest_path = outdir / "manifest.jsonl"

    specs = load_character_specs(Path(args.roster))
    if args.priority:
        priorities = {p.strip().upper() for p in args.priority.split(",") if p.strip()}
        specs = [s for s in specs if s.priority.upper() in priorities]
    if args.limit_characters:
        specs = specs[: args.limit_characters]
    original_specs = list(specs)
    prompt_specs = translate_specs_for_prompt(specs, enabled=not args.no_translate_extra)

    batch_id = uuid.uuid4().hex
    print(f"Provider: {provider}")
    print(f"Output: {outdir}")
    print(f"Characters: {len(specs)}")
    print(f"Images per character: {args.images_per_character}")
    print(f"Batch: {batch_id}")

    if args.dry_run:
        for spec, source_spec in zip(prompt_specs, original_specs):
            record = {
                "type": "dry_run",
                "character": asdict(source_spec),
                "prompt_character": asdict(spec),
                "prompt": build_prompt(spec, backend=provider, inference_spec=source_spec),
                "batch_id": batch_id,
            }
            _write_manifest_line(manifest_path, record)
            print(f"DRY {spec.name}")
        return 0

    if provider == "openai" and not config.get("openai_api_key"):
        raise SystemExit("Missing OpenAI API key in config.")
    if provider == "gemini" and not config.get("gemini_api_key"):
        raise SystemExit("Missing Gemini API key in config.")

    for spec_index, (spec, source_spec) in enumerate(zip(prompt_specs, original_specs), start=1):
        character_slug = slugify(spec.seed_id or spec.name)
        character_dir = outdir / character_slug
        character_dir.mkdir(parents=True, exist_ok=True)
        prompt = build_prompt(spec, backend=provider, inference_spec=source_spec)

        prompt_path = character_dir / "prompt.txt"
        prompt_path.write_text(prompt, encoding="utf-8")

        for image_index in range(1, args.images_per_character + 1):
            started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            filename_base = f"{character_slug}_{image_index:02d}"
            print(f"[{spec_index}/{len(specs)}] {spec.name} image {image_index}/{args.images_per_character}")
            try:
                data, mime = _generate_image(prompt, provider, config)
                ext = _extension_for_mime(mime)
                image_path = character_dir / f"{filename_base}{ext}"
                image_path.write_bytes(data)
                record = {
                    "type": "image",
                    "status": "ok",
                    "batch_id": batch_id,
                    "provider": provider,
                    "model": (
                        config.get("openai_model") if provider == "openai"
                        else config.get("gemini_model")
                    ),
                    "started_at": started_at,
                    "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "character": asdict(source_spec),
                    "prompt_character": asdict(spec),
                    "image_index": image_index,
                    "image_path": str(image_path),
                    "prompt_path": str(prompt_path),
                    "prompt": prompt,
                }
                _write_manifest_line(manifest_path, record)
                if args.add_to_library:
                    library.add_entry(
                        generator_type="character",
                        params={
                            "source": "arrokoth_roster_cli",
                            "character": asdict(source_spec),
                            "prompt_character": asdict(spec),
                            "provider": provider,
                        },
                        prompt=prompt,
                        image_path=str(image_path),
                        source_batch_id=batch_id,
                        tags=["arrokoth", "portrait", spec.priority],
                    )
            except Exception as exc:
                record = {
                    "type": "image",
                    "status": "error",
                    "batch_id": batch_id,
                    "provider": provider,
                    "started_at": started_at,
                    "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "character": asdict(source_spec),
                    "prompt_character": asdict(spec),
                    "image_index": image_index,
                    "error": str(exc),
                    "prompt": prompt,
                }
                _write_manifest_line(manifest_path, record)
                print(f"ERROR {spec.name} #{image_index}: {exc}")
                if not args.continue_on_error:
                    return 1
            if args.delay_seconds > 0:
                time.sleep(args.delay_seconds)

    print(f"Done. Manifest: {manifest_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", default=str(DEFAULT_ROSTER), help="Path to the Arrokoth roster markdown.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTDIR), help="Isolated output directory.")
    parser.add_argument("--provider", choices=["auto", "gemini", "openai"], default="auto")
    parser.add_argument("--limit-characters", type=int, default=2)
    parser.add_argument("--images-per-character", type=int, default=4)
    parser.add_argument("--priority", default="", help="Optional comma-separated priority filter, e.g. P0,P1.")
    parser.add_argument("--delay-seconds", type=float, default=0.0)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-translate-extra", action="store_true", help="Keep art-spec notes in their source language.")
    parser.add_argument("--add-to-library", action="store_true", help="Also register generated images in PromptGen library.")
    return parser


def main() -> int:
    return run(build_parser().parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
