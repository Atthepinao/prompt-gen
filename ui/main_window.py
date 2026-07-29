"""Main application window for PromptGen Tool (PySide6)."""

from __future__ import annotations
import os
import json
import datetime
from io import BytesIO

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QTabWidget, QWidget,
    QMessageBox, QFileDialog, QColorDialog,
    QApplication, QInputDialog, QStatusBar,
)

from paths import migrate_legacy_file
import gemini_service as gs
import core.openai_service as oi

from ui.right_panel import RightPanel
from ui.workers import (
    ImageGenWorker, BatchImageGenWorker, ImageEditWorker, GeminiEditWorker,
)

# Tab imports – added as tabs are migrated
from ui.tabs.spaceship_tab  import SpaceshipTab
from ui.tabs.mecha_tab      import MechaTab
from ui.tabs.mecha_part_tab import MechaPartTab
from ui.tabs.ship_tab       import ShipTab
from ui.tabs.items_tab      import ItemsTab
from ui.tabs.character_tab  import CharacterTab
from ui.tabs.clothing_tab   import ClothingTab
from ui.tabs.slicer_tab     import SlicerTab
from ui.tabs.curation_tab   import CurationTab
from ui.tabs.library_tab    import LibraryTab
from ui.tabs.settings_tab   import SettingsTab

APP_CONFIG_PATH = migrate_legacy_file("config.json")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PromptGen Tool")
        self.resize(1100, 860)
        self.setMinimumSize(QSize(800, 600))

        # ── Load config ──
        self.config     = self._load_config()
        self.ui_lang    = self.config.get("language", "en")

        # ── API / provider state ──
        self.api_provider         = self.config.get("api_provider", "Gemini")
        self.gemini_api_key       = self.config.get("gemini_api_key", "")
        self.gemini_model         = self.config.get("gemini_model", gs.DEFAULT_MODEL)
        self.openai_api_key       = self.config.get("openai_api_key", "")
        self.openai_base_url      = self.config.get("openai_base_url", oi.DEFAULT_BASE_URL)
        self.openai_model         = self.config.get("openai_model", oi.DEFAULT_MODEL)
        self.openai_image_size    = self.config.get("openai_image_size", "1024x1024")
        self.openai_image_quality = self.config.get("openai_image_quality", "auto")

        # ── Save-dir state ──
        self.image_save_dir    = self.config.get("image_save_dir", "outputs")
        self.spaceship_save_dir = self.config.get("spaceship_save_dir", "")
        self.items_save_dir    = self.config.get("items_save_dir", "")
        self.character_save_dir = self.config.get("character_save_dir", "")
        self.clothing_save_dir  = self.config.get("clothing_save_dir", "")

        # ── Active async workers (kept alive until done) ──
        self._active_workers: list = []

        self._build_ui()
        self._connect_signals()

    @property
    def active_backend(self) -> str:
        """Return 'openai' or 'gemini' based on the currently selected provider."""
        return "openai" if self.api_provider == "OpenAI" else "gemini"

    # ── Config helpers ────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        if os.path.exists(APP_CONFIG_PATH):
            try:
                with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self, data: dict) -> bool:
        try:
            with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(3)
        self.setCentralWidget(splitter)

        # ── Left: tab notebook ──
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(False)
        splitter.addWidget(self.tabs)

        # ── Right: output / preview panel ──
        self.right = RightPanel()
        splitter.addWidget(self.right)

        # Give left ~60 % of the initial width
        splitter.setSizes([660, 440])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        # ── Status bar ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # ── Instantiate all tabs ──
        self._spaceship = SpaceshipTab(self)
        self._mecha     = MechaTab(self)
        self._mecha_part = MechaPartTab(self)
        self._ship      = ShipTab(self)
        self._items     = ItemsTab(self)
        self._character = CharacterTab(self)
        self._clothing  = ClothingTab(self)
        self._slicer    = SlicerTab(self)
        self._curation  = CurationTab(self)
        self._library   = LibraryTab(self)
        self._settings  = SettingsTab(self)

        for tab, label in [
            (self._spaceship,  "Spaceship Components"),
            (self._mecha,      "Mecha"),
            (self._mecha_part, "Mecha Components"),
            (self._ship,       "Spaceship"),
            (self._items,      "Item Icons"),
            (self._character,  "Character Prompts"),
            (self._clothing,   "Clothing Presets"),
            (self._slicer,     "Image Slicer"),
            (self._curation,   "Asset Curation"),
            (self._library,    "Asset Library"),
            (self._settings,   "Settings"),
        ]:
            self.tabs.addTab(tab, self.t(label))

        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _connect_signals(self):
        r = self.right
        r.save_requested.connect(self._save_preview_image)
        r.discard_requested.connect(self._discard_preview_image)
        r.edit_requested.connect(self._open_edit_dialog)
        r.undo_edit_requested.connect(self._undo_edit)
        r.generate_image_requested.connect(self._generate_image)
        r.copy_requested.connect(self._copy_to_clipboard)

    # ── Translation ───────────────────────────────────────────────────────

    _ZH: dict[str, str] = {}   # populated lazily from app.py's UI_TEXTS_ZH

    def t(self, text: str) -> str:
        if self.ui_lang == "zh":
            # Import the translation table from the legacy module on first use
            if not MainWindow._ZH:
                try:
                    import app as _app_legacy
                    MainWindow._ZH = _app_legacy.UI_TEXTS_ZH
                except Exception:
                    pass
            return MainWindow._ZH.get(text, text)
        return text

    # ── Status helpers ────────────────────────────────────────────────────

    def set_status(self, msg: str):
        self.status_bar.showMessage(msg)

    def set_busy(self, busy: bool, msg: str = ""):
        self.right.set_busy(busy)
        self.status_bar.showMessage(msg if busy else "Ready")
        # Update generate button label based on provider
        provider = self._settings.provider() if hasattr(self._settings, "provider") else self.api_provider
        self.right.set_generate_button_label(
            f"Generate Image ({provider})" if not busy else "Generating…"
        )

    def set_output(self, text: str):
        self.right.set_output(text)

    # ── API credential helpers ────────────────────────────────────────────

    def get_credentials(self):
        """Return (provider, key, model, extra_kwargs) from the settings tab."""
        return self._settings.get_credentials()

    def get_save_dir(self) -> str:
        """Return the save directory for the currently active tab."""
        idx = self.tabs.currentIndex()
        tab = self.tabs.widget(idx)
        tab_dir = getattr(tab, "save_dir", lambda: "")()
        return tab_dir or self.image_save_dir or "outputs"

    # ── Image generation ─────────────────────────────────────────────────

    def _generate_image(self, concurrent: int):
        # Collect prompt from the active tab
        idx = self.tabs.currentIndex()
        tab = self.tabs.widget(idx)
        if not hasattr(tab, "build_prompt"):
            QMessageBox.information(self, "Info",
                "This tab doesn't support image generation directly.\n"
                "Generate a prompt first, then click the button.")
            return

        prompt = tab.build_prompt()
        if not prompt:
            return

        provider, key, model, extra = self.get_credentials()
        if not key:
            QMessageBox.warning(self, "No API Key",
                "Please enter an API key in the Settings tab.")
            return

        self.set_busy(True, "Generating image…")
        self.right.set_output(prompt)

        def _gen_fn(prompt, reference_images=None, text_last=False):
            if provider == "OpenAI":
                return oi.generate_image_bytes(
                    prompt, api_key=key, model=model,
                    reference_images=reference_images or [], **extra)
            else:
                return gs.generate_image_bytes(
                    prompt, api_key=key, model=model,
                    reference_images=reference_images if reference_images else None,
                    text_last=text_last)

        ref_images = getattr(tab, "get_reference_images", lambda: [])()
        text_last  = getattr(tab, "text_last", False)

        if concurrent > 1:
            w = BatchImageGenWorker(_gen_fn, prompt, concurrent, ref_images, text_last)
            w.image_ready.connect(lambda idx, data: None)  # partial update hook
            w.finished.connect(self._on_batch_done)
        else:
            w = ImageGenWorker(_gen_fn, prompt, ref_images, text_last)
            w.finished.connect(self._on_single_image_done)

        w.error.connect(self._on_gen_error)
        self._active_workers.append(w)
        w.finished.connect(lambda _: self._active_workers.remove(w))
        w.start()

    def _on_single_image_done(self, result):
        self.set_busy(False)
        # Services return (bytes, mime_str); handle both forms defensively
        if isinstance(result, tuple):
            data, mime = result[0], result[1] if len(result) > 1 else "image/png"
        else:
            data, mime = result, "image/png"
        self.right.show_single_image(data, mime)

    def _on_batch_done(self, results: list):
        self.set_busy(False)
        # Each successful entry is (bytes, mime) or bare bytes
        good_data: list[bytes] = []
        for r in results:
            if isinstance(r, Exception):
                continue
            if isinstance(r, tuple):
                good_data.append(r[0])
            elif isinstance(r, bytes):
                good_data.append(r)
        if good_data:
            self.right.show_batch_images(good_data)
        errs = [str(r) for r in results if isinstance(r, Exception)]
        if errs:
            QMessageBox.warning(self, "Some images failed",
                "\n".join(errs[:5]))

    def _on_gen_error(self, msg: str):
        self.set_busy(False)
        QMessageBox.critical(self, "Generation Error", msg)

    # ── Image edit ────────────────────────────────────────────────────────

    def _open_edit_dialog(self):
        if not self.right.current_image_bytes:
            return
        prompt, ok = QInputDialog.getText(
            self, "Edit Image", "Describe the edit to apply:")
        if not ok or not prompt.strip():
            return

        provider, key, model, extra = self.get_credentials()
        if not key:
            QMessageBox.warning(self, "No API Key",
                "Please enter an API key in the Settings tab.")
            return

        self.set_busy(True, "Editing image…")

        def _edit_fn(prompt, img_bytes, img_mime):
            if provider == "OpenAI":
                return oi.edit_image_bytes(
                    prompt, img_bytes, img_mime, api_key=key, model=model, **extra)
            else:
                return gs.edit_image_bytes(
                    prompt, img_bytes, img_mime, api_key=key, model=model)

        w = ImageEditWorker(
            _edit_fn, prompt,
            self.right.current_image_bytes,
            self.right.current_image_mime,
        )
        w.finished.connect(self._on_edit_done)
        w.error.connect(self._on_gen_error)
        self._active_workers.append(w)
        w.finished.connect(lambda _: self._active_workers.remove(w))
        w.start()

    def _on_edit_done(self, result):
        self.set_busy(False)
        if isinstance(result, tuple):
            data, mime = result[0], result[1] if len(result) > 1 else "image/png"
        else:
            data, mime = result, "image/png"
        self.right.push_edit(data, mime)

    def _undo_edit(self):
        prev = self.right.pop_undo()
        if prev is None:
            QMessageBox.information(self, "Undo", "Nothing to undo.")

    # ── Save / discard ────────────────────────────────────────────────────

    def _save_preview_image(self):
        data = self.right.current_image_bytes
        if not data:
            return

        save_dir = self.get_save_dir()
        os.makedirs(save_dir, exist_ok=True)

        ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        idx = self.tabs.currentIndex()
        tab = self.tabs.widget(idx)
        prefix = getattr(tab, "image_prefix", "image")
        filename = f"{prefix}_{ts}.png"
        filepath = os.path.join(save_dir, filename)

        try:
            with open(filepath, "wb") as f:
                f.write(data)
            self.set_status(f"Saved → {filepath}")
            # Notify the active tab (e.g. library tab may want to refresh)
            if hasattr(tab, "on_image_saved"):
                tab.on_image_saved(filepath)
        except Exception as exc:
            QMessageBox.critical(self, "Save Error", str(exc))

    def _discard_preview_image(self):
        self.right.clear_preview()
        self.set_status("Image discarded.")

    # ── Clipboard ─────────────────────────────────────────────────────────

    def _copy_to_clipboard(self):
        text = self.right.output_text.toPlainText()
        QApplication.clipboard().setText(text)
        self.set_status("Copied to clipboard.")

    # ── Tab events ────────────────────────────────────────────────────────

    def _on_tab_changed(self, index: int):
        tab = self.tabs.widget(index)
        if hasattr(tab, "on_tab_activated"):
            tab.on_tab_activated()
        # Update generate button to reflect provider
        provider = self._settings.provider() if hasattr(self._settings, "provider") else self.api_provider
        self.right.set_generate_button_label(f"Generate Image ({provider})")

    # ── Settings callback (called by SettingsTab on save) ─────────────────

    def on_settings_saved(self, cfg: dict):
        """Update window-level config from the settings tab."""
        self.api_provider         = cfg.get("api_provider", self.api_provider)
        self.gemini_api_key       = cfg.get("gemini_api_key", self.gemini_api_key)
        self.gemini_model         = cfg.get("gemini_model", self.gemini_model)
        self.openai_api_key       = cfg.get("openai_api_key", self.openai_api_key)
        self.openai_base_url      = cfg.get("openai_base_url", self.openai_base_url)
        self.openai_model         = cfg.get("openai_model", self.openai_model)
        self.openai_image_size    = cfg.get("openai_image_size", self.openai_image_size)
        self.openai_image_quality = cfg.get("openai_image_quality", self.openai_image_quality)
        self.image_save_dir       = cfg.get("image_save_dir", self.image_save_dir)
        self.spaceship_save_dir   = cfg.get("spaceship_save_dir", self.spaceship_save_dir)
        self.items_save_dir       = cfg.get("items_save_dir", self.items_save_dir)
        self.character_save_dir   = cfg.get("character_save_dir", self.character_save_dir)
        self.clothing_save_dir    = cfg.get("clothing_save_dir", self.clothing_save_dir)
        self.ui_lang              = cfg.get("language", self.ui_lang)
        self.save_config(cfg)

    # ── Close ─────────────────────────────────────────────────────────────

    # ── Multi-image Gemini edit (outfit swap etc.) ────────────────────────

    def run_gemini_edit_with_images(self, prompt: str, image_paths: list[str],
                                    output_name: str = "output"):
        """Run a Gemini edit with multiple reference images (e.g. outfit swap)."""
        import mimetypes as _mt

        provider, key, model, _ = self.get_credentials()
        if not key:
            QMessageBox.warning(self, "No API Key",
                "Please enter an API key in the Settings tab.")
            return

        ref_images: list[tuple[bytes, str]] = []
        for path in image_paths:
            if not os.path.exists(path):
                QMessageBox.warning(self, "Missing File",
                    f"Image not found: {path}")
                return
            with open(path, "rb") as fh:
                data = fh.read()
            mime = _mt.guess_type(path)[0] or "image/png"
            ref_images.append((data, mime))

        if not ref_images:
            return

        # Use the first image as the "base" for the edit worker
        base_data, base_mime = ref_images[0]

        self.set_busy(True, "Running outfit swap…")

        def _edit_fn(p, img_bytes, img_mime):
            return gs.edit_image_bytes(
                p, img_bytes, img_mime,
                api_key=key, model=model,
                extra_images=[ref_images[i] for i in range(1, len(ref_images))],
            )

        w = ImageEditWorker(_edit_fn, prompt, base_data, base_mime)
        w.finished.connect(self._on_edit_done)
        w.error.connect(self._on_gen_error)
        self._active_workers.append(w)
        w.finished.connect(lambda _: self._active_workers.remove(w))
        w.start()

    # ── Library → load image for Gemini edit ──────────────────────────────

    def load_image_for_edit(self, image_bytes: bytes, mime: str,
                             prefix: str = "image",
                             batch_id: str = "",
                             initial_prompt: str = ""):
        """Load an image from the library into the preview, then open the edit dialog."""
        self.right.show_single_image(image_bytes, mime)
        # Store prefix on the active tab (library) so save uses it
        self._pending_prefix  = prefix
        self._pending_batch_id = batch_id
        # Open the edit dialog pre-filled with the entry prompt
        prompt, ok = QInputDialog.getText(
            self, "Edit Image",
            "Describe the edit to apply:",
            text=initial_prompt)
        if not ok or not prompt.strip():
            return

        provider, key, model, extra = self.get_credentials()
        if not key:
            QMessageBox.warning(self, "No API Key",
                "Please enter an API key in the Settings tab.")
            return

        self.set_busy(True, "Editing image…")

        def _edit_fn(p, img_bytes, img_mime):
            if provider == "OpenAI":
                return oi.edit_image_bytes(
                    p, img_bytes, img_mime, api_key=key, model=model, **extra)
            else:
                return gs.edit_image_bytes(
                    p, img_bytes, img_mime, api_key=key, model=model)

        w = ImageEditWorker(_edit_fn, prompt, image_bytes, mime)
        w.finished.connect(self._on_edit_done)
        w.error.connect(self._on_gen_error)
        self._active_workers.append(w)
        w.finished.connect(lambda _: self._active_workers.remove(w))
        w.start()

    def closeEvent(self, event: QCloseEvent):
        for w in self._active_workers:
            w.quit()
            w.wait(500)
        event.accept()
