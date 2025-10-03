
# ========================================
# MIGRATION TO UNIVERSAL AI MANAGER
# ========================================
# Replace your old AI client initialization with this:

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.amas.services.universal_ai_manager import get_universal_ai_manager

# Initialize manager
ai_manager = get_universal_ai_manager()

# Generate AI response with automatic fallback
async def generate_response(prompt: str, system_prompt: str = None):
    """Generate AI response with full fallback support"""
    result = await ai_manager.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        strategy='intelligent',  # or 'priority', 'round_robin', 'fastest'
        max_tokens=4096,
        temperature=0.7
    )
    
    if result['success']:
        return result['content']
    else:
        raise Exception(f"AI generation failed: {result['error']}")

# Get statistics
stats = ai_manager.get_stats()
print(f"Success rate: {stats['success_rate']}")

# Get provider health
health = ai_manager.get_provider_health()
for provider_id, info in health.items():
    print(f"{info['name']}: {info['status']} ({info['success_rate']})")
