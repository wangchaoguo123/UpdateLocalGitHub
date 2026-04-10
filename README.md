# GitHub 仓库本地更新工具

批量检查和更新本地 GitHub 仓库的自动化工具。

## 功能特性

- 批量检查多个本地 GitHub 仓库是否有新更新
- 自动拉取更新
- **目录扫描模式**：递归扫描指定目录下的所有 Git 仓库
- **预览模式**：先查看哪些仓库需要更新，再决定是否更新
- 配置文件支持：可自定义排除目录列表
- 将更新历史记录到 CSV 文件
- 详细的控制台输出和日志记录
- **安全的路径验证**，防止命令注入攻击，禁止访问系统目录
- **路径遍历防护**：检测 `..` 序列
- **符号链接安全检查**：验证链接目标
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

### 方法一：扫描目录并更新（推荐）

```bash
# 扫描指定目录下的所有 Git 仓库并更新
python update_github_repos.py -d "D:\code"
python update_github_repos.py --dir "D:\code"
```

### 方法二：预览模式（先查看哪些需要更新）

```bash
# 仅显示需要更新的仓库，不执行更新
python update_github_repos.py -d "D:\code" --preview
```

预览模式会显示：
- 需要更新的仓库列表
- 已是最新状态的仓库
- 检查失败的仓库

确认后，去掉 `--preview` 参数执行更新。

### 方法三：直接指定仓库路径

```bash
python update_github_repos.py "D:\repo1" "D:\repo2" "D:\repo3"
```

### 方法四：使用批处理文件（Windows）

```batch
update_repos.bat "D:\repo1" "D:\repo2"
```

## 配置文件

### config.json

在项目根目录创建 `config.json` 配置文件：

```json
{
  "exclude_dirs": [
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    ".svn",
    ".hg"
  ],
  "git_timeout": 10,
  "fetch_timeout": 60,
  "pull_timeout": 60
}
```

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| exclude_dirs | 扫描时排除的目录列表 | node_modules, .venv, venv 等 |
| git_timeout | Git 命令超时（秒） | 10 |
| fetch_timeout | git fetch 超时（秒） | 60 |
| pull_timeout | git pull 超时（秒） | 60 |

## 输出说明

### 控制台输出格式（更新模式）

```
==================================================
  GitHub 仓库本地更新工具
==================================================

扫描目录: D:\code
排除目录: ['node_modules', 'venv', ...]

发现 5 个仓库

开始扫描目录更新...
==================================================

[仓库 1/5] D:\code\repo1
[检查] 正在检查更新...
[结果] 发现更新，正在拉取...
[输出] 已更新: abc1234 refactor: 优化代码
[记录] 已记录到 result_20260410.csv

[仓库 2/5] D:\code\repo2
[检查] 正在检查更新...
[结果] 已是最新，无需更新
[记录] 已记录到 result_20260410.csv

==================================================
完成！共处理 5 个仓库，成功 4 个，失败 1 个
==================================================
```

### 控制台输出格式（预览模式）

```
==================================================
  GitHub 仓库本地更新工具
==================================================

预览模式：只显示需要更新的仓库
==================================================

需要更新的仓库 (2 个)：
--------------------------------------------------
  [需更新] repo1
          D:\code\repo1
  [需更新] repo2
          D:\code\repo2

已是最新 (3 个)：
--------------------------------------------------
  [最新] repo3
  [最新] repo4
  [最新] repo5

==================================================
总计：5 个仓库
  需要更新: 2
  已是最新: 3
  检查失败: 0
==================================================

如需更新仓库，请去掉 --preview 参数重新运行
```

### CSV 文件结构

文件名格式：`result_YYYYMMDD.csv`

| 列名 | 说明 | 示例 |
|------|------|------|
| 仓库名称 | 仓库名（路径最后一部分） | repo1 |
| 本地路径 | 完整本地路径 | D:\repo1 |
| 更新时间 | 格式化时间戳 | 2026-04-10 10:30:15 |
| 更新履历 | 更新详情或状态信息 | 已更新: abc1234... |

### CSV 文件示例

```csv
仓库名称,本地路径,更新时间,更新履历
repo1,D:\repo1,2026-04-10 10:30:15,已更新: abc1234 refactor: 优化代码
repo2,D:\repo2,2026-04-10 10:30:18,已是最新
repo3,D:\repo3,2026-04-10 10:30:20,检查失败
```

## 安全特性

- **路径安全验证**：自动规范化路径，防止命令注入
- **路径遍历防护**：检测并阻止 `..` 路径遍历攻击
- **符号链接安全检查**：验证符号链接目标，防止逃逸
- **父目录权限验证**：检查访问父目录的读/执行权限
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
| 目录不存在 | 扫描目录路径不存在 | 检查目录路径是否正确 |
| 未发现任何 Git 仓库 | 目录中没有 Git 仓库 | 检查目录是否正确 |

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
| scan_git_repos(root_dir, exclude_dirs) | 递归扫描目录下的所有 Git 仓库 | root_dir: 目录路径, exclude_dirs: 排除列表 | 仓库路径列表 |
| check_repo_update(repo_path) | 检查仓库是否有更新 | repo_path: 路径字符串 | True/False/None |
| pull_repo(repo_path) | 执行 git pull 更新仓库 | repo_path: 路径字符串 | 更新信息或 None |
| analyze_git_error(result) | 分析 Git 命令错误信息 | result: CompletedProcess 对象 | 错误描述字符串 |

### src.config

| 函数 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| load_config(config_path) | 加载配置文件 | config_path: 配置文件路径 | 配置字典 |
| get_exclude_dirs() | 获取排除目录列表 | 无 | 目录列表 |
| get_git_timeout() | 获取 Git 命令超时时间 | 无 | 超时秒数 |
| get_fetch_timeout() | 获取 git fetch 超时时间 | 无 | 超时秒数 |
| get_pull_timeout() | 获取 git pull 超时时间 | 无 | 超时秒数 |

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
├── update_repos.bat           # 批处理文件（Windows）
├── config.json                # 配置文件（排除目录、超时）
├── src/
│   ├── __init__.py            # 包初始化
│   ├── config.py              # 配置加载模块
│   ├── constants.py           # 常量定义模块（错误消息、配置）
│   ├── utils.py               # 工具函数模块（路径验证、名称提取）
│   ├── git_ops.py             # Git 操作模块（检查更新、拉取、扫描）
│   └── csv_writer.py          # CSV 写入模块
├── tests/
│   ├── conftest.py            # 测试配置
│   ├── test_utils.py          # 工具函数测试
│   ├── test_git_ops.py        # Git 操作测试
│   ├── test_csv_writer.py     # CSV 写入测试
│   ├── test_main.py          # 主函数测试
│   ├── test_integration.py   # 集成测试
│   └── test_logging.py       # 日志和异常处理测试
├── requirements.txt           # 依赖列表
└── README.md                  # 本文件
```

## 代码规范

- 所有函数包含中文文档字符串（Docstring）
- 错误处理使用 Python logging 模块
- 中英文之间添加空格
- 变量名、函数名使用英文
- 常量集中管理在 `src/constants.py`
- 配置项通过 `config.json` 管理

## 代码质量

本项目经过严格的代码审查，确保代码质量：

- **安全性**：路径安全验证（路径遍历、符号链接、父目录权限）、防止命令注入、禁止访问系统目录
- **健壮性**：完善的错误处理和异常捕获
- **可维护性**：模块化设计，常量集中管理，配置外部化
- **可测试性**：97% 测试覆盖率，55 个测试用例

## 许可证

MIT

## 技术栈

- Python 3.7+
- subprocess（内置模块）
- csv（内置模块）
- datetime（内置模块）
- logging（内置模块）
- json（内置模块）
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-mock >= 3.10.0