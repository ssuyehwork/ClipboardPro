# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QScrollArea, QPushButton,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QColor, QCursor

from ui.flow_layout import FlowLayout

class TagPopup(QWidget):
    """
    动态标签选择/创建弹窗 (原生边缘拖拽调整大小)
    """
    tag_selected = pyqtSignal(str, bool)
    create_tag_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 启用鼠标追踪以实时更新光标
        self.setMouseTracking(True)

        # 尺寸限制
        self.setMinimumWidth(170)
        self.setMaximumWidth(800)
        self.setMinimumHeight(150)
        self.setMaximumHeight(420)

        # 拖拽调整大小相关的变量
        self._resizing = False
        self._resize_edge = None
        self._resize_start_pos = QPoint()
        self._resize_start_geom = QRect()
        self.margin = 5 # 边缘检测的灵敏度

        # 布局容器
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        
        self.container = QFrame()
        self.container.setObjectName("TagPopupContainer")
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.container.setMouseTracking(True) # 容器也需要追踪
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)
        
        self.layout_container = QVBoxLayout(self.container)
        self.layout_container.setContentsMargins(8, 8, 8, 8)
        self.layout_container.setSpacing(6)
        
        # ... (内部控件布局代码保持不变)
        self.creation_view = QFrame()
        self.creation_layout = QVBoxLayout(self.creation_view)
        self.creation_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_create = QPushButton()
        self.btn_create.setCursor(Qt.PointingHandCursor)
        self.btn_create.setObjectName("TagCreateButton")
        self.btn_create.clicked.connect(self._on_create_clicked)
        self.creation_layout.addWidget(self.btn_create)
        self.layout_container.addWidget(self.creation_view)
        
        self.history_view = QWidget()
        self.history_layout = QVBoxLayout(self.history_view)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(5)
        
        self.lbl_history = QLabel("最近使用")
        self.lbl_history.setObjectName("TagPopupHeader")
        self.history_layout.addWidget(self.lbl_history)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.tags_widget = QWidget()
        self.flow_layout = FlowLayout(self.tags_widget, margin=2, spacing=4)
        self.flow_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.tags_widget)

        self.history_layout.addWidget(self.scroll, 1)
        self.layout_container.addWidget(self.history_view, 1)
        
        self.main_layout.addWidget(self.container)
        
        self.lbl_tip = QLabel("关闭: Esc")
        self.lbl_tip.setObjectName("TagPopupTip")
        self.layout_container.addWidget(self.lbl_tip, 0, Qt.AlignRight)

        # 数据缓存
        self.current_tags = []
        self.selected_tags = set()
        self.typing_text = ""

    # --- 原生拖拽调整大小的核心实现 ---

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._resize_edge is not None:
            self._resizing = True
            self._resize_start_pos = event.globalPos()
            self._resize_start_geom = self.geometry()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._resizing:
            self._resizing = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self._resizing:
            delta = event.globalPos() - self._resize_start_pos
            geom = self._resize_start_geom

            new_geom = QRect(geom)

            if self._resize_edge & Qt.LeftEdge:
                new_geom.setLeft(geom.left() + delta.x())
            if self._resize_edge & Qt.RightEdge:
                new_geom.setRight(geom.right() + delta.x())
            if self._resize_edge & Qt.TopEdge:
                new_geom.setTop(geom.top() + delta.y())
            if self._resize_edge & Qt.BottomEdge:
                new_geom.setBottom(geom.bottom() + delta.y())

            # 确保不超出尺寸限制
            if new_geom.width() < self.minimumWidth():
                new_geom.setWidth(self.minimumWidth())
            if new_geom.width() > self.maximumWidth():
                new_geom.setWidth(self.maximumWidth())
            if new_geom.height() < self.minimumHeight():
                new_geom.setHeight(self.minimumHeight())
            if new_geom.height() > self.maximumHeight():
                new_geom.setHeight(self.maximumHeight())

            self.setGeometry(new_geom)
        else:
            self._update_cursor(event.pos())

    def _update_cursor(self, pos):
        """根据鼠标位置更新光标形状和拖拽边缘"""
        self._resize_edge = 0
        if pos.x() < self.margin:
            self._resize_edge |= Qt.LeftEdge
        if pos.x() > self.width() - self.margin:
            self._resize_edge |= Qt.RightEdge
        if pos.y() < self.margin:
            self._resize_edge |= Qt.TopEdge
        if pos.y() > self.height() - self.margin:
            self._resize_edge |= Qt.BottomEdge

        if self._resize_edge == (Qt.LeftEdge | Qt.TopEdge) or self._resize_edge == (Qt.RightEdge | Qt.BottomEdge):
            self.setCursor(QCursor(Qt.SizeFDiagCursor))
        elif self._resize_edge == (Qt.RightEdge | Qt.TopEdge) or self._resize_edge == (Qt.LeftEdge | Qt.BottomEdge):
            self.setCursor(QCursor(Qt.SizeBDiagCursor))
        elif self._resize_edge & (Qt.LeftEdge | Qt.RightEdge):
            self.setCursor(QCursor(Qt.SizeHorCursor))
        elif self._resize_edge & (Qt.TopEdge | Qt.BottomEdge):
            self.setCursor(QCursor(Qt.SizeVerCursor))
        else:
            self._resize_edge = None
            self.unsetCursor()

    # --- 业务逻辑方法 (保持不变) ---

    def load_history(self, tags, active_tags=None):
        self.current_tags = tags
        if active_tags:
            self.selected_tags = set(active_tags)
        self._populate_tags(self.current_tags)
        self.lbl_history.setText(f"最近使用 ({len(tags)})")
        self.creation_view.hide()
        self.history_view.show()

    def filter_ui(self, text):
        text = text.strip()
        self.typing_text = text
        filtered_tags = []
        is_exact_match = False
        if not text:
            filtered_tags = self.current_tags
        else:
            for name, count in self.current_tags:
                if text.lower() in name.lower():
                    filtered_tags.append((name, count))
                if text.lower() == name.lower():
                    is_exact_match = True
        self._populate_tags(filtered_tags)
        if not text:
            self.lbl_history.setText(f"最近使用 ({len(filtered_tags)})")
        else:
            self.lbl_history.setText("搜索结果")
        if text and not is_exact_match:
            self.creation_view.show()
            self.btn_create.setText(f"+ 新建标签 \"{text}\"")
        else:
            self.creation_view.hide()
        if filtered_tags:
            self.history_view.show()
        else:
            self.history_view.hide()

    def _populate_tags(self, tags):
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for name, count in tags:
            btn = self._create_tag_btn(name, count)
            self.flow_layout.addWidget(btn)
        self._refresh_check_state()

    def _create_tag_btn(self, name, count):
        btn = QPushButton()
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("tag_name", name)
        btn.setObjectName("TagPopupButton")
        btn.setText(f"🕒 {name}")
        btn.setToolTip(f"引用次数: {count}")
        btn.clicked.connect(lambda checked, n=name: self._on_tag_clicked(n, checked))
        return btn

    def _refresh_check_state(self):
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            if item and item.widget():
                btn = item.widget()
                name = btn.property("tag_name")
                btn.setChecked(name in self.selected_tags)

    def _on_tag_clicked(self, name, checked):
        if checked:
            self.selected_tags.add(name)
        else:
            self.selected_tags.discard(name)
        self._refresh_check_state()
        self.tag_selected.emit(name, checked)

    def _on_create_clicked(self):
        if self.typing_text:
            self.create_tag_requested.emit(self.typing_text)
            self.hide()
