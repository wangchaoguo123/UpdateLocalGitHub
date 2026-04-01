@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Error: Please provide at least one repository path
    echo.
    echo Usage:
    echo   %~nx0 ^<repo_path1^> [repo_path2] ...
    echo.
    echo Example:
    echo   %~nx0 C:\repos\project1 C:\repos\project2
    echo.
    pause
    exit /b 1
)

cd /d "%~dp0"

set PYTHONIOENCODING=utf-8

python update_github_repos.py %*

set error_code=!errorlevel!

if !error_code! neq 0 (
    echo.
    echo Program failed with error code: !error_code!
) else (
    echo.
    echo Program completed successfully
)

echo.
pause
