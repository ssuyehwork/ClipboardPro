# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListWidget, QLineEdit, QListWidgetItem)
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

QListWidget {
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px;
}

QListWidget::item {
    padding: 8px;
}

QListWidget::item:selected {
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
        self.list_widget.itemActivated.connect(self._on_item_activated) # itemActivated 包含双击和回车

        self._update_list()

    def _init_ui(self):
        self.setWindowTitle("Quick Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Popup)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("搜索...")

        self.list_widget = QListWidget(self)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(self.search_box)
        self.layout.addWidget(self.list_widget)

        self.setStyleSheet(DARK_STYLESHEET)
        self.resize(400, 600)

    def _on_search_text_changed(self):
        self.search_timer.start(300)

    def _update_list(self):
        search_text = self.search_box.text()
        items = self.db.get_items(search=search_text, limit=100)

        self.list_widget.clear()
        for item in items:
            list_item = QListWidgetItem(item.content.split('\n')[0])
            list_item.setData(Qt.UserRole, item)
            self.list_widget.addItem(list_item)

        # 默认选中第一项
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _on_item_activated(self, item):
        """当项目被激活（双击或回车）时调用。"""
        db_item = item.data(Qt.UserRole)
        if db_item:
            try:
                QApplication.clipboard().setText(db_item.content)
                print(f"已复制: {db_item.content[:50]}...") # Log for verification
                self.close()
            except Exception as e:
                print(f"复制到剪贴板失败: {e}")

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Escape:
            self.close()
        # 将上/下键事件从搜索框传递到列表
        elif key in (Qt.Key_Up, Qt.Key_Down):
            # 将焦点设置到 list_widget 并模拟按键事件
            self.list_widget.setFocus()
            QApplication.sendEvent(self.list_widget, event)
        else:
            # 确保搜索框能接收到其他按键事件
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

    # 默认聚焦到搜索框
    panel.search_box.setFocus()

    sys.exit(app.exec_())
