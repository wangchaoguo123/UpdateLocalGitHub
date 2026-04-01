# GitHub 仓库本地更新工具

批量检查和更新本地 GitHub 仓库的自动化工具。

## 功能特性

- 批量检查多个本地 GitHub 仓库是否有新更新
- 自动拉取更新
- 将更新历史记录到 CSV 文件
- 详细的控制台输出和日志记录
- **安全的路径验证**，防止命令注入攻击，禁止访问系统目录
- **超时机制**，防止 Git 命令挂起
- **网络错误检测**，提供清晰的错误提示
- **简化更新履历**，只记录最新提交信息

## 快速开始

### 环境要求

- Python >= 3.7
- Git 命令行工具已安装

### 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法一：直接运行 Python 脚本

```bash
python update_github_repos.py "D:\repo1" "D:\repo2" "D:\repo3"
```

### 方法二：使用批处理文件（Windows）

双击运行 `update_repos.bat`，或在命令行中执行：

```batch
update_repos.bat "D:\repo1" "D:\repo2" "D:\repo3"
```

### 方法三：使用相对路径

```bash
python update_github_repos.py "../my-repo" "./local-repo"
```

## 输出说明

### 控制台输出格式

```
==================================================
  GitHub 仓库本地更新工具
==================================================

开始检查仓库更新...
==================================================

[仓库 1/3] D:\repo1
[检查] 正在检查更新...
[结果] 发现更新，正在拉取...
[输出] fast-forward: main..origin/main branch main fast-forwarded
[记录] 已记录到 result_20260331.csv

[仓库 2/3] D:\repo2
[检查] 正在检查更新...
[结果] 已是最新，无需更新
[记录] 已记录到 result_20260331.csv

[仓库 3/3] D:\repo3
[检查] 正在检查更新...
[错误] 不是 Git 仓库
[记录] 已记录到 result_20260331.csv

==================================================
完成！共处理 3 个仓库，成功 2 个，失败 1 个
==================================================
```

### CSV 文件结构

文件名格式：`result_YYYYMMDD.csv`

| 列名 | 说明 | 示例 |
|------|------|------|
| 仓库名称 | 仓库名（路径最后一部分） | repo1 |
| 本地路径 | 完整本地路径 | D:\repo1 |
| 更新时间 | 格式化时间戳 | 2026-03-31 10:30:15 |
| 更新履历 | 更新详情或状态信息 | fast-forward: ... |

### CSV 文件示例

```csv
仓库名称,本地路径,更新时间,更新履历
repo1,D:\repo1,2026-03-31 10:30:15,fast-forward: main..origin/main branch main fast-forwarded
repo2,D:\repo2,2026-03-31 10:30:18,Already up to date.
repo3,D:\repo3,2026-03-31 10:30:20,error: 不是 Git 仓库
```

## 安全特性

- **路径安全验证**：自动规范化路径，防止命令注入
- **系统目录保护**：禁止访问 Windows 系统目录（C:\Windows、C:\Program Files）和 Unix 系统目录（/etc、/bin 等）
- **超时机制**：Git 命令设置超时（检查 60 秒，拉取 60 秒），防止挂起
- **异常日志**：所有异常记录到 Python logging 模块

## 错误处理

工具采用"跳过错误"策略：
- 单个仓库失败不会影响其他仓库的处理
- 错误信息会记录到控制台、日志和 CSV 文件
- 程序会显示成功和失败的统计信息

### 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| 路径不存在 | 指定的路径不存在 | 检查路径拼写和权限 |
| 路径不是目录 | 路径是文件而非目录 | 检查路径是否正确 |
| 不是 Git 仓库 | 目录不是 Git 仓库 | 检查是否包含 .git 目录 |
| 检查更新失败 | git 命令执行失败 | 检查 Git 是否正确安装和配置 |
| 拉取更新失败 | git pull 命令失败 | 检查网络连接和仓库权限 |

## API 参考

### src.utils

| 函数 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| validate_repo_path(repo_path) | 验证路径是否为有效的 Git 仓库 | repo_path: 路径字符串 | True/False |
| extract_repo_name(repo_path) | 从完整路径提取仓库名称 | repo_path: 路径字符串 | 仓库名字符串 |
| format_update_message(message) | 将多行消息合并为单行 | message: 原始消息 | 格式化后的字符串 |

### src.git_ops

| 函数 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| validate_path_security(repo_path) | 验证路径安全性（含系统目录检查） | repo_path: 路径字符串 | 安全路径或 None |
| check_repo_update(repo_path) | 检查仓库是否有更新 | repo_path: 路径字符串 | True/False/None |
| pull_repo(repo_path) | 执行 git pull 更新仓库 | repo_path: 路径字符串 | 更新信息或 None |
| analyze_git_error(result) | 分析 Git 命令错误信息 | result: CompletedProcess 对象 | 错误描述字符串 |

### src.constants

| 类/常量 | 说明 | 示例 |
|--------|------|------|
| ErrorMessages | 错误消息常量 | PATH_NOT_EXIST, NOT_GIT_REPO |
| StatusMessages | 状态消息常量 | UP_TO_DATE |
| CSVConfig | CSV 配置常量 | HEADERS, FILENAME_PREFIX |

### src.csv_writer

| 函数 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| get_current_time() | 获取当前时间字符串 | 无 | 时间字符串 |
| log_update_result(repo_name, repo_path, update_info, csv_path) | 记录更新结果到 CSV | 4 个字符串参数 | True/False |

## 开发和测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_utils.py
pytest tests/test_git_ops.py
pytest tests/test_csv_writer.py
pytest tests/test_main.py
pytest tests/test_integration.py
pytest tests/test_logging.py

# 生成覆盖率报告
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html  # HTML 报告
```

### 测试覆盖率

- 当前覆盖率：**97%**
- 测试用例数：**55**

## 项目结构

```
UpdateLocalGitHub/
├── update_github_repos.py     # 主程序入口
├── update_repos.bat            # 批处理文件（Windows）
├── src/
│   ├── __init__.py             # 包初始化
│   ├── constants.py            # 常量定义模块（错误消息、配置）
│   ├── utils.py                # 工具函数模块（路径验证、名称提取）
│   ├── git_ops.py              # Git 操作模块（检查更新、拉取）
│   └── csv_writer.py           # CSV 写入模块
├── tests/
│   ├── conftest.py             # 测试配置
│   ├── test_utils.py           # 工具函数测试
│   ├── test_git_ops.py         # Git 操作测试
│   ├── test_csv_writer.py      # CSV 写入测试
│   ├── test_main.py            # 主函数测试
│   ├── test_integration.py     # 集成测试
│   └── test_logging.py         # 日志和异常处理测试
├── requirements.txt            # 依赖列表
└── README.md                   # 本文件
```

## 代码规范

- 所有函数包含中文文档字符串（Docstring）
- 错误处理使用 Python logging 模块
- 中英文之间添加空格
- 变量名、函数名使用英文
- 常量集中管理在 `src/constants.py`

## 代码质量

本项目经过严格的代码审查，确保代码质量：

- **安全性**：路径安全验证，防止命令注入；禁止访问系统目录
- **健壮性**：完善的错误处理和异常捕获
- **可维护性**：模块化设计，常量集中管理
- **可测试性**：97% 测试覆盖率，55 个测试用例

## 许可证

MIT

## 技术栈

- Python 3.7+
- subprocess（内置模块）
- csv（内置模块）
- datetime（内置模块）
- logging（内置模块）
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-mock >= 3.10.0
