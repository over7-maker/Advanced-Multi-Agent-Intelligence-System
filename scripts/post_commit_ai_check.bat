@echo off
REM Post-Commit Hook: Check AI Analysis (Windows)
REM Add this to your .git/hooks/post-commit or run manually after commits

echo 🔍 Checking for PR number...

REM Try to get PR number from current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set BRANCH=%%i
echo | findstr /R /C:"pr.*[0-9]" >nul
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%i in ('git branch --show-current ^| findstr /R /C:"[0-9]"') do set PR_NUMBER=%%i
)

if "%PR_NUMBER%"=="" (
    echo ⚠️  Could not auto-detect PR number.
    echo 💡 Run manually: python scripts/wait_for_ai_analysis.py ^<PR_NUMBER^> --wait
    exit /b 0
)

echo ✅ Found PR #%PR_NUMBER%
echo ⏳ Waiting for AI Analysis...

python scripts/wait_for_ai_analysis.py %PR_NUMBER% --wait












