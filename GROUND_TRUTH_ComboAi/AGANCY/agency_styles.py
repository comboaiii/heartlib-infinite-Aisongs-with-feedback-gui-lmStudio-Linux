# agency_styles.py

MODERN_STYLES = """
/* 0. GLOBAL RESET & LINUX FIXES */
* {
    selection-background-color: #FF9F1A !important;
    selection-color: #000000 !important;
    outline: none;
}

QMainWindow, QDialog, QFrame, QAbstractScrollArea {
    background-color: #09090B !important;
    color: #E4E4E7 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* 1. SECTION HEADERS */
QLabel#SectionHeader {
    color: #71717A !important;
    font-weight: 800;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 15px;
    margin-bottom: 5px;
}

/* 2. MAIN INPUT AREAS */
QPlainTextEdit#TopicInput, QTextEdit, QLineEdit {
    background-color: #050505 !important;
    border: 1px solid #27272A !important;
    border-radius: 6px;
    padding: 10px;
    color: #FFFFFF !important;
}
QPlainTextEdit#TopicInput:focus, QTextEdit:focus, QLineEdit:focus {
    border: 1px solid #FF9F1A !important;
}

/* Specific styling for the Live Tags field to make it "Active" */
QLineEdit#LiveTags {
    color: #FF9F1A !important;
    font-weight: bold;
    background-color: #0D0D0F !important;
    border: 1px solid #3F3F46 !important;
}

/* 3. SIDEBAR & SPLITTERS */
QFrame#Sidebar {
    background-color: #0D0D0F !important;
    border-right: 1px solid #18181B !important;
}

QSplitter::handle {
    background-color: #18181B;
}
QSplitter::handle:horizontal { width: 1px; }
QSplitter::handle:vertical { height: 1px; }

/* 4. THE TAG LIBRARY TILES (High-End Badge Look) */
QCheckBox#TagTile {
    color: #A1A1AA !important;
    background-color: #121214 !important;
    border: 1px solid #27272A !important;
    border-radius: 4px;
    padding: 12px 5px;
    font-weight: bold;
}
QCheckBox#TagTile::indicator { width: 0px; height: 0px; } /* Hide checkbox square */

QCheckBox#TagTile:hover {
    background-color: #1C1C1F !important;
    border: 1px solid #3F3F46 !important;
    color: #FFFFFF !important;
}
QCheckBox#TagTile:checked {
    background-color: #FF9F1A !important;
    color: #000000 !important;
    border: 1px solid #FFB020 !important;
}

/* 5. BUTTONS */
QPushButton#PrimaryBtn {
    background-color: #FF9F1A !important;
    color: #000000 !important;
    font-weight: 900;
    border-radius: 4px;
    padding: 14px;
    text-transform: uppercase;
}
QPushButton#PrimaryBtn:hover { background-color: #FFB020 !important; }

QPushButton#SecondaryBtn {
    background-color: #18181B !important;
    border: 1px solid #3F3F46 !important;
    color: #E4E4E7 !important;
    font-weight: bold;
}
QPushButton#SecondaryBtn:hover { border: 1px solid #FF9F1A !important; color: #FF9F1A !important; }

QPushButton#FolderBtn {
    background-color: transparent !important;
    border: 1px solid #27272A !important;
    color: #FF9F1A !important;
    font-size: 16px;
}
QPushButton#FolderBtn:hover { background-color: #FF9F1A !important; color: #000000 !important; }

/* 6. VAULT & LISTS */
QListWidget {
    background-color: #050505 !important;
    border: 1px solid #18181B !important;
    border-radius: 6px;
}
QListWidget::item {
    padding: 10px;
    border-bottom: 1px solid #0D0D0F !important;
}
QListWidget::item:selected {
    background-color: #18181B !important;
    color: #FF9F1A !important;
    border-left: 3px solid #FF9F1A !important;
}

/* 7. PRO-AUDIO SLIDERS */
QSlider::groove:horizontal {
    height: 4px;
    background: #18181B;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #FF9F1A;
    border: 2px solid #09090B;
    width: 16px; height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

/* 8. INSPECTOR GRID LABELS */
QLabel#SpecLabel {
    color: #00FF7F !important;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 11px;
    background: #121214;
    padding: 5px;
    border-radius: 3px;
}

/* 9. SCROLLBARS */
QScrollBar:vertical {
    background: #09090B !important;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #27272A !important;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }

/* 10. CRITICAL VIEWPORT FIX */
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: #09090B !important;
    border: none !important;
}
"""