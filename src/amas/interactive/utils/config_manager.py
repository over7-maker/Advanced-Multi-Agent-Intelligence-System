"""
AMAS Configuration Manager - Advanced Configuration System
Advanced Multi-Agent Intelligence System - Interactive Mode

This module provides comprehensive configuration management for the AMAS
interactive system including user preferences, system settings, and
dynamic configuration updates.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Rich for enhanced output
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

@dataclass
class UserPreferences:
    """User preferences data structure"""
    display_mode: str = "detailed"
    color_scheme: str = "default"
    auto_save: bool = True
    notifications: bool = True
    verbose_output: bool = False
    default_priority: str = "normal"
    preferred_agents: List[str] = None
    custom_shortcuts: Dict[str, str] = None
    theme: str = "default"
    language: str = "en"
    
    def __post_init__(self):
        if self.preferred_agents is None:
            self.preferred_agents = []
        if self.custom_shortcuts is None:
            self.custom_shortcuts = {}

@dataclass
class SystemConfig:
    """System configuration data structure"""
    max_concurrent_tasks: int = 5
    task_timeout: int = 300
    auto_retry: bool = True
    max_retries: int = 3
    log_level: str = "INFO"
    data_retention_days: int = 30
    backup_enabled: bool = True
    performance_monitoring: bool = True
    security_mode: str = "standard"  # standard, strict, paranoid

class ConfigManager:
    """Advanced Configuration Management System"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        
        # Configuration paths
        self.config_dir = Path(config_path) if config_path else Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "interactive_config.json"
        self.user_prefs_file = self.config_dir / "user_preferences.json"
        self.system_config_file = self.config_dir / "system_config.json"
        self.session_file = self.config_dir / "session_data.json"
        
        # Configuration data
        self.config = {}
        self.user_preferences = UserPreferences()
        self.system_config = SystemConfig()
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load all configuration files"""
        try:
            # Load main configuration
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self._get_default_config()
                self._save_config()
            
            # Load user preferences
            if self.user_prefs_file.exists():
                with open(self.user_prefs_file, 'r') as f:
                    prefs_data = json.load(f)
                    self.user_preferences = UserPreferences(**prefs_data)
            else:
                self._save_user_preferences()
            
            # Load system configuration
            if self.system_config_file.exists():
                with open(self.system_config_file, 'r') as f:
                    sys_data = json.load(f)
                    self.system_config = SystemConfig(**sys_data)
            else:
                self._save_system_config()
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "interactive_mode": {
                "enabled": True,
                "max_concurrent_tasks": 5,
                "default_timeout": 300,
                "auto_save_results": True,
                "results_directory": "data/results"
            },
            "display": {
                "mode": "detailed",
                "use_colors": True,
                "show_progress": True,
                "detailed_logging": True,
                "refresh_rate": 0.1,
                "max_history": 50
            },
            "agents": {
                "code_analysis": {"enabled": True, "priority": 1, "max_tasks": 4},
                "security_expert": {"enabled": True, "priority": 1, "max_tasks": 3},
                "intelligence_gathering": {"enabled": True, "priority": 2, "max_tasks": 5},
                "performance_monitor": {"enabled": True, "priority": 3, "max_tasks": 3},
                "documentation_specialist": {"enabled": True, "priority": 3, "max_tasks": 2},
                "testing_coordinator": {"enabled": True, "priority": 3, "max_tasks": 3},
                "integration_manager": {"enabled": True, "priority": 2, "max_tasks": 2}
            },
            "nlp": {
                "model": "default",
                "confidence_threshold": 0.5,
                "max_entities": 10,
                "context_window": 5
            },
            "intent": {
                "patterns_enabled": True,
                "ml_enabled": False,
                "confidence_threshold": 0.6,
                "fallback_intent": "general_analysis"
            },
            "tasks": {
                "data_directory": "data/tasks",
                "auto_cleanup": True,
                "cleanup_interval_hours": 24,
                "max_task_history": 1000
            },
            "ui": {
                "theme": "default",
                "color_scheme": "default",
                "show_banner": True,
                "show_metrics": True,
                "show_agents": True,
                "show_timeline": True
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load main configuration"""
        return self.config.copy()
    
    def save_config(self, new_config: Dict[str, Any]):
        """Save main configuration"""
        self.config.update(new_config)
        self._save_config()
    
    def _save_config(self):
        """Save main configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def load_user_preferences(self) -> UserPreferences:
        """Load user preferences"""
        return self.user_preferences
    
    def save_user_preferences(self, preferences: Optional[UserPreferences] = None):
        """Save user preferences"""
        if preferences:
            self.user_preferences = preferences
        self._save_user_preferences()
    
    def _save_user_preferences(self):
        """Save user preferences to file"""
        try:
            prefs_data = asdict(self.user_preferences)
            with open(self.user_prefs_file, 'w') as f:
                json.dump(prefs_data, f, indent=2)
            self.logger.info("User preferences saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save user preferences: {e}")
    
    def load_system_config(self) -> SystemConfig:
        """Load system configuration"""
        return self.system_config
    
    def save_system_config(self, config: Optional[SystemConfig] = None):
        """Save system configuration"""
        if config:
            self.system_config = config
        self._save_system_config()
    
    def _save_system_config(self):
        """Save system configuration to file"""
        try:
            config_data = asdict(self.system_config)
            with open(self.system_config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            self.logger.info("System configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save system configuration: {e}")
    
    def save_session_data(self, session_data: Dict[str, Any]):
        """Save session data"""
        try:
            session_data["saved_at"] = datetime.now().isoformat()
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            self.logger.info("Session data saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")
    
    def load_session_data(self) -> Dict[str, Any]:
        """Load session data"""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load session data: {e}")
            return {}
    
    def get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get configuration for specific agent"""
        return self.config.get("agents", {}).get(agent_id, {})
    
    def update_agent_config(self, agent_id: str, updates: Dict[str, Any]):
        """Update configuration for specific agent"""
        if "agents" not in self.config:
            self.config["agents"] = {}
        
        if agent_id not in self.config["agents"]:
            self.config["agents"][agent_id] = {}
        
        self.config["agents"][agent_id].update(updates)
        self._save_config()
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get display configuration"""
        return self.config.get("display", {})
    
    def update_display_config(self, updates: Dict[str, Any]):
        """Update display configuration"""
        if "display" not in self.config:
            self.config["display"] = {}
        
        self.config["display"].update(updates)
        self._save_config()
    
    def get_nlp_config(self) -> Dict[str, Any]:
        """Get NLP configuration"""
        return self.config.get("nlp", {})
    
    def update_nlp_config(self, updates: Dict[str, Any]):
        """Update NLP configuration"""
        if "nlp" not in self.config:
            self.config["nlp"] = {}
        
        self.config["nlp"].update(updates)
        self._save_config()
    
    def get_intent_config(self) -> Dict[str, Any]:
        """Get intent classification configuration"""
        return self.config.get("intent", {})
    
    def update_intent_config(self, updates: Dict[str, Any]):
        """Update intent classification configuration"""
        if "intent" not in self.config:
            self.config["intent"] = {}
        
        self.config["intent"].update(updates)
        self._save_config()
    
    def get_tasks_config(self) -> Dict[str, Any]:
        """Get task management configuration"""
        return self.config.get("tasks", {})
    
    def update_tasks_config(self, updates: Dict[str, Any]):
        """Update task management configuration"""
        if "tasks" not in self.config:
            self.config["tasks"] = {}
        
        self.config["tasks"].update(updates)
        self._save_config()
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI configuration"""
        return self.config.get("ui", {})
    
    def update_ui_config(self, updates: Dict[str, Any]):
        """Update UI configuration"""
        if "ui" not in self.config:
            self.config["ui"] = {}
        
        self.config["ui"].update(updates)
        self._save_config()
    
    def reset_to_defaults(self):
        """Reset all configurations to defaults"""
        self.config = self._get_default_config()
        self.user_preferences = UserPreferences()
        self.system_config = SystemConfig()
        
        self._save_config()
        self._save_user_preferences()
        self._save_system_config()
        
        self.console.print("✅ All configurations reset to defaults", style="green")
    
    def export_config(self, file_path: str):
        """Export all configurations to file"""
        try:
            export_data = {
                "config": self.config,
                "user_preferences": asdict(self.user_preferences),
                "system_config": asdict(self.system_config),
                "export_timestamp": datetime.now().isoformat()
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.console.print(f"✅ Configuration exported to {file_path}", style="green")
            
        except Exception as e:
            self.console.print(f"❌ Failed to export configuration: {e}", style="red")
    
    def import_config(self, file_path: str):
        """Import configuration from file"""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            if "config" in import_data:
                self.config = import_data["config"]
                self._save_config()
            
            if "user_preferences" in import_data:
                self.user_preferences = UserPreferences(**import_data["user_preferences"])
                self._save_user_preferences()
            
            if "system_config" in import_data:
                self.system_config = SystemConfig(**import_data["system_config"])
                self._save_system_config()
            
            self.console.print(f"✅ Configuration imported from {file_path}", style="green")
            
        except Exception as e:
            self.console.print(f"❌ Failed to import configuration: {e}", style="red")
    
    def display_config_summary(self):
        """Display configuration summary"""
        # Main config table
        config_table = Table(title="⚙️ Configuration Summary")
        config_table.add_column("Category", style="cyan", width=20)
        config_table.add_column("Settings", style="green")
        
        # Interactive mode
        interactive = self.config.get("interactive_mode", {})
        config_table.add_row(
            "Interactive Mode",
            f"Enabled: {interactive.get('enabled', True)}, "
            f"Max Tasks: {interactive.get('max_concurrent_tasks', 5)}"
        )
        
        # Display settings
        display = self.config.get("display", {})
        config_table.add_row(
            "Display",
            f"Mode: {display.get('mode', 'detailed')}, "
            f"Colors: {display.get('use_colors', True)}"
        )
        
        # Agents
        agents = self.config.get("agents", {})
        enabled_agents = [aid for aid, config in agents.items() if config.get("enabled", True)]
        config_table.add_row(
            "Agents",
            f"Enabled: {len(enabled_agents)}/{len(agents)} agents"
        )
        
        # User preferences
        config_table.add_row(
            "User Preferences",
            f"Mode: {self.user_preferences.display_mode}, "
            f"Auto-save: {self.user_preferences.auto_save}"
        )
        
        # System config
        config_table.add_row(
            "System Config",
            f"Max Tasks: {self.system_config.max_concurrent_tasks}, "
            f"Timeout: {self.system_config.task_timeout}s"
        )
        
        self.console.print(config_table)
    
    def display_agent_configs(self):
        """Display agent configurations"""
        agents = self.config.get("agents", {})
        if not agents:
            self.console.print("No agent configurations found", style="yellow")
            return
        
        agent_table = Table(title="🤖 Agent Configurations")
        agent_table.add_column("Agent", style="cyan", width=20)
        agent_table.add_column("Enabled", style="green", width=10)
        agent_table.add_column("Priority", style="yellow", width=10)
        agent_table.add_column("Max Tasks", style="blue", width=10)
        agent_table.add_column("Status", style="magenta")
        
        for agent_id, config in agents.items():
            enabled = "✅" if config.get("enabled", True) else "❌"
            priority = config.get("priority", 1)
            max_tasks = config.get("max_tasks", 1)
            status = "Active" if config.get("enabled", True) else "Disabled"
            
            agent_table.add_row(
                agent_id.replace("_", " ").title(),
                enabled,
                str(priority),
                str(max_tasks),
                status
            )
        
        self.console.print(agent_table)
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return any issues"""
        issues = []
        
        # Check required sections
        required_sections = ["interactive_mode", "display", "agents", "nlp", "intent", "tasks", "ui"]
        for section in required_sections:
            if section not in self.config:
                issues.append(f"Missing required configuration section: {section}")
        
        # Check agent configurations
        agents = self.config.get("agents", {})
        for agent_id, config in agents.items():
            if not isinstance(config.get("enabled"), bool):
                issues.append(f"Agent {agent_id}: 'enabled' must be boolean")
            if not isinstance(config.get("priority"), int) or config.get("priority", 0) < 1:
                issues.append(f"Agent {agent_id}: 'priority' must be positive integer")
            if not isinstance(config.get("max_tasks"), int) or config.get("max_tasks", 0) < 1:
                issues.append(f"Agent {agent_id}: 'max_tasks' must be positive integer")
        
        # Check display configuration
        display = self.config.get("display", {})
        valid_modes = ["detailed", "compact", "minimal", "full"]
        if display.get("mode") not in valid_modes:
            issues.append(f"Display mode must be one of: {', '.join(valid_modes)}")
        
        # Check NLP configuration
        nlp = self.config.get("nlp", {})
        if not isinstance(nlp.get("confidence_threshold"), (int, float)) or not 0 <= nlp.get("confidence_threshold", 0) <= 1:
            issues.append("NLP confidence_threshold must be between 0 and 1")
        
        return issues
    
    def fix_config_issues(self, issues: List[str]):
        """Attempt to fix common configuration issues"""
        fixed = 0
        
        for issue in issues:
            if "Agent" in issue and "enabled" in issue:
                # Fix agent enabled field
                agent_id = issue.split(":")[0].split()[-1]
                if agent_id in self.config.get("agents", {}):
                    self.config["agents"][agent_id]["enabled"] = True
                    fixed += 1
            
            elif "Agent" in issue and "priority" in issue:
                # Fix agent priority field
                agent_id = issue.split(":")[0].split()[-1]
                if agent_id in self.config.get("agents", {}):
                    self.config["agents"][agent_id]["priority"] = 1
                    fixed += 1
            
            elif "Agent" in issue and "max_tasks" in issue:
                # Fix agent max_tasks field
                agent_id = issue.split(":")[0].split()[-1]
                if agent_id in self.config.get("agents", {}):
                    self.config["agents"][agent_id]["max_tasks"] = 1
                    fixed += 1
            
            elif "Display mode" in issue:
                # Fix display mode
                self.config.setdefault("display", {})["mode"] = "detailed"
                fixed += 1
            
            elif "confidence_threshold" in issue:
                # Fix NLP confidence threshold
                self.config.setdefault("nlp", {})["confidence_threshold"] = 0.5
                fixed += 1
        
        if fixed > 0:
            self._save_config()
            self.console.print(f"✅ Fixed {fixed} configuration issues", style="green")
        
        return fixed