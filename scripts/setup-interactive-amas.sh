#!/bin/bash
# AMAS Interactive Setup Script - Next Generation
# Advanced Multi-Agent Intelligence System - Interactive Mode Setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ASCII Art Banner
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🚀 ADVANCED MULTI-AGENT INTELLIGENCE SYSTEM (AMAS) - INTERACTIVE MODE    ║
║                                                                              ║
║    🤖 7 Specialized AI Agents Ready for Command                             ║
║    🧠 9 Advanced AI Models Coordinated                                      ║
║    🔒 Enterprise-Grade Security Hardened                                     ║
║    ⚡ Next-Gen Interactive Command Interface                                  ║
║    🎯 Natural Language Processing Enabled                                    ║
║    📊 Real-Time Agent Coordination                                           ║
║    🔄 Intelligent Task Management                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}🚀 Setting up AMAS Interactive Mode - Next Generation...${NC}"
echo -e "${BLUE}======================================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_warning "This script should not be run as root for security reasons"
   read -p "Continue anyway? (y/N): " -n 1 -r
   echo
   if [[ ! $REPLY =~ ^[Yy]$ ]]; then
       exit 1
   fi
fi

# Check Python version
echo -e "${BLUE}🐍 Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )[0-9]+\.[0-9]+')
required_version="3.8"

if command -v python3 &> /dev/null; then
    # Simple version comparison using Python itself
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_status "Python $python_version detected"
    else
        print_error "Python $required_version or higher required (found $python_version)"
        exit 1
    fi
else
    print_error "Python 3 not found. Please install Python 3.8 or higher"
    exit 1
fi

# Check pip
echo -e "${BLUE}📦 Checking pip...${NC}"
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
else
    print_error "pip3 not found. Please install pip3"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}🔧 Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
echo -e "${BLUE}🔄 Activating virtual environment...${NC}"
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo -e "${BLUE}⬆️  Upgrading pip...${NC}"
pip install --upgrade pip
print_status "pip upgraded"

# Install core requirements
echo -e "${BLUE}📦 Installing core requirements...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Core requirements installed"
else
    print_warning "requirements.txt not found, installing basic requirements"
    pip install asyncio rich click prompt-toolkit questionary
fi

# Install interactive mode requirements
echo -e "${BLUE}📦 Installing interactive mode requirements...${NC}"
pip install rich>=13.0.0 click>=8.0.0 prompt-toolkit>=3.0.0 questionary>=1.10.0
pip install colorama>=0.4.4 tabulate>=0.9.0 progressbar2>=4.0.0
pip install python-dotenv>=0.19.0 pyyaml>=6.0
pip install psutil>=5.8.0  # For system monitoring

# Optional NLP libraries
echo -e "${BLUE}🧠 Installing optional NLP libraries...${NC}"
pip install spacy>=3.4.0 nltk>=3.7 || print_warning "NLP libraries installation failed (optional)"

# Create required directories
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p data/{cache,results,tasks,backups}
mkdir -p config
mkdir -p src/amas/interactive/{core,ai,agents,utils}
print_status "Directories created"

# Set up configuration files
echo -e "${BLUE}⚙️  Setting up configuration...${NC}"

# Main interactive configuration
cat > config/interactive_config.json << 'EOF'
{
  "interactive_mode": {
    "enabled": true,
    "max_concurrent_tasks": 5,
    "default_timeout": 300,
    "auto_save_results": true,
    "results_directory": "data/results"
  },
  "display": {
    "mode": "detailed",
    "use_colors": true,
    "show_progress": true,
    "detailed_logging": true,
    "refresh_rate": 0.1,
    "max_history": 50
  },
  "agents": {
    "code_analysis": {"enabled": true, "priority": 1, "max_tasks": 4},
    "security_expert": {"enabled": true, "priority": 1, "max_tasks": 3},
    "intelligence_gathering": {"enabled": true, "priority": 2, "max_tasks": 5},
    "performance_monitor": {"enabled": true, "priority": 3, "max_tasks": 3},
    "documentation_specialist": {"enabled": true, "priority": 3, "max_tasks": 2},
    "testing_coordinator": {"enabled": true, "priority": 3, "max_tasks": 3},
    "integration_manager": {"enabled": true, "priority": 2, "max_tasks": 2}
  },
  "nlp": {
    "model": "default",
    "confidence_threshold": 0.5,
    "max_entities": 10,
    "context_window": 5
  },
  "intent": {
    "patterns_enabled": true,
    "ml_enabled": false,
    "confidence_threshold": 0.6,
    "fallback_intent": "general_analysis"
  },
  "tasks": {
    "data_directory": "data/tasks",
    "auto_cleanup": true,
    "cleanup_interval_hours": 24,
    "max_task_history": 1000
  },
  "ui": {
    "theme": "default",
    "color_scheme": "default",
    "show_banner": true,
    "show_metrics": true,
    "show_agents": true,
    "show_timeline": true
  }
}
EOF

# User preferences
cat > config/user_preferences.json << 'EOF'
{
  "display_mode": "detailed",
  "color_scheme": "default",
  "auto_save": true,
  "notifications": true,
  "verbose_output": false,
  "default_priority": "normal",
  "preferred_agents": [],
  "custom_shortcuts": {},
  "theme": "default",
  "language": "en"
}
EOF

# System configuration
cat > config/system_config.json << 'EOF'
{
  "max_concurrent_tasks": 5,
  "task_timeout": 300,
  "auto_retry": true,
  "max_retries": 3,
  "log_level": "INFO",
  "data_retention_days": 30,
  "backup_enabled": true,
  "performance_monitoring": true,
  "security_mode": "standard"
}
EOF

print_status "Configuration files created"

# Set up environment variables
echo -e "${BLUE}🌍 Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# AMAS Interactive Configuration
AMAS_MODE=interactive
AMAS_LOG_LEVEL=INFO
AMAS_MAX_AGENTS=7
AMAS_AI_MODELS=9

# AI Provider Configuration (add your keys)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_claude_key_here
OPENROUTER_API_KEY=your_openrouter_key_here

# Security Configuration
AMAS_SECURITY_LEVEL=high
AMAS_ENCRYPTION_ENABLED=true

# Performance Configuration
AMAS_CACHE_ENABLED=true
AMAS_PARALLEL_TASKS=3

# Interactive Mode Configuration
AMAS_INTERACTIVE_MODE=true
AMAS_DISPLAY_MODE=detailed
AMAS_AUTO_SAVE=true
EOF
    print_warning "Please update .env file with your API keys"
else
    print_info ".env file already exists"
fi

# Make scripts executable
echo -e "${BLUE}🔧 Setting permissions...${NC}"
chmod +x src/amas/interactive/core/interactive_cli.py 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
print_status "Permissions set"

# Create quick start script
echo -e "${BLUE}🚀 Creating quick start script...${NC}"
cat > start-amas-interactive.sh << 'EOF'
#!/bin/bash
# Quick start script for AMAS Interactive Mode

echo "🚀 Starting AMAS Interactive Mode - Next Generation..."
cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if interactive module exists
if [ -f "src/amas/interactive/core/interactive_cli.py" ]; then
    echo "✅ Interactive module found"
    python3 src/amas/interactive/core/interactive_cli.py
else
    echo "❌ Interactive module not found. Please run setup script first."
    exit 1
fi
EOF

chmod +x start-amas-interactive.sh
print_status "Quick start script created"

# Create test script
echo -e "${BLUE}🧪 Creating test script...${NC}"
cat > test-interactive.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for AMAS Interactive Mode
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from amas.interactive.core.interactive_cli import AMASInteractiveCLI
    from amas.interactive.ai.nlp_engine import NLPEngine
    from amas.interactive.core.agent_coordinator import AgentCoordinator
    from amas.interactive.core.task_manager import TaskManager
    from amas.interactive.core.visual_interface import VisualInterface
    from amas.interactive.utils.config_manager import ConfigManager
    from amas.interactive.utils.logger import InteractiveLogger
    
    print("✅ All interactive modules imported successfully!")
    print("🎉 AMAS Interactive Mode is ready to use!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

chmod +x test-interactive.py
print_status "Test script created"

# Run test
echo -e "${BLUE}🧪 Running test...${NC}"
python3 test-interactive.py

# Create documentation
echo -e "${BLUE}📚 Creating documentation...${NC}"
mkdir -p docs

cat > docs/INTERACTIVE_QUICK_START.md << 'EOF'
# 🚀 AMAS Interactive Quick Start Guide - Next Generation

Welcome to the Next-Generation Interactive Command Interface for your Advanced Multi-Agent Intelligence System!

## 🎯 Quick Setup

### 1. Installation
```bash
# Run the setup script
chmod +x scripts/setup-interactive-amas.sh
./scripts/setup-interactive-amas.sh

# Start AMAS Interactive Mode
./start-amas-interactive.sh
```

### 2. First Commands
Once AMAS starts, try these commands:

```
🤖 AMAS> help # Show all available commands
🤖 AMAS> status # Check system status
🤖 AMAS> scan google.com # Security scan example
```

## 🗣️ Natural Language Commands

AMAS understands natural language! Just describe what you want:

### Security Operations
- `scan website.com for vulnerabilities`
- `audit the security of github.com/user/repo`
- `analyze security of my-domain.com`
- `check if example.com is secure`

### Intelligence Gathering
- `research TechCorp company`
- `investigate suspicious-domain.com`
- `gather intelligence on target-system`
- `analyze threat landscape for AI security`

### Code Analysis
- `analyze code in /path/to/repository`
- `review code quality of github.com/user/project`
- `check performance of my application`
- `test coverage analysis for project`

## 🤖 Your AI Agents

AMAS coordinates these specialized agents:

1. **🔍 Code Analysis Agent** - Code quality and structure
2. **🛡️ Security Expert Agent** - Cybersecurity and threats  
3. **🕵️ Intelligence Gathering Agent** - OSINT and research
4. **⚡ Performance Monitor Agent** - System optimization
5. **📝 Documentation Specialist** - Auto-documentation
6. **🧪 Testing Coordinator** - Quality assurance
7. **🔗 Integration Manager** - System coordination

## 📊 Real-time Features

### Progress Monitoring
- **Live Updates**: See agents working in real-time
- **Progress Bars**: Visual feedback on task completion
- **Agent Status**: Know which agents are active

### Results Display
- **Rich Formatting**: Beautiful tables and panels
- **Detailed Findings**: Comprehensive analysis results
- **Export Options**: Save results for later use

### Task Management
- **Task History**: Review all previous tasks
- **Concurrent Tasks**: Run multiple analyses simultaneously
- **Task Status**: Monitor active, completed, and failed tasks

## 🎨 Interface Features

### Visual Elements
- **🎯 Colored Output**: Easy-to-read console interface
- **📊 Tables**: Organized data presentation
- **🔄 Progress Bars**: Real-time progress updates
- **📋 Panels**: Structured result display

### Commands
- `help` - Show all available commands
- `status` - Display system status
- `history` - Show task history
- `exit` - Quit interactive mode

## 🔧 Configuration

### Environment Variables
Update `.env` file with your API keys:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### Agent Configuration
Customize agent behavior in `config/interactive_config.json`:
- Enable/disable specific agents
- Set agent priorities
- Configure capabilities

## 🎉 Example Session

```
🚀 Starting AMAS Interactive Mode...
✅ AMAS system initialized successfully!

╔══════════════════════════════════════════════════════════════╗
║ ║
║ 🚀 ADVANCED MULTI-AGENT INTELLIGENCE SYSTEM (AMAS) ║
║ ║
║ 🤖 7 Specialized Agents Ready ║
║ 🧠 9 AI Models Coordinated ║
║ 🔒 Enterprise Security Hardened ║
║ ⚡ Interactive Command Interface ║
║ ║
╚══════════════════════════════════════════════════════════════╝

🎯 Welcome to AMAS Interactive Mode!
Type 'help' for commands or describe what you want me to do.

🤖 AMAS> scan google.com for vulnerabilities

🧠 Understanding your request: 'scan google.com for vulnerabilities'
✅ Interpreted as: security_scan task
🚀 Task submitted successfully!

[Progress bar with spinning indicator]
⠋ Security Expert Agent working...

📋 Task Results: abc12345
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Attribute ┃ Value ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Task Type │ Security Scan │
│ Target │ google.com │
│ Status │ COMPLETED │
│ Agents Involved │ Security Expert, Code... │
│ Duration │ 3.24 seconds │
│ Security Score │ A+ (95/100) │
│ Vulnerabilities │ 2 Low, 0 Medium, 0 High │
│ SSL Rating │ A+ │
└─────────────────┴──────────────────────────────┘

🔍 Detailed Findings
🔒 Security Analysis for google.com:
✅ Strengths:
• Strong SSL/TLS configuration (TLS 1.3)
• Secure headers implemented
• No exposed sensitive information
...

🤖 AMAS> status

🔋 AMAS System Status
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component ┃ Status ┃ Details ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ 🤖 Multi-Agent System │ ✅ Active │ 7 agents ready │
│ 🧠 AI Models │ ✅ Operational│ 9 models available │
│ 🔒 Security Layer │ ✅ Hardened │ 0 vulnerabilities │
│ ⚡ Fallback System │ ✅ Ready │ 16 providers config'd │
│ 📊 Monitoring │ ✅ Active │ Real-time metrics │
└───────────────────────┴───────────────┴───────────────────────┘

🤖 AMAS> exit
👋 Goodbye! AMAS signing off.
```

## 🚀 Ready to Command Your AI Army!

Your Advanced Multi-Agent Intelligence System is now ready for interactive use!

**Start exploring the power of coordinated AI agents working together to solve complex tasks!**

For advanced configuration and customization, see the full documentation in `/docs/`.

Happy commanding! 🤖⚡✨
EOF

print_status "Documentation created"

# Final status
echo ""
echo -e "${PURPLE}======================================================${NC}"
echo -e "${GREEN}🎉 AMAS Interactive Setup Complete - Next Generation!${NC}"
echo -e "${PURPLE}======================================================${NC}"
echo ""
print_status "Installation successful!"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Update your API keys in .env file"
echo "2. Run: ./start-amas-interactive.sh"
echo "3. Start commanding your AI agents!"
echo ""
echo -e "${BLUE}Example commands:${NC}"
echo "• scan google.com for vulnerabilities"
echo "• analyze security of github.com/microsoft/vscode"
echo "• research latest AI security trends"
echo ""
echo -e "${CYAN}Quick test:${NC}"
echo "• python3 test-interactive.py"
echo ""
echo -e "${GREEN}Happy AI commanding! 🤖⚡✨${NC}"