# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListWidget, QLineEdit,
                             QListWidgetItem, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QStyle, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QPoint

# 假设 data.database 在项目的 python-path 中
from data.database import DBManager

DARK_STYLESHEET = """
QWidget {
    background-color: #2E2E2E;
    color: #F0F0F0;
    font-family: "Microsoft YaHei";
    font-size: 14px;
}

QListWidget, QTreeWidget {
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px;
}

QListWidget::item, QTreeWidget::item {
    padding: 8px;
    outline: none; /* 移除虚线焦点框 */
}

QListWidget::item:selected, QTreeWidget::item:selected {
    background-color: #555555;
    color: #FFFFFF;
}

QLineEdit {
    background-color: #3C3C3C;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px;
    font-size: 16px;
}

/* --- 自定义标题栏样式 --- */
CustomTitleBar {
    background-color: #3C3C3C; /* 标题栏背景色 */
    height: 30px;
}

CustomTitleBar QPushButton {
    background-color: transparent;
    border: none;
    width: 25px;
    height: 25px;
    padding: 5px;
}

CustomTitleBar QPushButton:hover {
    background-color: #555555;
    border-radius: 4px;
}
"""

class CustomTitleBar(QWidget):
    """自定义标题栏，支持拖动和自定义按钮。"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 0, 5, 0) # 左右留边距，上下无
        self.layout.setSpacing(5)

        # 弹簧，将按钮推到右侧
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addSpacerItem(spacer)

        # 创建按钮
        self.pin_button = QPushButton(self)
        self.toggle_partition_button = QPushButton(self)
        self.close_button = QPushButton(self)

        # 添加到布局
        self.layout.addWidget(self.pin_button)
        self.layout.addWidget(self.toggle_partition_button)
        self.layout.addWidget(self.close_button)

        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()


class QuickPanel(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        if not db_manager:
            raise ValueError("DBManager instance is required.")
        self.db = db_manager
        self._init_ui()

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._update_list)

        self.search_box.textChanged.connect(self._on_search_text_changed)
        self.list_widget.itemActivated.connect(self._on_item_activated)
        self.partition_tree.currentItemChanged.connect(self._on_partition_selection_changed)

        # 连接标题栏按钮信号
        self.title_bar.pin_button.clicked.connect(self._toggle_stay_on_top)
        self.title_bar.toggle_partition_button.clicked.connect(self._toggle_partition_panel)
        self.title_bar.close_button.clicked.connect(self.close)

        self._update_partition_tree()
        self._setup_icons() # 设置图标
        self._is_pinned = False # 初始为非置顶状态

    def _init_ui(self):
        self.setWindowTitle("Quick Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool) # 修改为Tool类型，避免失去焦点时消失

        # 主布局变为垂直
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0) # 无边距，让标题栏和内容区填满
        self.main_layout.setSpacing(0)

        # 1. 添加自定义标题栏
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        # 2. 创建主内容区
        content_widget = QWidget(self)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)

        # 2.1 左侧容器 (搜索框 + 列表)
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("搜索...")

        self.list_widget = QListWidget(self)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        left_layout.addWidget(self.search_box)
        left_layout.addWidget(self.list_widget)

        # 2.2 右侧分区树
        self.partition_tree = QTreeWidget(self)
        self.partition_tree.setHeaderHidden(True)

        # 将左右两侧添加到内容区布局
        content_layout.addWidget(left_widget, 3)
        content_layout.addWidget(self.partition_tree, 1)

        # 3. 将主内容区添加到主布局
        self.main_layout.addWidget(content_widget)

        self.setStyleSheet(DARK_STYLESHEET)
        self.resize(600, 600)

    def _on_search_text_changed(self):
        self.search_timer.start(300)

    def _update_list(self):
        search_text = self.search_box.text()
        partition_filter = None
        current_partition = self.partition_tree.currentItem()
        if current_partition:
            partition_data = current_partition.data(0, Qt.UserRole)
            if partition_data and partition_data['type'] != 'all':
                partition_filter = partition_data
        items = self.db.get_items(search=search_text, partition_filter=partition_filter, limit=100)
        self.list_widget.clear()
        for item in items:
            list_item = QListWidgetItem(item.content.split('\n')[0])
            list_item.setData(Qt.UserRole, item)
            self.list_widget.addItem(list_item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _update_partition_tree(self):
        self.partition_tree.clear()
        all_items_node = QTreeWidgetItem(self.partition_tree, ["全部"])
        all_items_node.setData(0, Qt.UserRole, {'type': 'all', 'id': -1})
        top_level_partitions = self.db.get_partitions_tree()
        self._add_partition_recursive(top_level_partitions, self.partition_tree)
        self.partition_tree.expandAll()
        self.partition_tree.setCurrentItem(all_items_node)

    def _add_partition_recursive(self, partitions, parent_item):
        for partition in partitions:
            item = QTreeWidgetItem(parent_item, [partition.name])
            item.setData(0, Qt.UserRole, {'type': 'partition', 'id': partition.id})
            if partition.children:
                self._add_partition_recursive(partition.children, item)

    def _on_partition_selection_changed(self, current, previous):
        self._update_list()

    def _toggle_partition_panel(self):
        """切换分区面板的可见性。"""
        self.partition_tree.setVisible(not self.partition_tree.isVisible())

    def _toggle_stay_on_top(self):
        """切换窗口的置顶状态。"""
        self._is_pinned = not self._is_pinned
        if self._is_pinned:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.title_bar.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogYesButton)) # 使用一个现有图标示意
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.title_bar.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogNoButton)) # 使用一个现有图标示意
        self.show() # 重新显示窗口以应用标志更改

    def _setup_icons(self):
        """为标题栏按钮设置图标。"""
        # 使用QStyle提供的标准图标
        self.title_bar.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogNoButton))
        self.title_bar.toggle_partition_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.title_bar.close_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))

    def _on_item_activated(self, item):
        db_item = item.data(Qt.UserRole)
        if db_item:
            try:
                QApplication.clipboard().setText(db_item.content)
                self.close()
            except Exception as e:
                print(f"复制到剪贴板失败: {e}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        elif key in (Qt.Key_Up, Qt.Key_Down):
            self.list_widget.setFocus()
            QApplication.sendEvent(self.list_widget, event)
        else:
            self.search_box.setFocus()
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    db_manager = DBManager()
    panel = QuickPanel(db_manager=db_manager)
    panel.show()
    screen_geo = app.desktop().screenGeometry()
    panel_geo = panel.geometry()
    panel.move((screen_geo.width() - panel_geo.width()) // 2, (screen_geo.height() - panel_geo.height()) // 2)
    panel.search_box.setFocus()
    sys.exit(app.exec_())
