# -*- coding: utf-8 -*-

NAME = "深色模式"

# Color Palette based on user's image
# Main BG (Crust): #042326
# Panel BG (Base): #0A3A40
# Borders/UI (Surface): #0F5959
# Hover (Overlay): #1D7373
# Accent/Selection (Accent): #107361
# Main Text: #E0FBFC
# Sub Text: #89D9D9

STYLESHEET = """
    /* === 全局设置 === */
    QWidget {
        background-color: #0A3A40;
        color: #E0FBFC;
        font-family: "Microsoft YaHei UI", "Segoe UI";
        font-size: 13px;
        border: none;
    }

    /* === 主窗口框架 === */
    #MainFrame {
        background-color: #0A3A40;
        border: 1px solid #0F5959;
        border-radius: 8px;
    }

    /* === 滚动条 === */
    QScrollBar:vertical {
        background: #0A3A40;
        width: 10px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background: #0F5959;
        min-height: 25px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #1D7373;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background: #0A3A40;
        height: 10px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background: #0F5959;
        min-width: 25px;
        border-radius: 5px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #1D7373;
    }

    /* === Dock 面板与分割线 === */
    QDockWidget {
        border: 1px solid #0F5959;
        background-color: #0A3A40;
    }
    QDockWidget::title {
        background: #0F5959;
        padding: 6px;
        color: #E0FBFC;
        font-weight: bold;
        border-radius: 0px; /* Sharp corners */
        border-bottom: 1px solid #042326;
    }
    QMainWindow {
        background-color: #042326; /* Set the 'gap' color */
    }
    QMainWindow::separator, QSplitter::handle {
        background-color: #042326;
        width: 8px;
        height: 8px;
        border: none;
    }
    QMainWindow::separator:hover, QSplitter::handle:hover {
        background: #1D7373;
    }

    /* === 列表、树状控件 === */
    QListWidget, QTreeWidget {
        background-color: #0A3A40;
        border: none;
    }
    QTreeWidget::item {
        padding: 4px 0;
    }
    QTreeWidget::item:selected {
        background-color: #107361;
    }
    QTreeWidget::item:hover {
        background-color: #1D7373;
    }
    /* 隐藏分区面板的箭头 */
    PartitionTreeWidget::branch {
        border-image: none;
        image: none;
    }
    /* 筛选器面板标题 */
    FilterPanel QTreeWidget::item {
        color: #89D9D9; /* Sub-text color for headers */
        font-weight: bold;
    }


    /* === 表格 === */
    QTableWidget {
        background-color: #0A3A40;
        border: 1px solid #0F5959;
        border-radius: 6px;
        gridline-color: #0F5959;
    }
    QTableWidget::item {
        padding: 4px;
        border-bottom: 1px solid #0F5959; /* Row separator */
    }
    QTableWidget::item:selected {
        background-color: #107361;
        color: #FFFFFF;
    }
    /* 斑马纹 */
    QTableWidget[alternatingRowColors="true"]::item:alternate {
        background-color: #0F5959;
    }
    QHeaderView::section {
        background-color: #0F5959;
        color: #89D9D9;
        border: none;
        border-bottom: 1px solid #042326;
        padding: 6px;
    }
    QTableCornerButton::section {
        background-color: #0A3A40;
    }


    /* === 菜单 === */
    QMenu {
        background: #0F5959;
        border: 1px solid #1D7373;
        padding: 4px;
    }
    QMenu::item {
        padding: 6px 20px;
    }
    QMenu::item:selected {
        background: #1D7373;
    }

    /* === 输入框与文本框 (详情面板) === */
    QLabel#SectionTitle {
        color: #89D9D9;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    QTextEdit#PreviewBox, QLineEdit#NoteInput {
        background-color: #042326;
        border: 1px solid #0F5959;
        border-radius: 4px;
        padding: 6px;
    }
    QLineEdit#NoteInput {
        border: none;
        border-bottom: 2px solid #0F5959;
        border-radius: 0px;
    }
    QLineEdit#NoteInput:focus, QTextEdit#PreviewBox:focus {
        border-color: #1D7373;
    }
    QLabel#ImageBox {
        background-color: #042326;
        border: 1px solid #0F5959;
        border-radius: 4px;
    }

    /* === 标签组件 === */
    TagWidget {
        background-color: #0F5959;
        border: 1px solid #1D7373;
        border-radius: 10px;
        padding: 2px;
    }
    TagWidget > QLabel {
        color: #E0FBFC;
        font-size: 11px;
    }
    TagWidget > QPushButton {
        color: #89D9D9;
        border: none;
        border-radius: 8px;
        background-color: transparent;
        font-weight: bold;
        font-size: 12px;
    }
    TagWidget > QPushButton:hover {
        color: #FFFFFF;
        background-color: #107361;
    }

    /* === 按钮与底部栏 === */
    QPushButton {
        background-color: #0F5959;
        border: 1px solid #1D7373;
        border-radius: 4px;
        padding: 5px 10px;
    }
    QPushButton:hover {
        background-color: #1D7373;
    }
    /* 底部栏 */
    MainWindow > QWidget > QWidget > QFrame > QWidget {
       border-top: 1px solid #0F5959;
    }
"""