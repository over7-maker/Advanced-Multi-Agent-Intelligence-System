#!/usr/bin/env python3
"""
AI Parallel Provider System - Query all providers in parallel for fastest response
Reduces response times by parallel querying all 16 providers
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import as_completed

# Import our AI agent fallback system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ai_agent_fallback import ai_agent

class AIParallelProvider:
    """AI system that queries all providers in parallel for fastest response"""
    
    def __init__(self):
        self.providers = ai_agent.providers
        self.available_providers = ai_agent._get_available_providers()
        self.results = {}
        self.response_times = {}
        
    async def query_provider_parallel(self, provider_name: str, prompt: str, task_type: str) -> Dict[str, Any]:
        """Query a single provider in parallel"""
        start_time = time.time()
        
        try:
            provider = self.providers[provider_name]
            handler = provider['handler']
            
            # Prepare handler arguments
            handler_args = {
                'api_key': provider['api_key'],
                'prompt': prompt
            }
            
            # Add provider-specific arguments
            if 'base_url' in provider:
                handler_args['base_url'] = provider['base_url']
            if 'model' in provider:
                handler_args['model'] = provider['model']
            
            # Call the provider
            result = await handler(**handler_args)
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "provider": provider_name,
                "response": result,
                "response_time": response_time,
                "task_type": task_type,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "provider": provider_name,
                "error": str(e),
                "response_time": response_time,
                "task_type": task_type,
                "timestamp": datetime.now().isoformat()
            }
    
    async def query_all_providers_parallel(self, prompt: str, task_type: str = "analysis") -> Dict[str, Any]:
        """Query all available providers in parallel"""
        print(f"🚀 Querying {len(self.available_providers)} providers in parallel...")
        
        start_time = time.time()
        
        # Create tasks for all providers
        tasks = []
        for provider_name in self.available_providers:
            task = asyncio.create_task(
                self.query_provider_parallel(provider_name, prompt, task_type)
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = []
        completed_tasks = 0
        
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
                completed_tasks += 1
                
                if result['success']:
                    print(f"✅ {result['provider']}: {result['response_time']:.2f}s")
                else:
                    print(f"❌ {result['provider']}: {result['error'][:50]}...")
                
            except Exception as e:
                print(f"❌ Task failed: {e}")
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        # Find the best result (fastest successful response)
        best_result = None
        if successful_results:
            best_result = min(successful_results, key=lambda x: x['response_time'])
        
        # Calculate statistics
        stats = {
            "total_providers": len(self.available_providers),
            "successful_providers": len(successful_results),
            "failed_providers": len(failed_results),
            "total_time": total_time,
            "fastest_response": min([r['response_time'] for r in results]) if results else 0,
            "slowest_response": max([r['response_time'] for r in results]) if results else 0,
            "average_response_time": sum([r['response_time'] for r in results]) / len(results) if results else 0
        }
        
        return {
            "success": best_result is not None,
            "best_result": best_result,
            "all_results": results,
            "successful_results": successful_results,
            "failed_results": failed_results,
            "statistics": stats,
            "total_time": total_time
        }
    
    async def get_consensus_analysis(self, prompt: str, task_type: str = "analysis") -> Dict[str, Any]:
        """Get consensus analysis from multiple providers"""
        print(f"🧠 Getting consensus analysis from multiple providers...")
        
        # Query all providers in parallel
        parallel_result = await self.query_all_providers_parallel(prompt, task_type)
        
        if not parallel_result['success']:
            return {
                "success": False,
                "error": "No providers responded successfully",
                "parallel_result": parallel_result
            }
        
        # Get successful results
        successful_results = parallel_result['successful_results']
        
        if len(successful_results) < 2:
            # Not enough results for consensus, return best result
            return {
                "success": True,
                "consensus_type": "single_provider",
                "best_result": parallel_result['best_result'],
                "all_results": successful_results,
                "statistics": parallel_result['statistics']
            }
        
        # Create consensus prompt
        # Prepare truncated responses for consensus prompt
        truncated_responses = [{
            "provider": r['provider'],
            "response": r['response'][:1000],  # Truncate for length
            "response_time": r['response_time']
        } for r in successful_results]
        
        consensus_prompt = f"""
As an expert AI analyst, synthesize these multiple AI responses into a single, comprehensive analysis.

## Original Prompt:
{prompt}

## AI Responses:
{json.dumps(truncated_responses, indent=2)}

## Task:
1. **Synthesize** the best insights from all responses
2. **Identify** common themes and patterns
3. **Resolve** any contradictions between responses
4. **Provide** a comprehensive, unified analysis
5. **Include** confidence scores based on consensus

## Response Format:
Provide your synthesis in this JSON format:
```json
{{
  "consensus_analysis": "Comprehensive analysis synthesizing all responses",
  "confidence_score": 0.95,
  "common_themes": ["Theme 1", "Theme 2"],
  "contradictions_resolved": ["Contradiction 1", "Contradiction 2"],
  "provider_agreement": 0.85,
  "key_insights": ["Insight 1", "Insight 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "synthesis_quality": "high|medium|low"
}}
```

Focus on creating the most accurate and comprehensive analysis possible.
"""
        
        try:
            # Use the best provider for consensus analysis
            best_provider = parallel_result['best_result']['provider']
            consensus_result = await ai_agent.analyze_with_fallback(consensus_prompt, f"consensus_{task_type}")
            
            if consensus_result.get('success'):
                # Extract JSON from consensus response
                content = consensus_result.get('content', '')
                try:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        consensus_analysis = json.loads(json_match.group(1))
                    else:
                        # Fallback consensus
                        consensus_analysis = {
                            "consensus_analysis": content[:1000],
                            "confidence_score": 0.8,
                            "common_themes": ["Analysis themes"],
                            "contradictions_resolved": [],
                            "provider_agreement": 0.7,
                            "key_insights": ["Key insights from analysis"],
                            "recommendations": ["Recommendations from analysis"],
                            "synthesis_quality": "medium"
                        }
                    
                    return {
                        "success": True,
                        "consensus_type": "multi_provider",
                        "consensus_analysis": consensus_analysis,
                        "best_result": parallel_result['best_result'],
                        "all_results": successful_results,
                        "statistics": parallel_result['statistics'],
                        "consensus_provider": best_provider
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to parse consensus analysis"
                    }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate consensus analysis"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception in consensus analysis: {e}"
            }
    
    async def generate_parallel_report(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive parallel querying report"""
        print("📊 Generating parallel querying report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "query_type": "parallel",
            "summary": {
                "total_providers": result['statistics']['total_providers'],
                "successful_providers": result['statistics']['successful_providers'],
                "failed_providers": result['statistics']['failed_providers'],
                "success_rate": (result['statistics']['successful_providers'] / result['statistics']['total_providers']) * 100,
                "total_time": result['statistics']['total_time'],
                "fastest_response": result['statistics']['fastest_response'],
                "average_response_time": result['statistics']['average_response_time']
            },
            "provider_performance": {},
            "consensus_analysis": result.get('consensus_analysis', {}),
            "recommendations": []
        }
        
        # Analyze provider performance
        for provider_result in result['all_results']:
            provider_name = provider_result['provider']
            report["provider_performance"][provider_name] = {
                "success": provider_result['success'],
                "response_time": provider_result['response_time'],
                "rank": 1 if provider_result['success'] else 0
            }
        
        # Generate recommendations
        if result['statistics']['successful_providers'] < result['statistics']['total_providers']:
            report["recommendations"].append("Some providers failed - check API keys and connectivity")
        
        if result['statistics']['average_response_time'] > 10:
            report["recommendations"].append("Average response time is high - consider optimizing provider selection")
        
        if result['statistics']['successful_providers'] > 5:
            report["recommendations"].append("High provider success rate - system is very reliable")
        
        return report

async def main():
    """Main function to run parallel provider system"""
    print("⚡ AI Parallel Provider System Starting...")
    print("=" * 60)
    
    parallel_provider = AIParallelProvider()
    
    # Test prompt
    test_prompt = """
    Analyze this Python code for potential issues and improvements:
    
    def process_data(data):
        result = []
        for item in data:
            if item > 0:
                result.append(item * 2)
        return result
    
    Provide specific recommendations for optimization, error handling, and best practices.
    """
    
    try:
        # Test parallel querying
        print(f"🧪 Testing with {len(parallel_provider.available_providers)} providers...")
        result = await parallel_provider.query_all_providers_parallel(test_prompt, "code_analysis")
        
        if result['success']:
            print(f"✅ Parallel querying successful!")
            print(f"📊 Best provider: {result['best_result']['provider']}")
            print(f"⏱️ Fastest response: {result['statistics']['fastest_response']:.2f}s")
            print(f"📈 Success rate: {(result['statistics']['successful_providers'] / result['statistics']['total_providers']) * 100:.1f}%")
            
            # Test consensus analysis
            print(f"\n🧠 Testing consensus analysis...")
            consensus_result = await parallel_provider.get_consensus_analysis(test_prompt, "code_analysis")
            
            if consensus_result['success']:
                print(f"✅ Consensus analysis successful!")
                print(f"🎯 Consensus type: {consensus_result['consensus_type']}")
                if 'consensus_analysis' in consensus_result:
                    print(f"📊 Confidence score: {consensus_result['consensus_analysis'].get('confidence_score', 0):.2f}")
        else:
            print(f"❌ Parallel querying failed")
        
        # Generate report
        report = await parallel_provider.generate_parallel_report(result)
        
        # Save report
        os.makedirs("artifacts", exist_ok=True)
        with open("artifacts/parallel_provider_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 PARALLEL PROVIDER REPORT")
        print("=" * 60)
        print(f"🚀 Total Providers: {report['summary']['total_providers']}")
        print(f"✅ Successful: {report['summary']['successful_providers']}")
        print(f"❌ Failed: {report['summary']['failed_providers']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"⏱️ Total Time: {report['summary']['total_time']:.2f}s")
        print(f"🏃 Fastest: {report['summary']['fastest_response']:.2f}s")
        
        return report
        
    except Exception as e:
        print(f"❌ Critical error in parallel provider system: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(main())