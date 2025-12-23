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
        background-color: #3c3c3c; /* 统一主框架背景 */
        border: 1px solid #202020;
        border-radius: 4px;
    }

    QDockWidget {
        background-color: #3c3c3c; /* 恢复主背景，让高亮背景与之更协调 */
        border: 1px solid #202020;
        border-radius: 4px;
    }
    
    /* 移除面板的 8px 强制 Margin，解决文字截断问题 */
    FilterPanel, PartitionPanel, TagPanel, DetailPanel {
        padding: 0px; 
        background-color: #3c3c3c;
        border: 1px solid #4f4f4f;
        border-radius: 6px;
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
    
    /* 分割线：核心修复版 (4px 手感 + 主题色) */
    QMainWindow::separator, QSplitter::handle {
        background-color: #202020; /* 还原主题深色，与背景融为一体但保留手感区 */
        width: 4px;
        height: 4px;
    }
    QMainWindow::separator:horizontal {
        width: 4px;
    }
    QMainWindow::separator:vertical {
        height: 4px;
    }
    QMainWindow::separator:hover, QSplitter::handle:hover {
        background: #4a4a4a; /* 柔和的悬停反馈 */
    }

    /* === 滚动条：最终修复版 === */
    QScrollBar:vertical {
        background-color: #2d2d2d; /* 强制指定背景色 */
        background-image: none;    /* 强制禁用背景图，杜绝网格 */
        width: 14px;
        margin: 0px;               /* 强制边距为0，杜绝缝隙 */
        border: none;              /* 强制无边框，杜绝缝隙 */
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #555555;
        min-height: 25px;
        border-radius: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background: #6a6a6a;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: #2d2d2d; /* 轨道背景 */
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
        border: none;
        background: none;
    }

    QScrollBar:horizontal {
        background-color: #2d2d2d; /* 强制指定背景色 */
        background-image: none;    /* 强制禁用背景图，杜绝网格 */
        height: 14px;
        margin: 0px;               /* 强制边距为0，杜绝缝隙 */
        border: none;              /* 强制无边框，杜绝缝隙 */
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
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: #2d2d2d; /* 轨道背景 */
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
        border: none;
        background: none;
    }

    /* === 滚动条角落（修复右下角白块） === */
    QAbstractScrollArea::corner {
        background: #2d2d2d;
        border: none;
        background-image: none; /* 确保无背景图 */
    }

    /* === 列表与树状控件 === */
    QListWidget, QTreeWidget, QTableWidget {
        background-color: #3c3c3c;
        border-bottom: 1px solid #202020; /* 仅保留底部横向线 */
        border-left: none;               /* 移除侧向重叠线，消除黑边 */
        border-right: none;
        border-radius: 4px;
        padding: 0px;
        alternate-background-color: #353535; /* 深灰斑马纹，无白色 */
        background-image: none; /* 确保无背景图 */
    }

    QTreeView {
        padding: 0px;
        margin: 0px;
        outline: none; /* 关键：彻底移除虚线焦点框 */
        show-decoration-selected: 1; 
    }
    
    QTreeWidget {
        indentation: 20px; /* 恢复缩进，确保层级清晰 */
    }

    QTreeWidget::item, QListWidget::item {
        padding-left: 4px; 
        padding-right: 4px;
        padding-top: 5px;
        padding-bottom: 5px;
        border-radius: 0px;
    }

    QTreeWidget::item:selected, QListWidget::item:selected {
        background-color: #555555;
    }
    QTreeWidget::item:hover, QListWidget::item:hover {
        background-color: #4a4a4a;
    }

    /* 中性层级箭头图标 */
    QTreeView::branch:has-children:closed:has-siblings,
    QTreeView::branch:has-children:closed {
        image: url(ui/icons/arrow_grey_right.png);
    }

    QTreeView::branch:has-children:open:has-siblings,
    QTreeView::branch:has-children:open {
        image: url(ui/icons/arrow_grey_down.png);
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
        padding: 4px 8px;
        border: none;
        border-bottom: 1px solid #202020;
        border-right: 1px solid #202020;
    }

    /* 垂直表头（行号）特殊处理 */
    QHeaderView::section:vertical {
        padding: 4px 0px; /* 上下4px, 左右0px */
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

    QTextEdit, QLineEdit {
        background-color: #2d2d2d;
        border: 1px solid #202020;
        border-radius: 4px;
        padding: 4px 6px; /* 减小内边距，释放文字空间 */
    }
    QLineEdit:focus, QTextEdit:focus {
        border-color: #555555;
    }

    /* 顶部工具栏搜索框：向上偏移 2px */
    #ToolbarSearchBar {
        padding: 3px 8px;
        margin-bottom: 2px;
    }
    
    /* === 标题栏 === */
    CustomTitleBar {
        background-color: #323232;
        border-bottom: 1px solid #202020;
    }

    #WindowTitle {
        background: transparent;
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

    #ToolBarButton, #WindowControlButton, #WindowCloseButton, #TagCloseButton {
        background-color: transparent;
        border: none;
        border-radius: 4px;
        padding: 0px; /* 强行置零小型按钮内边距，解决符号遮盖问题 */
    }
    #ToolBarButton:hover, #WindowControlButton:hover {
        background-color: #4a4a4a;
    }
    #WindowCloseButton:hover {
        background-color: #c84c4c;
    }

    #DisplayCountButton {
        padding: 3px 12px 3px 6px; /* 垂直内边距进一步从 5px 减至 3px */
        margin-bottom: 2px; /* 向上偏移 2px */
    }

    #DisplayCountButton::menu-indicator {
        image: none;
    }
    
    #SearchBarClearButton {
        background: transparent;
        border: none;
        padding: 0px;
        margin: 0px;
        color: #a0a0a0;
        font-size: 16px;
        font-weight: bold;
    }
    #SearchBarClearButton:hover {
        color: #d0d0d0;
    }

    /* === 预览对话框整体质感 (PreviewDialog) === */
    #PreviewContainer {
        background-color: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 8px;
    }
    
    #PreviewInfoLabel {
        color: #888888;
        font-family: Consolas, monospace;
        font-size: 12px;
    }
    
    #PreviewControls {
        background-color: rgba(30, 30, 30, 0.8);
        border-top: 1px solid #2a2a2a;
        border-bottom-left-radius: 8px;
        border-bottom-right-radius: 8px;
    }
    
    #PreviewControlButton {
        background-color: #333333;
        border: 1px solid #444444;
        border-radius: 4px;
        color: #a0a0a0;
        padding: 4px 12px;
        font-weight: bold;
    }
    
    #PreviewControlButton:hover {
        background-color: #444444;
        border-color: #666666;
        color: #ffffff;
    }
        
    /* 底部栏 */
    MainWindow > QWidget > QWidget > QFrame > QWidget > QWidget {
       border-top: 1px solid #202020;
    }

    /* === 消除一切脑残虚线框 (Focus Rect) === */
    * {
        outline: none;
    }
    QTreeWidget:focus, QListWidget:focus, QTableWidget:focus,
    QTreeWidget::item:focus, QListWidget::item:item:focus, QTableWidget::item:focus {
        outline: none;
        border: none;
    }

    /* === 预览窗口修复 === */
    #PreviewDialogCloseButton {
        background: transparent;
        color: #c8c8c8; /* 确保文字可见 */
        font-size: 20px;
        font-weight: bold;
        border: none;
        padding: 0; /* 移除继承的内边距 */
    }
    #PreviewDialogCloseButton:hover {
        background: #555555;
    }

    /* === 标题栏设置按钮修复 (使用属性选择器) === */
    /* 仅隐藏带有 class="no-arrow" 属性的 QToolButton 的下拉箭头 */
    QToolButton#ToolBarButton[class="no-arrow"]::menu-indicator {
        image: none;
    }

    /* 侧边栏自定义标题栏样式 (强制渲染背景) */
    CustomDockTitleBar, QWidget#CustomDockTitleBar {
        background-color: #323232;
        border-bottom: 1px solid #202020;
        border-top: 1px solid #4f4f4f; /* 增加顶部分割线，提升高级感 */
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    #customDockLabel {
        background: transparent;
        background-color: transparent;
        color: #a0a0a0;
        font-weight: bold;
        border: none;
        font-size: 14px;
    }

    #customDockMenuButton {
        background: transparent;
        background-color: transparent;
        border: none;
        color: #a0a0a0;
        font-size: 14px;
    }

    #customDockMenuButton:hover {
        background-color: #4a4a4a;
        border-radius: 4px;
        color: #d0d0d0;
    }

    /* === 标签组件精修 (TagWidget & TagChip) === */
    TagWidget, TagChip {
        background-color: #444444; /* 改为深碳灰，匹配整体暗黑主题 */
        border: 1px solid #555555;
        border-radius: 4px;
    }
    TagWidget:hover, TagChip:hover {
        background-color: #4f4f4f;
        border-color: #666666;
    }
    TagWidget QLabel, TagChip QLabel {
        color: #d0d0d0;
        font-size: 13px;
        font-weight: 500;
        background: transparent;
        padding: 0px 2px;
    }
    #TagCloseButton:hover {
        background-color: #e74c3c;
        color: white;
    }

    /* === 标签弹出层样式 (TagPopup) === */
    #TagPopupContainer {
        background-color: #2b2b2b;
        border: 1px solid #3f3f3f;
        border-top: 1px solid #4a4a4a; /* 微亮顶部边距，增加立体感 */
        border-radius: 6px;
    }
    
    #TagPopupHeader {
        color: #a0a0a0;
        font-weight: bold;
        padding-top: 4px;
        padding-bottom: 2px;
    }
    
    #TagPopupTip {
        color: #707070;
        font-size: 11px;
    }
    
    #TagPopupButton {
        background-color: #383838;
        border: 1px solid #454545;
        border-radius: 3px;
        color: #a0a0a0;
        padding: 5px 8px;
        text-align: left;
    }
    
    #TagPopupButton:hover {
        background-color: #4a4a4a;
        border-color: #606060;
    }
    
    #TagPopupButton:checked {
        background-color: #555555; /* 选中状态改为深灰高亮 */
        color: #ffffff;
        border-color: #707070;
    }

    #TagCreateButton {
        background-color: #27ae60;
        color: white;
        border-radius: 4px;
        padding: 6px;
        font-weight: bold;
    }
    #TagCreateButton:hover {
        background-color: #2ecc71;
    }

    /* === 详情面板内容展示增强 (3D 质感) === */
    #PreviewBox {
        background-color: #2b2b2b;
        border: 1px solid #3f3f3f;
        border-radius: 6px;
        padding: 8px;
    }

    #ImageBox {
        background-color: transparent;
        border: none;
    }
"""
