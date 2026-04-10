"""
GitHub 仓库本地更新工具

批量检查和更新本地 GitHub 仓库的自动化工具。

功能：
- 批量检查多个仓库是否有更新
- 自动拉取有更新的仓库
- 扫描目录批量处理所有 Git 仓库
- 将更新记录保存到 CSV 文件

使用方法：
    # 扫描指定目录下的所有仓库
    python update_github_repos.py -d <目录路径>
    python update_github_repos.py --dir <目录路径>

    # 直接指定仓库路径（多个）
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
from git_ops import check_repo_update, pull_repo, scan_git_repos
from csv_writer import log_update_result
from config import get_exclude_dirs

# 尝试导入常量模块，如果失败则使用默认值
try:
    from constants import ErrorMessages, StatusMessages
    
    # 错误消息常量（保持向后兼容）
    ERROR_PATH_NOT_EXIST = ErrorMessages.PATH_NOT_EXIST
    ERROR_NOT_DIRECTORY = ErrorMessages.NOT_DIRECTORY
    ERROR_NOT_GIT_REPO = ErrorMessages.NOT_GIT_REPO
    ERROR_CHECK_FAILED = ErrorMessages.CHECK_FAILED
    ERROR_PULL_FAILED = ErrorMessages.PULL_FAILED
    ERROR_PATH_NOT_SAFE = ErrorMessages.PATH_NOT_SAFE
    STATUS_UP_TO_DATE = StatusMessages.UP_TO_DATE
except ImportError:
    # 如果 constants 模块不存在，使用默认值
    ERROR_PATH_NOT_EXIST = "路径不存在"
    ERROR_NOT_DIRECTORY = "路径不是目录"
    ERROR_NOT_GIT_REPO = "不是 Git 仓库"
    ERROR_CHECK_FAILED = "检查更新失败"
    ERROR_PULL_FAILED = "拉取更新失败"
    ERROR_PATH_NOT_SAFE = "路径不安全"
    STATUS_UP_TO_DATE = "已是最新"


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
    同时验证当前目录是否可写

    返回值:
        CSV 文件名（字符串）
    
    异常:
        IOError: 当前目录不可写时抛出
    """
    filename = f"result_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # 验证当前目录是否可写
    try:
        test_path = os.path.join(os.getcwd(), '.test_write')
        with open(test_path, 'w') as f:
            f.write('test')
        os.remove(test_path)
    except (IOError, OSError) as e:
        logger.error(f"当前目录不可写: {os.getcwd()}")
        raise IOError(f"当前目录不可写，请检查权限: {os.getcwd()}") from e
    
    return filename


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
    
    # 解析命令行参数，支持两种模式：
    # 1. -d/--dir <目录>：扫描目录下所有 Git 仓库
    # 2. -h/--help：显示帮助信息
    # 3. 直接指定仓库路径：处理指定的仓库列表
    target_repos = []
    scan_mode = False
    preview_mode = False
    
    # 检查帮助参数
    if args and args[0] in ('-h', '--help'):
        print("使用方法：")
        print("  # 扫描指定目录下的所有 Git 仓库（预览模式）")
        print("  python update_github_repos.py -d <目录路径> --preview")
        print("  python update_github_repos.py --dir <目录路径> --preview")
        print()
        print("  # 扫描指定目录并更新所有仓库")
        print("  python update_github_repos.py -d <目录路径>")
        print("  python update_github_repos.py --dir <目录路径>")
        print()
        print("  # 直接指定仓库路径（多个）")
        print("  python update_github_repos.py <repo_path1> [repo_path2] ...")
        print()
        print("配置文件：")
        print("  config.json - 排除目录、超时配置")
        return 0
    
    # 检查是否有 --preview 参数
    if '--preview' in args:
        preview_mode = True
        args = [a for a in args if a != '--preview']
    
    if args:
        if args[0] in ('-d', '--dir'):
            # 目录扫描模式
            if len(args) < 2:
                print("[错误] 请提供目录路径")
                print()
                print("使用方法：")
                print("  python update_github_repos.py -d <目录路径>")
                print("  python update_github_repos.py --dir <目录路径>")
                return 1
            
            target_dir = args[1]
            
            # 检查目录是否存在
            if not os.path.isdir(target_dir):
                print(f"[错误] 目录不存在: {target_dir}")
                return 1
            
            # 扫描目录获取仓库列表
            exclude_dirs = get_exclude_dirs()
            print(f"扫描目录: {target_dir}")
            print(f"排除目录: {exclude_dirs}")
            print()
            
            target_repos = scan_git_repos(target_dir, exclude_dirs)
            scan_mode = True
            
            if not target_repos:
                print("[警告] 未发现任何 Git 仓库")
                return 0
            
            print(f"发现 {len(target_repos)} 个仓库")
            print()
        else:
            # 直接指定仓库路径模式
            target_repos = args
    
    # 验证参数
    if not target_repos:
        print("[错误] 请提供至少一个仓库路径")
        print()
        print("使用方法：")
        print("  # 扫描目录")
        print("  python update_github_repos.py -d <目录路径>")
        print()
        print("  # 直接指定仓库")
        print("  python update_github_repos.py <repo_path1> [repo_path2] ...")
        return 1

    # 打印开始信息
    mode_text = "扫描目录" if scan_mode else "检查仓库"
    print(f"开始{mode_text}更新...")
    print("=" * 50)
    print()

    # 预览模式：只列出需要更新的仓库，不执行更新
    if preview_mode:
        print("预览模式：只显示需要更新的仓库")
        print("=" * 50)
        print()
        
        repos_need_update = []
        repos_up_to_date = []
        repos_error = []
        
        for repo_path in target_repos:
            repo_name = extract_repo_name(repo_path)
            has_update = check_repo_update(repo_path)
            
            if has_update is None:
                repos_error.append((repo_name, repo_path, "检查失败"))
            elif has_update:
                repos_need_update.append((repo_name, repo_path))
            else:
                repos_up_to_date.append((repo_name, repo_path))
        
        # 显示需要更新的仓库
        print(f"需要更新的仓库 ({len(repos_need_update)} 个)：")
        print("-" * 50)
        for repo_name, repo_path in repos_need_update:
            print(f"  [需更新] {repo_name}")
            print(f"          {repo_path}")
        print()
        
        # 显示已是最新仓库
        print(f"已是最新 ({len(repos_up_to_date)} 个)：")
        print("-" * 50)
        for repo_name, repo_path in repos_up_to_date:
            print(f"  [最新] {repo_name}")
        print()
        
        # 显示错误仓库
        if repos_error:
            print(f"检查失败 ({len(repos_error)} 个)：")
            print("-" * 50)
            for repo_name, repo_path, error in repos_error:
                print(f"  [错误] {repo_name}")
                print(f"          {error}")
            print()
        
        print("=" * 50)
        print(f"总计：{len(target_repos)} 个仓库")
        print(f"  需要更新: {len(repos_need_update)}")
        print(f"  已是最新: {len(repos_up_to_date)}")
        print(f"  检查失败: {len(repos_error)}")
        print("=" * 50)
        print()
        print("如需更新仓库，请去掉 --preview 参数重新运行")
        
        return 0

    # 生成 CSV 文件名
    csv_path = get_csv_filename()

    # 初始化统计计数器
    total = len(target_repos)
    success = 0

    # 遍历处理每个仓库
    for index, repo_path in enumerate(target_repos, 1):
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
