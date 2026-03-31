import pytest
import os
import subprocess
from unittest.mock import patch

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
        assert "error" in captured.out.lower()


def test_main_integration_mock(tmp_path, capsys, monkeypatch):
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()

    mock_count = {'count': 0}

    def mock_run(cmd, cwd, capture_output, text):
        mock_count['count'] += 1
        if '--dry-run' in cmd:
            return subprocess.CompletedProcess(cmd=cmd, returncode=0, stdout="Already up to date.", stderr="")
        else:
            return subprocess.CompletedProcess(cmd=cmd, returncode=0, stdout="Already up to date.", stderr="")

    monkeypatch.setattr(subprocess, 'run', mock_run)

    with patch.object(update_github_repos, 'log_update_result'):
        result = update_github_repos.main([str(repo_path)])
        captured = capsys.readouterr()
        assert result == 0
        assert "完成" in captured.out