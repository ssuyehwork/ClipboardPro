# -*- coding: utf-8 -*-

NAME = "浅色模式"

STYLESHEET = """
    /* 全局背景 */
    QWidget { background-color: #f5f5f7; color: #333333; font-family: "Microsoft YaHei UI", "Segoe UI"; font-size: 13px; }
    
    /* === 修复：面板之间的间距 (3像素) === */
    QMainWindow::separator {
        background-color: #f5f5f7;
        width: 3px;
        height: 3px;
    }
    QMainWindow::separator:hover {
        background-color: #007aff;
    }

    /* 表格整体 */
    QTableWidget, QListWidget, QTreeWidget { 
        background-color: #ffffff; 
        border: 1px solid #d1d1d6; 
        alternate-background-color: #f2f2f7; 
        gridline-color: #d1d1d6;
    }
    
    QTableCornerButton::section {
        background-color: #ffffff;
        border: 1px solid #d1d1d6;
    }
    
    /* === 修复：列标题高度缩小 === */
    QHeaderView { background-color: #ffffff; border: none; }
    QHeaderView::section { 
        background-color: #e5e5ea; 
        color: #333333; 
        border: none; 
        border-right: 1px solid #d1d1d6;
        border-bottom: 1px solid #d1d1d6;
        padding: 1px 4px;
        min-height: 24px;
    }

    /* 选中状态 */
    QTableWidget::item:selected, QTreeWidget::item:selected { 
        background-color: #e5f1ff; 
        color: #007aff; 
    }
    
    /* 输入框 */
    QLineEdit, QTextEdit { 
        background-color: #ffffff; 
        border: 1px solid #d1d1d6; 
        border-radius: 4px; 
        padding: 4px; 
        color: #333333; 
    }
    
    /* 按钮 */
    QPushButton { 
        background-color: #ffffff; 
        border: 1px solid #d1d1d6; 
        border-radius: 4px; 
        padding: 5px; 
        color: #333333; 
    }
    QPushButton:hover { 
        background-color: #e5e5ea; 
        border-color: #007aff; 
    }
    
    /* 滚动条 */
    QScrollBar:vertical { background: #f5f5f7; width: 12px; margin: 0; }
    QScrollBar::handle:vertical { background: #c7c7cc; min-height: 20px; border-radius: 6px; margin: 2px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    
    /* 菜单 */
    QMenu { background: #ffffff; border: 1px solid #d1d1d6; padding: 5px; }
    QMenu::item { padding: 5px 20px; color: #333333; }
    QMenu::item:selected { background: #e5f1ff; color: #007aff; }
"""