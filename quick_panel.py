# -*- coding: utf-8 -*-
import sys
import os
import ctypes
import time
from ctypes import wintypes

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QListWidget, QLineEdit, 
                             QListWidgetItem, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QPushButton, QStyle, QSpacerItem, QSizePolicy, QAction)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage

from data.database import DBManager

# --- Win32 API Definitions for Ditto Mode ---

# For GetGUIThreadInfo
class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("hwndActive", wintypes.HWND),
        ("hwndFocus", wintypes.HWND),
        ("hwndCapture", wintypes.HWND),
        ("hwndMenuOwner", wintypes.HWND),
        ("hwndMoveSize", wintypes.HWND),
        ("hwndCaret", wintypes.HWND),
        ("rcCaret", wintypes.RECT),
    ]

# For SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_ushort), ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

# Constants
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_V = 0x56

DARK_STYLESHEET = """
QWidget { background-color: #2E2E2E; color: #F0F0F0; font-family: "Microsoft YaHei"; font-size: 14px; }
QListWidget, QTreeWidget { border: 1px solid #444; border-radius: 4px; padding: 5px; }
QListWidget::item { padding: 8px; }
QTreeWidget::item { padding-top: 2px; padding-bottom: 2px; padding-left: 6px; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #4D4D4D; color: #FFFFFF; }
QLineEdit { background-color: #3C3C3C; border: 1px solid #555; border-radius: 4px; padding: 6px; font-size: 16px; }
CustomTitleBar { background-color: #3C3C3C; height: 30px; }
CustomTitleBar QPushButton { background-color: transparent; border: none; width: 25px; height: 25px; padding: 5px; }
CustomTitleBar QPushButton:hover { background-color: #555555; border-radius: 4px; }
"""

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.setSpacing(5)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout.addSpacerItem(spacer)
        self.pin_button = QPushButton(self)
        self.toggle_partition_button = QPushButton(self)
        self.close_button = QPushButton(self)
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
        self.last_active_hwnd = None
        self.last_focus_hwnd = None
        self.last_thread_id = None
        self._init_ui()
        
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._track_active_window)
        self.monitor_timer.start(200)

        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._update_list)
        
        self.search_box.textChanged.connect(self._on_search_text_changed)
        self.list_widget.itemActivated.connect(self._on_item_activated)
        self.partition_tree.currentItemChanged.connect(self._on_partition_selection_changed)
        self.clear_action.triggered.connect(self.search_box.clear)
        self.search_box.textChanged.connect(lambda text: self.clear_action.setVisible(bool(text)))
        self.clear_action.setVisible(False)
        self.title_bar.pin_button.clicked.connect(self._toggle_stay_on_top)
        self.title_bar.toggle_partition_button.clicked.connect(self._toggle_partition_panel)
        self.title_bar.close_button.clicked.connect(self.close)

        self._update_partition_tree()
        self._setup_icons()
        self._is_pinned = False

    def _init_ui(self):
        self.setWindowTitle("Quick Panel")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window | Qt.Tool)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)
        content_widget = QWidget(self)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("搜索...")
        self.clear_action = QAction(self)
        self.clear_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.search_box.addAction(self.clear_action, QLineEdit.TrailingPosition)
        self.list_widget = QListWidget(self)
        self.list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        left_layout.addWidget(self.search_box)
        left_layout.addWidget(self.list_widget)
        self.partition_tree = QTreeWidget(self)
        self.partition_tree.setHeaderHidden(True)
        self.partition_tree.setFocusPolicy(Qt.NoFocus)
        content_layout.addWidget(left_widget, 3)
        content_layout.addWidget(self.partition_tree, 1)
        self.main_layout.addWidget(content_widget)
        self.setStyleSheet(DARK_STYLESHEET)
        self.resize(600, 600)

    def _track_active_window(self):
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if hwnd and hwnd != self.winId():
                self.last_active_hwnd = hwnd

                thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
                gui_thread_info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))

                if ctypes.windll.user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui_thread_info)):
                    self.last_focus_hwnd = gui_thread_info.hwndFocus
                    self.last_thread_id = thread_id
                else:
                    self.last_focus_hwnd = self.last_active_hwnd
        except AttributeError:
            pass

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
            display_text = self._get_content_display(item)
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.UserRole, item)
            list_item.setToolTip(item.content)
            self.list_widget.addItem(list_item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def _get_content_display(self, item):
        if item.item_type == 'file' and item.file_path: return os.path.basename(item.file_path)
        elif item.item_type == 'url' and item.url_domain: return f"[{item.url_domain}] {item.url_title or ''}"
        elif item.item_type == 'image': return "[图片] " + os.path.basename(item.image_path) if item.image_path else "[图片]"
        else: return item.content.replace('\n', ' ').replace('\r', '').strip()[:150]

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
            if partition.children: self._add_partition_recursive(partition.children, item)
    
    def _on_partition_selection_changed(self, current, previous): self._update_list()
    def _toggle_partition_panel(self): self.partition_tree.setVisible(not self.partition_tree.isVisible())

    def _toggle_stay_on_top(self):
        self._is_pinned = not self._is_pinned
        if self._is_pinned: self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else: self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def _setup_icons(self):
        self.title_bar.pin_button.setIcon(self.style().standardIcon(QStyle.SP_DialogNoButton))
        self.title_bar.toggle_partition_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.title_bar.close_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))

    def _send_paste_command(self):
        current_thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        attached = False
        try:
            # 权限挂接
            attached = ctypes.windll.user32.AttachThreadInput(current_thread_id, self.last_thread_id, True)
            if not attached:
                print("AttachThreadInput 失败")
                return

            # 激活与聚焦
            ctypes.windll.user32.SetForegroundWindow(self.last_active_hwnd)
            ctypes.windll.user32.SetFocus(self.last_focus_hwnd)

            # 模拟粘贴
            ctrl_down = Input(type=1, ii=Input_I(ki=KeyBdInput(wVk=VK_CONTROL, wScan=0, dwFlags=0, time=0, dwExtraInfo=None)))
            v_down = Input(type=1, ii=Input_I(ki=KeyBdInput(wVk=VK_V, wScan=0, dwFlags=0, time=0, dwExtraInfo=None)))
            v_up = Input(type=1, ii=Input_I(ki=KeyBdInput(wVk=VK_V, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=None)))
            ctrl_up = Input(type=1, ii=Input_I(ki=KeyBdInput(wVk=VK_CONTROL, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=None)))
            inputs = (Input * 4)(ctrl_down, v_down, v_up, ctrl_up)
            ctypes.windll.user32.SendInput(4, ctypes.pointer(inputs), ctypes.sizeof(inputs[0]))

        finally:
            # 脱离挂接
            if attached:
                ctypes.windll.user32.AttachThreadInput(current_thread_id, self.last_thread_id, False)

    def _on_item_activated(self, item):
        db_item = item.data(Qt.UserRole)
        if not db_item or not self.last_active_hwnd:
            return

        try:
            if db_item.item_type == 'image' and db_item.data_blob:
                image = QImage()
                image.loadFromData(db_item.data_blob)
                QApplication.clipboard().setImage(image)
            else:
                QApplication.clipboard().setText(db_item.content)

            self.hide() # 必须先隐藏自己，否则自己会成为前景窗口
            QTimer.singleShot(50, self._send_paste_command)
            # 粘贴动作完成后，重新显示窗口
            QTimer.singleShot(100, self.show)

        except Exception as e:
            print(f"处理项目激活失败: {e}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape: self.close()
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
