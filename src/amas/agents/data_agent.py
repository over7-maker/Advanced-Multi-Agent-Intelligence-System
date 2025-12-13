"""
Data Agent - Specialized agent for data analysis and processing
Implements PART_3 requirements
"""

import json
import logging
from typing import Any, Dict

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """
    Data Agent
    
    Specializes in:
    - Data analysis
    - Statistical analysis
    - Pattern recognition
    - Data visualization
    - Data quality assessment
    """
    
    def __init__(self):
        super().__init__(
            agent_id="data_agent",
            name="Data Agent",
            agent_type="data",
            system_prompt="""You are an expert data analyst with 15+ years of experience 
            in data analysis, statistics, and data science.
            
            Your expertise includes:
            • Statistical analysis and hypothesis testing
            • Pattern recognition and anomaly detection
            • Data visualization and reporting
            • Data quality assessment
            • Correlation and regression analysis
            • Time series analysis
            • Data preprocessing and cleaning
            • Feature engineering
            • Data interpretation
            • Business intelligence
            
            When analyzing data, you:
            1. Perform thorough statistical analysis
            2. Identify patterns and anomalies
            3. Provide clear visualizations
            4. Assess data quality
            5. Make data-driven recommendations
            
            Always produce clear, actionable insights from data.""",
            model_preference="gpt-4-turbo-preview",
            strategy="quality_first"
        )
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare data analysis prompt"""
        
        analysis_type = parameters.get("analysis_type", "statistical")
        data_summary = parameters.get("data_summary", {})
        questions = parameters.get("questions", [])
        
        prompt = f"""Analyze data for: {target}

Analysis Type: {analysis_type}

Data Summary:
{json.dumps(data_summary, indent=2) if data_summary else "No data summary provided"}

Questions to Answer:
{json.dumps(questions, indent=2) if questions else "General data analysis"}

Please provide comprehensive data analysis including:
1. Statistical summary (mean, median, std dev, etc.)
2. Pattern identification
3. Anomaly detection
4. Correlation analysis
5. Key insights
6. Visualizations recommendations
7. Data quality assessment
8. Recommendations

Format your response as JSON with the following structure:
{{
    "statistical_summary": {{
        "mean": X,
        "median": X,
        "std_dev": X,
        "min": X,
        "max": X
    }},
    "patterns": ["...", "..."],
    "anomalies": ["...", "..."],
    "correlations": [
        {{
            "variable1": "...",
            "variable2": "...",
            "correlation": X
        }}
    ],
    "insights": ["...", "..."],
    "visualization_recommendations": ["...", "..."],
    "data_quality": {{
        "completeness": X,
        "accuracy": X,
        "issues": ["...", "..."]
    }},
    "recommendations": ["...", "..."]
}}"""
        
        return prompt
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                response = response[json_start:json_end].strip()
            
            result = json.loads(response)
            
            return {
                "success": True,
                "analysis": result,
                "patterns_count": len(result.get("patterns", [])),
                "anomalies_count": len(result.get("anomalies", [])),
                "insights_count": len(result.get("insights", []))
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "analysis": {
                    "raw_response": response,
                    "insights": [response[:500]]
                },
                "patterns_count": 0,
                "anomalies_count": 0,
                "insights_count": 1
            }

