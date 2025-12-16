# -*- coding: utf-8 -*-
import logging
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QMenu, QInputDialog, QMessageBox, QLineEdit, QColorDialog,
                             QAbstractItemView, QStyle, QTreeWidgetItemIterator)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPainter

log = logging.getLogger(__name__)


class PartitionTreeWidget(QTreeWidget):
    """
    一个 QTreeWidget 子类，增加了拖放功能，用于对分区和组进行重新排序和重新分配。
    """
    partitionsUpdated = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setIndentation(15)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSortingEnabled(False)

    def keyPressEvent(self, event):
        """处理键盘事件，特别是删除键。"""
        if event.key() == Qt.Key_Delete:
            selected_item = self.currentItem()
            if selected_item:
                # 调用父级 PartitionPanel 的删除方法
                # 我们假设父级是 PartitionPanel，这在这个应用中是安全的
                self.parent()._delete_item(selected_item)
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        # 检查MIME类型，只接受我们自定义的数据
        if event.mimeData().hasFormat("application/x-clipboard-item-ids"):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        target_item = self.itemAt(event.pos())
        if not target_item:
            event.ignore()
            return
            
        target_data = target_item.data(0, Qt.UserRole)
        if not target_data:
            event.ignore()
            return
            
        target_type = target_data.get('type')
        
        # 检查拖动的数据源
        if event.mimeData().hasFormat("application/x-clipboard-item-ids"):
            # 从主列表拖动：允许放置在 'partition' 或 'trash'
            if target_type in ['partition', 'trash']:
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            # 内部拖动
            dragged_item = self.currentItem()
            if not dragged_item:
                event.ignore()
                return
            dragged_data = dragged_item.data(0, Qt.UserRole)
            if not dragged_data:
                event.ignore()
                return
            dragged_type = dragged_data.get('type')

            if target_type == 'trash' and dragged_type in ['group', 'partition', 'item']:
                # 允许将分区、分组或数据项拖到回收站
                event.acceptProposedAction()
            else:
                # 保持原有的父子拖动排序逻辑
                super().dragMoveEvent(event)

    def dropEvent(self, event):
        target_item = self.itemAt(event.pos())
        if not target_item:
            event.ignore()
            return
            
        target_data = target_item.data(0, Qt.UserRole)
        if not target_data:
            event.ignore()
            return
            
        target_type = target_data.get('type')

        if event.mimeData().hasFormat("application/x-clipboard-item-ids"):
            # --- 处理从外部表格拖拽过来的数据 ---
            encoded_data = event.mimeData().data("application/x-clipboard-item-ids")
            item_ids_str = encoded_data.data().decode()
            item_ids = [int(id_str) for id_str in item_ids_str.split(',') if id_str]

            if not item_ids:
                event.ignore()
                return

            if target_type == 'trash':
                # 拖拽到回收站
                log.info(f"正在通过拖拽将 {len(item_ids)} 个项目移动到回收站")
                self.db.move_items_to_trash(item_ids)
                self.partitionsUpdated.emit()
                event.acceptProposedAction()
                
            elif target_type == 'partition':
                # 拖拽到分区
                partition_id = target_data.get('id')
                
                # 检查拖拽源
                is_from_trash = event.mimeData().hasFormat("application/x-clipboard-source") and \
                                event.mimeData().data("application/x-clipboard-source") == b"trash"

                if is_from_trash:
                    # 从回收站恢复并移动
                    log.info(f"正在从回收站恢复 {len(item_ids)} 个项目到分区 {partition_id}")
                    if self.db.restore_and_move_items(item_ids, partition_id):
                        self.partitionsUpdated.emit()
                else:
                    # 从普通列表移动
                    log.info(f"正在将 {len(item_ids)} 个项目移动到分区 {partition_id}")
                    if self.db.move_items_to_partition(item_ids, partition_id):
                        self.partitionsUpdated.emit()
                
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            # --- 处理内部拖拽排序 ---
            dragged_item = self.currentItem()
            if not dragged_item:
                event.ignore()
                return

            if target_type == 'trash':
                # 将一个内部项目（分组/分区/数据项）拖到回收站
                log.info(f"正在通过内部拖拽删除项目 '{dragged_item.text(0)}'")
                # 复用现有的删除方法，它包含了确认对话框
                self.parent()._delete_item(dragged_item)
                event.acceptProposedAction()
            else:
                # 正常的排序操作
                super().dropEvent(event)
                self._update_database_from_tree_state()
    
    def _update_database_from_tree_state(self):
        """遍历整个树，并将新的结构和顺序持久化到数据库中"""
        group_sort_index = 0
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            data = item.data(0, Qt.UserRole)

            if data and data.get('type') == 'group':
                group_id = data['id']
                self.db.update_partition_group(group_id, sort_index=float(group_sort_index))
                group_sort_index += 1

                partition_sort_index = 0
                for j in range(item.childCount()):
                    part_item = item.child(j)
                    part_data = part_item.data(0, Qt.UserRole)
                    if part_data and part_data.get('type') == 'partition':
                        part_id = part_data['id']
                        # 检查分区是否被移动到了一个新的组
                        original_group_id = part_data.get('group_id')
                        if original_group_id != group_id:
                            log.info(f"分区 {part_id} 已从组 {original_group_id} 移动到组 {group_id}。")
                            # 应用新组的标签到该分区的所有现有项目
                            self.db.apply_group_tags_to_partition_items(group_id, part_id)
                        
                        self.db.update_partition(part_id, group_id=group_id, sort_index=float(partition_sort_index))
                        partition_sort_index += 1
        
        log.info("分区顺序和结构已通过拖放更新。")
        self.partitionsUpdated.emit()


class PartitionPanel(QWidget):
    """
    分区管理面板
    """
    partitionSelectionChanged = pyqtSignal(object)
    itemSelectedInList = pyqtSignal(int)
    partitionsUpdated = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.tree = None
        self.predefined_colors = [
            "#FF5733", "#33FF57", "#3357FF", "#FF33A1", "#A133FF",
            "#33FFA1", "#FFC300", "#C70039", "#900C3F", "#581845"
        ]
        self._init_ui()
        self.refresh_partitions()

    def _init_ui(self):
        """初始化UI组件"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tree = PartitionTreeWidget(self.db, self)
        self.tree.setObjectName("PartitionTree")
        
        # 核心修复：禁用组件自带的双击展开功能，防止与我们的自定义逻辑冲突
        self.tree.setExpandsOnDoubleClick(False)
        # 核心修复：禁用所有鼠标交互的展开功能（包括单击隐藏箭头），确保只有我们的代码能控制展开
        self.tree.setItemsExpandable(False)
        
        # 隐藏箭头并连接双击事件
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        self.tree.customContextMenuRequested.connect(self._show_context_menu)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.partitionsUpdated.connect(self.partitionsUpdated.emit) # 直接转发信号
        
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def _on_item_double_clicked(self, item, column):
        """处理项的双击事件，仅用于展开/折叠"""
        log.debug(f"双击事件触发于项目: {item.text(0)}")
        item_data = item.data(0, Qt.UserRole)
        if item_data and item_data.get('type') in ['group', 'partition']:
            item.setExpanded(not item.isExpanded())
            log.debug(f"项目 '{item.text(0)}' 的新展开状态: {item.isExpanded()}")

    def _create_color_icon(self, color_str):
        """根据颜色字符串创建一个方形图标"""
        if not color_str: color_str = "#808080"
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(color_str))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(2, 2, 12, 12, 3, 3)
        painter.end()
        return QIcon(pixmap)

    def refresh_partitions(self):
        """从数据库加载并显示分区"""
        current_selection = self.get_current_selection()
        self.tree.clear()
        
        counts = self.db.get_partition_item_counts()
        partition_counts = counts.get('partitions', {})
        group_counts = counts.get('groups', {})
        
        total_items = sum(partition_counts.values()) + counts.get('uncategorized', 0)
        all_data_item = QTreeWidgetItem(self.tree, [f"全部数据 ({total_items})"])
        all_data_item.setData(0, Qt.UserRole, {'type': 'all', 'id': -1})
        all_data_item.setFont(0, QFont("Arial", 10, QFont.Bold))
        all_data_item.setIcon(0, self.style().standardIcon(QStyle.SP_DirHomeIcon))
        all_data_item.setFlags(all_data_item.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

        # 添加 未分类 选项
        uncategorized_count = counts.get('uncategorized', 0)
        uncategorized_item = QTreeWidgetItem(self.tree, [f"未分类 ({uncategorized_count})"])
        uncategorized_item.setData(0, Qt.UserRole, {'type': 'uncategorized', 'id': -2})
        uncategorized_item.setFont(0, QFont("Arial", 10, QFont.Bold))
        uncategorized_item.setIcon(0, self.style().standardIcon(QStyle.SP_MessageBoxWarning))
        uncategorized_item.setFlags(uncategorized_item.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)
        
        # 添加 未标签 选项
        untagged_count = counts.get('untagged', 0)
        untagged_item = QTreeWidgetItem(self.tree, [f"未标签 ({untagged_count})"])
        untagged_item.setData(0, Qt.UserRole, {'type': 'untagged', 'id': -3})
        untagged_item.setFont(0, QFont("Arial", 10, QFont.Bold))
        untagged_item.setIcon(0, self.style().standardIcon(QStyle.SP_DialogHelpButton))
        untagged_item.setFlags(untagged_item.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

        # 添加 回收站 选项
        trash_count = counts.get('trash', 0)
        trash_item = QTreeWidgetItem(self.tree, [f"回收站 ({trash_count})"])
        trash_item.setData(0, Qt.UserRole, {'type': 'trash', 'id': -4})
        trash_item.setFont(0, QFont("Arial", 10, QFont.Bold))
        trash_item.setIcon(0, self.style().standardIcon(QStyle.SP_TrashIcon))
        trash_item.setFlags(trash_item.flags() & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

        groups = self.db.get_partitions_tree()
        for group in groups:
            count = group_counts.get(group.id, 0)
            group_item = QTreeWidgetItem(self.tree, [f"{group.name} ({count})"])
            group_item.setData(0, Qt.UserRole, {'type': 'group', 'id': group.id, 'color': group.color})
            group_item.setFont(0, QFont("Arial", 10, QFont.Bold))
            group_item.setIcon(0, self._create_color_icon(group.color))
            group_item.setFlags(group_item.flags() & ~Qt.ItemIsDropEnabled)

            for partition in group.partitions:
                count = partition_counts.get(partition.id, 0)
                part_item = QTreeWidgetItem(group_item, [f"{partition.name} ({count})"])
                part_item.setData(0, Qt.UserRole, {'type': 'partition', 'id': partition.id, 'color': partition.color, 'group_id': group.id})
                part_item.setIcon(0, QIcon("ui/icons/partition_icon.png"))
        
        self.tree.expandAll()
        
        if current_selection:
            self.select_item_by_data(current_selection)
        else:
            self.tree.setCurrentItem(all_data_item)

    def select_item_by_data(self, data_to_find):
        """根据数据在树中查找并选中对应的项"""
        if not data_to_find or 'type' not in data_to_find or 'id' not in data_to_find:
            return
        
        iterator = QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            item = iterator.value()
            item_data = item.data(0, Qt.UserRole)
            if item_data and item_data.get('id') == data_to_find.get('id') and item_data.get('type') == data_to_find.get('type'):
                self.tree.setCurrentItem(item)
                return
            iterator += 1

    def _on_selection_changed(self):
        """
        当选择项变化时，根据项目类型发射不同的信号。
        - 分组/分区/静态项: 发射 partitionSelectionChanged 信号以刷新主列表 (筛选)。
        - 数据项: 发射 itemSelectedInList 信号以高亮主列表中的对应项 (高亮)。
        """
        data = self.get_current_selection()
        if not data:
            return

        item_type = data.get('type')
        
        # 点击的是分组、分区或静态类别，发射筛选信号
        if item_type == 'all':
            self.partitionSelectionChanged.emit(None)
        else:
            self.partitionSelectionChanged.emit(data)

    def _show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu()
        item = self.tree.itemAt(pos)
        
        if item:
            item_data = item.data(0, Qt.UserRole)
            item_type = item_data.get('type')
            
            if item_type in ['all', 'uncategorized', 'untagged', 'trash']:
                return

            if item_type == 'group':
                menu.addAction("添加分区", lambda: self._add_partition(item))
                menu.addAction("设置预设标签", lambda: self._set_group_tags(item))
                menu.addAction("修改颜色", lambda: self._change_item_color(item))
                menu.addSeparator()
            elif item_type == 'partition':
                menu.addAction("设置预设标签", lambda: self._set_partition_tags(item))
                menu.addAction("修改颜色", lambda: self._change_item_color(item))
                menu.addSeparator()

            menu.addAction("重命名", lambda: self._rename_item(item))
            menu.addAction("删除", lambda: self._delete_item(item))
        else:
            menu.addAction("添加分组", self._add_group)
            
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def _get_random_color(self):
        """从预定义颜色列表中随机选择一个"""
        return random.choice(self.predefined_colors)

    def _add_group(self):
        """添加新分组"""
        name, ok = QInputDialog.getText(self, "添加分组", "请输入分组名称:", QLineEdit.Normal, "")
        if ok and name:
            new_group = self.db.add_partition_group(name)
            if new_group:
                random_color = self._get_random_color()
                self.db.update_partition_group(new_group.id, color=random_color)
                self.refresh_partitions()
                self.partitionsUpdated.emit()
            else:
                QMessageBox.warning(self, "错误", "分组名称已存在或无效。")

    def _add_partition(self, group_item):
        """在分组下添加新分区"""
        group_data = group_item.data(0, Qt.UserRole)
        name, ok = QInputDialog.getText(self, "添加分区", "请输入分区名称:", QLineEdit.Normal, "")
        if ok and name:
            new_partition = self.db.add_partition(name, group_data['id'])
            if new_partition:
                group_color = group_data.get('color')
                if group_color:
                    self.db.update_partition(new_partition.id, color=group_color)
                self.refresh_partitions()
                self.partitionsUpdated.emit()

    def _change_item_color(self, item):
        """修改分组或分区的颜色"""
        item_data = item.data(0, Qt.UserRole)
        current_color_str = item_data.get('color', '#FFFFFF')
        color = QColorDialog.getColor(QColor(current_color_str), self, "选择颜色")
        if color.isValid():
            if item_data['type'] == 'group':
                self.db.update_partition_group(item_data['id'], color=color.name())
            else:
                self.db.update_partition(item_data['id'], color=color.name())
            self.refresh_partitions()
            self.partitionsUpdated.emit()

    def _rename_item(self, item):
        """重命名分组或分区"""
        item_data = item.data(0, Qt.UserRole)
        original_text = item.text(0)
        old_name = original_text.split(' (')[0]
        
        new_name, ok = QInputDialog.getText(self, f"重命名", "请输入新名称:", QLineEdit.Normal, old_name)
        if ok and new_name and new_name != old_name:
            if item_data['type'] == 'group':
                self.db.rename_partition_group(item_data['id'], new_name)
            else:
                self.db.rename_partition(item_data['id'], new_name)
            self.refresh_partitions()
            self.partitionsUpdated.emit()

    def _delete_item(self, item):
        """删除分组、分区或单个数据项，并提供操作反馈。"""
        if not item:
            return
            
        item_data = item.data(0, Qt.UserRole)
        item_type = item_data.get('type')
        
        # 防止删除静态项目
        if item_type not in ['group', 'partition']:
            log.warning(f"尝试删除一个无效类型的项目: {item_type}")
            return
        
        item_name = item.text(0).split(' (')[0]
        
        if item_type in ['group', 'partition']:
            # 删除分组或分区
            item_type_text = "分组" if item_type == 'group' else '分区'
            reply = QMessageBox.question(self, f"确认删除", f"确定要删除 {item_type_text} '{item_name}' 吗？\n此操作会将其包含的所有数据移至回收站。",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                success = False
                if item_type == 'group':
                    success = self.db.delete_partition_group(item_data['id'])
                else: # partition
                    success = self.db.delete_partition(item_data['id'])
                
                if success:
                    self.refresh_partitions()
                    self.partitionsUpdated.emit()
                else:
                    QMessageBox.warning(self, "删除失败", f"无法删除 {item_type_text} '{item_name}'。\n请检查日志以获取详细信息。")
    
    def _set_partition_tags(self, item):
        """为分区设置预设标签"""
        item_data = item.data(0, Qt.UserRole)
        current_tags_str = ", ".join(self.db.get_partition_tags(item_data['id']))
        new_tags_str, ok = QInputDialog.getText(self, "设置预设标签", "请输入标签（用逗号分隔）:", 
                                                QLineEdit.Normal, current_tags_str)
        if ok:
            tag_names = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
            self.db.set_partition_tags(item_data['id'], tag_names)
            self.partitionsUpdated.emit()

    def _set_group_tags(self, item):
        """为分组设置预设标签"""
        item_data = item.data(0, Qt.UserRole)
        current_tags_str = ", ".join(self.db.get_partition_group_tags(item_data['id']))
        new_tags_str, ok = QInputDialog.getText(self, "设置分组预设标签", "请输入标签（用逗号分隔）:", 
                                                QLineEdit.Normal, current_tags_str)
        if ok:
            tag_names = [tag.strip() for tag in new_tags_str.split(',') if tag.strip()]
            self.db.set_partition_group_tags(item_data['id'], tag_names)
            self.partitionsUpdated.emit()
            
    def get_current_selection(self):
        """获取当前选择项的数据"""
        item = self.tree.currentItem()
        if item:
            return item.data(0, Qt.UserRole)
        return None
