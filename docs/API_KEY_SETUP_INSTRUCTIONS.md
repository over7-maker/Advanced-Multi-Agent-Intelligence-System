# 🔑 API Key Setup Instructions

## 🚨 CRITICAL: Add At Least One Valid API Key

The bulletproof AI system requires **at least one valid API key** from the supported providers to function. Without valid API keys, the system will correctly refuse to generate fake responses.

## ✅ Supported Providers

Add **any one** of these API keys to your repository secrets:

### **Recommended (Free/Cheap Options):**
- `DEEPSEEK_API_KEY` - DeepSeek API (via OpenRouter)
- `NVIDIA_API_KEY` - NVIDIA AI Playground
- `CEREBRAS_API_KEY` - Cerebras AI
- `CODESTRAL_API_KEY` - Mistral Codestral

### **Premium Options:**
- `CLAUDE_API_KEY` - Anthropic Claude
- `GPT4_API_KEY` - OpenAI GPT-4
- `COHERE_API_KEY` - Cohere AI
- `GROQAI_API_KEY` - Groq AI

## 🔧 How to Add API Keys

1. **Go to Repository Settings**
   - Navigate to your GitHub repository
   - Click on "Settings" tab
   - Click on "Secrets and variables" → "Actions"

2. **Add New Repository Secret**
   - Click "New repository secret"
   - Name: `DEEPSEEK_API_KEY` (or any supported provider)
   - Value: Your actual API key from the provider

3. **Verify the Secret**
   - The secret should show as "***" in the GitHub UI
   - Make sure the name matches exactly (case-sensitive)

## 🧪 Test Your Setup

After adding an API key, create a new PR to test:

1. **Expected Success:**
   ```
   🤖 BULLETPROOF REAL AI Analysis
   Status: ✅ REAL AI Analysis Verified
   Provider: deepseek (CONFIRMED REAL API CALL)
   Response Time: 3.47s (Actual API Response)
   ```

2. **Expected Failure (No Keys):**
   ```
   🚨 CRITICAL: NO REAL AI PROVIDERS AVAILABLE!
   ❌ Please add at least one valid API key to repository secrets
   ```

## 🔍 Troubleshooting

### **"Provider: Unknown" Error**
- **Cause:** No valid API keys available
- **Fix:** Add at least one API key from supported providers

### **"Response Time: 0s" Error**
- **Cause:** Fake AI response detected
- **Fix:** Ensure API key is valid and has sufficient credits

### **"Timeout" Error**
- **Cause:** Network issues or API rate limits
- **Fix:** Check API key validity and try again

### **"Permission Denied" Error**
- **Cause:** Repository secrets not accessible
- **Fix:** Ensure the workflow has proper permissions (already configured)

## 📊 Provider Status Check

The workflow will now show which providers are available:

```
🔍 Checking AI provider availability...
✅ DEEPSEEK_API_KEY: Available (32 chars)
❌ NVIDIA_API_KEY: Missing or invalid
❌ CEREBRAS_API_KEY: Missing or invalid
✅ COHERE_API_KEY: Available (28 chars)
📊 Total available providers: 2/16
```

## 🎯 Expected Results

Once you add a valid API key, you should see:

- ✅ **Real provider names** (deepseek, nvidia, etc.)
- ✅ **Variable response times** (2.3s, 4.7s, etc.)
- ✅ **Specific code analysis** with file names and line numbers
- ✅ **Bulletproof validation** in all responses

**No more fake responses like:**
- ❌ "Provider: AI System"
- ❌ "Response Time: 1.5s" (identical times)
- ❌ "AI-powered analysis completed successfully"
- ❌ "Mock/Fallback (No real AI used)"