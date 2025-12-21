#!/usr/bin/env python3
"""
Bulletproof AI PR Analyzer - Orchestrated Version
Uses Zero-Failure AI Orchestrator for all AI calls
"""

import asyncio
import os
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_orchestrator import AIOrchestrator, TaskType


async def analyze_pr_with_orchestrator():
    """Analyze PR using orchestrator"""
    orchestrator = AIOrchestrator(cache_enabled=True)
    
    # Get PR context
    pr_number = os.getenv("PR_NUMBER", "")
    pr_title = os.getenv("PR_TITLE", "")
    pr_body = os.getenv("PR_BODY", "")
    
    # Build analysis prompt
    system_message = """You are an expert code reviewer and PR analyst. Provide comprehensive analysis including:
1. Code quality assessment
2. Security vulnerabilities
3. Performance implications
4. Best practices compliance
5. Specific recommendations with file names and line numbers"""
    
    user_prompt = f"""Analyze this Pull Request:

PR #{pr_number}
Title: {pr_title}
Description: {pr_body}

Provide detailed analysis with specific recommendations."""
    
    # Execute analysis using orchestrator
    result = await orchestrator.execute(
        task_type=TaskType.PR_ANALYSIS.value,
        system_message=system_message,
        user_prompt=user_prompt,
        max_tokens=4000,
        temperature=0.7
    )
    
    if result.get("success"):
        return {
            "success": True,
            "analysis": result.get("response", ""),
            "provider": result.get("provider", "unknown"),
            "cached": result.get("cached", False)
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Unknown error")
        }


async def main():
    """Main entry point"""
    result = await analyze_pr_with_orchestrator()
    
    if result.get("success"):
        print(result["analysis"])
        sys.exit(0)
    else:
        print(f"Analysis failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
