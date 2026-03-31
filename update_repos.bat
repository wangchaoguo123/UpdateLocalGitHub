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
