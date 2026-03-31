import pytest
import os
import sys

from src.utils import validate_repo_path, extract_repo_name, format_update_message


def test_validate_repo_path_not_exist():
    assert validate_repo_path(r"D:\\nonexistent\\path") == False


def test_validate_repo_path_not_directory(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("test")
    assert validate_repo_path(str(file_path)) == False


def test_validate_repo_path_not_git_repo(tmp_path):
    assert validate_repo_path(str(tmp_path)) == False


def test_validate_repo_path_valid_git_repo(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    assert validate_repo_path(str(tmp_path)) == True


def test_validate_repo_path_git_file(tmp_path):
    git_file = tmp_path / ".git"
    git_file.write_text("gitdir: /some/path")
    assert validate_repo_path(str(tmp_path)) == True


def test_extract_repo_name_windows():
    assert extract_repo_name(r"D:\\code\\repo1") == "repo1"
    assert extract_repo_name(r"C:\\Users\\user\\my-re") == "my-re"


def test_extract_repo_name_unix():
    assert extract_repo_name("/home/user/repo2") == "repo2"
    assert extract_repo_name("/var/www/my-re") == "my-re"


def test_extract_repo_name_trailing_slash():
    assert extract_repo_name(r"D:\\code\\repo1\\") == "repo1"
    assert extract_repo_name("/home/user/repo2/") == "repo2"


def test_extract_repo_name_empty():
    assert extract_repo_name("") == ""


def test_format_update_message_multiline():
    input_msg = "Updating abc..def\nFast-forward\n file.py | 2 +"
    expected = "Updating abc..def Fast-forward  file.py | 2 +"
    assert format_update_message(input_msg) == expected


def test_format_update_message_empty():
    assert format_update_message("") == ""
    assert format_update_message(None) == ""


def test_format_update_message_single_line():
    assert format_update_message("Already up to date.") == "Already up to date."
    