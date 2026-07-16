import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox,
    QVBoxLayout, QGridLayout, QGroupBox, QRadioButton, QPushButton, QHBoxLayout, QTabWidget, QSlider, QSpinBox, QDoubleSpinBox, QScrollArea, QProgressBar
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt


def fmt(value):
    value = float(value)
    if value.is_integer():
        return f"{int(value):,}"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


class StorageConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.partition_widgets = []  # Tracks dynamic RAM partitions
        self.is_updating = False     # Prevents recursion loops during value updates
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Silly little Ram Calc tool :3")
        self.setWindowIcon(QIcon("feather-red.png"))
        self.setFixedSize(450, 600)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        self.storage_tab = QWidget()
        self.ram_tab = QWidget()
        self.close_tab = QWidget()

        self.tabs.addTab(self.storage_tab, "Storage Converter")
        self.tabs.addTab(self.ram_tab, "RAM Planner")
        self.tabs.addTab(self.close_tab, "✖ Close")

        self.tabs.currentChanged.connect(self.handle_tab_change)

        layout.addWidget(self.tabs)

        self.build_storage_tab()
        self.build_ram_tab()
        
        self.dark_mode = True
        self.apply_theme()

    def handle_tab_change(self, index):
        if self.tabs.widget(index) == self.close_tab :
            QApplication.quit()
    
    def build_storage_tab(self):
        layout = QVBoxLayout(self.storage_tab)
        layout.setSpacing(12)

        title = QLabel("Storage Converter")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        input_layout = QHBoxLayout()
        
        self.value_edit = QLineEdit()
        self.value_edit.setPlaceholderText("Enter a value...")
        self.value_edit.textChanged.connect(self.convert)
        
        self.theme_button = QPushButton("☀")
        self.theme_button.setFixedWidth(40)
        self.theme_button.clicked.connect(self.toggle_theme)
        
        input_layout.addWidget(self.value_edit)
        input_layout.addWidget(self.theme_button)
        layout.addLayout(input_layout)

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
        rows = ["Bytes", "KB", "MB", "GB", "TB", "", "Breakdown"]

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

    def build_ram_tab(self):
        layout = QVBoxLayout(self.ram_tab)
        layout.setSpacing(10)

        # Config Header Area
        config_layout = QGridLayout()
        
        max_ram_label = QLabel("Max RAM (GB):")
        max_ram_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.max_ram = QDoubleSpinBox()
        self.max_ram.setRange(1.0, 1024.0)
        self.max_ram.setValue(64.0)
        self.max_ram.setSingleStep(4.0)
        self.max_ram.valueChanged.connect(self.on_max_ram_changed)

        parts_label = QLabel("Parts:")
        parts_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.parts = QSpinBox()
        self.parts.setRange(1, 128)
        self.parts.setValue(8)
        self.parts.valueChanged.connect(self.adjust_partition_count)

        config_layout.addWidget(max_ram_label, 0, 0)
        config_layout.addWidget(self.max_ram, 0, 1)
        config_layout.addWidget(parts_label, 1, 0)
        config_layout.addWidget(self.parts, 1, 1)
        
        layout.addLayout(config_layout)

        # Divider
        divider = QLabel("=" * 45)
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(divider)

        # Scrollable area for dynamic partitions
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # Bottom UI (Progress bar, Metrics & Action Buttons)
        bottom_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p%")
        bottom_layout.addWidget(self.progress_bar)

        metrics_layout = QHBoxLayout()
        self.used_label = QLabel("Used: 0.00 GB")
        self.used_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.remaining_label = QLabel("Remaining: 64.00 GB")
        self.remaining_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        metrics_layout.addWidget(self.used_label)
        metrics_layout.addWidget(self.remaining_label)
        bottom_layout.addLayout(metrics_layout)

        # Command Buttons
        btn_layout = QHBoxLayout()
        self.btn_split = QPushButton("Split Evenly")
        self.btn_split.clicked.connect(self.split_evenly)
        self.btn_reset = QPushButton("Reset All")
        self.btn_reset.clicked.connect(self.reset_all)
        btn_layout.addWidget(self.btn_split)
        btn_layout.addWidget(self.btn_reset)
        bottom_layout.addLayout(btn_layout)

        layout.addLayout(bottom_layout)

        # Initialize partitions
        self.adjust_partition_count()

    def adjust_partition_count(self):
        """Dynamically matches UI partition rows to the 'Parts' SpinBox value."""
        target_count = self.parts.value()
        current_count = len(self.partition_widgets)

        default_names = [
            "Minecraft Server", "Windows VM", "Docker", "NAS", 
            "Media Server", "Backup Pool", "Web Host", "Dev Sandbox"
        ]

        if current_count < target_count:
            # Add partitions
            for i in range(current_count, target_count):
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)

                # Editable Name
                name_text = default_names[i] if i < len(default_names) else f"Partition {i+1}"
                name_edit = QLineEdit(name_text)
                name_edit.setPlaceholderText("Name...")
                name_edit.setFixedWidth(120)

                # Slider (scaled by 100 for decimals)
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(int(self.max_ram.value() * 100))
                slider.setValue(0)
                
                # Value label
                val_label = QLabel("0.00 GB")
                val_label.setFixedWidth(65)
                val_label.setFont(QFont("Consolas", 9))
                val_label.setAlignment(Qt.AlignmentFlag.AlignRight)

                # Connect signals
                slider.valueChanged.connect(lambda v, s=slider, l=val_label: self.on_slider_moved(s, l))

                row_layout.addWidget(name_edit)
                row_layout.addWidget(slider)
                row_layout.addWidget(val_label)
                self.scroll_layout.addWidget(row_widget)

                self.partition_widgets.append({
                    "widget": row_widget,
                    "name_edit": name_edit,
                    "slider": slider,
                    "label": val_label
                })
        elif current_count > target_count:
            # Remove extra partitions
            for _ in range(current_count - target_count):
                item = self.partition_widgets.pop()
                self.scroll_layout.removeWidget(item["widget"])
                item["widget"].deleteLater()

        self.update_ram_metrics()

    def on_max_ram_changed(self):
        """Updates limits of existing sliders to align with the new Max RAM limit."""
        if self.is_updating:
            return
        max_val = self.max_ram.value()
        for item in self.partition_widgets:
            item["slider"].setMaximum(int(max_val * 100))
        self.update_ram_metrics()

    def on_slider_moved(self, active_slider, val_label):
        """Monitors slider movement and dynamically limits total usage to Max RAM."""
        if self.is_updating:
            return

        self.is_updating = True
        
        max_ram = self.max_ram.value()
        total_other_allocated = sum(
            item["slider"].value() / 100.0 
            for item in self.partition_widgets if item["slider"] is not active_slider
        )

        # Limit current slider to remaining headroom
        allowed_max = max_ram - total_other_allocated
        current_allocated = active_slider.value() / 100.0

        if current_allocated > allowed_max:
            active_slider.setValue(int(allowed_max * 100))
            current_allocated = allowed_max

        val_label.setText(f"{current_allocated:.2f} GB")
        
        self.is_updating = False
        self.update_ram_metrics()

    def update_ram_metrics(self):
        """Calculates total usage, remaining overhead, and updates the progress bar."""
        if self.is_updating:
            return

        total_max = self.max_ram.value()
        total_used = sum(item["slider"].value() / 100.0 for item in self.partition_widgets)
        remaining = max(0.0, total_max - total_used)

        self.used_label.setText(f"Used: {total_used:.2f} GB")
        self.remaining_label.setText(f"Remaining: {remaining:.2f} GB")

        # Update labels of all rows during broad resets/splits
        for item in self.partition_widgets:
            item["label"].setText(f"{(item['slider'].value() / 100.0):.2f} GB")

        percent = int((total_used / total_max) * 100) if total_max > 0 else 0
        self.progress_bar.setValue(percent)

    def split_evenly(self):
        """Evenly distributes the total Max RAM allocation among active partitions."""
        self.is_updating = True
        num_parts = len(self.partition_widgets)
        if num_parts == 0:
            self.is_updating = False
            return

        max_ram = self.max_ram.value()
        even_share = max_ram / num_parts
        slider_value = int(even_share * 100)

        for item in self.partition_widgets:
            item["slider"].setMaximum(int(max_ram * 100))
            item["slider"].setValue(slider_value)

        self.is_updating = False
        self.update_ram_metrics()

    def reset_all(self):
        """Resets all partition allocations to 0.00 GB."""
        self.is_updating = True
        for item in self.partition_widgets:
            item["slider"].setValue(0)
        self.is_updating = False
        self.update_ram_metrics()

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
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def apply_theme(self):
        if self.dark_mode:
            self.theme_button.setText("☀")
            self.setStyleSheet("""
                QWidget {
                    background: #2b2b2b;
                    color: white;
                }
                QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                    background: #3c3c3c;
                    color: white;
                    border: 1px solid #666;
                    padding: 4px;
                    border-radius: 4px;
                }
                QPushButton {
                    background: #444;
                    color: white;
                    border: 1px solid #666;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #555;
                }
                QGroupBox {
                    border: 1px solid #666;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                }
                QScrollArea {
                    border: 1px solid #555;
                    border-radius: 4px;
                }
                QProgressBar {
                    border: 1px solid #666;
                    border-radius: 4px;
                    text-align: center;
                    background: #3c3c3c;
                }
                QProgressBar::chunk {
                    background-color: #cc0505;
                    width: 10px;
                }
                QProgressBar::chunk {
                    background-color: #cc0505;
                    width: 10px;
                }

                QSlider::groove:horizontal {
                    height: 6px;
                    background: #444;
                    border: 1px solid #666;
                    border-radius: 3px;
                }
                QSlider::sub-page:horizontal {
                    background: #cc0505; 
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #eee;
                    border: 1px solid #777;
                    width: 14px;
                    height: 14px;
                    margin-top: -5px;
                    margin-bottom: -5px;
                    border-radius: 7px;
                }
            """)
        else:
            self.theme_button.setText("🌙")
            self.setStyleSheet("""
                QWidget {
                    background: white;
                    color: black;
                }
                QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox {
                    background: white;
                    color: black;
                    border: 1px solid #888;
                    padding: 4px;
                    border-radius: 4px;
                }
                QPushButton {
                    background: #e0e0e0;
                    color: black;
                    border: 1px solid #888;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background: #d0d0d0;
                }
                QGroupBox {
                    border: 1px solid #888;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                }
                QScrollArea {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
                QProgressBar {
                    border: 1px solid #bbb;
                    border-radius: 4px;
                    text-align: center;
                    background: #e0e0e0;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: #d70000;
                    width: 10px;
                }

                QProgressBar::chunk {
                    background-color: #d70000;
                    width: 10px;
                    color: white;
                }

                QSlider::groove:horizontal {
                    height: 6px;
                    background: #e0e0e0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    color: white;
                }
                QSlider::sub-page:horizontal {
                    background: #d70000;
                    border-radius: 3px;
                    color: white;
                }
                QSlider::handle:horizontal {
                    background: white;
                    border: 1px solid #aaa;
                    width: 14px;
                    height: 14px;
                    margin-top: -5px;
                    margin-bottom: -5px;
                    border-radius: 7px;
                    color: white;
                }
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StorageConverter()
    window.show()
    sys.exit(app.exec())