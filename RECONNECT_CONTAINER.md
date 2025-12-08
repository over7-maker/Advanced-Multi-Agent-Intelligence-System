# 🔌 How to Reconnect to AMAS Development Container

## 📋 Quick Steps to Reconnect

### **Method 1: Using VS Code/Cursor Command Palette (Recommended)**

1. **Open Command Palette:**
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Or click `View` → `Command Palette`

2. **Reconnect to Container:**
   - Type: `Dev Containers: Reopen in Container`
   - Select the command
   - Wait for the container to start and connect

3. **Alternative Commands:**
   - `Dev Containers: Reopen Folder in Container`
   - `Remote-Containers: Reopen in Container`

---

### **Method 2: Using the Bottom-Left Corner**

1. **Click the Green Icon:**
   - Look at the bottom-left corner of VS Code/Cursor
   - You should see a green icon with `><` or container status

2. **Select "Reopen in Container":**
   - Click the icon
   - Select `Reopen in Container` from the menu

---

### **Method 3: Using the Remote Indicator**

1. **Check Remote Status:**
   - Look at the bottom-left corner
   - If it shows "WSL" or "Local", click it

2. **Select Container:**
   - Choose `Reopen in Container`
   - Or `Attach to Running Container` if container is already running

---

### **Method 4: If Container is Already Running**

1. **Attach to Running Container:**
   - Press `Ctrl+Shift+P`
   - Type: `Dev Containers: Attach to Running Container`
   - Select your AMAS container from the list

---

## 🔍 Verify Connection

After reconnecting, verify you're in the container:

```bash
# Check if you're in the container
whoami
pwd

# Should show:
# - User: root (or your container user)
# - Path: /workspaces/Advanced-Multi-Agent-Intelligence-System

# Check Node.js is available
node --version
npm --version

# Check Python is available
python3 --version

# Check if frontend dependencies are installed
cd frontend && test -d node_modules && echo "✅ Dependencies installed" || echo "❌ Run: npm install"
```

---

## 🚀 After Reconnecting - Quick Setup

### **1. Verify Environment**

```bash
# Check current directory
pwd
# Should be: /workspaces/Advanced-Multi-Agent-Intelligence-System

# List files
ls -la
```

### **2. Check Services Status**

```bash
# Check if Node.js is installed
node --version
npm --version

# Check if Python is installed
python3 --version

# Check if dependencies are installed
cd frontend && test -d node_modules && echo "✅ Frontend deps OK" || npm install
```

### **3. Start Development Servers**

#### **Backend (if needed):**
```bash
# From project root
python3 main.py
# Or use the auto-port script
python3 start_backend_auto_port.py
```

#### **Frontend:**
```bash
# From frontend directory
cd frontend
npm run dev
# Server will start on http://localhost:3000 (or 3001 if 3000 is busy)
```

---

## 🐛 Troubleshooting

### **Issue: "Command 'Dev Containers: Reopen in Container' not found"**

**Solution:**
1. Install the "Dev Containers" extension:
   - Press `Ctrl+Shift+X` to open Extensions
   - Search for "Dev Containers"
   - Install the extension by Microsoft

### **Issue: Container won't start**

**Solution:**
1. Check Docker is running:
   ```bash
   docker ps
   ```

2. Rebuild the container:
   - Press `Ctrl+Shift+P`
   - Type: `Dev Containers: Rebuild Container`
   - Wait for rebuild to complete

### **Issue: Can't find the container**

**Solution:**
1. List all containers:
   ```bash
   docker ps -a
   ```

2. Start the container manually:
   ```bash
   docker start <container-name>
   ```

3. Then attach using Method 4 above

### **Issue: Ports not accessible**

**Solution:**
1. Check port forwarding in VS Code/Cursor:
   - Look at the "PORTS" tab at the bottom
   - Ensure ports 3000, 8000, 8001, 8002 are forwarded

2. Manually forward ports:
   - Right-click on the PORTS tab
   - Select "Port Forwarding"
   - Add ports: 3000, 8000, 8001, 8002

---

## 📝 Quick Reference

| Action | Command/Shortcut |
|--------|------------------|
| Open Command Palette | `Ctrl+Shift+P` (Windows/Linux)<br>`Cmd+Shift+P` (Mac) |
| Reopen in Container | `Dev Containers: Reopen in Container` |
| Attach to Container | `Dev Containers: Attach to Running Container` |
| Rebuild Container | `Dev Containers: Rebuild Container` |
| Check Container Status | Bottom-left corner icon |

---

## ✅ Success Indicators

You're successfully connected when you see:

1. **Bottom-left corner shows:** `Dev Container: ...` or container name
2. **Terminal shows:** Container path (`/workspaces/...`)
3. **Extensions:** Container-specific extensions are active
4. **File system:** You can access project files

---

## 🔗 Additional Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Cursor Dev Containers Guide](https://cursor.sh/docs)

---

**Need Help?** Check the `.devcontainer/devcontainer.json` file for container configuration details.


