@echo off
REM Simple script to create PR - Step by step
echo ========================================
echo AMAS PR Creation Script
echo ========================================
echo.

REM Step 1: Check current branch
echo [Step 1] Checking current branch...
for /f "tokens=*" %%b in ('git branch --show-current') do set CURRENT_BRANCH=%%b
echo Current branch: %CURRENT_BRANCH%
echo.

REM Step 2: Check if changes exist
echo [Step 2] Checking for changes...
git status --short
if %ERRORLEVEL% NEQ 0 (
    echo No changes to commit.
    pause
    exit /b 1
)
echo.

REM Step 3: Add all changes
echo [Step 3] Adding all changes...
git add -A
echo Changes staged.
echo.

REM Step 4: Create commit
echo [Step 4] Creating commit...
git commit -m "feat: Complete AMAS Integration Verification and Improvements" -m "Add all 12 specialized agents extending BaseAgent" -m "Enhance AI router with 26 providers" -m "Complete database schema with all 11 tables" -m "Verify ML predictions integration" -m "Verify all cache services with correct TTLs" -m "Verify WebSocket real-time updates" -m "Verify all platform integrations" -m "Verify 50+ Prometheus metrics" -m "Verify frontend complete integration" -m "Verify Docker/K8s production configs" -m "Verify security measures" -m "Add comprehensive verification scripts" -m "Add end-to-end integration test" -m "Add complete verification report" -m "All 31 architectural rules verified and implemented. System is fully integrated and production-ready."
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create commit.
    pause
    exit /b 1
)
echo Commit created successfully.
echo.

REM Step 5: Push to GitHub
echo [Step 5] Pushing to GitHub...
echo Please make sure you are authenticated with GitHub.
echo If not, run: scripts\setup_git_auth.bat
echo.
git push -u origin %CURRENT_BRANCH%
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Push failed. Possible reasons:
    echo 1. Not authenticated with GitHub
    echo 2. No write access to repository
    echo.
    echo Please run: scripts\setup_git_auth.bat
    pause
    exit /b 1
)
echo.
echo ✅ Push successful!
echo.

REM Step 6: Create PR using GitHub CLI
echo [Step 6] Creating Pull Request...
where gh >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo GitHub CLI not found. Please create PR manually:
    echo https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/compare/main...%CURRENT_BRANCH%
    pause
    exit /b 0
)

gh pr create --title "feat: Complete AMAS Integration Verification & Improvements" --body-file PR_DESCRIPTION.md --base main --head %CURRENT_BRANCH%
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Pull Request created successfully!
    echo View at: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls
) else (
    echo.
    echo ⚠️  Failed to create PR automatically.
    echo Please create it manually:
    echo https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/compare/main...%CURRENT_BRANCH%
)

echo.
pause



