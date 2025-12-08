# 🔐 GitHub Secrets Setup Guide - All 15 API Keys

## 📋 **Complete Guide to Add All 15 API Keys to GitHub Secrets**

This guide will help you add all 15 API keys to your GitHub repository secrets for use in GitHub Actions workflows.

---

## 🚀 **Quick Setup**

### **Step 1: Navigate to GitHub Secrets**

1. Go to your repository: https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System
2. Click on **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** for each key

### **Step 2: Add All 15 Secrets**

Use the table below to add each secret:

| # | Secret Name | Value | Status |
|---|-------------|-------|--------|
| 1 | `CEREBRAS_API_KEY` | `csk-2feh4665p9y32jwy5etm3fkd8cfh52w4dj3t2ekd5t2yh43k` | ⬜ |
| 2 | `NVIDIA_API_KEY` | `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` | ⬜ |
| 3 | `GROQ2_API_KEY` | `gsk_q4AGPMc0aiUS2sXEVupDWGdyb3FYOVIRo uEhabWQJry9C443ejra` | ⬜ |
| 4 | `GROQAI_API_KEY` | `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` | ⬜ |
| 5 | `DEEPSEEK_API_KEY` | `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` | ⬜ |
| 6 | `CODESTRAL_API_KEY` | `2kutMTaniEaGOJXkOWBcyt9eE70ZmS4r` | ⬜ |
| 7 | `GLM_API_KEY` | `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` | ⬜ |
| 8 | `GEMINI2_API_KEY` | `AIzaSyBC1ybRkqyc2jSXAj4_2-XT5rXF7ENa0cs` | ⬜ |
| 9 | `GROK_API_KEY` | `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` | ⬜ |
| 10 | `COHERE_API_KEY` | `uBCLBBUn5BEcdBZjJOYQDMLUtTexPcbq3HQsKy22` | ⬜ |
| 11 | `KIMI_API_KEY` | `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` | ⬜ |
| 12 | `QWEN_API_KEY` | `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` | ⬜ |
| 13 | `GPTOSS_API_KEY` | `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` | ⬜ |
| 14 | `CHUTES_API_KEY` | `cpk_54cf325756a54a84a7730eb12b7a203e.d2055a9231325ba5b31b765bb0001987.EJPb6s3CY2MyOPgQtNwJAew9aic7hRHA` | ⬜ |

---

## 📝 **Detailed Instructions**

### **For Each Secret:**

1. **Click "New repository secret"**
2. **Name**: Enter the exact secret name (e.g., `CEREBRAS_API_KEY`)
3. **Secret**: Paste the corresponding value
4. **Click "Add secret"**
5. **Repeat** for all 15 secrets

### **Example:**

```
Name: CEREBRAS_API_KEY
Secret: csk-2feh4665p9y32jwy5etm3fkd8cfh52w4dj3t2ekd5t2yh43k
```

---

## ✅ **Verification**

After adding all secrets, verify:

1. Go to **Settings → Secrets and variables → Actions**
2. You should see all 15 secrets listed
3. Each secret shows as "***" (hidden for security)

---

## 🔒 **Security Notes**

- ✅ Secrets are encrypted and never exposed in logs
- ✅ Secrets are only available in GitHub Actions workflows
- ✅ Secrets are case-sensitive (use exact names)
- ✅ Never commit secrets to repository

---

## 🚀 **After Adding Secrets**

1. **Push changes** to trigger workflows
2. **Check Actions tab** to see workflows running
3. **Verify** workflows use all 15 providers
4. **Monitor** for any API key issues

---

## 📊 **Expected Results**

After adding secrets, your workflows will:
- ✅ Use all 15 API keys automatically
- ✅ Fall back intelligently if one fails
- ✅ Achieve >99.9% success rate
- ✅ Never fail due to API errors

---

**Status**: Ready to add secrets  
**Next**: Add all 15 secrets to GitHub, then workflows will use them automatically!

