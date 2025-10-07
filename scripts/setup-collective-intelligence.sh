#!/bin/bash
# AMAS Collective Intelligence Setup Script

set -e

echo "🧠 Setting up AMAS Collective Intelligence System..."
echo "================================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Install Python ML dependencies
echo "📦 Installing machine learning dependencies..."
pip install scikit-learn pandas numpy networkx matplotlib seaborn joblib

# Create required directories
echo "📁 Creating intelligence directories..."
mkdir -p data/collective_knowledge
mkdir -p data/personalities
mkdir -p data/models
mkdir -p data/predictions
mkdir -p logs/intelligence

# Initialize collective knowledge base
echo "🧠 Initializing collective knowledge base..."
python3 -c "
import pickle
import os
os.makedirs('data/collective_knowledge', exist_ok=True)
with open('data/collective_knowledge/collective_knowledge.pkl', 'wb') as f:
    pickle.dump({}, f)
print('✅ Knowledge base initialized')
"

# Create intelligence configuration
echo "⚙️ Creating intelligence configuration..."
cat > config/intelligence.json << EOF
{
    "collective_learning": {
        "enabled": true,
        "learning_cycle_hours": 1,
        "knowledge_retention_days": 30,
        "min_confidence_threshold": 0.7,
        "adaptation_rate": 0.1
    },
    "adaptive_personalities": {
        "enabled": true,
        "adaptation_strength": 0.05,
        "personality_persistence": true,
        "user_profile_retention_days": 90
    },
    "predictive_intelligence": {
        "enabled": true,
        "model_retrain_threshold": 50,
        "prediction_confidence_threshold": 0.6,
        "resource_prediction_horizon_minutes": 60
    },
    "models": {
        "task_success_model": "GradientBoostingClassifier",
        "duration_model": "RandomForestRegressor", 
        "quality_model": "RandomForestRegressor",
        "resource_model": "LinearRegression"
    }
}
EOF

# Create intelligence test script
echo "🧪 Creating intelligence test script..."
cat > test-intelligence.py << 'EOF'
#!/usr/bin/env python3
"""Test AMAS Intelligence Systems"""

import asyncio
import sys
import os
sys.path.append('src')

from amas.intelligence.intelligence_manager import intelligence_manager

async def test_intelligence_systems():
    """Test all intelligence systems"""
    
    print("🧪 Testing AMAS Intelligence Systems...")
    print("="*50)
    
    # Start intelligence systems
    await intelligence_manager.start_intelligence_systems()
    
    # Test task optimization
    print("\n🎯 Testing Task Optimization...")
    task_data = {
        'task_type': 'security_scan',
        'target': 'example.com',
        'parameters': {'depth': 'standard'},
        'user_id': 'test_user'
    }
    
    optimization = await intelligence_manager.optimize_task_before_execution(task_data)
    print(f"✅ Optimal agents: {optimization['optimal_agents']}")
    print(f"✅ Task prediction confidence: {optimization['task_prediction'].confidence:.2f}")
    print(f"✅ Recommendations: {len(optimization['optimization_recommendations'])}")
    
    # Test task completion processing
    print("\n📝 Testing Task Completion Processing...")
    completed_task = {
        'task_id': 'test_001',
        'task_type': 'security_scan',
        'target': 'example.com',
        'parameters': {'depth': 'standard'},
        'agents_used': optimization['optimal_agents'],
        'execution_time': 120.5,
        'success_rate': 0.9,
        'solution_quality': 0.85,
        'user_feedback': {'rating': 4, 'comments': 'Good results'},
        'user_id': 'test_user'
    }
    
    await intelligence_manager.process_task_completion(completed_task)
    print("✅ Task completion processed")
    
    # Test dashboard data
    print("\n📊 Testing Dashboard Data...")
    dashboard_data = await intelligence_manager.get_intelligence_dashboard_data()
    print(f"✅ Collective insights: {dashboard_data['collective_intelligence']['total_insights']}")
    print(f"✅ Personality adaptations: {dashboard_data['adaptive_personalities']['total_agents']}")
    print(f"✅ Prediction models: {len(dashboard_data['predictive_accuracy']['model_accuracies'])}")
    
    print("\n🎉 All intelligence systems working correctly!")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(test_intelligence_systems())
EOF

chmod +x test-intelligence.py

# Create intelligence monitoring script
cat > monitor-intelligence.py << 'EOF'
#!/usr/bin/env python3
"""Monitor AMAS Intelligence Systems"""

import asyncio
import time
import sys
import os
sys.path.append('src')

from amas.intelligence.intelligence_manager import intelligence_manager

async def monitor_intelligence():
    """Monitor intelligence systems in real-time"""
    
    print("🧠 AMAS Intelligence Monitor")
    print("="*40)
    print("Press Ctrl+C to stop monitoring")
    print()
    
    try:
        # Start intelligence systems
        await intelligence_manager.start_intelligence_systems()
        
        while True:
            # Get current status
            dashboard_data = await intelligence_manager.get_intelligence_dashboard_data()
            
            # Clear screen and show status
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🧠 AMAS Intelligence Monitor")
            print("="*40)
            print(f"Status: {dashboard_data['system_status']}")
            print(f"Intelligence Level: {dashboard_data['intelligence_level']}")
            print()
            
            # Collective Intelligence
            ci = dashboard_data['collective_intelligence']
            print("📚 Collective Intelligence:")
            print(f"  Insights: {ci['total_insights']} (High confidence: {ci['high_confidence_insights']})")
            print(f"  Knowledge Entries: {ci['knowledge_entries']}")
            print(f"  Learning Graph: {ci['learning_graph_nodes']} nodes, {ci['learning_graph_edges']} edges")
            print()
            
            # Adaptive Personalities
            ap = dashboard_data['adaptive_personalities']
            print("🎭 Adaptive Personalities:")
            print(f"  Active Agents: {ap['total_agents']}")
            print(f"  Total Interactions: {ap['total_interactions']}")
            print(f"  Average Satisfaction: {ap['average_satisfaction']:.2f}")
            print()
            
            # Predictive Intelligence
            pa = dashboard_data['predictive_accuracy']
            print("🔮 Predictive Intelligence:")
            print(f"  Active Models: {len(pa['model_accuracies'])}")
            print(f"  Total Predictions: {pa['total_predictions']}")
            print()
            
            # Resource Predictions
            rp = dashboard_data['resource_predictions']
            print("📊 Resource Predictions (60 min):")
            print(f"  CPU: {rp['predicted_cpu_usage']:.1f}%")
            print(f"  Memory: {rp['predicted_memory_usage']:.1f}%")
            print(f"  Task Load: {rp['predicted_task_load']}")
            if rp['bottleneck_predictions']:
                print(f"  Bottlenecks: {', '.join(rp['bottleneck_predictions'])}")
            print()
            
            print(f"Last updated: {time.strftime('%H:%M:%S')}")
            print("Press Ctrl+C to stop")
            
            # Wait before next update
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n👋 Intelligence monitoring stopped")

if __name__ == "__main__":
    asyncio.run(monitor_intelligence())
EOF

chmod +x monitor-intelligence.py

# Create intelligence learning script
cat > learn-intelligence.py << 'EOF'
#!/usr/bin/env python3
"""Train AMAS Intelligence Systems with Sample Data"""

import asyncio
import sys
import os
sys.path.append('src')

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
EOF

chmod +x learn-intelligence.py

# Create intelligence dashboard integration
cat > src/amas/intelligence/__init__.py << 'EOF'
#!/usr/bin/env python3
"""
AMAS Intelligence Package
Collective learning, adaptive personalities, and predictive intelligence
"""

from .collective_learning import CollectiveIntelligenceEngine, CollectiveIntelligenceManager
from .adaptive_personality import AdaptiveAgentPersonality, PersonalityOrchestrator
from .predictive_engine import PredictiveIntelligenceEngine
from .intelligence_manager import AMASIntelligenceManager, intelligence_manager

__all__ = [
    'CollectiveIntelligenceEngine',
    'CollectiveIntelligenceManager', 
    'AdaptiveAgentPersonality',
    'PersonalityOrchestrator',
    'PredictiveIntelligenceEngine',
    'AMASIntelligenceManager',
    'intelligence_manager'
]
EOF

echo ""
echo -e "${BLUE}================================================="
echo "✅ AMAS Collective Intelligence Setup Complete!"
echo -e "=================================================${NC}"
echo ""
echo -e "${GREEN}Intelligence Features Installed:${NC}"
echo "  🧠 Collective Learning Engine"
echo "  🎭 Adaptive Agent Personalities"
echo "  🔮 Predictive Intelligence"
echo "  📊 Cross-Agent Knowledge Transfer"
echo "  🎯 Task Optimization Recommendations"
echo "  📈 Performance Prediction Models"
echo "  🔄 Continuous Learning Cycles"
echo ""
echo -e "${YELLOW}Available Commands:${NC}"
echo "  ./test-intelligence.py      - Test intelligence systems"
echo "  ./monitor-intelligence.py   - Real-time intelligence monitoring"
echo "  ./learn-intelligence.py     - Train with sample data"
echo ""
echo -e "${BLUE}Intelligence Capabilities:${NC}"
echo "  ✅ 7 AI agents with collective learning"
echo "  ✅ Dynamic personality adaptation"
echo "  ✅ Task outcome prediction"
echo "  ✅ Resource usage forecasting"
echo "  ✅ Cross-agent knowledge sharing"
echo "  ✅ Continuous optimization"
echo ""
echo -e "${RED}Next Steps:${NC}"
echo "1. Test intelligence systems: ./test-intelligence.py"
echo "2. Train with sample data: ./learn-intelligence.py"
echo "3. Monitor in real-time: ./monitor-intelligence.py"
echo ""
echo "🧠 Your AMAS agents are now truly intelligent and collaborative! 🚀"