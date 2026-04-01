import pytest
import subprocess
import os

from src.git_ops import check_repo_update, pull_repo


def test_check_repo_update_has_update(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        cmd = args[0] if args else ['git']
        
        if 'fetch' in cmd:
            # fetch 成功
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")
        elif 'rev-parse' in cmd and '--abbrev-ref' in cmd:
            # 返回当前分支
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="main\n", stderr="")
        elif 'rev-parse' in cmd and '@{u}' in ' '.join(cmd):
            # 有上游分支
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="origin/main\n", stderr="")
        elif 'rev-parse' in cmd and 'origin/' in ' '.join(cmd):
            # 验证远程分支存在
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="origin/main\n", stderr="")
        elif 'rev-list' in cmd and 'HEAD..origin/main' in ' '.join(cmd):
            # 本地落后 3 个提交
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="3\n", stderr="")
        elif 'rev-list' in cmd and 'origin/main..HEAD' in ' '.join(cmd):
            # 本地没有领先
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="0\n", stderr="")
        elif 'log' in cmd:
            # 返回日志信息
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="abc123 Update file1\n", stderr="")
        else:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = check_repo_update(str(tmp_path))
    assert result == True


def test_check_repo_update_no_update(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        cmd = args[0] if args else ['git']
        
        if 'fetch' in cmd:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")
        elif 'rev-parse' in cmd and '--abbrev-ref' in cmd:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="main\n", stderr="")
        elif 'rev-parse' in cmd and '@{u}' in ' '.join(cmd):
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="origin/main\n", stderr="")
        elif 'rev-parse' in cmd and 'origin/' in ' '.join(cmd):
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="origin/main\n", stderr="")
        elif 'rev-list' in cmd and 'HEAD..origin/main' in ' '.join(cmd):
            # 本地没有落后
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="0\n", stderr="")
        elif 'rev-list' in cmd and 'origin/main..HEAD' in ' '.join(cmd):
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="0\n", stderr="")
        else:
            return subprocess.CompletedProcess(cmd, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = check_repo_update(str(tmp_path))
    assert result == False


def test_check_repo_update_failure(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ['git'], stderr="fatal: not a git repository")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = check_repo_update(str(tmp_path))
    assert result is None


def test_pull_repo_success(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0] if args else ['git'],
            returncode=0,
            stdout="Updating abc123..def456\nFast-forward\n file1.py | 5 +++++\n 1 file changed, 5 insertions(+)",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = pull_repo(str(tmp_path))
    assert "Fast-forward" in result
    assert "file1.py" in result


def test_pull_repo_failure(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ['git'], stderr="fatal: unable to access")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = pull_repo(str(tmp_path))
    assert result is None


def test_pull_repo_already_up_to_date(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args[0] if args else ['git'],
            returncode=0,
            stdout="Already up to date.",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = pull_repo(str(tmp_path))
    assert "Already up to date" in result
