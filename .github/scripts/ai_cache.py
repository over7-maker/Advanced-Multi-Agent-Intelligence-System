#!/usr/bin/env python3
"""
AI Response Cache
File-based caching for AI responses to reduce redundant API calls and save costs.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AICache:
    """File-based cache for AI responses"""
    
    cache_dir: str = ".github/cache/ai_responses"
    ttl_hours: int = 24
    
    def __post_init__(self):
        """Initialize cache directory"""
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
    
    def _key(self, task_type: str, prompt: str, system_message: str = "") -> str:
        """Generate SHA256 cache key from task parameters"""
        content = f"{task_type}:{system_message}:{prompt}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get(self, task_type: str, prompt: str, system_message: str = "") -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available and not expired"""
        cache_key = self._key(task_type, prompt, system_message)
        cache_file = Path(self.cache_dir) / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            
            # Check expiry
            cached_time = datetime.fromisoformat(cached['timestamp'])
            expiry = cached_time + timedelta(hours=self.ttl_hours)
            
            if datetime.now() > expiry:
                cache_file.unlink()  # Delete expired cache
                return None
            
            return cached['response']
        
        except Exception:
            # If cache file is corrupted, delete it
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def set(self, task_type: str, prompt: str, response: Dict[str, Any], 
            system_message: str = "") -> None:
        """Store new response in cache"""
        cache_key = self._key(task_type, prompt, system_message)
        cache_file = Path(self.cache_dir) / f"{cache_key}.json"
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'response': response
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception:
            # Silently fail if cache write fails
            pass
    
    def clear(self, task_type: Optional[str] = None) -> int:
        """Clear cache (all or by task type). Returns number of files deleted."""
        cache_path = Path(self.cache_dir)
        if not cache_path.exists():
            return 0
        
        deleted = 0
        for cache_file in cache_path.glob("*.json"):
            try:
                if task_type:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached = json.load(f)
                    if cached.get('task_type') == task_type:
                        cache_file.unlink()
                        deleted += 1
                else:
                    cache_file.unlink()
                    deleted += 1
            except Exception:
                # Delete corrupted files
                cache_file.unlink()
                deleted += 1
        
        return deleted
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_path = Path(self.cache_dir)
        if not cache_path.exists():
            return {'total_files': 0, 'total_size_mb': 0, 'expired_files': 0}
        
        total_files = 0
        total_size = 0
        expired_files = 0
        now = datetime.now()
        
        for cache_file in cache_path.glob("*.json"):
            total_files += 1
            total_size += cache_file.stat().st_size
            
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                cached_time = datetime.fromisoformat(cached['timestamp'])
                expiry = cached_time + timedelta(hours=self.ttl_hours)
                if now > expiry:
                    expired_files += 1
            except Exception:
                expired_files += 1
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'expired_files': expired_files,
            'valid_files': total_files - expired_files
        }