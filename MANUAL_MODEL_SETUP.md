# AMAS Manual Model Setup Guide

## 🚀 Quick Start - Get AMAS Working in 5 Minutes

### **Step 1: Open the Web Interface**
Double-click this file to open AMAS in your browser:
```
amas_web_interface.html
```

### **Step 2: Download a Model Manually**

#### **Option A: Use Ollama Desktop (Easiest)**
1. Download Ollama Desktop from: https://ollama.ai/download
2. Install and run Ollama Desktop
3. In the Ollama Desktop app, click "Pull a model"
4. Try these models (in order of preference):
   - `phi3:mini` (smallest, fastest)
   - `gemma2:2b` (small)
   - `mistral:7b` (medium)
   - `llama3.1:8b` (larger)

#### **Option B: Command Line (Advanced)**
Open Command Prompt and run:
```bash
# Try the smallest model first
ollama pull phi3:mini

# If that works, try a larger one
ollama pull gemma2:2b
```

### **Step 3: Test AMAS**
1. Open the web interface
2. Select your downloaded model
3. Ask: "Hello! What is AMAS?"
4. Enjoy your AI assistant!

## 🔧 Troubleshooting

### **If Models Won't Download:**
1. **Check Internet Connection**: Make sure you have stable internet
2. **Try Different Models**: Start with the smallest models first
3. **Use Ollama Desktop**: It handles downloads better than command line
4. **Check Firewall**: Make sure Ollama can access the internet

### **If Web Interface Doesn't Work:**
1. Make sure Docker is running: `docker-compose ps`
2. Check LLM service: `curl http://localhost:11434/api/tags`
3. Restart services: `docker-compose restart llm-service`

## 🎯 What You Can Do with AMAS

### **Basic Chat**
- Ask questions
- Get explanations
- Creative writing
- Code help

### **Advanced Features** (Coming Soon)
- Multi-agent orchestration
- Code analysis
- Research assistance
- Document processing

## 📞 Need Help?

1. **Check the logs**: `docker-compose logs llm-service`
2. **Restart everything**: `docker-compose down && docker-compose up -d`
3. **Validate system**: `python validate_system.py`

## 🎉 Success!

Once you have a model working, you'll see:
- ✅ Model appears in the web interface dropdown
- ✅ You can send messages and get responses
- ✅ AMAS is fully operational!

**Your AMAS system is ready - just needs a model to be complete!**
