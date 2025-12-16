# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QIcon, QMouseEvent
import os
from .flow_layout import FlowLayout  # 导入新的布局管理器
from .widgets.tag_widget import TagWidget


class DetailPanel(QWidget):
    update_note_signal = pyqtSignal(str)
    tags_added_signal = pyqtSignal(list) # 新的信号，用于提交标签列表
    remove_tag_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
            
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16) # 舒适的内边距
        self.layout.setSpacing(16) # 模块间距
        
        # 0. 所属分区/分组信息
        partition_info_layout = QHBoxLayout()
        self.lbl_group = QLabel("分组: --")
        self.lbl_group.setObjectName("PartitionInfoLabel")
        self.lbl_partition = QLabel("分区: --")
        self.lbl_partition.setObjectName("PartitionInfoLabel")
        partition_info_layout.addWidget(self.lbl_group)
        partition_info_layout.addSpacing(20)
        partition_info_layout.addWidget(self.lbl_partition)
        partition_info_layout.addStretch()
        self.layout.addLayout(partition_info_layout)

        # 1. 内容预览模块
        # 文本预览组件
        self.preview = QTextEdit()
        self.preview.setObjectName("PreviewBox")
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("暂无内容...")
        self.preview.textChanged.connect(self._update_preview_height) # 文本变化时更新高度
        self.layout.addWidget(self.preview)
        
        # 图片预览组件 (默认隐藏，和文本预览互斥显示)
        self.image_label = QLabel()
        self.image_label.setObjectName("ImageBox")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.hide()
        self.layout.addWidget(self.image_label)

        # 2. 备注模块
        note_container = QWidget()
        note_layout = QVBoxLayout(note_container)
        note_layout.setContentsMargins(0, 0, 0, 0)
        note_layout.setSpacing(4)
        
        lbl_note = QLabel("备注:")
        lbl_note.setObjectName("SectionTitle")
        note_layout.addWidget(lbl_note)
        
        self.note_edit = QLineEdit()
        self.note_edit.setObjectName("NoteInput")
        self.note_edit.setPlaceholderText("点击添加备注信息...")
        self.note_edit.returnPressed.connect(lambda: self.update_note_signal.emit(self.note_edit.text()))
        note_layout.addWidget(self.note_edit)
        
        self.layout.addWidget(note_container)
        
        # 3. 标签模块
        tag_container_widget = QWidget()
        tag_main_layout = QVBoxLayout(tag_container_widget)
        tag_main_layout.setContentsMargins(0, 0, 0, 0)
        tag_main_layout.setSpacing(8)
        
        # 标签头
        header_line = QHBoxLayout()
        lbl_tags = QLabel("标签:")
        lbl_tags.setObjectName("SectionTitle")
        header_line.addWidget(lbl_tags)
        header_line.addStretch()
        tag_main_layout.addLayout(header_line)
        
        # 标签流式区域 (替换为 FlowLayout)
        self.tag_content = QWidget()
        self.tag_content.setObjectName("TagContainer")
        self.tag_layout = FlowLayout(self.tag_content, spacing=6) # 使用新的布局
        self.tag_layout.setContentsMargins(0, 0, 0, 0)
        
        tag_main_layout.addWidget(self.tag_content)
        
        self.layout.addWidget(tag_container_widget)

        # 新增：标签输入框（移动到主布局的末尾）
        self.tag_input = QLineEdit()
        self.tag_input.setObjectName("NoteInput") # 复用备注输入框的样式
        self.tag_input.setPlaceholderText("输入标签，用逗号分隔...")
        self.tag_input.returnPressed.connect(self._on_tags_submitted)
        self.tag_input.setEnabled(False) # 默认禁用

        # 添加一个弹簧，将所有内容推到顶部
        self.layout.addStretch(1)
        self.layout.addWidget(self.tag_input)

    def load_item(self, content, note, tags, group_name=None, partition_name=None, item_type='text', image_path=None, file_path=None):
        # 设置分区信息
        self.lbl_group.setText(f"分组: {group_name or '--'}")
        self.lbl_partition.setText(f"分区: {partition_name or '未分类'}")

        # 设置备注
        self.note_edit.setText(note)
        self.note_edit.setCursorPosition(0)
        
        # 处理图片/文本切换逻辑
        final_image_path = None
        if image_path and os.path.exists(image_path):
            final_image_path = image_path
        elif file_path and os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']:
                final_image_path = file_path
        
        if final_image_path:
            self.preview.hide()
            self.image_label.show()
            pixmap = QPixmap(final_image_path)
            if not pixmap.isNull():
                # 以宽度为基准，创建一个正方形的缩略图
                size = self.image_label.width()
                self.image_label.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                # 关键：设置固定高度以保持正方形
                self.image_label.setFixedHeight(size)
            else:
                self.image_label.setText("图片无法加载")
        else:
            self.image_label.hide()
            self.preview.show()
            self.preview.setText(content)

        # 刷新标签和高度
        self._refresh_tags(tags)
        self._update_preview_height()

    def _update_preview_height(self):
        """智能计算并设置预览框的高度"""
        # 仅在文本预览可见时操作
        if self.preview.isVisible():
            # 获取文档的实际高度
            doc_height = self.preview.document().size().height()
            
            # 获取边距 (approax.)
            margins = self.preview.contentsMargins()
            # 额外增加5像素的缓冲空间，避免因细微计算误差导致不必要的滚动条出现
            content_height = doc_height + margins.top() + margins.bottom() + 5
            
            # 最大高度不能超过宽度
            max_h = self.preview.width()
            
            # 设置固定高度
            final_height = min(content_height, max_h)
            self.preview.setFixedHeight(int(final_height))

    def _refresh_tags(self, tags):
        # 清空旧标签
        while self.tag_layout.count():
            item = self.tag_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            
        if not tags:
            lbl_empty = QLabel("无标签")
            lbl_empty.setObjectName("EmptyTagLabel")
            self.tag_layout.addWidget(lbl_empty)
            return

        for tag_name in tags:
            tag_widget = TagWidget(tag_name)
            tag_widget.removed.connect(self.remove_tag_signal.emit)
            self.tag_layout.addWidget(tag_widget)

    def clear(self):
        self.lbl_group.setText("分组: --")
        self.lbl_partition.setText("分区: --")
        self.preview.clear()
        self.note_edit.clear()
        self._refresh_tags([])
        self.image_label.hide()
        self.preview.show()

    def resizeEvent(self, event):
        """重写 resize 事件，以便在面板宽度变化时更新预览高度"""
        super().resizeEvent(event)
        self._update_preview_height()

    def _on_tags_submitted(self):
        """处理标签输入框的回车事件"""
        text = self.tag_input.text().strip()
        if text:
            # 同时支持中英文逗号分割
            tags = [tag.strip() for tag in text.replace('，', ',').split(',') if tag.strip()]
            if tags:
                self.tags_added_signal.emit(tags)
            self.tag_input.clear()