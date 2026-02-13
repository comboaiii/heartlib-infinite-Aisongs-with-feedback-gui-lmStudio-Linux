

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

import sys
import os
import json
import threading
import time
import random
import re
from pathlib import Path
from datetime import datetime

# --- CRITICAL ENVIRONMENT SETUP ---
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# --- SYSTEM PATHS ---
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# --- IMPORTS ---
try:
    # Core Engine
    from orphio_config import conf
    from orphio_engine import OrphioEngine
    import torch

    # Pipeline Tools
    from Album_Post_Processor import AlbumPostProcessor

    # NEW: Import the Blueprint Engine for Dynamic Strategies
    from Blueprint_Executor import ProducerBlueprintEngine

    # UI Styles
    from agency_styles import MODERN_STYLES
    from tagSelector import TagSelectorDialog

    # PyQt6
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QLineEdit, QFrame,
        QProgressBar, QComboBox, QMessageBox, QSlider,
        QScrollArea, QCheckBox, QGridLayout, QListWidget, QListWidgetItem,
        QSplitter, QFileDialog, QPlainTextEdit, QTabWidget, QMenu, QInputDialog,
        QSizePolicy, QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QGroupBox,
        QAbstractItemView
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QObject, QUrl, QSize, QTimer
    from PyQt6.QtGui import QFont, QTextCursor, QPainter, QColor, QBrush, QAction, QIcon, QPalette
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)


# ============================================================
# RENDERING SETTINGS DIALOG (STYLED)
# ============================================================
class RenderSettingsDialog(QDialog):
    """Dialog for configuring rendering parameters before batch render"""

    def __init__(self, track_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"🎚️ Render Settings for {track_count} Tracks")
        self.setMinimumWidth(600)
        self.setStyleSheet("""
            QDialog { background-color: #09090B; color: #E4E4E7; border: 1px solid #3F3F46; }
            QLabel { color: #E4E4E7; font-size: 13px; }
            QGroupBox { 
                border: 1px solid #27272A; 
                border-radius: 6px; 
                margin-top: 20px; 
                font-weight: bold; 
                color: #00FF7F; 
                padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QSpinBox, QDoubleSpinBox { 
                background: #18181B; border: 1px solid #3F3F46; 
                color: white; padding: 8px; border-radius: 4px; font-weight: bold;
            }
            QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #00FF7F; }
            QCheckBox { color: #A1A1AA; spacing: 8px; }
            QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #3F3F46; border-radius: 3px; background: #18181B; }
            QCheckBox::indicator:checked { background: #00FF7F; border: 1px solid #00FF7F; image: url(none); }
            QPushButton { 
                background: #27272A; color: white; border: 1px solid #3F3F46; 
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { border-color: #00FF7F; color: #00FF7F; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"CONFIGURE BATCH RENDER")
        title.setStyleSheet("font-size: 16px; font-weight: 900; color: #00FF7F; letter-spacing: 1px;")
        layout.addWidget(title)

        sub_title = QLabel(f"Adjust generation parameters for {track_count} queued tracks.")
        sub_title.setStyleSheet("color: #A1A1AA; font-style: italic;")
        layout.addWidget(sub_title)

        # Load ranges from config (or use defaults)
        self.cfg_range = getattr(conf, 'CFG_RANGE', (1.0, 3.0))
        self.temp_range = getattr(conf, 'TEMP_RANGE', (0.7, 1.3))
        self.dur_range = getattr(conf, 'DURATION_RANGE', (30, 300))

        # Settings Grid
        settings_group = QGroupBox("GENERATION PARAMETERS")
        settings_layout = QGridLayout()
        settings_layout.setVerticalSpacing(15)
        settings_layout.setHorizontalSpacing(20)
        settings_layout.setContentsMargins(15, 25, 15, 15)

        # Duration
        lbl_dur = QLabel("Duration (seconds):")
        lbl_dur.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(lbl_dur, 0, 0)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(self.dur_range[0], self.dur_range[1])
        self.duration_spin.setValue(getattr(conf, 'DEFAULT_DURATION', 120))
        self.duration_spin.setSingleStep(10)
        self.duration_spin.setSuffix(" s")
        settings_layout.addWidget(self.duration_spin, 0, 1)

        # CFG Scale
        lbl_cfg = QLabel(f"CFG Scale ({self.cfg_range[0]}-{self.cfg_range[1]}):")
        lbl_cfg.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(lbl_cfg, 1, 0)

        self.cfg_spin = QDoubleSpinBox()
        self.cfg_spin.setRange(self.cfg_range[0], self.cfg_range[1])
        self.cfg_spin.setValue(getattr(conf, 'DEFAULT_CFG', 1.5))
        self.cfg_spin.setSingleStep(0.1)
        self.cfg_spin.setDecimals(2)
        settings_layout.addWidget(self.cfg_spin, 1, 1)

        # Temperature
        lbl_temp = QLabel(f"Temperature ({self.temp_range[0]}-{self.temp_range[1]}):")
        lbl_temp.setStyleSheet("font-weight: bold;")
        settings_layout.addWidget(lbl_temp, 2, 0)

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(self.temp_range[0], self.temp_range[1])
        self.temp_spin.setValue(getattr(conf, 'DEFAULT_TEMP', 1.0))
        self.temp_spin.setSingleStep(0.05)
        self.temp_spin.setDecimals(2)
        settings_layout.addWidget(self.temp_spin, 2, 1)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Parameter Guide
        guide = QLabel(
            "💡 <b>Tip:</b> Higher CFG adheres strictly to tags. Higher Temperature increases creativity/chaos."
        )
        guide.setStyleSheet("color: #71717A; font-size: 11px; margin-top: 5px;")
        layout.addWidget(guide)

        # Apply to All checkbox
        self.apply_all_check = QCheckBox(f"FORCE these settings on all {track_count} tracks (Override drafts)")
        self.apply_all_check.setChecked(True)
        self.apply_all_check.setStyleSheet("color: #E4E4E7; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.apply_all_check)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        # Style the OK button to be visible
        btn_ok = buttons.button(QDialogButtonBox.StandardButton.Ok)
        btn_ok.setText("START RENDER")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        # FORCE NEON STYLE
        btn_ok.setStyleSheet("""
            background-color: #00FF7F; 
            color: #000000; 
            border: none; 
            padding: 12px 24px;
            font-weight: 900;
            border-radius: 4px;
        """)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_settings(self):
        """Returns dict of selected settings"""
        return {
            'duration': self.duration_spin.value(),
            'cfg': self.cfg_spin.value(),
            'temp': self.temp_spin.value(),
            'apply_all': self.apply_all_check.isChecked()
        }


# ============================================================
# 1. CUSTOM UI COMPONENTS
# ============================================================

class AgencyWaveform(QWidget):
    seek_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.bars = []
        self.progress = 0.0
        self.duration_ms = 1
        self.generate_random_shape(12345)

    def generate_random_shape(self, seed):
        random.seed(seed)
        self.bars = [random.uniform(0.15, 0.95) for _ in range(120)]
        self.update()

    def set_progress(self, current_ms, total_ms):
        if total_ms > 0:
            self.progress = current_ms / total_ms
            self.duration_ms = total_ms
        else:
            self.progress = 0
            self.duration_ms = 1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        painter.fillRect(self.rect(), QColor("#0D0D0F"))

        if not self.bars: return

        bar_width = w / len(self.bars)
        for i, h_factor in enumerate(self.bars):
            bar_h = h * h_factor * 0.8
            is_active = i <= int(self.progress * len(self.bars))

            # Active = Neon Green, Inactive = Dark Grey
            color = QColor("#00FF7F") if is_active else QColor("#27272A")

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw rounded bars
            x = int(i * bar_width)
            y = int((h - bar_h) / 2)
            bw = int(bar_width - 1)
            if bw < 1: bw = 1

            painter.drawRoundedRect(x, y, bw, int(bar_h), 2, 2)

    def mousePressEvent(self, event):
        if self.duration_ms <= 0: return
        x_pos = event.position().x()
        width = self.width()
        percent = x_pos / width
        seek_ms = int(percent * self.duration_ms)
        self.seek_requested.emit(seek_ms)
        self.progress = percent
        self.update()


class WorkerSignals(QObject):
    log = pyqtSignal(str)
    finished_draft = pyqtSignal(str, list)
    batch_progress = pyqtSignal(int, int)
    finished_render = pyqtSignal(str)
    finished_decorate = pyqtSignal(str)
    error = pyqtSignal(str)


# ============================================================
# 2. MAIN PRODUCTION STUDIO
# ============================================================

class OrphioStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎹 ORPHIO AGENCY STUDIO - ULTIMATE EDITION")
        self.resize(1800, 1000)

        # Apply Base Styles
        self.setStyleSheet(MODERN_STYLES + """
            QMainWindow { background-color: #050505; }
            QScrollBar:vertical { background: #09090B; width: 10px; margin: 0; }
            QScrollBar::handle:vertical { background: #27272A; min-height: 20px; border-radius: 5px; }
            QScrollBar::handle:vertical:hover { background: #3F3F46; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        # --- LOGIC ENGINES ---
        self.signals = WorkerSignals()
        self.engine = OrphioEngine(log_callback=lambda m: self.signals.log.emit(m))

        # NEW: Initialize Blueprint Engine for Strategies
        try:
            self.blueprint_engine = ProducerBlueprintEngine()
        except Exception as e:
            print(f"Blueprint Engine Init Error: {e}")
            self.blueprint_engine = None

        # Audio
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # State
        self.current_album_path = None
        self.current_working_file = None
        self.render_queue = []
        self.stop_requested = False

        # NEW: Rendering settings storage
        self.last_render_settings = {
            'duration': getattr(conf, 'DEFAULT_DURATION', 120),
            'cfg': getattr(conf, 'DEFAULT_CFG', 1.5),
            'temp': getattr(conf, 'DEFAULT_TEMP', 1.0)
        }

        # Connections
        self.signals.log.connect(self.log_system)
        self.signals.finished_draft.connect(self.on_draft_complete)
        self.signals.finished_decorate.connect(self.on_decorate_complete)
        self.signals.finished_render.connect(self.on_render_complete)
        self.signals.error.connect(self.on_error)
        self.signals.batch_progress.connect(self.on_batch_progress)

        # Player Signals
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)
        self.player.playbackStateChanged.connect(self.update_play_btn_icon)

        self.init_ui()
        self.waveform.seek_requested.connect(self.do_seek)

        self.refresh_vault()
        self.log_system("🎹 System Ready. Select a Strategy Blueprint to begin.")

    def do_seek(self, ms):
        """Explicitly handles the seek request"""
        self.player.setPosition(ms)

    def update_duration_preview(self, value):
        """Update duration preview label and settings"""
        self.lbl_dur_preview.setText(f"{value}s")
        self.last_render_settings['duration'] = value

    def update_cfg_preview(self, value):
        """Update CFG preview label and settings"""
        cfg_val = value / 100.0
        self.lbl_cfg_preview.setText(f"{cfg_val:.2f}")
        self.last_render_settings['cfg'] = cfg_val

    def update_temp_preview(self, value):
        """Update temperature preview label and settings"""
        temp_val = value / 100.0
        self.lbl_temp_preview.setText(f"{temp_val:.2f}")
        self.last_render_settings['temp'] = temp_val

    # -------------------------------------------------------------------------
    # UI CONSTRUCTION
    # -------------------------------------------------------------------------
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === TOP TOOLBAR ===
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #09090B; border-bottom: 1px solid #27272A;")
        toolbar.setFixedHeight(60)
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("ORPHIO AGENCY STUDIO")
        title.setStyleSheet("color: #00FF7F; font-weight: 900; font-size: 20px; letter-spacing: 2px;")

        self.status_lbl = QLabel("⚫ SYSTEM IDLE")
        self.status_lbl.setStyleSheet("color: #71717A; font-weight: bold; font-family: monospace;")

        tb_layout.addWidget(title)
        tb_layout.addStretch()
        tb_layout.addWidget(self.status_lbl)

        main_layout.addWidget(toolbar)

        # === MAIN WORKSPACE SPLITTER ===
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle { background-color: #27272A; }
            QSplitter::handle:hover { background-color: #00FF7F; }
        """)

        # ---------------------------------------------------------
        # 1. LEFT PANEL: CONFIG & STRATEGY (Scrollable)
        # ---------------------------------------------------------
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        left_content = QWidget()
        left_content.setStyleSheet("background-color: #0C0C0E;")
        l_layout = QVBoxLayout(left_content)
        l_layout.setContentsMargins(15, 20, 15, 20)
        l_layout.setSpacing(15)

        # 1. STRATEGY (DYNAMIC LIST)
        l_layout.addWidget(QLabel("1. STRATEGY BLUEPRINT", objectName="SectionHeader"))

        self.strategy_list = QListWidget()
        self.strategy_list.setFixedHeight(140)
        self.strategy_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.strategy_list.setStyleSheet("""
            QListWidget { 
                background: #050505; 
                border: 1px solid #27272A; 
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item { 
                padding: 8px 10px; 
                color: #A1A1AA;
                border-radius: 4px;
                margin-bottom: 2px;
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background: #18181B;
                color: #FFFFFF;
            }
            QListWidget::item:selected { 
                background: #18181B; 
                color: #00FF7F; 
                border-left: 3px solid #00FF7F;
                font-weight: bold;
            }
        """)

        # Load strategies
        try:
            if self.blueprint_engine:
                producers = self.blueprint_engine.list_producers()
                for p in producers:
                    item = QListWidgetItem(p['name'])
                    item.setToolTip(p['desc'])
                    item.setData(Qt.ItemDataRole.UserRole, p)
                    self.strategy_list.addItem(item)
                if self.strategy_list.count() > 0:
                    self.strategy_list.setCurrentRow(0)
            else:
                self.strategy_list.addItem("Error: Blueprint Engine Not Loaded")
        except Exception as e:
            self.strategy_list.addItem(f"Error: {e}")
        l_layout.addWidget(self.strategy_list)

        # 2. TOPIC
        l_layout.addSpacing(5)
        l_layout.addWidget(QLabel("2. CONCEPT / TOPIC", objectName="SectionHeader"))

        self.input_topic = QPlainTextEdit()
        self.input_topic.setPlaceholderText("Enter album concept (e.g., 'A cyberpunk detective story in 2088')...")
        self.input_topic.setFixedHeight(100)
        self.input_topic.setStyleSheet("""
            QPlainTextEdit {
                background-color: #050505;
                border: 1px solid #27272A;
                border-radius: 6px;
                padding: 12px;
                color: #E4E4E7;
                font-size: 13px;
                line-height: 1.4;
            }
            QPlainTextEdit:focus { border: 1px solid #00FF7F; background-color: #000000; }
        """)
        l_layout.addWidget(self.input_topic)

        # 3. TAG STRATEGY
        l_layout.addSpacing(5)
        l_layout.addWidget(QLabel("3. TAG STRATEGY", objectName="SectionHeader"))

        tag_strat_layout = QHBoxLayout()
        self.combo_tag_mode = QComboBox()
        self.combo_tag_mode.addItems(["1. USER DEFINED", "2. AI GENERATED", "3. MIXED (USER + AI)"])
        self.combo_tag_mode.setFixedHeight(35)

        btn_lib = QPushButton("📚 LIBRARY")
        btn_lib.setFixedHeight(35)
        btn_lib.setCursor(Qt.CursorShape.PointingHandCursor)
        # STYLE: Dark Grey + White
        btn_lib.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #00FF7F;
                color: #00FF7F;
            }
        """)
        btn_lib.clicked.connect(self.open_tag_lib_global)

        tag_strat_layout.addWidget(self.combo_tag_mode, 2)
        tag_strat_layout.addWidget(btn_lib, 1)
        l_layout.addLayout(tag_strat_layout)

        self.input_global_tags = QLineEdit()
        self.input_global_tags.setPlaceholderText("Global Tags (e.g. Pop, Female Vocals)...")
        self.input_global_tags.setFixedHeight(35)
        l_layout.addWidget(self.input_global_tags)

        # 4. ALBUM PARAMETERS
        l_layout.addSpacing(5)
        l_layout.addWidget(QLabel("4. PRODUCTION SETTINGS", objectName="SectionHeader"))

        # Count Row
        count_container = QFrame()
        count_container.setStyleSheet("background: #18181B; border-radius: 6px; padding: 8px;")
        count_layout = QHBoxLayout(count_container)
        count_layout.setContentsMargins(10, 5, 10, 5)

        count_label = QLabel("Total Songs:")
        count_label.setStyleSheet("color: #E4E4E7; font-weight: bold; border: none;")

        self.spin_count = QComboBox()
        self.spin_count.addItems([str(i) for i in range(1, 21)])
        self.spin_count.setCurrentText("3")
        self.spin_count.setFixedWidth(60)
        self.spin_count.setStyleSheet("background: #27272A; border: none; color: #00FF7F; font-weight: bold;")

        count_layout.addWidget(count_label)
        count_layout.addStretch()
        count_layout.addWidget(self.spin_count)
        l_layout.addWidget(count_container)

        # SETTINGS GROUP
        settings_preview = QGroupBox("DEFAULT RENDER PARAMS")
        settings_preview.setStyleSheet("""
            QGroupBox {
                background-color: #0D0D0F;
                border: 1px solid #27272A;
                border-radius: 6px;
                margin-top: 15px;
                padding-top: 25px;
                font-weight: 700;
                color: #A1A1AA;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        settings_prev_layout = QVBoxLayout()
        settings_prev_layout.setSpacing(15)
        settings_prev_layout.setContentsMargins(15, 10, 15, 15)

        # Sliders Helper
        def add_slider_row(label, val_label, slider_obj):
            row = QVBoxLayout()
            row.setSpacing(5)

            header = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #71717A; font-size: 11px; font-weight: 600; border: none;")
            val_label.setStyleSheet("color: #00FF7F; font-weight: bold; font-size: 12px; border: none;")
            header.addWidget(lbl)
            header.addStretch()
            header.addWidget(val_label)
            row.addLayout(header)

            slider_obj.setOrientation(Qt.Orientation.Horizontal)
            slider_obj.setStyleSheet("""
                QSlider::groove:horizontal { height: 4px; background: #27272A; border-radius: 2px; }
                QSlider::handle:horizontal { background: #00FF7F; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
                QSlider::handle:horizontal:hover { background: #34D399; }
                QSlider::sub-page:horizontal { background: #059669; border-radius: 2px; }
            """)
            row.addWidget(slider_obj)
            settings_prev_layout.addLayout(row)

        # Duration
        self.lbl_dur_preview = QLabel(f"{self.last_render_settings['duration']}s")
        self.sld_dur = QSlider()
        self.sld_dur.setRange(30, 300)
        self.sld_dur.setValue(self.last_render_settings['duration'])
        self.sld_dur.setSingleStep(10)
        self.sld_dur.valueChanged.connect(self.update_duration_preview)
        add_slider_row("Duration", self.lbl_dur_preview, self.sld_dur)

        # CFG
        self.lbl_cfg_preview = QLabel(f"{self.last_render_settings['cfg']:.2f}")
        self.sld_cfg = QSlider()
        cfg_range = getattr(conf, 'CFG_RANGE', (1.0, 3.0))
        self.sld_cfg.setRange(int(cfg_range[0] * 100), int(cfg_range[1] * 100))
        self.sld_cfg.setValue(int(self.last_render_settings['cfg'] * 100))
        self.sld_cfg.valueChanged.connect(self.update_cfg_preview)
        add_slider_row("CFG Scale (Adherence)", self.lbl_cfg_preview, self.sld_cfg)

        # Temp
        self.lbl_temp_preview = QLabel(f"{self.last_render_settings['temp']:.2f}")
        self.sld_temp = QSlider()
        temp_range = getattr(conf, 'TEMP_RANGE', (0.7, 1.3))
        self.sld_temp.setRange(int(temp_range[0] * 100), int(temp_range[1] * 100))
        self.sld_temp.setValue(int(self.last_render_settings['temp'] * 100))
        self.sld_temp.valueChanged.connect(self.update_temp_preview)
        add_slider_row("Temperature (Creativity)", self.lbl_temp_preview, self.sld_temp)

        settings_preview.setLayout(settings_prev_layout)
        l_layout.addWidget(settings_preview)

        l_layout.addSpacing(15)

        # GENERATE BUTTON (Explicitly Styled)
        self.btn_gen_album = QPushButton("🎼  GENERATE ALBUM DRAFTS")
        self.btn_gen_album.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gen_album.setFixedHeight(50)
        # FORCE STYLE: Neon Green Bg, Black Text
        self.btn_gen_album.setStyleSheet("""
            QPushButton {
                background-color: #00FF7F;
                color: #000000;
                font-weight: 900;
                font-size: 13px;
                border-radius: 6px;
                border: none;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #34D399;
            }
            QPushButton:pressed {
                background-color: #059669;
                padding-top: 2px;
            }
        """)
        self.btn_gen_album.clicked.connect(self.run_album_generation)
        l_layout.addWidget(self.btn_gen_album)

        l_layout.addStretch()

        left_scroll.setWidget(left_content)
        splitter.addWidget(left_scroll)

        # ---------------------------------------------------------
        # 2. CENTER PANEL: TABS (Queue & Editor)
        # ---------------------------------------------------------
        center_panel = QFrame()
        center_panel.setStyleSheet("background-color: #09090B;")
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 10, 0, 0)

        self.center_tabs = QTabWidget()
        self.center_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #27272A; background: #050505; border-radius: 0 0 6px 6px; }
            QTabBar::tab { 
                background: #18181B; color: #71717A; padding: 12px 25px; 
                border-top-left-radius: 4px; border-top-right-radius: 4px;
                font-weight: bold; margin-right: 2px;
            }
            QTabBar::tab:selected { background: #050505; color: #00FF7F; border-top: 2px solid #00FF7F; }
            QTabBar::tab:hover { color: #FFFFFF; background: #27272A; }
        """)

        # TAB 1: QUEUE
        self.queue_tab = QWidget()
        q_layout = QVBoxLayout(self.queue_tab)
        q_layout.setContentsMargins(20, 20, 20, 20)
        q_layout.setSpacing(15)

        q_head = QHBoxLayout()
        q_title = QLabel("PRODUCTION QUEUE")
        q_title.setStyleSheet("font-weight:900; color:white; font-size:16px; letter-spacing:1px;")

        btn_ref = QPushButton("🔄 REFRESH")
        btn_ref.setFixedSize(90, 30)
        btn_ref.setCursor(Qt.CursorShape.PointingHandCursor)
        # STYLE: Dark Grey + White
        btn_ref.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                border-color: #00FF7F;
                color: #00FF7F;
            }
        """)
        btn_ref.clicked.connect(self.load_album_queue)

        q_head.addWidget(q_title)
        q_head.addStretch()
        q_head.addWidget(btn_ref)
        q_layout.addLayout(q_head)

        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget { 
                background: #0D0D0F; 
                border: 1px solid #27272A; 
                font-size: 13px;
                border-radius: 6px;
                padding: 10px;
                outline: none;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #18181B;
                border-radius: 4px;
                margin-bottom: 4px;
                color: #D4D4D8;
            }
            QListWidget::item:hover { background: #18181B; color: white; }
            QListWidget::item:selected { 
                background: #27272A; 
                border-left: 3px solid #00FF7F; 
                color: #00FF7F;
                font-weight: bold;
            }
        """)
        self.queue_list.itemClicked.connect(self.load_draft_from_queue)
        q_layout.addWidget(self.queue_list)

        btn_render_all = QPushButton("🎬  START BATCH RENDER")
        btn_render_all.setFixedHeight(50)
        btn_render_all.setCursor(Qt.CursorShape.PointingHandCursor)
        # FORCE STYLE: Neon Green Bg, Black Text
        btn_render_all.setStyleSheet("""
            QPushButton {
                background-color: #00FF7F;
                color: #000000;
                font-weight: 900;
                font-size: 13px;
                border-radius: 6px;
                border: none;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background-color: #34D399;
            }
            QPushButton:pressed {
                background-color: #059669;
                padding-top: 2px;
            }
        """)
        btn_render_all.clicked.connect(self.run_batch_render)
        q_layout.addWidget(btn_render_all)

        self.center_tabs.addTab(self.queue_tab, "ALBUM QUEUE")

        # TAB 2: EDITOR
        self.editor_tab = QWidget()
        e_layout = QVBoxLayout(self.editor_tab)
        e_layout.setContentsMargins(20, 20, 20, 20)
        e_layout.setSpacing(15)

        # Editor Header
        e_head = QHBoxLayout()
        self.lbl_editing = QLabel("EDITING: None")
        self.lbl_editing.setStyleSheet("color: #FF9F1A; font-weight: bold; font-size: 14px;")

        btn_save = QPushButton("💾 SAVE CHANGES")
        btn_save.setFixedSize(130, 35)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        # STYLE: Dark Grey + White
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #00FF7F;
                color: #00FF7F;
            }
        """)
        btn_save.clicked.connect(self.save_current_draft)

        e_head.addWidget(self.lbl_editing)
        e_head.addStretch()
        e_head.addWidget(btn_save)
        e_layout.addLayout(e_head)

        # Editable Tags Field
        tags_container = QGroupBox("LIVE TAGS (These define the sound)")
        tags_container.setStyleSheet(
            "QGroupBox { font-weight: bold; color: #71717A; border: 1px solid #27272A; padding-top: 15px; border-radius: 4px; }")
        t_layout = QVBoxLayout(tags_container)

        self.txt_live_tags = QLineEdit()
        self.txt_live_tags.setPlaceholderText("e.g. Pop, Female Vocals, Sad, Synthesizer...")
        self.txt_live_tags.setStyleSheet("""
            background: #18181B; color: #00FF7F; font-weight: bold; 
            border: 1px solid #3F3F46; padding: 10px; font-size: 13px;
        """)
        t_layout.addWidget(self.txt_live_tags)
        e_layout.addWidget(tags_container)

        # Lyrics Canvas
        e_layout.addWidget(
            QLabel("LYRICS & STRUCTURE:", styleSheet="color: #71717A; font-weight: bold; margin-top: 5px;"))
        self.txt_lyrics = QTextEdit()
        self.txt_lyrics.setFont(QFont("Consolas", 11))
        self.txt_lyrics.setPlaceholderText("Generated lyrics will appear here...")
        self.txt_lyrics.setStyleSheet("""
            QTextEdit {
                background: #0D0D0F; color: #E4E4E7; padding: 15px; 
                border: 1px solid #27272A; border-radius: 6px; line-height: 150%;
            }
            QTextEdit:focus { border: 1px solid #00FF7F; }
        """)
        e_layout.addWidget(self.txt_lyrics)

        # Decorator Controls
        dec_frame = QFrame()
        dec_frame.setStyleSheet("background: #18181B; border-radius: 6px; padding: 5px;")
        dec_layout = QHBoxLayout(dec_frame)
        dec_layout.setContentsMargins(10, 10, 10, 10)

        dec_lbl = QLabel("Lyrics Decorator:")
        dec_lbl.setStyleSheet("color: #A1A1AA; font-weight: bold;")

        self.combo_dec = QComboBox()
        self.combo_dec.addItems(list(conf.DECORATOR_SCHEMAS.keys()))
        self.combo_dec.setStyleSheet("background: #27272A; color: white; padding: 5px;")

        btn_dec = QPushButton("✨ APPLY")
        btn_dec.setFixedSize(80, 30)
        btn_dec.setCursor(Qt.CursorShape.PointingHandCursor)
        # STYLE: Dark Grey + White
        btn_dec.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #FFFFFF;
                border: 1px solid #3F3F46;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: #00FF7F;
                color: #00FF7F;
            }
        """)
        btn_dec.clicked.connect(self.run_decorate)

        dec_layout.addWidget(dec_lbl)
        dec_layout.addWidget(self.combo_dec, 1)
        dec_layout.addWidget(btn_dec)
        e_layout.addWidget(dec_frame)

        self.center_tabs.addTab(self.editor_tab, "LYRIC EDITOR")
        center_layout.addWidget(self.center_tabs)
        splitter.addWidget(center_panel)

        # ---------------------------------------------------------
        # 3. RIGHT PANEL: VAULT & LOGS
        # ---------------------------------------------------------
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #0C0C0E;")
        r_layout = QVBoxLayout(right_panel)
        r_layout.setContentsMargins(0, 0, 0, 0)
        r_layout.setSpacing(0)

        # Top: Vault
        vault_container = QWidget()
        v_layout = QVBoxLayout(vault_container)
        v_layout.setContentsMargins(15, 20, 15, 10)

        v_head = QHBoxLayout()
        v_head.addWidget(QLabel("COMPLETED VAULT", objectName="SectionHeader"))
        v_head.addStretch()

        btn_folder = QPushButton("📂")
        btn_folder.setToolTip("Open Folder")
        btn_folder.setFixedSize(30, 25)
        # STYLE: Transparent + White
        btn_folder.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #A1A1AA;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover { color: #00FF7F; }
        """)
        btn_folder.clicked.connect(self.open_vault_folder)
        v_head.addWidget(btn_folder)
        v_layout.addLayout(v_head)

        self.vault_list = QListWidget()
        self.vault_list.setStyleSheet("""
            QListWidget {
                background: #050505;
                border: 1px solid #27272A;
                border-radius: 6px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                color: #A1A1AA;
                border-bottom: 1px solid #18181B;
            }
            QListWidget::item:hover { background: #18181B; color: white; }
            QListWidget::item:selected { color: #00FF7F; background: #18181B; }
        """)
        self.vault_list.itemDoubleClicked.connect(self.play_vault_item)
        v_layout.addWidget(self.vault_list)
        r_layout.addWidget(vault_container, 2)

        # Bottom: Log
        log_container = QWidget()
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(15, 0, 15, 20)
        log_layout.addWidget(QLabel("SYSTEM LOG", objectName="SectionHeader"))

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("""
            QTextEdit { 
                font-family: 'Consolas', monospace; 
                font-size: 10px; 
                color: #A1A1AA; 
                background: #000000;
                border: 1px solid #27272A;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.txt_log)
        r_layout.addWidget(log_container, 1)

        splitter.addWidget(right_panel)

        # Set Splitter Ratios (Left: 20%, Center: 55%, Right: 25%)
        splitter.setSizes([350, 900, 350])
        main_layout.addWidget(splitter)

        # === BOTTOM: PLAYER BAR ===
        player_frame = QFrame()
        player_frame.setFixedHeight(80)
        player_frame.setStyleSheet("""
            QFrame { background: #0D0D0F; border-top: 1px solid #27272A; }
        """)
        p_layout = QHBoxLayout(player_frame)
        p_layout.setContentsMargins(20, 10, 20, 10)
        p_layout.setSpacing(20)

        # Play Button
        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(50, 50)
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.setStyleSheet("""
            QPushButton {
                border-radius: 25px;
                background: #00FF7F;
                color: black;
                font-size: 20px;
                padding-bottom: 2px;
                border: 2px solid #059669;
            }
            QPushButton:hover { background: #34D399; }
            QPushButton:pressed { background: #059669; }
        """)
        self.btn_play.clicked.connect(self.toggle_play)
        p_layout.addWidget(self.btn_play)

        # Waveform
        self.waveform = AgencyWaveform()
        p_layout.addWidget(self.waveform, 1)

        # Time
        self.lbl_time = QLabel("00:00 / 00:00")
        self.lbl_time.setStyleSheet("font-family: monospace; font-size: 12px; color: #E4E4E7; font-weight: bold;")
        self.lbl_time.setFixedWidth(100)
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p_layout.addWidget(self.lbl_time)

        main_layout.addWidget(player_frame)

        # Progress Bar (Bottom Edge)
        self.prog_bar = QProgressBar()
        self.prog_bar.setFixedHeight(4)
        self.prog_bar.setTextVisible(False)
        self.prog_bar.setStyleSheet("""
            QProgressBar { background: transparent; border: none; }
            QProgressBar::chunk { background-color: #00FF7F; }
        """)
        main_layout.addWidget(self.prog_bar)

    # -------------------------------------------------------------------------
    # CORE LOGIC: ALBUM GENERATION (DYNAMIC STRATEGY)
    # -------------------------------------------------------------------------

    def run_album_generation(self):
        topic = self.input_topic.toPlainText()
        if not topic:
            QMessageBox.warning(self, "Missing Concept", "Please enter an album concept.")
            return

        # 1. Get Selected Blueprint
        selected_items = self.strategy_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Missing Strategy", "Please select a Strategy Blueprint from the list.")
            return

        blueprint_meta = selected_items[0].data(Qt.ItemDataRole.UserRole)

        # Load the actual JSON content via the engine
        if not self.blueprint_engine:
            QMessageBox.critical(self, "Error", "Blueprint Engine failed to initialize.")
            return

        try:
            blueprint_data = self.blueprint_engine.load_blueprint(blueprint_meta['path'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load blueprint file: {e}")
            return

        count = int(self.spin_count.currentText())
        tag_mode = self.combo_tag_mode.currentText()
        global_tags = self.input_global_tags.text()

        self.log_system(f"🚀 Initializing: '{blueprint_meta['name']}' ({count} tracks)")
        self.prog_bar.setRange(0, 0)

        # Run in thread
        threading.Thread(
            target=self._bg_generate_album_logic,
            args=(topic, count, blueprint_data, tag_mode, global_tags),
            daemon=True
        ).start()

    def _bg_generate_album_logic(self, topic, count, blueprint, tag_mode, global_tags):
        try:
            # --- 1. ROBUST PLANNER (Blueprint Driven) ---
            self.signals.log.emit(f"🧠 {blueprint['name']}: Planning tracklist...")

            # Extract System Prompt from Blueprint
            exec_prompt = blueprint['executive_strategy']['system_prompt']

            # We use a dirty-json parser approach
            system_prompt = (
                f"{exec_prompt}\n"
                f"Context: {topic}\n"
                f"Requirement: Plan exactly {count} tracks.\n"
                "STRICT OUTPUT FORMAT: Return ONLY a raw JSON list of objects. No markdown. No text.\n"
                "Example: [{\"title\": \"Song A\", \"mood\": \"Dark\", \"instruction\": \"Slow build\"}, ...]"
            )

            plan_raw = self.engine.lms.chat(system_prompt, "Generate JSON plan now.", temp=0.7)

            # CLEAN THE JSON (The Fix)
            plan_raw = plan_raw.replace("```json", "").replace("```", "").strip()
            # Find the first '[' and last ']'
            start = plan_raw.find('[')
            end = plan_raw.rfind(']') + 1

            tracks_meta = []
            if start != -1 and end != -1:
                try:
                    tracks_meta = json.loads(plan_raw[start:end])
                except:
                    self.signals.log.emit("⚠️ JSON Plan Failed. Using Fallback Generator.")

            # Fallback if LLM failed JSON
            if not tracks_meta or len(tracks_meta) != count:
                for i in range(count):
                    tracks_meta.append({
                        "title": f"Track {i + 1} - {topic[:10]}...",
                        "mood": "General",
                        "instruction": f"Part {i + 1} of the story."
                    })

            # Setup Directory
            # FIX: Aggressively sanitize the topic string for Windows filenames
            # Remove special characters like newlines, tabs, colons, etc.
            safe_topic = "".join([c for c in topic if c.isalnum() or c == " "]).strip()

            # Additional check to ensure we don't end up with empty string
            if not safe_topic:
                safe_topic = "Untitled_Project"

            # Replace spaces with underscores and limit length
            safe_topic = safe_topic.replace(" ", "_")[:20]

            album_title = f"ALBUM_{int(time.time())}_{safe_topic}"
            album_dir = conf.OUTPUT_DIR / album_title
            album_dir.mkdir(parents=True, exist_ok=True)

            # Save Blueprint Manifest
            with open(album_dir / "00_BLUEPRINT_MANIFEST.json", "w", encoding='utf-8') as f:
                json.dump({"blueprint": blueprint, "plan": tracks_meta}, f, indent=4)

            # --- 2. LOAD TAG LIBRARY ---
            library_tags = []
            if "LIB" in tag_mode or "MIXED" in tag_mode:
                if conf.TAGS_FILE.exists():
                    try:
                        with open(conf.TAGS_FILE, 'r') as f:
                            tag_data = json.load(f)
                            if isinstance(tag_data, dict):
                                for k, v in tag_data.items():
                                    if isinstance(v, list): library_tags.extend(v)
                            elif isinstance(tag_data, list):
                                library_tags = tag_data
                    except:
                        self.signals.log.emit("⚠️ Could not load Tag Library.")

            # --- 3. GENERATION LOOP (Blueprint Propagation) ---
            context_history = []
            lyric_template = blueprint['propagation_logic']['lyric_instruction_template']

            for i, meta in enumerate(tracks_meta):
                t_title = meta.get('title', f"Track {i + 1}")
                t_instr = meta.get('instruction', '')
                t_mood = meta.get('mood', '')

                self.signals.log.emit(f"✍️ Writing {i + 1}/{count}: {t_title}")

                # Dynamic Context Prompt
                prev_ctx = context_history[-1] if context_history else "Opening Track"

                # Use the template from the JSON blueprint
                lyric_prompt = lyric_template.replace("{album_title}", topic) \
                    .replace("{album_theme}", topic) \
                    .replace("{track_title}", t_title) \
                    .replace("{track_num}", str(i + 1)) \
                    .replace("{total_tracks}", str(count)) \
                    .replace("{scene_description}", f"{t_mood}. {t_instr}") \
                    .replace("{prev_context}", prev_ctx)

                lyrics = self.engine.lms.chat(conf.PROMPT_WRITER, lyric_prompt, temp=0.8)
                lyrics = self.engine._enforce_tag_schema(lyrics)

                # --- TAG LOGIC ---
                final_tags = []
                user_input_tags = [t.strip() for t in global_tags.split(',') if t.strip()]

                lib_selected = []
                if "LIB" in tag_mode and library_tags:
                    lib_selected = random.sample(library_tags, min(2, len(library_tags)))

                ai_tags = []
                if "AI" in tag_mode or "MIXED" in tag_mode:
                    raw_ai = self.engine.lms.chat(conf.PROMPT_TAGGER, lyrics, temp=0.3)
                    ai_tags = self.engine._clean_tags_list(raw_ai)

                if "USER" in tag_mode:
                    final_tags = user_input_tags
                elif "AI" in tag_mode:
                    final_tags = ai_tags
                elif "LIB" in tag_mode:
                    final_tags = lib_selected + user_input_tags
                elif "MIXED" in tag_mode:
                    final_tags = user_input_tags + lib_selected + ai_tags

                final_tags = list(set(final_tags))[:6]

                # SAVE DRAFT
                draft_data = {
                    "track_number": i + 1,
                    "title": t_title,
                    "status": "DRAFT_READY",
                    "parameters": {
                        "topic": t_title,
                        "lyrics": lyrics,
                        "tags": final_tags,
                        "blueprint_used": blueprint['name']
                    }
                }

                safe_name = "".join([c for c in t_title if c.isalnum() or c in " _-"]).strip().replace(" ", "_")
                fname = f"{i + 1:02d}_{safe_name}_DRAFT.json"
                with open(album_dir / fname, "w", encoding='utf-8') as f:
                    json.dump(draft_data, f, indent=4)

                context_history.append(f"Song {t_title} was about {t_mood}")
                time.sleep(0.5)

            self.current_album_path = album_dir
            self.signals.finished_draft.emit("ALBUM_COMPLETE", [])

        except Exception as e:
            self.signals.error.emit(f"Gen Error: {str(e)}")

    def on_draft_complete(self, msg, tags):
        self.prog_bar.setRange(0, 100)
        self.prog_bar.setValue(100)
        self.load_album_queue()
        self.center_tabs.setCurrentIndex(0)
        QMessageBox.information(self, "Success", "Album Generation Complete! Review drafts in the queue.")

    # -------------------------------------------------------------------------
    # QUEUE & EDITOR
    # -------------------------------------------------------------------------

    def load_album_queue(self):
        self.queue_list.clear()
        self.render_queue = []

        if not self.current_album_path:
            if conf.OUTPUT_DIR.exists():
                albums = sorted([d for d in conf.OUTPUT_DIR.glob("ALBUM_*") if d.is_dir()],
                                key=os.path.getmtime, reverse=True)
                if albums:
                    self.current_album_path = albums[0]
                else:
                    return

        if not self.current_album_path: return

        self.log_system(f"📂 Loaded Album: {self.current_album_path.name}")

        drafts = sorted(list(self.current_album_path.glob("*_DRAFT.json")))
        for d in drafts:
            wav_name = d.name.replace("_DRAFT.json", ".wav")
            is_done = (self.current_album_path / wav_name).exists()

            icon = "✅" if is_done else "📝"
            item = QListWidgetItem(f"{icon} {d.name}")
            item.setData(Qt.ItemDataRole.UserRole, str(d))

            if not is_done:
                self.render_queue.append(d)
                # Draft item styling
                item.setForeground(QBrush(QColor("#E4E4E7")))
            else:
                # Finished item styling
                item.setForeground(QBrush(QColor("#00FF7F")))

            self.queue_list.addItem(item)

    def load_draft_from_queue(self, item):
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        if not path.exists(): return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.current_working_file = path
            self.lbl_editing.setText(f"EDITING: {path.name}")

            params = data.get('parameters', {})
            self.txt_lyrics.setPlainText(params.get('lyrics', ''))
            self.txt_live_tags.setText(", ".join(params.get('tags', [])))

            self.center_tabs.setCurrentIndex(1)

        except Exception as e:
            self.log_system(f"Error loading draft: {e}")

    def save_current_draft(self):
        if not self.current_working_file: return
        try:
            with open(self.current_working_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            data['parameters']['lyrics'] = self.txt_lyrics.toPlainText()
            data['parameters']['tags'] = [t.strip() for t in self.txt_live_tags.text().split(",") if t.strip()]

            with open(self.current_working_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)

            self.log_system(f"💾 Saved: {self.current_working_file.name}")
            self.load_album_queue()
        except Exception as e:
            self.log_system(f"Save failed: {e}")

    # -------------------------------------------------------------------------
    # BATCH RENDERING (ENHANCED WITH SETTINGS DIALOG)
    # -------------------------------------------------------------------------

    def run_batch_render(self):
        if not self.render_queue:
            QMessageBox.information(self, "Empty", "No drafts to render.")
            return

        # NEW: Show settings dialog before rendering, using current slider values
        dialog = RenderSettingsDialog(len(self.render_queue), self)

        # Pre-populate with current slider values
        dialog.duration_spin.setValue(self.last_render_settings['duration'])
        dialog.cfg_spin.setValue(self.last_render_settings['cfg'])
        dialog.temp_spin.setValue(self.last_render_settings['temp'])

        if dialog.exec() == QDialog.DialogCode.Accepted:
            settings = dialog.get_settings()

            # Update sliders and labels to match dialog
            self.sld_dur.setValue(settings['duration'])
            self.sld_cfg.setValue(int(settings['cfg'] * 100))
            self.sld_temp.setValue(int(settings['temp'] * 100))

            self.log_system(f"🔥 Batch Rendering {len(self.render_queue)} tracks...")
            self.log_system(
                f"⚙️ Settings: Duration={settings['duration']}s, CFG={settings['cfg']}, Temp={settings['temp']}")

            threading.Thread(
                target=self._bg_batch_render,
                args=(self.render_queue, settings),
                daemon=True
            ).start()

    def _bg_batch_render(self, queue, settings):
        total = len(queue)
        for i, draft_path in enumerate(queue):
            self.signals.log.emit(f"Rendering {i + 1}/{total}: {draft_path.name}")
            self.signals.batch_progress.emit(i, total)

            try:
                with open(draft_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                params = data.get('parameters', {})

                # Use settings from dialog
                wav_path, ledger = self.engine.render_audio_stage(
                    topic=data.get('title', 'Untitled'),
                    lyrics=params.get('lyrics'),
                    tags=params.get('tags'),
                    duration_s=settings['duration'],
                    cfg=settings['cfg'],
                    temp=settings['temp']
                )

                # NEW: Update ledger with actual settings used
                ledger.configuration.cfg_scale = settings['cfg']
                ledger.configuration.temperature = settings['temp']
                ledger.configuration.duration_sec = settings['duration']

                # Save updated ledger
                json_path = Path(wav_path).with_suffix('.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    f.write(ledger.model_dump_json(indent=4))

                # Rename
                dest = draft_path.with_suffix('.wav').name.replace("_DRAFT", "")
                final = draft_path.parent / dest
                if Path(wav_path).exists():
                    Path(wav_path).rename(final)
                    # Also move the JSON
                    json_dest = final.with_suffix('.json')
                    if json_path.exists():
                        json_path.rename(json_dest)

            except Exception as e:
                self.signals.error.emit(f"Render Error: {e}")

        self.signals.batch_progress.emit(total, total)

        # Auto Master
        try:
            self.signals.log.emit("🎚️ Mastering Album...")
            processor = AlbumPostProcessor(queue[0].parent)
            processor.process_album()
            self.signals.finished_render.emit("DONE")
        except:
            pass

    def on_batch_progress(self, curr, total):
        self.prog_bar.setRange(0, total)
        self.prog_bar.setValue(curr)

    def on_render_complete(self, msg):
        self.refresh_vault()
        self.load_album_queue()
        QMessageBox.information(self, "Done", "Batch Render & Mastering Complete.")

    # -------------------------------------------------------------------------
    # UTILS
    # -------------------------------------------------------------------------
    def open_tag_lib_global(self):
        dlg = TagSelectorDialog(self.input_global_tags.text(), self)
        if dlg.exec():
            self.input_global_tags.setText(", ".join(dlg.get_selected_tags()))

    def run_decorate(self):
        txt = self.txt_lyrics.toPlainText()
        tags = [t.strip() for t in self.txt_live_tags.text().split(",")]
        conf.CURRENT_DECORATOR_SCHEMA = self.combo_dec.currentText()
        self.prog_bar.setRange(0, 0)
        threading.Thread(target=self._bg_decorate, args=(txt, tags), daemon=True).start()

    def _bg_decorate(self, t, tags):
        res = self.engine.decorate_lyrics_stage(t, tags)
        self.signals.finished_decorate.emit(res)

    def on_decorate_complete(self, txt):
        self.prog_bar.setRange(0, 100)
        self.txt_lyrics.setPlainText(txt)

    def log_system(self, msg):
        self.txt_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        self.status_lbl.setText(msg[:40] + "...")

    def refresh_vault(self):
        self.vault_list.clear()
        if not conf.OUTPUT_DIR.exists(): return
        files = list(conf.OUTPUT_DIR.glob("**/*.wav"))
        files.sort(key=os.path.getmtime, reverse=True)
        for f in files:
            i = QListWidgetItem(f.name)
            i.setData(Qt.ItemDataRole.UserRole, str(f))
            self.vault_list.addItem(i)

    def play_vault_item(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()
        try:
            j = Path(path).with_suffix(".json")
            if j.exists():
                with open(j) as f: d = json.load(j)
                self.waveform.generate_random_shape(d['configuration']['seed'])
        except:
            pass

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def update_position(self, pos):
        dur = self.player.duration()
        self.waveform.set_progress(pos, dur)
        self.lbl_time.setText(f"{pos // 1000}s / {dur // 1000}s")

    def update_duration(self, dur):
        self.update_position(self.player.position())

    def update_play_btn_icon(self, state):
        self.btn_play.setText("⏸" if state == QMediaPlayer.PlaybackState.PlayingState else "▶")

    def open_vault_folder(self):
        os.startfile(conf.OUTPUT_DIR) if sys.platform == "win32" else None

    def on_error(self, msg):
        self.prog_bar.setRange(0, 100)
        QMessageBox.critical(self, "Error", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Global Palette Fix for Dark Mode
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#050505"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#E4E4E7"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#09090B"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0D0D0F"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#E4E4E7"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#E4E4E7"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#E4E4E7"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#18181B"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#E4E4E7"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#00FF7F"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#00FF7F"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#00FF7F"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    app.setPalette(palette)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    win = OrphioStudio()
    win.show()
    sys.exit(app.exec())