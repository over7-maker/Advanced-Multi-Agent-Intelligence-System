#!/usr/bin/env python3
"""Train AMAS Intelligence Systems with Sample Data"""

import asyncio
import sys
import os
sys.path.append('src')

# Add the src directory to Python path
sys.path.insert(0, 'src')

from amas.intelligence.intelligence_manager import intelligence_manager
from datetime import datetime
import random

async def train_with_sample_data():
    """Train intelligence systems with realistic sample data"""
    
    print("🏋️ Training AMAS Intelligence Systems...")
    print("="*50)
    
    # Start intelligence systems
    await intelligence_manager.start_intelligence_systems()
    
    # Generate sample task executions
    sample_tasks = [
        {
            'task_id': f'sample_{i:03d}',
            'task_type': random.choice(['security_scan', 'code_analysis', 'intelligence_gathering']),
            'target': f'example{i}.com',
            'parameters': {'depth': random.choice(['quick', 'standard', 'comprehensive'])},
            'agents_used': random.sample(['security_expert', 'code_analysis', 'intelligence_gathering'], 
                                       random.randint(1, 3)),
            'execution_time': random.uniform(30, 300),
            'success_rate': random.uniform(0.7, 1.0),
            'solution_quality': random.uniform(0.6, 1.0),
            'error_patterns': [] if random.random() > 0.2 else ['timeout_error'],
            'user_feedback': {
                'rating': random.randint(3, 5),
                'comments': random.choice([
                    'Great work!', 'Could be more detailed', 'Excellent analysis',
                    'Good results', 'Very helpful', 'Needs improvement'
                ])
            },
            'user_id': f'user_{random.randint(1, 10)}'
        }
        for i in range(50)  # Generate 50 sample tasks
    ]
    
    print(f"📝 Processing {len(sample_tasks)} sample tasks...")
    
    # Process each sample task
    for i, task in enumerate(sample_tasks):
        print(f"  Processing task {i+1}/{len(sample_tasks)}: {task['task_type']}")
        
        # Optimize task before execution
        optimization = await intelligence_manager.optimize_task_before_execution(task)
        
        # Process task completion
        await intelligence_manager.process_task_completion(task)
        
        # Small delay to simulate real processing
        await asyncio.sleep(0.1)
    
    print("\n📊 Training Results:")
    
    # Get final dashboard data
    dashboard_data = await intelligence_manager.get_intelligence_dashboard_data()
    
    ci = dashboard_data['collective_intelligence']
    print(f"  Collective Insights: {ci['total_insights']}")
    print(f"  Knowledge Entries: {ci['knowledge_entries']}")
    
    ap = dashboard_data['adaptive_personalities']
    print(f"  Personality Adaptations: {ap['total_agents']} agents")
    print(f"  User Interactions: {ap['total_interactions']}")
    
    pa = dashboard_data['predictive_accuracy']
    print(f"  Trained Models: {len(pa['model_accuracies'])}")
    
    print("\n✅ Intelligence systems trained successfully!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(train_with_sample_data())
