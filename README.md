# GitHub 仓库本地更新工具

批量检查和更新本地 GitHub 仓库的自动化工具。

## 功能特性

- 批量检查多个本地 GitHub 仓库是否有新更新
- 自动拉取更新
- 将更新历史记录到 CSV 文件
- 详细的控制台输出和错误提示

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
====================================
  GitHub 仓库本地更新工具
====================================

开始检查仓库更新...
=====================================

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

=====================================
完成！共处理 3 个仓库，成功 2 个，失败 1 个
=====================================

程序执行成功
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

## 错误处理

工具采用"跳过错误"策略：
- 单个仓库失败不会影响其他仓库的处理
- 错误信息会记录到控制台和 CSV 文件
- 程序会显示成功和失败的统计信息

### 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| 路径不存在 | 指定的路径不存在 | 检查路径拼写和权限 |
| 路径不是目录 | 路径是文件而非目录 | 检查路径是否正确 |
| 不是 Git 仓库 | 目录不是 Git 仓库 | 检查是否包含 .git 目录 |
| 检查更新失败 | git 命令执行失败 | 检查 Git 是否正确安装和配置 |
| 拉取更新失败 | git pull 命令失败 | 检查网络连接和仓库权限 |

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

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 测试覆盖率目标

≥ 80%

## 项目结构

```
UpdateLocalGitHub/
├── update_github_repos.py     # 主程序
├── update_repos.bat            # 批处理文件（Windows）
├── src/
│   ├── __init__.py             # 包初始化
│   ├── utils.py                # 工具函数模块
│   ├── git_ops.py              # Git 操作模块
│   └── csv_writer.py           # CSV 写入模块
├── tests/
│   ├── conftest.py             # 测试配置
│   ├── test_utils.py           # 工具函数测试
│   ├── test_git_ops.py         # Git 操作测试
│   ├── test_csv_writer.py      # CSV 写入测试
│   ├── test_main.py            # 主函数测试
│   └── test_integration.py     # 集成测试
├── requirements.txt            # 依赖列表
└── README.md                   # 本文件
```

## 许可证

MIT

## 技术栈

- Python 3.7+
- subprocess（内置模块）
- csv（内置模块）
- datetime（内置模块）
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- pytest-mock >= 3.10.0
