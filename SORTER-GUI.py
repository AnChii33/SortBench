import sys
import os
import csv
import datetime
import importlib.util
import random
import threading
import queue
from timeit import default_timer

# Suppress console window and set up environment
os.environ["QT_API"] = "PyQt6"

# Hide console window on Windows
if sys.platform == "win32":
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

sys.setrecursionlimit(10**8)

import xlsxwriter

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTabWidget, QGroupBox, QCheckBox, QPushButton, QLineEdit, 
    QTextEdit, QScrollArea, QLabel, QFileDialog, QMessageBox, QSplitter, 
    QScrollBar, QComboBox, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QDialog
)
from PyQt6.QtCore import Qt, QTimer, QThread
from PyQt6.QtGui import QFont, QPainter, QColor, QIcon

class FileViewerDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"View File: {os.path.basename(file_path)}")
        self.setGeometry(200, 200, 800, 570)  # Reduced height from 600 to 570
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        
        # Use custom EmojiScrollBar for consistency
        scroll_bar = EmojiScrollBar(Qt.Orientation.Vertical)
        self.text_edit.setVerticalScrollBar(scroll_bar)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setPlainText(content)
        except Exception as e:
            self.text_edit.setPlainText(f"Error reading file: {str(e)}")
        
        layout.addWidget(self.text_edit)

class DatasetInfoDialog(QDialog):
    def __init__(self, dataset_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dataset Statistics")
        self.setGeometry(300, 300, 280, 150)  # Reduced height from 180 to 150
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setPlainText(dataset_info)
        
        # Use custom EmojiScrollBar for consistency
        scroll_bar = EmojiScrollBar(Qt.Orientation.Vertical)
        self.text_edit.setVerticalScrollBar(scroll_bar)
        
        layout.addWidget(self.text_edit)

class DatasetInfoTooltip(QPushButton):
    def __init__(self, dataset_file, dataset_path=None, parent=None):
        super().__init__("View Details", parent)
        self.dataset_file = dataset_file
        self.dataset_path = dataset_path  # For custom datasets
        self.setFixedSize(55, 28)  # Increased height from 22 to 28
        self.clicked.connect(self.show_dataset_info)
    
    def show_dataset_info(self):
        try:
            if self.dataset_path:
                # Custom dataset - use absolute path
                file_path = self.dataset_path
            else:
                # Default dataset - use resource path
                file_path = resource_path(f"DATASETS/{self.dataset_file}")
            
            if not os.path.exists(file_path):
                QMessageBox.warning(self, "File Not Found", f"Dataset file not found: {self.dataset_file}")
                return
            
            # Use the same readtolist function as used in the main application
            vals = []
            try:
                with open(file_path, "r") as f:
                    while True:
                        line = f.readline()
                        if not line:
                             break
                        num = [int(float(s)) if float(s).is_integer() else float(s) for s in line.split()]
                        vals.extend(num)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error reading dataset: {str(e)}")
                return
            
            if not vals:
                QMessageBox.information(self, "Dataset Info", f"No valid numeric data found in {self.dataset_file}")
                return
            
            length = len(vals)
            max_val = max(vals) if vals else 0
            min_val = min(vals) if vals else 0
            unique_count = len(set(vals))
            unsorted_elements = SortingBenchmarkGUI.sortvarchk(self, vals)
            
            info_text = f"""Dataset: {self.dataset_file}
Total Elements: {length:,}
Maximum Value: {max_val:,}
Minimum Value: {min_val:,}
Unique Elements: {unique_count:,}
Unsorted Elements: {unsorted_elements:,}"""
            
            dialog = DatasetInfoDialog(info_text, self)
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error analyzing dataset: {str(e)}")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class EmojiCheckBox(QCheckBox):
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setFont(QFont("Segoe UI Emoji", 12))
            painter.setPen(QColor("#000000"))
            painter.drawText(3, 15, "✔️")


class EmojiScrollBar(QScrollBar):
    
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None):
        super().__init__(orientation, parent)
        self.is_dark_theme = False
        self.apply_style()
    
    def set_theme(self, is_dark):
        self.is_dark_theme = is_dark
        self.apply_style()
        self.update()
    
    def apply_style(self):
        """Apply theme-specific styling to the scrollbar"""
        if self.is_dark_theme:
            style = """
            QScrollBar:vertical {
                background-color: #404040;
                width: 16px;
                margin: 0px;
                border: 1px solid #555555;
            }
            QScrollBar::handle:vertical {
                background-color: #666666;
                min-height: 20px;
                margin: 20px 2px 20px 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #888888;
            }
            QScrollBar::add-line:vertical {
                height: 16px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border: 1px solid #555555;
                background-color: #555555;
            }
            QScrollBar::sub-line:vertical {
                height: 16px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border: 1px solid #555555;
                background-color: #555555;
            }
            QScrollBar::add-line:vertical:hover,
            QScrollBar::sub-line:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """
        else:
            style = """
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 16px;
                margin: 0px;
                border: 1px solid #cccccc;
            }
            QScrollBar::handle:vertical {
                background-color: #cccccc;
                min-height: 20px;
                margin: 20px 2px 20px 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #999999;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #777777;
            }
            QScrollBar::add-line:vertical {
                height: 16px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border: 1px solid #aaaaaa;
                background-color: #e8e8e8;
            }
            QScrollBar::sub-line:vertical {
                height: 16px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border: 1px solid #aaaaaa;
                background-color: #e8e8e8;
            }
            QScrollBar::add-line:vertical:hover,
            QScrollBar::sub-line:vertical:hover {
                background-color: #d0d0d0;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """
        
        self.setStyleSheet(style)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.orientation() == Qt.Orientation.Vertical:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Use better contrast colors for arrows
            if self.is_dark_theme:
                arrow_color = "#ffffff"
            else:
                arrow_color = "#333333"
                
            painter.setFont(QFont("Segoe UI Emoji", 9))
            painter.setPen(QColor(arrow_color))
            
            rect = self.rect()
            button_height = 16
            up_rect = rect.adjusted(0, 0, 0, -(rect.height() - button_height))
            down_rect = rect.adjusted(0, rect.height() - button_height, 0, 0)
            
            painter.drawText(up_rect, Qt.AlignmentFlag.AlignCenter, "▲")
            painter.drawText(down_rect, Qt.AlignmentFlag.AlignCenter, "▼")

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=12, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

class RemovalDialog(QDialog):
    def __init__(self, parent, title, items_to_remove, item_type="algorithm"):
        super().__init__(parent)
        self.parent = parent
        self.item_type = item_type
        self.items_to_remove = items_to_remove
        self.selected_items = {}
        
        self.setWindowTitle(title)
        self.setGeometry(300, 300, 600, 400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header with selection controls
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"Select {item_type}s to remove:"))
        header_layout.addStretch()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(lambda: self.select_all_items(True))
        header_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(lambda: self.select_all_items(False))
        header_layout.addWidget(select_none_btn)
        
        self.count_label = QLabel("")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Scroll area with items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(250)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.custom_scrollbar = EmojiScrollBar(Qt.Orientation.Vertical)
        scroll.setVerticalScrollBar(self.custom_scrollbar)
        
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        scroll.setWidget(self.scroll_widget)
        
        layout.addWidget(scroll)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        remove_btn = QPushButton(f"Remove Selected {item_type.title()}s")
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.populate_items()
        self.update_count()
    
    def populate_items(self):
        for name, data in self.items_to_remove.items():
            checkbox = EmojiCheckBox(name)
            checkbox.setChecked(False)
            
            container = QWidget()
            container.setMinimumHeight(35)
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(checkbox)
            
            if self.item_type == "algorithm":
                context_label = QLabel(f"({data['func']} from {os.path.basename(data['file'])})")
                context_label.setObjectName("context_label")
                container_layout.addWidget(context_label)
            
            container_layout.addStretch()
            
            if self.item_type == "algorithm":
                view_btn = QPushButton("View File")
                view_btn.setFixedSize(50, 28)
                view_btn.setToolTip(f"View {os.path.basename(data['file'])}")
                view_btn.clicked.connect(lambda checked, f=data['file']: self.parent.view_algorithm_file(f))
                container_layout.addWidget(view_btn)
            else:  # dataset
                info_tooltip = DatasetInfoTooltip(data['file'], data.get('path'))
                container_layout.addWidget(info_tooltip)
            
            self.selected_items[name] = checkbox
            checkbox.stateChanged.connect(self.update_count)
            
            self.scroll_layout.addWidget(container)
        
        self.scroll_layout.addStretch()
    
    def select_all_items(self, select_all=True):
        for checkbox in self.selected_items.values():
            checkbox.setChecked(select_all)
        self.update_count()
    
    def update_count(self):
        selected = sum(1 for checkbox in self.selected_items.values() if checkbox.isChecked())
        total = len(self.selected_items)
        self.count_label.setText(f"{selected}/{total} selected")
    
    def remove_selected(self):
        to_remove = [name for name, checkbox in self.selected_items.items() if checkbox.isChecked()]
        
        if not to_remove:
            QMessageBox.information(self, "No Selection", f"No {self.item_type}s selected for removal.")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Are you sure you want to remove {len(to_remove)} selected custom {self.item_type}(s)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.item_type == "algorithm":
                self.parent._remove_algorithms(to_remove)
            else:
                self.parent._remove_datasets(to_remove)
            
            QMessageBox.information(self, "Removal Complete", f"Removed {len(to_remove)} custom {self.item_type}(s).")
            self.accept()

class SortingBenchmarkGUI(QMainWindow):
    
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_variables()
        self._init_data()
        self.setup_gui()
        self.setup_output_monitoring()
    
    def _init_window(self):
        self.setWindowTitle("SortBench - Sorting Benchmark Tool")
        self.setGeometry(100, 100, 1400, 700)
        self.setMinimumSize(1400, 700)
    
    def _init_variables(self):
        self.MAXTIME = 300
        self.output_queue = queue.Queue()
        self.is_running = False
        self.execution_stopped = False
        self.logging_active = True
        self.current_thread = None
        self.is_dark_theme = False
        self.algo_vars = {}
        self.dataset_vars = {}
        self.state_vars = {}
        
        self.chart_data = {}
        self.benchmarking_completed = False
        
        self.selected_dataset_files = []
    
    def _init_data(self):
        self.default_sorts = [
            ("COUNT SORT", "countSort", "countSort.py"),
            ("RADIX SORT", "radixSort", "radixsort.py"),
            ("HEAP SORT", "heapSort", "heapsort.py"),
            ("TIM SORT", "timSort", "timsort.py"),
            ("MERGE SORT", "mergeSort", "mergesort_n.py"),
            ("QUICK SORT", "quicksort", "quicksort_n.py"),
            ("INSERTION SORT", "insertionsort", "insertionSort.py"),
            ("SELECTION SORT", "selectionSort", "selectionsort.py"),
            ("BUBBLE SORT", "bubbleSort", "bubble_Sort.py"),
        ]
        
        self.default_datasets = [
            ("chess.txt", "Standard Dataset 1 (334 KB)"),
            ("mushroom.txt", "Standard Dataset 2 (557 KB)"),
            ("T10I4D100K.txt", "Standard Dataset 3 (3.7 MB)"),
            ("pumsb_star.txt", "Standard Dataset 5 (10.7 MB)"),
            ("connect.txt", "Standard Dataset 4 (8.8 MB)"),
            ("pumsb.txt", "Standard Dataset 7 (15.9 MB)"),
            ("T40I10D100K.txt", "Standard Dataset 6 (14.6 MB)"),
        ]
        
        self.test_states = [
            "ORIGINAL", "RANDOM", "NEARLY SORTED", "SORTED", "REVERSE SORTED"
        ]
        
    def setup_gui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        config_widget = QWidget()
        exec_widget = QWidget()
        charts_widget = QWidget()
        tables_widget = QWidget()
        self.tab_widget.addTab(config_widget, "Configuration")
        self.tab_widget.addTab(exec_widget, "Execution")
        self.tab_widget.addTab(charts_widget, "Charts")
        self.tab_widget.addTab(tables_widget, "Tables")
        
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        
        self.setup_config_tab(config_widget)
        self.setup_execution_tab(exec_widget)
        self.setup_charts_tab(charts_widget)
        self.setup_tables_tab(tables_widget)
        
        self._create_theme_switcher(main_layout)
        
        self.apply_theme()
    
    def _create_theme_switcher(self, parent_layout):
        theme_layout = QHBoxLayout()
        
        # Add About and Help buttons at the left
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.show_about_dialog)
        self.about_button.setMaximumWidth(80)
        theme_layout.addWidget(self.about_button)
        
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help_dialog)
        self.help_button.setMaximumWidth(80)
        theme_layout.addWidget(self.help_button)
        
        theme_layout.addStretch()
        
        self.start_button = QPushButton("Start Benchmarking")
        self.start_button.clicked.connect(self.start_benchmarking)
        theme_layout.addWidget(self.start_button)
        
        self.theme_button = QPushButton("🌙 Dark Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.theme_button.setMaximumWidth(200)
        theme_layout.addWidget(self.theme_button)
        
        parent_layout.addLayout(theme_layout)
        
    def setup_config_tab(self, parent):
        main_layout = QVBoxLayout(parent)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        algo_group = self._create_algorithm_section()
        left_layout.addWidget(algo_group)
        
        main_splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        dataset_group = self._create_datasets_section()
        right_layout.addWidget(dataset_group)
        
        main_splitter.addWidget(right_widget)
        
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
    
    def _create_algorithm_section(self):
        algo_group = QGroupBox("Sorting Algorithms")
        algo_layout = QVBoxLayout(algo_group)
        
        self.algo_vars = {}

        algo_header_layout = QHBoxLayout()
        algo_header_layout.addWidget(QLabel("Select Algorithms:"))
        algo_header_layout.addStretch()
        
        select_all_algo_btn = QPushButton("Select All")
        select_all_algo_btn.clicked.connect(lambda: self.select_all_algorithms(True))
        algo_header_layout.addWidget(select_all_algo_btn)
        
        select_none_algo_btn = QPushButton("Select None")
        select_none_algo_btn.clicked.connect(lambda: self.select_all_algorithms(False))
        algo_header_layout.addWidget(select_none_algo_btn)
        
        self.algo_count_label = QLabel("")
        algo_header_layout.addWidget(self.algo_count_label)
        
        algo_layout.addLayout(algo_header_layout)
        
        algo_scroll = QScrollArea()
        algo_scroll.setWidgetResizable(True)
        algo_scroll.setMaximumHeight(250)
        algo_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        algo_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.algo_custom_scrollbar = EmojiScrollBar(Qt.Orientation.Vertical)
        algo_scroll.setVerticalScrollBar(self.algo_custom_scrollbar)
        
        self.algo_scroll_widget = QWidget()
        self.algo_scroll_layout = QVBoxLayout(self.algo_scroll_widget)
        algo_scroll.setWidget(self.algo_scroll_widget)
        
        algo_layout.addWidget(algo_scroll)
        
        self.populate_algorithms()
        
        custom_algo_group = self._create_custom_algorithm_section()
        algo_layout.addWidget(custom_algo_group)
        
        settings_group = self._create_settings_section()
        algo_layout.addWidget(settings_group)
        
        return algo_group
    
    def _create_custom_algorithm_section(self):
        custom_algo_group = QGroupBox("Add/Remove Custom Algorithms")
        custom_algo_layout = QVBoxLayout(custom_algo_group)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.custom_name_input = QLineEdit()
        name_layout.addWidget(self.custom_name_input)
        custom_algo_layout.addLayout(name_layout)
        
        func_file_layout = QHBoxLayout()
        func_file_layout.addWidget(QLabel("Function:"))
        self.custom_func_input = QLineEdit()
        func_file_layout.addWidget(self.custom_func_input)
        
        func_file_layout.addWidget(QLabel("File:"))
        self.custom_file_input = QLineEdit()
        self.custom_file_input.textChanged.connect(self.update_view_file_button)
        func_file_layout.addWidget(self.custom_file_input)
        
        browse_file_btn = QPushButton("Browse")
        browse_file_btn.clicked.connect(self.browse_custom_file)
        func_file_layout.addWidget(browse_file_btn)
        
        custom_algo_layout.addLayout(func_file_layout)
        
        # Create layout for Add Algorithm, Remove Custom Algorithms, and View File buttons
        button_layout = QHBoxLayout()
        add_algo_btn = QPushButton("Add Algorithm")
        add_algo_btn.clicked.connect(self.add_custom_algorithm)
        button_layout.addWidget(add_algo_btn)
        
        remove_custom_btn = QPushButton("Remove Custom Algorithms")
        remove_custom_btn.clicked.connect(self.open_algorithm_removal_dialog)
        button_layout.addWidget(remove_custom_btn)
        
        view_file_btn = QPushButton("View File")
        view_file_btn.clicked.connect(self.view_custom_file)
        view_file_btn.setEnabled(False)
        self.view_custom_file_btn = view_file_btn
        button_layout.addWidget(view_file_btn)
        
        custom_algo_layout.addLayout(button_layout)
        
        return custom_algo_group
    
    def _create_settings_section(self):
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        maxtime_layout = QHBoxLayout()
        maxtime_layout.addWidget(QLabel("Max Time per Algorithm (seconds):"))
        self.maxtime_input = QLineEdit()
        self.maxtime_input.setText("300")
        self.maxtime_input.setMaximumWidth(80)
        maxtime_layout.addWidget(self.maxtime_input)
        maxtime_layout.addStretch()
        settings_layout.addLayout(maxtime_layout)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output Directory:"))
        self.output_dir_input = QLineEdit("")  # Start with empty directory
        self.output_dir_input.setPlaceholderText("Click 'Browse' to select output directory...")
        output_layout.addWidget(self.output_dir_input)
        
        browse_dir_btn = QPushButton("Browse")
        browse_dir_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_dir_btn)
        
        settings_layout.addLayout(output_layout)
        
        return settings_group
    
    def _create_datasets_section(self):
        dataset_group = QGroupBox("Datasets")
        dataset_layout = QVBoxLayout(dataset_group)
        
        self.dataset_vars = {}
        
        dataset_header_layout = QHBoxLayout()
        dataset_header_layout.addWidget(QLabel("Select Datasets:"))
        dataset_header_layout.addStretch()
        
        select_all_dataset_btn = QPushButton("Select All")
        select_all_dataset_btn.clicked.connect(lambda: self.select_all_datasets(True))
        dataset_header_layout.addWidget(select_all_dataset_btn)
        
        select_none_dataset_btn = QPushButton("Select None")
        select_none_dataset_btn.clicked.connect(lambda: self.select_all_datasets(False))
        dataset_header_layout.addWidget(select_none_dataset_btn)
        
        self.dataset_count_label = QLabel("")
        dataset_header_layout.addWidget(self.dataset_count_label)
        
        dataset_layout.addLayout(dataset_header_layout)
        
        dataset_scroll = QScrollArea()
        dataset_scroll.setWidgetResizable(True)
        dataset_scroll.setMaximumHeight(250)
        dataset_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        dataset_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.dataset_custom_scrollbar = EmojiScrollBar(Qt.Orientation.Vertical)
        dataset_scroll.setVerticalScrollBar(self.dataset_custom_scrollbar)
        
        self.dataset_scroll_widget = QWidget()
        self.dataset_scroll_layout = QVBoxLayout(self.dataset_scroll_widget)
        dataset_scroll.setWidget(self.dataset_scroll_widget)
        
        dataset_layout.addWidget(dataset_scroll)
        
        self.populate_datasets()
        
        custom_dataset_group = self._create_custom_dataset_section()
        dataset_layout.addWidget(custom_dataset_group)
        
        states_group = self._create_test_states_section()
        dataset_layout.addWidget(states_group)
        
        return dataset_group
    
    def _create_custom_dataset_section(self):
        custom_dataset_group = QGroupBox("Add/Remove Custom Datasets")
        custom_dataset_layout = QVBoxLayout(custom_dataset_group)
        
        file_selection_layout = QHBoxLayout()
        
        self.custom_dataset_input = QLineEdit()
        self.custom_dataset_input.setPlaceholderText("Selected dataset files will appear here...")
        self.custom_dataset_input.setReadOnly(True)
        file_selection_layout.addWidget(self.custom_dataset_input)
        
        browse_dataset_btn = QPushButton("Browse Files")
        browse_dataset_btn.clicked.connect(self.browse_datasets)
        browse_dataset_btn.setToolTip("Select one or multiple dataset files")
        file_selection_layout.addWidget(browse_dataset_btn)
        
        custom_dataset_layout.addLayout(file_selection_layout)
        
        button_layout = QHBoxLayout()
        
        add_dataset_btn = QPushButton("Add Selected Datasets")
        add_dataset_btn.clicked.connect(self.add_custom_datasets)
        add_dataset_btn.setToolTip("Add all selected dataset files to the list")
        add_dataset_btn.setEnabled(False)
        self.add_datasets_btn = add_dataset_btn
        button_layout.addWidget(add_dataset_btn)
        
        remove_custom_btn = QPushButton("Remove Custom Datasets")
        remove_custom_btn.clicked.connect(self.open_dataset_removal_dialog)
        button_layout.addWidget(remove_custom_btn)
        
        clear_selection_btn = QPushButton("Clear Selection")
        clear_selection_btn.clicked.connect(self.clear_dataset_selection)
        clear_selection_btn.setToolTip("Clear the current file selection")
        button_layout.addWidget(clear_selection_btn)
        
        button_layout.addStretch()
        
        custom_dataset_layout.addLayout(button_layout)
        
        return custom_dataset_group
    
    def _create_test_states_section(self):
        states_group = QGroupBox("Test States")
        states_layout = QVBoxLayout(states_group)
        
        self.state_vars = {}
        states_grid_layout = QGridLayout()
        
        for i, state in enumerate(self.test_states):
            checkbox = EmojiCheckBox(state)
            checkbox.setChecked(False)  # Uncheck all states by default
            self.state_vars[state] = checkbox
            states_grid_layout.addWidget(checkbox, i // 2, i % 2)
        
        states_layout.addLayout(states_grid_layout)
        
        iter_layout = QVBoxLayout()
        
        random_iter_layout = QHBoxLayout()
        random_iter_layout.addWidget(QLabel("Random Iterations:"))
        self.random_iter_input = QLineEdit()
        self.random_iter_input.setText("5")
        self.random_iter_input.setFixedHeight(30)
        self.random_iter_input.setFixedWidth(50)
        random_iter_layout.addWidget(self.random_iter_input)
        self.random_iter_disabled_label = QLabel("Disabled")
        self.random_iter_disabled_label.setVisible(False)
        random_iter_layout.addWidget(self.random_iter_disabled_label)
        random_iter_layout.addStretch()
        iter_layout.addLayout(random_iter_layout)
        
        nearly_sorted_iter_layout = QHBoxLayout()
        nearly_sorted_iter_layout.addWidget(QLabel("Nearly Sorted Iterations:"))
        self.nearly_sorted_iter_input = QLineEdit()
        self.nearly_sorted_iter_input.setText("5")
        self.nearly_sorted_iter_input.setFixedHeight(30)
        self.nearly_sorted_iter_input.setFixedWidth(50)
        nearly_sorted_iter_layout.addWidget(self.nearly_sorted_iter_input)
        self.nearly_sorted_incompatible_label = QLabel("Incompatible with Low size dataset(s)")
        self.nearly_sorted_incompatible_label.setStyleSheet("color: #888888; font-style: italic; font-size: 10px;")
        self.nearly_sorted_incompatible_label.setVisible(False)
        nearly_sorted_iter_layout.addWidget(self.nearly_sorted_incompatible_label)
        self.nearly_sorted_iter_disabled_label = QLabel("Disabled")
        self.nearly_sorted_iter_disabled_label.setVisible(False)
        nearly_sorted_iter_layout.addWidget(self.nearly_sorted_iter_disabled_label)
        nearly_sorted_iter_layout.addStretch()
        iter_layout.addLayout(nearly_sorted_iter_layout)
        
        if "RANDOM" in self.state_vars:
            self.state_vars["RANDOM"].stateChanged.connect(self.on_random_checkbox_changed)
        if "NEARLY SORTED" in self.state_vars:
            self.state_vars["NEARLY SORTED"].stateChanged.connect(self.on_nearly_sorted_checkbox_changed)
        
        self.on_random_checkbox_changed()
        self.on_nearly_sorted_checkbox_changed()
        
        states_layout.addLayout(iter_layout)
        
        return states_group
        
    def setup_execution_tab(self, parent):
        main_layout = QVBoxLayout(parent)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        control_layout = self._create_execution_controls()
        main_layout.addLayout(control_layout)
        
        output_group = self._create_console_output()
        main_layout.addWidget(output_group)
    
    def _create_execution_controls(self):
        control_layout = QHBoxLayout()
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.combined_stop_action)
        self.stop_button.setEnabled(False)
        self.stop_button.setToolTip("Stop benchmarking and logging")
        self.stop_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; }")
        control_layout.addWidget(self.stop_button)
        
        self.restart_button = QPushButton("Restart Benchmarking")
        self.restart_button.clicked.connect(self.start_benchmarking)
        self.restart_button.setEnabled(False)
        control_layout.addWidget(self.restart_button)
        
        self.clear_button = QPushButton("Clear Output")
        self.clear_button.clicked.connect(self.clear_output)
        control_layout.addWidget(self.clear_button)
        
        control_layout.addStretch()
        
        self.progress_label = QLabel("Ready")
        control_layout.addWidget(self.progress_label)
        
        return control_layout
    
    def _create_console_output(self):
        output_group = QGroupBox("Console Output")
        output_layout = QVBoxLayout(output_group)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(400)
        
        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.console.setFont(font)
        
        self.console_custom_scrollbar = EmojiScrollBar(Qt.Orientation.Vertical)
        self.console.setVerticalScrollBar(self.console_custom_scrollbar)
        
        output_layout.addWidget(self.console)
        
        console_control_layout = QHBoxLayout()
        
        save_text_btn = QPushButton("Save to Text")
        save_text_btn.clicked.connect(self.save_console_text)
        console_control_layout.addWidget(save_text_btn)
        
        save_pdf_btn = QPushButton("Save to PDF")
        save_pdf_btn.clicked.connect(self.save_console_pdf)
        console_control_layout.addWidget(save_pdf_btn)
        
        console_control_layout.addStretch()
        
        output_layout.addLayout(console_control_layout)
        
        return output_group
        
    def setup_charts_tab(self, parent):
        main_layout = QVBoxLayout(parent)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        control_layout = self._create_chart_controls()
        main_layout.addLayout(control_layout)
        chart_group = self._create_chart_display()
        main_layout.addWidget(chart_group)
    
    def get_dataset_length(self, dataset_name):
        try:
            # Check if it's a custom dataset with stored path
            if dataset_name in self.dataset_vars and 'path' in self.dataset_vars[dataset_name]:
                file_path = self.dataset_vars[dataset_name]['path']
            else:
                # Default dataset in DATASETS folder
                file_path = resource_path(f"DATASETS/{dataset_name}")
            
            if not os.path.exists(file_path):
                return 0
            
            vals = []
            with open(file_path, "r") as f:
                while True:
                    line = f.readline()
                    if not line:
                         break
                    num = [int(float(s)) if float(s).is_integer() else float(s) for s in line.split()]
                    vals.extend(num)
            
            return len(vals)
        except:
            return 0
    
    def build_dataset_length_map(self, chart_data):
        """Build a dictionary mapping dataset names to their lengths"""
        # Use precomputed mapping if available
        if hasattr(self, 'precomputed_dataset_length_map') and self.precomputed_dataset_length_map:
            return self.precomputed_dataset_length_map
        
        # Fallback to original computation (should rarely be used)
        dataset_length_map = {}
        
        # Extract unique dataset names from chart labels
        dataset_names = set()
        for algo_data in chart_data.values():
            for label in algo_data['labels']:
                # Extract dataset part from label like "T10I4D100K..RD" ->  "T10I4D100K"
                dataset_part = label.split('..')[0]
                
                # Find the full dataset name (add .txt extension to match with dataset_vars)
                full_dataset_name = None
                
                # Check dataset_vars (includes both default and custom) - case insensitive
                for dataset_name in self.dataset_vars.keys():
                    # Remove .txt for comparison and make case-insensitive
                    name_without_ext = dataset_name.replace('.txt', '')
                    if name_without_ext.lower() == dataset_part.lower():
                        full_dataset_name = dataset_name
                        break
                
                if not full_dataset_name:
                    # Try default datasets as fallback - case insensitive
                    for dataset_name, _ in self.default_datasets:
                        name_without_ext = dataset_name.replace('.txt', '')
                        if name_without_ext.lower() == dataset_part.lower():
                            full_dataset_name = dataset_name
                            break
                
                if full_dataset_name:
                    dataset_names.add(full_dataset_name)
        
        # Get lengths for all datasets
        for dataset_name in dataset_names:
            length = self.get_dataset_length(dataset_name)
            dataset_length_map[dataset_name] = length
        
        # Store mapping by dataset part (without .txt and uppercase) for easier lookup
        final_map = {}
        for dataset_name, length in dataset_length_map.items():
            dataset_part = dataset_name.replace('.txt', '').upper()  # Match the format in chart labels
            final_map[dataset_part] = length
        return final_map
    
    def _precompute_chart_data(self):
        try:
            # Initialize all precomputed data
            self.precomputed_dataset_length_map = None
            self.precomputed_sorted_labels = None
            self.precomputed_display_labels = None
            self.precomputed_plot_data = None
            self.precomputed_chart_ready = False
            
            # Prepare chart data
            chart_data = self.prepare_chart_data()
            if not chart_data:
                return
            
            # Build dataset length mapping
            dataset_length_map = {}
            dataset_names = set()
            
            for algo_data in chart_data.values():
                for label in algo_data['labels']:
                    dataset_part = label.split('..')[0]
                    full_dataset_name = None
                    
                    # Check dataset_vars (includes both default and custom) - case insensitive
                    for dataset_name in self.dataset_vars.keys():
                        name_without_ext = dataset_name.replace('.txt', '')
                        if name_without_ext.lower() == dataset_part.lower():
                            full_dataset_name = dataset_name
                            break
                    
                    if not full_dataset_name:
                        # Try default datasets as fallback - case insensitive
                        for dataset_name, _ in self.default_datasets:
                            name_without_ext = dataset_name.replace('.txt', '')
                            if name_without_ext.lower() == dataset_part.lower():
                                full_dataset_name = dataset_name
                                break
                    
                    if full_dataset_name:
                        dataset_names.add(full_dataset_name)
            
            # Get lengths for all datasets
            for dataset_name in dataset_names:
                length = self.get_dataset_length(dataset_name)
                dataset_length_map[dataset_name] = length
            
            # Store mapping by dataset part (without .txt and uppercase) for easier lookup
            final_map = {}
            for dataset_name, length in dataset_length_map.items():
                dataset_part = dataset_name.replace('.txt', '').upper()
                final_map[dataset_part] = length
            
            self.precomputed_dataset_length_map = final_map
            
            # Precompute sorted labels using dataset lengths
            all_labels = []
            for algo_data in chart_data.values():
                all_labels.extend(algo_data['labels'])
            common_labels = list(set(all_labels))
            
            # Sort labels by dataset length, then alphabetically, keeping states together
            def sort_key(label):
                dataset_part = label.split('..')[0]
                state_part = label.split('..')[1] if '..' in label else 'OG'
                dataset_length = final_map.get(dataset_part, 0)
                state_order = {'OG': 0, 'RD': 1, 'NS': 2, 'RS': 3, 'S': 4}
                state_priority = state_order.get(state_part, 999)
                return (dataset_length, dataset_part, state_priority)
            
            common_labels.sort(key=sort_key)
            self.precomputed_sorted_labels = common_labels
            
            # Create display labels showing lengths instead of filenames
            display_labels = []
            for label in common_labels:
                dataset_part = label.split('..')[0]
                state_part = label.split('..')[1] if '..' in label else 'OG'
                dataset_length = final_map.get(dataset_part, 0)
                display_label = f"{dataset_length}..{state_part}"
                display_labels.append(display_label)
                
            self.precomputed_display_labels = display_labels

            # PRECOMPUTE ALL PLOT DATA - This is the key optimization
            # Generate colors for all algorithms
            colors = list(mcolors.TABLEAU_COLORS.values())
            if len(chart_data) > len(colors):
                colors.extend(mcolors.CSS4_COLORS.values())
            
            # Precompute all algorithm plot data with sorted positions
            precomputed_algorithms = []
            
            for i, (algorithm, algo_data) in enumerate(chart_data.items()):
                if not algo_data['times'] or not algo_data['labels']:
                    continue
                
                # Precompute x,y positions for this algorithm using sorted labels
                x_positions = []
                y_values = []
                
                for j, label in enumerate(common_labels):
                    if label in algo_data['labels']:
                        idx = algo_data['labels'].index(label)
                        x_positions.append(j)
                        y_values.append(algo_data['times'][idx])
                
                if x_positions and y_values:
                    algorithm_plot_data = {
                        'name': algorithm,
                        'x_positions': x_positions,
                        'y_values': y_values,
                        'color': colors[i % len(colors)]
                    }
                    precomputed_algorithms.append(algorithm_plot_data)
            
            # Store all precomputed plot data
            self.precomputed_plot_data = {
                'algorithms': precomputed_algorithms,
                'x_labels': list(range(len(common_labels))),
                'display_labels': display_labels,
                'sorted_labels': common_labels
            }
            
            # Mark as ready for instant plotting
            self.precomputed_chart_ready = True
            
            # Log success
            if hasattr(self, 'log_output'):
                unique_datasets = len(set(label.split('..')[0] for label in common_labels))
                total_points = sum(len(algo['x_positions']) for algo in precomputed_algorithms)
                self.log_output(f"Chart data fully precomputed: {len(precomputed_algorithms)} algorithms, {unique_datasets} datasets, {len(common_labels)} labels, {total_points} plot points\n")
            
        except Exception as e:
            # Log error but don't crash - chart will fall back to original computation
            if hasattr(self, 'log_output'):
                self.log_output(f"Warning: Chart precomputation failed: {e}\n")
            # Reset all precomputed data on error
            self.precomputed_dataset_length_map = None
            self.precomputed_sorted_labels = None
            self.precomputed_display_labels = None
            self.precomputed_plot_data = None
            self.precomputed_chart_ready = False

    def _create_chart_controls(self):
        control_layout = QHBoxLayout()
        
        self.refresh_chart_button = QPushButton("Refresh Chart")
        self.refresh_chart_button.clicked.connect(self.update_chart)
        control_layout.addWidget(self.refresh_chart_button)
        
        self.export_chart_button = QPushButton("Export Chart")
        self.export_chart_button.clicked.connect(self.export_chart)
        control_layout.addWidget(self.export_chart_button)
        
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator1)
        
        time_unit_label = QLabel("Time Unit:")
        control_layout.addWidget(time_unit_label)
        
        self.time_unit_combo = QComboBox()
        self.time_unit_combo.addItems(["Milliseconds", "Seconds", "Minutes", "Hours"])
        self.time_unit_combo.setCurrentText("Milliseconds")
        self.time_unit_combo.setToolTip("Select the time unit for the Y-axis display")
        self.time_unit_combo.currentTextChanged.connect(self.on_time_unit_changed)
        control_layout.addWidget(self.time_unit_combo)
        
        scale_label = QLabel("Y-axis Scale:")
        control_layout.addWidget(scale_label)
        
        self.scale_combo = QComboBox()
        self.scale_combo.addItems(["Linear", "Logarithmic"])
        self.scale_combo.setCurrentText("Linear")
        self.scale_combo.setToolTip("Choose between linear and logarithmic Y-axis scaling\nLogarithmic is useful for data with large ranges")
        self.scale_combo.currentTextChanged.connect(self.update_chart)
        control_layout.addWidget(self.scale_combo)
        
        control_layout.addStretch()
        
        self.chart_info_label = QLabel("Chart will be available after successful benchmarking completion")
        control_layout.addWidget(self.chart_info_label)
        
        return control_layout
    
    def _create_chart_canvas(self):
        """Create the matplotlib canvas - only called when charts are actually needed"""
        if self.chart_canvas is not None:
            return  # Already created
            
        # Ensure we're on the main thread
        if not QApplication.instance().thread() == QThread.currentThread():
            QTimer.singleShot(0, self._create_chart_canvas)
            return
            
        try:
            # Create the canvas
            self.chart_canvas = MplCanvas(self, width=12, height=8, dpi=100)
            self.chart_ax = self.chart_canvas.axes
            self.chart_figure = self.chart_canvas.fig
            
            # Set up the chart
            self.chart_ax.set_title("Sorting Algorithm Performance Comparison", fontsize=14, fontweight='bold')
            self.chart_ax.set_xlabel("Dataset and State", fontsize=12)
            self.chart_ax.set_ylabel("Time (milliseconds)", fontsize=12)
            self.chart_ax.grid(True, alpha=0.3)
            
            # Replace the placeholder with the actual canvas
            chart_group = self.chart_placeholder.parent()
            chart_layout = chart_group.layout()
            chart_layout.removeWidget(self.chart_placeholder)
            self.chart_placeholder.deleteLater()
            chart_layout.addWidget(self.chart_canvas)
            
            # Force the layout to update and make the canvas visible
            self.chart_canvas.show()
            chart_group.update()
            
        except Exception as e:
            # If matplotlib fails, show error message
            error_label = QLabel(f"Chart display requires matplotlib with PyQt6 support.\n\nTo enable charts, install:\npip install matplotlib>=3.6.0 numpy>=1.21.0\n\nCharts are optional - all other functionality works normally.\n\nError details: {str(e)}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("""
                QLabel {
                    padding: 20px;
                    background-color: #ffe6e6;
                    border: 1px solid #ff9999;
                    border-radius: 5px;
                    color: #cc0000;
                    font-size: 11px;
                }
            """)
            error_label.setWordWrap(True)
            
            # Replace the placeholder with error message
            chart_group = self.chart_placeholder.parent()
            chart_layout = chart_group.layout()
            chart_layout.removeWidget(self.chart_placeholder)
            self.chart_placeholder.deleteLater()
            chart_layout.addWidget(error_label)
            chart_layout.addWidget(error_label)

    def _create_chart_display(self):
        chart_group = QGroupBox("Performance Chart")
        chart_layout = QVBoxLayout(chart_group)
        
        # Initialize canvas variables but don't create the actual matplotlib canvas yet
        self.chart_canvas = None
        self.chart_ax = None
        self.chart_figure = None
        
        # Create a placeholder label that will be replaced with the actual chart when needed
        self.chart_placeholder = QLabel('Charts will be available after successful benchmarking completion.\n\nThe chart will show:\n->  Each algorithm as a different colored line\n->  X-axis: Dataset states (OG, RD, NS, RS, S)\n->  Y-axis: Execution time (configurable unit)\n->  Legend with algorithm-color mapping\n->  Configurable linear/logarithmic Y-axis scale\n\nAlso check the Tables tab for detailed data!')
        self.chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_placeholder.setStyleSheet("""
            QLabel {
                padding: 20px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                font-size: 11px;
            }
        """)
        chart_layout.addWidget(self.chart_placeholder)
        
        return chart_group
    
    def setup_tables_tab(self, parent):
        main_layout = QVBoxLayout(parent)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        control_layout = self._create_table_controls()
        main_layout.addLayout(control_layout)
        
        table_group = self._create_table_display()
        main_layout.addWidget(table_group)
        
        export_info_group = self._create_export_info()
        main_layout.addWidget(export_info_group)
    
    def _create_table_controls(self):
        control_layout = QHBoxLayout()
        
        self.refresh_table_button = QPushButton("Refresh Table")
        self.refresh_table_button.clicked.connect(self.update_table)
        control_layout.addWidget(self.refresh_table_button)
        
        self.export_table_button = QPushButton("Export Table")
        self.export_table_button.clicked.connect(self.export_table)
        control_layout.addWidget(self.export_table_button)
        
        self.autofit_columns_button = QPushButton("Autofit Columns")
        self.autofit_columns_button.clicked.connect(self.autofit_table_columns)
        self.autofit_columns_button.setToolTip("Auto-resize columns to fit content.\nColumns will become adjustable after autofit.")
        control_layout.addWidget(self.autofit_columns_button)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        control_layout.addWidget(separator)
        
        self.oracle_commit_button = QPushButton("Commit to Oracle DB")
        self.oracle_commit_button.clicked.connect(self.commit_to_oracle_placeholder)
        self.oracle_commit_button.setToolTip("Commit benchmark data to Oracle Database\n(Feature coming soon)")
        oracle_style = """
        QPushButton {
            background-color: #e67e22;
            color: white;
            font-weight: bold;
            border: 1px solid #d35400;
            padding: 5px 10px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #d35400;
        }
        """
        self.oracle_commit_button.setStyleSheet(oracle_style)
        control_layout.addWidget(self.oracle_commit_button)
        
        control_layout.addStretch()
        
        self.table_info_label = QLabel("Table will be available after successful benchmarking completion")
        control_layout.addWidget(self.table_info_label)
        
        return control_layout
    
    def _create_table_display(self):
        table_group = QGroupBox("Benchmark Results Table")
        table_layout = QVBoxLayout(table_group)
        
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(False)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setSortingEnabled(True)
        self.results_table.setMinimumHeight(400)
        
        self.table_v_scrollbar = EmojiScrollBar(Qt.Orientation.Vertical)
        self.results_table.setVerticalScrollBar(self.table_v_scrollbar)
        
        self.table_headers = ["Dataset.State"]
        self.results_table.setColumnCount(len(self.table_headers))
        self.results_table.setHorizontalHeaderLabels(self.table_headers)
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)
        
        self.results_table.setRowCount(1)
        instruction_item = QTableWidgetItem("Benchmark results will appear here after successful completion.\n\nThe table will show:\n->  Dataset.State in first column\n->  Each algorithm as a separate column\n->  Time values or 'Error' for failed runs\n->  Row-wise color coding for better readability")
        instruction_item.setFlags(instruction_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.results_table.setItem(0, 0, instruction_item)
        if len(self.table_headers) > 1:
            self.results_table.setSpan(0, 0, 1, len(self.table_headers))
        
        table_layout.addWidget(self.results_table)
        
        return table_group
    
    def _create_export_info(self):
        export_group = QGroupBox("Export Information")
        export_layout = QVBoxLayout(export_group)
        
        self.csv_path_label = QLabel("CSV Export: Not yet generated")
        self.csv_path_label.setWordWrap(True)
        export_layout.addWidget(self.csv_path_label)
        
        self.excel_path_label = QLabel("Excel Export: Not yet generated")
        self.excel_path_label.setWordWrap(True)
        export_layout.addWidget(self.excel_path_label)
        
        self.db_status_label = QLabel("Oracle DB Status: Not connected")
        self.db_status_label.setWordWrap(True)
        export_layout.addWidget(self.db_status_label)
        
        return export_group
    
    def populate_algorithms(self):
        for i in reversed(range(self.algo_scroll_layout.count())):
            child = self.algo_scroll_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.algo_vars.clear()
        
        for name, func, file in self.default_sorts:
            checkbox = EmojiCheckBox(name)
            checkbox.setChecked(False)
            
            container = QWidget()
            container.setMinimumHeight(35)  # Increased height for better visibility
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(checkbox)
            container_layout.addStretch()
            
            view_btn = QPushButton("View File")
            view_btn.setFixedSize(50, 28)  # Increased height from 22 to 28
            view_btn.setToolTip(f"View {file}")
            view_btn.clicked.connect(lambda checked, f=file: self.view_algorithm_file(f))
            container_layout.addWidget(view_btn)
            
            self.algo_vars[name] = {'checkbox': checkbox, 'func': func, 'file': file}
            checkbox.stateChanged.connect(self.update_algo_count)
            
            self.algo_scroll_layout.addWidget(container)
        
        self.algo_scroll_layout.addStretch()
        self.update_algo_count()
    
    def populate_datasets(self):
        for i in reversed(range(self.dataset_scroll_layout.count())):
            child = self.dataset_scroll_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        self.dataset_vars.clear()
        
        for file, desc in self.default_datasets:
            checkbox = EmojiCheckBox(file)
            checkbox.setChecked(False)
            
            container = QWidget()
            container.setMinimumHeight(35)  # Increased height for better visibility
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(checkbox)
            container_layout.addStretch()
            
            info_tooltip = DatasetInfoTooltip(file)
            container_layout.addWidget(info_tooltip)
            
            self.dataset_vars[file] = {'checkbox': checkbox, 'file': file, 'desc': desc}
            checkbox.stateChanged.connect(self.update_dataset_count)
            
            self.dataset_scroll_layout.addWidget(container)
        
        self.dataset_scroll_layout.addStretch()
        self.update_dataset_count()
    
    def select_all_algorithms(self, select_all=True):
        for name, data in self.algo_vars.items():
            data['checkbox'].setChecked(select_all)
        self.update_algo_count()
    
    def select_all_datasets(self, select_all=True):
        for name, data in self.dataset_vars.items():
            data['checkbox'].setChecked(select_all)
        self.update_dataset_count()
    
    def update_algo_count(self):
        selected = sum(1 for data in self.algo_vars.values() if data['checkbox'].isChecked())
        total = len(self.algo_vars)
        self.algo_count_label.setText(f"{selected}/{total} selected")
    
    def update_dataset_count(self):
        selected = sum(1 for data in self.dataset_vars.values() if data['checkbox'].isChecked())
        total = len(self.dataset_vars)
        self.dataset_count_label.setText(f"{selected}/{total} selected")
    
    def browse_custom_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Python File", "",
            "Python files (*.py);;All files (*.*)"
        )
        if filename:
            self.custom_file_input.setText(filename)
            self.view_custom_file_btn.setEnabled(True)
    
    def add_custom_algorithm(self):
        name = self.custom_name_input.text().strip()
        func = self.custom_func_input.text().strip()
        file = self.custom_file_input.text().strip()
        
        if not all([name, func, file]):
            QMessageBox.critical(self, "Error", "Please fill in all fields for the custom algorithm")
            return
            
        if name in self.algo_vars:
            QMessageBox.critical(self, "Error", "Algorithm name already exists")
            return
        
        checkbox = EmojiCheckBox(name)
        checkbox.setChecked(True)
        
        container = QWidget()
        container.setMinimumHeight(35)  # Increased height for better visibility
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(checkbox)
        
        context_label = QLabel(f"({func} from {os.path.basename(file)})")
        context_label.setObjectName("context_label")
        container_layout.addWidget(context_label)
        container_layout.addStretch()
        
        # Add remove button for custom algorithms
        remove_btn = QPushButton("Remove")
        remove_btn.setFixedSize(50, 28)
        remove_btn.setToolTip(f"Remove custom algorithm: {name}")
        remove_btn.clicked.connect(lambda checked, n=name: self.remove_single_algorithm(n))
        container_layout.addWidget(remove_btn)
        
        view_btn = QPushButton("View File")
        view_btn.setFixedSize(50, 28)  # Increased height from 22 to 28
        view_btn.setToolTip(f"View {os.path.basename(file)}")
        view_btn.clicked.connect(lambda checked, f=file: self.view_algorithm_file(f))
        container_layout.addWidget(view_btn)
        
        self.algo_vars[name] = {'checkbox': checkbox, 'func': func, 'file': file}
        checkbox.stateChanged.connect(self.update_algo_count)
        
        self.algo_scroll_layout.insertWidget(self.algo_scroll_layout.count() - 1, container)
        
        self.custom_name_input.clear()
        self.custom_func_input.clear()
        self.custom_file_input.clear()
        
        self.update_algo_count()
        QMessageBox.information(self, "Success", f"Added custom algorithm: {name}")
        self.view_custom_file_btn.setEnabled(False)
    
    def update_view_file_button(self):
        """Enable/disable view file button based on file input"""
        file_path = self.custom_file_input.text().strip()
        self.view_custom_file_btn.setEnabled(bool(file_path and os.path.exists(file_path)))
    
    def view_custom_file(self):
        file_path = self.custom_file_input.text().strip()
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", "Please select a valid file first.")
            return
        
        dialog = FileViewerDialog(file_path, self)
        dialog.exec()
    
    def view_algorithm_file(self, filename):
        if os.path.isabs(filename):
            file_path = filename
        else:
            file_path = resource_path(filename)
        
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Not Found", f"Algorithm file not found: {filename}")
            return
        
        dialog = FileViewerDialog(file_path, self)
        dialog.exec()
    
    def browse_datasets(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self, "Select Dataset Files", "",
            "Text files (*.txt);;All files (*.*)"
        )
        if filenames:
            self.selected_dataset_files = filenames
            if len(filenames) == 1:
                display_text = os.path.basename(filenames[0])
            else:
                display_text = f"{len(filenames)} files selected: {', '.join([os.path.basename(f) for f in filenames[:3]])}"
                if len(filenames) > 3:
                    display_text += "..."
            self.custom_dataset_input.setText(display_text)
            self.add_datasets_btn.setEnabled(True)
    
    def clear_dataset_selection(self):
        self.selected_dataset_files = []
        self.custom_dataset_input.clear()
        self.add_datasets_btn.setEnabled(False)
    
    def add_custom_datasets(self):
        if not self.selected_dataset_files:
            QMessageBox.critical(self, "Error", "Please select dataset files first")
            return
        
        added_files = []
        skipped_files = []
        error_files = []
        
        for file_path in self.selected_dataset_files:
            try:
                filename = os.path.basename(file_path)
                
                if filename in self.dataset_vars:
                    skipped_files.append(filename)
                    continue
                
                try:
                    size = os.path.getsize(file_path) / (1024 * 1024)
                    desc = f"Custom Dataset ({size:.1f} MB)"
                except:
                    desc = "Custom Dataset"
                
                checkbox = EmojiCheckBox(filename)
                checkbox.setChecked(True)
                
                container = QWidget()
                container.setMinimumHeight(35)  # Increased height for better visibility
                container_layout = QHBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(checkbox)
                container_layout.addStretch()
                
                # Add remove button for custom datasets
                remove_btn = QPushButton("Remove")
                remove_btn.setFixedSize(50, 28)
                remove_btn.setToolTip(f"Remove custom dataset: {filename}")
                remove_btn.clicked.connect(lambda checked, n=filename: self.remove_single_dataset(n))
                container_layout.addWidget(remove_btn)
                
                info_tooltip = DatasetInfoTooltip(filename, file_path)
                container_layout.addWidget(info_tooltip)
                
                self.dataset_vars[filename] = {'checkbox': checkbox, 'file': filename, 'path': file_path, 'desc': desc}
                checkbox.stateChanged.connect(self.update_dataset_count)
                
                self.dataset_scroll_layout.insertWidget(self.dataset_scroll_layout.count() - 1, container)
                added_files.append(filename)
                
            except Exception as e:
                error_files.append(f"{os.path.basename(file_path)} ({str(e)})")
        
        self.clear_dataset_selection()
        self.update_dataset_count()
        
        message_parts = []
        max_files_to_show = 10
        
        if added_files:
            if len(added_files) <= max_files_to_show:
                message_parts.append(f"Successfully added {len(added_files)} dataset(s):\n->  " + "\n->  ".join(added_files))
            else:
                shown_files = added_files[:max_files_to_show]
                remaining_count = len(added_files) - max_files_to_show
                message_parts.append(f"Successfully added {len(added_files)} dataset(s):\n->  " + "\n->  ".join(shown_files) + f"\n->  ... and {remaining_count} more files")
        
        if skipped_files:
            if len(skipped_files) <= max_files_to_show:
                message_parts.append(f"Skipped {len(skipped_files)} existing dataset(s):\n->  " + "\n->  ".join(skipped_files))
            else:
                shown_files = skipped_files[:max_files_to_show]
                remaining_count = len(skipped_files) - max_files_to_show
                message_parts.append(f"Skipped {len(skipped_files)} existing dataset(s):\n->  " + "\n->  ".join(shown_files) + f"\n->  ... and {remaining_count} more files")
        
        if error_files:
            if len(error_files) <= max_files_to_show:
                message_parts.append(f"Failed to add {len(error_files)} dataset(s):\n->  " + "\n->  ".join(error_files))
            else:
                shown_files = error_files[:max_files_to_show]
                remaining_count = len(error_files) - max_files_to_show
                message_parts.append(f"Failed to add {len(error_files)} dataset(s):\n->  " + "\n->  ".join(shown_files) + f"\n->  ... and {remaining_count} more files")
        
        if message_parts:
            full_message = "\n\n".join(message_parts)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Dataset Addition Results")
            msg_box.setText(full_message)
            
            msg_box.setMinimumWidth(400)
            msg_box.setMaximumWidth(600)
            msg_box.setMaximumHeight(500)
            
            msg_box.setTextFormat(Qt.TextFormat.PlainText)
            
            if self.is_dark_theme:
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #2b2b2b;
                        color: #ffffff;
                    }
                    QMessageBox QLabel {
                        color: #ffffff;
                        background-color: #2b2b2b;
                    }
                    QMessageBox QPushButton {
                        background-color: #404040;
                        color: #ffffff;
                        border: 1px solid #555555;
                        padding: 6px 16px;
                        border-radius: 3px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #4a4a4a;
                    }
                """)
            else:
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: #f5f5f5;
                        color: #000000;
                    }
                    QMessageBox QLabel {
                        color: #000000;
                        background-color: #f5f5f5;
                    }
                    QMessageBox QPushButton {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #cccccc;
                        padding: 6px 16px;
                        border-radius: 3px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #e8e8e8;
                    }
                """)
            
            if error_files and not added_files:
                msg_box.setIcon(QMessageBox.Icon.Critical)
            elif error_files or skipped_files:
                msg_box.setIcon(QMessageBox.Icon.Warning)
            else:
                msg_box.setIcon(QMessageBox.Icon.Information)
            
            msg_box.exec()
    
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_dir_input.setText(directory)
    
    def validate_iteration_input(self, input_field, field_name):
        try:
            value = int(input_field.text().strip())
            if value < 1:
                QMessageBox.critical(self, "Invalid Input", f"{field_name} must be at least 1")
                return None
            return value
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", f"{field_name} must be a valid number")
            return None
    
    def validate_maxtime_input(self):
        try:
            value = int(self.maxtime_input.text().strip())
            if value < 60:
                QMessageBox.critical(self, "Invalid Input", "Max Time must be at least 60 seconds")
                return None
            if value > 3600:
                QMessageBox.critical(self, "Invalid Input", "Max Time must be at most 3600 seconds")
                return None
            return value
        except ValueError:
            QMessageBox.critical(self, "Invalid Input", "Max Time must be a valid number")
            return None
    
    def log_output(self, message):
        self.output_queue.put(message)
    
    def setup_output_monitoring(self):
        if self.logging_active:
            try:
                messages_processed = 0
                for _ in range(50):  # Increased from 10 to 50 to process more messages per cycle
                    message = self.output_queue.get_nowait()
                    self.console.append(message)
                    messages_processed += 1
                # If we processed a lot of messages, schedule the next check sooner
                next_check_interval = 25 if messages_processed > 20 else 50
            except queue.Empty:
                next_check_interval = 50
        else:
            try:
                for _ in range(50):
                    self.output_queue.get_nowait()
            except queue.Empty:
                pass
            next_check_interval = 50
        
        QTimer.singleShot(next_check_interval, self.setup_output_monitoring)
    
    def start_benchmarking(self):
        if self.is_running:
            return
            
        selected_algos = [(name, data) for name, data in self.algo_vars.items() if data['checkbox'].isChecked()]
        
        selected_datasets = [(name, data) for name, data in self.dataset_vars.items() if data['checkbox'].isChecked()]
        
        selected_states = [state for state, checkbox in self.state_vars.items() if checkbox.isChecked()]
        
        if not selected_algos:
            QMessageBox.critical(self, "Error", "Please select at least one sorting algorithm")
            return
        if not selected_datasets:
            QMessageBox.critical(self, "Error", "Please select at least one dataset")
            return
        if not selected_states:
            QMessageBox.critical(self, "Error", "Please select at least one test state")
            return
        
        # Check if output directory is selected
        output_dir = self.output_dir_input.text().strip()
        if not output_dir:
            QMessageBox.information(self, "Select Output Directory", 
                                  "Please select an output directory for saving benchmark results.")
            directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if directory:
                self.output_dir_input.setText(directory)
                output_dir = directory
            else:
                return  # User cancelled directory selection
        
        # Validate that the selected directory exists
        if not os.path.exists(output_dir):
            QMessageBox.critical(self, "Error", f"Selected output directory does not exist:\n{output_dir}")
            return
            
        self.is_running = True
        self.execution_stopped = False  
        
        self.logging_active = True
        self.stop_button.setText("Stop")
        self.stop_button.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; }")
        self.stop_button.setToolTip("Stop benchmarking and logging")
        self.stop_button.setEnabled(True)
        
        try:
            while True:
                self.output_queue.get_nowait()
        except queue.Empty:
            pass  
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.restart_button.setEnabled(False)
        self.progress_label.setText("Starting...")
        
        self.chart_data = {}
        self.benchmarking_completed = False
        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)
        
        self.tab_widget.setCurrentIndex(1)
        
        self.current_thread = threading.Thread(
            target=self.run_benchmarking,
            args=(selected_algos, selected_datasets, selected_states),
            daemon=True
        )
        self.current_thread.start()
    
    def stop_benchmarking(self):
        self.is_running = False
        self.start_button.setEnabled(True)
        # Keep stop button enabled if logging is still active, otherwise disable it
        self.stop_button.setEnabled(self.logging_active)
        self.restart_button.setEnabled(True)
        self.progress_label.setText("Stopped")
        self.log_output("\n*** BENCHMARKING FORCEFULLY STOPPED BY USER ***\n")
        
        self.execution_stopped = True
        
        if hasattr(self, 'report') and self.report:
            try:
                self.report.close()
                self.log_output("Excel report discarded due to forced stop.\n")
            except:
                pass
            finally:
                self.report = None
        
        if self.current_thread and self.current_thread.is_alive():
            self.log_output("Thread forcefully terminated.\n")
    
    def combined_stop_action(self):
        """Combined action to stop benchmarking (if running) and then stop logging (if active)"""
        # First, stop benchmarking if it's running
        if self.is_running:
            self.stop_benchmarking()
        
        # Then, always stop logging if it's active (regardless of benchmarking status)
        if self.logging_active:
            self.toggle_logging()
    
    def run_benchmarking(self, selected_algos, selected_datasets, selected_states):
        try:
            maxtime = self.validate_maxtime_input()
            if maxtime is None:
                self.is_running = False
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.restart_button.setEnabled(True)
                return
            self.MAXTIME = maxtime
            output_dir = self.output_dir_input.text()
            self.current_output_dir = output_dir
            os.makedirs(os.path.join(output_dir, "OUTPUTS"), exist_ok=True)
            self.setup_logging_files(output_dir)
            
            now = datetime.datetime.now()
            self.log_output(f"\n\nExecution started on {now.strftime('%A, %dth %B %Y, %H:%M:%S')}")
            
            prog_start = default_timer()
            
            self.log_output("\nLOADING DATASET FILES...")
            full_dataset, successfully_loaded_datasets = self.load_datasets(selected_datasets, selected_states)
            
            if not self.is_running:
                return
                
            readEnd = datetime.datetime.now()
            self.log_output(f"\n\nALL DATASETS LOADED SUCCESSFULLY!!... {readEnd.strftime('%dth %B %Y, %H:%M:%S')}\n")
            
            self.log_output("\n\n------------------------- BENCHMARKING SORTING ALGORITHMS -------------------------\n\n")
            
            total_tests = len(selected_algos) * len(successfully_loaded_datasets) * self.calculate_total_states(selected_states)
            current_test = 0
            
            for algo_name, algo_data in selected_algos:
                if not self.is_running:
                    break
                    
                self.log_output(f"\n>>  {algo_name}")
                self.log_output("------------------------------------------------------------------\n")
                
                try:
                    algo_func = self.load_algorithm_function(algo_data)
                except Exception as e:
                    self.log_output(f"Failed to load algorithm {algo_name}: {e}")
                    continue
                
                for dataset_idx, (dataset_file, dataset_data) in enumerate(successfully_loaded_datasets):
                    if not self.is_running:
                        break
                        
                    dataset_name = dataset_file.removesuffix(".txt").upper()
                    self.log_output(f"\nDATASET: {dataset_name} ({dataset_data['desc']})")
                    self.log_output("----------------------------------------------------\n")
                    
                    states_data = full_dataset[dataset_idx]
                    state_idx = 0
                    
                    for state in selected_states:
                        if not self.is_running:
                            break
                            
                        if state == "RANDOM":
                            iterations = self.validate_iteration_input(self.random_iter_input, "Random Iterations")
                            if iterations is None:
                                return
                        elif state == "NEARLY SORTED":
                            iterations = self.validate_iteration_input(self.nearly_sorted_iter_input, "Nearly Sorted Iterations")
                            if iterations is None:
                                return
                        else:
                            iterations = 1
                            
                        for i in range(iterations):
                            if not self.is_running:
                                break
                                
                            current_test += 1
                            progress = f"Test {current_test}/{total_tests}"
                            self.progress_label.setText(progress)
                            
                            QApplication.processEvents()
                            
                            state_name = f"{state} {i+1}" if iterations > 1 else state
                            self.log_output(f"\nSTATE: {state_name}")
                            self.log_output("--------------------------------------\n")
                            
                            vals = states_data[state_idx].copy()
                            
                            if not self.is_running:
                                break
                                
                            self.run_single_test(algo_name, algo_func, dataset_name, dataset_file, 
                                               state_name, vals, output_dir)
                            
                            state_idx += 1
                    
                    self.log_output("\n\t------------------X-------------X-------------X------------------\n\n")
                
                self.log_output("\n ---------------------------------------------------------------------------------")
                self.log_output(" ---------------------------------------------------------------------------------\n\n\n")
            
            if self.is_running and not getattr(self, 'execution_stopped', False):
                self.log_output("\n----------------------- BENCHMARKING COMPLETED SUCCESSFULLY -----------------------\n")
                now = datetime.datetime.now()
                self.log_output(f"Execution ended on {now.strftime('%A, %dth %B %Y, %H:%M:%S')}")
                self.log_output(f"TOTAL EXECUTION TIME: {default_timer() - prog_start:.2f} secs\n\n")
                
                if hasattr(self, 'report') and self.report:
                    try:
                        self.report.close()
                        excel_path = os.path.join(output_dir, "REPORT.xlsx")
                        self.log_output(f"EXCEL REPORT: {excel_path}\n\n")
                    except Exception as e:
                        self.log_output(f"Error saving Excel report: {e}\n\n")
                
                self.benchmarking_completed = True
                self.tab_widget.setTabEnabled(2, True)
                self.tab_widget.setTabEnabled(3, True)
                
                # Precompute dataset length mapping and sorted labels to avoid lag during chart updates
                QTimer.singleShot(0, self._precompute_chart_data)
                
                # Defer chart and table updates to main thread to avoid threading issues
                # First create the chart canvas, then update it
                QTimer.singleShot(0, self._create_chart_canvas)
                QTimer.singleShot(0, self.update_chart)  # Allow time for canvas creation
                QTimer.singleShot(0, self.update_table)
                
                self.tab_widget.setCurrentIndex(2)
                
                self.log_output("CHARTS TAB: Now available with performance visualization\n")
                self.log_output("TABLES TAB: Now available with detailed benchmark data\n\n")
                
                self.progress_label.setText("Completed Successfully")
                
                # Update stop button text and tooltip since only logging remains
                if self.logging_active:
                    self.stop_button.setText("Stop Logging")
                    self.stop_button.setToolTip("Stop console output logging")
            elif getattr(self, 'execution_stopped', False):
                self.log_output("\n*** EXECUTION WAS STOPPED - NO EXCEL REPORT GENERATED ***\n")
                if hasattr(self, 'report') and self.report:
                    try:
                        self.report.close()
                    except:
                        pass
                    self.report = None
                self.progress_label.setText("Stopped by user")
            
        except Exception as e:
            import traceback
            self.log_output(f"\nERROR: {str(e)}\n")
            self.log_output(f"TRACEBACK: {traceback.format_exc()}\n")
            self.progress_label.setText("Error occurred")
            if hasattr(self, 'report') and self.report:
                try:
                    self.report.close()
                    self.log_output("Excel report discarded due to error.\n")
                except:
                    pass
                self.report = None
        finally:
            self.is_running = False
            self.start_button.setEnabled(True)
            # Keep stop button enabled if logging is still active, otherwise disable it
            self.stop_button.setEnabled(self.logging_active)
            self.restart_button.setEnabled(True)
    
    def calculate_total_states(self, selected_states):
        total = 0
        for state in selected_states:
            if state == "RANDOM":
                try:
                    value = int(self.random_iter_input.text().strip())
                    total += max(1, value)
                except ValueError:
                    total += 5
            elif state == "NEARLY SORTED":
                try:
                    value = int(self.nearly_sorted_iter_input.text().strip())
                    total += max(1, value)
                except ValueError:
                    total += 5
            else:
                total += 1
        return total
    
    def setup_logging_files(self, output_dir):
        record_file = os.path.join(output_dir, "RECORDS.csv")
        
        record_header = ["ALGORITHM", "DATASET", "FILE SIZE (MB)", "ELEMENTS", "STATE", "ERROR", "SORT", "TIME (SECS)"]
        
        with open(record_file, "w", newline="") as f:
            csvf = csv.writer(f)
            csvf.writerow(record_header)
        
        self.report = xlsxwriter.Workbook(os.path.join(output_dir, "REPORT.xlsx"))
        self.ws1 = self.report.add_worksheet("Total Data")
        self.ws2 = self.report.add_worksheet("Mean Data")
        
        self.excel_row_counter = 1  
        
        headers = ["DATASET", "ALGORITHM", "SIZE(MB)", "ELEMENTS", "STATE", "ERROR", "SORTED", "TIME(secs)"]
        for col, header in enumerate(headers):
            self.ws1.write(0, col, header)
            self.ws2.write(0, col, header)
    
    def load_algorithm_function(self, algo_data):
        func_name = algo_data['func']
        file_name = algo_data['file']
        
        try:
            module_name = os.path.splitext(file_name)[0]
            try:
                module = __import__(module_name)
                return getattr(module, func_name)
            except ImportError:
                file_path = resource_path(file_name)
                spec = importlib.util.spec_from_file_location("algorithm_module", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return getattr(module, func_name)
        except Exception as e:
            raise ImportError(f"Could not load function {func_name} from {file_name}: {e}")
    
    def load_datasets(self, selected_datasets, selected_states):
        full_dataset = []
        successfully_loaded_datasets = []
        
        for dataset_file, dataset_data in selected_datasets:
            if not self.is_running:
                break
                
            dataset_path = dataset_data.get('path', resource_path(os.path.join("DATASETS", dataset_file)))
            self.log_output(f"\nLOADING {dataset_file}...")
            
            QApplication.processEvents()
            
            try:
                vals = []
                self.readtolist(vals, dataset_path)
                
                if not self.is_running:
                    break
                
                dataset_states = []
                dataset_processing_failed = False
                
                for state in selected_states:
                    if not self.is_running:
                        break
                    if state == "ORIGINAL":
                        self.log_output(f"\nGENERATING STATE {state}...")
                        self.log_output(f"TOTAL ELEMENTS: {len(vals)}")
                        self.log_output(f"UNSORTED ELEMENTS: {self.sortvarchk(vals)}")
                        dataset_states.append(vals.copy())
                        
                    elif state == "RANDOM":
                        iterations = self.validate_iteration_input(self.random_iter_input, "Random Iterations")
                        if iterations is None:
                            self.log_output(f"Error: Invalid random iterations input. Skipping {dataset_file}")
                            dataset_processing_failed = True
                            break  # Skip this dataset and continue with next one
                        for i in range(iterations):
                            state_name = f"{state} {i+1}"
                            self.log_output(f"\nGENERATING STATE {state_name}...")
                            x = vals.copy()
                            random.shuffle(x)
                            self.log_output(f"TOTAL ELEMENTS: {len(x)}")
                            self.log_output(f"UNSORTED ELEMENTS: {self.sortvarchk(x)}")
                            dataset_states.append(x)
                            
                    elif state == "NEARLY SORTED":
                        iterations = self.validate_iteration_input(self.nearly_sorted_iter_input, "Nearly Sorted Iterations")
                        if iterations is None:
                            self.log_output(f"Error: Invalid nearly sorted iterations input. Skipping {dataset_file}")
                            dataset_processing_failed = True
                            break  # Skip this dataset and continue with next one
                        for i in range(iterations):
                            state_name = f"{state} {i+1}"
                            self.log_output(f"\nGENERATING STATE {state_name}...")
                            x = vals.copy()
                            self.nearlySort(x)
                            self.log_output(f"TOTAL ELEMENTS: {len(x)}")
                            self.log_output(f"UNSORTED ELEMENTS: {self.sortvarchk(x)}")
                            dataset_states.append(x)
                            
                    elif state == "SORTED":
                        self.log_output(f"\nGENERATING STATE {state}...")
                        x = sorted(vals.copy())
                        self.log_output(f"TOTAL ELEMENTS: {len(x)}")
                        self.log_output(f"UNSORTED ELEMENTS: {self.sortvarchk(x)}")
                        dataset_states.append(x)
                        
                    elif state == "REVERSE SORTED":
                        self.log_output(f"\nGENERATING STATE {state}...")
                        x = sorted(vals.copy(), reverse=True)
                        self.log_output(f"TOTAL ELEMENTS: {len(x)}")
                        self.log_output(f"UNSORTED ELEMENTS: {self.sortvarchk(x)}")
                        dataset_states.append(x)
                
                # Only add dataset to full_dataset if processing was successful
                if not dataset_processing_failed and self.is_running:
                    full_dataset.append(dataset_states)
                    successfully_loaded_datasets.append((dataset_file, dataset_data))
                    self.log_output(f"\n\n{dataset_file} LOADED SUCCESSFULLY!...")
                    self.log_output("---------------------------------------------------\n")
                else:
                    self.log_output(f"\n\n{dataset_file} SKIPPED DUE TO ERRORS...")
                    self.log_output("---------------------------------------------------\n")
                
            except Exception as e:
                self.log_output(f"Error loading {dataset_file}: {e}")
                continue
        
        return full_dataset, successfully_loaded_datasets
    
    def readtolist(self, vals, filepath):
        try:
            with open(filepath, "r") as f:
                while True:
                    line = f.readline()
                    if not line:
                         break
                    num = [int(float(s)) if float(s).is_integer() else float(s) for s in line.split()]
                    vals.extend(num)
        except MemoryError:
                self.log_output("READING ERROR!")
                self.log_output("OUT OF MEMORY")
                raise
    
    def random_pair(self, start, end, max_diff):
        while True: 
            x = random.randint(start, end-max_diff-1) 
            y = random.randint(x + 2, end) 
            if 2 < y - x <= max_diff: 
                return (x, y) 

    def allNotSame(self, arr):
        if len(set(arr)) > 1:
            return True
        return False
            

    def nearlySort(self, vals):
        n = len(vals)
        vals.sort()
        if n <= 2:
            return vals
        elif n <= 10:
            id1 = random.randint(0, n-2)
            id2 = random.randint(id1+1, n-1)
            vals[id1], vals[id2] = vals[id2], vals[id1]
            return vals
        trace = []
        max_reps = random.randint(3, 5)
        reps = 0
        while reps <= max_reps:
            t = self.random_pair(0, n-1, n//2)
            if t not in trace:
                trace.append(t)
                x, y = t
                temp = vals[x:y+1]
                if self.allNotSame(temp):
                    random.shuffle(temp)
                    vals[x:y+1] = temp
                    reps += 1
        return vals
    
    def sortvarchk(self, arr):
        chk = sorted(arr)
        c = 0
        for i in range(len(arr)):
            if arr[i] != chk[i]:
                c += 1
        return c
    
    def checkSorted(self, vals):
        for i in range(len(vals) - 1):
            if vals[i] > vals[i + 1]:
                return False
        return True
    
    def run_single_test(self, algo_name, algo_func, dataset_name, dataset_file, state_name, vals, output_dir):
        if not self.is_running:
            return
            

        n = len(vals)
        unsorted = self.sortvarchk(vals)
        
        self.log_output(f"\tELEMENTS: {n}")
        self.log_output(f"\tUNSORTED ELEMENTS: {unsorted}")
        
        QApplication.processEvents()
        
        try:
            sort_start = datetime.datetime.now()
            self.log_output(f"\tSTART: {sort_start.strftime('%dth %B %Y, %H:%M:%S')}")
            self.log_output(f"\tNow running {algo_name} on {dataset_name} (STATE: {state_name}) .....")
            
            QApplication.processEvents()
            
            start = default_timer()
            
            try:
                algo_func(vals, 0, n-1, start, self.MAXTIME)
            except TypeError:
                algo_func(vals)
            
            stop = default_timer() - start
            sort_end = datetime.datetime.now()
            
            if not self.is_running:
                return
            
            self.log_output(f"\tEND: {sort_end.strftime('%dth %B %Y, %H:%M:%S')}")
            self.log_output(f"\tTime: {stop:.6f} secs")
            
            sortchk = self.checkSorted(vals)
            self.log_output(f"\tSORTED: {sortchk}")
            
            self.log_to_csv(algo_name, dataset_name, dataset_file, state_name, 
                           len(vals), False, sortchk, stop, output_dir)
            
            try:
                if dataset_file in self.dataset_vars and 'path' in self.dataset_vars[dataset_file]:
                    file_path = self.dataset_vars[dataset_file]['path']
                else:
                    file_path = resource_path(os.path.join("DATASETS", dataset_file))
                size = os.path.getsize(file_path) / (1024 * 1024)
            except (OSError, KeyError):
                size = 0
                
            if size <= 10:
                output_file = os.path.join(output_dir, "OUTPUTS", 
                    f"{dataset_name}_{state_name.replace(' ', '_')}_{algo_name.replace(' ', '_')}_OUTPUT.txt")
                self.writetotext(vals, output_file)
                self.log_output(f"\tOUTPUT PATH: {output_file}")
            else:
                self.log_output(f"\tOUTPUT PATH: NA (Content > 10 MB)")
                
        except Exception as e:
            stop = default_timer() - start
            error_msg = str(e)
            if "Time limit exceeded" in error_msg or stop > self.MAXTIME:
                error_msg = f"Time limit exceeded, (Limit: {self.MAXTIME} secs)"
            
            sort_end = datetime.datetime.now()
            self.log_output(f"\tEND: {sort_end.strftime('%dth %B %Y, %H:%M:%S')}")
            self.log_output(f"\t!! SORTING FAILED !!")
            self.log_output(f"\tException: {type(e).__name__} {error_msg}")
            
            self.log_to_csv(algo_name, dataset_name, dataset_file, state_name, 
                           len(vals), True, "NA", stop, output_dir)
        
        self.log_output("")  
        
        QApplication.processEvents()
    
    def log_to_csv(self, algo_name, dataset_name, dataset_file, state_name, 
                   elements, error, sortchk, time_taken, output_dir):
        try:
            record_file = os.path.join(output_dir, "RECORDS.csv")
            
            try:
                if dataset_file in self.dataset_vars and 'path' in self.dataset_vars[dataset_file]:
                    file_path = self.dataset_vars[dataset_file]['path']
                else:
                    file_path = resource_path(os.path.join("DATASETS", dataset_file))
                size = os.path.getsize(file_path) / (1024 * 1024)
            except (OSError, KeyError):
                size = 0.0
            
            with open(record_file, "a", newline="") as f:
                csvf = csv.writer(f)
                csvf.writerow([algo_name, dataset_name, f"{size:.3f}", elements, 
                              state_name, error, sortchk, f"{time_taken:.6f}"])
            
            if hasattr(self, 'report') and self.report and hasattr(self, 'ws1'):
                try:
                    if not hasattr(self, 'excel_row_counter'):
                        self.excel_row_counter = 1  
                    
                    row = self.excel_row_counter
                    
                    self.ws1.write(row, 0, dataset_name)
                    self.ws1.write(row, 1, algo_name)
                    self.ws1.write(row, 2, f"{size:.3f}")
                    self.ws1.write(row, 3, elements)
                    self.ws1.write(row, 4, state_name)
                    self.ws1.write(row, 5, "Yes" if error else "No")
                    self.ws1.write(row, 6, "Yes" if sortchk else "No")
                    self.ws1.write(row, 7, f"{time_taken:.6f}")
                    
                    self.ws2.write(row, 0, dataset_name)
                    self.ws2.write(row, 1, algo_name)
                    self.ws2.write(row, 2, f"{size:.3f}")
                    self.ws2.write(row, 3, elements)
                    self.ws2.write(row, 4, state_name)
                    self.ws2.write(row, 5, "Yes" if error else "No")
                    self.ws2.write(row, 6, "Yes" if sortchk else "No")
                    self.ws2.write(row, 7, f"{time_taken:.6f}")
                    
                    self.excel_row_counter += 1
                    
                except Exception as e:
                    self.log_output(f"Warning: Could not write to Excel: {e}")
            
            self.store_chart_data(algo_name, dataset_name, state_name, error, time_taken)
                    
        except Exception as e:
            self.log_output(f"Warning: Could not log to CSV: {e}")
    
    def store_chart_data(self, algo_name, dataset_name, state_name, error, time_taken):
        try:
            if not hasattr(self, 'chart_data'):
                self.chart_data = {}
            
            key = f"{algo_name}_{dataset_name}_{state_name}_{len(self.chart_data)}"
            
            self.chart_data[key] = {
                'algorithm': algo_name,
                'dataset': dataset_name,
                'state': state_name,
                'error': error,
                'time': time_taken if not error else "NA"
            }
        except Exception as e:
            self.log_output(f"Warning: Could not store chart data: {e}")
    
    def writetotext(self, vals, filepath):
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w+") as f:
                for i in vals:
                    f.write(str(i)+" ")
        except Exception as e:
            self.log_output(f"Warning: Could not write output file: {e}")
    
    def clear_output(self):
        self.console.clear()
        try:
            while True:
                self.output_queue.get_nowait()
        except queue.Empty:
            pass
    
    def save_console_text(self):
        content = self.console.toPlainText()
        self.save_text_content(content)
    
    def save_text_content(self, content):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Console Output", "",
            "Text files (*.txt);;All files (*.*)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Console output saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
    
    def save_console_pdf(self):
        content = self.console.toPlainText()
        self.save_pdf_content(content)
    
    def save_pdf_content(self, content):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Console Output as PDF", "",
            "PDF files (*.pdf);;All files (*.*)"
        )
        if filename:
            try:
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import inch
                    
                    doc = SimpleDocTemplate(filename, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip():
                            p = Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), 
                                        styles['Normal'])
                            story.append(p)
                        else:
                            story.append(Spacer(1, 0.1 * inch))
                    
                    doc.build(story)
                    QMessageBox.information(self, "Success", f"Console output saved to {filename}")
                    
                except ImportError:
                    QMessageBox.warning(self, "PDF Export", 
                        "ReportLab not available. Please install it for PDF export:\npip install reportlab")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save PDF: {e}")
    
    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()
    
    def update_disabled_label_styling(self):
        if self.is_dark_theme:
            disabled_style = "color: #606060; font-style: italic;"
            context_style = "color: #808080;"
            disabled_input_style = "background-color: #3a3a3a; color: #888888; border: 2px solid #555555;"
        else:
            disabled_style = "color: #888888; font-style: italic;"
            context_style = "color: #666666;"
            disabled_input_style = "background-color: #f0f0f0; color: #888888; border: 2px solid #dddddd;"
        
        try:
            self.random_iter_disabled_label.setStyleSheet(disabled_style)
            self.nearly_sorted_iter_disabled_label.setStyleSheet(disabled_style)
        except Exception as e:
            print(f"Warning: Could not apply disabled label styling: {e}")
        
        try:
            for context_label in self.findChildren(QLabel):
                if context_label.objectName() == "context_label":
                    context_label.setStyleSheet(context_style)
        except Exception as e:
            print(f"Warning: Could not apply context label styling: {e}")
        
        try:
            if hasattr(self, 'random_iter_input') and not self.random_iter_input.isEnabled():
                self.random_iter_input.setStyleSheet(disabled_input_style)
            if hasattr(self, 'nearly_sorted_iter_input') and not self.nearly_sorted_iter_input.isEnabled():
                self.nearly_sorted_iter_input.setStyleSheet(disabled_input_style)
        except Exception as e:
            print(f"Warning: Could not apply disabled input styling: {e}")

    def apply_theme(self):
        if self.is_dark_theme:
            self.apply_dark_theme()
            self.theme_button.setText("☀️ Light Theme")
        else:
            self.apply_light_theme()
            self.theme_button.setText("🌙 Dark Theme")
        
        if hasattr(self, 'algo_custom_scrollbar'):
            self.algo_custom_scrollbar.set_theme(self.is_dark_theme)
        if hasattr(self, 'dataset_custom_scrollbar'):
            self.dataset_custom_scrollbar.set_theme(self.is_dark_theme)
        if hasattr(self, 'console_custom_scrollbar'):
            self.console_custom_scrollbar.set_theme(self.is_dark_theme)
        if hasattr(self, 'table_v_scrollbar'):
            self.table_v_scrollbar.set_theme(self.is_dark_theme)
        
        self.update_disabled_label_styling()
    
    def apply_light_theme(self):
        light_style = """
        /* Main Window */
        QMainWindow {
            background-color: #f5f5f5;
            color: #000000;
        }

        /* Central Widget */
        QWidget {
            background-color: #f5f5f5;
            color: #000000;
        }

        /* Group Boxes */
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            margin-top: 12px;
            padding-top: 12px;
            background-color: #f5f5f5;
            color: #000000;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            color: #000000;
            background-color: #f5f5f5;
        }

        /* Labels */
        QLabel {
            color: #000000;
            background-color: transparent;
        }

        /* Buttons */
        QPushButton {
            background-color: #e8e8e8;
            border: 1px solid #b0b0b0;
            padding: 8px 16px;
            min-width: 80px;
            color: #000000;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #f0f0f0;
            border-color: #999999;
        }
        QPushButton:pressed {
            background-color: #e0e0e0;
            border-color: #888888;
        }
        QPushButton:disabled {
            background-color: #f8f9fa;
            color: #6c757d;
            border-color: #dee2e6;
        }

        /* Text Fields */
        QLineEdit, QTextEdit {
            background-color: #ffffff;
            border: 2px solid #cccccc;
            padding: 6px;
            color: #000000;
            selection-background-color: #3399ff;
            selection-color: #ffffff;
        }
        QLineEdit:focus, QTextEdit:focus {
            border-color: #007bff;
        }
        QLineEdit:disabled {
            background-color: #f0f0f0;
            color: #888888;
            border-color: #dddddd;
        }

        /* Spin Boxes */
        QSpinBox {
            background-color: #ffffff;
            border: 2px solid #cccccc;
            padding: 6px;
            color: #000000;
        }
        QSpinBox:focus {
            border-color: #007bff;
        }

        /* Checkboxes */
        QCheckBox {
            color: #000000;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }
        QCheckBox::indicator:hover {
            border-color: #999999;
        }

        /* Tab Widget */
        QTabWidget::pane {
            border: 2px solid #cccccc;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #e9ecef;
            border: 1px solid #cccccc;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            color: #000000;
        }
        QTabBar::tab:selected {
            background-color: #ffffff;
            border-bottom: 2px solid #ffffff;
            color: #000000;
        }
        QTabBar::tab:hover {
            background-color: #f8f9fa;
        }

        /* Scroll Areas */
        QScrollArea {
            border: 1px solid #cccccc;
            background-color: #ffffff;
        }
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 16px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #cccccc;
            min-height: 20px;
            margin: 20px 2px 20px 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #999999;
        }
        QScrollBar::add-line:vertical {
            height: 16px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
            border: 1px solid #aaaaaa;
            background-color: #e8e8e8;
        }
        QScrollBar::sub-line:vertical {
            height: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
            border: 1px solid #aaaaaa;
            background-color: #e8e8e8;
        }
        QScrollBar::up-arrow:vertical {
            image: none;
            border: none;
            width: 16px;
            height: 16px;
        }
        QScrollBar::down-arrow:vertical {
            image: none;
            border: none;
            width: 16px;
            height: 16px;
        }
        QScrollBar::add-line:vertical:hover,
        QScrollBar::sub-line:vertical:hover {
            background-color: #d0d0d0;
        }
        QScrollBar::up-arrow:vertical:hover {
            border-bottom-color: #333333;
        }
        QScrollBar::down-arrow:vertical:hover {
            border-top-color: #333333;
        }

        /* Splitter */
        QSplitter::handle {
            background-color: #cccccc;
        }
        QSplitter::handle:hover {
            background-color: #999999;
        }

        /* Combo Boxes */
        QComboBox {
            background-color: #ffffff;
        }
        
        /* Table Widget */
        QTableWidget {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            color: #000000;
            gridline-color: #e0e0e0;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #e0e0e0;
        }
        QTableWidget::item:selected {
            background-color: #3399ff;
            color: #ffffff;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            padding: 8px;
            font-weight: bold;
            color: #000000;
        }
        """
        try:
            self.setStyleSheet(light_style)
        except Exception as e:
            print(f"Warning: Could not apply light theme stylesheet: {e}")
            self.setStyleSheet("QMainWindow { background-color: #f5f5f5; color: #ffffff; }")

    def apply_dark_theme(self):
        dark_style = """
        /* Main Window */
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        /* Central Widget */
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        /* Group Boxes */
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555555;
            margin-top: 12px;
            padding-top: 12px;
            background-color: #3c3c3c;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            color: #ffffff;
            background-color: #2b2b2b;
        }
        
        /* Labels */
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        
        
        /* Buttons */
        QPushButton {
            background-color: #404040;
            border: 1px solid #606060;
            padding: 8px 16px;
            min-width: 80px;
            color: #ffffff;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
            border-color: #707070;
        }
        QPushButton:pressed {
            background-color: #353535;
            border-color: #505050;
        }
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #808080;
            border-color: #404040;
        }
        
        /* Text Fields */
        QLineEdit, QTextEdit {
            background-color: #1e1e1e;
            border: 2px solid #555555;
            padding: 6px;
            color: #ffffff;
            selection-background-color: #0078d4;
            selection-color: #ffffff;
        }
        QLineEdit:focus, QTextEdit:focus {
            border-color: #0078d4;
        }
        QLineEdit:disabled {
            background-color: #3a3a3a;
            color: #888888;
            border-color: #555555;
        }
        
        /* Spin Boxes */
        QSpinBox {
            background-color: #1e1e1e;
            border: 2px solid #555555;
            padding: 6px;
            color: #ffffff;
        }
        QSpinBox:focus {
            border-color: #0078d4;
        }
        
        /* Checkboxes */
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 1px solid #555555;
            background-color: #1e1e1e;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #555555;
            background-color: #1e1e1e;
        }
        QCheckBox::indicator:hover {
            border-color: #777777;
        }
        
        /* Tab Widget */
        QTabWidget::pane {
            border: 2px solid #555555;
            background-color: #3c3c3c;
        }
        QTabBar::tab {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            color: #ffffff;
        }
        QTabBar::tab:selected {
            background-color: #3c3c3c;
            border-bottom: 2px solid #3c3c3c;
            color: #ffffff;
        }
        QTabBar::tab:hover {
            background-color: #4a4a4a;
        }
        
        /* Scroll Areas */
        QScrollArea {
            border: 1px solid #555555;
            background-color: #3c3c3c;
        }
        QScrollBar:vertical {
            background-color: #404040;
            width: 16px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #666666;
            min-height: 20px;
            margin: 20px 2px 20px 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #777777;
        }
        QScrollBar::add-line:vertical {
            height: 16px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
            border: 1px solid #555555;
            background-color: #555555;
        }
        QScrollBar::sub-line:vertical {
            height: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
            border: 1px solid #555555;
            background-color: #555555;
        }
        QScrollBar::up-arrow:vertical {
            image: none;
            border: none;
            width: 16px;
            height: 16px;
        }
        QScrollBar::down-arrow:vertical {
            image: none;
            border: none;
            width: 16px;
            height: 16px;
        }
        QScrollBar::add-line:vertical:hover,
        QScrollBar::sub-line:vertical:hover {
            background-color: #666666;
        }
        }
        
        /* Splitter */
        QSplitter::handle {
            background-color: #555555;
        }
        QSplitter::handle:hover {
            background-color: #666666;
        }
        
        /* Table Widget */
        QTableWidget {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            gridline-color: #555555;
            color: #ffffff;
            selection-background-color: #0078d4;
            selection-color: #ffffff;
        }
        QTableWidget::item {
            padding: 6px;
            border-bottom: 1px solid #555555;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        QTableWidget::item:hover {
            background-color: #4a4a4a;
        }
        QTableWidget QScrollBar:vertical {
            background-color: #404040;
            width: 16px;
            margin: 0px;
        }
        QTableWidget QScrollBar::handle:vertical {
            background-color: #666666;
            min-height: 20px;
            margin: 20px 2px 20px 2px;
        }
        QTableWidget QScrollBar::handle:vertical:hover {
            background-color: #777777;
        }
        QTableWidget QScrollBar::add-line:vertical {
            height: 16px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
            border: 1px solid #555555;
            background-color: #555555;
        }
        QTableWidget QScrollBar::sub-line:vertical {
            height: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
            border: 1px solid #555555;
            background-color: #555555;
        }
        QTableWidget QScrollBar::up-arrow:vertical {
            image: none;
            border: none;
            width: 16px;
            height: 16px;
        }
        QTableWidget QScrollBar::down-arrow:vertical {
            image: none;
            border: none;
            width: 16px;
            height: 16px;
        }
        QTableWidget QScrollBar::add-line:vertical:hover,
        QTableWidget QScrollBar::sub-line:vertical:hover {
            background-color: #666666;
        }
        QHeaderView::section {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 6px;
            font-weight: bold;
            color: #ffffff;
        }
        QHeaderView::section:hover {
            background-color: #4a4a4a;
        }
        """
        try:
            self.setStyleSheet(dark_style)
        except Exception as e:
            print(f"Warning: Could not apply dark theme stylesheet: {e}")
            self.setStyleSheet("QMainWindow { background-color: #2b2b2b; color: #ffffff; }")

    def on_random_checkbox_changed(self):
        if "RANDOM" in self.state_vars:
            is_checked = self.state_vars["RANDOM"].isChecked()
            self.random_iter_input.setEnabled(is_checked)
            QTimer.singleShot(0, lambda: self.random_iter_disabled_label.setVisible(not is_checked))
            
            if not is_checked:
                if self.is_dark_theme:
                    disabled_input_style = "background-color: #3a3a3a; color: #888888; border: 2px solid #555555;"
                else:
                    disabled_input_style = "background-color: #f0f0f0; color: #888888; border: 2px solid #dddddd;"
                self.random_iter_input.setStyleSheet(disabled_input_style)
            else:
                self.random_iter_input.setStyleSheet("")
    
    def on_nearly_sorted_checkbox_changed(self):
        if "NEARLY SORTED" in self.state_vars:
            is_checked = self.state_vars["NEARLY SORTED"].isChecked()
            self.nearly_sorted_iter_input.setEnabled(is_checked)
            QTimer.singleShot(0, lambda: self.nearly_sorted_iter_disabled_label.setVisible(not is_checked))
            
            if not is_checked:
                if self.is_dark_theme:
                    disabled_input_style = "background-color: #3a3a3a; color: #888888; border: 2px solid #555555;"
                else:
                    disabled_input_style = "background-color: #f0f0f0; color: #888888; border: 2px solid #dddddd;"
                self.nearly_sorted_iter_input.setStyleSheet(disabled_input_style)
            else:
                self.nearly_sorted_iter_input.setStyleSheet("")
    
    def on_time_unit_changed(self):
        """Handle time unit change with debugging"""
        if hasattr(self, 'chart_ax') and hasattr(self, 'chart_canvas'):
            # Force disable precomputed data to ensure fresh calculation
            self.precomputed_chart_ready = False
            self.precomputed_plot_data = None
            
            # Clear the chart completely
            self.chart_ax.clear()
            
            # Get fresh chart data with new time unit conversion
            chart_data = self.prepare_chart_data()
            
            if chart_data:
                # Debug: Print some values to console to verify conversion
                for algo_name, algo_data in chart_data.items():
                    if algo_data['times']:
                        break
                
                self.create_performance_plot(chart_data)
            
            # Force canvas redraw
            self.chart_canvas.draw()

    def update_chart(self):
        if not self.benchmarking_completed:
            return
            
        # Check if chart exists
        if self.chart_canvas is None or not hasattr(self, 'chart_figure') or self.chart_figure is None:
            return
            
        try:
            self.chart_ax.clear()
            
            chart_data = self.prepare_chart_data()
            
            if not chart_data:
                self.chart_ax.text(0.5, 0.5, 'No valid data available for charting', 
                                 horizontalalignment='center', verticalalignment='center', 
                                 transform=self.chart_ax.transAxes, fontsize=12)
                self.chart_canvas.draw()
                return
            
            self.create_performance_plot(chart_data)
            
            # Draw the canvas to display the chart
            self.chart_canvas.draw()
            
            total_algorithms = len(chart_data)
            total_points = sum(len(data['times']) for data in chart_data.values())
            self.chart_info_label.setText(f"Chart: {total_algorithms} algorithms, {total_points} data points")
            
        except Exception as e:
            self.chart_ax.clear()
            self.chart_ax.text(0.5, 0.5, f'Error creating chart: {str(e)}', 
                             horizontalalignment='center', verticalalignment='center', 
                             transform=self.chart_ax.transAxes, fontsize=12)
            self.chart_canvas.draw()
    
    def prepare_chart_data(self):
        """Prepare chart data from benchmarking results"""
        if not hasattr(self, 'chart_data') or not self.chart_data:
            return {}
        
        # Get current time unit and conversion factor
        time_unit = getattr(self, 'time_unit_combo', None)
        unit_text = time_unit.currentText() if time_unit else "Milliseconds"
        
        # Define conversion factors from milliseconds
        if unit_text == "Seconds":
            conversion_factor = 0.001  # ms to seconds
        elif unit_text == "Minutes":
            conversion_factor = 0.001 / 60  # ms to minutes  
        elif unit_text == "Hours":
            conversion_factor = 0.001 / 3600  # ms to hours
        else:  # Milliseconds or default
            conversion_factor = 1.0
        
        chart_data = {}
        
        for key, data in self.chart_data.items():
            algorithm = data['algorithm']
            dataset = data['dataset']
            state = data['state']
            time_secs = data['time']
            error = data['error']
            
            if error or time_secs == "NA":
                continue
                
            try:
                time_value = float(time_secs)
                time_ms = time_value * 1000  # Convert seconds to milliseconds
                
                # Apply time unit conversion
                converted_time = time_ms * conversion_factor
                
            except (ValueError, TypeError):
                continue
            
            if algorithm not in chart_data:
                chart_data[algorithm] = {
                    'times': [],
                    'labels': [],
                    'datasets': {}
                }
            
            # Initialize dataset structure if not exists
            if dataset not in chart_data[algorithm]['datasets']:
                chart_data[algorithm]['datasets'][dataset] = {}
            
            # Store the converted time for this dataset and state
            chart_data[algorithm]['datasets'][dataset][state] = converted_time
        
        # Process the stored data to create times and labels arrays
        for algorithm in chart_data:
            algo_data = chart_data[algorithm]
            
            for dataset in algo_data['datasets']:
                dataset_data = algo_data['datasets'][dataset]
                
                # Remove .txt extension from dataset name for labels
                dataset_name = dataset.replace('.txt', '')
                
                if 'ORIGINAL' in dataset_data:
                    algo_data['times'].append(dataset_data['ORIGINAL'])
                    algo_data['labels'].append(f"{dataset_name}..OG")
                
                random_times = [v for k, v in dataset_data.items() if k.startswith('RANDOM')]
                if random_times:
                    avg_random = sum(random_times) / len(random_times)
                    algo_data['times'].append(avg_random)
                    algo_data['labels'].append(f"{dataset_name}..RD")
                
                nearly_times = [v for k, v in dataset_data.items() if k.startswith('NEARLY SORTED')]
                if nearly_times:
                    avg_nearly = sum(nearly_times) / len(nearly_times)
                    algo_data['times'].append(avg_nearly)
                    algo_data['labels'].append(f"{dataset_name}..NS")
                
                if 'REVERSE SORTED' in dataset_data:
                    algo_data['times'].append(dataset_data['REVERSE SORTED'])
                    algo_data['labels'].append(f"{dataset_name}..RS")
                
                if 'SORTED' in dataset_data:
                    algo_data['times'].append(dataset_data['SORTED'])
                    algo_data['labels'].append(f"{dataset_name}..S")
        
        return chart_data
      
    def create_performance_plot(self, chart_data):
        if not chart_data:
            return
        
        # Skip precomputed data for time unit conversions - always use fresh calculation
        # This ensures time unit conversions work properly
        
        # ALWAYS use fresh computation for accurate time unit conversion
        colors = list(mcolors.TABLEAU_COLORS.values())
        if len(chart_data) > len(colors):
            colors.extend(mcolors.CSS4_COLORS.values())
        
        # Use precomputed sorted labels if available, otherwise compute them
        if hasattr(self, 'precomputed_sorted_labels') and self.precomputed_sorted_labels:
            common_labels = self.precomputed_sorted_labels
            display_labels = getattr(self, 'precomputed_display_labels', [])
        else:
            # Fallback to original computation
            all_labels = []
            for algo_data in chart_data.values():
                all_labels.extend(algo_data['labels'])
            common_labels = list(set(all_labels))
            
            # Build dataset length mapping
            dataset_length_map = self.build_dataset_length_map(chart_data)
            
            # Sort labels by dataset length, then alphabetically, keeping states together
            def sort_key(label):
                dataset_part = label.split('..')[0]
                state_part = label.split('..')[1] if '..' in label else 'OG'
                dataset_length = dataset_length_map.get(dataset_part, 0)
                state_order = {'OG': 0, 'RD': 1, 'NS': 2, 'RS': 3, 'S': 4}
                state_priority = state_order.get(state_part, 999)
                return (dataset_length, dataset_part, state_priority)
            
            common_labels.sort(key=sort_key)
            self.precomputed_sorted_labels = common_labels
            
            # Create display labels showing lengths instead of filenames
            display_labels = []
            for label in common_labels:
                dataset_part = label.split('..')[0]
                state_part = label.split('..')[1] if '..' in label else 'OG'
                dataset_length = dataset_length_map.get(dataset_part, 0)
                display_label = f"{dataset_length}..{state_part}"
                display_labels.append(display_label)
            
            # Fallback if no labels found
            if not common_labels:
                for algo_data in chart_data.values():
                    if algo_data['labels']:
                        common_labels = algo_data['labels']
                        display_labels = common_labels  # Use original labels as display labels
                        break
        
        # Plot algorithms using fresh computation with converted time values
        for i, (algorithm, algo_data) in enumerate(chart_data.items()):
            if not algo_data['times'] or not algo_data['labels']:
                continue
                
            x_positions = []
            y_values = []
            
            for j, label in enumerate(common_labels):
                if label in algo_data['labels']:
                    idx = algo_data['labels'].index(label)
                    x_positions.append(j)
                    y_values.append(algo_data['times'][idx])  # These are already converted values
            
            if x_positions and y_values:
                color = colors[i % len(colors)]
                self.chart_ax.plot(x_positions, y_values, 
                                 marker='', linewidth=2, markersize=6,
                                 label=algorithm, color=color)
        
        # Set X-axis labels
        if common_labels and display_labels:
            self.chart_ax.set_xticks(range(len(common_labels)))
            self.chart_ax.set_xticklabels(display_labels, rotation=45, ha='right')
        
        # Common chart formatting (applies to both precomputed and fallback)
        self.chart_ax.set_title("Sorting Algorithm Performance Comparison", fontsize=14, fontweight='bold')
        self.chart_ax.set_xlabel("Dataset Length and State", fontsize=12)
        
        # Set Y-axis label based on current time unit
        time_unit = getattr(self, 'time_unit_combo', None)
        unit_text = time_unit.currentText() if time_unit else "Milliseconds"
        
        unit_label_map = {
            "Milliseconds": "milliseconds",
            "Seconds": "seconds", 
            "Minutes": "minutes",
            "Hours": "hours"
        }
        unit_label = unit_label_map.get(unit_text, "milliseconds")
        self.chart_ax.set_ylabel(f"Time ({unit_label})", fontsize=12)
        
        self.chart_ax.grid(True, alpha=0.3)
        
        if chart_data:
            self.chart_ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        scale_combo = getattr(self, 'scale_combo', None)
        scale_type = scale_combo.currentText() if scale_combo else "Linear"
        
        if scale_type == "Logarithmic":
            self.chart_ax.set_yscale('log')
        else:
            if chart_data:
                all_times = []
                for algo_data in chart_data.values():
                    all_times.extend(algo_data['times'])
                
                if all_times and scale_type == "Linear" and max(all_times) / min(all_times) > 1000:
                    self.chart_ax.set_yscale('log')
                    self.chart_ax.text(0.02, 0.98, 'Auto log scale applied (large range)', 
                                    transform=self.chart_ax.transAxes, fontsize=9, 
                                    verticalalignment='top', alpha=0.7,
                                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.3))
                else:
                    self.chart_ax.set_yscale('linear')
        
        # Force tight layout and canvas refresh
        self.chart_figure.tight_layout()
        self.chart_canvas.draw()
    
    def export_chart(self):
        if not self.benchmarking_completed:
            QMessageBox.information(self, "Export Chart", "No chart data available to export")
            return
            
        # Check if chart exists
        if self.chart_canvas is None or not hasattr(self, 'chart_figure') or self.chart_figure is None:
            QMessageBox.information(self, "Export Chart", "No chart data available to export")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Chart", "",
            "PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg);;All files (*.*)"
        )
        
        if filename:
            try:
                self.chart_figure.savefig(filename, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Export Successful", f"Chart exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export chart: {str(e)}")
    
    def update_table(self):
        if not self.benchmarking_completed or not hasattr(self, 'chart_data') or not self.chart_data:
            return
        
        processed_data = {}
        algorithms = set()
        
        for key, data in self.chart_data.items():
            algorithm = data['algorithm']
            dataset = data['dataset']
            state = data['state']
            time_secs = data['time']
            error = data['error']
            
            algorithms.add(algorithm)
            
            if algorithm not in processed_data:
                processed_data[algorithm] = {}
            if dataset not in processed_data[algorithm]:
                processed_data[algorithm][dataset] = {}
            
            if error or time_secs == "NA":
                processed_data[algorithm][dataset][state] = "Error"
            else:
                try:
                    processed_data[algorithm][dataset][state] = float(time_secs)
                except (ValueError, TypeError):
                    processed_data[algorithm][dataset][state] = "Error"
        
        table_data = {}
        dataset_states = set();
        
        for algorithm in processed_data:
            table_data[algorithm] = {}
            
            for dataset in processed_data[algorithm]:
                dataset_data = processed_data[algorithm][dataset]
                
                if 'ORIGINAL' in dataset_data:
                    state_key = f"{dataset}.ORIGINAL"
                    table_data[algorithm][state_key] = dataset_data['ORIGINAL']
                    dataset_states.add(state_key)
                
                random_times = []
                random_errors = []
                for state, value in dataset_data.items():
                    if state.startswith('RANDOM'):
                        if value == "Error":
                            random_errors.append(value)
                        elif isinstance(value, (int, float)):
                            random_times.append(value)
                
                if random_times or random_errors:
                    state_key = f"{dataset}.RANDOM"
                    if random_errors and not random_times:
                        table_data[algorithm][state_key] = "Error"
                    elif random_times:
                        avg_random = sum(random_times) / len(random_times)
                        table_data[algorithm][state_key] = avg_random
                    dataset_states.add(state_key)
                
                nearly_times = []
                nearly_errors = []
                for state, value in dataset_data.items():
                    if state.startswith('NEARLY SORTED'):
                        if value == "Error":
                            nearly_errors.append(value)
                        elif isinstance(value, (int, float)):
                            nearly_times.append(value)
                
                if nearly_times or nearly_errors:
                    state_key = f"{dataset}.NEARLY SORTED"
                    if nearly_errors and not nearly_times:
                        table_data[algorithm][state_key] = "Error"
                    elif nearly_times:
                        avg_nearly = sum(nearly_times) / len(nearly_times)
                        table_data[algorithm][state_key] = avg_nearly
                    dataset_states.add(state_key)
                
                for single_state in ['REVERSE SORTED', 'SORTED']:
                    if single_state in dataset_data:
                        state_key = f"{dataset}.{single_state}"
                        table_data[algorithm][state_key] = dataset_data[single_state]
                        dataset_states.add(state_key)
        
        algorithms = sorted(list(algorithms))
        dataset_states = list(dataset_states)
        
        self.table_headers = ["Dataset.State"] + algorithms
        self.results_table.setColumnCount(len(self.table_headers))
        self.results_table.setHorizontalHeaderLabels(self.table_headers)
        
        self.results_table.setRowCount(len(dataset_states))
        
        row_color_light = QColor(248, 248, 248)
        row_color_dark = QColor(238, 238, 238)
        
        for row, dataset_state in enumerate(dataset_states):
            row_bg_color = row_color_light if row % 2 == 0 else row_color_dark
            
            dataset_state_item = QTableWidgetItem(dataset_state)
            dataset_state_item.setFlags(dataset_state_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            dataset_state_item.setBackground(row_bg_color)
            self.results_table.setItem(row, 0, dataset_state_item)
            
            for col, algorithm in enumerate(algorithms, start=1):
                if algorithm in table_data and dataset_state in table_data[algorithm]:
                    value = table_data[algorithm][dataset_state]
                    
                    if value == "Error":
                        display_value = "Error"
                        cell_bg_color = QColor(255, 200, 200)
                    elif isinstance(value, (int, float)):
                        display_value = f"{value:.6f}"
                        cell_bg_color = row_bg_color
                    else:
                        display_value = "Error"
                        cell_bg_color = QColor(255, 200, 200)
                else:
                    display_value = "-"
                    cell_bg_color = QColor(220, 220, 220)
                
                time_item = QTableWidgetItem(display_value)
                time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                time_item.setBackground(cell_bg_color)
                
                self.results_table.setItem(row, col, time_item)
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)
        
        total_combinations = len(dataset_states) * len(algorithms)
        actual_data = sum(len(table_data.get(algo, {})) for algo in algorithms)
        self.table_info_label.setText(f"Table: {len(dataset_states)} dataset-state combinations × {len(algorithms)} algorithms ({actual_data} data points, averaged for multi-iteration states)")
        
        output_dir = getattr(self, 'current_output_dir', 'OUTPUTS')
        csv_path = os.path.join(output_dir, "RECORDS.csv")
        excel_path = os.path.join(output_dir, "REPORT.xlsx")
        
        if os.path.exists(csv_path):
            self.csv_path_label.setText(f"CSV Export: {csv_path}")
        if os.path.exists(excel_path):
            self.excel_path_label.setText(f"Excel Export: {excel_path}")
    
    def export_table(self):
        if not self.benchmarking_completed:
            QMessageBox.information(self, "Export Table", "No table data available to export")
            return
        
        filename, file_type = QFileDialog.getSaveFileName(
            self, "Export Table Data", "",
            "CSV files (*.csv);;Excel files (*.xlsx);;All files (*.*)"
        )
        
        if filename:
            try:
                if filename.endswith('.xlsx') or 'Excel' in file_type:
                    self.export_table_to_excel(filename)
                else:
                    self.export_table_to_csv(filename)
                QMessageBox.information(self, "Export Successful", f"Table exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export table: {str(e)}")
    
    def export_table_to_csv(self, filename):
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.table_headers)
            for row in range(self.results_table.rowCount()):
                row_data = []
                for col in range(self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)
    
    def export_table_to_excel(self, filename):
        import xlsxwriter
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet("Benchmark Results")
        
        header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3'})
        for col, header in enumerate(self.table_headers):
            worksheet.write(0, col, header, header_format)
        
        for row in range(self.results_table.rowCount()):
            for col in range(self.results_table.columnCount()):
                item = self.results_table.item(row, col)
                value = item.text() if item else ""
                worksheet.write(row + 1, col, value)
        
        for col in range(len(self.table_headers)):
            worksheet.set_column(col, col, 15)
        
        workbook.close()
    
    def autofit_table_columns(self):
        if not hasattr(self, 'results_table') or self.results_table.rowCount() == 0:
            return
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.results_table.resizeColumnsToContents()
        
        QApplication.processEvents()
        
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        if hasattr(self, 'table_info_label'):
            original_text = self.table_info_label.text()
            self.table_info_label.setText("Columns auto-fitted to content")
            
            def reset_text():
                if hasattr(self, 'table_info_label'):
                    self.table_info_label.setText(original_text)
            
            try:
                QTimer.singleShot(2000, reset_text)
            except Exception:
                self.table_info_label.setText(original_text)

    def commit_to_oracle_placeholder(self):
        QMessageBox.information(
            self, 
            "Oracle DB Integration", 
            "Oracle Database integration will be implemented in the next update (v2.0).\n\n"
            "This feature will allow you to:\n"
            "-> Connect to Oracle Database\n"
            "-> Create schema automatically\n"
            "-> Store benchmark results\n"
            "-> Query historical data\n\n"
            "Please stay tuned for this exciting feature!"
        )
    
    def toggle_logging(self):
        self.logging_active = False
        
        self.stop_button.setText("Logging Stopped")
        self.stop_button.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; font-weight: bold; }")
        self.stop_button.setToolTip("Console logging stopped for current session. Will restart with new benchmark.")
        self.stop_button.setEnabled(False)
        
        try:
            while True:
                self.output_queue.get_nowait()
        except queue.Empty:
            pass
        
        self.console.append("\n*** CONSOLE LOGGING STOPPED FOR CURRENT SESSION ***\nLogging will restart when you begin a new benchmark.\n")
    
    def remove_selected_custom_algorithms(self):
        """Remove all currently selected custom algorithms"""
        to_remove = []
        
        # Find custom algorithms that are selected
        for name, data in self.algo_vars.items():
            if data['checkbox'].isChecked():
                # Check if it's a custom algorithm (has context_label or not in default_sorts)
                is_default = any(name == default_name for default_name, _, _ in self.default_sorts)
                if not is_default:
                    to_remove.append(name)
        
        if not to_remove:
            QMessageBox.information(self, "No Selection", "No custom algorithms are currently selected.")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Are you sure you want to remove {len(to_remove)} selected custom algorithm(s)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self._remove_algorithms(to_remove)
            QMessageBox.information(self, "Removal Complete", f"Removed {len(to_remove)} custom algorithm(s).")

    def remove_all_custom_algorithms(self):
        """Remove all custom algorithms"""
        to_remove = []
        
        # Find all custom algorithms
        for name, data in self.algo_vars.items():
            is_default = any(name == default_name for default_name, _, _ in self.default_sorts)
            if not is_default:
                to_remove.append(name)
        
        if not to_remove:
            QMessageBox.information(self, "No Custom Algorithms", "No custom algorithms found to remove.")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Are you sure you want to remove all {len(to_remove)} custom algorithm(s)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self._remove_algorithms(to_remove)
            QMessageBox.information(self, "Removal Complete", f"Removed {len(to_remove)} custom algorithm(s).")

    def _remove_algorithms(self, algorithm_names):
        """Helper method to remove specified algorithms from the UI and data structures"""
        for name in algorithm_names:
            if name in self.algo_vars:
                # Find and remove the container widget from the layout
                checkbox = self.algo_vars[name]['checkbox']
                for i in range(self.algo_scroll_layout.count()):
                    item = self.algo_scroll_layout.itemAt(i)
                    if item and item.widget():
                        container = item.widget()
                        # Check if this container contains our checkbox
                        container_layout = container.layout()
                        if container_layout:
                            for j in range(container_layout.count()):
                                widget_item = container_layout.itemAt(j)
                                if widget_item and widget_item.widget() == checkbox:
                                    container.setParent(None)
                                    break
                
                # Remove from data structure
                del self.algo_vars[name]
        
        self.update_algo_count()

    def remove_selected_custom_datasets(self):
        """Remove all currently selected custom datasets"""
        to_remove = []
        
        # Find custom datasets that are selected
        for name, data in self.dataset_vars.items():
            if data['checkbox'].isChecked():
                # Check if it's a custom dataset (has 'path' key)
                if 'path' in data:
                    to_remove.append(name)
        
        if not to_remove:
            QMessageBox.information(self, "No Selection", "No custom datasets are currently selected.")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Are you sure you want to remove {len(to_remove)} selected custom dataset(s)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self._remove_datasets(to_remove)
            QMessageBox.information(self, "Removal Complete", f"Removed {len(to_remove)} custom dataset(s).")

    def remove_all_custom_datasets(self):
        """Remove all custom datasets"""
        to_remove = []
        
        # Find all custom datasets (those with 'path' key)
        for name, data in self.dataset_vars.items():
            if 'path' in data:
                to_remove.append(name)
        
        if not to_remove:
            QMessageBox.information(self, "No Custom Datasets", "No custom datasets found to remove.")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                   f"Are you sure you want to remove all {len(to_remove)} custom dataset(s)?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self._remove_datasets(to_remove)
            QMessageBox.information(self, "Removal Complete", f"Removed {len(to_remove)} custom dataset(s).")

    def _remove_datasets(self, dataset_names):
        """Helper method to remove specified datasets from the UI and data structures"""
        for name in dataset_names:
            if name in self.dataset_vars:
                # Find and remove the container widget from the layout
                checkbox = self.dataset_vars[name]['checkbox']
                for i in range(self.dataset_scroll_layout.count()):
                    item = self.dataset_scroll_layout.itemAt(i)
                    if item and item.widget():
                        container = item.widget()
                        # Check if this container contains our checkbox
                        container_layout = container.layout()
                        if container_layout:
                            for j in range(container_layout.count()):
                                widget_item = container_layout.itemAt(j)
                                if widget_item and widget_item.widget() == checkbox:
                                    container.setParent(None)
                                    break
                
                # Remove from data structure
                del self.dataset_vars[name]
        
        self.update_dataset_count()
    
    def open_algorithm_removal_dialog(self):
        """Open dialog to remove custom algorithms"""
        # Get custom algorithms only (not in default_sorts)
        custom_algos = {}
        for name, data in self.algo_vars.items():
            is_default = any(name == default_name for default_name, _, _ in self.default_sorts)
            if not is_default:
                custom_algos[name] = data
        
        if not custom_algos:
            QMessageBox.information(self, "No Custom Algorithms", "No custom algorithms found to remove.")
            return
        
        dialog = RemovalDialog(self, "Remove Custom Algorithms", custom_algos, "algorithm")
        dialog.exec()
    
    def open_dataset_removal_dialog(self):
        """Open dialog to remove custom datasets"""
        # Get custom datasets only (those with 'path' key)
        custom_datasets = {}
        for name, data in self.dataset_vars.items():
            if 'path' in data:
                custom_datasets[name] = data
        
        if not custom_datasets:
            QMessageBox.information(self, "No Custom Datasets", "No custom datasets found to remove.")
            return
        
        dialog = RemovalDialog(self, "Remove Custom Datasets", custom_datasets, "dataset")
        dialog.exec()
    
    def remove_single_algorithm(self, name):
        """Remove a single algorithm - used by individual remove buttons in the main list"""
        if name in self.algo_vars:
            reply = QMessageBox.question(self, "Confirm Removal", 
                                       f"Are you sure you want to remove the algorithm '{name}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self._remove_algorithms([name])
                QMessageBox.information(self, "Removal Complete", f"Removed algorithm '{name}'.")
    
    def remove_single_dataset(self, name):
        """Remove a single dataset - used by individual remove buttons in the main list"""
        if name in self.dataset_vars:
            reply = QMessageBox.question(self, "Confirm Removal", 
                                       f"Are you sure you want to remove the dataset '{name}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self._remove_datasets([name])
                QMessageBox.information(self, "Removal Complete", f"Removed dataset '{name}'.")

    def show_about_dialog(self):
        """Show the About dialog with application information"""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About SortBench")
        about_dialog.setFixedSize(700, 480)
        about_dialog.setModal(True)
        
        # Set icon for the dialog
        icon_path = os.path.join(os.path.dirname(__file__), "benchmark.ico")
        if os.path.exists(icon_path):
            about_dialog.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(about_dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Application icon and title
        title_layout = QHBoxLayout()
        
        # Icon (if available)
        if os.path.exists(icon_path):
            icon_label = QLabel()
            icon_pixmap = QIcon(icon_path).pixmap(64, 64)
            icon_label.setPixmap(icon_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(icon_label)
        
        # Title and version
        title_info = QVBoxLayout()
        app_name = QLabel("SortBench v1.1")
        app_name.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        app_name.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_info.addWidget(app_name)
        
        subtitle_label = QLabel("Sorting Benchmark Tool")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_info.addWidget(subtitle_label)
        
        title_layout.addLayout(title_info)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Description
        description = QLabel("This tool provides comprehensive benchmarking and comparison of sorting algorithms (intended for educational and research purposes). It includes multiple algorithm implementations with performance charts and tabulated data.")
        description.setFont(QFont("Arial", 10))
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Features
        features_text = """Key Features:
->  9 Built-in sorting algorithms (Bubble, Selection, Insertion, Merge, Quick, Heap, Count, Radix, Tim)
->  Custom sorting algorithm and dataset support
->  Multiple test states (Original, Random, Nearly-Sorted, Sorted, Reverse-Sorted)
->  Execution logs with export option (TXT, PDF)
->  Performance charts with export option (PNG)
->  Tabulated data with export option (CSV, Excel)
->  (Planned Future Update) Oracle DB integration to store algorithm details, dataset details, and performance data"""
        
        features_label = QLabel(features_text)
        features_label.setFont(QFont("Arial", 9))
        features_label.setWordWrap(True)
        layout.addWidget(features_label)
        
        # System Requirements
        requirements_text = """System Requirements:
->  Windows 10/11 (64-bit)
->  Minimum 4GB RAM (8GB recommended)
->  1GB free disk space"""
        
        requirements_label = QLabel(requirements_text)
        requirements_label.setFont(QFont("Arial", 9))
        requirements_label.setWordWrap(True)
        layout.addWidget(requirements_label)
        
        # Developer info
        developer_label = QLabel("Developed by Anurag Chattopadhyay")
        developer_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        developer_label.setWordWrap(True)
        developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(developer_label)
        
        about_dialog.exec()

    def show_help_dialog(self):
        """Show the Help dialog with comprehensive usage instructions"""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("SortBench Help Guide")
        help_dialog.setFixedSize(1000, 600)
        help_dialog.setModal(True)
        
        # Set icon for the dialog
        icon_path = os.path.join(os.path.dirname(__file__), "benchmark.ico")
        if os.path.exists(icon_path):
            help_dialog.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout(help_dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("SortBench Help Guide")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Help content in a scrollable text area
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFont(QFont("Arial", 10))
        
        help_content = """
<h3>Getting Started</h3>
<p><b>1. Select Algorithms:</b> Choose the sorting algorithms you want to benchmark from the "Select Algorithms" panel or add custom ones using the "Add/Remove Custom Algorithms" panel.<br>
<b>2. Select Datasets:</b> Choose datasets from the "Select Datasets" panel or add custom ones using the "Add/Remove Custom Datasets" panel.<br>
<b>3. Choose Test States:</b> Select which data arrangements to test (ORIGINAL, RANDOM, etc.).<br>
<b>4. Set Output Directory:</b> Choose where to save results.<br>
<b>5. Start Benchmarking:</b> Click "Start Benchmarking" to begin the process.</p>

<h3>Basic Usage Guide</h3>
<p><b>Configuration Tab:</b><br>
- Select Algorithms, Datasets, Test States, Add/Remove Custom Algorithm (Code files) and/or Custom Datasets<br>
- View algorithm code file contents using "View File" buttons<br>
- Configure maximum time per algorithm (in seconds, default: 300 seconds)<br>
- Set output directory for saving results</p>

<p><b>Execution Tab:</b><br>
- Console output shows benchmarking progress logs<br>
- Use Stop button to halt current benchmarking<br>
- Save console output to text or PDF files<br>
- Clear output to reset the console</p>

<p><b>Charts Tab:</b><br>
- View Performance chart after benchmarking completion<br>
- Configurable time units (milliseconds, seconds, minutes, hours)<br>
- Configurable Y-axis scaling options (Linear, Logarithmic)<br>
- Export charts as PNG images</p>

<p><b>Tables Tab:</b><br>
- Benchmark results (time in seconds)) in tabular format<br>
- Export to CSV or Excel formats<br>

<h3>Custom Datasets Guide</h3>
<p><b>About the dataset file:</b><br>
-> Must be a text (.txt) file<br>
-> Must contain single whitespace separated numeric values<br>
-> Accepts positive, negative, floating-point numbers, all types of rational numbers</p>

<p><b>Usage:</b><br>
-> Click "Browse Files" to select dataset files<br>
-> Click "Add Selected Datasets" to add the files to the list<br>
-> Use "Remove Custom Datasets" to remove previously added files</p>

<h3>Custom Algorithms Guide</h3>
<p><b>About the algorithm file:</b><br>
-> Must be a Python (.py) file [only Python code accepted]<br>
-> The main sorting function must accept 5 arguments: <i>arr (list), leftmark (int), rightmark (int), start (float), maxtime (float)</i> [in the same sequence]<br>
-> The tool will invoke function with leftmark as 0, and rightmark as last index (length - 1)<br>
-> Sorting must be <b>in-place</b> - tool does not expect return value<br>
-> For non in-place algorithms like merge sort, copy output to original input list at end</p>

<p><b>Maximum Time Limit Implementation:</b><br>
-> Import: <code>from timeit import default_timer</code><br>
-> Add this line as first line inside every loop in every function:<br>
&nbsp;&nbsp;&nbsp;<code>if default_timer() - start > maxtime: raise SystemError</code></p>

<p><b>Usage:</b><br>
-> Click "Browse" to select the algorithm code file<br>
-> Click "View File" to preview the file contents<br>
-> In "Function" field, write the exact main sorting function name (case-sensitive, without parentheses)<br>
-> In "Name" field, write a display name for your algorithm<br>
-> Click "Add Algorithm" to add the custom algorithm</p>

<h3>Test States Explained</h3>
<p>- <b>ORIGINAL:</b> Test data as-is from the file<br>
- <b>RANDOM:</b> Randomly shuffled data (configurable iterations) (MOST Recommended for general purpose)<br>
- <b>NEARLY SORTED:</b> Partially sorted data with very few unsorted elements (configurable iterations) (NOT Recommended for datasets with less than 30 elements)<br>
- <b>SORTED:</b> Fully sorted data in ascending order<br>
- <b>REVERSE SORTED:</b> Data sorted in descending order</p>

<h3>Tips & Best Practices</h3>
<p>- Use larger datasets (more than 1000 elements) for more accurate benchmarking<br>
- Use more iterations of RANDOM and NEARLY SORTED states for more accurate benchmarking<br>
- Ensure sufficient disk space in output directory before starting a benchmark<br>
- For custom algorithms, verify function name matches exactly (case-sensitive)<br>
- In the Execution tab, Console Output Log is way slower than the actual benchmarking in background (follow the top right corner status text). If you do not need the log output, once the Performance Chart tab is opened, go back to Execution tab and click on "Stop" button<br> 
- Very Large datasets (more than 100000) may take considerable time - adjust max time accordingly, and please be patient</p>
        """
        
        help_text.setHtml(help_content)
        
        # Use custom scrollbar for consistency
        help_scrollbar = EmojiScrollBar(Qt.Orientation.Vertical)
        help_text.setVerticalScrollBar(help_scrollbar)
        
        layout.addWidget(help_text)
        
        help_dialog.exec()


def main():
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("SortBench - Sorting Benchmark Application")
    app.setApplicationVersion("1.1")
    app.setOrganizationName("Developed by Anurag Chattopadhyay")
    app.setWindowIcon(QIcon("benchmark.ico"))
    
    window = SortingBenchmarkGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()