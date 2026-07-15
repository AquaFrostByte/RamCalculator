import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QGridLayout, QGroupBox, QRadioButton
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


def fmt(value):
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


class StorageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Storage Converter")
        self.setFixedSize(430, 430)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Storage Converter")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Enter a value...")
        self.value_edit.textChanged.connect(self.convert)
        layout.addWidget(self.value_edit)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["TB", "GB", "MB", "KB", "Bytes"])
        self.unit_combo.setCurrentIndex(1)
        self.unit_combo.currentIndexChanged.connect(self.convert)
        layout.addWidget(self.unit_combo)

        group = QGroupBox("Conversion Base")
        group_layout = QVBoxLayout()

        self.binary = QRadioButton("Binary (1024)")
        self.binary.setChecked(True)

        self.decimal = QRadioButton("Decimal (1000)")

        self.binary.toggled.connect(self.convert)
        self.decimal.toggled.connect(self.convert)

        group_layout.addWidget(self.binary)
        group_layout.addWidget(self.decimal)
        group.setLayout(group_layout)

        layout.addWidget(group)

        grid = QGridLayout()

        self.labels = {}

        rows = [
            "Bytes",
            "KB",
            "MB",
            "GB",
            "TB",
            "",
            "Breakdown"
        ]

        row = 0

        for item in rows:
            if item == "":
                row += 1
                continue

            name = QLabel(item)
            name.setFont(QFont("Arial", 10, QFont.Weight.Bold))

            value = QLabel("-")
            value.setAlignment(Qt.AlignmentFlag.AlignRight)
            value.setFont(QFont("Consolas", 10))

            grid.addWidget(name, row, 0)
            grid.addWidget(value, row, 1)

            self.labels[item] = value
            row += 1

        layout.addLayout(grid)

    def convert(self):
        text = self.value_edit.text().strip()

        if not text:
            for lbl in self.labels.values():
                lbl.setText("-")
            return

        try:
            value = float(text)
        except ValueError:
            return

        base = 1024 if self.binary.isChecked() else 1000

        unit = self.unit_combo.currentText()

        factors = {
            "Bytes": 1,
            "KB": base,
            "MB": base ** 2,
            "GB": base ** 3,
            "TB": base ** 4
        }

        total_bytes = int(value * factors[unit])

        self.labels["Bytes"].setText(f"{total_bytes:,}")

        self.labels["KB"].setText(fmt(total_bytes / base))
        self.labels["MB"].setText(fmt(total_bytes / (base**2)))
        self.labels["GB"].setText(fmt(total_bytes / (base**3)))
        self.labels["TB"].setText(fmt(total_bytes / (base**4)))

        remaining = total_bytes

        tb = remaining // (base**4)
        remaining %= (base**4)

        gb = remaining // (base**3)
        remaining %= (base**3)

        mb = remaining // (base**2)
        remaining %= (base**2)

        kb = remaining // base
        b = remaining % base

        self.labels["Breakdown"].setText(
            f"{tb:,} TB\n"
            f"{gb:,} GB\n"
            f"{mb:,} MB\n"
            f"{kb:,} KB\n"
            f"{b:,} B"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = StorageConverter()
    window.show()

    sys.exit(app.exec())