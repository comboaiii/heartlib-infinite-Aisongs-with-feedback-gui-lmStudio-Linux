import json
import sys
from pathlib import Path
from typing import List
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QScrollArea, QWidget,
    QCheckBox, QPushButton, QLineEdit, QGridLayout,
    QSizePolicy, QLabel, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt

# === COMPACT & PROFESSIONAL STYLESHEET ===
COMPACT_TAG_STYLES = """
/* MAIN DIALOG */
QDialog { 
    background-color: #0A0A0C; 
    color: #E4E4E7;
}

/* SEARCH BAR */
QLineEdit {
    background-color: #18181B;
    border: 1px solid #3F3F46;
    border-radius: 6px;
    padding: 10px 16px;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 500;
}
QLineEdit:focus { 
    border: 1px solid #00FF7F; 
}
QLineEdit::placeholder {
    color: #52525B;
    font-style: italic;
}

/* SCROLL AREA */
QScrollArea { 
    border: none; 
    background-color: transparent; 
}

/* CATEGORY HEADERS - MORE COMPACT */
QLabel#CategoryHeader {
    color: #00FF7F;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.5px;
    background-color: transparent;
    padding: 8px 0px 4px 0px;
    margin-top: 12px;
    border-bottom: 2px solid #27272A;
}

/* TAG CHECKBOXES - COMPACT TILES */
QCheckBox {
    color: #D4D4D8;
    background-color: #18181B;
    border: 1px solid #27272A;
    border-radius: 4px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 0px;
    height: 0px;
}

QCheckBox:hover {
    background-color: #27272A;
    color: #FFFFFF;
    border: 1px solid #52525B;
}

QCheckBox:checked {
    background-color: #00FF7F;
    color: #000000;
    border: 1px solid #00FF7F;
    font-weight: 700;
}

/* BUTTONS - COMPACT */
QPushButton#PrimaryBtn {
    background-color: #00FF7F;
    color: #000000;
    border: none;
    border-radius: 6px;
    font-weight: 900;
    font-size: 13px;
    padding: 12px;
    text-transform: uppercase;
}
QPushButton#PrimaryBtn:hover { 
    background-color: #00E672; 
}

QPushButton#SecondaryBtn {
    background-color: #27272A;
    color: #A1A1AA;
    border: 1px solid #3F3F46;
    border-radius: 4px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#SecondaryBtn:hover { 
    color: #FFFFFF; 
    background-color: #3F3F46;
}

/* FOOTER */
QFrame#Footer {
    background-color: #111113;
    border-top: 1px solid #27272A;
    padding: 12px;
}

QLabel#SelectionLabel {
    color: #71717A;
    font-size: 11px;
    padding: 8px;
    background-color: #18181B;
    border-radius: 4px;
    border-left: 2px solid #00FF7F;
}

/* SCROLLBAR - THIN */
QScrollBar:vertical {
    background: transparent; 
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #3F3F46; 
    min-height: 30px; 
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover { 
    background: #52525B; 
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { 
    height: 0px; 
}
"""


class TagSelectorDialog(QDialog):
    """Compact, professional tag library"""

    def __init__(self, current_tags_str="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tag Library")

        # MUCH SMALLER SIZE
        self.resize(1000, 700)
        self.setMinimumSize(900, 600)

        self.initially_selected = [t.strip().lower() for t in current_tags_str.split(",") if t.strip()]
        self.checkboxes = []
        self.category_widgets = []

        self.setStyleSheet(COMPACT_TAG_STYLES)
        self.init_ui()
        self.load_tags()

    def init_ui(self):
        """Initialize compact UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # COMPACT HEADER
        header = QHBoxLayout()

        title = QLabel("TAG LIBRARY")
        title.setStyleSheet("color: #00FF7F; font-weight: 900; font-size: 18px; letter-spacing: 2px;")
        header.addWidget(title)

        header.addStretch()

        btn_clear = QPushButton("Clear All")
        btn_clear.setObjectName("SecondaryBtn")
        btn_clear.clicked.connect(self.clear_all)
        header.addWidget(btn_clear)

        layout.addLayout(header)

        # COMPACT SEARCH
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter tags... (e.g. 'Dark', 'Pop', '95%')")
        self.search_input.textChanged.connect(self.filter_tags)
        layout.addWidget(self.search_input)

        # SCROLLABLE TAG AREA
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setSpacing(8)
        self.main_layout.setContentsMargins(0, 0, 10, 0)

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)

        # COMPACT FOOTER
        footer = QFrame()
        footer.setObjectName("Footer")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(10)

        self.selection_label = QLabel("No tags selected")
        self.selection_label.setObjectName("SelectionLabel")
        self.selection_label.setWordWrap(True)
        footer_layout.addWidget(self.selection_label)

        self.apply_btn = QPushButton("Apply Selection")
        self.apply_btn.setObjectName("PrimaryBtn")
        self.apply_btn.clicked.connect(self.accept)
        footer_layout.addWidget(self.apply_btn)

        layout.addWidget(footer)

    def load_tags(self):
        """Load tags from JSON"""
        path = Path(__file__).parent / "tags.json"
        if not path.exists():
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for cat_key in sorted(data.keys()):
                # Clean up category name
                clean_name = cat_key.split('_', 1)[-1].replace('_', ' ').upper()
                # Extract percentage if present
                if '%' in cat_key:
                    percentage = cat_key.split('_')[0].split()[-1]
                    clean_name = f"{clean_name} • {percentage}"

                self._create_category_block(clean_name, data[cat_key])

            self.main_layout.addStretch(1)
            self.update_ui_state()

        except Exception as e:
            print(f"Error loading tags: {e}")

    def _create_category_block(self, category_name: str, tags: List[str]):
        """Create compact category with tags"""
        cat_widget = QWidget()
        cat_layout = QVBoxLayout(cat_widget)
        cat_layout.setContentsMargins(0, 0, 0, 0)
        cat_layout.setSpacing(8)

        # Category header
        header = QLabel(category_name)
        header.setObjectName("CategoryHeader")
        cat_layout.addWidget(header)

        # Tag grid - MORE TAGS PER ROW (6 instead of 5)
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        cols = 6  # 6 tags per row for compact view

        for i, tag in enumerate(tags):
            cb = QCheckBox(tag)
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

            if tag.lower() in self.initially_selected:
                cb.setChecked(True)

            cb.stateChanged.connect(self.update_ui_state)
            cb.category = category_name
            cb.tag_text = tag.lower()

            self.checkboxes.append(cb)
            grid.addWidget(cb, i // cols, i % cols)

        cat_layout.addLayout(grid)

        self.main_layout.addWidget(cat_widget)
        self.category_widgets.append((cat_widget, category_name))

    def filter_tags(self, text: str):
        """Filter tags"""
        search = text.lower()

        if not search:
            for cb in self.checkboxes:
                cb.setVisible(True)
            for widget, _ in self.category_widgets:
                widget.setVisible(True)
            return

        # Filter
        for cb in self.checkboxes:
            matches = search in cb.tag_text or search in cb.category.lower()
            cb.setVisible(matches)

        # Hide empty categories
        for widget, name in self.category_widgets:
            visible = sum(1 for c in widget.findChildren(QCheckBox) if not c.isHidden())
            widget.setVisible(visible > 0)

    def update_ui_state(self):
        """Update selection display"""
        selected = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        count = len(selected)

        if count > 0:
            preview = ", ".join(selected[:8])
            if count > 8:
                preview += f" (+{count - 8} more)"
            self.selection_label.setText(f"Selected ({count}): {preview}")
            self.apply_btn.setText(f"Apply {count} Tags")
        else:
            self.selection_label.setText("No tags selected")
            self.apply_btn.setText("Apply Selection")

    def clear_all(self):
        """Clear all selections"""
        for cb in self.checkboxes:
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)
        self.update_ui_state()

    def get_selected_tags(self) -> List[str]:
        """Return selected tags"""
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]


def main():
    """Test dialog"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    dialog = TagSelectorDialog("Pop, Electronic, Dark")

    if dialog.exec():
        print(f"Selected: {', '.join(dialog.get_selected_tags())}")


if __name__ == "__main__":
    main()