# 🔧 Fixing GitHub Workflow Permission Issues

## 🚨 **Problem**: HTTP 403 Error when running `gh workflow run`

## ✅ **SOLUTION 1: Fix GitHub CLI Authentication**

### **Step 1: Re-authenticate GitHub CLI**
```bash
# Logout and re-login
gh auth logout
gh auth login

# Choose GitHub.com
# Choose HTTPS
# Choose Yes for Git operations
# Choose Login with a web browser
# Follow the browser authentication
```

### **Step 2: Verify Authentication**
```bash
# Check current authentication
gh auth status

# Test with a simple command
gh repo view
```

### **Step 3: Check Repository Access**
```bash
# Verify you have access to the repository
gh repo view ${{ github.repository }}

# Check if you can see workflows
gh workflow list
```

## ✅ **SOLUTION 2: Alternative Ways to Run Audit**

### **Method 1: Manual Workflow Dispatch via GitHub Web UI**
1. Go to your repository on GitHub
2. Click on **Actions** tab
3. Find **"Comprehensive Workflow & Code Audit"** workflow
4. Click **"Run workflow"** button
5. Select branch and options
6. Click **"Run workflow"**

### **Method 2: Direct Python Script Execution**
```bash
# Run the audit engine directly
cd /workspace
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output audit_results.json
```

### **Method 3: Create a Simple Test Script**
```bash
# Create a test runner
cat > run_audit_test.sh << 'EOF'
#!/bin/bash
echo "🔍 Running Comprehensive Audit Test..."
cd /workspace
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output test_audit_results.json

echo "📊 Audit Results:"
cat test_audit_results.json | jq '.statistics'
EOF

chmod +x run_audit_test.sh
./run_audit_test.sh
```

## ✅ **SOLUTION 3: Fix Workflow File Issues**

### **Check if Workflow File Exists**
```bash
# Verify workflow file exists
ls -la .github/workflows/comprehensive-audit.yml

# Check file permissions
ls -la .github/workflows/
```

### **Validate YAML Syntax**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/comprehensive-audit.yml'))"
```

## ✅ **SOLUTION 4: Enable GitHub Actions**

### **Check if GitHub Actions is Enabled**
1. Go to repository **Settings**
2. Click **Actions** in left sidebar
3. Ensure **Actions permissions** is set to **Allow all actions and reusable workflows**
4. Check **Workflow permissions** is set to **Read and write permissions**

## ✅ **SOLUTION 5: Use Alternative Commands**

### **Method 1: Using curl with GitHub API**
```bash
# Get repository info
REPO_OWNER="your-username"
REPO_NAME="your-repo-name"
GITHUB_TOKEN="your-personal-access-token"

# Trigger workflow via API
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/workflows/comprehensive-audit.yml/dispatches" \
  -d '{"ref":"main"}'
```

### **Method 2: Using GitHub Actions API**
```bash
# List available workflows
gh api repos/${{ github.repository }}/actions/workflows

# Get workflow ID
WORKFLOW_ID=$(gh api repos/${{ github.repository }}/actions/workflows | jq '.workflows[] | select(.name=="Comprehensive Workflow & Code Audit") | .id')

# Trigger workflow
gh api repos/${{ github.repository }}/actions/workflows/$WORKFLOW_ID/dispatches \
  --method POST \
  -f ref=main
```

## 🎯 **RECOMMENDED IMMEDIATE ACTION**

### **Quick Test (No GitHub CLI needed)**
```bash
# Run this to test the audit system immediately
cd /workspace
python3 .github/scripts/comprehensive_audit_engine.py \
  --audit-type comprehensive \
  --create-issues false \
  --notify-on-failure false \
  --output immediate_audit_results.json

echo "✅ Audit completed! Results saved to immediate_audit_results.json"
```

## 🔍 **TROUBLESHOOTING STEPS**

### **Step 1: Check GitHub CLI Version**
```bash
gh --version
# Should be 2.0.0 or higher
```

### **Step 2: Check Repository Access**
```bash
# Verify you can access the repository
gh repo view

# Check if you can see workflows
gh workflow list
```

### **Step 3: Check Workflow File**
```bash
# Verify the workflow file exists and is valid
ls -la .github/workflows/comprehensive-audit.yml
head -20 .github/workflows/comprehensive-audit.yml
```

### **Step 4: Test with Simple Workflow**
```bash
# Try running a simpler workflow first
gh workflow run workflow-audit-monitor.yml
```

## 🎉 **SUCCESS INDICATORS**

You'll know it's working when you see:
- ✅ No HTTP 403 errors
- ✅ Workflow appears in GitHub Actions tab
- ✅ Audit results are generated
- ✅ Issues are created (if enabled)

## 🚨 **If All Else Fails**

### **Emergency Workaround**
```bash
# Create a simple test workflow
cat > .github/workflows/test-audit.yml << 'EOF'
name: Test Audit
on: workflow_dispatch
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Audit
        run: |
          python3 .github/scripts/comprehensive_audit_engine.py \
            --audit-type comprehensive \
            --create-issues false \
            --notify-on-failure false \
            --output test_results.json
          cat test_results.json
EOF

# Commit and push
git add .github/workflows/test-audit.yml
git commit -m "Add test audit workflow"
git push

# Then run it via GitHub UI
```

---

**Try the immediate action first, then work through the solutions in order!** 🚀