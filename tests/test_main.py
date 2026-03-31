import pytest
import os
import subprocess
from unittest.mock import patch, MagicMock

import update_github_repos


def test_main_no_args(capsys):
    result = update_github_repos.main([])
    captured = capsys.readouterr()
    assert result == 1
    assert "请提供至少一个仓库路径" in captured.out


def test_main_path_not_exist(tmp_path, capsys):
    nonexistent = tmp_path / "nonexistent"
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.main([str(nonexistent)])
        captured = capsys.readouterr()
        assert result == 0
        assert "错误" in captured.out or "不存在" in captured.out


def test_main_integration_mock(tmp_path, capsys, monkeypatch):
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()

    mock_count = {'count': 0}

    def mock_run(*args, **kwargs):
        mock_count['count'] += 1
        return subprocess.CompletedProcess(
            args=args[0] if args else ['git'],
            returncode=0,
            stdout="Already up to date.",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.main([str(repo_path)])
        captured = capsys.readouterr()
        assert result == 0
        assert "完成" in captured.out


# 新增测试：覆盖 process_repo 函数中的错误情况
def test_process_repo_not_directory(tmp_path, capsys):
    """测试路径不是目录的情况"""
    # 创建一个文件而不是目录
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test")
    
    csv_path = str(tmp_path / "test.csv")
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.process_repo(str(file_path), csv_path, 1, 1)
        captured = capsys.readouterr()
        
        assert result is False
        assert "路径不是目录" in captured.out


def test_process_repo_not_git_repo(tmp_path, capsys):
    """测试不是 Git 仓库的情况"""
    # 创建一个空目录（没有 .git）
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.process_repo(str(repo_path), csv_path, 1, 1)
        captured = capsys.readouterr()
        
        assert result is False
        assert "不是 Git 仓库" in captured.out


def test_process_repo_check_update_failed(tmp_path, capsys, monkeypatch):
    """测试检查更新失败的情况"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    # 模拟 check_repo_update 返回 None（检查失败）
    def mock_check_update(path):
        return None
    
    monkeypatch.setattr(update_github_repos, 'check_repo_update', mock_check_update)
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.process_repo(str(repo_path), csv_path, 1, 1)
        captured = capsys.readouterr()
        
        assert result is False
        assert "检查更新失败" in captured.out


def test_process_repo_pull_success(tmp_path, capsys, monkeypatch):
    """测试拉取更新成功的情况"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    # 模拟检查有更新
    def mock_check_update(path):
        return True
    
    # 模拟拉取成功
    def mock_pull_repo(path):
        return "Fast-forward"
    
    monkeypatch.setattr(update_github_repos, 'check_repo_update', mock_check_update)
    monkeypatch.setattr(update_github_repos, 'pull_repo', mock_pull_repo)
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.process_repo(str(repo_path), csv_path, 1, 1)
        captured = capsys.readouterr()
        
        assert result is True
        assert "发现更新，正在拉取" in captured.out
        assert "Fast-forward" in captured.out


def test_process_repo_pull_failed(tmp_path, capsys, monkeypatch):
    """测试拉取更新失败的情况"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    # 模拟检查有更新
    def mock_check_update(path):
        return True
    
    # 模拟拉取失败（返回 None）
    def mock_pull_repo(path):
        return None
    
    monkeypatch.setattr(update_github_repos, 'check_repo_update', mock_check_update)
    monkeypatch.setattr(update_github_repos, 'pull_repo', mock_pull_repo)
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.process_repo(str(repo_path), csv_path, 1, 1)
        captured = capsys.readouterr()
        
        assert result is False
        assert "拉取更新失败" in captured.out


def test_process_repo_no_update(tmp_path, capsys, monkeypatch):
    """测试无需更新的情况"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    # 模拟检查无更新
    def mock_check_update(path):
        return False
    
    monkeypatch.setattr(update_github_repos, 'check_repo_update', mock_check_update)
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.process_repo(str(repo_path), csv_path, 1, 1)
        captured = capsys.readouterr()
        
        assert result is True
        assert "已是最新，无需更新" in captured.out


# 新增测试：覆盖 main 函数中的异常处理
def test_main_exception_handling(tmp_path, capsys, monkeypatch):
    """测试 main 函数中的异常处理"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    # 模拟 process_repo 抛出异常
    def mock_process_repo(*args, **kwargs):
        raise ValueError("模拟异常")
    
    monkeypatch.setattr(update_github_repos, 'process_repo', mock_process_repo)
    
    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.main([str(repo_path)])
        captured = capsys.readouterr()
        
        assert result == 0  # main 函数返回 0，即使有异常
        assert "处理仓库时发生异常" in captured.out


# 新增测试：覆盖 main_with_csv 函数
def test_main_with_csv_no_args():
    """测试 main_with_csv 函数的空参数情况"""
    result = update_github_repos.main_with_csv([], "test.csv")
    assert result == 1


def test_main_with_csv_success(tmp_path, monkeypatch):
    """测试 main_with_csv 函数的成功情况"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    # 模拟 process_repo 成功
    def mock_process_repo(*args, **kwargs):
        return True
    
    monkeypatch.setattr(update_github_repos, 'process_repo', mock_process_repo)
    
    result = update_github_repos.main_with_csv([str(repo_path)], csv_path)
    assert result == 0


def test_main_with_csv_exception(tmp_path, monkeypatch):
    """测试 main_with_csv 函数的异常处理"""
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()
    
    csv_path = str(tmp_path / "test.csv")
    
    # 模拟 process_repo 抛出异常
    def mock_process_repo(*args, **kwargs):
        raise RuntimeError("测试异常")
    
    monkeypatch.setattr(update_github_repos, 'process_repo', mock_process_repo)
    
    # main_with_csv 静默处理异常，应该返回 0
    result = update_github_repos.main_with_csv([str(repo_path)], csv_path)
    assert result == 0


