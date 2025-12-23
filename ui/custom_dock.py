# -*- coding: utf-8 -*-
import logging
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QToolButton, QMenu, QAction, QDockWidget, QStylePainter, QStyleOption, QStyle
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor

# 配置日志
log = logging.getLogger("CustomDock")

# 添加边缘宽度常量
BORDER_WIDTH = 5

class CustomDockTitleBar(QWidget):
    def __init__(self, title, dock_widget, main_window, parent=None):
        super().__init__(parent)
        self.dock = dock_widget
        self.mw = main_window 
        
        self.setFixedHeight(38) # 增加高度，避免被视觉挤压
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("CustomDockTitleBar")  # 关键：设置对象名以确保样式表生效
        
        # 关键修复：设置显式的背景色，作为明显的拖拽手柄
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 5, 6) # 增加垂直内边距
        layout.setSpacing(0)
        
        self.label = QLabel(title)
        self.label.setObjectName("customDockLabel")
        layout.addWidget(self.label)
        
        layout.addStretch()
        
        self.btn_menu = QToolButton()
        self.btn_menu.setObjectName("customDockMenuButton")
        self.btn_menu.setText("≡")
        self.btn_menu.setFixedSize(24, 24)
        self.btn_menu.setCursor(Qt.PointingHandCursor)
        self.btn_menu.setPopupMode(QToolButton.InstantPopup)
        self.btn_menu.clicked.connect(self.show_menu)
        
        layout.addWidget(self.btn_menu)

        # --- 新增：用于拖拽和缩放的变量 ---
        self.resizing = False
        self.moving = False
        self.start_pos = QPoint()
        self.start_geometry = None
        self.resize_edge = None
        self.setMouseTracking(True) # 启用鼠标跟踪以实时更新光标

    def _update_cursor(self, pos):
        """根据鼠标位置更新光标形状"""
        if not self.dock.isFloating():
            self.unsetCursor()
            return

        parent = self.dock.parentWidget()
        if not parent: return

        rect = parent.rect()
        on_left = abs(pos.x() - rect.left()) < BORDER_WIDTH
        on_right = abs(pos.x() - rect.right()) < BORDER_WIDTH
        on_top = abs(pos.y() - rect.top()) < BORDER_WIDTH
        on_bottom = abs(pos.y() - rect.bottom()) < BORDER_WIDTH

        if on_top and on_left: self.resize_edge = "top_left"; self.setCursor(Qt.SizeFDiagCursor)
        elif on_bottom and on_right: self.resize_edge = "bottom_right"; self.setCursor(Qt.SizeFDiagCursor)
        elif on_top and on_right: self.resize_edge = "top_right"; self.setCursor(Qt.SizeBDiagCursor)
        elif on_bottom and on_left: self.resize_edge = "bottom_left"; self.setCursor(Qt.SizeBDiagCursor)
        elif on_left: self.resize_edge = "left"; self.setCursor(Qt.SizeHorCursor)
        elif on_right: self.resize_edge = "right"; self.setCursor(Qt.SizeHorCursor)
        elif on_top: self.resize_edge = "top"; self.setCursor(Qt.SizeVerCursor)
        elif on_bottom: self.resize_edge = "bottom"; self.setCursor(Qt.SizeVerCursor)
        else: self.resize_edge = None; self.unsetCursor()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.dock.isFloating():
            parent = self.dock.parentWidget()
            if not parent: return

            self.start_pos = event.globalPos()
            self.start_geometry = parent.geometry()

            # 检查是否在边缘
            if self.resize_edge:
                self.resizing = True
            else: # 不在边缘，则为拖动
                self.moving = True

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        parent = self.dock.parentWidget()
        if not parent:
            super().mouseMoveEvent(event)
            return

        # 实时更新光标形状 (无论是否按下)
        if not (self.resizing or self.moving):
            # 将事件坐标转换为父窗口坐标系
            self._update_cursor(parent.mapFromGlobal(event.globalPos()))

        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.start_pos

            if self.moving:
                parent.move(self.start_geometry.topLeft() + delta)

            elif self.resizing:
                geom = self.start_geometry

                if "left" in self.resize_edge:
                    geom.setLeft(self.start_geometry.left() + delta.x())
                if "right" in self.resize_edge:
                    geom.setRight(self.start_geometry.right() + delta.x())
                if "top" in self.resize_edge:
                    geom.setTop(self.start_geometry.top() + delta.y())
                if "bottom" in self.resize_edge:
                    geom.setBottom(self.start_geometry.bottom() + delta.y())

                parent.setGeometry(geom)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False
            self.resizing = False
            self.resize_edge = None
            self.start_pos = QPoint()
            self.start_geometry = None

        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """强制渲染 QSS 背景色，解决自定义 QWidget 背景不生效的问题"""
        opt = QStyleOption()
        opt.initFrom(self)
        p = QStylePainter(self)
        p.drawPrimitive(QStyle.PE_Widget, opt)
        super().paintEvent(event)

    def show_menu(self):
        log.info(f"🍔 点击了 [{self.label.text()}] 的菜单按钮")
        menu = QMenu(self)
        
        # 查找所有 Dock
        docks = self.mw.findChildren(QDockWidget)
        log.info(f"🔍 查找到 {len(docks)} 个面板: {[d.windowTitle() for d in docks]}")
        
        if not docks:
            log.warning("⚠️ 没有找到任何 Dock 面板！")
            
        for dock in docks:
            title = dock.windowTitle()
            if not title: continue
            
            action = QAction(title, menu)
            action.setCheckable(True)
            action.setChecked(dock.isVisible())
            # 使用闭包防止变量污染
            action.triggered.connect(lambda checked, d=dock: self.toggle_dock(d, checked))
            menu.addAction(action)
            
        menu.exec_(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft()))

    def toggle_dock(self, dock, visible):
        log.info(f"🔄 切换面板 [{dock.windowTitle()}] 可见性 -> {visible}")
        dock.setVisible(visible)