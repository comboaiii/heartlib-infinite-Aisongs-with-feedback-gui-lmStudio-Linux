import sys
import json
import random
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QListWidget, QListWidgetItem, QPushButton,
                               QTextEdit, QLabel, QScrollArea, QFileDialog, QSlider,
                               QGridLayout, QFrame, QMessageBox, QLineEdit, QSplitter,
                               QTabWidget, QGroupBox, QDialog)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import Qt, QUrl, QTime
from PySide6.QtGui import QColor, QPainter, QBrush, QAction

# --- IMPORTS FROM YOUR PROJECT ---
try:
    from tagSelector import TagSelectorDialog
    from orphio_config import conf
except ImportError:
    # Fallback if run standalone without config context
    conf = None

# --- PATH SETUP ---
SCRIPT_DIR = Path(__file__).parent.absolute()
DEFAULT_VAULT_PATH = SCRIPT_DIR.parent / "outputSongs_ComboAi"
if not DEFAULT_VAULT_PATH.exists():
    DEFAULT_VAULT_PATH = SCRIPT_DIR

# --- STYLES ---
CORE_BLACK = "#0a0a0b"
PANEL_GRAY = "#161617"
BORDER_GRAY = "#2a2a2c"
ACCENT_GREEN = "#00ff7f"
ACCENT_AMBER = "#FF9F1A"
TEXT_DIM = "#88888e"
TEXT_BRIGHT = "#e1e1e6"

STYLE_SHEET = f"""
QMainWindow {{ background-color: {CORE_BLACK}; }}
QFrame#Sidebar {{ background-color: {CORE_BLACK}; border-right: 1px solid {BORDER_GRAY}; }}
QWidget {{ color: {TEXT_BRIGHT}; font-family: 'Segoe UI', sans-serif; }}
QGroupBox {{
    font-weight: bold; border: 1px solid {BORDER_GRAY}; margin-top: 20px; border-radius: 6px;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; }}
QPushButton#TagBtn {{
    background-color: {PANEL_GRAY}; border: 1px solid {BORDER_GRAY}; padding: 5px; border-radius: 4px;
}}
QPushButton#TagBtn:checked {{
    background-color: {ACCENT_AMBER}; color: black; border: 1px solid {ACCENT_AMBER};
}}
QSlider::groove:horizontal {{ height: 4px; background: {BORDER_GRAY}; }}
QSlider::handle:horizontal {{ background: {ACCENT_GREEN}; width: 14px; margin: -5px 0; border-radius: 7px; }}
"""

# Technical Audit Categories (Kept from your original)
TECHNICAL_SCHEMA = {
    "MIXING": ["Clear", "Muddy", "Wide", "Mono", "Loud", "Quiet"],
    "VOCALS": ["Clear", "Buried", "Robotic", "Natural", "Glitchy"],
    "STRUCTURE": ["Coherent", "Abrupt End", "Looping", "Evolving"]
}


class AdherenceSlider(QWidget):
    """Widget to judge how well a specific tag was adhered to."""

    def __init__(self, tag_name, score=0):
        super().__init__()
        self.tag_name = tag_name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lbl = QLabel(f"{tag_name.upper()}")
        self.lbl.setFixedWidth(120)
        self.lbl.setStyleSheet(f"font-weight:bold; color: {TEXT_DIM};")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 10)  # 0 to 10 score
        self.slider.setValue(score)

        self.score_lbl = QLabel(str(score))
        self.score_lbl.setFixedWidth(30)
        self.score_lbl.setStyleSheet(f"color: {ACCENT_GREEN}; font-weight:bold;")

        self.slider.valueChanged.connect(lambda v: self.score_lbl.setText(str(v)))

        layout.addWidget(self.lbl)
        layout.addWidget(self.slider)
        layout.addWidget(self.score_lbl)

    def get_score(self):
        return self.slider.value()


class WaveformDisplay(QWidget):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.setFixedHeight(80)
        self.bars = []
        self.pos_ratio = 0
        self.setStyleSheet(f"background: {PANEL_GRAY}; border-radius: 6px;")

    def set_seed(self, seed_val):
        random.seed(seed_val)
        self.bars = [random.uniform(0.2, 0.9) for _ in range(100)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Draw Bars
        if not self.bars: return
        bar_w = w / len(self.bars)

        for i, val in enumerate(self.bars):
            bar_h = val * h * 0.8
            x = i * bar_w
            y = (h - bar_h) / 2

            # Color logic based on playhead
            if (i / len(self.bars)) < self.pos_ratio:
                painter.setBrush(QBrush(QColor(ACCENT_GREEN)))
            else:
                painter.setBrush(QBrush(QColor("#333")))

            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), int(y), int(bar_w - 1), int(bar_h), 2, 2)

    def mousePressEvent(self, event):
        dur = self.player.duration()
        if dur > 0:
            pos = int((event.position().x() / self.width()) * dur)
            self.player.setPosition(pos)


class OrphioAuditorPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ORPHIO EVALUATOR PRO - Adherence & Feedback")
        self.resize(1400, 900)
        self.setStyleSheet(STYLE_SHEET)

        self.vault_path = DEFAULT_VAULT_PATH
        self.current_json_path = None
        self.adherence_widgets = []  # Stores slider widgets
        self.feedback_tags = []  # Stores strings of added tags
        self.tech_btns = {}  # Stores technical buttons

        # Audio
        self.player = QMediaPlayer()
        self.audio_out = QAudioOutput()
        self.player.setAudioOutput(self.audio_out)
        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)

        self.init_ui()
        self.scan_vault()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        splitter = QSplitter(Qt.Horizontal)

        # --- LEFT: FILE LIST ---
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(300)
        sb_layout = QVBoxLayout(sidebar)

        self.btn_load = QPushButton("📁 OPEN VAULT")
        self.btn_load.clicked.connect(self.open_vault)
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_song)
        self.lbl_stats = QLabel("0 / 0 Evaluated")

        sb_layout.addWidget(self.btn_load)
        sb_layout.addWidget(self.file_list)
        sb_layout.addWidget(self.lbl_stats)

        # --- RIGHT: WORKSPACE ---
        workspace = QWidget()
        ws_layout = QVBoxLayout(workspace)

        # Header
        self.lbl_title = QLabel("SELECT A TRACK")
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: 900; color: white;")
        ws_layout.addWidget(self.lbl_title)

        # Audio Controls
        self.wave_view = WaveformDisplay(self.player)
        ws_layout.addWidget(self.wave_view)

        ctrl_layout = QHBoxLayout()
        self.btn_play = QPushButton("▶ PLAY")
        self.btn_play.setFixedSize(100, 40)
        self.btn_play.setStyleSheet(f"background: {ACCENT_GREEN}; color: black; font-weight: bold;")
        self.btn_play.clicked.connect(self.toggle_play)
        self.lbl_time = QLabel("00:00 / 00:00")
        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.lbl_time)
        ctrl_layout.addStretch()
        ws_layout.addLayout(ctrl_layout)

        # --- EVALUATION ZONES (Split Vertical) ---
        eval_splitter = QSplitter(Qt.Vertical)

        # ZONE 1: ADHERENCE (Did we get what we asked for?)
        zone_adherence = QFrame()
        za_layout = QVBoxLayout(zone_adherence)
        za_layout.addWidget(
            QLabel("1. PROMPT ADHERENCE JUDGMENT", styleSheet=f"color:{ACCENT_AMBER}; font-weight:900;"))

        self.scroll_adherence = QScrollArea()
        self.scroll_adherence.setWidgetResizable(True)
        self.cont_adherence = QWidget()
        self.lyt_adherence = QVBoxLayout(self.cont_adherence)  # Will be populated dynamically
        self.scroll_adherence.setWidget(self.cont_adherence)
        za_layout.addWidget(self.scroll_adherence)

        # ZONE 2: FEEDBACK & DISCOVERY (What is it actually?)
        zone_feedback = QFrame()
        zf_layout = QVBoxLayout(zone_feedback)

        # Top half of Zone 2: Tag List
        h_tag_head = QHBoxLayout()
        h_tag_head.addWidget(
            QLabel("2. PERCEIVED TAGS (FEEDBACK)", styleSheet=f"color:{ACCENT_AMBER}; font-weight:900;"))
        btn_add_tag = QPushButton("+ ADD TAGS")
        btn_add_tag.setFixedSize(100, 25)
        btn_add_tag.setStyleSheet(f"background: {PANEL_GRAY}; border: 1px solid {ACCENT_AMBER}; color: {ACCENT_AMBER};")
        btn_add_tag.clicked.connect(self.open_tag_selector)
        h_tag_head.addWidget(btn_add_tag)
        zf_layout.addLayout(h_tag_head)

        self.txt_feedback_tags = QTextEdit()
        self.txt_feedback_tags.setPlaceholderText("Tags will appear here (e.g. 'Slow, Dark, Piano')...")
        self.txt_feedback_tags.setFixedHeight(60)
        self.txt_feedback_tags.setReadOnly(True)  # Read only because we use the dialog
        zf_layout.addWidget(self.txt_feedback_tags)

        # Bottom half of Zone 2: Technical Checkboxes
        zf_layout.addWidget(
            QLabel("3. TECHNICAL AUDIT", styleSheet=f"color:{ACCENT_AMBER}; font-weight:900; margin-top:10px;"))
        self.tech_grid = QGridLayout()
        row = 0
        for cat, opts in TECHNICAL_SCHEMA.items():
            self.tech_grid.addWidget(QLabel(cat, styleSheet="color:#555; font-weight:bold;"), row, 0)
            col = 1
            self.tech_btns[cat] = []
            for opt in opts:
                btn = QPushButton(opt)
                btn.setCheckable(True)
                btn.setObjectName("TagBtn")
                btn.setFixedHeight(25)
                self.tech_grid.addWidget(btn, row, col)
                self.tech_btns[cat].append(btn)
                col += 1
                if col > 5:
                    col = 1;
                    row += 1
            row += 1

        tech_widget = QWidget()
        tech_widget.setLayout(self.tech_grid)
        zf_layout.addWidget(tech_widget)

        # Add zones to splitter
        eval_splitter.addWidget(zone_adherence)
        eval_splitter.addWidget(zone_feedback)
        ws_layout.addWidget(eval_splitter)

        # --- FOOTER: COMMIT ---
        footer = QFrame()
        f_layout = QHBoxLayout(footer)
        self.lbl_overall = QLabel("OVERALL SCORE: 5")
        self.slider_overall = QSlider(Qt.Horizontal)
        self.slider_overall.setRange(1, 10)
        self.slider_overall.setValue(5)
        self.slider_overall.valueChanged.connect(lambda v: self.lbl_overall.setText(f"OVERALL SCORE: {v}"))

        self.btn_commit = QPushButton("✅ SAVE EVALUATION")
        self.btn_commit.setFixedSize(150, 40)
        self.btn_commit.setStyleSheet(f"background: {TEXT_BRIGHT}; color: black; font-weight: 900;")
        self.btn_commit.clicked.connect(self.save_evaluation)

        f_layout.addWidget(self.lbl_overall)
        f_layout.addWidget(self.slider_overall)
        f_layout.addWidget(self.btn_commit)
        ws_layout.addWidget(footer)

        splitter.addWidget(sidebar)
        splitter.addWidget(workspace)
        main_layout.addWidget(splitter)

    # --- LOGIC ---

    def scan_vault(self):
        self.file_list.clear()
        if not self.vault_path.exists(): return

        files = sorted(list(self.vault_path.glob("*.json")), key=lambda f: f.stat().st_mtime, reverse=True)
        evaluated_count = 0

        for f in files:
            try:
                with open(f, 'r', encoding='utf-8') as jf:
                    data = json.load(jf)

                status = data.get('human_evaluation', {}).get('status', 'PENDING')
                title = data.get('provenance', {}).get('title', f.stem)

                icon = "🟢" if status == "VALIDATED" else "⚪"
                if status == "VALIDATED": evaluated_count += 1

                item = QListWidgetItem(f"{icon} {title}")
                item.setData(Qt.UserRole, str(f))
                self.file_list.addItem(item)
            except:
                pass

        self.lbl_stats.setText(f"{evaluated_count} / {len(files)} Evaluated")

    def load_song(self, item):
        json_path = Path(item.data(Qt.UserRole))
        self.current_json_path = json_path
        wav_path = json_path.with_suffix(".wav")

        # Reset UI
        for i in reversed(range(self.lyt_adherence.count())):
            self.lyt_adherence.itemAt(i).widget().setParent(None)
        self.adherence_widgets.clear()
        self.feedback_tags = []
        self.txt_feedback_tags.clear()

        # Load Data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Setup Audio
        if wav_path.exists():
            self.player.setSource(QUrl.fromLocalFile(str(wav_path)))
            self.lbl_title.setText(data.get('provenance', {}).get('title', wav_path.stem))
            seed = data.get('configuration', {}).get('seed', 0)
            self.wave_view.set_seed(seed)
        else:
            self.lbl_title.setText("AUDIO FILE MISSING")

        # 2. Populate Adherence (Judgment)
        prompt_tags = data.get('configuration', {}).get('input_prompt', {}).get('tags', [])
        # Check if we already have scores
        saved_adh = data.get('human_evaluation', {}).get('prompt_adherence_scores', {})

        for tag in prompt_tags:
            # Default score 5 if not evaluated, or load saved score
            score = saved_adh.get(tag, 5)
            widget = AdherenceSlider(tag, score)
            self.lyt_adherence.addWidget(widget)
            self.adherence_widgets.append(widget)

        # 3. Populate Feedback (Discovery)
        saved_perceived = data.get('human_evaluation', {}).get('perceived_tags', [])
        self.feedback_tags = saved_perceived
        self.txt_feedback_tags.setText(", ".join(self.feedback_tags))

        # 4. Populate Technical & Overall
        saved_eval = data.get('human_evaluation', {})
        self.slider_overall.setValue(saved_eval.get('overall_score', 5))

        saved_tech = saved_eval.get('technical_audit_scores', {})
        for cat, btns in self.tech_btns.items():
            for btn in btns:
                # Check based on text
                val = saved_tech.get(btn.text(), 0)
                btn.setChecked(val == 1)

    def open_tag_selector(self):
        """Opens the Dialog to select feedback tags from tags.json"""
        current_str = ", ".join(self.feedback_tags)

        # Use the class from tagSelector.py
        dlg = TagSelectorDialog(current_str, self)
        if dlg.exec():
            # Get list of strings
            new_tags = dlg.get_selected_tags()
            self.feedback_tags = new_tags
            self.txt_feedback_tags.setText(", ".join(new_tags))

    def save_evaluation(self):
        if not self.current_json_path: return

        with open(self.current_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Gather Adherence Scores
        adh_scores = {w.tag_name: w.get_score() for w in self.adherence_widgets}

        # 2. Gather Technical Scores
        tech_scores = {}
        for cat, btns in self.tech_btns.items():
            for btn in btns:
                if btn.isChecked():
                    tech_scores[btn.text()] = 1

        # 3. Update JSON Structure
        data['human_evaluation'] = {
            "status": "VALIDATED",
            "overall_score": self.slider_overall.value(),
            "timestamp": datetime.now().isoformat(),

            # THE TWO NEW WAYS YOU REQUESTED:
            "prompt_adherence_scores": adh_scores,  # Judgement
            "perceived_tags": self.feedback_tags,  # Feedback/Discovery

            "technical_audit_scores": tech_scores
        }

        with open(self.current_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        self.scan_vault()
        QMessageBox.information(self, "Success", "Evaluation Saved!")

    # --- AUDIO HELPERS ---
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause();
            self.btn_play.setText("▶")
        else:
            self.player.play();
            self.btn_play.setText("⏸")

    def on_position_changed(self, pos):
        dur = self.player.duration()
        if dur > 0:
            self.wave_view.pos_ratio = pos / dur
            self.wave_view.update()

            cur_min = (pos // 1000) // 60
            cur_sec = (pos // 1000) % 60
            tot_min = (dur // 1000) // 60
            tot_sec = (dur // 1000) % 60
            self.lbl_time.setText(f"{cur_min:02}:{cur_sec:02} / {tot_min:02}:{tot_sec:02}")

    def on_duration_changed(self, dur):
        pass

    def open_vault(self):
        path = QFileDialog.getExistingDirectory(self, "Select Vault", str(self.vault_path))
        if path:
            self.vault_path = Path(path)
            self.scan_vault()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OrphioAuditorPro()
    win.show()
    sys.exit(app.exec())