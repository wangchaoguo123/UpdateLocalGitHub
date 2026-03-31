import pytest
import os
import subprocess

import update_github_repos


def test_full_workflow_with_mock_repo(tmp_path, monkeypatch, capsys):
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

    csv_path = tmp_path / "result_test.csv"

    result = update_github_repos.main_with_csv([str(repo_path)], str(csv_path))

    captured = capsys.readouterr()
    assert result == 0
    assert csv_path.exists()

    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "test-repo" in content