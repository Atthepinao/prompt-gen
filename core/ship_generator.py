"""Spaceship (full vessel) prompt generator — Nano Banana / Gemini-tuned rewrite.

Generates a 2x2 four-view reference sheet prompt for a complete spaceship of a
given archetype, in the visual idiom of late-1980s to mid-1990s Japanese mecha
OVA capital-ship illustration.

This rewrite (April 2026) follows the prompt-engineering findings collected in
``nanobanana_ship_prompt_research.md``:

  * Narrative prose, not tag soup or uppercase directive blocks.
  * Subject + medium + designer is loaded into the FIRST paragraph so the
    high-weight first-50-words window carries the visual anchor.
  * The whole prompt sits in the 200-400 word sweet spot.
  * No "NEGATIVE" / "FORBIDDEN" / "NEVER" sections — Nano Banana ignores
    negative prompts and tends to invert them. Everything is phrased as
    positive description (what the picture IS, not what it isn't).
  * Designer NAMES are kept (they are useful style anchors) but specific
    work titles are dropped to reduce safety-system / copyright friction.
  * Carrier directive is folded inline as positive description when the
    archetype carries mecha — no separate anti-flat-deck negative block.
"""
import json
import logging
import os
import random
import sys
from typing import Dict, List, Optional

from paths import resource_path
from . import prompt_generator as pg
from . import mecha_generator as mg


log = logging.getLogger(__name__)

ARCHETYPES_PATH = resource_path("ship_archetypes.json")


def _emit_load_error(msg: str) -> None:
    """Surface a data-load failure on every available channel.

    This runs at import time, BEFORE init_app_logging() configures handlers,
    so we also write directly to stderr — otherwise the failure would be
    silently swallowed and the UI would crash later with a confusing
    `Index 0 out of range` from an empty Combobox.
    """
    log.error(msg)
    try:
        sys.stderr.write("[ship_generator] " + msg + "\n")
        sys.stderr.flush()
    except Exception:
        pass


def _load_data() -> Dict:
    if not os.path.exists(ARCHETYPES_PATH):
        _emit_load_error(
            "ship_archetypes.json NOT FOUND at %s — UI will start with an "
            "empty archetype list. Restore the file from the repo root."
            % ARCHETYPES_PATH
        )
        return {"archetypes": [], "variants": []}
    try:
        with open(ARCHETYPES_PATH, "r", encoding="utf-8-sig") as fh:
            text = fh.read()
    except OSError as e:
        _emit_load_error(
            "Failed to read ship_archetypes.json (%s): %s" % (ARCHETYPES_PATH, e)
        )
        return {"archetypes": [], "variants": []}

    # Use raw_decode so any trailing whitespace or stray bytes after the
    # first complete JSON value are silently ignored. Python 3.14's strict
    # json.load() rejects trailing data, which previously bit this project
    # when an editor saved a stray newline past the closing brace.
    try:
        data, _end = json.JSONDecoder().raw_decode(text.lstrip())
    except json.JSONDecodeError as e:
        _emit_load_error(
            "ship_archetypes.json is not valid JSON (%s): %s" % (ARCHETYPES_PATH, e)
        )
        return {"archetypes": [], "variants": []}

    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"archetypes": data, "variants": []}
    _emit_load_error(
        "ship_archetypes.json has unexpected top-level type %s — expected dict or list"
        % type(data).__name__
    )
    return {"archetypes": [], "variants": []}


def load_archetypes() -> List[Dict]:
    return list(_load_data().get("archetypes", []))


def load_variants() -> List[Dict]:
    return list(_load_data().get("variants", []))


ARCHETYPES = load_archetypes()
if not ARCHETYPES:
    _emit_load_error(
        "ARCHETYPES is empty after load — downstream Combobox.current(0) "
        "calls will fail. Check ship_archetypes.json for parse errors above."
    )
ARCHETYPE_BY_NAME: Dict[str, Dict] = {a["name"]: a for a in ARCHETYPES}

VARIANTS = load_variants()
if not VARIANTS:
    VARIANTS = [
        {"id": "Standard", "name_en": "Standard", "name_zh": "标准型", "descriptor": ""},
    ]

SHIP_VARIANTS: List[str] = [v["id"] for v in VARIANTS]
VARIANT_BY_ID: Dict[str, Dict] = {v["id"]: v for v in VARIANTS}


# --- Archetype helpers ---

def get_archetype_names() -> List[str]:
    return [a["name"] for a in ARCHETYPES]


def get_archetype(name: str) -> Optional[Dict]:
    return ARCHETYPE_BY_NAME.get(name)


def get_archetype_list(lang: str = "en") -> List[str]:
    if lang == "zh":
        return [a.get("name_zh") or a["name"] for a in ARCHETYPES]
    return [a["name"] for a in ARCHETYPES]


def get_archetype_label_map(lang: str = "en") -> Dict[str, str]:
    if lang == "zh":
        return {(a.get("name_zh") or a["name"]): a["name"] for a in ARCHETYPES}
    return {a["name"]: a["name"] for a in ARCHETYPES}


# --- Variant helpers ---

def get_variant_list(lang: str = "en") -> List[str]:
    if lang == "zh":
        return [v.get("name_zh") or v["name_en"] for v in VARIANTS]
    return [v["name_en"] for v in VARIANTS]


def get_variant_label_map(lang: str = "en") -> Dict[str, str]:
    if lang == "zh":
        return {(v.get("name_zh") or v["name_en"]): v["id"] for v in VARIANTS}
    return {v["name_en"]: v["id"] for v in VARIANTS}


def _variant_descriptor(variation_id: Optional[str]) -> str:
    if not variation_id or variation_id == "Standard":
        return ""
    v = VARIANT_BY_ID.get(variation_id)
    return v.get("descriptor", "") if v else ""


# --- Carrier inline directive (positive description, no negatives) ---
#
# Kept as a single short positive sentence so it can be inlined into the
# silhouette paragraph when ``carries_mecha`` is true. The old version was a
# multi-paragraph "DO NOT DRAW A FLAT FLIGHT DECK" block which Nano Banana
# tended to invert.

_CARRIER_INLINE = (
    "The vessel is a space carrier whose forward third opens into a wide "
    "longitudinal launch channel running fore-to-aft along the centerline, "
    "exiting face-first out of the bow opening, with outboard hangar sponsons "
    "running parallel along the flanks; the dorsal command block is a low "
    "stepped armored structure integrated flush into the dorsal spine, with "
    "horizontal viewport bands."
)


# --- Prose templates ---

# These are crafted to be read as natural prose by Nano Banana / Gemini, not
# parsed as bullet lists. Each variable is interpolated into a paragraph
# rather than appended as a separate uppercase section.

_MEDIUM_LINE = (
    "Hand-painted Japanese mecha OVA cel artwork in the visual tradition of "
    "late-1980s to mid-1990s capital-ship illustration."
)

_COMPOSITION_PROSE_CAPITAL = (
    "The hull reads as three clearly differentiated longitudinal acts along "
    "its long axis. The forward third is an aggressive prow carrying the "
    "heaviest concentration of weapons, sensors, or launch infrastructure, "
    "setting the vessel's direction. The middle third is a vertically stacked "
    "multi-tier armored superstructure, visually denser and taller than the "
    "bow or stern, bristling with antenna masts, sensor dishes, and secondary "
    "turrets — this is the visual focal point. The aft third is a thick "
    "armored engine block whose multiple large thruster bells are partially "
    "recessed into the armor plate, with internal framework only glimpsed "
    "through armor cutouts and access panels rather than hung off external "
    "scaffolding."
)

_SURFACE_PROSE_CAPITAL = (
    "Surface detail is dense and reads as a true capital-ship illustration. "
    "Hundreds of small lighted viewports, portholes, and access hatches are "
    "scattered across the entire hull surface, sized as human-scale crew "
    "ports — they are the implicit scale reference that makes the vessel "
    "read as 500 to 2000 meters long. Every large armor face is subdivided "
    "by panel-line work into smaller sub-panels with clear seam lines and "
    "rivet courses. Antenna mast forests, parabolic dish clusters, and sensor "
    "arrays bristle from the dorsal spine. Conduit channels, panel seams, and "
    "inset cable trays live within the armor envelope. Stenciled hull numbers, "
    "painted unit markings, and warning chevron stripes punctuate the surface "
    "as accent-color details. The primary hull volume is strictly left/right "
    "symmetric, while small bolted-on modules, antenna mounts, patch panels, "
    "and equipment pods are placed asymmetrically to give the vessel a "
    "lived-in production history. The hull is at least four times longer "
    "than it is tall."
)

_SURFACE_PROSE_FIGHTER = (
    "Surface detail is crisp and densely greebled at the scale of a single-"
    "pilot fighter: panel-line work subdivides every armor face into smaller "
    "sub-panels with rivet courses, intake grilles, and access hatches; "
    "stenciled unit numbers and warning chevron stripes punctuate the hull "
    "as accent-color details; small bolted-on antenna mounts, conformal "
    "hardpoints, and pylon adapters are placed asymmetrically over a strictly "
    "symmetric primary airframe."
)

_STYLE_PROSE = (
    "The artwork uses hard-edged cel-shaded shadow boundaries with one or "
    "two flat shadow tones per surface, combined with subtle airbrushed "
    "gradients within the largest armor faces to give the metal weight and "
    "curvature. Bold black ink linework defines all silhouette edges, with "
    "finer ink for panel lines, rivet courses, and surface greebles. Line "
    "weight is heavier on the silhouette and finer on internal detail. The "
    "primary hull tone occupies roughly seventy percent of the surface area "
    "as the calm dominant color; a darker structural tone occupies roughly "
    "twenty-five percent, used inside engine bells, panel recesses, and "
    "shadowed zones beneath overhanging armor; a single saturated warning "
    "accent (red, orange, or yellow) occupies the remaining five percent, "
    "used sparingly for warning stripes, stenciled numbers, hazard chevrons, "
    "and one or two unit insignia."
)

_LAYOUT_PROSE = (
    "The image is a clean reference sheet on a pure solid white background. "
    "Four orthographic views of the same vessel are arranged in a 2x2 grid "
    "at 1:1 aspect ratio: front view in the upper left, side view in the "
    "upper right, top-down view in the lower left, and three-quarter "
    "isometric view in the lower right. The four views are visually isolated "
    "from each other with no overlap and no panel separator lines drawn "
    "between them. The artwork is purely visual — no text, letters, numbers, "
    "labels, captions, arrows, callout lines, dimension markings, or any "
    "other typographic or diagrammatic overlay."
)


# --- Generator class ---

class ShipGenerator(pg.ComponentGenerator):
    def __init__(
        self,
        tier: pg.Tier,
        archetype_name: str,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        manufacturer_data: Optional[Dict] = None,
        variation: Optional[str] = None,
        designers: Optional[List[Dict]] = None,
    ):
        # ComponentType is unused by the ship pipeline (generate_full_prompt is
        # fully overridden), but the parent constructor requires a value.
        super().__init__(
            tier,
            pg.ComponentType.WEAPON,
            archetype_name,
            primary_color,
            secondary_color,
            manufacturer_data,
            variation,
        )
        self.designers = designers or []
        self.archetype = get_archetype(archetype_name) or {}

    # --- Internal helpers -------------------------------------------------

    def _is_capital_class(self) -> bool:
        """Three-act composition + 4:1 length clause apply to anything large
        enough to support a stacked superstructure. Single-pilot fighters and
        small private craft are excluded."""
        return self.archetype.get("id") not in {"fighter"}

    def _palette_clause(self) -> str:
        """Resolve the palette into a single descriptive clause that sits at
        the end of the style paragraph. Manufacturer > custom > tier default."""
        if self.manufacturer_data:
            return f"The hull palette is: {self.manufacturer_data['color_palette']}"
        if self.primary_color and self.secondary_color:
            return (
                f"The hull palette is: {self.primary_color} as the dominant "
                f"hull tone, {self.secondary_color} as the accent and warning "
                "marking color, with darker mechanical recesses."
            )
        return f"The hull palette is: {self.get_tier_data()['color_palette']}"

    def _designer_attribution(self) -> str:
        """Short attribution for paragraph 1 — names only, kept under one
        sentence so the high-weight first ~50 words stay punchy."""
        if not self.designers:
            return ""
        names = [d["name"] for d in self.designers]
        if len(names) == 1:
            return f"The vessel is designed by {names[0]}."
        return f"The vessel is designed by {', '.join(names)}."

    def _designer_signature_clause(self) -> str:
        """Long-form designer style signature for paragraph 2. Multi-designer
        selection lists every name but uses only the first designer's
        signature for stability — combining signatures tends to produce
        contradictory direction."""
        if not self.designers:
            return ""
        primary = self.designers[0]
        sig = (primary.get("signature") or "").strip().rstrip(".")
        if not sig:
            return ""
        return (
            f"The designer's distinctive visual vocabulary drives every "
            f"silhouette decision: {sig}."
        )

    def _article(self, word: str) -> str:
        return "an" if word[:1].lower() in {"a", "e", "i", "o", "u"} else "a"

    def _features_prose(self) -> str:
        """Pick a handful of features from the archetype pool and stitch them
        into a natural sentence rather than a bulleted list."""
        pool = list(self.archetype.get("features_pool", []))
        if not pool:
            return ""
        n = 3 if self.archetype.get("id") == "fighter" else 4
        picks = random.sample(pool, min(n, len(pool)))
        if len(picks) == 1:
            return f"Visible structural features include {picks[0]}."
        head, tail = picks[:-1], picks[-1]
        return "Visible structural features include " + ", ".join(head) + ", and " + tail + "."

    # --- Paragraph builders ----------------------------------------------

    def _para_subject(self) -> str:
        """Paragraph 1 — Medium + Subject + Designer attribution. Loaded
        into the high-weight first ~50 words; deliberately kept short.
        The longer designer signature goes in paragraph 2."""
        arche = self.archetype
        tier_data = self.get_tier_data()
        tier_adj = tier_data["adjectives"][0].lower()

        role = arche.get("role", "spaceship")
        scale = arche.get("scale_note", "").strip().rstrip(".")

        manuf_clause = ""
        if self.manufacturer_data:
            manuf_clause = f" built by {self.manufacturer_data['name']}"

        article = self._article(tier_adj)
        sentences = [
            _MEDIUM_LINE,
            f"The subject is {article} {tier_adj}-grade {role}{manuf_clause}.",
        ]
        if scale:
            sentences.append(f"Scale: {scale}.")

        attribution = self._designer_attribution()
        if attribution:
            sentences.append(attribution)

        return " ".join(sentences)

    def _para_silhouette(self) -> str:
        """Paragraph 2 — Defining anchor + silhouette + (capital-only)
        three-act composition + (carrier-only) inline launch directive +
        designer signature (folded in here so it directly informs the
        shape rather than getting lost up top)."""
        arche = self.archetype
        anchor = (arche.get("unique_anchor") or "").strip().rstrip(".")
        silhouette = (arche.get("silhouette") or "").strip().rstrip(".")

        sentences: List[str] = []

        designer_sig = self._designer_signature_clause()
        if designer_sig:
            sentences.append(designer_sig)

        if anchor:
            sentences.append(f"The defining visual anchor that must dominate the silhouette is: {anchor}.")
        if silhouette:
            sentences.append(f"Overall silhouette: {silhouette}.")

        if self._is_capital_class():
            sentences.append(_COMPOSITION_PROSE_CAPITAL)

        if arche.get("carries_mecha"):
            sentences.append(_CARRIER_INLINE)

        return " ".join(sentences)

    def _para_surface(self) -> str:
        """Paragraph 3 — Surface density + features + (variant)."""
        sentences: List[str] = []
        if self._is_capital_class():
            sentences.append(_SURFACE_PROSE_CAPITAL)
        else:
            sentences.append(_SURFACE_PROSE_FIGHTER)

        feats = self._features_prose()
        if feats:
            sentences.append(feats)

        variant_text = _variant_descriptor(self.variation).strip()
        if variant_text:
            sentences.append(variant_text)

        return " ".join(sentences)

    def _para_style(self) -> str:
        """Paragraph 4 — Cel-shading style + color rhythm + palette."""
        return _STYLE_PROSE + " " + self._palette_clause()

    def _para_layout(self) -> str:
        """Paragraph 5 — Four-view sheet layout + zero-text positive directive."""
        return _LAYOUT_PROSE

    # --- Public API -------------------------------------------------------

    def generate_subject_description(self) -> str:
        """Kept for backward compatibility with anything calling the old API
        (e.g. unit tests that exercise individual sections). Returns the
        subject + silhouette paragraphs joined."""
        return self._para_subject() + "\n\n" + self._para_silhouette()

    def _para_layout_openai(self) -> str:
        """Paragraph 5 variant for GPT-image: same content but uses explicit
        negative sentences that reasoning models handle better than omission."""
        return (
            _LAYOUT_PROSE
            + " Do not add any text, labels, dimension lines, callout arrows, "
            "or typographic overlays anywhere in the image."
        )

    def generate_full_prompt(self, backend: str = "gemini") -> str:
        if backend == "openai":
            paragraphs = [
                self._para_subject(),
                self._para_silhouette(),
                self._para_surface(),
                self._para_style(),
                self._para_layout_openai(),
            ]
        else:
            paragraphs = [
                self._para_subject(),
                self._para_silhouette(),
                self._para_surface(),
                self._para_style(),
                self._para_layout(),
            ]
        body = "\n\n".join(p for p in paragraphs if p)
        return body + "\n"


# --- UI helpers ---

def get_designer_options(lang: str = "en") -> List[str]:
    """Filter designer pool to ship-capable designers only."""
    return mg.get_designer_options(lang, scope="ship")


def get_designer_label_map(lang: str = "en") -> Dict[str, str]:
    return mg.get_designer_label_map(lang, scope="ship")


def generate_ship_prompt_by_strings(
    tier_name: str,
    archetype_name: str,
    primary_color: Optional[str] = None,
    secondary_color: Optional[str] = None,
    manufacturer_name: Optional[str] = None,
    variation_name: Optional[str] = None,
    designer_names: Optional[List[str]] = None,
    backend: str = "gemini",
) -> str:
    try:
        tier = pg.Tier[tier_name]
    except KeyError:
        return "Error: Invalid Tier"

    if archetype_name not in ARCHETYPE_BY_NAME:
        return f"Error: Unknown ship archetype '{archetype_name}'"

    manufacturer_data = None
    if manufacturer_name and manufacturer_name not in (None, "None", "None / Generic"):
        manufacturer_data = pg.get_manufacturer_by_name(manufacturer_name)

    designers = []
    for n in designer_names or []:
        d = mg.get_designer_by_name(n)
        if d:
            designers.append(d)

    gen = ShipGenerator(
        tier=tier,
        archetype_name=archetype_name,
        primary_color=primary_color,
        secondary_color=secondary_color,
        manufacturer_data=manufacturer_data,
        variation=variation_name,
        designers=designers,
    )
    return gen.generate_full_prompt(backend=backend)


if __name__ == "__main__":
    out = generate_ship_prompt_by_strings(
        "TIER_3_MILITARY",
        "Fleet Carrier",
        manufacturer_name=None,
        variation_name="Block-II Refit",
        designer_names=["Kazutaka Miyatake"],
    )
    print(out)
