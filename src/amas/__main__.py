#!/usr/bin/env python3
"""
AMAS Main Entry Point
Advanced Multi-Agent Intelligence System
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from amas.intelligence.intelligence_manager import intelligence_manager
from amas.providers.manager import provider_manager, validate_environment

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/amas.log", mode="a"),
        ],
    )

def print_banner():
    """Print AMAS banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🚀 AMAS - Advanced Multi-Agent Intelligence System 🚀     ║
    ║                                                              ║
    ║    🤖 7 Specialized AI Agents                               ║
    ║    🧠 Collective Intelligence & Learning                     ║
    ║    🎭 Adaptive Personalities                                ║
    ║    🔮 Predictive Intelligence                               ║
    ║    📊 Real-time Monitoring & Analytics                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_provider_status():
    """Print AI provider status"""
    print("\n🔍 AI Provider Status:")
    print("=" * 50)

    try:
        status = provider_manager.get_provider_status()
        enabled_count = 0

        for name, info in status.items():
            if info["available"]:
                icon = "✅"
                status_text = "ENABLED"
                enabled_count += 1
            elif info["status"] == "missing_key":
                icon = "✖️"
                status_text = "MISSING KEY"
            else:
                icon = "❌"
                status_text = info["status"].upper()

            print(f"  {icon} {name:15} {status_text:12} (Priority: {info['priority']})")

        print(f"\n📊 Summary: {enabled_count} providers enabled")

        if enabled_count < 2:
            print("⚠️  Warning: Consider adding more providers for better redundancy")
        elif enabled_count >= 5:
            print("🎉 Excellent! You have great provider redundancy")

    except Exception as e:
        print(f"❌ Error checking provider status: {e}")

async def main():
    """Main AMAS function"""
    print_banner()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Validate environment
        print("🔍 Validating environment...")
        validation = validate_environment()

        if not validation["valid"]:
            print("❌ Environment validation failed!")
            print("Missing required providers:", validation["missing_required"])
            print("\n🚀 Quick Start:")
            print("1. Copy .env.example to .env")
            print("2. Add at least 2-3 API keys")
            print("3. Run: python scripts/validate_env.py")
            return 1

        print("✅ Environment validation passed!")

        # Show provider status
        print_provider_status()

        # Start intelligence systems
        print("\n🧠 Starting intelligence systems...")
        await intelligence_manager.start_intelligence_systems()
        print("✅ Intelligence systems started")

        # Show system status
        print("\n📊 System Status:")
        print("=" * 30)
        print("✅ Multi-Agent System: Ready")
        print("✅ Provider Management: Active")
        print("✅ Collective Intelligence: Learning")
        print("✅ Adaptive Personalities: Adapting")
        print("✅ Predictive Intelligence: Forecasting")
        print("✅ Performance Monitoring: Active")

        print("\n🎯 AMAS is ready for action!")
        print("💡 Use the React dashboard at http://localhost:3000")
        print("📊 Monitor performance with: python monitor-intelligence.py")

        # Keep the system running
        print("\n🔄 System running... Press Ctrl+C to stop")
        try:
            while True:
                await asyncio.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Shutting down AMAS...")
            return 0

    except Exception as e:
        logger.error(f"❌ AMAS startup failed: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Run AMAS
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 AMAS stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
