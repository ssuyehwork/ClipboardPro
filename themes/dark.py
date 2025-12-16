# -*- coding: utf-8 -*-

NAME = "专业深灰 (柔和版)"

STYLESHEET = """
    /* === 全局设置 === */
    QWidget {
        background-color: #3c3c3c;
        color: #c8c8c8;
        font-family: "Microsoft YaHei UI", "Segoe UI", system-ui, sans-serif;
        font-size: 14px;
        border: none;
    }

    /* === 主窗口与布局 === */
    QMainWindow {
        background-color: #2d2d2d;
    }
    
    #MainFrame {
        border: 1px solid #202020;
        border-radius: 4px;
    }

    QDockWidget {
        background-color: #3c3c3c;
        border-radius: 4px;
    }

    QDockWidget::title {
        background: #323232;
        padding: 8px 12px;
        color: #a0a0a0;
        font-weight: bold;
        border-top: 1px solid #4f4f4f;
        border-bottom: 1px solid #202020;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    /* 分割线 */
    QMainWindow::separator, QSplitter::handle {
        background-color: #2d2d2d;
        border: 1px solid #202020;
        width: 3px;
        height: 3px;
    }
    QMainWindow::separator:hover, QSplitter::handle:hover {
        background: #4a4a4a;
    }

    /* === 滚动条（强制纯色，禁止继承网格） === */
    QScrollBar:vertical {
        background: #2d2d2d;   /* 纯深灰，不透明 */
        width: 14px;
        margin: 1px;
        border: 1px solid #202020;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #555555;   /* 深灰 handle */
        min-height: 25px;
        border-radius: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background: #6a6a6a;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        border: none;
        background: none;
    }

    QScrollBar:horizontal {
        background: #2d2d2d;   /* 纯深灰，不透明 */
        height: 14px;
        margin: 1px;
        border: 1px solid #202020;
        border-radius: 3px;
    }
    QScrollBar::handle:horizontal {
        background: #555555;
        min-width: 25px;
        border-radius: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #6a6a6a;
    }

    /* === 列表与树状控件 === */
    QListWidget, QTreeWidget, QTableWidget {
        background-color: #3c3c3c;
        border: 1px solid #202020;
        border-radius: 4px;
        padding: 0px;
        alternate-background-color: #353535; /* 深灰斑马纹，无白色 */
    }

    /* 减少左侧缩进（让红色区域变窄） */
    QTreeWidget {
        indentation: 12px;
    }
    
    /* item 内部右移 4px（你要求的） */
    QTreeWidget::item, QListWidget::item {
        padding-left: 6px;  /* 原本 2px + 4px 扩展 */
        padding-right: 2px;
        padding-top: 2px;
        padding-bottom: 2px;
        border-radius: 3px;
    }

    QTreeWidget::item:selected, QListWidget::item:selected {
        background-color: #555555;
    }
    QTreeWidget::item:hover, QListWidget::item:hover {
        background-color: #4a4a4a;
    }

    PartitionTreeWidget::branch {
        border-image: none;
        image: none;
    }

    /* === 表格 === */
    QTableWidget {
        gridline-color: #4a4a4a;
        alternate-background-color: #353535;
    }
    QTableWidget::item {
        padding-left: 6px;
        padding-right: 2px;
        padding-top: 2px;
        padding-bottom: 2px;
        border-bottom: 1px solid #4a4a4a;
    }
    QTableWidget::item:selected {
        background-color: #555555;
        color: #d0d0d0; /* 亮灰，不是白色 */
    }

    QHeaderView::section {
        background-color: #323232;
        color: #a0a0a0;
        padding: 8px;
        border: none;
        border-bottom: 1px solid #202020;
        border-right: 1px solid #202020;
    }

    QTableCornerButton::section {
        background-color: #323232;
        border-bottom: 1px solid #202020;
        border-right: 1px solid #202020;
    }

    /* === 菜单 === */
    QMenu {
        background: #3c3c3c;
        border: 1px solid #202020;
        border-radius: 4px;
        padding: 5px;
    }
    QMenu::item {
        padding: 8px 24px;
        border-radius: 3px;
    }
    QMenu::item:selected {
        background: #555555;
    }
    QMenu::separator {
        height: 1px;
        background: #202020;
        margin: 4px 0;
    }

    /* === 输入框与文本框 === */
    QTextEdit, QLineEdit {
        background-color: #2d2d2d;
        border: 1px solid #202020;
        border-radius: 4px;
        padding: 8px;
    }
    QLineEdit:focus, QTextEdit:focus {
        border-color: #555555;
    }
    
    /* === 标题栏 === */
    CustomTitleBar {
        background-color: #323232;
        border-bottom: 1px solid #202020;
    }

    /* === 按钮 === */
    QPushButton {
        background-color: #4a4a4a;
        border: 1px solid #202020;
        border-radius: 4px;
        padding: 6px 14px;
    }
    QPushButton:hover {
        background-color: #555555;
        border-color: #3c3c3c;
    }
    QPushButton:pressed {
        background-color: #3c3c3c;
    }

    /* 标题栏 & 工具栏按钮特殊处理 */
    QToolButton {
        background-color: #4a4a4a;
        border: 1px solid #202020;
        border-radius: 4px;
        padding: 6px;
    }
    QToolButton:hover {
        background-color: #555555;
    }

    #ToolBarButton, #WindowControlButton, #WindowCloseButton {
        background-color: transparent;
        border: none;
        padding: 0;
        min-width: 0;
        border-radius: 4px;
    }
    #ToolBarButton:hover, #WindowControlButton:hover {
        background-color: #4a4a4a;
    }
    #WindowCloseButton:hover {
        background-color: #c84c4c;
    }
    
    /* 底部栏 */
    MainWindow > QWidget > QWidget > QFrame > QWidget > QWidget {
       border-top: 1px solid #202020;
    }

    /* === 去除所有虚线焦点框 === */
    *:focus {
        outline: none;
    }
    QTreeWidget::item:focus,
    QListWidget::item:focus,
    QTableWidget::item:focus {
        outline: none;
    }
"""
