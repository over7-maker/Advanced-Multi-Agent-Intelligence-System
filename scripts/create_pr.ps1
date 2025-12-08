# PowerShell script to create PR on GitHub
# Usage: .\scripts\create_pr.ps1

Write-Host "Creating Pull Request..." -ForegroundColor Cyan

# Check if GitHub CLI is installed
try {
    $ghVersion = gh --version
    Write-Host "GitHub CLI found" -ForegroundColor Green
} catch {
    Write-Host "GitHub CLI not found. Please install it first." -ForegroundColor Red
    Write-Host "Install: winget install --id GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# Check if authenticated
try {
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Not authenticated. Please run: gh auth login" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Please authenticate: gh auth login" -ForegroundColor Yellow
    exit 1
}

# Get current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Cyan

# Check if branch exists on remote
$remoteBranch = git ls-remote --heads origin $currentBranch
if ($remoteBranch) {
    Write-Host "Branch already exists on remote" -ForegroundColor Green
} else {
    Write-Host "Pushing branch to remote..." -ForegroundColor Yellow
    git push -u origin $currentBranch
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to push branch" -ForegroundColor Red
        exit 1
    }
}

# Create PR
Write-Host "Creating Pull Request..." -ForegroundColor Cyan
$prTitle = "feat: Complete AMAS Integration Verification & Improvements"
$prBody = Get-Content -Path "PR_DESCRIPTION.md" -Raw

$prUrl = gh pr create `
    --title $prTitle `
    --body $prBody `
    --base main `
    --head $currentBranch

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Pull Request created successfully!" -ForegroundColor Green
    Write-Host "PR URL: $prUrl" -ForegroundColor Cyan
    Write-Host "`nYou can view it at: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pulls" -ForegroundColor Yellow
} else {
    Write-Host "Failed to create PR" -ForegroundColor Red
    exit 1
}



