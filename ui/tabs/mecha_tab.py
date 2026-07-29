"""Mecha tab."""

from __future__ import annotations
from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QListWidget, QAbstractItemView,
    QFrame, QMessageBox,
)

import mecha_generator as mg
import prompt_generator as pg
from ui.tabs.base_tab import BaseTab


class MechaTab(BaseTab):
    image_prefix = "mecha"

    def __init__(self, window, parent=None):
        self._lang = window.ui_lang
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout
        lang = self._lang

        title = QLabel("Mecha Prompt Generation")
        title.setObjectName("header")
        lay.addWidget(title)
        sub = QLabel("Generate a 4-view bare-frame mecha reference sheet (90s OVA real-robot style).")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addWidget(_sep())

        # ── Class ──
        self._subcat_map = mg.get_subcategory_label_map(lang)
        lay.addWidget(QLabel(self.t("Mecha Class:")))
        self.combo_class = QComboBox()
        self.combo_class.addItems(list(self._subcat_map.keys()))
        lay.addWidget(self.combo_class)

        # ── Variant ──
        self._variant_map = mg.get_variant_label_map(lang)
        lay.addWidget(QLabel(self.t("Mecha Variant:")))
        self.combo_variant = QComboBox()
        self.combo_variant.addItems(list(self._variant_map.keys()))
        lay.addWidget(self.combo_variant)

        # ── Tier ──
        self._tier_map = mg.get_tier_label_map(lang)
        lay.addWidget(QLabel(self.t("Tech Tier:")))
        self.combo_tier = QComboBox()
        self.combo_tier.addItems(list(self._tier_map.keys()))
        self.combo_tier.setCurrentIndex(2)
        lay.addWidget(self.combo_tier)

        lay.addWidget(_sep())

        # ── Manufacturer ──
        lay.addWidget(QLabel(self.t("Manufacturer Preset")))
        self.combo_manu = QComboBox()
        manu_list = ["None / Generic"] + pg.get_manufacturer_names()
        self.combo_manu.addItems(manu_list)
        lay.addWidget(self.combo_manu)

        lay.addWidget(_sep())

        # ── Design Controls ──
        ctrl_lbl = QLabel(self.t("Design Controls (Auto = random / by designer)"))
        ctrl_lbl.setObjectName("header")
        lay.addWidget(ctrl_lbl)

        axes = [
            ("Sensor Module:",     mg.get_sensor_module_options,      mg.get_sensor_module_label_map),
            ("Surface Treatment:", mg.get_surface_treatment_options,   mg.get_surface_treatment_label_map),
            ("Shoulder Form:",     mg.get_shoulder_form_options,       mg.get_shoulder_form_label_map),
            ("Propulsion Style:",  mg.get_propulsion_style_options,    mg.get_propulsion_style_label_map),
            ("Paint Scheme:",      mg.get_paint_scheme_options,        mg.get_paint_scheme_label_map),
        ]
        self._axis_combos: list[tuple[QComboBox, dict]] = []
        for label_key, opts_fn, map_fn in axes:
            lay.addWidget(QLabel(self.t(label_key)))
            combo = QComboBox()
            opts = opts_fn(lang)
            combo.addItems(opts)
            lay.addWidget(combo)
            self._axis_combos.append((combo, map_fn(lang)))

        lay.addWidget(_sep())

        # ── Designer multi-select ──
        designer_lbl = QLabel(self.t("Mecha Designer (multi-select)"))
        designer_lbl.setObjectName("header")
        lay.addWidget(designer_lbl)

        self._designer_map = mg.get_designer_label_map(lang)
        self.list_designers = QListWidget()
        self.list_designers.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_designers.addItems(mg.get_designer_options(lang))
        self.list_designers.setMaximumHeight(140)
        lay.addWidget(self.list_designers)

        btn_clear = QPushButton(self.t("Clear Selection"))
        btn_clear.clicked.connect(self.list_designers.clearSelection)
        lay.addWidget(btn_clear)

        lay.addWidget(_sep())

        # ── Generate ──
        self.btn_gen = QPushButton(self.t("GENERATE MECHA PROMPT"))
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

    def _generate(self):
        tier_label = self.combo_tier.currentText()
        sub_label  = self.combo_class.currentText()
        var_label  = self.combo_variant.currentText()
        manu = self.combo_manu.currentText()

        tier = self._tier_map.get(tier_label, tier_label)
        sub  = self._subcat_map.get(sub_label, sub_label)
        var  = self._variant_map.get(var_label, var_label)

        if not tier or not sub:
            QMessageBox.warning(self, "Error", "Please select all options.")
            return

        manu_val = None if manu == "None / Generic" else manu

        axis_keys = []
        for combo, label_map in self._axis_combos:
            axis_keys.append(label_map.get(combo.currentText()))

        selected = [self.list_designers.item(i).text()
                    for i in range(self.list_designers.count())
                    if self.list_designers.item(i).isSelected()]
        designers = [self._designer_map.get(lbl, lbl) for lbl in selected]

        prompt = mg.generate_mecha_prompt_by_strings(
            tier_name=tier,
            subcategory=sub,
            manufacturer_name=manu_val,
            variation_name=var,
            designer_names=designers,
            sensor_module_key=axis_keys[0],
            surface_treatment_key=axis_keys[1],
            shoulder_form_key=axis_keys[2],
            propulsion_style_key=axis_keys[3],
            paint_scheme_key=axis_keys[4],
            backend=self.window.active_backend,
        )
        self.set_output(prompt)

    def build_prompt(self) -> str:
        self._generate()
        return self.window.right.output_text.toPlainText()

    def save_dir(self) -> str:
        return self.window.image_save_dir


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f
