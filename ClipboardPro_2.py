# -*- coding: utf-8 -*-
import sys
import logging
import traceback
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# === 配置日志 ===
# 创建日志格式
log_format = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_format)

# 文件输出
file_handler = logging.FileHandler('debug.log', encoding='utf-8', mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_format)

# 配置根日志
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

log = logging.getLogger("Main")

def exception_hook(exctype, value, tb):
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    log.critical(f"🔥 崩溃信息:\n{error_msg}")
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

def main():
    log.info("🚀 启动印象记忆_Pro (QuickPanel 主窗口版)...")
    
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("ClipboardManagerPro")
    
    # 单实例检测
    from PyQt5.QtCore import QSharedMemory
    shared_mem = QSharedMemory("ClipboardPro_SingleInstance")
    
    if shared_mem.attach():
        # 已有实例在运行
        log.info("检测到旧实例，正在清理...")
        shared_mem.detach()
        # 清理并创建新的
        if shared_mem.create(1):
            log.info("✅ 已清理旧实例，启动新实例")
    else:
        # 首次运行
        if not shared_mem.create(1):
            log.error("❌ 无法创建单实例锁")
            return

    try:
        # 导入新的主窗口和数据库管理器
        from quick_panel import QuickPanel
        from data.database import DBManager
        
        # 创建实例
        db_manager = DBManager()
        window = QuickPanel(db_manager=db_manager)

        # 显示并居中窗口
        window.show()
        screen_geo = app.desktop().screenGeometry()
        panel_geo = window.geometry()
        window.move((screen_geo.width() - panel_geo.width()) // 2, (screen_geo.height() - panel_geo.height()) // 2)
        window.search_box.setFocus()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        log.critical(f"❌ 启动失败: {e}", exc_info=True)

if __name__ == "__main__":
    main()
