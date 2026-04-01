"""
GitHub 仓库本地更新工具

批量检查和更新本地 GitHub 仓库的自动化工具。

功能：
- 批量检查多个仓库是否有更新
- 自动拉取有更新的仓库
- 将更新记录保存到 CSV 文件

使用方法：
    python update_github_repos.py <repo_path1> [repo_path2] ...
"""

import sys
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 设置标准输出编码，确保中文正确显示
# 只在直接运行时重新包装输出，测试时保持原样
import io
if __name__ == '__main__':
    try:
        # 尝试使用 UTF-8
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError) as e:
        logger.debug(f"设置编码失败: {e}")

# 将 src 目录添加到模块搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import validate_repo_path, extract_repo_name
from git_ops import check_repo_update, pull_repo
from csv_writer import log_update_result

# 尝试导入常量模块，如果失败则使用默认值
try:
    from constants import ErrorMessages, StatusMessages
    
    # 错误消息常量（保持向后兼容）
    ERROR_PATH_NOT_EXIST = ErrorMessages.PATH_NOT_EXIST
    ERROR_NOT_DIRECTORY = ErrorMessages.NOT_DIRECTORY
    ERROR_NOT_GIT_REPO = ErrorMessages.NOT_GIT_REPO
    ERROR_CHECK_FAILED = ErrorMessages.CHECK_FAILED
    ERROR_PULL_FAILED = ErrorMessages.PULL_FAILED
    STATUS_UP_TO_DATE = StatusMessages.UP_TO_DATE
except ImportError:
    # 如果 constants 模块不存在，使用默认值
    ERROR_PATH_NOT_EXIST = "error: 路径不存在"
    ERROR_NOT_DIRECTORY = "error: 路径不是目录"
    ERROR_NOT_GIT_REPO = "error: 不是 Git 仓库"
    ERROR_CHECK_FAILED = "error: 检查更新失败"
    ERROR_PULL_FAILED = "error: 拉取更新失败"
    STATUS_UP_TO_DATE = "Already up to date."


def print_header():
    """打印程序标题"""
    print("=" * 50)
    print("  GitHub 仓库本地更新工具")
    print("=" * 50)
    print()


def get_csv_filename():
    """
    生成 CSV 文件名

    文件名格式：result_YYYYMMDD.csv

    返回值:
        CSV 文件名（字符串）
    """
    return f"result_{datetime.now().strftime('%Y%m%d')}.csv"


def process_repo(repo_path, csv_path, index, total):
    """
    处理单个仓库的更新流程

    执行步骤：
    1. 验证路径是否存在
    2. 验证是否为目录
    3. 验证是否为 Git 仓库
    4. 检查是否有更新
    5. 如有更新则拉取
    6. 记录结果到 CSV

    参数:
        repo_path: 仓库路径（字符串）
        csv_path: CSV 文件路径（字符串）
        index: 当前仓库序号（整数）
        total: 仓库总数（整数）

    返回值:
        True: 处理成功
        False: 处理失败
    """
    # 提取仓库名称用于显示和记录
    repo_name = extract_repo_name(repo_path)

    # 显示当前处理进度
    print(f"[仓库 {index}/{total}] {repo_path}")
    print("[检查] 正在检查更新...")

    # 步骤 1：验证路径是否存在
    if not os.path.exists(repo_path):
        print("[错误] 路径不存在")
        log_update_result(repo_name, repo_path, ERROR_PATH_NOT_EXIST, csv_path)
        return False

    # 步骤 2：验证是否为目录
    if not os.path.isdir(repo_path):
        print("[错误] 路径不是目录")
        log_update_result(repo_name, repo_path, ERROR_NOT_DIRECTORY, csv_path)
        return False

    # 步骤 3：验证是否为 Git 仓库
    if not validate_repo_path(repo_path):
        print("[错误] 不是 Git 仓库")
        log_update_result(repo_name, repo_path, ERROR_NOT_GIT_REPO, csv_path)
        return False

    # 步骤 4：检查是否有更新
    has_update = check_repo_update(repo_path)

    if has_update is None:
        print("[错误] 检查更新失败")
        log_update_result(repo_name, repo_path, ERROR_CHECK_FAILED, csv_path)
        return False

    # 步骤 5：如果有更新则拉取
    if has_update:
        print("[结果] 发现更新，正在拉取...")
        result = pull_repo(repo_path)

        if result:
            # 拉取成功，记录更新信息
            print(f"[输出] {result}")
            print(f"[记录] 已记录到 {os.path.basename(csv_path)}")
            log_update_result(repo_name, repo_path, result, csv_path)
            return True
        else:
            # 拉取失败
            print("[错误] 拉取更新失败")
            log_update_result(repo_name, repo_path, ERROR_PULL_FAILED, csv_path)
            return False
    else:
        # 无需更新
        print("[结果] 已是最新，无需更新")
        print(f"[记录] 已记录到 {os.path.basename(csv_path)}")
        log_update_result(repo_name, repo_path, STATUS_UP_TO_DATE, csv_path)
        return True


def main(args):
    """
    主函数：程序入口

    参数:
        args: 命令行参数列表（不含脚本名）

    返回值:
        0: 成功
        1: 失败（参数错误）
    """
    # 打印标题
    print_header()

    # 验证参数
    if not args:
        print("[错误] 请提供至少一个仓库路径")
        print()
        print("使用方法：")
        print("  python update_github_repos.py <repo_path1> [repo_path2] ...")
        return 1

    # 打印开始信息
    print("开始检查仓库更新...")
    print("=" * 50)
    print()

    # 生成 CSV 文件名
    csv_path = get_csv_filename()

    # 初始化统计计数器
    total = len(args)
    success = 0

    # 遍历处理每个仓库
    for index, repo_path in enumerate(args, 1):
        try:
            if process_repo(repo_path, csv_path, index, total):
                success += 1
            print()
        except Exception as e:
            # 捕获意外异常，确保程序不会崩溃
            print(f"[错误] 处理仓库时发生异常: {str(e)}")
            logger.exception(f"处理仓库 {repo_path} 时发生异常")
            print()

    # 打印统计信息
    print("=" * 50)
    print(f"完成！共处理 {total} 个仓库，成功 {success} 个，失败 {total - success} 个")
    print("=" * 50)

    return 0


def main_with_csv(args, csv_path):
    """
    主函数的变体：使用指定的 CSV 文件路径

    主要用于测试，允许指定 CSV 文件路径。

    参数:
        args: 仓库路径列表
        csv_path: CSV 文件路径

    返回值:
        0: 成功
        1: 失败
    """
    if not args:
        return 1

    total = len(args)
    success = 0

    for index, repo_path in enumerate(args, 1):
        try:
            if process_repo(repo_path, csv_path, index, total):
                success += 1
        except Exception as e:
            # 静默处理异常（用于测试场景）
            logger.error(f"处理仓库 {repo_path} 时发生异常: {e}")

    return 0


if __name__ == '__main__':
    # 程序入口
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
