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
    elif ('connection refused' in stderr or 
          'could not resolve host' in stderr or 
          'failed to connect' in stderr or
          'could not connect to server' in stderr or
          ('unable to access' in stderr and 'https' in stderr)):
        error_parts.append("网络连接失败，请检查网络连接或代理设置")
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

    安全检查：
    1. 路径规范化
    2. 路径长度限制
    3. 禁止访问系统目录
    4. 路径遍历攻击防护（检测 ..）
    5. 符号链接解析与验证
    6. 父目录访问权限验证

    参数:
        repo_path: 仓库路径（字符串）

    返回值:
        安全的规范化路径，如果路径不安全则返回 None
    """
    # 步骤1：路径遍历攻击防护
    # 检查路径中是否包含 .. 序列，防止通过路径遍历逃逸
    normalized = os.path.normpath(repo_path)
    if '..' in normalized.split(os.sep):
        logger.warning(f"检测到路径遍历攻击: {repo_path}")
        return None

    # 步骤2：规范化路径，处理相对路径
    safe_path = os.path.normpath(os.path.abspath(repo_path))

    # 步骤3：检查路径长度（Windows 最大路径长度限制）
    if len(safe_path) > 260:
        logger.warning(f"路径过长: {safe_path}")
        return None

    # 步骤4：禁止访问系统目录（只检查根目录，不包括子目录）
    forbidden_paths = []
    
    # Windows 系统目录
    if os.name == 'nt':
        system_root = os.environ.get('SystemRoot', 'C:\\Windows').lower()
        program_files = os.environ.get('ProgramFiles', 'C:\\Program Files').lower()
        
        forbidden_paths = [system_root, program_files]
    
    # Unix 系统目录
    else:
        forbidden_paths = ['/etc', '/bin', '/sbin', '/sys', '/proc']
    
    safe_path_lower = safe_path.lower()
    for forbidden in forbidden_paths:
        if forbidden:
            # 只检查是否完全匹配或以目录分隔符结尾，避免禁止子目录
            if safe_path_lower == forbidden or safe_path_lower.startswith(forbidden + os.sep):
                logger.warning(f"禁止访问系统目录: {safe_path}")
                return None

    # 步骤5：符号链接安全检查
    # 解析真实路径，防止通过符号链接逃逸到禁止目录
    try:
        real_path = os.path.realpath(repo_path)
        if real_path != safe_path:
            logger.info(f"检测到符号链接: {repo_path} -> {real_path}")
            # 对符号链接目标进行二次安全检查
            real_lower = real_path.lower()
            for forbidden in forbidden_paths:
                if forbidden:
                    if real_lower == forbidden or real_lower.startswith(forbidden + os.sep):
                        logger.warning(f"符号链接指向系统目录: {real_path}")
                        return None
    except OSError as e:
        logger.warning(f"解析真实路径失败: {e}")
        return None

    # 步骤6：验证父目录访问权限
    # 确保用户有权限访问仓库的父目录
    parent_dir = os.path.dirname(safe_path)
    if parent_dir and not os.path.exists(parent_dir):
        logger.warning(f"父目录不存在: {parent_dir}")
        return None
    
    if parent_dir and not os.access(parent_dir, os.R_OK | os.X_OK):
        logger.warning(f"父目录权限不足: {parent_dir}")
        return None

    return safe_path


def _get_remote_branch(safe_path, current_branch):
    """
    获取远程分支名称

    参数:
        safe_path: 安全的仓库路径
        current_branch: 当前分支名称

    返回值:
        远程分支名称，如果找不到返回 None
    """
    # 1. 检查上游分支
    upstream_cmd = ['git', 'rev-parse', '--verify', '@{u}']
    upstream_result = subprocess.run(
        upstream_cmd, cwd=safe_path, capture_output=True, text=True, timeout=10
    )
    
    if upstream_result.returncode == 0:
        return upstream_result.stdout.strip()
    
    # 2. 尝试 origin/分支名
    remote_branch = f'origin/{current_branch}'
    verify_cmd = ['git', 'rev-parse', '--verify', remote_branch]
    verify_result = subprocess.run(
        verify_cmd, cwd=safe_path, capture_output=True, text=True, timeout=10
    )
    
    if verify_result.returncode == 0:
        return remote_branch
    
    # 3. 尝试备用分支
    for alt_branch in ['origin/master', 'origin/main']:
        verify_cmd = ['git', 'rev-parse', '--verify', alt_branch]
        verify_result = subprocess.run(
            verify_cmd, cwd=safe_path, capture_output=True, text=True, timeout=10
        )
        if verify_result.returncode == 0:
            logger.info(f"使用备用分支: {alt_branch}")
            return alt_branch
    
    return None


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
        logger.debug(f"正在获取远程更新: {safe_path}")
        fetch_cmd = ['git', 'fetch', '--prune', 'origin']
        fetch_result = subprocess.run(
            fetch_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时：大型仓库网络下载可能较慢
        )
        
        if fetch_result.returncode != 0:
            error_info = analyze_git_error(fetch_result)
            logger.warning(f"git fetch 返回错误码 {fetch_result.returncode}: {error_info}")
            return None
        
        logger.debug(f"git fetch 成功: {safe_path}")

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
        
        # 检查是否处于 detached HEAD 状态
        if current_branch == 'HEAD':
            logger.warning("处于 detached HEAD 状态，无法确定当前分支")
            return None
        
        logger.debug(f"当前分支: {current_branch}")
        
        # 步骤3: 确定远程分支名称
        remote_branch = _get_remote_branch(safe_path, current_branch)
        if remote_branch is None:
            logger.warning("未找到有效的远程分支")
            return False
        
        logger.debug(f"远程分支: {remote_branch}")
        
        # 步骤4: 检查本地是否落后于远程
        # git rev-list HEAD..remote_branch: 显示在 HEAD 中但不在 remote_branch 中的提交（本地落后远程）
        check_cmd = ['git', 'rev-list', '--count', f'HEAD..{remote_branch}']
        check_result = subprocess.run(
            check_cmd,
            cwd=safe_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if check_result.returncode != 0:
            logger.warning(f"无法比较本地和远程分支: {check_result.stderr}")
            return False
            
        behind_count = int(check_result.stdout.strip())
        logger.debug(f"本地落后远程 {behind_count} 个提交")
        
        # 步骤5: 检查远程是否落后于本地（可选信息）
        # git rev-list remote_branch..HEAD: 显示在 remote_branch 中但不在 HEAD 中的提交（本地领先远程）
        ahead_cmd = ['git', 'rev-list', '--count', f'{remote_branch}..HEAD']
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
            logger.debug(f"本地领先远程 {ahead_count} 个提交")
        
        # 步骤6: 获取远程分支的最新提交信息
        if behind_count > 0:
            # 获取远程最新提交信息
            log_cmd = ['git', 'log', '--oneline', '-n', '3', f'{remote_branch}']
            log_result = subprocess.run(
                log_cmd,
                cwd=safe_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if log_result.returncode == 0:
                logger.info(f"远程最新提交:\n{log_result.stdout}")
            
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
        成功：更新履历字符串（简化格式）
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
            output = result.stdout.strip()
            
            # 检查是否已经是最新
            if 'already up to date' in output.lower():
                return "已是最新"
            
            # 获取最新提交的简短信息
            log_cmd = ['git', 'log', '-1', '--pretty=format:%h - %s', 'HEAD']
            log_result = subprocess.run(
                log_cmd,
                cwd=safe_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if log_result.returncode == 0 and log_result.stdout.strip():
                # 返回最新提交的简短信息
                return f"已更新: {log_result.stdout.strip()}"
            else:
                # 备用方案：返回简化的输出
                lines = output.split('\n')
                if len(lines) > 0:
                    # 只取第一行有意义的信息
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('From'):
                            return line[:100]  # 限制长度
                return "已更新"
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
