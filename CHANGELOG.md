# 更新日志

本文件记录所有重要的项目变更，格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 完整的本地 GitHub 仓库更新检查工具
- 批量检查多个本地 GitHub 仓库是否有更新
- 自动拉取更新功能
- 更新历史记录到 CSV 文件
- 支持自定义 CSV 文件路径和仓库目录

### 修复
- 路径安全验证，防止命令注入攻击
- Git worktree 支持，同时处理 .git 文件和目录情况
- 超时机制，防止 Git 命令挂起

### 文档
- 完整的 README.md 使用说明
- 项目规格文档和实现计划
- 中文文档字符串（Docstring）规范

### 测试
- 45 个单元测试，覆盖率 96%
- 包括单元测试、集成测试、日志和异常处理测试
- 测试驱动开发（TDD）方法

### 重构
- 代码结构优化
- 安全性改进
- 日志功能增强

## [0.1.0] - 2026-03-31

### 新增
- 初始版本：本地 GitHub 仓库更新检查工具
- 核心模块：utils.py（工具函数）
- 核心模块：git_ops.py（Git 操作）
- 核心模块：csv_writer.py（CSV 写入）
- 主程序：update_github_repos.py
- 批处理文件：update_repos.bat

### 文档
- 项目 README.md
- 项目规格文档
- 实现计划

### 测试
- pytest 测试配置
- 所有核心模块的测试文件