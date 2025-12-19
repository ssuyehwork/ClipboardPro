# -*- coding: utf-8 -*-
import sys
import os

# 将项目根目录添加到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import DBManager

def print_banner(title):
    print("\n" + "="*50)
    print(f"===== {title.center(40)} =====")
    print("="*50)

def assert_equal(val1, val2, msg):
    if val1 == val2:
        print(f"✅ PASSED: {msg}")
    else:
        print(f"❌ FAILED: {msg}. Expected {val2}, got {val1}")
        # 在失败时抛出异常以停止脚本
        raise AssertionError(f"FAILED: {msg}. Expected {val2}, got {val1}")

def run_verification():
    """自动化验证脚本"""
    db_path = "verification_test.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    db = DBManager(db_name=db_path)
    session = db.get_session()

    # 1. 初始化
    print_banner("1. 初始化和数据准备")
    
    # 清理所有表
    from data.database import Partition, ClipboardItem, Tag, item_tags
    session.execute(item_tags.delete())
    session.query(ClipboardItem).delete()
    session.query(Partition).delete()
    session.query(Tag).delete()
    session.commit()
    print("数据库已清理。")

    # 创建分区结构 (使用新的递归模型)
    # "工作" 是顶级分区 (parent_id is None)
    group1 = db.add_partition("工作", parent_id=None)
    part1 = db.add_partition("项目A", parent_id=group1.id)
    part2 = db.add_partition("项目B", parent_id=group1.id)
    # "个人" 是另一个顶级分区
    group2 = db.add_partition("个人", parent_id=None)
    part3 = db.add_partition("学习", parent_id=group2.id)

    # 添加数据项
    db.add_item("这是项目A的第一个笔记", partition_id=part1.id)
    item2, _ = db.add_item("这是项目A的第二个笔记", partition_id=part1.id)
    db.add_item("这是项目B的笔记", partition_id=part2.id)
    db.add_item("学习Python", partition_id=part3.id)
    item5, _ = db.add_item("学习SQL", partition_id=part3.id)
    db.add_item("未分类的笔记1")
    item7, _ = db.add_item("未分类的笔记2")
    
    # 添加标签
    db.add_tags_to_items([item2.id], ["重要", "紧急"])
    db.add_tags_to_items([item5.id], ["重要"])
    
    print("测试数据准备完毕。")

    # 2. 验证初始计数
    print_banner("2. 验证初始计数")
    counts = db.get_partition_item_counts()
    
    assert_equal(counts.get('uncategorized', 0), 2, "未分类计数")
    assert_equal(counts.get('trash', 0), 0, "回收站计数")
    assert_equal(counts.get('untagged', 0), 5, "未标签计数")
    
    # get_partition_item_counts 返回的 'partitions' key 包含所有后代的计数
    # 所以可以直接验证父分区 ("Group") 的计数
    assert_equal(counts.get('partitions', {}).get(part1.id, 0), 2, "分区 '项目A' 计数")
    assert_equal(counts.get('partitions', {}).get(part2.id, 0), 1, "分区 '项目B' 计数")
    assert_equal(counts.get('partitions', {}).get(part3.id, 0), 2, "分区 '学习' 计数")
    assert_equal(counts.get('partitions', {}).get(group1.id, 0), 3, "父分区 '工作' 计数")
    assert_equal(counts.get('partitions', {}).get(group2.id, 0), 2, "父分区 '个人' 计数")

    # 3. 验证删除子分区逻辑
    print_banner("3. 验证删除子分区逻辑")
    
    # 删除分区 part1 ("项目A")，其中包含2个项目
    print(f"正在删除分区 '项目A' (ID: {part1.id})...")
    db.delete_partition(part1.id)
    
    counts_after_del = db.get_partition_item_counts()
    
    assert_equal(counts_after_del.get('trash', 0), 2, "回收站计数 (删除分区后)")
    assert_equal(counts_after_del.get('partitions', {}).get(part1.id, 0), 0, "已删除分区 '项目A' 计数应为0")
    assert_equal(counts_after_del.get('partitions', {}).get(group1.id, 0), 1, "父分区 '工作' 计数 (删除子分区后)")

    # 4. 验证恢复逻辑
    print_banner("4. 验证恢复逻辑")
    
    # 恢复刚才删除的2个项目
    items_in_trash = session.query(ClipboardItem).filter_by(is_deleted=True).all()
    trash_ids = [item.id for item in items_in_trash]
    print(f"正在从回收站恢复 {len(trash_ids)} 个项目...")
    db.restore_items_from_trash(trash_ids)
    
    counts_after_restore = db.get_partition_item_counts()
    
    # 因为原分区 part1 已被删除，这2个项目应该被恢复到“未分类”
    assert_equal(counts_after_restore.get('trash', 0), 0, "回收站计数 (恢复后)")
    assert_equal(counts_after_restore.get('uncategorized', 0), 4, "未分类计数 (智能恢复后)")
    
    # 5. 验证删除父分区逻辑
    print_banner("5. 验证删除父分区逻辑")
    
    # 删除父分区 group2 ("个人")，它包含子分区 part3 ("学习")，part3 中有2个项目
    print(f"正在删除父分区 '个人' (ID: {group2.id})...")
    db.delete_partition(group2.id)
    
    counts_after_del_group = db.get_partition_item_counts()
    
    assert_equal(counts_after_del_group.get('trash', 0), 2, "回收站计数 (删除父分区后)")
    assert_equal(counts_after_del_group.get('partitions', {}).get(part3.id, 0), 0, "分区 '学习' 计数应为0 (随父分区删除)")
    assert_equal(counts_after_del_group.get('partitions', {}).get(group2.id, 0), 0, "父分区 '个人' 计数应为0")
    
    # 6. 验证带标签项目的恢复
    print_banner("6. 验证带标签项目的恢复和'未标签'计数")
    
    # 恢复刚才删除的2个项目 (其中1个是带标签的)
    items_in_trash_2 = session.query(ClipboardItem).filter_by(is_deleted=True).all()
    trash_ids_2 = [item.id for item in items_in_trash_2]
    db.restore_items_from_trash(trash_ids_2)
    
    counts_final = db.get_partition_item_counts()
    
    # 原分区 part3 已删除，恢复到“未分类”
    assert_equal(counts_final.get('uncategorized', 0), 6, "未分类计数 (最终)")
    # 恢复后，带标签的项目不应计入'未标签'
    # 初始5个untagged -> 删除项目A(2个untagged) -> 剩3个 -> 恢复项目A(2个untagged)到未分类 -> 5个
    # 删除个人(2个，1个untagged) -> 剩4个 -> 恢复个人(1个untagged) -> 5个
    assert_equal(counts_final.get('untagged', 0), 5, "'未标签'计数 (最终)")

    session.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    print("\n" + "="*50)
    print("===== VERIFICATION COMPLETE =====")
    print("="*50)

if __name__ == "__main__":
    run_verification()
