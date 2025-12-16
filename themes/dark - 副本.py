# -*- coding: utf-8 -*-

NAME = "极简深色"

# === 8色极简调色板 ===
# 1. 边框 (BORDER_COLOR): black
# 2. 主背景 (MAIN_BG_COLOR): #1e1e2e (近黑的深灰)
# 3. 面板背景 (PANEL_BG_COLOR): #313244 (深石板灰)
# 4. 主文本 (PRIMARY_TEXT_COLOR): #cdd6f4 (淡薰衣草色)
# 5. 次要文本 (SECONDARY_TEXT_COLOR): #a6adc8 (石板灰)
# 6. 强调/选中 (ACCENT_COLOR): #89b4fa (天蓝色)
# 7. 悬停 (HOVER_COLOR): #45475a (深灰色)
# 8. 警告/特殊 (WARNING_COLOR): #f38ba8 (粉红色)

STYLESHEET = """
    /* === 全局默认 === */
    * {
        font-family: "Microsoft YaHei UI", "Segoe UI";
        font-size: 13px;
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        background-color: #313244; /* PANEL_BG_COLOR */
        border: 2px solid black; /* BORDER_COLOR */
        border-radius: 0px;
    }

    /* === 窗口与框架 === */
    QMainWindow, #MainFrame {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        border: none;
    }
    
    QWidget {
        border: none; /* 覆盖默认边框，只在需要时添加 */
        background-color: #313244;
    }

    /* === 标题栏与Dock标题 === */
    CustomTitleBar, QDockWidget::title {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        font-weight: bold;
        padding: 6px;
        border: 2px solid black;
    }

    /* === 分割线 === */
    QMainWindow::separator, QSplitter::handle {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        width: 8px;
        height: 8px;
        border: none;
    }
    QMainWindow::separator:hover, QSplitter::handle:hover {
        background: #45475a; /* HOVER_COLOR */
    }

    /* === 滚动条 === */
    QScrollBar {
        background: #1e1e2e; /* MAIN_BG_COLOR */
        width: 12px;
        height: 12px;
        margin: 0;
        border: none;
    }
    QScrollBar::handle {
        background: #45475a; /* HOVER_COLOR */
        min-height: 25px;
        min-width: 25px;
        border: none; /* 移除边框 */
    }
    QScrollBar::handle:hover {
        background: #a6adc8; /* SECONDARY_TEXT_COLOR */
    }
    QScrollBar::add-line, QScrollBar::sub-line {
        height: 0;
        width: 0;
    }

    /* === 列表、树、表 === */
    QListWidget, QTreeWidget, QTableWidget {
        background-color: #313244; /* PANEL_BG_COLOR */
        border: 2px solid black;
        gridline-color: black;
    }
    QListWidget::item, QTreeWidget::item, QTableWidget::item {
        padding: 5px;
        border: none; /* 移除项目自身的边框 */
        border-bottom: 2px solid black; /* 用底部边框作为行分隔符 */
    }
    QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
        background-color: #89b4fa; /* ACCENT_COLOR */
        color: #1e1e2e; /* 在亮背景上用深色文本 */
    }
    QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {
        background-color: #45475a; /* HOVER_COLOR */
    }

    /* === 表头 === */
    QHeaderView::section {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        font-weight: bold;
        padding: 6px;
        border: 2px solid black;
    }
    QTableCornerButton::section {
        background-color: #1e1e2e;
    }

    /* === 输入框、文本框、标签 === */
    QLineEdit, QTextEdit, QLabel {
        background-color: #1e1e2e; /* MAIN_BG_COLOR for inputs */
        border: 2px solid black;
        padding: 5px;
    }
    
    /* 标签/标题等不需要背景的元素 */
    QLabel, #StatusLabel, #PageLabel, #PartitionInfoLabel, #EmptyTagLabel {
        background-color: transparent;
        border: none;
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
    }
    
    QLabel#SectionTitle, #PageLabel {
        font-weight: bold;
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
    }

    /* === 按钮 === */
    QPushButton {
        background-color: #45475a; /* HOVER_COLOR */
        border: 2px solid black;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #a6adc8; /* SECONDARY_TEXT_COLOR */
        color: #1e1e2e;
    }
    QPushButton:pressed {
        background-color: #89b4fa; /* ACCENT_COLOR */
    }
    
    /* === 特殊控件 === */
    /* 分区面板加粗项 */
    #PartitionTree::item[accessibleName="partition-tree-bold-item"] {
        font-weight: bold;
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
    }
    
    /* 隐藏分区面板箭头 */
    #PartitionTree::branch {
        image: none;
    }

    /* 标签组件 */
    TagWidget {
        background-color: #45475a; /* HOVER_COLOR */
        border: 2px solid black;
        padding: 2px;
    }

    /* === 标签输入组件 (widget_tag_input.py) === */
    #TagInputWidget {
        background-color: #313244; /* PANEL_BG_COLOR */
        border: 2px solid black;
    }
    #TagInputWidget:focus-within {
        border: 2px solid #89b4fa; /* ACCENT_COLOR */
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
    }
    #TagInputWidget > #ChipsContainer {
        background: transparent;
        border: none;
    }
    #TagInputWidget > QLineEdit {
        background: transparent;
        border: none;
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        padding: 4px 2px;
    }

    /* 标签胶囊 (TagChip) */
    TagChip {
        background-color: #89b4fa; /* ACCENT_COLOR */
        border: none; /* No extra border */
    }
    TagChip > QLabel {
        color: #1e1e2e; /* Dark text on bright background */
        border: none;
        padding: 0 4px;
        font-weight: bold;
    }
    TagChip > QPushButton {
        border: none;
        color: #1e1e2e;
        font-weight: bold;
        background: transparent;
    }
    TagChip > QPushButton:hover {
        color: #f38ba8; /* WARNING_COLOR */
    }
    TagWidget > QLabel {
        background: transparent;
        border: none;
    }

    /* 菜单 */
    QMenu {
        background-color: #313244; /* PANEL_BG_COLOR */
        border: 2px solid black;
        padding: 4px;
    }
    QMenu::item:selected {
        background-color: #89b4fa; /* ACCENT_COLOR */
        color: #1e1e2e;
    }

    /* === 标签选择弹窗 === */
    #TagPopupContainer {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        border: 2px solid black;
    }
    #TagCreateButton {
        background-color: #313244; /* PANEL_BG_COLOR */
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        border: 2px solid black;
        padding: 10px;
        text-align: left;
        font-weight: bold;
    }
    #TagCreateButton:hover {
        background-color: #45475a; /* HOVER_COLOR */
    }
    #TagPopupButton {
        background-color: #313244; /* PANEL_BG_COLOR */
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        border: 2px solid black;
        padding: 6px;
        text-align: left;
    }
    #TagPopupButton:hover {
        background-color: #45475a; /* HOVER_COLOR */
    }
    #TagPopupButton:checked {
        background-color: #89b4fa; /* ACCENT_COLOR */
        color: #1e1e2e; /* Darker text on bright background */
        font-weight: bold;
    }
    #TagPopupHeader {
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
        font-weight: bold;
        padding-left: 4px;
    }
    #TagPopupTip {
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
        font-size: 10px;
        padding: 4px;
        border-top: 2px solid black;
    }

    /* === 标题栏组件 (components.py) === */
    #FilterTree {
        border: 2px solid black;
    }

    #SearchBarClearButton {
        background: transparent;
        border: none;
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
        font-weight: bold;
        font-size: 14px;
    }
    #SearchBarClearButton:hover {
        color: #f38ba8; /* WARNING_COLOR */
    }

    #WindowTitle {
        font-weight: bold;
        font-size: 14px;
        border: none;
        background: transparent;
    }

    #ClearSearchButton {
        background: transparent;
        border: none;
        font-size: 14px;
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
    }
    #ClearSearchButton:hover {
        background: #45475a; /* HOVER_COLOR */
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
    }

    #DisplayCountButton {
        border: 2px solid black;
        padding: 4px 8px;
    }
    #DisplayCountButton::menu-indicator {
        image: none; /* 隐藏默认箭头 */
    }

    #ToolBarButton {
        background: transparent;
        border: none;
        font-size: 16px;
    }
    #ToolBarButton:hover {
        background: #45475a; /* HOVER_COLOR */
    }
    #ToolBarButton:checked {
        background: #89b4fa; /* ACCENT_COLOR */
        color: #1e1e2e;
    }

    #TitleBarSeparator {
        color: black;
    }

    #WindowControlButton, #WindowCloseButton {
        background: transparent;
        border: none;
        font-size: 14px;
    }
    #WindowControlButton:hover {
        background: #45475a; /* HOVER_COLOR */
    }
    #WindowCloseButton:hover {
        background: #f38ba8; /* WARNING_COLOR */
    }

    /* === 预览对话框 (dialog_preview.py) === */
    #PreviewContainer {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        border: 2px solid black;
    }

    #PreviewInfoLabel {
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
        background: transparent;
        border: none;
    }

    #PreviewCloseButton {
        color: #a6adc8; /* SECONDARY_TEXT_COLOR */
        border: none;
        background: transparent;
        font-size: 24px;
        font-weight: bold;
    }
    #PreviewCloseButton:hover {
        color: #f38ba8; /* WARNING_COLOR */
    }

    #PreviewTextEdit {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        border: none;
        font-family: Consolas, monospace;
        font-size: 14px;
        padding: 15px;
    }

    #PreviewControls {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
        border-top: 2px solid black;
    }
    #PreviewControlButton {
        background: transparent;
        border: 2px solid black;
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        min-width: 30px;
        min-height: 24px;
        font-size: 14px;
        margin: 0 4px;
    }
    #PreviewControlButton:hover {
        background: #45475a; /* HOVER_COLOR */
    }
    #PreviewControlButton:pressed {
        background: #89b4fa; /* ACCENT_COLOR */
    }

    /* === 标签面板 (panel_tags.py) === */
    #TagPanel {
        background: transparent;
        border: none;
    }

    /* === 标签组件 (tag_widget.py) === */
    TagWidget {
        background-color: #45475a; /* HOVER_COLOR */
        border: 2px solid black;
        padding: 2px;
    }
    TagWidget > QLabel {
        color: #89b4fa; /* ACCENT_COLOR */
        border: none;
        background-color: transparent;
        font-size: 11px;
        padding: 1px 0px;
    }
    TagWidget > QPushButton {
        color: #cdd6f4; /* PRIMARY_TEXT_COLOR */
        border: none;
        background-color: transparent;
        font-weight: bold;
        font-size: 12px;
    }
    TagWidget > QPushButton:hover {
        color: #1e1e2e; /* MAIN_BG_COLOR */
        background-color: #f38ba8; /* WARNING_COLOR */
    }

    /* === 颜色选择对话框 (dialogs.py) === */
    #ColorDialogButton {
        border: 2px solid black;
    }
    #ColorDialogButton[color="#f38ba8"] { background-color: #f38ba8; }
    #ColorDialogButton[color="#f9e2af"] { background-color: #f9e2af; }
    #ColorDialogButton[color="#a6e3a1"] { background-color: #a6e3a1; }
    #ColorDialogButton[color="#89b4fa"] { background-color: #89b4fa; }
    #ColorDialogButton[color="#cba6f7"] { background-color: #cba6f7; }

    /* === 颜色选择器 (color_selector.py) === */
    QDialog#ColorSelectorDialog {
        background-color: #1e1e2e; /* MAIN_BG_COLOR */
    }
    QDialog#ColorSelectorDialog QLabel {
        font-weight: bold;
        margin-top: 10px;
    }

    #ColorPreviewButton {
        border: 2px solid black;
    }
    #ColorPickButton, #CancelButton {
        background-color: #45475a; /* HOVER_COLOR */
    }
    #ClearColorButton {
        background-color: #45475a;
        color: #f38ba8; /* WARNING_COLOR */
    }
    #OkButton {
        background-color: #89b4fa; /* ACCENT_COLOR */
        color: #1e1e2e;
    }
    
    #ColorSelectorButton {
        border: 2px solid black;
    }
    #ColorSelectorButton[color="#ffadad"] { background-color: #ffadad; }
    #ColorSelectorButton[color="#ffd6a5"] { background-color: #ffd6a5; }
    #ColorSelectorButton[color="#fdffb6"] { background-color: #fdffb6; }
    #ColorSelectorButton[color="#caffbf"] { background-color: #caffbf; }
    #ColorSelectorButton[color="#9bf6ff"] { background-color: #9bf6ff; }
    #ColorSelectorButton[color="#a0c4ff"] { background-color: #a0c4ff; }
    #ColorSelectorButton[color="#bdb2ff"] { background-color: #bdb2ff; }
    #ColorSelectorButton[color="#ffc6ff"] { background-color: #ffc6ff; }
    #ColorSelectorButton[color="#ef476f"] { background-color: #ef476f; }
    #ColorSelectorButton[color="#ffd166"] { background-color: #ffd166; }
    #ColorSelectorButton[color="#06d6a0"] { background-color: #06d6a0; }
    #ColorSelectorButton[color="#118ab2"] { background-color: #118ab2; }
    #ColorSelectorButton[color="#073b4c"] { background-color: #073b4c; }
    #ColorSelectorButton[color="#f72585"] { background-color: #f72585; }
    #ColorSelectorButton[color="#7209b7"] { background-color: #7209b7; }
    #ColorSelectorButton[color="#3a0ca3"] { background-color: #3a0ca3; }
    #ColorSelectorButton[color="#ffffff"] { background-color: #ffffff; }
    #ColorSelectorButton[color="#000000"] { background-color: #000000; }
    #ColorSelectorButton[color="#808080"] { background-color: #808080; }
"""
