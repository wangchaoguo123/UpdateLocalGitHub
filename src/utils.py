"""
工具函数模块

提供路径验证、名称提取等通用工具函数。
"""

import os


def validate_repo_path(repo_path):
    """
    验证路径是否为有效的 Git 仓库

    检查步骤：
    1. 检查路径是否存在
    2. 检查是否为目录
    3. 检查 .git 目录或文件是否存在

    注意：支持 Git worktree（.git 可能是文件）

    参数:
        repo_path: 仓库路径（字符串）

    返回值:
        True: 有效 Git 仓库
        False: 无效路径或非 Git 仓库
    """
    # 第一步：检查路径是否存在
    if not os.path.exists(repo_path):
        return False

    # 第二步：检查是否为目录
    if not os.path.isdir(repo_path):
        return False

    # 第三步：检查 .git 目录或文件是否存在
    # 注意：在 Git worktree 中，.git 是一个文件而非目录
    git_path = os.path.join(repo_path, '.git')
    return os.path.exists(git_path)


def extract_repo_name(repo_path):
    r"""
    从完整路径提取仓库名称

    示例：
    - 'D:\code\repo1' -> 'repo1'
    - '/home/user/my-repo' -> 'my-repo'

    参数:
        repo_path: 仓库路径（字符串）

    返回值:
        仓库名称（字符串），如果输入为空则返回空字符串
    """
    # 处理空路径
    if not repo_path:
        return ""

    # 移除尾部的路径分隔符
    repo_path = repo_path.rstrip(os.sep)

    # 提取最后一部分作为仓库名
    return os.path.basename(repo_path)


def format_update_message(message):
    """
    格式化更新消息，将多行文本合并为单行

    用于将 Git 命令的多行输出转换为适合 CSV 存储的单行格式。

    参数:
        message: 原始消息（字符串）

    返回值:
        格式化后的消息（换行符替换为空格）
    """
    # 处理空值
    if not message:
        return ""

    # 替换换行符为空格，保持消息为单行
    return message.replace('\n', ' ').replace('\r', '')
