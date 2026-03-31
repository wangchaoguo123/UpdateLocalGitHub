import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import validate_repo_path, extract_repo_name
from git_ops import check_repo_update, pull_repo
from csv_writer import log_update_result


def print_header():
    print("=" * 50)
    print("  GitHub 仓库本地更新工具")
    print("=" * 50)
    print()


def get_csv_filename():
    return f"result_{datetime.now().strftime('%Y%m%d')}.csv"


def process_repo(repo_path, csv_path, index, total):
    repo_name = extract_repo_name(repo_path)

    print(f"[仓库 {index}/{total}] {repo_path}")
    print("[检查] 正在检查更新...")

    if not os.path.exists(repo_path):
        print(f"[错误] 路径不存在")
        log_update_result(repo_name, repo_path, "error: 路径不存在", csv_path)
        return False

    if not os.path.isdir(repo_path):
        print(f"[错误] 路径不是目录")
        log_update_result(repo_name, repo_path, "error: 路径不是目录", csv_path)
        return False

    if not validate_repo_path(repo_path):
        print(f"[错误] 不是 Git 仓库")
        log_update_result(repo_name, repo_path, "error: 不是 Git 仓库", csv_path)
        return False

    has_update = check_repo_update(repo_path)

    if has_update is None:
        print(f"[错误] 检查更新失败")
        log_update_result(repo_name, repo_path, "error: 检查更新失败", csv_path)
        return False

    if has_update:
        print("[结果] 发现更新，正在拉取...")
        result = pull_repo(repo_path)
        if result:
            print(f"[输出] {result}")
            print(f"[记录] 已记录到 {os.path.basename(csv_path)}")
            log_update_result(repo_name, repo_path, result, csv_path)
            return True
        else:
            print(f"[错误] 拉取更新失败")
            log_update_result(repo_name, repo_path, "error: 拉取更新失败", csv_path)
            return False
    else:
        print("[结果] 已是最新，无需更新")
        print(f"[记录] 已记录到 {os.path.basename(csv_path)}")
        log_update_result(repo_name, repo_path, "Already up to date.", csv_path)
        return True


def main(args):
    print_header()

    if not args:
        print("[错误] 请提供至少一个仓库路径")
        print()
        print("使用方法：")
        print("  python update_github_repos.py <repo_path1> [repo_path2] ...")
        return 1

    print("开始检查仓库更新...")
    print("=" * 50)
    print()

    csv_path = get_csv_filename()
    total = len(args)
    success = 0

    for index, repo_path in enumerate(args, 1):
        try:
            if process_repo(repo_path, csv_path, index, total):
                success += 1
            print()
        except Exception as e:
            print(f"[错误] 处理仓库时发生异常: {str(e)}")
            print()

    print("=" * 50)
    print(f"完成！共处理 {total} 个仓库，成功 {success} 个，失败 {total - success} 个")
    print("=" * 50)

    return 0


def main_with_csv(args, csv_path):
    if not args:
        return 1

    total = len(args)
    success = 0

    for index, repo_path in enumerate(args, 1):
        try:
            if process_repo(repo_path, csv_path, index, total):
                success += 1
        except Exception as e:
            pass

    return 0


if __name__ == '__main__':
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
