# GitHub 仓库本地更新工具 - 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 开发一个批量检查和更新本地 GitHub 仓库的自动化工具，并将更新历史记录到 CSV 文件中。

**架构：** 采用双层架构，批处理文件作为用户界面层，Python 脚本作为业务逻辑层。Python 脚本内部按职责划分为 utils、git_ops、csv_writer 和 main 四个模块。

**技术栈：** Python 3.7+, subprocess, csv, datetime, pytest

---

## 项目时间表（5 天）

| 天次 | 任务 | 目标 |
|------|------|------|
| Day 1 | 工具函数模块 | 实现 utils.py 及其测试 |
| Day 2 | Git 操作模块 | 实现 git_ops.py 及其测试 |
| Day 3 | CSV 写入模块 | 实现 csv_writer.py 及其测试 |
| Day 4 | 主程序和批处理 | 实现 update_github_repos.py 和 update_repos.bat |
| Day 5 | 集成测试与文档 | 集成测试、README、最终验证 |

---

## 文件结构

```
UpdateLocalGitHub/
├── update_github_repos.py          # 主程序（新建）
├── update_repos.bat                 # 批处理文件（新建）
├── src/
│   ├── __init__.py                  # 包初始化（新建）
│   ├── utils.py                     # 工具函数模块（新建）
│   ├── git_ops.py                   # Git 操作模块（新建）
│   └── csv_writer.py                # CSV 写入模块（新建）
├── tests/
│   ├── conftest.py                   # 测试配置（新建）
│   ├── test_utils.py                 # 工具函数测试（新建）
│   ├── test_git_ops.py               # Git 操作测试（新建）
│   ├── test_csv_writer.py            # CSV 写入测试（新建）
│   ├── test_main.py                 # 主函数测试（新建）
│   └── test_integration.py           # 集成测试（新建）
├── requirements.txt                  # 依赖列表（更新）
└── README.md                         # 使用说明（更新）
```

---

## Day 1：工具函数模块（utils.py）

### 任务 1.0：创建测试配置和依赖文件

**文件：**
- 创建：`tests/conftest.py`
- 创建：`requirements.txt`
- 修改：无
- 测试：无

- [ ] **步骤 1：创建 conftest.py**

创建文件 `tests/conftest.py`，添加以下内容（见附录 A）：

```python
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

- [ ] **步骤 2：创建或更新 requirements.txt**

确保 `requirements.txt` 包含以下内容：

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
```

- [ ] **步骤 3：Commit**

```bash
git add tests/conftest.py requirements.txt
git commit -m "test: add pytest configuration and requirements"
```

### 任务 1.1：创建 src 包结构

**文件：**
- 创建：`src/__init__.py`
- 修改：无
- 测试：无

- [ ] **步骤 1：创建 src 目录**

运行：`mkdir -p src`

- [ ] **步骤 2：创建空包文件**

创建文件 `src/__init__.py`，内容为空

- [ ] **步骤 3：验证目录结构**

运行：`ls -la src/`
预期：显示 `__init__.py` 文件

- [ ] **步骤 4：Commit**

```bash
git add src/__init__.py
git commit -m "feat: initialize src package"
```

### 任务 1.2：实现 validate_repo_path 函数

**文件：**
- 创建：`src/utils.py`
- 修改：无
- 测试：`tests/test_utils.py`

- [ ] **步骤 1：编写失败的测试**

在 `tests/test_utils.py` 中添加测试用例（见附录 A）

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest tests/test_utils.py -v`
预期：FAIL，报错 "ModuleNotFoundError: No module named 'utils'"

- [ ] **步骤 3：实现 validate_repo_path 函数**

创建文件 `src/utils.py`，实现路径验证逻辑（见附录 B）：

```python
def validate_repo_path(repo_path):
    if not os.path.exists(repo_path):
        return False
    if not os.path.isdir(repo_path):
        return False
    git_path = os.path.join(repo_path, '.git')
    return os.path.exists(git_path)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`pytest tests/test_utils.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add tests/test_utils.py src/utils.py
git commit -m "feat: implement validate_repo_path function with tests"
```

### 任务 1.3：实现 extract_repo_name 和 format_update_message 函数

**文件：**
- 修改：`src/utils.py`
- 修改：`tests/test_utils.py`

- [ ] **步骤 1：编写失败的测试**

在 `tests/test_utils.py` 中添加测试用例（见附录 A）

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest tests/test_utils.py::test_extract_repo_name_windows -v`
预期：FAIL，报错 "name 'extract_repo_name' is not defined"

- [ ] **步骤 3：实现 extract_repo_name 函数**

在 `src/utils.py` 中添加以下代码（见附录 B）：

```python
def extract_repo_name(repo_path):
    if not repo_path:
        return ""
    repo_path = repo_path.rstrip(os.sep)
    return os.path.basename(repo_path)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`pytest tests/test_utils.py -v`
预期：PASS

- [ ] **步骤 5：实现 format_update_message 函数**

在 `src/utils.py` 中添加以下代码（见附录 B）：

```python
def format_update_message(message):
    if not message:
        return ""
    return message.replace('\n', ' ').replace('\r', '')
```

- [ ] **步骤 6：运行测试验证通过**

运行：`pytest tests/test_utils.py -v`
预期：PASS

- [ ] **步骤 7：Commit**

```bash
git add src/utils.py tests/test_utils.py
git commit -m "feat: implement extract_repo_name and format_update_message functions"
```

---

## Day 2：Git 操作模块（git_ops.py）

### 任务 2.1：实现 check_repo_update 函数

**文件：**
- 创建：`src/git_ops.py`
- 修改：无
- 测试：`tests/test_git_ops.py`

- [ ] **步骤 1：编写失败的测试**

创建文件 `tests/test_git_ops.py`，包含测试用例（见附录 A）

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest tests/test_git_ops.py -v`
预期：FAIL，报错 "ModuleNotFoundError: No module named 'git_ops'"

- [ ] **步骤 3：实现 check_repo_update 函数**

创建文件 `src/git_ops.py`，添加以下代码（见附录 B）：

```python
import subprocess

def check_repo_update(repo_path):
    try:
        cmd = ['git', 'pull', '--dry-run']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        output = result.stdout.lower()
        if 'already up to date' in output:
            return False
        elif 'fatal' in output or 'error' in output:
            return None
        else:
            return True
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None
```

- [ ] **步骤 4：运行测试验证通过**

运行：`pytest tests/test_git_ops.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add src/git_ops.py tests/test_git_ops.py
git commit -m "feat: implement check_repo_update function with tests"
```

### 任务 2.2：实现 pull_repo 函数

**文件：**
- 修改：`src/git_ops.py`
- 修改：`tests/test_git_ops.py`

- [ ] **步骤 1：编写失败的测试**

在 `tests/test_git_ops.py` 中添加测试用例（见附录 A）

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest tests/test_git_ops.py::test_pull_repo_success -v`
预期：FAIL，报错 "name 'pull_repo' is not defined"

- [ ] **步骤 3：实现 pull_repo 函数**

在 `src/git_ops.py` 中添加以下代码（见附录 B）：

```python
def pull_repo(repo_path):
    try:
        cmd = ['git', 'pull']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            formatted_output = output.replace('\n', ' ').replace('\r', '')
            return formatted_output
        else:
            return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None
```

- [ ] **步骤 4：运行测试验证通过**

运行：`pytest tests/test_git_ops.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add src/git_ops.py tests/test_git_ops.py
git commit -m "feat: implement pull_repo function with tests"
```

---

## Day 3：CSV 写入模块（csv_writer.py）

### 任务 3.1：实现 get_current_time 和 log_update_result 函数

**文件：**
- 创建：`src/csv_writer.py`
- 修改：无
- 测试：`tests/test_csv_writer.py`

- [ ] **步骤 1：编写失败的测试**

创建文件 `tests/test_csv_writer.py`，包含测试用例（见附录 A）

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest tests/test_csv_writer.py -v`
预期：FAIL，报错 "ModuleNotFoundError: No module named 'csv_writer'"

- [ ] **步骤 3：实现 get_current_time 和 log_update_result 函数**

创建文件 `src/csv_writer.py`，添加以下代码（见附录 B）：

```python
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`pytest tests/test_csv_writer.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add src/csv_writer.py tests/test_csv_writer.py
git commit -m "feat: implement csv_writer functions with tests"
```

---

## Day 4：主程序和批处理文件

### 任务 4.1：实现主程序 main 函数

**文件：**
- 创建：`update_github_repos.py`
- 修改：无
- 测试：`tests/test_main.py`

- [ ] **步骤 1：编写失败的测试**

创建文件 `tests/test_main.py`，包含测试用例（见附录 A）

- [ ] **步骤 2：运行测试验证失败**

运行：`pytest tests/test_main.py -v`
预期：FAIL，报错 "ModuleNotFoundError" 或其他错误

- [ ] **步骤 3：实现主程序**

创建文件 `update_github_repos.py`，实现完整的更新流程（见附录 B）

主程序需要实现：
1. 解析命令行参数
2. 验证参数有效性
3. 遍历处理每个仓库
4. 输出详细日志
5. 返回退出码

- [ ] **步骤 4：运行测试验证通过**

运行：`pytest tests/test_main.py -v`
预期：PASS

- [ ] **步骤 5：Commit**

```bash
git add update_github_repos.py tests/test_main.py
git commit -m "feat: implement main program with tests"
```

### 任务 4.2：创建批处理文件

**文件：**
- 创建：`update_repos.bat`
- 修改：无
- 测试：无

- [ ] **步骤 1：创建批处理文件**

创建文件 `update_repos.bat`，内容见规格说明 4.2 节

- [ ] **步骤 2：验证文件内容**

运行：`cat update_repos.bat`
预期：显示批处理文件内容

- [ ] **步骤 3：Commit**

```bash
git add update_repos.bat
git commit -m "feat: add batch file for Windows execution"
```

---

## Day 5：集成测试与文档

### 任务 5.1：集成测试

**文件：**
- 创建：`tests/test_integration.py`
- 修改：无
- 测试：`tests/test_integration.py`

- [ ] **步骤 1：编写集成测试**

创建文件 `tests/test_integration.py`，包含集成测试用例（见附录 A）

- [ ] **步骤 2：运行集成测试**

运行：`pytest tests/test_integration.py -v`
预期：PASS

- [ ] **步骤 3：Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration tests"
```

### 任务 5.2：更新 README.md

**文件：**
- 修改：`README.md`
- 修改：无
- 测试：无

- [ ] **步骤 1：编写 README**

更新 `README.md`，添加以下内容：

- 项目简介：简要说明工具的功能和用途
- 快速开始：：安装和基本使用步骤
- 使用方法：详细的命令行参数说明
- 输出说明：控制台输出格式和 CSV 文件结构示例
- 示例：实际运行示例
- 常见问题：错误处理说明

- [ ] **步骤 2：Commit**

```bash
git add README.md
git commit -m "docs: update README with usage instructions"
```

### 任务 5.3：最终验证

- [ ] **步骤 1：运行所有测试**

运行：`pytest -v`
预期：所有测试通过

- [ ] **步骤 2：生成覆盖率报告**

运行：`pytest --cov=. --cov-report=html`
预期：覆盖率 ≥ 80%

- [ ] **步骤 3：手动测试**

1. 创建测试仓库
2. 运行程序
3. 验证 CSV 输出

---

## 附录 A：测试文件详细内容

### tests/conftest.py 完整内容

```python
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
```

### tests/test_utils.py 完整内容

```python
import pytest
import os
import sys

from src.utils import validate_repo_path, extract_repo_name, format_update_message


def test_validate_repo_path_not_exist():
    assert validate_repo_path(r"D:\nonexistent\path") == False


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
    assert extract_repo_name(r"D:\code\repo1") == "repo1"
    assert extract_repo_name(r"C:\Users\user\my-re") == "my-re"


def test_extract_repo_name_unix():
    assert extract_repo_name("/home/user/repo2") == "repo2"
    assert extract_repo_name("/var/www/my-re") == "my-re"


def test_extract_repo_name_trailing_slash():
    assert extract_repo_name(r"D:\code\repo1\") == "repo1"
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
```

### tests/test_git_ops.py 完整内容

```python
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
            stdout="From https://github.com/user/repo\n * branch            main       -> FETCH_HEAD\nUpdating abc123..def456",
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
        return subprocess.CompletedProcess(
            cmd=cmd,
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
```

### tests/test_csv_writer.py 完整内容

```python
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
```

### tests/test_main.py 完整内容

```python
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
```

### tests/test_integration.py 完整内容

```python
import pytest
import os
import subprocess

import update_github_repos


def test_full_workflow_with_mock_repo(tmp_path, monkeypatch, capsys):
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / ".git").mkdir()

    mock_count = {'count': 0}

    def mock_run(cmd, cwd, capture_output, text):
        mock_count['count'] += 1
        return subprocess.CompletedProcess(
            cmd=cmd,
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
```

---

## 附录 B：关键函数实现代码

### src/utils.py

```python
import os


def validate_repo_path(repo_path):
    if not os.path.exists(repo_path):
        return False
    if not os.path.isdir(repo_path):
        return False
    git_path = os.path.join(repo_path, '.git')
    return os.path.exists(git_path)


def extract_repo_name(repo_path):
    if not repo_path:
        return ""
    repo_path = repo_path.rstrip(os.sep)
    return os.path.basename(repo_path)


def format_update_message(message):
    if not message:
        return ""
    return message.replace('\n', ' ').replace('\r', '')
```

### src/git_ops.py

```python
import subprocess


def check_repo_update(repo_path):
    try:
        cmd = ['git', 'pull', '--dry-run']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        output = result.stdout.lower()
        if 'already up to date' in output:
            return False
        elif 'fatal' in output or 'error' in output:
            return None
        else:
            return True
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None


def pull_repo(repo_path):
    try:
        cmd = ['git', 'pull']
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            formatted_output = output.replace('\n', ' ').replace('\r', '')
            return formatted_output
        else:
            return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None
```

### src/csv_writer.py

```python
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
```

### update_github_repos.py

```python
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils import validate_repo_path, extract_repo_name
from git_ops import check_repo_update, pull_repo
from csv_writer import log_update_result


def print_header():
    print("=" * 50)
    print("  GitHub 仓库本地更新工具")
    print("=" * 50)
    print()


def get_csv_filename():
    return f"result_{datetime.now().strftime('%Y%m%d')}.csv"


def process_repo(repo_path, csv_path, index, total):
    repo_name = extract_repo_name(repo_path)

    print(f"[仓库 {index}/{total}] {repo_path}")
    print("[检查] 正在检查更新...")

    if not os.path.exists(repo_path):
        print(f"[错误] 路径不存在")
        log_update_result(repo_name, repo_path, "error: 路径不存在", csv_path)
        return False

    if not os.path.isdir(repo_path):
        print(f"[错误] 路径不是目录")
        log_update_result(repo_name, repo_path, "error: 路径不是目录", csv_path)
        return False

    if not validate_repo_path(repo_path):
        print(f"[错误] 不是 Git 仓库")
        log_update_result(repo_name, repo_path, "error: 不是 Git 仓库", csv_path)
        return False

    has_update = check_repo_update(repo_path)

    if has_update is None:
        print(f"[错误] 检查更新失败")
        log_update_result(repo_name, repo_path, "error: 检查更新失败", csv_path)
        return False

    if has_update:
        print("[结果] 发现更新，正在拉取...")
        result = pull_repo(repo_path)
        if result:
            print(f"[输出] {result}")
            print(f"[记录] 已记录到 {os.path.basename(csv_path)}")
            log_update_result(repo_name, repo_path, result, csv_path)
            return True
        else:
            print(f"[错误] 拉取更新失败")
            log_update_result(repo_name, repo_path, "error: 拉取更新失败", csv_path)
            return False
    else:
        print("[结果] 已是最新，无需更新")
        print(f"[记录] 已记录到 {os.path.basename(csv_path)}")
        log_update_result(repo_name, repo_path, "Already up to date.", csv_path)
        return True


def main(args):
    print_header()

    if not args:
        print("[错误] 请提供至少一个仓库路径")
        print()
        print("使用方法：")
        print("  python update_github_repos.py <repo_path1> [repo_path2] ...")
        return 1

    print("开始检查仓库更新...")
    print("=" * 50)
    print()

    csv_path = get_csv_filename()
    total = len(args)
    success = 0

    for index, repo_path in enumerate(args, 1):
        try:
            if process_repo(repo_path, csv_path, index, total):
                success += 1
            print()
        except Exception as e:
            print(f"[错误] 处理仓库时发生异常: {str(e)}")
            print()

    print("=" * 50)
    print(f"完成！共处理 {total} 个仓库，成功 {success} 个，失败 {total - success} 个")
    print("=" * 50)

    return 0


def main_with_csv(args, csv_path):
    if not args:
        return 1

    total = len(args)
    success = 0

    for index, repo_path in enumerate(args, 1):
        try:
            if process_repo(repo_path, csv_path, index, total):
                success += 1
        except Exception as e:
            pass

    return 0


if __name__ == '__main__':
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
```

### update_repos.bat

```batch
@echo off
chcp 65001
echo =====================================
echo   GitHub 仓库本地更新工具
echo =====================================
echo.

python update_github_repos.py %*

if %errorlevel% neq 0 (
    echo.
    echo 程序执行失败，错误码: %errorlevel%
) else (
    echo.
    echo 程序执行成功
)

echo.
pause
```

---

**计划结束**
