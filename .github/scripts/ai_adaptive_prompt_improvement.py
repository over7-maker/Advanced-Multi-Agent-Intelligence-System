from standalone_universal_ai_manager import get_api_key
#!/usr/bin/env python3
"""
AI Adaptive Prompt Improvement Script
Automated prompt analysis and improvement using multiple AI models
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI


class AIAdaptivePromptImprovement:
    def __init__(self):
        self.deepseek_key = get_api_key("DEEPSEEK_API_KEY")
        self.claude_key = get_api_key("CLAUDE_API_KEY")
        self.gpt4_key = os.environ.get("GPT4_API_KEY")
        self.glm_key = get_api_key("GLM_API_KEY")
        self.grok_key = get_api_key("GROK_API_KEY")
        self.kimi_key = get_api_key("KIMI_API_KEY")
        self.qwen_key = get_api_key("QWEN_API_KEY")
        self.gemini_key = get_api_key("GEMINI_API_KEY")
        self.gptoss_key = get_api_key("GPTOSS_API_KEY")
        self.repo_name = os.environ.get("REPO_NAME")
        self.issue_number = os.environ.get("ISSUE_NUMBER")

        # Initialize AI clients with intelligent fallback priority
        self.agents = []

        # Priority order: DeepSeek (most reliable), GLM, Grok, Kimi, Qwen, GPTOSS
        if self.deepseek_key:
            try:
                self.agents.append(
                    {
                        "name": "DeepSeek",
                        "client": OpenAI(
                            base_url="https://api.deepseek.com/v1",
                            api_key=self.deepseek_key,
                        ),
                        "model": "deepseek-chat",
                        "role": "Primary Prompt Analyst",
                        "priority": 1,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize DeepSeek agent: {e}")

        if self.glm_key:
            try:
                self.agents.append(
                    {
                        "name": "GLM",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.glm_key,
                        ),
                        "model": "z-ai/glm-4.5-air:free",
                        "role": "Prompt Optimization Specialist",
                        "priority": 2,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GLM agent: {e}")

        if self.grok_key:
            try:
                self.agents.append(
                    {
                        "name": "Grok",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.grok_key,
                        ),
                        "model": "x-ai/grok-4-fast:free",
                        "role": "Strategic Prompt Advisor",
                        "priority": 3,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Grok agent: {e}")

        if self.kimi_key:
            try:
                self.agents.append(
                    {
                        "name": "Kimi",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.kimi_key,
                        ),
                        "model": "moonshot/moonshot-v1-8k:free",
                        "role": "Technical Prompt Specialist",
                        "priority": 4,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Kimi agent: {e}")

        if self.qwen_key:
            try:
                self.agents.append(
                    {
                        "name": "Qwen",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.qwen_key,
                        ),
                        "model": "qwen/qwen-2.5-7b-instruct:free",
                        "role": "Prompt Research Specialist",
                        "priority": 5,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize Qwen agent: {e}")

        if self.gptoss_key:
            try:
                self.agents.append(
                    {
                        "name": "GPTOSS",
                        "client": OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=self.gptoss_key,
                        ),
                        "model": "openai/gpt-3.5-turbo:free",
                        "role": "Prompt Validation Specialist",
                        "priority": 6,
                    }
                )
            except Exception as e:
                print(f"Failed to initialize GPTOSS agent: {e}")

        # Sort by priority
        self.agents.sort(key=lambda x: x["priority"])

        if not self.agents:
            print("⚠️ No AI agents available - cannot perform prompt analysis")
            return

        print(f"🧠 Initialized {len(self.agents)} AI agents for prompt improvement:")
        for agent in self.agents:
            print(f"  - {agent['name']}: {agent['role']}")

    async def call_agent(
        self, agent: Dict[str, Any], prompt: str, context: str = ""
    ) -> Optional[str]:
        """Call a specific AI agent with error handling"""
        try:
            print(f"🤖 {agent['name']} ({agent['role']}) is working...")

            full_prompt = f"{prompt}\n\nContext: {context}" if context else prompt

            extra_headers = {}
            if "openrouter.ai" in str(agent["client"].base_url):
                extra_headers = {
                    "HTTP-Referer": f"https://github.com/{self.repo_name}",
                    "X-Title": "AMAS Adaptive Prompt Improvement",
                }

            response = agent["client"].chat.completions.create(
                extra_headers=extra_headers if extra_headers else None,
                model=agent["model"],
                messages=[
                    {
                        "role": "system",
                        "content": f"You are {agent['role']} for the AMAS Intelligence System. {agent.get('description', '')}",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            result = response.choices[0].message.content
            print(f"✅ {agent['name']} completed prompt analysis")
            return result

        except Exception as e:
            print(f"❌ {agent['name']} failed: {e}")
            return None

    def collect_prompts_from_codebase(self) -> List[Dict[str, Any]]:
        """Collect all prompts from the codebase"""
        prompts = []

        # Define directories to search for prompts
        search_dirs = [".github/scripts", ".github/workflows"]

        for search_dir in search_dirs:
            if os.path.exists(search_dir):
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    content = f.read()

                                # Look for prompt patterns
                                prompt_patterns = self._extract_prompts_from_content(
                                    content, file_path
                                )
                                prompts.extend(prompt_patterns)
                            except Exception as e:
                                print(f"Error reading {file_path}: {e}")

        return prompts

    def _extract_prompts_from_content(
        self, content: str, file_path: str
    ) -> List[Dict[str, Any]]:
        """Extract prompts from file content"""
        prompts = []

        # Look for prompt patterns in the code
        prompt_patterns = [
            r'prompt\s*=\s*["\'](.*?)["\']',
            r'full_prompt\s*=\s*f["\'](.*?)["\']',
            r'messages\s*=\s*\[.*?{"role":\s*"user",\s*"content":\s*["\'](.*?)["\']',
            r"You are.*?for the AMAS Intelligence System",
            r"Analyze.*?and provide:",
            r"Provide.*?including:",
            r"Generate.*?report",
        ]

        for pattern in prompt_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                prompt_text = match.group(1) if match.groups() else match.group(0)
                prompts.append(
                    {
                        "file": file_path,
                        "prompt": prompt_text,
                        "line": content[: match.start()].count("\n") + 1,
                        "type": (
                            "system_prompt"
                            if "You are" in prompt_text
                            else "user_prompt"
                        ),
                    }
                )

        return prompts

    async def analyze_prompt_effectiveness(
        self, prompts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze prompt effectiveness using multiple agents"""
        if not self.agents:
            return {"error": "No agents available"}

        print("🧠 Starting Multi-Agent Prompt Analysis...")

        # Step 1: Prompt Analysis (DeepSeek or first available agent)
        primary_agent = self.agents[0]
        analysis_prompt = f"""
        Analyze these AI prompts for effectiveness and provide:
        - Prompt clarity and specificity assessment
        - Context and instruction quality
        - Potential improvements and optimizations
        - Consistency across different prompts
        - Best practices implementation
        - Performance optimization suggestions

        Prompts to analyze:
        {json.dumps(prompts, indent=2)}
        """

        prompt_analysis = await self.call_agent(primary_agent, analysis_prompt)
        if not prompt_analysis:
            return {"error": "Prompt analysis failed"}

        # Step 2: Optimization Recommendations (GLM or second agent)
        optimization_agent = self.agents[1] if len(self.agents) > 1 else self.agents[0]
        optimization_prompt = f"""
        Provide specific optimization recommendations including:
        - Prompt structure improvements
        - Language and tone enhancements
        - Context addition suggestions
        - Performance optimization techniques
        - Version control recommendations
        - A/B testing suggestions

        Analysis Results:
        {prompt_analysis}
        """

        optimization_recommendations = await self.call_agent(
            optimization_agent, optimization_prompt, prompt_analysis
        )
        if not optimization_recommendations:
            optimization_recommendations = (
                "Optimization recommendations failed - using analysis only"
            )

        # Step 3: Strategic Improvements (Grok or third agent)
        strategy_agent = self.agents[2] if len(self.agents) > 2 else self.agents[0]
        strategy_prompt = f"""
        Provide strategic prompt improvements including:
        - Long-term prompt evolution strategy
        - Cross-workflow prompt consistency
        - Advanced prompt engineering techniques
        - Performance monitoring and metrics
        - Prompt versioning and rollback strategies
        - Integration with other AI workflows

        Optimization Recommendations:
        {optimization_recommendations}
        """

        strategic_improvements = await self.call_agent(
            strategy_agent, strategy_prompt, optimization_recommendations
        )
        if not strategic_improvements:
            strategic_improvements = (
                "Strategic improvements failed - review optimization recommendations"
            )

        # Step 4: Technical Implementation (Kimi or fourth agent)
        technical_agent = self.agents[3] if len(self.agents) > 3 else self.agents[0]
        technical_prompt = f"""
        Provide technical implementation details including:
        - Code-level prompt improvements
        - Integration with existing workflows
        - Performance monitoring implementation
        - Error handling and fallback strategies
        - Testing and validation procedures
        - Documentation and maintenance

        Strategic Improvements:
        {strategic_improvements}
        """

        technical_implementation = await self.call_agent(
            technical_agent, technical_prompt, strategic_improvements
        )
        if not technical_implementation:
            technical_implementation = (
                "Technical implementation failed - review strategic improvements"
            )

        return {
            "prompts_analyzed": len(prompts),
            "prompt_analysis": prompt_analysis,
            "optimization_recommendations": optimization_recommendations,
            "strategic_improvements": strategic_improvements,
            "technical_implementation": technical_implementation,
            "agents_used": [agent["name"] for agent in self.agents],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

    def generate_prompt_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive prompt improvement report"""
        if "error" in results:
            return f"# Prompt Analysis Failed\n\nError: {results['error']}"

        report = f"""# 🧠 AMAS Adaptive Prompt Improvement Report

**Generated:** {results['timestamp']}
**Agents Used:** {', '.join(results['agents_used'])}
**Prompts Analyzed:** {results['prompts_analyzed']}

---

## 📊 Executive Summary

This report presents comprehensive prompt analysis and improvement recommendations conducted by multiple AI agents working in coordination to optimize the effectiveness of AI prompts across the AMAS system.

---

## 🔍 Step 1: Prompt Analysis

**Agent:** {results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['prompt_analysis']}

---

## 🎯 Step 2: Optimization Recommendations

**Agent:** {results['agents_used'][1] if len(results['agents_used']) > 1 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['optimization_recommendations']}

---

## 🏛️ Step 3: Strategic Improvements

**Agent:** {results['agents_used'][2] if len(results['agents_used']) > 2 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['strategic_improvements']}

---

## 🔧 Step 4: Technical Implementation

**Agent:** {results['agents_used'][3] if len(results['agents_used']) > 3 else results['agents_used'][0] if results['agents_used'] else 'Unknown'}

{results['technical_implementation']}

---

## 📈 Key Prompt Insights

- **Prompt Quality:** Assessed by multi-agent analysis
- **Optimization Opportunities:** Identified through coordinated analysis
- **Strategic Recommendations:** Prioritized based on effectiveness
- **Technical Implementation:** Areas requiring immediate attention

---

## 🔄 Recommended Actions

1. **Immediate Actions:** Implement high-priority prompt improvements
2. **Short-term:** Enhance prompt clarity and specificity
3. **Long-term:** Develop strategic prompt evolution plan

---

*Report generated by AMAS Multi-Agent Adaptive Prompt Improvement System*
*Powered by: {', '.join(results['agents_used']) if results['agents_used'] else 'AI Agents'}*
"""
        return report

    async def run(self):
        """Main execution function"""
        print("🚀 Starting AMAS Adaptive Prompt Improvement System...")

        # Create artifacts directory
        os.makedirs("artifacts", exist_ok=True)

        # Collect prompts from codebase
        prompts = self.collect_prompts_from_codebase()
        print(f"📝 Found {len(prompts)} prompts to analyze")

        # Analyze prompt effectiveness
        results = await self.analyze_prompt_effectiveness(prompts)

        # Generate report
        report = self.generate_prompt_report(results)

        # Save report
        report_path = "artifacts/prompt_improvement_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📋 Prompt improvement report saved to {report_path}")
        print("✅ Adaptive Prompt Improvement Complete!")

        return results


async def main():
    analyzer = AIAdaptivePromptImprovement()
    await analyzer.run()


if __name__ == "__main__":
    print("🧠 AMAS Adaptive Prompt Improvement System")
    print("=" * 50)

    # Check API key availability
    print("🔑 API Key Status:")
    print(f"  DeepSeek: {'✅' if get_api_key("DEEPSEEK_API_KEY") else '❌'}")
    print(f"  GLM: {'✅' if get_api_key("GLM_API_KEY") else '❌'}")
    print(f"  Grok: {'✅' if get_api_key("GROK_API_KEY") else '❌'}")
    print(f"  Kimi: {'✅' if get_api_key("KIMI_API_KEY") else '❌'}")
    print(f"  Qwen: {'✅' if get_api_key("QWEN_API_KEY") else '❌'}")
    print(f"  GPTOSS: {'✅' if get_api_key("GPTOSS_API_KEY") else '❌'}")
    print()

    asyncio.run(main())
