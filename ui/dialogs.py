# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QLineEdit, QColorDialog, QLabel,
                             QDialogButtonBox, QSizePolicy)
from PyQt5.QtCore import Qt, QPoint

from .widget_tag_input import TagInputWidget
from .popup_tag import TagPopup

class TagDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.selected_tag = None
        self.setWindowTitle("标签管理")
        self.resize(300, 400)
        layout = QVBoxLayout(self)
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("输入新标签...")
        self.input.returnPressed.connect(self.accept_input)
        layout.addWidget(self.input)
        
        self.list = QListWidget()
        self.list.itemClicked.connect(self.item_clicked)
        layout.addWidget(self.list)
        self.refresh_list()
        
    def refresh_list(self):
        self.list.clear()
        tags = self.db.get_stats()['tags']
        for name, count in tags: self.list.addItem(f"{name}")

    def accept_input(self):
        text = self.input.text().strip()
        if text: self.selected_tag = text; self.accept()

    def item_clicked(self, item):
        self.selected_tag = item.text(); self.accept()

class ColorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = None
        self.setWindowTitle("选择颜色")
        layout = QVBoxLayout(self)
        grid = QHBoxLayout()
        for c in ["#f38ba8", "#f9e2af", "#a6e3a1", "#89b4fa", "#cba6f7"]:
            btn = QPushButton()
            btn.setFixedSize(30, 30)
            btn.setObjectName("ColorDialogButton")
            btn.setProperty("color", c) # 使用setProperty存储颜色
            btn.clicked.connect(lambda _, col=c: self.done_color(col))
            grid.addWidget(btn)
        layout.addLayout(grid)
        sys_btn = QPushButton("更多颜色...")
        sys_btn.clicked.connect(self.pick_sys)
        layout.addWidget(sys_btn)
        
    def done_color(self, c): self.color = c; self.accept()
    def pick_sys(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.color = c.name(); self.accept()

class SetPartitionTagsDialog(QDialog):
    """设置分区预设标签的对话框"""
    def __init__(self, db_manager, partition_name, current_tags=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.partition_name = partition_name
        self.setWindowTitle("设置自动标签")
        self.setMinimumWidth(350)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(10)

        # 分区名称标签
        name_layout = QHBoxLayout()
        name_label = QLabel("分区名称:")
        name_value = QLabel(self.partition_name)
        name_value.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_value, 1)
        self.main_layout.addLayout(name_layout)

        # 标签输入组件
        tags_label = QLabel("自动添加标签:")
        self.tag_input = TagInputWidget()
        self.tag_input.line_edit.setPlaceholderText("添加标签")
        self.tag_input.text_changed.connect(self._on_tag_input_text_changed)

        if current_tags:
            for tag in current_tags:
                self.tag_input.add_chip(tag)

        self.main_layout.addWidget(tags_label)
        self.main_layout.addWidget(self.tag_input)

        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.button_box)

        # 弹出选择器
        self.popup = TagPopup(self)
        self.popup.tag_selected.connect(self._on_popup_tag_selected)
        self.popup.create_tag_requested.connect(self._on_popup_create_tag)
        self.popup.hide()

    def get_selected_tags(self):
        return self.tag_input.get_tags()

    def _on_tag_input_text_changed(self, text):
        if not text.strip():
            self.popup.hide()
            return

        # 定位和显示弹出窗口
        pos = self.tag_input.mapToGlobal(self.tag_input.line_edit.pos())
        popup_pos = QPoint(pos.x(), pos.y() + self.tag_input.line_edit.height() + 2)
        self.popup.move(popup_pos)
        self.popup.setFixedWidth(self.tag_input.width())

        all_tags = self.db.get_stats().get('tags', [])
        self.popup.load_history(all_tags, self.tag_input.get_tags())
        self.popup.filter_ui(text)
        self.popup.show()

    def _on_popup_tag_selected(self, tag_name, is_checked):
        if is_checked:
            if tag_name not in self.tag_input.get_tags():
                self.tag_input.add_chip(tag_name)
        else:
            for chip in self.tag_input.chips:
                if chip.text() == tag_name:
                    self.tag_input.remove_chip(chip)
                    break
        self.tag_input.clear_text()
        self.popup.hide()

    def _on_popup_create_tag(self, tag_name):
        if tag_name not in self.tag_input.get_tags():
            self.tag_input.add_chip(tag_name)
        self.tag_input.clear_text()
        self.popup.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.popup.isVisible():
            self.popup.hide()
        else:
            super().keyPressEvent(event)
