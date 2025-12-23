# 🖥️ Cursor Desktop + GitHub Integration Guide

## Complete Guide to Using Cursor Desktop with Your GitHub Project

This guide shows you how to view PR comments, AI analysis results, and interact with your GitHub project directly from Cursor desktop.

---

## 📋 **Table of Contents**

1. [Setting Up Git in Cursor](#setting-up-git-in-cursor)
2. [Viewing PRs in Cursor](#viewing-prs-in-cursor)
3. [Seeing AI Analysis Comments](#seeing-ai-analysis-comments)
4. [Working with PRs Locally](#working-with-prs-locally)
5. [Syncing with GitHub](#syncing-with-github)
6. [Checking Workflow Results](#checking-workflow-results)

---

## 1️⃣ **Setting Up Git in Cursor**

### **Step 1: Verify Git is Configured**

1. **Open Terminal in Cursor**:
   - Press `` Ctrl+` `` (backtick) or go to **Terminal → New Terminal**

2. **Check Git Status**:
   ```bash
   git status
   git remote -v
   ```

3. **If not configured, set up Git**:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### **Step 2: Configure GitHub Authentication**

1. **Generate Personal Access Token** (if needed):
   - Go to: https://github.com/settings/tokens
   - Click **Generate new token (classic)**
   - Select scopes: `repo`, `workflow`, `read:org`
   - Copy the token

2. **Authenticate Git**:
   ```bash
   git config --global credential.helper store
   # When prompted, use your GitHub username and token as password
   ```

---

## 2️⃣ **Viewing PRs in Cursor**

### **Method 1: Using GitLens Extension (Recommended)**

1. **Install GitLens**:
   - Press `Ctrl+Shift+X` (Extensions)
   - Search for **"GitLens"**
   - Click **Install**

2. **Authenticate GitLens with GitHub**:
   - After installation, GitLens will prompt for GitHub authentication
   - Click **Sign in with GitHub**
   - Follow the browser authentication flow

3. **View PRs**:
   - Open **Source Control** panel (Ctrl+Shift+G)
   - Look for **GitLens** section
   - Click **Pull Requests** to see all PRs
   - Click on a PR to see details

### **Method 2: Using GitHub CLI (gh)**

1. **Install GitHub CLI**:
   ```bash
   # Windows (using winget)
   winget install --id GitHub.cli
   
   # Or download from: https://cli.github.com/
   ```

2. **Authenticate**:
   ```bash
   gh auth login
   # Follow prompts to authenticate
   ```

3. **View PRs in Terminal**:
   ```bash
   # List all PRs
   gh pr list
   
   # View specific PR
   gh pr view 3542
   
   # View PR comments
   gh pr view 3542 --comments
   ```

### **Method 3: Using Source Control Panel**

1. **Open Source Control**:
   - Press `Ctrl+Shift+G` or click Source Control icon

2. **Check Out PR Branch**:
   - Click **...** (three dots) → **Branch** → **Checkout...**
   - Or use command: `git fetch origin pull/3542/head:pr-3542 && git checkout pr-3542`

---

## 3️⃣ **Seeing AI Analysis Comments**

### **Viewing PR Comments in Cursor**

#### **Option A: Using GitLens**

1. **Open GitLens Panel**:
   - Press `Ctrl+Shift+G` → **GitLens** section
   - Expand **Pull Requests**
   - Find your PR: `cursor/enhance-production-readiness-for-multi-agent-ai-platform-3542`

2. **View Comments**:
   - Click on the PR
   - Scroll to see all comments
   - AI analysis comments will appear with `@github-actions` bot

#### **Option B: Using GitHub CLI**

```bash
# View all comments on a PR
gh pr view 3542 --comments

# View in browser
gh pr view 3542 --web
```

#### **Option C: Using Terminal + Browser**

```bash
# Open PR in browser
gh pr view 3542 --web

# Or manually
start https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/pull/3542
```

### **Understanding AI Analysis Output**

Your **BULLETPROOF REAL AI Analysis** comments show:

```
🤖 BULLETPROOF REAL AI Analysis
Status: ✅ REAL AI Verified
Provider: cerebras (or other provider)
Response Time: 2.88s
Validation: Bulletproof validated ✓

🔍 Analysis
[Detailed analysis here...]
```

**Key Sections**:
- **Status**: Shows if AI is verified (✅ REAL AI Verified)
- **Provider**: Which AI provider was used (cerebras, nvidia, etc.)
- **Response Time**: How long the analysis took
- **Validation**: Bulletproof validation status

---

## 4️⃣ **Working with PRs Locally**

### **Checkout PR Branch**

```bash
# Fetch PR branch
git fetch origin pull/3542/head:pr-3542

# Checkout the branch
git checkout pr-3542

# Or create a new branch based on PR
git checkout -b local-pr-3542 origin/pr-3542
```

### **View PR Changes**

```bash
# See all changes in PR
git diff origin/main...pr-3542

# See changes in specific file
git diff origin/main...pr-3542 -- path/to/file

# See commit history
git log origin/main..pr-3542
```

### **Make Changes and Push**

```bash
# Make your changes
# ... edit files in Cursor ...

# Stage changes
git add .

# Commit
git commit -m "fix: address AI analysis recommendations"

# Push to PR branch
git push origin pr-3542
```

---

## 5️⃣ **Syncing with GitHub**

### **Pull Latest Changes**

```bash
# Pull from main branch
git checkout main
git pull origin main

# Pull from PR branch
git checkout pr-3542
git pull origin pr-3542
```

### **Push Local Changes**

```bash
# Stage all changes
git add .

# Commit
git commit -m "Your commit message"

# Push
git push origin your-branch-name
```

### **Using Cursor's Built-in Git**

1. **Source Control Panel** (`Ctrl+Shift+G`):
   - See all changed files
   - Stage/unstage files
   - Commit changes
   - Push/pull

2. **Commit**:
   - Type commit message in the box
   - Press `Ctrl+Enter` to commit
   - Click **Sync** to push

---

## 6️⃣ **Checking Workflow Results**

### **View Workflow Status in Terminal**

```bash
# List recent workflow runs
gh run list

# View specific workflow run
gh run view <run-id>

# Watch workflow in real-time
gh run watch <run-id>
```

### **View Workflow Results in Browser**

```bash
# Open Actions tab
start https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/actions

# Open specific PR checks
gh pr checks 3542
```

### **Understanding Workflow Results**

Your PR shows:
- ✅ **24 successful checks**
- ⏭️ **1 skipped check**
- 🤖 **AI workflows** (Bulletproof AI Analysis, etc.)

**Check Status**:
- ✅ Green = Success
- ❌ Red = Failed
- ⏭️ Gray = Skipped
- 🟡 Yellow = In Progress

---

## 🔧 **Practical Workflow**

### **Daily Workflow**

1. **Morning - Check PRs**:
   ```bash
   # See all open PRs
   gh pr list
   
   # View specific PR
   gh pr view 3542
   ```

2. **Review AI Analysis**:
   ```bash
   # View comments
   gh pr view 3542 --comments
   
   # Or open in browser
   gh pr view 3542 --web
   ```

3. **Work on PR**:
   ```bash
   # Checkout PR branch
   git fetch origin pull/3542/head:pr-3542
   git checkout pr-3542
   
   # Make changes in Cursor
   # ... edit files ...
   
   # Commit and push
   git add .
   git commit -m "fix: address AI recommendations"
   git push origin pr-3542
   ```

4. **Check Workflow Results**:
   ```bash
   # Check PR status
   gh pr checks 3542
   
   # View workflow runs
   gh run list --workflow="Bulletproof AI PR Analysis"
   ```

---

## 📊 **Quick Reference Commands**

### **PR Management**

```bash
# List all PRs
gh pr list

# View PR details
gh pr view <number>

# View PR comments
gh pr view <number> --comments

# Open PR in browser
gh pr view <number> --web

# Check PR status
gh pr checks <number>

# Checkout PR locally
git fetch origin pull/<number>/head:pr-<number>
git checkout pr-<number>
```

### **Git Operations**

```bash
# Status
git status

# Pull latest
git pull origin main

# Push changes
git push origin <branch>

# View changes
git diff

# Commit
git commit -m "message"
```

### **Workflow Management**

```bash
# List workflows
gh workflow list

# List workflow runs
gh run list

# View workflow run
gh run view <run-id>

# Watch workflow
gh run watch <run-id>
```

---

## 🎯 **Viewing Your AI Analysis Results**

### **In Cursor Desktop**

1. **Using GitLens**:
   - Open Source Control (`Ctrl+Shift+G`)
   - GitLens → Pull Requests
   - Click on PR → View Comments
   - Scroll to see AI analysis

2. **Using Terminal**:
   ```bash
   # View comments
   gh pr view 3542 --comments
   
   # Filter for AI comments
   gh pr view 3542 --comments | grep "BULLETPROOF"
   ```

3. **Using Browser** (Recommended):
   ```bash
   # Open PR in browser
   gh pr view 3542 --web
   ```
   - Navigate to **Conversation** tab
   - Scroll to see all `@github-actions` comments
   - Each comment shows:
     - 🤖 BULLETPROOF REAL AI Analysis
     - Status, Provider, Response Time
     - Detailed analysis sections

### **Understanding Analysis Sections**

Each AI analysis comment includes:

1. **🔍 Analysis** - Main analysis content
2. **Code Quality Issues** - Code quality problems
3. **Potential Bugs** - Logic errors
4. **Security Vulnerabilities** - Security issues
5. **Performance Bottlenecks** - Performance issues
6. **Best Practice Violations** - Best practice issues
7. **📊 Verification** - AI verification status

---

## ✅ **Troubleshooting**

### **GitLens Not Showing PRs**

1. **Re-authenticate**:
   - GitLens → Settings → GitHub Authentication
   - Sign out and sign in again

2. **Check Repository**:
   - Ensure you're in the correct repository
   - Verify remote URL: `git remote -v`

### **Can't See Comments**

1. **Use GitHub CLI**:
   ```bash
   gh pr view <number> --comments
   ```

2. **Open in Browser**:
   ```bash
   gh pr view <number> --web
   ```

### **Workflow Not Running**

1. **Check GitHub Actions**:
   ```bash
   gh workflow list
   gh run list
   ```

2. **View Workflow File**:
   ```bash
   cat .github/workflows/bulletproof-ai-pr-analysis.yml
   ```

---

## 🚀 **Best Practices**

1. **Always Pull Before Push**:
   ```bash
   git pull origin main
   ```

2. **Check PR Status**:
   ```bash
   gh pr checks <number>
   ```

3. **Review AI Analysis**:
   - Read comments carefully
   - Address critical issues first
   - Test fixes before pushing

4. **Use Branches**:
   ```bash
   git checkout -b feature/new-feature
   ```

5. **Commit Often**:
   - Small, focused commits
   - Clear commit messages

---

## 📚 **Additional Resources**

- **GitLens Documentation**: https://gitlens.amod.io/
- **GitHub CLI Docs**: https://cli.github.com/manual/
- **Cursor Git Guide**: https://docs.cursor.com/

---

## 🎯 **Quick Scripts for PR Analysis**

### **View PR Comments (Including AI Analysis)**

```bash
# View all comments on PR #3542
python scripts/view_pr_comments.py 3542

# View only AI analysis comments
python scripts/view_pr_comments.py 3542 --ai-only

# Open PR in browser
python scripts/view_pr_comments.py 3542 --web
```

### **Check PR Workflow Status**

```bash
# Check all workflow checks for PR #3542
python scripts/check_pr_workflows.py 3542

# Or use GitHub CLI directly
gh pr checks 3542
```

---

## 🎉 **Summary**

✅ **View PRs**: Use GitLens or `gh pr list`  
✅ **See Comments**: `python scripts/view_pr_comments.py <PR_NUMBER>`  
✅ **Check Workflows**: `python scripts/check_pr_workflows.py <PR_NUMBER>`  
✅ **Work Locally**: Checkout PR branch and edit  
✅ **Sync Changes**: Push to GitHub  

**Status**: 🟢 Ready to use Cursor with GitHub!

---

**Last Updated**: Complete integration guide ready  
**Next**: Start using Cursor with your GitHub project!

