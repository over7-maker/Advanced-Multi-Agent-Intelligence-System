#!/usr/bin/env python3
"""
Setup script to detect and configure local AI models for AMAS project.
This script:
1. Detects available Ollama models
2. Detects LocalAI instances (if available)
3. Updates .env file with detected models
4. Configures the AI router to use local models
"""

import os
import sys
import json
import httpx
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def detect_ollama_models() -> List[str]:
    """Detect available Ollama models"""
    models = []
    try:
        # Try API endpoint
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if response.status_code == 200:
            data = response.json()
            models = [model.get("name", "") for model in data.get("models", [])]
            print(f"Found {len(models)} Ollama models via API")
    except Exception as e:
        print(f"Could not fetch Ollama models via API: {e}")
    
    # Try CLI as fallback
    if not models:
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                print(f"Found {len(models)} Ollama models via CLI")
        except Exception as e:
            print(f"Could not fetch Ollama models via CLI: {e}")
    
    return models

def detect_localai() -> Optional[Dict]:
    """Detect LocalAI instance"""
    endpoints = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5000",
    ]
    
    for endpoint in endpoints:
        try:
            response = httpx.get(f"{endpoint}/v1/models", timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                models = [m.get("id", "") for m in data.get("data", [])]
                print(f"Found LocalAI at {endpoint} with {len(models)} models")
                return {
                    "endpoint": endpoint,
                    "models": models
                }
        except Exception:
            continue
    
    return None

def update_env_file(models: List[str], localai: Optional[Dict] = None):
    """Update .env file with detected models"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    # Read existing .env if it exists
    env_content = ""
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8")
    
    # Determine best model to use
    preferred_models = ["deepseek-r1:8b", "mistral:latest", "qwen3:4b", "llama3.2", "llama3.1:8b"]
    best_model = None
    for preferred in preferred_models:
        if preferred in models:
            best_model = preferred
            break
    
    if not best_model and models:
        best_model = models[0]
    
    # Update OLLAMA_MODEL
    if best_model:
        if "OLLAMA_MODEL=" in env_content:
            # Replace existing
            lines = env_content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("OLLAMA_MODEL="):
                    lines[i] = f"OLLAMA_MODEL={best_model}"
                    break
            env_content = "\n".join(lines)
        else:
            # Add new
            if env_content and not env_content.endswith("\n"):
                env_content += "\n"
            env_content += f"# Local AI Models Configuration\n"
            env_content += f"OLLAMA_MODEL={best_model}\n"
            env_content += f"OLLAMA_BASE_URL=http://localhost:11434/v1\n"
        
        print(f"Configured OLLAMA_MODEL={best_model}")
    
    # Add LocalAI configuration if available
    if localai:
        if "LOCALAI_BASE_URL=" not in env_content:
            if env_content and not env_content.endswith("\n"):
                env_content += "\n"
            env_content += f"LOCALAI_BASE_URL={localai['endpoint']}\n"
            print(f"Configured LocalAI at {localai['endpoint']}")
    
    # Write updated .env
    if env_file.exists():
        backup_file = project_root / ".env.backup"
        if not backup_file.exists():
            backup_file.write_text(env_content, encoding="utf-8")
            print(f"Created backup at .env.backup")
    
    env_file.write_text(env_content, encoding="utf-8")
    print(f"Updated .env file")

def create_models_config(models: List[str], localai: Optional[Dict] = None):
    """Create a models configuration file"""
    config = {
        "ollama": {
            "available": True,
            "base_url": "http://localhost:11434/v1",
            "models": models,
            "preferred_model": models[0] if models else None
        }
    }
    
    if localai:
        config["localai"] = {
            "available": True,
            "base_url": localai["endpoint"],
            "models": localai["models"]
        }
    
    config_file = project_root / "local_ai_models.json"
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Created models config at {config_file}")
    
    return config

def main():
    """Main function"""
    print("Detecting local AI models...\n")
    
    # Detect Ollama models
    ollama_models = detect_ollama_models()
    if ollama_models:
        print(f"Ollama Models: {', '.join(ollama_models)}\n")
    else:
        print("No Ollama models found. Install models with: ollama pull <model-name>\n")
    
    # Detect LocalAI
    localai = detect_localai()
    if localai:
        print(f"LocalAI Models: {', '.join(localai['models'])}\n")
    
    # Update .env file
    if ollama_models or localai:
        update_env_file(ollama_models, localai)
        create_models_config(ollama_models, localai)
        
        print("\nLocal AI models configured successfully!")
        print("\nSummary:")
        if ollama_models:
            print(f"   - Ollama: {len(ollama_models)} models available")
            print(f"     Models: {', '.join(ollama_models)}")
        if localai:
            print(f"   - LocalAI: {len(localai['models'])} models available")
            print(f"     Endpoint: {localai['endpoint']}")
        print("\nThe system will now use these local models as fallback providers.")
    else:
        print("\nNo local AI models detected.")
        print("   Install Ollama models with: ollama pull llama3.2")

if __name__ == "__main__":
    main()

