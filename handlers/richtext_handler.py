# -*- coding: utf-8 -*-
import logging
from PyQt5.QtCore import QMimeData
from handlers.base_handler import BaseHandler

log = logging.getLogger("RichTextHandler")

class RichTextHandler(BaseHandler):
    """富文本处理器"""

    def __init__(self):
        super().__init__(priority=35) # 介于URL和纯文本之间

    def can_handle(self, mime_data: QMimeData) -> bool:
        return mime_data.hasHtml()

    def handle(self, mime_data: QMimeData, db_manager, partition_info: dict = None):
        try:
            html = mime_data.html()
            text = mime_data.text()

            # 使用纯文本内容进行去重检查
            if self._is_duplicate(text):
                log.debug("富文本内容重复，跳过")
                return None, False

            partition_id = partition_info.get('id') if partition_info and partition_info.get('type') == 'partition' else None

            item, is_new = db_manager.add_item(
                text=text, # 纯文本内容用于预览和搜索
                item_type='richtext',
                data_blob=html.encode('utf-8'), # 将HTML字符串编码为二进制数据
                partition_id=partition_id
            )

            if is_new:
                log.info(f"✅ 捕获富文本: {text[:50]}...")

            return item, is_new

        except Exception as e:
            log.error(f"富文本处理失败: {e}", exc_info=True)
            return None, False
