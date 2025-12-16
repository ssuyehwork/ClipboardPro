# diagnose_startup.py
import logging
import sys
from data.database import DBManager, ClipboardItem

# 配置日志记录，以便我们可以看到详细的输出
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("Diagnose")

def run_diagnosis():
    log.info("--- 开始诊断 ---")
    
    try:
        # 1. 初始化 DBManager，这将触发 _check_migrations
        log.info("正在初始化 DBManager...")
        db = DBManager()
        log.info("DBManager 初始化成功。")
        
        # 2. 尝试执行一个依赖于新列的查询
        log.info("尝试查询 partition_id 列...")
        session = db.get_session()
        
        # 尝试获取第一个项目的 partition_id
        # 如果列不存在，这应该会失败
        result = session.query(ClipboardItem.partition_id).first()
        
        session.close()
        
        log.info(f"查询成功。结果 (可能是 None): {result}")
        log.info("诊断成功：数据库迁移逻辑似乎已正确执行。")
        
    except Exception as e:
        log.error(f"诊断失败: {e}", exc_info=True)
        sys.exit(1) # 以错误码退出

    log.info("--- 诊断结束 ---")

if __name__ == "__main__":
    run_diagnosis()
