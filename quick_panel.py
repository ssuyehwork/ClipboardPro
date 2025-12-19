# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListWidget, QLineEdit, QListWidgetItem, QHBoxLayout, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QTimer

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
"""

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

        # 初始化并加载数据
        self._update_partition_tree()
        # _update_list() 将在分区树加载并选中默认项后自动调用

    def _init_ui(self):
        self.setWindowTitle("Quick Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup)

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

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

        self.main_layout.addWidget(left_widget, 3)

        self.partition_tree = QTreeWidget(self)
        self.partition_tree.setHeaderHidden(True)

        self.main_layout.addWidget(self.partition_tree, 1)

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
        """当分区选择改变时，更新剪贴板列表。"""
        self._update_list()

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
