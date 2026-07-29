"""Spaceship (full vessel) tab."""

from __future__ import annotations
from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QListWidget, QAbstractItemView,
    QFrame, QMessageBox,
)

import ship_generator as sg
import prompt_generator as pg
from ui.tabs.base_tab import BaseTab


class ShipTab(BaseTab):
    image_prefix = "ship"

    def __init__(self, window, parent=None):
        self._lang = window.ui_lang
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay = self._layout
        lang = self._lang

        title = QLabel("Spaceship Prompt Generation")
        title.setObjectName("header")
        lay.addWidget(title)
        sub = QLabel(
            "Generate a 4-view full-vessel spaceship reference sheet "
            "(90s OVA capital ship style).")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addWidget(_sep())

        # ── Archetype ──
        self._archetype_map = sg.get_archetype_label_map(lang)
        lay.addWidget(QLabel(self.t("Ship Archetype:")))
        self.combo_archetype = QComboBox()
        archetype_vals = sg.get_archetype_list(lang)
        self.combo_archetype.addItems(archetype_vals)
        lay.addWidget(self.combo_archetype)

        # ── Variant ──
        self._variant_map = sg.get_variant_label_map(lang)
        lay.addWidget(QLabel(self.t("Ship Variant:")))
        self.combo_variant = QComboBox()
        self.combo_variant.addItems(sg.get_variant_list(lang))
        lay.addWidget(self.combo_variant)

        # ── Tier ──
        lay.addWidget(QLabel(self.t("Tech Tier:")))
        self.combo_tier = QComboBox()
        self.combo_tier.addItems(pg.get_tier_list())
        self.combo_tier.setCurrentIndex(2)
        lay.addWidget(self.combo_tier)

        lay.addWidget(_sep())

        # ── Manufacturer ──
        manu_lbl = QLabel(self.t("Manufacturer Preset"))
        manu_lbl.setObjectName("header")
        lay.addWidget(manu_lbl)
        self.combo_manu = QComboBox()
        manu_list = ["None / Generic"] + pg.get_manufacturer_names()
        self.combo_manu.addItems(manu_list)
        lay.addWidget(self.combo_manu)

        lay.addWidget(_sep())

        # ── Designer multi-select ──
        designer_lbl = QLabel(self.t("Ship Designer (multi-select)"))
        designer_lbl.setObjectName("header")
        lay.addWidget(designer_lbl)

        self._designer_map = sg.get_designer_label_map(lang)
        self.list_designers = QListWidget()
        self.list_designers.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_designers.addItems(sg.get_designer_options(lang))
        self.list_designers.setMaximumHeight(140)
        lay.addWidget(self.list_designers)

        btn_clear = QPushButton(self.t("Clear Selection"))
        btn_clear.clicked.connect(self.list_designers.clearSelection)
        lay.addWidget(btn_clear)

        lay.addWidget(_sep())

        self.btn_gen = QPushButton(self.t("GENERATE SHIP PROMPT"))
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

    def _generate(self):
        tier = self.combo_tier.currentText()
        archetype_label = self.combo_archetype.currentText()
        variant_label   = self.combo_variant.currentText()
        manu = self.combo_manu.currentText()

        if not tier or not archetype_label:
            QMessageBox.warning(self, "Error", "Please select all options.")
            return

        archetype = self._archetype_map.get(archetype_label, archetype_label)
        var       = self._variant_map.get(variant_label, variant_label)
        manu_val  = None if manu == "None / Generic" else manu

        selected = [self.list_designers.item(i).text()
                    for i in range(self.list_designers.count())
                    if self.list_designers.item(i).isSelected()]
        designers = [self._designer_map.get(lbl, lbl) for lbl in selected]

        prompt = sg.generate_ship_prompt_by_strings(
            tier_name=tier,
            archetype_name=archetype,
            manufacturer_name=manu_val,
            variation_name=var,
            designer_names=designers,
            backend=self.window.active_backend,
        )
        self.set_output(prompt)

    def build_prompt(self) -> str:
        self._generate()
        return self.window.right.output_text.toPlainText()

    def save_dir(self) -> str:
        return self.window.spaceship_save_dir or self.window.image_save_dir


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f
