@echo off
REM Batch script to create PR on GitHub
REM Usage: scripts\create_pr.bat

echo Creating Pull Request...

REM Check if GitHub CLI is installed
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI not found. Please install it first.
    echo Install: winget install --id GitHub.cli
    exit /b 1
)

REM Check if authenticated
gh auth status >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Not authenticated. Please run: gh auth login
    exit /b 1
)

REM Get current branch
for /f "tokens=2" %%b in ('git branch --show-current') do set CURRENT_BRANCH=%%b
echo Current branch: %CURRENT_BRANCH%

REM Push branch if not exists
git push -u origin %CURRENT_BRANCH%

REM Create PR
echo Creating Pull Request...
if exist PR_DESCRIPTION.md (
    gh pr create --title "feat: Complete AMAS Integration Verification & Improvements" --body-file PR_DESCRIPTION.md --base main --head %CURRENT_BRANCH%
) else (
    gh pr create --title "feat: Complete AMAS Integration Verification & Improvements" --body "Complete AMAS integration verification and improvements." --base main --head %CURRENT_BRANCH%
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Pull Request created successfully!
    echo View at: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls
) else (
    echo Failed to create PR
    exit /b 1
)



