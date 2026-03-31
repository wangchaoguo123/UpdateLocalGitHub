import pytest
import subprocess
import os

from src.git_ops import check_repo_update, pull_repo


def test_check_repo_update_has_update(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(cmd, cwd, capture_output, text):
        return subprocess.CompletedProcess(
            cmd=cmd,
            returncode=0,
            stdout="From https://github.com/user/repo\\n * branch            main       -> FETCH_HEAD
Updating abc123..def456",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = check_repo_update(str(tmp_path))
    assert result == True


def test_check_repo_update_no_update(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(cmd, cwd, capture_output, text):
        return subprocess.CompletedProcess(
            cmd=cmd,
            returncode=0,
            stdout="Already up to date.",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = check_repo_update(str(tmp_path))
    assert result == False


def test_check_repo_update_failure(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(cmd, cwd, capture_output, text):
        raise subprocess.CalledProcessError(1, cmd, stderr="fatal: not a git repository")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = check_repo_update(str(tmp_path))
    assert result is None


def test_pull_repo_success(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(cmd, cwd, capture_output, text):
        return subprocess.Completed
        Process(
            cmd=cmd,
            returncode=0,
            stdout="Updating abc123..def456
Fast-forward
 file1.py | 5 +++++
 1 file changed, 5 insertions(+)",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = pull_repo(str(tmp_path))
    assert "Fast-forward" in result
    assert "file1.py" in result


def test_pull_repo_failure(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
"
    git_dir.mkdir()

    def mock_run(cmd, cwd, capture_output, text):
        raise subprocess.CalledProcessError(1, cmd, stderr="fatal: unable to access")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = pull_repo(str(tmp_path))
    assert result is None


def test_pull_repo_already_up_to_date(tmp_path, monkeypatch):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    def mock_run(cmd, cwd, capture_output, text):
        return subprocess.CompletedProcess(
            cmd=cmd,
            returncode=0,
            stdout="Already up to date.",
            stderr=""
        )

    monkeypatch.setattr(subprocess, 'run', mock_run)

    result = pull_repo(str(tmp_path))
    assert "Already up to date" in result
