#!/usr/bin/env python3
"""
Research Pipeline Example
Demonstrates multi-agent research workflow
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AMASIntelligenceSystem

async def research_pipeline_example():
    """Research pipeline example"""
    print("🔬 AMAS Research Pipeline Example")
    print("=" * 50)
    
    # Configuration
    config = {
        'llm_service_url': 'http://localhost:11434',
        'vector_service_url': 'http://localhost:8001',
        'graph_service_url': 'http://localhost:7474',
        'n8n_url': 'http://localhost:5678',
        'n8n_api_key': 'your_api_key_here'
    }
    
    try:
        # Initialize AMAS system
        print("🚀 Initializing AMAS system...")
        amas = AMASIntelligenceSystem(config)
        await amas.initialize()
        print("✅ AMAS system initialized")
        
        # Research topic
        research_topic = "Advanced Persistent Threats (APTs) in 2024"
        
        print(f"\n🎯 Research Topic: {research_topic}")
        
        # Phase 1: OSINT Collection
        print("\n📊 Phase 1: OSINT Collection")
        osint_task = {
            'type': 'osint',
            'description': f'Collect intelligence on {research_topic}',
            'priority': 2,
            'metadata': {
                'sources': ['news', 'academic_papers', 'security_reports'],
                'keywords': ['APT', 'advanced persistent threat', 'cyber attack', 'malware'],
                'timeframe': '2024'
            }
        }
        
        osint_task_id = await amas.submit_intelligence_task(osint_task)
        print(f"✅ OSINT task submitted: {osint_task_id}")
        
        # Phase 2: Data Analysis
        print("\n📈 Phase 2: Data Analysis")
        analysis_task = {
            'type': 'data_analysis',
            'description': f'Analyze collected data on {research_topic}',
            'priority': 2,
            'metadata': {
                'data_sources': ['osint_results'],
                'analysis_type': 'statistical',
                'output_format': 'report'
            }
        }
        
        analysis_task_id = await amas.submit_intelligence_task(analysis_task)
        print(f"✅ Data analysis task submitted: {analysis_task_id}")
        
        # Phase 3: Investigation
        print("\n🔍 Phase 3: Investigation")
        investigation_task = {
            'type': 'investigation',
            'description': f'Investigate patterns and relationships in {research_topic}',
            'priority': 3,
            'metadata': {
                'focus': 'threat_actors',
                'methodology': 'link_analysis',
                'scope': 'global'
            }
        }
        
        investigation_task_id = await amas.submit_intelligence_task(investigation_task)
        print(f"✅ Investigation task submitted: {investigation_task_id}")
        
        # Phase 4: Reporting
        print("\n📝 Phase 4: Report Generation")
        reporting_task = {
            'type': 'reporting',
            'description': f'Generate comprehensive report on {research_topic}',
            'priority': 1,
            'metadata': {
                'report_type': 'intelligence_assessment',
                'audience': 'security_analysts',
                'format': 'pdf',
                'sections': ['executive_summary', 'threat_landscape', 'recommendations']
            }
        }
        
        reporting_task_id = await amas.submit_intelligence_task(reporting_task)
        print(f"✅ Reporting task submitted: {reporting_task_id}")
        
        # Monitor progress
        print("\n⏳ Monitoring research pipeline progress...")
        
        # Check task statuses
        tasks = [osint_task_id, analysis_task_id, investigation_task_id, reporting_task_id]
        task_names = ['OSINT Collection', 'Data Analysis', 'Investigation', 'Report Generation']
        
        for i, (task_id, task_name) in enumerate(zip(tasks, task_names)):
            status = await amas.orchestrator.get_task_status(task_id)
            print(f"  {i+1}. {task_name}: {status['status']}")
        
        # Get system status
        print("\n📈 System Status:")
        status = await amas.get_system_status()
        print(f"  Active Agents: {status['agents']}")
        print(f"  Active Tasks: {status['active_tasks']}")
        print(f"  Completed Tasks: {status['completed_tasks']}")
        
        print("\n🎉 Research pipeline example completed!")
        print("📊 Research pipeline demonstrates:")
        print("  - Multi-agent collaboration")
        print("  - Sequential task execution")
        print("  - Data flow between agents")
        print("  - Comprehensive reporting")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    finally:
        # Shutdown
        print("\n🔄 Shutting down AMAS system...")
        await amas.shutdown()
        print("✅ AMAS system shutdown complete")
    
    return True

if __name__ == "__main__":
    asyncio.run(research_pipeline_example())