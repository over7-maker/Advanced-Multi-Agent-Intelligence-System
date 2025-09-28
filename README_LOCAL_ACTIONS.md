# 🤖 Local GitHub Actions Runner

Run your GitHub Actions workflows locally with a beautiful web interface that mimics the GitHub Actions experience!

## 🚀 Quick Start

### Option 1: One-Command Setup
```bash
python3 start_local_actions.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements_local.txt

# Start the runner
python3 local_github_actions.py
```

## 🌐 Web Interface

Once started, open your browser to:
- **URL**: http://127.0.0.1:5000
- **Auto-opens**: The browser will open automatically

## 📋 Features

### 🎯 Workflows Tab
- **View all workflows** from `.github/workflows/`
- **Run workflows** with a single click
- **Real-time status** updates
- **Workflow descriptions** and metadata

### ⚡ Jobs Tab
- **Running jobs** in real-time
- **Job history** with status tracking
- **Job details** and execution info
- **Quick access** to job logs

### 📊 Logs Tab
- **Live log streaming** for running jobs
- **Historical logs** for completed jobs
- **Color-coded output** for better readability
- **Auto-scroll** to latest logs

## 🔧 How It Works

### 1. Workflow Discovery
- Automatically scans `.github/workflows/` directory
- Loads all `.yml` workflow files
- Parses workflow metadata and steps

### 2. Job Execution
- Runs workflow steps in sequence
- Executes shell commands in your environment
- Captures output and errors
- Provides real-time feedback

### 3. Environment Simulation
- Sets up GitHub Actions environment variables
- Simulates GitHub Actions context
- Maintains workspace isolation

## 🛠️ Supported Workflow Features

### ✅ Fully Supported
- **Shell commands** (`run` steps)
- **Environment variables**
- **Working directory** management
- **Step dependencies**
- **Error handling**

### 🔄 Partially Supported
- **Action marketplace** (simulated)
- **Matrix strategies** (basic support)
- **Conditional steps** (basic support)

### ❌ Not Supported
- **Docker containers**
- **Service containers**
- **Artifact uploads**
- **Secret management**

## 📁 Project Structure

```
.
├── local_github_actions.py      # Main runner application
├── start_local_actions.py      # Quick start script
├── requirements_local.txt       # Python dependencies
├── templates/
│   └── index.html              # Web interface
├── .github/workflows/          # Your GitHub Actions workflows
└── README_LOCAL_ACTIONS.md     # This file
```

## 🎨 Web Interface Features

### GitHub-Style Design
- **Dark theme** matching GitHub's interface
- **Responsive layout** for all screen sizes
- **Tabbed navigation** for easy switching
- **Real-time updates** without page refresh

### Workflow Management
- **Visual workflow cards** with status indicators
- **One-click execution** of workflows
- **Progress tracking** for running jobs
- **Error reporting** with detailed logs

### Job Monitoring
- **Live job status** updates
- **Execution timeline** tracking
- **Log streaming** in real-time
- **Job history** with search

## 🔧 Configuration

### Environment Variables
The runner automatically sets these GitHub Actions environment variables:
- `GITHUB_WORKSPACE`: Current working directory
- `GITHUB_REPOSITORY`: `local/Advanced-Multi-Agent-Intelligence-System`
- `GITHUB_ACTIONS`: `true`
- `RUNNER_OS`: `Linux`
- `RUNNER_ARCH`: `X64`

### Custom Configuration
You can modify `local_github_actions.py` to:
- Change the server host/port
- Add custom environment variables
- Modify workflow execution behavior
- Customize the web interface

## 🚨 Troubleshooting

### Common Issues

#### 1. "Not in a git repository"
**Solution**: Run from your project root directory
```bash
cd /path/to/your/project
python3 start_local_actions.py
```

#### 2. "No .github/workflows directory found"
**Solution**: Create the directory and add workflow files
```bash
mkdir -p .github/workflows
# Add your .yml workflow files
```

#### 3. "Module not found" errors
**Solution**: Install dependencies
```bash
pip install -r requirements_local.txt
```

#### 4. Port already in use
**Solution**: Kill the process or use a different port
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or modify the port in local_github_actions.py
```

### Debug Mode
Enable debug mode for detailed logging:
```python
# In local_github_actions.py, change:
self.app.run(host=host, port=port, debug=True)
```

## 🎯 Use Cases

### 1. Local Development
- **Test workflows** before pushing to GitHub
- **Debug workflow issues** locally
- **Develop new workflows** with instant feedback

### 2. CI/CD Testing
- **Validate workflow changes** before deployment
- **Test workflow logic** without GitHub API limits
- **Develop and iterate** on complex workflows

### 3. Learning and Training
- **Understand GitHub Actions** without GitHub account
- **Practice workflow development** locally
- **Learn workflow syntax** with immediate feedback

## 🔮 Future Enhancements

### Planned Features
- **Docker support** for containerized workflows
- **Secret management** for sensitive data
- **Artifact handling** for file uploads/downloads
- **Matrix strategy** support for parallel jobs
- **Workflow visualization** with dependency graphs

### Community Contributions
- **Plugin system** for custom actions
- **Workflow templates** for common patterns
- **Integration** with popular IDEs
- **API endpoints** for external tools

## 📞 Support

### Getting Help
- **Issues**: Report bugs and feature requests
- **Documentation**: Check this README for common solutions
- **Community**: Join discussions and get help

### Contributing
- **Code**: Submit pull requests for improvements
- **Documentation**: Help improve this README
- **Testing**: Test with different workflow types

---

**🤖 Local GitHub Actions Runner**  
**Version**: 1.0.0  
**Status**: ✅ Ready for Development  
**Compatibility**: Python 3.7+ | GitHub Actions Workflows