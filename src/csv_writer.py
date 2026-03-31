import csv
import os
from datetime import datetime


def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log_update_result(repo_name, repo_path, update_info, csv_path):
    try:
        file_exists = os.path.exists(csv_path)
        timestamp = get_current_time()

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['仓库名称', '本地路径', '更新时间', '更新履历'])
            writer.writerow([repo_name, repo_path, timestamp, update_info])
        return True
    except Exception:
        return False
