"""
日志功能测试
"""

import pytest
import logging
import os
import sys
import builtins

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.git_ops import validate_path_security, check_repo_update, pull_repo
from src.csv_writer import log_update_result


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


def test_check_repo_update_invalid_path():
    """测试无效路径检查更新"""
    result = check_repo_update("D:\\nonexistent\\path")
    assert result is None


def test_check_repo_update_not_git_repo(tmp_path):
    """测试非 Git 仓库检查更新"""
    result = check_repo_update(str(tmp_path))
    assert result is None


def test_pull_repo_invalid_path():
    """测试无效路径拉取"""
    result = pull_repo("D:\\nonexistent\\path")
    assert result is None


def test_log_update_result_permission_error(tmp_path, monkeypatch):
    """测试 CSV 写入权限错误"""
    csv_path = tmp_path / "test.csv"
    
    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")
    
    monkeypatch.setattr(builtins, 'open', mock_open)
    
    result = log_update_result("repo1", "D:\\repo1", "success", str(csv_path))
    assert result == False
