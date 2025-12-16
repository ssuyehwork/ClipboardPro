# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QTableWidget, QAbstractItemView, QLineEdit, QWidget, 
                             QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, 
                             QFrame, QLabel, QCompleter, QComboBox, QToolButton, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings, QSize
from PyQt5.QtGui import QColor, QBrush, QIcon
from core.shared import get_color_icon

# === 侧边栏 ===
class FilterTreeWidget(QTreeWidget):
    filterChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setObjectName("FilterTree") # 设置ObjectName
        self.itemChanged.connect(lambda: self.filterChanged.emit())
        
        self.roots = {}
        order = [
            ('stars', '⭐ 评级'),
            ('colors', '🎨 颜色'),
            ('tags', '🏷️ 标签'),
            ('date_create', '📅 创建日期'),
            ('date_modify', '📅 修改日期')
        ]
        
        for key, label in order:
            item = QTreeWidgetItem(self)
            item.setText(0, label)
            item.setExpanded(True)
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
            self.roots[key] = item
            
        self._add_fixed_date_options('date_create')
        self._add_fixed_date_options('date_modify')

    def _add_fixed_date_options(self, key):
        root = self.roots[key]
        options = ["今日", "昨日", "周内", "两周", "本月", "上月", "自定义"]
        for opt in options:
            child = QTreeWidgetItem(root)
            child.setText(0, opt)
            child.setData(0, Qt.UserRole, opt)
            child.setCheckState(0, Qt.Unchecked)

    def update_stats(self, stats):
        self.blockSignals(True)
        
        star_data = []
        for i in range(5, 0, -1):
            label = "★" * i
            count = stats['stars'].get(i, 0)
            star_data.append((i, label, count))
        
        if 0 in stats['stars']:
            star_data.append((0, "无", stats['stars'][0]))

        self._refresh('stars', star_data)
        self._refresh('colors', [(c, c.upper(), count) for c, count in stats['colors'].items()], is_col=True)
        self._refresh('tags', stats.get('tags', []), is_tag=True)
        self.blockSignals(False)

    def _refresh(self, key, data, is_tag=False, is_col=False):
        root = self.roots[key]
        checked = {root.child(i).data(0, Qt.UserRole) for i in range(root.childCount()) if root.child(i).checkState(0) == Qt.Checked}
        root.takeChildren()
        
        if not data:
            empty = QTreeWidgetItem(root)
            empty.setText(0, "暂无")
            empty.setFlags(Qt.NoItemFlags)
            return

        for v, l, c in data:
            if is_tag: v, l, c = v, v, l
            if c == 0 and v not in checked: continue
            child = QTreeWidgetItem(root); child.setText(0, f"{l} ({c})"); child.setData(0, Qt.UserRole, v)
            child.setCheckState(0, Qt.Checked if v in checked else Qt.Unchecked)
            if is_col: child.setIcon(0, get_color_icon(v))

    def get_checked(self, key):
        root = self.roots[key]
        return [root.child(i).data(0, Qt.UserRole) for i in range(root.childCount()) if root.child(i).checkState(0) == Qt.Checked]

# === 表格 ===
class DraggableTable(QTableWidget):
    reorder_signal = pyqtSignal(list)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True); self.setAcceptDrops(True); self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionBehavior(QAbstractItemView.SelectRows); self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setShowGrid(False); self.setAlternatingRowColors(True)

    def dropEvent(self, event):
        if event.source() != self: super().dropEvent(event); return
        super().dropEvent(event)
        new_ids = []
        for r in range(self.rowCount()):
            item = self.item(r, 9)
            if item: new_ids.append(int(item.text()))
        self.reorder_signal.emit(new_ids)

# === 搜索框 ===
class SearchBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("🔍 搜索内容...")
        self.settings = QSettings("ClipboardPro", "SearchHistory")
        self.history = self.settings.value("history", [], type=list)
        self.completer = QCompleter(self.history); self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self.completer)
        self.returnPressed.connect(self._save)
        
        self.clearBtn = QPushButton("×", self)
        self.clearBtn.setCursor(Qt.PointingHandCursor)
        self.clearBtn.setFixedSize(20, 20)
        self.clearBtn.setObjectName("SearchBarClearButton") # 设置ObjectName
        self.clearBtn.clicked.connect(self.clear)
        self.clearBtn.hide()
        self.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self, text):
        self.clearBtn.setVisible(bool(text))

    def resizeEvent(self, event):
        sz = self.clearBtn.sizeHint()
        fr = self.rect()
        self.clearBtn.move(fr.right() - sz.width() - 4, (fr.bottom() - sz.height()) // 2)
        super().resizeEvent(event)

    def _save(self):
        t = self.text().strip()
        if t and t not in self.history:
            self.history.insert(0, t); self.history = self.history[:20]; self.settings.setValue("history", self.history)
            self.completer = QCompleter(self.history); self.setCompleter(self.completer)

# === 标题栏 ===
class CustomTitleBar(QWidget):
    refresh_clicked = pyqtSignal()
    theme_clicked = pyqtSignal()
    search_changed = pyqtSignal()
    clean_clicked = pyqtSignal()
    color_clicked = pyqtSignal()
    pin_clicked = pyqtSignal(bool)
    mode_clicked = pyqtSignal(bool)
    display_count_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0)
        layout.setSpacing(6)
        
        title = QLabel("💾 印象记忆")
        title.setObjectName("WindowTitle") # 设置ObjectName
        layout.addWidget(title)
        
        self.search_bar = SearchBar()
        self.search_bar.setFixedWidth(220)
        self.search_bar.textChanged.connect(lambda: self.search_changed.emit())
        self.search_bar.returnPressed.connect(lambda: self.search_changed.emit())
        layout.addWidget(self.search_bar)
        
        btn_clear_search = QPushButton("✕")
        btn_clear_search.setFixedSize(24, 24)
        btn_clear_search.setToolTip("清空搜索")
        btn_clear_search.setObjectName("ClearSearchButton") # 设置ObjectName
        btn_clear_search.clicked.connect(lambda: self.search_bar.clear())
        layout.addWidget(btn_clear_search)

        self.btn_display_count = QToolButton()
        self.btn_display_count.setText("显示: 100")
        self.btn_display_count.setPopupMode(QToolButton.InstantPopup)
        self.btn_display_count.setIconSize(QSize(12, 12))
        self.btn_display_count.setObjectName("DisplayCountButton") # 设置ObjectName
        
        menu = QMenu(self)
        counts = ["显示条数", 100, 200, 300, 400, 500, 1000]
        for count in counts:
            action = menu.addAction(str(count))
            action.setData(count if isinstance(count, int) else -1)
        
        menu.triggered.connect(self._on_display_count_changed)
        self.btn_display_count.setMenu(menu)
        layout.addWidget(self.btn_display_count)
        
        layout.addStretch()
        
        self.btn_clean = self._btn("🗑️", "清理"); self.btn_clean.setObjectName("ToolBarButton"); self.btn_clean.clicked.connect(self.clean_clicked.emit); layout.addWidget(self.btn_clean)
        self.btn_refresh = self._btn("🔄", "刷新"); self.btn_refresh.setObjectName("ToolBarButton"); self.btn_refresh.clicked.connect(self.refresh_clicked.emit); layout.addWidget(self.btn_refresh)
        self.btn_color = self._btn("🌈", "设置标签颜色"); self.btn_color.setObjectName("ToolBarButton"); self.btn_color.clicked.connect(self.color_clicked.emit); layout.addWidget(self.btn_color)
        self.btn_mode = self._btn("📝", "编辑模式", True); self.btn_mode.setObjectName("ToolBarButton"); self.btn_mode.clicked.connect(self.mode_clicked.emit); layout.addWidget(self.btn_mode)
        self.btn_pin = self._btn("📌", "置顶", True); self.btn_pin.setObjectName("ToolBarButton"); self.btn_pin.clicked.connect(self.pin_clicked.emit); layout.addWidget(self.btn_pin)

        self.btn_settings = QToolButton()
        self.btn_settings.setText("⚙️")
        self.btn_settings.setPopupMode(QToolButton.InstantPopup)
        self.btn_settings.setObjectName("ToolBarButton") # 复用样式
        
        settings_menu = QMenu(self)
        theme_action = settings_menu.addAction("切换主题")
        theme_action.triggered.connect(self.theme_clicked.emit)
        
        self.reset_layout_action = settings_menu.addAction("恢复默认布局")
        
        self.btn_settings.setMenu(settings_menu)
        layout.addWidget(self.btn_settings)
        
        line = QFrame(); line.setFrameShape(QFrame.VLine); line.setFrameShadow(QFrame.Sunken); line.setFixedHeight(20); line.setObjectName("TitleBarSeparator")
        layout.addWidget(line)
        
        self.btn_min = self._win_btn("—"); self.btn_min.setObjectName("WindowControlButton"); self.btn_min.clicked.connect(self.window().showMinimized); layout.addWidget(self.btn_min)
        self.btn_max = self._win_btn("⬜"); self.btn_max.setObjectName("WindowControlButton"); self.btn_max.clicked.connect(self.toggle_max); layout.addWidget(self.btn_max)
        self.btn_close = self._win_btn("✕", True); self.btn_close.setObjectName("WindowCloseButton"); self.btn_close.clicked.connect(self.window().close); layout.addWidget(self.btn_close)

    def _on_display_count_changed(self, action):
        count = action.data()
        self._update_display_count_text(count)
        self.display_count_changed.emit(count)

    def _update_display_count_text(self, count):
        if count == -1:
            self.btn_display_count.setText("显示条数")
        else:
            self.btn_display_count.setText(f"显示: {count}")

    def set_display_count(self, count):
        self._update_display_count_text(count)
    
    def _btn(self, t, tip, chk=False):
        b = QPushButton(t); b.setToolTip(tip); b.setFixedSize(34, 34)
        if chk:
            b.setCheckable(True)
        return b

    def _win_btn(self, t, cls=False):
        b = QPushButton(t)
        b.setFixedSize(46, 34)
        return b

    def toggle_max(self):
        w = self.window()
        if w.isMaximized(): w.showNormal(); self.btn_max.setText("⬜")
        else: w.showMaximized(); self.btn_max.setText("❐")
            
    def get_search_text(self): return self.search_bar.text().strip()
