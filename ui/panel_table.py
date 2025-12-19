# -*- coding: utf-8 -*-
import os
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal

class TablePanel(QTableWidget):
    reorder_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_trash_view = False  # 添加一个状态来跟踪是否在回收站视图
        self.setColumnCount(9)  # 从10改为9
        self.setHorizontalHeaderLabels(["状态", "内容", "备注", "星级", "大小", "类型", "创建时间", "PATH", "ID"])  # 移除"序"
        # 隐藏 PATH 和 ID 列（索引调整：原8,9变为7,8）
        self.hideColumn(7)
        self.hideColumn(8)
        
        # 设置列宽
        self.setColumnWidth(0, 40)  # 状态列
        
        # 样式与交互
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setShowGrid(False)
        # 启用斑马纹
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # 表头设置
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        # 启用列拖拽
        header.setSectionsMovable(True)
        header.setDragEnabled(True)
        
        # 启用行号列（垂直表头）
        self.verticalHeader().setVisible(True)
        # 开启手动调整模式：允许用户通过鼠标拖拽调整行高
        self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        # 修复：设置行号文本居中对齐
        self.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.verticalHeader().setDefaultSectionSize(25)

        # 监听 Viewport 的事件 (解决 Ctrl+滚轮 偶尔失效问题)
        self.viewport().installEventFilter(self)
        
        # 加载字体设置
        self.load_font_settings()

    def load_font_settings(self):
        from PyQt5.QtCore import QSettings
        settings = QSettings("MyCompany", "ClipboardPro")
        size = settings.value("table_font_size", 10, type=int)
        
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
        self.verticalHeader().setDefaultSectionSize(size + 18)

    def eventFilter(self, source, event):
        if source == self.viewport() and event.type() == event.Wheel:
            if event.modifiers() == Qt.ControlModifier:
                delta = event.angleDelta().y()
                # 转发给自己的处理函数
                self.handle_zoom(delta)
                self.handle_zoom(delta)
                return True
            
            # 屏蔽水平滚动：如果水平分量绝对值大于垂直分量，则忽略该事件
            # 这能防止触摸板或某些鼠标滚轮触发意外的水平滚动
            if abs(event.angleDelta().x()) > abs(event.angleDelta().y()):
                return True
                
        return super().eventFilter(source, event)

    def handle_zoom(self, delta):
        font = self.font()
        size = font.pointSize()
        
        # 调整字体大小
        if delta > 0:
            size += 1
        else:
            size = max(8, size - 1) # 最小8pt
            
        font.setPointSize(size)
        self.setFont(font)
        
        # 调整行高适应字体
        self.verticalHeader().setDefaultSectionSize(size + 18)
        
        # 保存设置
        from PyQt5.QtCore import QSettings
        settings = QSettings("MyCompany", "ClipboardPro")
        settings.setValue("table_font_size", size)

    def dropEvent(self, event):
        if event.source() != self: 
            super().dropEvent(event)
            return
        
        super().dropEvent(event)
        
        # 获取新的 ID 顺序
        new_ids = []
        for r in range(self.rowCount()):
            item = self.item(r, 8)  # ID列从9改为8
            if item: new_ids.append(int(item.text()))
        
        self.reorder_signal.emit(new_ids)

    def mimeData(self, indexes):
        from PyQt5.QtCore import QMimeData
        mime_data = QMimeData()
        
        # 使用自定义的MIME类型
        item_ids = []
        # 去重，只获取唯一的行
        unique_rows = {index.row() for index in indexes}
        
        for row in unique_rows:
            id_item = self.item(row, 8) # ID列
            if id_item:
                item_ids.append(id_item.text())
        
        if item_ids:
            # 将ID列表编码为字节串
            encoded_data = ",".join(item_ids).encode()
            mime_data.setData("application/x-clipboard-item-ids", encoded_data)

            # 如果在回收站视图中，添加额外的信息
            if self.is_trash_view:
                mime_data.setData("application/x-clipboard-source", b"trash")
            
        return mime_data

    # 移除旧的 wheelEvent，改用 viewport eventFilter

    def populate_table(self, items, col_alignments):
        from PyQt5.QtWidgets import QTableWidgetItem
        from core.shared import get_color_icon
        import os

        self.blockSignals(True)
        self.setRowCount(len(items))
        
        for row, item in enumerate(items):
            # ID列
            self.setItem(row, 8, QTableWidgetItem(str(item.id)))
            
            # 状态列
            st_flags = ""
            if item.is_pinned: st_flags += "📌"
            if item.is_favorite: st_flags += "❤️"
            if item.is_locked: st_flags += "🔒"
            
            type_icon = self._get_type_icon(item)
            display_text = f"{type_icon} {st_flags}".strip()
            
            state_item = QTableWidgetItem(display_text)
            if item.custom_color:
                state_item.setIcon(get_color_icon(item.custom_color))
            self.setItem(row, 0, state_item)
            
            # 其他列
            self.setItem(row, 1, QTableWidgetItem(item.content.replace('\\n', ' ')[:100]))
            self.setItem(row, 2, QTableWidgetItem(item.note))
            self.setItem(row, 3, QTableWidgetItem("★" * item.star_level))
            self.setItem(row, 4, QTableWidgetItem(str(len(item.content)))) # 简单用长度代替
            
            type_str = self._get_type_string(item)
            self.setItem(row, 5, QTableWidgetItem(type_str))
            
            self.setItem(row, 6, QTableWidgetItem(item.created_at.strftime("%m-%d %H:%M")))
            
            # 设置对齐
            for col in range(7):
                align = col_alignments.get(col, Qt.AlignLeft | Qt.AlignVCenter if col in [1, 2] else Qt.AlignCenter)
                it = self.item(row, col)
                if it: it.setTextAlignment(align)

        self.blockSignals(False)

    def _get_type_icon(self, item):
        if item.item_type == 'url': return "🔗"
        if item.item_type == 'image': return "🖼️"
        if item.item_type == 'file' and item.file_path:
            if os.path.exists(item.file_path):
                if os.path.isdir(item.file_path): return "📂"
                ext = os.path.splitext(item.file_path)[1].lower()
                if ext in ['.mp3', '.wav', '.flac']: return "🎵"
                if ext in ['.mp4', '.mkv', '.avi']: return "🎬"
                return "📄"
            else:
                return "📄" # 文件丢失
        return ""

    def _get_type_string(self, item):
        if item.item_type == 'file' and item.file_path:
            _, ext = os.path.splitext(item.file_path)
            return ext.upper()[1:] if ext else "FILE"
        return "TXT"
