import pytest
import os
import csv
from datetime import datetime

from src.csv_writer import log_update_result, get_current_time


def test_log_update_result_new_file(tmp_path):
    csv_path = tmp_path / "test.csv"

    log_update_result("repo1", r"D:\repo1", "success", str(csv_path))

    assert csv_path.exists()

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ['仓库名称', '本地路径', '更新时间', '更新履历']
        assert rows[1][0] == 'repo1'
        assert rows[1][1] == r'D:\repo1'
        assert rows[1][3] == 'success'


def test_log_update_result_append(tmp_path):
    csv_path = tmp_path / "test.csv"

    log_update_result("repo1", r"D:\repo1", "success", str(csv_path))
    log_update_result("repo2", r"D:\repo2", "error", str(csv_path))

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) == 3
        assert rows[1][0] == 'repo1'
        assert rows[2][0] == 'repo2'


def test_log_update_result_timestamp_format(tmp_path):
    csv_path = tmp_path / "test.csv"

    log_update_result("repo1", r"D:\repo1", "test", str(csv_path))

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        timestamp = rows[1][2]
        datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')


def test_log_update_result_unicode(tmp_path):
    csv_path = tmp_path / "test.csv"

    log_update_result("测试仓库", r"D:\测试仓库", "更新成功", str(csv_path))

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert rows[1][0] == "测试仓库"


def test_get_current_time_format():
    time_str = get_current_time()
    datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')