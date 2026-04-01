"""
日志和错误处理功能测试
"""

import pytest
import logging
import os
import sys
import builtins
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.git_ops import validate_path_security, check_repo_update, pull_repo
from src.csv_writer import log_update_result, get_current_time


# ========== validate_path_security 测试 ==========

def test_validate_path_security_normal(tmp_path):
    """测试正常路径验证"""
    result = validate_path_security(str(tmp_path))
    assert result is not None
    assert os.path.isabs(result)


def test_validate_path_security_too_long():
    """测试超长路径验证"""
    long_path = "a" * 300
    result = validate_path_security(long_path)
    assert result is None


# ========== check_repo_update 测试 ==========

def test_check_repo_update_invalid_path():
    """测试无效路径检查更新"""
    result = check_repo_update("D:\\nonexistent\\path")
    assert result is None


def test_check_repo_update_not_git_repo(tmp_path):
    """测试非 Git 仓库检查更新"""
    result = check_repo_update(str(tmp_path))
    assert result is None


def test_check_repo_update_timeout(tmp_path, monkeypatch):
    """测试检查更新超时"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(['git'], 30)

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = check_repo_update(str(tmp_path))
    assert result is None


def test_check_repo_update_nonzero_returncode(tmp_path, monkeypatch):
    """测试检查更新返回非零退出码"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0] if args else ['git'],
            returncode=1,
            stdout="",
            stderr="fatal: not a git repository"
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = check_repo_update(str(tmp_path))
    assert result is None


def test_check_repo_update_fatal_in_output(tmp_path, monkeypatch):
    """测试检查更新输出包含 fatal"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0] if args else ['git'],
            returncode=0,
            stdout="fatal: unable to access remote",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = check_repo_update(str(tmp_path))
    assert result is None


def test_check_repo_update_empty_output(tmp_path, monkeypatch):
    """测试检查更新空输出"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        cmd = args[0] if args else ['git']
        
        if 'fetch' in cmd:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")
        elif 'rev-parse' in cmd and '--abbrev-ref' in cmd:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="main\n", stderr="")
        elif 'rev-parse' in cmd and '@{u}' in ' '.join(cmd):
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="abc123\n", stderr="")
        elif 'rev-list' in cmd and '@{u}..HEAD' in ' '.join(cmd):
            # 返回空字符串，会导致转换错误
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")
        elif 'rev-list' in cmd and 'HEAD..@{u}' in ' '.join(cmd):
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="0\n", stderr="")
        else:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = check_repo_update(str(tmp_path))
    # 当 rev-list 返回空字符串时，会抛出异常，返回 None
    assert result is None


def test_check_repo_update_generic_exception(tmp_path, monkeypatch):
    """测试检查更新通用异常"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        raise RuntimeError("意外错误")

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = check_repo_update(str(tmp_path))
    assert result is None


# ========== pull_repo 测试 ==========

def test_pull_repo_invalid_path():
    """测试无效路径拉取"""
    result = pull_repo("D:\\nonexistent\\path")
    assert result is None


def test_pull_repo_timeout(tmp_path, monkeypatch):
    """测试拉取更新超时"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(['git'], 60)

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = pull_repo(str(tmp_path))
    assert result is None


def test_pull_repo_nonzero_returncode(tmp_path, monkeypatch):
    """测试拉取更新返回非零退出码"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0] if args else ['git'],
            returncode=1,
            stdout="",
            stderr="error: unable to pull"
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = pull_repo(str(tmp_path))
    assert result is None


def test_pull_repo_generic_exception(tmp_path, monkeypatch):
    """测试拉取更新通用异常"""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        raise RuntimeError("网络错误")

    monkeypatch.setattr(subprocess, 'run', mock_run)
    result = pull_repo(str(tmp_path))
    assert result is None


# ========== log_update_result 测试 ==========

def test_log_update_result_permission_error(tmp_path, monkeypatch):
    """测试 CSV 写入权限错误"""
    csv_path = tmp_path / "test.csv"
    
    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")
    
    monkeypatch.setattr(builtins, 'open', mock_open)
    
    result = log_update_result("repo1", "D:\\repo1", "success", str(csv_path))
    assert result == False


def test_log_update_result_io_error(tmp_path, monkeypatch):
    """测试 CSV 写入 IO 错误"""
    csv_path = tmp_path / "test.csv"
    
    def mock_open(*args, **kwargs):
        raise IOError("磁盘已满")
    
    monkeypatch.setattr(builtins, 'open', mock_open)
    
    result = log_update_result("repo1", "D:\\repo1", "success", str(csv_path))
    assert result == False


def test_log_update_result_generic_error(tmp_path, monkeypatch):
    """测试 CSV 写入通用异常"""
    csv_path = tmp_path / "test.csv"
    
    def mock_open(*args, **kwargs):
        raise RuntimeError("意外错误")
    
    monkeypatch.setattr(builtins, 'open', mock_open)
    
    result = log_update_result("repo1", "D:\\repo1", "success", str(csv_path))
    assert result == False


def test_log_update_result_readonly_file(tmp_path, monkeypatch):
    """测试 CSV 写入只读文件系统"""
    csv_path = tmp_path / "readonly" / "test.csv"
    
    def mock_makedirs(*args, **kwargs):
        raise OSError("只读文件系统")
    
    monkeypatch.setattr(os, 'makedirs', mock_makedirs)
    
    result = log_update_result("repo1", "D:\\repo1", "success", str(csv_path))
    assert result == False


# ========== get_current_time 测试 ==========

def test_get_current_time_format():
    """测试时间格式"""
    time_str = get_current_time()
    # 验证格式 YYYY-MM-DD HH:MM:SS
    assert len(time_str) == 19
    assert time_str[4] == '-'
    assert time_str[7] == '-'
    assert time_str[10] == ' '
    assert time_str[13] == ':'
    assert time_str[16] == ':'
