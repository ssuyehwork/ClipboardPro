# -*- coding: utf-8 -*-
"""
图片处理器
处理图片剪贴板数据（新功能）
"""
import logging
import os
import sys
import hashlib
from datetime import datetime
from PyQt5.QtCore import QMimeData
from PyQt5.QtGui import QImage
from handlers.base_handler import BaseHandler

log = logging.getLogger("ImageHandler")


class ImageHandler(BaseHandler):
    """图片处理器"""
    
    def __init__(self):
        super().__init__(priority=10) # 修正：必须调用基类初始化以获取 last_content 等属性
        # 修复：使用绝对路径，避免在不同工作目录下出错
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            
        self.image_dir = os.path.join(base_dir, "data", "images")
        self._ensure_image_dir()
    
    def _ensure_image_dir(self):
        """确保图片目录存在"""
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir, exist_ok=True)
    
    def can_handle(self, mime_data: QMimeData) -> bool:
        """判断是否为图片数据"""
        return mime_data.hasImage()
    
    def handle(self, mime_data: QMimeData, db_manager, partition_info: dict = None):
        """处理图片数据"""
        try:
            image = mime_data.imageData()
            if not image or image.isNull():
                log.warning("图片数据为空")
                return None, False
            
            # 转换为QImage
            qimage = QImage(image)
            if qimage.isNull():
                log.warning("无法解析图片")
                return None, False
            
            # 生成唯一文件名（基于时间戳和图片哈希）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 计算图片哈希用于去重
            ba = qimage.bits().asstring(qimage.byteCount())
            img_hash = hashlib.md5(ba).hexdigest()[:8]
            
            # 去重检查
            if self._is_duplicate(img_hash):
                log.debug("图片重复，跳过")
                return None, False
            
            # 保存图片
            filename = f"img_{timestamp}_{img_hash}.png"
            image_path = os.path.join(self.image_dir, filename)
            
            if not qimage.save(image_path, "PNG"):
                log.error(f"保存图片失败: {image_path}")
                return None, False
            
            # 生成缩略图
            thumbnail_path = self._create_thumbnail(qimage, timestamp, img_hash)
            
            partition_id = partition_info.get('id') if partition_info and partition_info.get('type') == 'partition' else None
            
            # 保存到数据库
            item, is_new = db_manager.add_item(
                text=f"[图片] {filename}",
                item_type='image',
                is_file=False,
                image_path=image_path,
                thumbnail_path=thumbnail_path,
                partition_id=partition_id
            )
            
            if is_new:
                size_kb = os.path.getsize(image_path) / 1024
                log.info(f"✅ 捕获图片: {filename} ({size_kb:.1f}KB)")

            return item, is_new
            
        except Exception as e:
            log.error(f"图片处理失败: {e}", exc_info=True)
            return None, False
    
    def _create_thumbnail(self, qimage: QImage, timestamp: str, img_hash: str) -> str:
        """
        创建缩略图
        
        Args:
            qimage: 原始图片
            timestamp: 时间戳
            img_hash: 图片哈希
            
        Returns:
            str: 缩略图路径
        """
        try:
            # 缩略图尺寸
            thumb_size = 200
            
            # 等比例缩放
            thumbnail = qimage.scaled(
                thumb_size, thumb_size,
                aspectRatioMode=1,  # Qt.KeepAspectRatio
                transformMode=1     # Qt.SmoothTransformation
            )
            
            # 保存缩略图
            thumb_filename = f"thumb_{timestamp}_{img_hash}.png"
            thumb_path = os.path.join(self.image_dir, thumb_filename)
            
            if thumbnail.save(thumb_path, "PNG"):
                return thumb_path
            else:
                log.warning("缩略图保存失败")
                return None
                
        except Exception as e:
            log.error(f"创建缩略图失败: {e}")
            return None
