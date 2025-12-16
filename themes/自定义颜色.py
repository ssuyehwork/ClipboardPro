import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QListWidget, QDockWidget,
    QHeaderView, QTableWidget, QTableWidgetItem
)

# --- 1. 集中定义和自定义颜色变量 ---
# 只需修改这里的十六进制颜色值即可
COLOR_SCHEME = {
    # 基础颜色和边框
    "BORDER_COLOR": "#000000",        # 1. 边框色 (black)
    "MAIN_BG_COLOR": "#1e1e2e",       # 2. 主背景色 (近黑的深灰)
    "PANEL_BG_COLOR": "#313244",      # 3. 面板背景色 (深石板灰)

    # 文本颜色
    "PRIMARY_TEXT_COLOR": "#cdd6f4",  # 4. 主文本色 (淡薰衣草色)
    "SECONDARY_TEXT_COLOR": "#a6adc8",# 5. 次要文本色 (石板灰)

    # 交互/反馈颜色
    "ACCENT_COLOR": "#89b4fa",        # 6. 强调/选中色 (天蓝色)
    "HOVER_COLOR": "#45475a",         # 7. 悬停色 (深灰色)
    "WARNING_COLOR": "#f38ba8",        # 8. 警告/特殊色 (粉红色)

    # 尺寸（保持固定，如果您不需要修改边框大小）
    "BORDER_WIDTH": "2px",
    "BORDER_RADIUS": "4px",
}

# --- 2. 构建 QSS 样式表字符串 (无需修改) ---
def get_stylesheet(colors: dict) -> str:
    """根据颜色字典生成完整的 Qt Style Sheet 字符串"""

    # 此处使用 f-string 自动将上面的颜色值应用到对应的 QSS 属性
    qss = f"""
        /* --- 全局背景和默认颜色 --- */
        QMainWindow, #MainFrame {{
            background-color: {colors["MAIN_BG_COLOR"]};
        }}
        * {{
            color: {colors["PRIMARY_TEXT_COLOR"]};
            background-color: {colors["PANEL_BG_COLOR"]};
            font-size: 14px;
        }}

        /* --- 边框和轮廓 --- */
        QDockWidget, QListWidget, QTreeWidget, QTableWidget, QLineEdit, QTextEdit, QPushButton, QHeaderView {{
            border: {colors["BORDER_WIDTH"]} solid {colors["BORDER_COLOR"]};
            border-radius: {colors["BORDER_RADIUS"]};
        }}
        QTableWidget {{
            gridline-color: {colors["BORDER_COLOR"]}; /* 表格网格线 */
        }}

        /* --- 列表/树/表格的交互状态 --- */
        QListWidget, QTreeWidget, QTableWidget {{
            background-color: {colors["PANEL_BG_COLOR"]};
        }}
        QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {{
            background-color: {colors["HOVER_COLOR"]};
        }}
        QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {{
            background-color: {colors["ACCENT_COLOR"]};
            color: {colors["MAIN_BG_COLOR"]}; /* 选中时文字颜色与背景色互补 */
        }}

        /* --- 输入框 (QLineEdit/QTextEdit) --- */
        QLineEdit, QTextEdit {{
            background-color: {colors["MAIN_BG_COLOR"]}; /* 输入区域背景 */
            padding: 4px;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border: {colors["BORDER_WIDTH"]} solid {colors["ACCENT_COLOR"]}; /* 焦点边框 */
        }}

        /* --- 按钮 (QPushButton) --- */
        QPushButton {{
            background-color: {colors["HOVER_COLOR"]};
            padding: 5px 15px;
            min-height: 25px;
        }}
        QPushButton:hover {{
            background-color: {colors["ACCENT_COLOR"]};
        }}
        
        /* 强调/OK 按钮 */
        QPushButton#OkButton {{
            background-color: {colors["ACCENT_COLOR"]};
            color: {colors["MAIN_BG_COLOR"]};
        }}
        
        /* 警告/删除按钮 */
        QPushButton#ClearColorButton {{
            color: {colors["WARNING_COLOR"]};
            background-color: {colors["PANEL_BG_COLOR"]};
            border: none;
        }}
        
        /* --- 文本 (QLabel) --- */
        QLabel {{
            color: {colors["SECONDARY_TEXT_COLOR"]}; /* 大部分 QLabel 使用次要文本色 */
        }}
        QLabel#TitleLabel {{
            color: {colors["PRIMARY_TEXT_COLOR"]};
            font-weight: bold;
        }}
        /* 模拟 Tag Chip */
        QLabel#TagChip {{ 
            background-color: {colors["ACCENT_COLOR"]}; 
            color: {colors["MAIN_BG_COLOR"]}; 
            border-radius: 12px; 
            padding: 5px; 
        }}
    """
    return qss

# --- 3. 示例应用主窗口 (无需修改) ---
class MainWindow(QMainWindow):
    def __init__(self, style_sheet):
        super().__init__()
        self.setWindowTitle("自定义颜色主题示例")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(style_sheet)

        central_widget = QWidget()
        central_widget.setObjectName("MainFrame")
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # 列表面板
        dock_list = QDockWidget("列表 (选中/悬停色)", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock_list)
        list_widget = QListWidget()
        for i in range(5):
            list_widget.addItem(f"列表项 {i+1}")
        list_widget.item(1).setSelected(True) 
        dock_list.setWidget(list_widget)
        
        # 输入和按钮面板
        dock_input = QDockWidget("输入与按钮", self)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_input)
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        input_layout.addWidget(QLabel("主文本色标题", objectName="TitleLabel"))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("输入框 (MAIN_BG_COLOR)")
        input_layout.addWidget(line_edit)
        
        input_layout.addWidget(QPushButton("普通按钮 (HOVER_COLOR)"))
        input_layout.addWidget(QPushButton("确定按钮 (ACCENT_COLOR)", objectName="OkButton"))
        input_layout.addWidget(QPushButton("清除 (WARNING_COLOR)", objectName="ClearColorButton"))
        
        tag_label = QLabel("标签 (Tag Chip 模拟)", objectName="TagChip")
        input_layout.addWidget(tag_label)
        input_layout.addStretch()
        dock_input.setWidget(input_widget)

        # 表格面板
        dock_table = QDockWidget("表格", self)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock_table)
        table_widget = QTableWidget(4, 3)
        table_widget.setHorizontalHeaderLabels(["名称", "值 A", "值 B"])
        table_widget.setItem(0, 0, QTableWidgetItem("表格项 1"))
        table_widget.selectRow(1)
        dock_table.setWidget(table_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # ---------------------------------------------
    # **您的调整区域**
    # 尝试将主题改为亮色模式 (例如，所有背景变为白色/浅灰色)
    # COLOR_SCHEME["MAIN_BG_COLOR"] = "#f5f5f5" 
    # COLOR_SCHEME["PANEL_BG_COLOR"] = "#ffffff"
    # COLOR_SCHEME["PRIMARY_TEXT_COLOR"] = "#333333"
    # COLOR_SCHEME["ACCENT_COLOR"] = "#0078d4" # 微软蓝
    # ---------------------------------------------

    style_sheet = get_stylesheet(COLOR_SCHEME)
    window = MainWindow(style_sheet)
    window.show()
    
    sys.exit(app.exec())