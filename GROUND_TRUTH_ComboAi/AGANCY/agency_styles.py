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

# agency_styles.py
# THEME: CYBER GREEN & DARK NOIR

# agency_styles.py
# THEME: CYBER GREEN & DARK NOIR (Enhanced)

MODERN_STYLES = """
/* === 0. GLOBAL & WINDOW === */
QMainWindow, QDialog {
    background-color: #09090B;
    color: #E4E4E7;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QWidget {
    background-color: #09090B;
    color: #E4E4E7;
    font-size: 13px;
}
QFrame { border: none; }

/* === 1. TYPOGRAPHY === */
QLabel { color: #A1A1AA; background: transparent; }
QLabel#SectionHeader {
    color: #00FF7F;
    font-weight: 800;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 15px;
    margin-bottom: 5px;
    border-bottom: 2px solid #18181B;
    padding-bottom: 3px;
}
QLabel#StatLabel {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: bold;
}
QLabel#StatValue {
    color: #00FF7F;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}

/* === 2. INPUT FIELDS === */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {
    background-color: #121214;
    border: 1px solid #27272A;
    border-radius: 6px;
    padding: 10px;
    color: #FAFAFA;
    selection-background-color: #00FF7F;
    selection-color: #000000;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #00FF7F;
    background-color: #000000;
}
QLineEdit::placeholder, QTextEdit::placeholder {
    color: #52525B;
    font-style: italic;
}

/* === 3. BUTTONS === */
QPushButton {
    padding: 10px 15px;
    border-radius: 5px;
    font-weight: 600;
    border: 1px solid transparent;
}
QPushButton#PrimaryBtn {
    background-color: #00FF7F;
    color: #000000;
    font-weight: 900;
    text-transform: uppercase;
}
QPushButton#PrimaryBtn:hover {
    background-color: #22C55E;
    border: 1px solid #DCFCE7;
}
QPushButton#SecondaryBtn {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    color: #E4E4E7;
}
QPushButton#SecondaryBtn:hover {
    border-color: #00FF7F;
    color: #00FF7F;
    background-color: #121214;
}
QPushButton#IconBtn {
    background-color: transparent;
    color: #71717A;
    font-size: 16px;
}
QPushButton#IconBtn:hover { color: #00FF7F; }

/* === 4. LISTS & TABLES (The Vault) === */
QListWidget, QTableWidget {
    background-color: #050505;
    border: 1px solid #18181B;
    border-radius: 6px;
    outline: none;
}
QListWidget::item, QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #0D0D0F;
    color: #A1A1AA;
}
QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #18181B;
    color: #00FF7F;
    border-left: 3px solid #00FF7F;
}
QListWidget::item:hover {
    background-color: #0E0E11;
    color: #FFFFFF;
}

/* === 5. SCROLLBARS (Crucial for Dark Mode) === */
QScrollBar:vertical {
    background: #09090B;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #27272A;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover { background: #00FF7F; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

/* === 6. TABS === */
QTabWidget::pane { border: 1px solid #18181B; }
QTabBar::tab {
    background: #09090B;
    color: #71717A;
    padding: 8px 20px;
    border-bottom: 2px solid transparent;
    font-weight: bold;
    text-transform: uppercase;
}
QTabBar::tab:selected {
    color: #00FF7F;
    border-bottom: 2px solid #00FF7F;
}
QTabBar::tab:hover { color: #FFFFFF; }

/* === 7. SIDEBAR SPECIFIC === */
QFrame#Sidebar {
    background-color: #0C0C0E;
    border-right: 1px solid #18181B;
}
QFrame#Inspector {
    background-color: #0C0C0E;
    border-left: 1px solid #18181B;
}

/* === 8. PROGRESS BAR === */
QProgressBar {
    background-color: #18181B;
    border: none;
    height: 4px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #00FF7F;
    border-radius: 2px;
}

/* === 9. SLIDERS === */
QSlider::groove:horizontal {
    height: 4px;
    background: #27272A;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #00FF7F;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
"""