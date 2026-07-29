"""Character Prompts tab."""

from __future__ import annotations
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel, QComboBox, QPushButton, QCheckBox,
    QListWidget, QAbstractItemView,
    QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout,
    QSlider, QFrame, QLineEdit, QFileDialog, QMessageBox, QWidget,
)

import character_generator as cg
from ui.tabs.base_tab import BaseTab


class CharacterTab(BaseTab):
    image_prefix = "character"
    text_last    = True

    def __init__(self, window, parent=None):
        self._lang = window.ui_lang
        self._style_ref_path: str = ""
        super().__init__(window, parent)

    def _build_ui(self, body):
        lay  = self._layout
        lang = self._lang

        title = QLabel("Character Prompt Generation")
        title.setObjectName("header")
        lay.addWidget(title)
        sub = QLabel("Build a detailed character prompt for retro sci-fi anime portraits.")
        sub.setObjectName("subheader")
        sub.setWordWrap(True)
        lay.addWidget(sub)
        lay.addWidget(_sep())

        # ── Core Descriptors ──────────────────────────────────────────────
        grp_core = QGroupBox("Core Descriptors")
        g = QGridLayout(grp_core)
        g.setColumnStretch(1, 1)
        g.setColumnStretch(3, 1)

        g.addWidget(QLabel("Gender:"), 0, 0)
        self.combo_gender = QComboBox()
        self.combo_gender.addItems(cg.get_gender_options(lang))
        self.combo_gender.currentTextChanged.connect(self._refresh_hair_styles)
        g.addWidget(self.combo_gender, 0, 1)

        g.addWidget(QLabel("Age:"), 0, 2)
        age_row = QHBoxLayout()
        self.slider_age = QSlider(Qt.Horizontal)
        self.slider_age.setRange(10, 60)
        self.slider_age.setValue(17)
        self.lbl_age = QLabel("17")
        self.slider_age.valueChanged.connect(lambda v: self.lbl_age.setText(str(v)))
        age_row.addWidget(self.slider_age)
        age_row.addWidget(self.lbl_age)
        age_w = QWidget()
        age_w.setLayout(age_row)
        g.addWidget(age_w, 0, 3)

        g.addWidget(QLabel("Body Type:"), 1, 0)
        self.combo_body = QComboBox()
        self.combo_body.addItems(cg.get_body_type_options(lang))
        g.addWidget(self.combo_body, 1, 1)

        g.addWidget(QLabel("Skin Tone:"), 1, 2)
        self.combo_skin = QComboBox()
        self.combo_skin.addItems(cg.get_skin_tone_options(lang))
        g.addWidget(self.combo_skin, 1, 3)

        g.addWidget(QLabel("Framing:"), 2, 0)
        self.combo_framing = QComboBox()
        self.combo_framing.addItems(cg.get_framing_options(lang))
        g.addWidget(self.combo_framing, 2, 1)

        g.addWidget(QLabel("Aspect Ratio:"), 2, 2)
        self.combo_aspect = QComboBox()
        self.combo_aspect.addItems(cg.get_aspect_ratio_options(lang))
        g.addWidget(self.combo_aspect, 2, 3)

        g.addWidget(QLabel("Expression:"), 3, 0)
        self.combo_expr = QComboBox()
        self.combo_expr.addItems(cg.get_expression_options(lang))
        g.addWidget(self.combo_expr, 3, 1)

        g.addWidget(QLabel("Gaze:"), 3, 2)
        self.combo_gaze = QComboBox()
        self.combo_gaze.addItems(cg.get_gaze_options(lang))
        g.addWidget(self.combo_gaze, 3, 3)

        g.addWidget(QLabel("Clothing Hint:"), 4, 0)
        self.combo_clothing_hint = QComboBox()
        self.combo_clothing_hint.addItems(cg.get_clothing_hint_options(lang))
        g.addWidget(self.combo_clothing_hint, 4, 1)

        lay.addWidget(grp_core)

        # ── Hair ─────────────────────────────────────────────────────────
        grp_hair = QGroupBox("Hair")
        h = QGridLayout(grp_hair)
        h.setColumnStretch(1, 1)
        h.setColumnStretch(3, 1)

        h.addWidget(QLabel("Hair Style:"), 0, 0)
        self.combo_hair_style = QComboBox()
        h.addWidget(self.combo_hair_style, 0, 1)

        h.addWidget(QLabel("Hair Color:"), 0, 2)
        self.combo_hair_color = QComboBox()
        self.combo_hair_color.addItems(cg.get_hair_color_options(lang))
        h.addWidget(self.combo_hair_color, 0, 3)

        self.chk_filter_hair = QCheckBox("Only show hair styles for current gender")
        self.chk_filter_hair.setChecked(True)
        self.chk_filter_hair.toggled.connect(self._refresh_hair_styles)
        h.addWidget(self.chk_filter_hair, 1, 0, 1, 4)

        h.addWidget(QLabel("Bangs Presence:"), 2, 0)
        self.combo_bangs_presence = QComboBox()
        self.combo_bangs_presence.addItems(cg.get_bangs_presence_options(lang))
        h.addWidget(self.combo_bangs_presence, 2, 1)

        h.addWidget(QLabel("Bangs Style:"), 2, 2)
        self.combo_bangs_style = QComboBox()
        self.combo_bangs_style.addItems(cg.get_bangs_style_options(lang))
        h.addWidget(self.combo_bangs_style, 2, 3)

        lay.addWidget(grp_hair)

        # ── Face ─────────────────────────────────────────────────────────
        grp_face = QGroupBox("Face")
        f = QGridLayout(grp_face)
        f.setColumnStretch(1, 1)
        f.setColumnStretch(3, 1)

        f.addWidget(QLabel("Face Shape:"), 0, 0)
        self.combo_face_shape = QComboBox()
        self.combo_face_shape.addItems(cg.get_face_shape_options(lang))
        f.addWidget(self.combo_face_shape, 0, 1)

        f.addWidget(QLabel("Eye Size:"), 0, 2)
        self.combo_eye_size = QComboBox()
        self.combo_eye_size.addItems(cg.get_eye_size_options(lang))
        f.addWidget(self.combo_eye_size, 0, 3)

        f.addWidget(QLabel("Nose Size:"), 1, 0)
        self.combo_nose_size = QComboBox()
        self.combo_nose_size.addItems(cg.get_nose_size_options(lang))
        f.addWidget(self.combo_nose_size, 1, 1)

        f.addWidget(QLabel("Mouth Shape:"), 1, 2)
        self.combo_mouth_shape = QComboBox()
        self.combo_mouth_shape.addItems(cg.get_mouth_shape_options(lang))
        f.addWidget(self.combo_mouth_shape, 1, 3)

        f.addWidget(QLabel("Cheek Fullness:"), 2, 0)
        self.combo_cheek = QComboBox()
        self.combo_cheek.addItems(cg.get_cheek_fullness_options(lang))
        f.addWidget(self.combo_cheek, 2, 1)

        f.addWidget(QLabel("Jaw Width:"), 2, 2)
        self.combo_jaw = QComboBox()
        self.combo_jaw.addItems(cg.get_jaw_width_options(lang))
        f.addWidget(self.combo_jaw, 2, 3)

        f.addWidget(QLabel("Eye Color:"), 3, 0)
        self.combo_eye_color = QComboBox()
        self.combo_eye_color.addItems(cg.get_eye_color_options(lang))
        f.addWidget(self.combo_eye_color, 3, 1)

        lay.addWidget(grp_face)

        # ── Face Features multi-select ────────────────────────────────────
        grp_feat = QGroupBox("Face Features (multi-select)")
        feat_lay = QVBoxLayout(grp_feat)
        self.list_features = QListWidget()
        self.list_features.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_features.addItems(cg.get_appearance_options(lang))
        self.list_features.setMaximumHeight(100)
        feat_lay.addWidget(self.list_features)
        lay.addWidget(grp_feat)

        # ── Artist Styles multi-select ────────────────────────────────────
        grp_artist = QGroupBox("Artist Styles (multi-select)")
        art_lay = QVBoxLayout(grp_artist)
        self._artist_label_map = cg.get_artist_label_map(lang)
        self.list_artists = QListWidget()
        self.list_artists.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_artists.addItems(cg.get_artist_options(lang))
        self.list_artists.setMaximumHeight(100)
        art_lay.addWidget(self.list_artists)
        lay.addWidget(grp_artist)

        # ── Style Reference ───────────────────────────────────────────────
        grp_ref = QGroupBox("Style Reference (Optional)")
        ref_lay = QVBoxLayout(grp_ref)
        btn_ref_row = QHBoxLayout()
        btn_sel_ref = QPushButton("Select Style Image…")
        btn_sel_ref.clicked.connect(self._select_style_ref)
        btn_clr_ref = QPushButton("Clear")
        btn_clr_ref.clicked.connect(self._clear_style_ref)
        btn_ref_row.addWidget(btn_sel_ref)
        btn_ref_row.addWidget(btn_clr_ref)
        btn_ref_row.addStretch(1)
        ref_lay.addLayout(btn_ref_row)
        self.lbl_style_ref = QLabel("No style image selected")
        self.lbl_style_ref.setObjectName("subheader")
        self.lbl_style_ref.setWordWrap(True)
        ref_lay.addWidget(self.lbl_style_ref)
        self.chk_ref_only = QCheckBox(
            "Use style reference only (remove style text from prompt)")
        self.chk_ref_only.setEnabled(False)
        ref_lay.addWidget(self.chk_ref_only)
        lay.addWidget(grp_ref)

        # ── Extra modifiers + Generate ────────────────────────────────────
        lay.addWidget(_sep())
        extra_row = QHBoxLayout()
        extra_row.addWidget(QLabel("Extra modifiers (optional):"))
        self.edit_extra = QLineEdit()
        self.edit_extra.setPlaceholderText("(optional)")
        extra_row.addWidget(self.edit_extra, 1)
        lay.addLayout(extra_row)

        self.btn_gen = QPushButton("GENERATE CHARACTER PROMPT")
        self.btn_gen.setObjectName("primary")
        self.btn_gen.clicked.connect(self._generate)
        lay.addWidget(self.btn_gen)

        # Init hair list
        self._refresh_hair_styles()

    # ── Hair filter ───────────────────────────────────────────────────────

    def _refresh_hair_styles(self):
        lang    = self._lang
        current = self.combo_hair_style.currentText()

        if self.chk_filter_hair.isChecked():
            gender_label = self.combo_gender.currentText()
            gender_map   = cg.get_gender_label_map(lang)
            gender_key   = gender_map.get(gender_label, gender_label)
            by_gender    = cg.get_hair_style_options_by_gender(lang)
            options = (by_gender.get(gender_key)
                       or by_gender.get(gender_label)
                       or cg.get_hair_style_options(lang))
        else:
            options = cg.get_hair_style_options(lang)

        self.combo_hair_style.blockSignals(True)
        self.combo_hair_style.clear()
        self.combo_hair_style.addItems(options or [])
        idx = self.combo_hair_style.findText(current)
        self.combo_hair_style.setCurrentIndex(max(idx, 0))
        self.combo_hair_style.blockSignals(False)

    # ── Style ref ─────────────────────────────────────────────────────────

    def _select_style_ref(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Style Reference Image", "",
            "Images (*.png *.jpg *.jpeg *.webp);;All Files (*)")
        if path:
            self._style_ref_path = path
            self.lbl_style_ref.setText(os.path.basename(path))
            self.chk_ref_only.setEnabled(True)

    def _clear_style_ref(self):
        self._style_ref_path = ""
        self.lbl_style_ref.setText("No style image selected")
        self.chk_ref_only.setChecked(False)
        self.chk_ref_only.setEnabled(False)

    # ── Generation ────────────────────────────────────────────────────────

    def _generate(self):
        lang = self._lang

        face_features = [
            self.list_features.item(i).text()
            for i in range(self.list_features.count())
            if self.list_features.item(i).isSelected()
        ]
        artists = [
            self._artist_label_map.get(
                self.list_artists.item(i).text(),
                self.list_artists.item(i).text())
            for i in range(self.list_artists.count())
            if self.list_artists.item(i).isSelected()
        ]

        try:
            prompt = cg.generate_character_prompt(
                gender=self.combo_gender.currentText(),
                age=self.slider_age.value(),
                framing=self.combo_framing.currentText(),
                aspect_ratio=self.combo_aspect.currentText(),
                expression=self.combo_expr.currentText(),
                gaze=self.combo_gaze.currentText(),
                appearance_features=face_features,
                body_type=self.combo_body.currentText(),
                skin_tone=self.combo_skin.currentText(),
                hair_style=self.combo_hair_style.currentText(),
                hair_color=self.combo_hair_color.currentText(),
                hair_colors=[],
                hair_bangs_presence=self.combo_bangs_presence.currentText(),
                hair_bangs_style=self.combo_bangs_style.currentText(),
                face_shape=self.combo_face_shape.currentText(),
                eye_size=self.combo_eye_size.currentText(),
                nose_size=self.combo_nose_size.currentText(),
                mouth_shape=self.combo_mouth_shape.currentText(),
                cheek_fullness=self.combo_cheek.currentText(),
                jaw_width=self.combo_jaw.currentText(),
                eye_color=self.combo_eye_color.currentText(),
                clothing_hint=self.combo_clothing_hint.currentText(),
                artists=artists,
                lang=lang,
                extra_modifiers=self.edit_extra.text().strip(),
                include_style=not self.chk_ref_only.isChecked(),
                backend=self.window.active_backend,
            )
            self.set_output(prompt)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def build_prompt(self) -> str:
        self._generate()
        return self.window.right.output_text.toPlainText()

    def save_dir(self) -> str:
        return self.window.character_save_dir or self.window.image_save_dir

    def get_reference_images(self) -> list[tuple[bytes, str]]:
        if not self._style_ref_path or not os.path.exists(self._style_ref_path):
            return []
        import mimetypes
        with open(self._style_ref_path, "rb") as fh:
            data = fh.read()
        mime = mimetypes.guess_type(self._style_ref_path)[0] or "image/png"
        return [(data, mime)]


def _sep():
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    return f
