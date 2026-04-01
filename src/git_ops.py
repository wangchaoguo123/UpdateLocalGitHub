"""
Git 操作模块

提供 Git 命令执行与结果解析功能。
"""

import subprocess
import os
import logging

# 配置日志
logger = logging.getLogger(__name__)


def analyze_git_error(result):
    """
    分析 Git 命令错误信息，提供更详细的错误描述

    参数:
        result: subprocess.CompletedProcess 对象

    返回值:
        错误描述字符串
    """
    error_parts = []
    
    # 检查 stderr 输出
    stderr = result.stderr.strip().lower() if result.stderr else ""
    stdout = result.stdout.strip().lower() if result.stdout else ""
    
    # 分析常见错误模式
    if 'not a git repository' in stderr or 'not a git repository' in stdout:
        error_parts.append("不是 Git 仓库")
    elif 'permission denied' in stderr:
        error_parts.append("权限被拒绝")
    elif 'connection refused' in stderr or 'could not resolve host' in stderr:
        error_parts.append("无法连接到远程仓库")
    elif 'local changes' in stderr or 'uncommitted changes' in stderr:
        error_parts.append("本地有未提交的更改")
    elif 'conflict' in stderr or 'merge conflict' in stderr:
        error_parts.append("存在合并冲突")
    elif 'fatal:' in stderr:
        error_parts.append(f"Git 错误: {result.stderr.strip()}")
    elif stderr:
        error_parts.append(f"错误: {result.stderr.strip()}")
    elif stdout:
        # stdout 也可能包含错误信息
        error_parts.append(f"输出: {result.stdout.strip()}")
    
    if not error_parts:
        error_parts.append("未知错误")
    
    return "; ".join(error_parts)


def validate_path_security(repo_path):
    """
    验证仓库路径的安全性

    参数:
        repo_path: 仓库路径（字符串）

    返回值:
        安全的规范化路径，如果路径不安全则返回 None
    """
    # 规范化路径，处理相对路径和符号链接
    safe_path = os.path.normpath(os.path.abspath(repo_path))

    # 检查路径长度（Windows 最大路径长度限制）
    if len(safe_path) > 260:
        logger.warning(f"路径过长: {safe_path}")
        return None

    return safe_path


def check_repo_update(repo_path):
    """
    检查仓库是否有新更新

    使用 git fetch 获取远程更新，然后比较本地和远程分支的差异。

    参数:
        repo_path: 仓库路径（字符串）

    返回值:
        True: 有新更新
        False: 无更新
        None: 执行失败
    """
    # 验证路径安全性
    safe_path = validate_path_security(repo_path)
    if safe_path is None:
        logger.error(f"路径验证失败: {repo_path}")
        return None

    try:
        # 步骤1: 获取远程更新
        fetch_cmd = ['git', 'fetch', '--prune']
        fetch_result = subprocess.run(
            fetch_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if fetch_result.returncode != 0:
            error_info = analyze_git_error(fetch_result)
            logger.warning(f"git fetch 返回错误码 {fetch_result.returncode}: {error_info}")
            return None

        # 步骤2: 获取当前分支名称
        branch_cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
        branch_result = subprocess.run(
            branch_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if branch_result.returncode != 0:
            logger.warning("无法获取当前分支名称")
            return None
            
        current_branch = branch_result.stdout.strip()
        
        # 步骤3: 检查是否有上游分支
        upstream_cmd = ['git', 'rev-parse', '--verify', '@{u}']
        upstream_result = subprocess.run(
            upstream_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if upstream_result.returncode != 0:
            # 没有设置上游分支，尝试使用 origin/分支名
            remote_branch = f'origin/{current_branch}'
            check_cmd = ['git', 'rev-list', '--count', f'{remote_branch}..HEAD']
        else:
            # 有上游分支，检查本地落后多少
            check_cmd = ['git', 'rev-list', '--count', '@{u}..HEAD']
        
        # 步骤4: 检查本地是否落后于远程
        check_result = subprocess.run(
            check_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if check_result.returncode != 0:
            # 如果检查失败，可能是远程分支不存在
            logger.info(f"无法比较本地和远程分支，可能远程分支不存在")
            return False
            
        # 如果本地落后的提交数为0，表示没有更新
        behind_count = int(check_result.stdout.strip())
        
        # 步骤5: 检查本地是否领先于远程
        ahead_cmd = ['git', 'rev-list', '--count', 'HEAD..@{u}'] if upstream_result.returncode == 0 else ['git', 'rev-list', '--count', f'HEAD..origin/{current_branch}']
        ahead_result = subprocess.run(
            ahead_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        ahead_count = 0
        if ahead_result.returncode == 0:
            ahead_count = int(ahead_result.stdout.strip())
        
        # 如果本地落后于远程（behind_count > 0），表示有更新
        if behind_count > 0:
            logger.info(f"本地落后远程 {behind_count} 个提交")
            return True
        else:
            logger.info("本地已是最新")
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"Git 命令超时: {safe_path}")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Git 命令执行失败: {e}")
        return None
    except Exception as e:
        logger.error(f"检查更新时发生异常: {e}")
        return None


def pull_repo(repo_path):
    """
    执行 git pull 更新仓库

    参数:
        repo_path: 仓库路径（字符串）

    返回值:
        成功：更新履历字符串（换行符替换为空格）
        失败：None
    """
    # 验证路径安全性
    safe_path = validate_path_security(repo_path)
    if safe_path is None:
        logger.error(f"路径验证失败: {repo_path}")
        return None

    try:
        cmd = ['git', 'pull']
        result = subprocess.run(
            cmd,
            cwd=safe_path,  # 使用安全路径
            capture_output=True,
            text=True,
            timeout=60  # 拉取操作可能需要更长时间
        )

        if result.returncode == 0:
            # 格式化输出，替换换行符为空格
            output = result.stdout.strip()
            formatted_output = output.replace('\n', ' ').replace('\r', '')
            return formatted_output
        else:
            # 分析错误原因
            error_info = analyze_git_error(result)
            logger.warning(f"git pull 返回错误码 {result.returncode}: {error_info}")
            return None

    except subprocess.TimeoutExpired:
        logger.error(f"Git pull 命令超时: {safe_path}")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Git pull 执行失败: {e}")
        return None
    except Exception as e:
        logger.error(f"更新仓库时发生异常: {e}")
        return None
