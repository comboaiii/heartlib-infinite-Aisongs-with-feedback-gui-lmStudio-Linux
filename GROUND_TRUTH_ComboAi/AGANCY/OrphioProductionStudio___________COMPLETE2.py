# === AUTO-PATCHED: DLL Fix Import (DO NOT REMOVE) ===
try:
    import windows_dll_fix
except ImportError:
    import os, sys

    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    if sys.platform == "win32":
        try:
            os.add_dll_directory(r"C:\Windows\System32")
        except:
            pass
# === END AUTO-PATCH ===

"""
ORPHIO PRODUCTION STUDIO - PRO EDITION
==========================================
Workflow: Generate → Review → Render → Vault
Version 5.1 - Cyber-Audio UI Overhaul
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import List

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from orphio_config import conf
    from orphio_engine import OrphioEngine
    from lmstudio_controler import LMStudioController
    from Blueprint_Executor import ProducerBlueprintEngine
    import torch
except ImportError as e:
    print(f"❌ {e}")
    sys.exit(1)

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QUrl, QSize
from PyQt6.QtGui import QFont, QTextCursor, QPainter, QColor, QIcon, QPalette
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

try:
    from tagSelector import TagSelectorDialog
except:
    pass

# ============================================================
# 🎨 PRO-AUDIO CYBER STYLESHEET
# ============================================================

PRO_STYLE = """
/* --- GLOBAL RESET --- */
* {
    outline: none;
    selection-background-color: #00FF9D;
    selection-color: #000000;
}

QMainWindow, QWidget {
    background-color: #09090B; /* Deepest Void */
    color: #E4E4E7;
    font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
    font-size: 13px;
}

/* --- HEADERS --- */
QLabel { color: #A1A1AA; }

QLabel#TitleMain {
    color: #00FF9D;
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 1px;
}

QLabel#SectionHeader {
    color: #00FF9D;
    font-weight: 800;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 10px 0px 4px 0px;
    background: transparent;
}

QLabel#StatValue {
    color: #FFFFFF;
    font-family: 'Consolas', monospace;
    font-size: 14px;
    font-weight: bold;
}

/* --- INPUTS & EDITORS --- */
QPlainTextEdit, QTextEdit, QLineEdit {
    background-color: #121214;
    border: 1px solid #27272A;
    border-radius: 6px;
    padding: 12px;
    color: #FFFFFF;
    font-family: 'Consolas', 'Segoe UI', monospace;
}

QPlainTextEdit:focus, QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #00FF9D;
    background-color: #18181B;
}

QLineEdit:disabled, QComboBox:disabled {
    background-color: #0F0F11;
    color: #52525B;
    border: 1px solid #18181B;
}

/* --- COMBO BOX --- */
QComboBox {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 8px 12px;
    color: #F4F4F5;
    min-height: 25px;
}

QComboBox:hover {
    border: 1px solid #71717A;
    background-color: #27272A;
}

QComboBox:on { /* shift the text when the popup opens */
    border: 1px solid #00FF9D;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    selection-background-color: #00FF9D;
    selection-color: #000000;
    color: #F4F4F5;
    outline: none;
}

/* --- SPIN BOX --- */
QSpinBox {
    background-color: #121214;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 8px;
    color: #00FF9D;
    font-weight: bold;
}

QSpinBox:focus {
    border: 1px solid #00FF9D;
}

/* --- BUTTONS --- */
QPushButton {
    background-color: #27272A;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 10px 20px;
    color: #F4F4F5;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
}

QPushButton:hover {
    background-color: #3F3F46;
    border: 1px solid #52525B;
    color: #FFFFFF;
}

QPushButton:pressed {
    background-color: #18181B;
}

/* PRIMARY ACTION BUTTON */
QPushButton#PrimaryBtn {
    background-color: #00FF9D;
    color: #000000;
    border: 1px solid #00FF9D;
    font-weight: 900;
    font-size: 13px;
    padding: 15px;
}

QPushButton#PrimaryBtn:hover {
    background-color: #34D399; /* Slightly darker green/teal */
    border: 1px solid #34D399;
    color: #000000;
}

QPushButton#PrimaryBtn:pressed {
    background-color: #059669;
}

QPushButton#PrimaryBtn:disabled {
    background-color: #27272A;
    border: 1px solid #27272A;
    color: #52525B;
}

/* --- TAB WIDGET (The Pill Look) --- */
QTabWidget::pane {
    border: 1px solid #27272A;
    border-radius: 8px;
    background: #0C0C0E;
    top: -1px; /* Align nicely with bar */
}

QTabBar::tab {
    background: transparent;
    color: #71717A;
    padding: 12px 24px;
    margin-right: 4px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 12px;
}

QTabBar::tab:selected {
    background: #27272A;
    color: #00FF9D;
    border-bottom: 2px solid #00FF9D;
}

QTabBar::tab:hover:!selected {
    background: #18181B;
    color: #E4E4E7;
}

/* --- LISTS --- */
QListWidget {
    background-color: #0C0C0E;
    border: 1px solid #27272A;
    border-radius: 6px;
    padding: 5px;
}

QListWidget::item {
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 2px;
    color: #D4D4D8;
}

QListWidget::item:hover {
    background-color: #18181B;
}

QListWidget::item:selected {
    background-color: #18181B;
    color: #00FF9D;
    border-left: 3px solid #00FF9D;
}

/* --- PROGRESS BAR --- */
QProgressBar {
    background-color: #18181B;
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #00FF9D;
    border-radius: 4px;
}

/* --- SCROLLBAR --- */
QScrollBar:vertical {
    background: #09090B;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #27272A;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover { background: #3F3F46; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

/* --- CHECKBOX --- */
QCheckBox {
    spacing: 8px;
    color: #D4D4D8;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #3F3F46;
    background: #18181B;
}
QCheckBox::indicator:checked {
    background-color: #00FF9D;
    border: 1px solid #00FF9D;
    image: none; /* Can add custom checkmark image if needed */
}

/* --- STATUS BAR --- */
QFrame#StatusBar {
    background-color: #0C0C0E;
    border-top: 1px solid #27272A;
}
"""


# ============================================================
# SIGNAL MANAGER
# ============================================================

class WorkerSignals(QObject):
    log = pyqtSignal(str, str)
    progress = pyqtSignal(int, int)
    draft_complete = pyqtSignal(object)
    render_complete = pyqtSignal(str)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)


# ============================================================
# TAB 1: GENERATE
# ============================================================

class GenerateTab(QWidget):
    """Tab for generating album drafts"""

    generate_requested = pyqtSignal(dict)  # config dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Title
        title = QLabel("GENERATE STUDIO")
        title.setObjectName("TitleMain")
        layout.addWidget(title)

        desc = QLabel("Define the sonic architecture of your album.")
        desc.setStyleSheet("color: #71717A; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(desc)

        # Concept
        layout.addWidget(QLabel("1. ALBUM CONCEPT", objectName="SectionHeader"))
        self.txt_concept = QPlainTextEdit()
        self.txt_concept.setPlaceholderText("Describe your album concept, story, or desired vibe in detail...")
        self.txt_concept.setFixedHeight(100)
        layout.addWidget(self.txt_concept)

        # Settings Container
        settings_frame = QFrame()
        settings_frame.setStyleSheet("background: #0C0C0E; border-radius: 8px; border: 1px solid #18181B;")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(20, 20, 20, 20)
        settings_layout.setSpacing(15)

        # Row 1
        r1 = QHBoxLayout()

        # Strategy
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("PRODUCER STRATEGY", objectName="SectionHeader"))
        self.combo_strategy = QComboBox()
        self.combo_strategy.setMinimumHeight(40)
        v1.addWidget(self.combo_strategy)
        r1.addLayout(v1, 2)

        # Tracks
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("TRACK COUNT", objectName="SectionHeader"))
        self.spin_tracks = QSpinBox()
        self.spin_tracks.setRange(1, 20)
        self.spin_tracks.setValue(5)
        self.spin_tracks.setMinimumHeight(40)
        self.spin_tracks.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v2.addWidget(self.spin_tracks)
        r1.addLayout(v2, 1)

        settings_layout.addLayout(r1)

        # Row 2
        r2 = QHBoxLayout()

        v3 = QVBoxLayout()
        v3.addWidget(QLabel("TAGGING MODE", objectName="SectionHeader"))
        self.combo_tags = QComboBox()
        self.combo_tags.addItems(
            ["AI GENERATED - (Let the model decide)", "MANUAL - (Use Library)", "HYBRID - (Mix both)"])
        self.combo_tags.setMinimumHeight(40)
        v3.addWidget(self.combo_tags)
        r2.addLayout(v3, 1)

        settings_layout.addLayout(r2)

        # Manual Tags Input
        v4 = QVBoxLayout()
        v4.addWidget(QLabel("MANUAL TAG OVERRIDE (Optional)", objectName="SectionHeader"))
        tag_row = QHBoxLayout()
        self.txt_tags = QLineEdit()
        self.txt_tags.setPlaceholderText("e.g. Dark, Synthwave, Slow...")
        self.txt_tags.setMinimumHeight(40)
        tag_row.addWidget(self.txt_tags)

        btn_lib = QPushButton("LIBRARY")
        btn_lib.setFixedSize(80, 40)
        btn_lib.clicked.connect(self.open_tag_library)
        tag_row.addWidget(btn_lib)
        v4.addLayout(tag_row)

        settings_layout.addLayout(v4)

        layout.addWidget(settings_frame)
        layout.addStretch()

        # Generate button
        self.btn_generate = QPushButton("Initialize Generation Sequence")
        self.btn_generate.setObjectName("PrimaryBtn")
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self.emit_generate)
        layout.addWidget(self.btn_generate)

    def open_tag_library(self):
        try:
            dlg = TagSelectorDialog(self.txt_tags.text(), self)
            if dlg.exec():
                self.txt_tags.setText(', '.join(dlg.get_selected_tags()))
        except:
            pass

    def emit_generate(self):
        config = {
            'concept': self.txt_concept.toPlainText(),
            'strategy': self.combo_strategy.currentData(),
            'track_count': self.spin_tracks.value(),
            'tag_mode': self.combo_tags.currentText().split()[0],
            'manual_tags': [t.strip() for t in self.txt_tags.text().split(',') if t.strip()]
        }
        self.generate_requested.emit(config)

    def load_strategies(self, strategies):
        self.combo_strategy.clear()
        for s in strategies:
            name = s['name'] if isinstance(s, dict) else s.name
            # Store full data in userdata
            self.combo_strategy.addItem(name, s)


# ============================================================
# TAB 2: REVIEW DRAFTS
# ============================================================

class ReviewTab(QWidget):
    """Tab for reviewing generated drafts"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.drafts = []
        self.current_draft = None
        self.album_dir = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Left: Draft list
        left_container = QFrame()
        left_container.setStyleSheet("background: #0C0C0E; border-right: 1px solid #27272A;")
        left = QVBoxLayout(left_container)
        left.setContentsMargins(10, 10, 10, 10)

        left.addWidget(QLabel("DRAFT QUEUE", objectName="SectionHeader"))

        self.draft_list = QListWidget()
        self.draft_list.setFrameShape(QFrame.Shape.NoFrame)
        self.draft_list.setStyleSheet("background: transparent; border: none;")
        self.draft_list.currentRowChanged.connect(self.load_draft)
        left.addWidget(self.draft_list)

        layout.addWidget(left_container, 1)

        # Right: Editor
        right = QVBoxLayout()
        right.setContentsMargins(10, 0, 0, 0)

        right.addWidget(QLabel("TRACK METADATA", objectName="SectionHeader"))

        meta_grid = QGridLayout()
        meta_grid.addWidget(QLabel("Title:", styleSheet="color: #71717A;"), 0, 0)
        self.txt_title = QLineEdit()
        meta_grid.addWidget(self.txt_title, 0, 1)

        meta_grid.addWidget(QLabel("Style Tags:", styleSheet="color: #71717A;"), 1, 0)
        self.txt_tags = QLineEdit()
        self.txt_tags.setStyleSheet("color: #00FF9D; font-weight: bold;")
        meta_grid.addWidget(self.txt_tags, 1, 1)

        right.addLayout(meta_grid)

        right.addWidget(QLabel("LYRIC CANVAS", objectName="SectionHeader"))
        self.txt_lyrics = QTextEdit()
        self.txt_lyrics.setStyleSheet("font-size: 14px; line-height: 1.4;")
        right.addWidget(self.txt_lyrics, 1)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("SAVE CHANGES")
        btn_save.setFixedSize(150, 40)
        btn_save.clicked.connect(self.save_draft)

        btn_row.addStretch()
        btn_row.addWidget(btn_save)

        right.addLayout(btn_row)

        layout.addLayout(right, 2)

    def load_album(self, album_path):
        self.album_dir = album_path
        self.drafts = sorted(list(album_path.glob("*_DRAFT.json")))

        self.draft_list.clear()
        for draft in self.drafts:
            try:
                with open(draft, 'r') as f:
                    data = json.load(f)
                    title = data.get('title', 'Untitled')
                    item = QListWidgetItem(f"{title}")
                    item.setData(Qt.ItemDataRole.UserRole, draft)
                    self.draft_list.addItem(item)
            except:
                pass

        if self.drafts:
            self.draft_list.setCurrentRow(0)

    def load_draft(self, index):
        if index < 0 or index >= len(self.drafts):
            return

        try:
            with open(self.drafts[index], 'r') as f:
                self.current_draft = json.load(f)

            params = self.current_draft.get('parameters', {})
            self.txt_title.setText(self.current_draft.get('title', ''))
            self.txt_tags.setText(', '.join(params.get('tags', [])))
            self.txt_lyrics.setPlainText(params.get('lyrics', ''))
        except:
            pass

    def save_draft(self):
        if not self.current_draft:
            return

        try:
            self.current_draft['title'] = self.txt_title.text()
            params = self.current_draft.get('parameters', {})
            params['lyrics'] = self.txt_lyrics.toPlainText()
            params['tags'] = [t.strip() for t in self.txt_tags.text().split(',') if t.strip()]

            idx = self.draft_list.currentRow()
            with open(self.drafts[idx], 'w') as f:
                json.dump(self.current_draft, f, indent=4)

            # Update list item text
            self.draft_list.item(idx).setText(self.txt_title.text())

            QMessageBox.information(self, "Saved", "Draft saved successfully")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def get_all_drafts(self):
        return self.drafts


# ============================================================
# TAB 3: RENDER
# ============================================================

class RenderTab(QWidget):
    """Tab for rendering audio"""

    render_requested = pyqtSignal(list, dict)  # paths, settings

    def __init__(self, parent=None):
        super().__init__(parent)
        self.draft_paths = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        title = QLabel("RENDER ENGINE")
        title.setObjectName("TitleMain")
        layout.addWidget(title)

        # --- Config Panel ---
        config_box = QFrame()
        config_box.setStyleSheet("background: #121214; border: 1px solid #27272A; border-radius: 8px;")
        grid = QGridLayout(config_box)
        grid.setContentsMargins(25, 25, 25, 25)
        grid.setSpacing(20)

        # Duration
        grid.addWidget(QLabel("TARGET DURATION (Sec)", objectName="SectionHeader"), 0, 0)
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(30, 300)
        self.spin_duration.setValue(120)
        self.spin_duration.setFixedHeight(40)
        grid.addWidget(self.spin_duration, 0, 1)

        # CFG
        grid.addWidget(QLabel("CFG SCALE (Adherence)", objectName="SectionHeader"), 1, 0)
        cfg_h = QHBoxLayout()
        self.spin_cfg = QSlider(Qt.Orientation.Horizontal)
        self.spin_cfg.setRange(10, 30)
        self.spin_cfg.setValue(15)
        self.lbl_cfg = QLabel("1.5")
        self.lbl_cfg.setObjectName("StatValue")
        self.lbl_cfg.setStyleSheet("color: #00FF9D; font-size: 18px;")

        self.spin_cfg.valueChanged.connect(lambda v: self.lbl_cfg.setText(f"{v / 10:.1f}"))
        cfg_h.addWidget(self.spin_cfg)
        cfg_h.addWidget(self.lbl_cfg)
        grid.addLayout(cfg_h, 1, 1)

        # Temp
        grid.addWidget(QLabel("TEMPERATURE (Creativity)", objectName="SectionHeader"), 2, 0)
        temp_h = QHBoxLayout()
        self.spin_temp = QSlider(Qt.Orientation.Horizontal)
        self.spin_temp.setRange(7, 13)
        self.spin_temp.setValue(10)
        self.lbl_temp = QLabel("1.0")
        self.lbl_temp.setObjectName("StatValue")
        self.lbl_temp.setStyleSheet("color: #00FF9D; font-size: 18px;")

        self.spin_temp.valueChanged.connect(lambda v: self.lbl_temp.setText(f"{v / 10:.1f}"))
        temp_h.addWidget(self.spin_temp)
        temp_h.addWidget(self.lbl_temp)
        grid.addLayout(temp_h, 2, 1)

        layout.addWidget(config_box)

        # --- Queue Selection ---
        queue_box = QFrame()
        queue_layout = QVBoxLayout(queue_box)

        queue_layout.addWidget(QLabel("PROCESSING QUEUE", objectName="SectionHeader"))

        self.radio_group = QButtonGroup()

        self.check_all = QRadioButton("Render Full Album Sequence")
        self.check_all.setChecked(True)
        self.check_all.setStyleSheet("font-size: 14px; padding: 5px;")
        self.radio_group.addButton(self.check_all)
        queue_layout.addWidget(self.check_all)

        h_sel = QHBoxLayout()
        self.check_selected = QRadioButton("Render Single Track:")
        self.check_selected.setStyleSheet("font-size: 14px; padding: 5px;")
        self.radio_group.addButton(self.check_selected)
        h_sel.addWidget(self.check_selected)

        self.track_selector = QComboBox()
        self.track_selector.setEnabled(False)
        self.track_selector.setStyleSheet("min-width: 250px;")
        h_sel.addWidget(self.track_selector)
        h_sel.addStretch()

        queue_layout.addLayout(h_sel)

        self.check_selected.toggled.connect(self.track_selector.setEnabled)

        layout.addWidget(queue_box)
        layout.addStretch()

        # Render button
        self.btn_render = QPushButton("INITIATE AUDIO RENDER")
        self.btn_render.setObjectName("PrimaryBtn")
        self.btn_render.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_render.clicked.connect(self.emit_render)
        layout.addWidget(self.btn_render)

        # Progress
        self.progress = QProgressBar()
        layout.addWidget(self.progress)
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

    def load_drafts(self, draft_paths):
        self.draft_paths = draft_paths
        self.track_selector.clear()

        for path in draft_paths:
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    title = data.get('title', 'Untitled')
                    self.track_selector.addItem(f"{title}", path)
            except:
                pass

    def emit_render(self):
        if self.check_all.isChecked():
            paths = self.draft_paths
        else:
            idx = self.track_selector.currentIndex()
            paths = [self.draft_paths[idx]] if idx >= 0 else []

        if not paths:
            return

        settings = {
            'duration': self.spin_duration.value(),
            'cfg': self.spin_cfg.value() / 10.0,
            'temp': self.spin_temp.value() / 10.0
        }

        self.render_requested.emit(paths, settings)

    def set_progress(self, current, total):
        if total > 0:
            self.progress.setRange(0, total)
            self.progress.setValue(current)
            self.lbl_status.setText(f"Processing Track {current} of {total}...")
        else:
            self.progress.setRange(0, 0)
            self.lbl_status.setText("Initializing...")


# ============================================================
# TAB 4: VAULT (PLAY & INSPECT)
# ============================================================

class VaultTab(QWidget):
    """Tab for playing and inspecting songs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.positionChanged.connect(self.update_time)
        self.init_ui()
        self.refresh_vault()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Left: Song list
        left_frame = QFrame()
        left_frame.setStyleSheet("background: #0C0C0E; border-right: 1px solid #27272A;")
        left = QVBoxLayout(left_frame)

        header = QHBoxLayout()
        header.addWidget(QLabel("AUDIO VAULT", objectName="SectionHeader"))
        btn_refresh = QPushButton("⟳")
        btn_refresh.setFixedSize(30, 30)
        btn_refresh.clicked.connect(self.refresh_vault)
        header.addWidget(btn_refresh)
        left.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter tracks...")
        self.search.textChanged.connect(self.filter_songs)
        left.addWidget(self.search)

        self.song_list = QListWidget()
        self.song_list.setFrameShape(QFrame.Shape.NoFrame)
        self.song_list.setStyleSheet("background: transparent; border: none;")
        self.song_list.itemClicked.connect(self.load_metadata)
        self.song_list.itemDoubleClicked.connect(self.play_song)
        left.addWidget(self.song_list)

        self.lbl_count = QLabel("0 items")
        self.lbl_count.setStyleSheet("color: #52525B; font-size: 11px;")
        left.addWidget(self.lbl_count)

        layout.addWidget(left_frame, 1)

        # Right: Inspector + Player
        right = QVBoxLayout()
        right.setContentsMargins(10, 0, 0, 0)

        # Player Controls Box
        player_box = QFrame()
        player_box.setStyleSheet("background: #121214; border: 1px solid #27272A; border-radius: 12px;")
        p_layout = QHBoxLayout(player_box)
        p_layout.setContentsMargins(20, 20, 20, 20)

        self.btn_play = QPushButton("▶")
        self.btn_play.setStyleSheet("""
            QPushButton {
                background-color: #00FF9D;
                color: #000;
                font-size: 24px;
                border-radius: 25px;
                min-width: 50px;
                max-width: 50px;
                min-height: 50px;
                max-height: 50px;
                padding: 0;
            }
            QPushButton:hover { background-color: #34D399; }
        """)
        self.btn_play.clicked.connect(self.toggle_play)
        p_layout.addWidget(self.btn_play)

        v_time = QVBoxLayout()
        self.lbl_title_play = QLabel("Select a Track")
        self.lbl_title_play.setStyleSheet("font-weight: bold; font-size: 16px; color: #fff;")
        v_time.addWidget(self.lbl_title_play)

        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setStyleSheet("color: #00FF9D; font-family: monospace;")
        v_time.addWidget(self.lbl_time)
        p_layout.addLayout(v_time)
        p_layout.addStretch()

        right.addWidget(player_box)

        # Info
        right.addWidget(QLabel("TAGS & METADATA", objectName="SectionHeader"))
        self.lbl_tags = QLabel("—")
        self.lbl_tags.setStyleSheet(
            "background: #18181B; padding: 12px; border-radius: 6px; color: #00FF9D; border: 1px solid #27272A;")
        self.lbl_tags.setWordWrap(True)
        right.addWidget(self.lbl_tags)

        right.addWidget(QLabel("LYRICS", objectName="SectionHeader"))
        self.txt_lyrics = QTextEdit()
        self.txt_lyrics.setReadOnly(True)
        self.txt_lyrics.setStyleSheet("color: #A1A1AA; background: transparent; border: 1px solid #27272A;")
        right.addWidget(self.txt_lyrics, 1)

        layout.addLayout(right, 2)

    def refresh_vault(self):
        self.song_list.clear()
        if not conf.OUTPUT_DIR.exists():
            return

        songs = sorted(conf.OUTPUT_DIR.rglob("*.wav"), key=lambda p: p.stat().st_mtime, reverse=True)

        for song in songs:
            if "DISTRIBUTION" in str(song):
                continue
            item = QListWidgetItem(f"{song.stem}")
            item.setData(Qt.ItemDataRole.UserRole, str(song))
            item.setIcon(QIcon())  # Can add music icon here
            self.song_list.addItem(item)

        self.lbl_count.setText(f"{len(songs)} tracks stored")

    def filter_songs(self, text):
        for i in range(self.song_list.count()):
            item = self.song_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def load_metadata(self, item):
        filepath = Path(item.data(Qt.ItemDataRole.UserRole))
        self.lbl_title_play.setText(filepath.stem.replace("_", " "))

        json_path = filepath.with_suffix('.json')
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)

                tags = data.get('configuration', {}).get('input_prompt', {}).get('tags', [])
                self.lbl_tags.setText(', '.join(tags) if tags else "No tags")

                lyrics = data.get('configuration', {}).get('input_prompt', {}).get('lyrics', 'No lyrics')
                self.txt_lyrics.setPlainText(lyrics)
            except:
                self.lbl_tags.setText("Error loading metadata")

    def play_song(self, item):
        filepath = Path(item.data(Qt.ItemDataRole.UserRole))
        self.load_metadata(item)
        self.player.setSource(QUrl.fromLocalFile(str(filepath)))
        self.player.play()
        self.btn_play.setText("⏸")

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            self.player.play()
            self.btn_play.setText("⏸")

    def update_time(self, pos):
        dur = self.player.duration()
        if dur > 0:
            cur = f"{pos // 60000:02d}:{(pos // 1000) % 60:02d}"
            tot = f"{dur // 60000:02d}:{(dur // 1000) % 60:02d}"
            self.lbl_time.setText(f"{cur} / {tot}")
        else:
            self.lbl_time.setText("00:00 / 00:00")


# ============================================================
# MAIN WINDOW - SIMPLE TAB STRUCTURE
# ============================================================

class OrphioStudio(QMainWindow):
    """Pro Studio Workflow"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ORPHIO PRODUCTION STUDIO v5.1")
        self.resize(1400, 850)
        self.setStyleSheet(PRO_STYLE)

        # Components
        self.signals = WorkerSignals()
        self.engine = OrphioEngine(log_callback=lambda m: self.log(m))
        self.lms = LMStudioController(conf.LM_STUDIO_URL)
        self.blueprint_engine = ProducerBlueprintEngine()

        self.rendering_active = False
        self.current_album_dir = None

        # Connect signals
        self.signals.log.connect(self.log_message)
        self.signals.progress.connect(self.update_progress)
        self.signals.draft_complete.connect(self.on_drafts_complete)
        self.signals.render_complete.connect(self.on_render_complete)
        self.signals.error.connect(self.on_error)

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header Bar
        top_bar = QHBoxLayout()
        logo = QLabel("ORPHIO")
        logo.setStyleSheet("color: #FFFFFF; font-weight: 900; font-size: 20px; letter-spacing: 2px;")
        top_bar.addWidget(logo)

        ver = QLabel("STUDIO v5.1")
        ver.setStyleSheet("color: #00FF9D; font-weight: bold; font-size: 11px; margin-top: 5px;")
        top_bar.addWidget(ver)

        top_bar.addStretch()

        self.lbl_lms = QLabel("CONNECTING...")
        self.lbl_lms.setStyleSheet(
            "color: #71717A; font-weight: bold; background: #121214; padding: 5px 10px; border-radius: 4px;")
        top_bar.addWidget(self.lbl_lms)

        layout.addLayout(top_bar)

        # Main tabs
        self.tabs = QTabWidget()

        # Tab 1: Generate
        self.tab_generate = GenerateTab()
        self.tab_generate.load_strategies(self.blueprint_engine.list_producers())
        self.tab_generate.generate_requested.connect(self.start_generation)
        self.tabs.addTab(self.tab_generate, "1. GENERATE")

        # Tab 2: Review
        self.tab_review = ReviewTab()
        self.tabs.addTab(self.tab_review, "2. REVIEW")

        # Tab 3: Render
        self.tab_render = RenderTab()
        self.tab_render.render_requested.connect(self.start_rendering)
        self.tabs.addTab(self.tab_render, "3. RENDER")

        # Tab 4: Vault
        self.tab_vault = VaultTab()
        self.tabs.addTab(self.tab_vault, "4. VAULT")

        layout.addWidget(self.tabs)

        # Status footer
        self.lbl_status = QLabel("System Ready")
        self.lbl_status.setObjectName("StatusBar")
        self.lbl_status.setStyleSheet("color: #52525B; padding: 5px; font-size: 11px;")
        layout.addWidget(self.lbl_status)

        # Check LM Studio
        self.check_lm_studio()

    def check_lm_studio(self):
        ok, msg = self.lms.check_connection()
        if ok:
            self.lbl_lms.setText(f"LINK: {msg}")
            self.lbl_lms.setStyleSheet(
                "color: #00FF9D; background: #064E3B; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        else:
            self.lbl_lms.setText("OFFLINE")
            self.lbl_lms.setStyleSheet(
                "color: #EF4444; background: #450A0A; padding: 5px 10px; border-radius: 4px; font-weight: bold;")

    def log(self, msg):
        self.signals.log.emit(msg, "white")

    def log_message(self, msg, color):
        print(f"[LOG] {msg}")
        self.lbl_status.setText(msg)

    def update_progress(self, current, total):
        self.tab_render.set_progress(current, total)

    def start_generation(self, config):
        if not config['concept']:
            QMessageBox.warning(self, "Missing Input", "Please describe your album concept.")
            return

        self.tab_generate.btn_generate.setEnabled(False)
        self.tab_generate.btn_generate.setText("GENERATING BLUEPRINT...")
        self.lbl_status.setText("Orchestrating production sequence...")

        def generate():
            try:
                blueprint_path = config['strategy']['path'] if isinstance(config['strategy'], dict) else config[
                    'strategy']
                blueprint = self.blueprint_engine.load_blueprint(blueprint_path)

                album_dir = self.blueprint_engine.stage_1_draft_content(
                    blueprint,
                    config['concept'],
                    config['track_count'],
                    config['tag_mode'],
                    config['manual_tags'] if config['tag_mode'] in ["MANUAL", "HYBRID"] else None
                )

                self.signals.draft_complete.emit(album_dir)
            except Exception as e:
                self.signals.error.emit(str(e))

        threading.Thread(target=generate, daemon=True).start()

    def on_drafts_complete(self, album_dir):
        self.current_album_dir = album_dir
        self.tab_generate.btn_generate.setEnabled(True)
        self.tab_generate.btn_generate.setText("Initialize Generation Sequence")
        self.lbl_status.setText("Drafts successfully generated.")

        # Load into review tab
        self.tab_review.load_album(album_dir)

        # Load into render tab
        self.tab_render.load_drafts(self.tab_review.get_all_drafts())

        # Switch to review tab
        self.tabs.setCurrentIndex(1)

        QMessageBox.information(self, "Drafts Ready",
                                "Production blueprint generated. Please review lyrics and tags in Tab 2.")

    def start_rendering(self, paths, settings):
        if self.rendering_active:
            return

        self.rendering_active = True
        self.tab_render.btn_render.setEnabled(False)
        self.tab_render.btn_render.setText("RENDERING IN PROGRESS...")
        self.lbl_status.setText("Initializing audio engine...")

        def render():
            try:
                total = len(paths)
                for idx, path in enumerate(paths, 1):
                    self.signals.progress.emit(idx, total)

                    with open(path, 'r') as f:
                        data = json.load(f)

                    params = data.get('parameters', {})

                    self.engine.free_memory()
                    wav_path, _ = self.engine.render_audio_stage(
                        topic=data.get('title', 'Track'),
                        lyrics=params.get('lyrics', ''),
                        tags=params.get('tags', []),
                        duration_s=settings['duration'],
                        cfg=settings['cfg'],
                        temp=settings['temp']
                    )

                    # Move files
                    album_dir = path.parent
                    track_num = data.get('track_number', idx)
                    title = "".join([c for c in data.get('title', 'Track') if c.isalnum() or c in " _-"]).replace(" ",
                                                                                                                  "_")

                    final_wav = album_dir / f"{track_num:02d}_{title}.wav"
                    final_json = album_dir / f"{track_num:02d}_{title}.json"

                    Path(wav_path).rename(final_wav)
                    Path(wav_path).with_suffix('.json').rename(final_json)
                    path.unlink()

                    time.sleep(1)

                self.signals.render_complete.emit(str(album_dir))
            except Exception as e:
                self.signals.error.emit(str(e))
            finally:
                self.rendering_active = False

    def on_render_complete(self, album_path):
        self.lbl_status.setText("Production Complete.")
        self.tab_render.btn_render.setEnabled(True)
        self.tab_render.btn_render.setText("INITIATE AUDIO RENDER")
        self.signals.progress.emit(0, 0)

        # Refresh vault
        self.tab_vault.refresh_vault()

        # Switch to vault
        self.tabs.setCurrentIndex(3)

        QMessageBox.information(self, "Production Complete",
                                f"Audio rendering finished successfully.\nLocation: {album_path}")

    def on_error(self, msg):
        self.tab_generate.btn_generate.setEnabled(True)
        self.tab_generate.btn_generate.setText("Initialize Generation Sequence")
        self.tab_render.btn_render.setEnabled(True)
        self.tab_render.btn_render.setText("INITIATE AUDIO RENDER")
        self.rendering_active = False
        self.lbl_status.setText("System Error")
        QMessageBox.critical(self, "System Error", msg)


# ============================================================
# MAIN
# ============================================================

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set dark palette for Fusion
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(9, 9, 11))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(228, 228, 231))
    app.setPalette(palette)

    window = OrphioStudio()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()