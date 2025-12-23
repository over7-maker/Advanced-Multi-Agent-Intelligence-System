# AMAS Setup Guide - Complete Installation

## 🚀 **Quick Start (Recommended)**

### **Step 1: Install Docker Desktop**
1. Download Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop/
2. Run the installer as Administrator
3. Restart your computer when prompted
4. Launch Docker Desktop and complete the setup wizard
5. Verify installation: Open Command Prompt and run `docker --version`

### **Step 2: Install Prerequisites**
```powershell
# Run as Administrator
.\setup_windows_enhanced.ps1 --enable-internet --confirm-ingest
```

### **Step 3: Validate Installation**
```powershell
python validate_system.py
```

---

## 📋 **Detailed Setup Instructions**

### **Prerequisites**
- Windows 11 Pro (24H2) or Windows 10 Pro (22H2+)
- Administrator privileges
- Internet connection (for initial setup)
- 50GB+ free disk space
- 8GB+ RAM (32GB recommended)

### **1. Docker Desktop Installation**

#### **Download and Install**
1. Go to https://www.docker.com/products/docker-desktop/
2. Click "Download for Windows"
3. Run `Docker Desktop Installer.exe` as Administrator
4. Follow the installation wizard
5. **Important**: Enable WSL 2 integration when prompted
6. Restart your computer

#### **Verify Docker Installation**
```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Test Docker daemon
docker run hello-world
```

#### **Configure Docker Desktop**
1. Launch Docker Desktop
2. Go to Settings → Resources → Advanced
3. Set Memory to 8GB+ (recommended: 16GB)
4. Set CPUs to 4+ (recommended: 8+)
5. Enable "Use WSL 2 based engine"
6. Apply & Restart

### **2. Python Environment Setup**

#### **Install Python 3.11+**
1. Download from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Verify installation: `python --version`

#### **Create Virtual Environment**
```powershell
# Navigate to project directory
cd "C:\Users\Admin\Desktop\TASKS\STUDIES\Self_Hosted_AI_super_Agents\AMAS_Project\amas-unified"

# Create virtual environment
python -m venv amas-env

# Activate virtual environment
.\amas-env\Scripts\Activate

# Upgrade pip
python -m pip install --upgrade pip
```

### **3. Install Dependencies**

#### **Install Python Dependencies**
```powershell
# Make sure virtual environment is activated
pip install -r requirements.txt
```

#### **Install Node.js Dependencies (for Web Interface)**
```powershell
# Install Node.js 18+ from https://nodejs.org/
# Then install dependencies
cd web
npm install
cd ..
```

### **4. System Configuration**

#### **Run Setup Script**
```powershell
# Run as Administrator
.\setup_windows_enhanced.ps1 --enable-internet --confirm-ingest
```

#### **Fix Common Issues**
```powershell
python fix_common_issues.py
```

### **5. Validation and Testing**

#### **Run System Validation**
```powershell
python validate_system.py
```

#### **Run Comprehensive Tests**
```powershell
python run_comprehensive_tests.py
```

#### **Run Health Check**
```powershell
.\scripts\health_check_comprehensive.ps1 -Detailed
```

---

## 🔧 **Troubleshooting**

### **Docker Issues**

#### **Docker Not Found**
```powershell
# Check if Docker is in PATH
where docker

# If not found, add Docker to PATH or reinstall
# Restart Command Prompt after installation
```

#### **Docker Daemon Not Running**
```powershell
# Start Docker Desktop
# Or start Docker service
net start com.docker.service
```

#### **WSL 2 Issues**
```powershell
# Enable WSL 2
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer, then:
wsl --set-default-version 2
```

### **Python Issues**

#### **Virtual Environment Not Activating**
```powershell
# Check execution policy
Get-ExecutionPolicy

# If restricted, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **Package Installation Failures**
```powershell
# Update pip
python -m pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with verbose output
pip install -r requirements.txt -v
```

### **Permission Issues**

#### **File Access Denied**
```powershell
# Run Command Prompt as Administrator
# Or check folder permissions
icacls "C:\Users\Admin\Desktop\TASKS\STUDIES\Self_Hosted_AI_super_Agents\AMAS_Project\amas-unified"
```

---

## 🎯 **Verification Checklist**

### **Before Deployment**
- [ ] Docker Desktop installed and running
- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] System validation passes
- [ ] Health check passes
- [ ] Docker services can start

### **After Deployment**
- [ ] All Docker containers running
- [ ] Web interface accessible (http://localhost:3000)
- [ ] API responding (http://localhost:8000/health)
- [ ] LLM service working (http://localhost:11434/api/tags)
- [ ] Monitoring dashboards accessible

---

## 🆘 **Getting Help**

### **Common Commands**
```powershell
# Check system status
python validate_system.py

# Diagnose Docker issues
python diagnose_docker.py

# Fix common issues
python fix_common_issues.py

# Run health check
.\scripts\health_check_comprehensive.ps1

# View logs
docker-compose logs

# Restart services
docker-compose restart
```

### **Log Files**
- System logs: `logs/`
- Docker logs: `docker-compose logs [service-name]`
- Validation reports: `logs/validation_report_*.json`
- Test reports: `logs/test_report_*.json`

---

## 🎉 **Success!**

Once all validation checks pass, your AMAS system is ready for production use!

**Access Points:**
- Web Interface: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Monitoring: http://localhost:3001
- LLM Service: http://localhost:11434

**Next Steps:**
1. Explore the web interface
2. Run some test agent tasks
3. Configure monitoring dashboards
4. Set up automated backups
5. Review security settings
