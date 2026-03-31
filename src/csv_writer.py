"""
CSV 写入模块

提供 CSV 文件的创建和追加功能，用于记录仓库更新历史。
"""

import csv
import os
from datetime import datetime
import logging

# 配置日志
logger = logging.getLogger(__name__)

# CSV 表头定义
CSV_HEADERS = ['仓库名称', '本地路径', '更新时间', '更新履历']


def get_current_time():
    """
    获取当前时间的格式化字符串

    返回值:
        格式化的时间字符串，格式：YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log_update_result(repo_name, repo_path, update_info, csv_path):
    """
    将仓库更新结果记录到 CSV 文件

    如果 CSV 文件不存在，会创建文件并写入表头；
    如果文件已存在，则直接追加记录。

    参数:
        repo_name: 仓库名称（字符串）
        repo_path: 本地路径（字符串）
        update_info: 更新履历或状态信息（字符串）
        csv_path: CSV 文件路径（字符串）

    返回值:
        True: 写入成功
        False: 写入失败
    """
    try:
        # 检查文件是否已存在
        file_exists = os.path.exists(csv_path)

        # 获取当前时间戳
        timestamp = get_current_time()

        # 以追加模式打开文件，使用带 BOM 的 UTF-8 编码，确保 Excel 能正确识别中文
        with open(csv_path, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # 如果文件不存在，先写入表头
            if not file_exists:
                writer.writerow(CSV_HEADERS)
                logger.info(f"创建 CSV 文件: {csv_path}")

            # 写入数据行
            writer.writerow([repo_name, repo_path, timestamp, update_info])

        logger.debug(f"记录已写入: {repo_name} -> {csv_path}")
        return True

    except PermissionError as e:
        logger.error(f"CSV 文件写入权限错误: {e}")
        return False
    except IOError as e:
        logger.error(f"CSV 文件 IO 错误: {e}")
        return False
    except Exception as e:
        logger.error(f"写入 CSV 时发生异常: {e}")
        return False
