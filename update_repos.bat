@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =====================================
echo   GitHub 仓库本地更新工具
echo =====================================
echo.

REM 检查是否提供了参数
if "%~1"=="" (
    echo 错误: 请提供至少一个仓库路径
    echo.
    echo 使用方法:
    echo   %~nx0 ^<仓库路径1^> [仓库路径2] ...
    echo.
    echo 示例:
    echo   %~nx0 C:\repos\project1 C:\repos\project2
    echo.
    pause
    exit /b 1
)

REM 切换到批处理文件所在目录
cd /d "%~dp0"

REM 设置 Python 输出编码为 UTF-8
set PYTHONIOENCODING=utf-8

REM 运行 Python 脚本
python update_github_repos.py %*

set error_code=!errorlevel!

if !error_code! neq 0 (
    echo.
    echo 程序执行失败，错误码: !error_code!
) else (
    echo.
    echo 程序执行成功
)

echo.
pause
