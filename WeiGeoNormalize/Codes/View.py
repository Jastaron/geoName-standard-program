from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QTextBrowser, QPushButton, \
    QLineEdit, QApplication, QTextEdit, QMessageBox, QAction
from PyQt5.QtGui import QColor


class SGNS_View(QMainWindow):
    # 信号
    standard_begin_signal = pyqtSignal(str)
    standard_data_addition_signal = pyqtSignal()
    select_file_signal = pyqtSignal()
    download_csv_signal = pyqtSignal(str)
    output_to_csv_signal = pyqtSignal(str)

    # 初始化函数，设计界面
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SGNS")
        self.setDarkTheme()
        # self.setStyleSheet("QLabel, QPushButton, QLineEdit, QTextBrowser, QTextEdit, QAction { font-size: 24px; }")
        self.setGeometry(500, 300, 1280, 960)

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("文件")
        self.open_file_act = QAction("打开文件", self)
        self.open_file_act.triggered.connect(self.select_file_signal.emit)
        self.add_standard_act = QAction("添加标准数据", self)
        self.add_standard_act.triggered.connect(self.standard_data_addition_signal.emit)
        self.output_file_act = QAction("结果输出为..", self)
        self.output_file_act.triggered.connect(self.output_to_csv)

        self.file_menu.addAction(self.open_file_act)
        self.file_menu.addAction(self.add_standard_act)
        self.file_menu.addAction(self.output_file_act)

        # 输入
        self.search_input_layout = QVBoxLayout()
        self.search_option_layout = QHBoxLayout()
        self.search_label = QLabel("待标准化地名输入:")
        self.search_option_layout.addWidget(self.search_label)
        self.clear_btn = QPushButton("清除输入")
        self.clear_btn.setFixedSize(300, 50)
        self.clear_btn.clicked.connect(self.clear_input)
        self.search_option_layout.addWidget(self.clear_btn)

        self.search_input = QTextEdit()

        self.search_input_layout.addLayout(self.search_option_layout)
        self.search_input_layout.addWidget(self.search_input)

        # 输出结果
        self.standard_result_layout = QVBoxLayout()
        self.standard_result_option_layout = QHBoxLayout()
        self.output_label = QLabel("标准化结果输出:")
        self.search_btn = QPushButton("开始标准化")
        self.search_btn.setFixedSize(300,50)
        self.search_btn.clicked.connect(self.start_standard)
        self.standard_result = QTextBrowser()
        self.standard_result_option_layout.addWidget(self.output_label)
        self.standard_result_option_layout.addWidget(self.search_btn)
        self.standard_result_layout.addLayout(self.standard_result_option_layout)
        self.standard_result_layout.addWidget(self.standard_result)

        # 主界面
        self.main_layout.addLayout(self.search_input_layout)
        self.main_layout.addLayout(self.standard_result_layout)
        self.main_widget.setLayout(self.main_layout)

        # Set the main widget as central widget
        self.setCentralWidget(self.main_widget)

        # Connect buttons to appropriate functions

    def setDarkTheme(self):
        # Set dark theme colors
        dark_background_color = "#222"
        dark_menu_color = '#333'
        dark_text_color = "white"
        dark_menu_selected_color = "#777"
        dark_menu_item_padding = "5px 20px"
        dark_button_color = "#555"
        dark_button_text_color = "white"
        dark_button_hover_color = "#666"
        dark_text_edit_color = "#333"
        dark_text_edit_text_color = "white"
        dark_browser_color = "#333"

        # Apply dark theme styles
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {dark_background_color};
            }}
            QLabel, QPushButton, QLineEdit, QTextBrowser, QTextEdit, QAction {{
                font-size: 24px;
                color: {dark_text_color};
            }}
            QMenuBar {{
                background-color: {dark_menu_color};
                color: {dark_text_color};
            }}
            QMessageBox {{
                background-color: {dark_menu_color};
                color: {dark_text_color};
            }}
            QMenuBar::item {{
                spacing: 3px;
                padding: 5px 10px;
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {dark_menu_selected_color};
            }}
            QMenu {{
                background-color: {dark_menu_item_padding};
                border: 1px solid black;
            }}
            QMenu::item {{
                padding: {dark_menu_item_padding};
            }}
            QMenu::item:selected {{
                background-color: {dark_menu_selected_color};
            }}
            QPushButton {{
                background-color: {dark_button_color};
                color: {dark_button_text_color};
                min-width: 30px;  /* Set the desired minimum width */
                min-height: 10px;  /* Set the desired minimum height */
            }}
            QPushButton:hover {{
                background-color: {dark_button_hover_color};
            }}
            QTextEdit {{
                background-color: {dark_text_edit_color};
                color: {dark_text_edit_text_color};
            }}
            QTextBrowser {{
                background-color: {dark_browser_color};
                color: {dark_text_color};
            }}
        """)


    def display_input(self, input_str):
        self.search_input.clear()
        self.search_input.append(input_str)
    def display_result(self, result):
        self.standard_result.clear()
        self.standard_result.append(result)

    def output_to_csv(self):
        output_str = self.standard_result.toPlainText()
        if output_str == '':
            return self.display_output_nothing_error()
        self.output_to_csv_signal.emit(output_str)

    def start_standard(self):
        input_str = self.search_input.toPlainText()
        if input_str == '':
            return
        self.standard_begin_signal.emit(input_str)

    def clear_input(self):
        self.search_input.clear()
        self.standard_result.clear()

    # 展示登录错误
    def display_select_file_error(self):
        QMessageBox.critical(self, "Error", "软件只支持csv或txt文件\n请重试...")

    def display_output_nothing_error(self):
        QMessageBox.critical(self, "Error", "您还未输出标准化结果\n请重试...")
