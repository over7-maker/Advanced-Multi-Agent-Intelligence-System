"""
Data Agent - Specialized agent for data analysis and processing
Implements PART_3 requirements
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser

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
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.data_tools = []
    
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
    
    async def _perform_statistical_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive statistical analysis on data
        """
        stats = {
            "summary": {},
            "distributions": {},
            "correlations": [],
            "error": None
        }
        
        try:
            logger.info(f"DataAgent: Performing statistical analysis on {len(data)} records")
            
            if not data:
                stats["error"] = "No data provided"
                return stats
            
            # Extract numeric columns
            numeric_columns = {}
            for record in data:
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_columns:
                            numeric_columns[key] = []
                        numeric_columns[key].append(value)
            
            # Calculate statistics for each numeric column
            for column, values in numeric_columns.items():
                if not values:
                    continue
                
                sorted_values = sorted(values)
                n = len(values)
                
                # Basic statistics
                mean = sum(values) / n
                median = sorted_values[n // 2] if n % 2 == 1 else (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
                min_val = min(values)
                max_val = max(values)
                
                # Standard deviation
                variance = sum((x - mean) ** 2 for x in values) / n
                std_dev = variance ** 0.5
                
                # Quartiles
                q1_idx = n // 4
                q3_idx = 3 * n // 4
                q1 = sorted_values[q1_idx]
                q3 = sorted_values[q3_idx]
                iqr = q3 - q1
                
                stats["summary"][column] = {
                    "count": n,
                    "mean": round(mean, 4),
                    "median": round(median, 4),
                    "std_dev": round(std_dev, 4),
                    "min": min_val,
                    "max": max_val,
                    "q1": round(q1, 4),
                    "q3": round(q3, 4),
                    "iqr": round(iqr, 4),
                    "range": max_val - min_val
                }
                
                # Distribution type (simplified)
                if std_dev == 0:
                    distribution = "constant"
                elif abs(mean - median) < 0.1 * std_dev:
                    distribution = "normal"
                elif mean > median:
                    distribution = "right_skewed"
                else:
                    distribution = "left_skewed"
                
                stats["distributions"][column] = distribution
            
            # Calculate correlations between numeric columns
            column_names = list(numeric_columns.keys())
            for i, col1 in enumerate(column_names):
                for col2 in column_names[i + 1:]:
                    values1 = numeric_columns[col1]
                    values2 = numeric_columns[col2]
                    
                    if len(values1) != len(values2):
                        continue
                    
                    # Pearson correlation
                    mean1 = sum(values1) / len(values1)
                    mean2 = sum(values2) / len(values2)
                    
                    numerator = sum((values1[j] - mean1) * (values2[j] - mean2) for j in range(len(values1)))
                    denom1 = sum((x - mean1) ** 2 for x in values1) ** 0.5
                    denom2 = sum((x - mean2) ** 2 for x in values2) ** 0.5
                    
                    if denom1 > 0 and denom2 > 0:
                        correlation = numerator / (denom1 * denom2)
                        stats["correlations"].append({
                            "variable1": col1,
                            "variable2": col2,
                            "correlation": round(correlation, 4),
                            "strength": "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.3 else "weak"
                        })
            
            logger.info(f"DataAgent: Statistical analysis complete - {len(stats['summary'])} columns analyzed")
        
        except Exception as e:
            stats["error"] = f"Statistical analysis failed: {str(e)}"
            logger.error(f"DataAgent: Statistical analysis failed: {e}", exc_info=True)
        
        return stats
    
    async def _detect_anomalies(self, data: List[Dict[str, Any]], method: str = "iqr") -> List[Dict[str, Any]]:
        """
        Detect anomalies in data using various methods
        """
        anomalies = []
        
        try:
            logger.info(f"DataAgent: Detecting anomalies using {method} method")
            
            if not data:
                return anomalies
            
            # Extract numeric columns
            numeric_columns = {}
            for record in data:
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_columns:
                            numeric_columns[key] = []
                        numeric_columns[key].append((value, record))
            
            for column, value_records in numeric_columns.items():
                if not value_records:
                    continue
                
                values = [vr[0] for vr in value_records]
                sorted_values = sorted(values)
                n = len(values)
                
                if method == "iqr":
                    # IQR method
                    q1_idx = n // 4
                    q3_idx = 3 * n // 4
                    q1 = sorted_values[q1_idx]
                    q3 = sorted_values[q3_idx]
                    iqr = q3 - q1
                    
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    for value, record in value_records:
                        if value < lower_bound or value > upper_bound:
                            anomalies.append({
                                "column": column,
                                "value": value,
                                "method": "iqr",
                                "bounds": {"lower": lower_bound, "upper": upper_bound},
                                "record": record
                            })
                
                elif method == "zscore":
                    # Z-score method
                    mean = sum(values) / n
                    std_dev = (sum((x - mean) ** 2 for x in values) / n) ** 0.5
                    
                    if std_dev > 0:
                        threshold = 3.0  # 3 standard deviations
                        for value, record in value_records:
                            z_score = abs((value - mean) / std_dev)
                            if z_score > threshold:
                                anomalies.append({
                                    "column": column,
                                    "value": value,
                                    "method": "zscore",
                                    "z_score": round(z_score, 4),
                                    "mean": round(mean, 4),
                                    "std_dev": round(std_dev, 4),
                                    "record": record
                                })
            
            logger.info(f"DataAgent: Detected {len(anomalies)} anomalies using {method} method")
        
        except Exception as e:
            logger.error(f"DataAgent: Anomaly detection failed: {e}", exc_info=True)
        
        return anomalies
    
    async def _generate_visualizations(self, data: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate visualization recommendations and configurations
        """
        visualizations = []
        
        try:
            logger.info("DataAgent: Generating visualization recommendations")
            
            # Extract numeric columns for visualization
            numeric_columns = set()
            for record in data:
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        numeric_columns.add(key)
            
            # Histogram recommendations
            for column in numeric_columns:
                if column in analysis.get("summary", {}):
                    visualizations.append({
                        "type": "histogram",
                        "title": f"Distribution of {column}",
                        "x_axis": column,
                        "y_axis": "Frequency",
                        "description": f"Shows the distribution of {column} values"
                    })
            
            # Correlation heatmap
            correlations = analysis.get("correlations", [])
            if correlations:
                visualizations.append({
                    "type": "heatmap",
                    "title": "Correlation Matrix",
                    "description": "Shows correlations between numeric variables",
                    "data": correlations
                })
            
            # Box plot for anomaly detection
            if analysis.get("anomalies"):
                visualizations.append({
                    "type": "box_plot",
                    "title": "Anomaly Detection",
                    "description": "Shows outliers using box plot",
                    "anomalies_count": len(analysis.get("anomalies", []))
                })
            
            # Time series if timestamp column exists
            timestamp_columns = [col for col in data[0].keys() if "time" in col.lower() or "date" in col.lower()]
            if timestamp_columns and numeric_columns:
                visualizations.append({
                    "type": "line_chart",
                    "title": "Time Series Analysis",
                    "x_axis": timestamp_columns[0],
                    "y_axis": list(numeric_columns)[0],
                    "description": "Shows trends over time"
                })
            
            # Scatter plot for correlations
            strong_correlations = [c for c in correlations if abs(c.get("correlation", 0)) > 0.7]
            for corr in strong_correlations[:3]:  # Top 3
                visualizations.append({
                    "type": "scatter_plot",
                    "title": f"{corr['variable1']} vs {corr['variable2']}",
                    "x_axis": corr["variable1"],
                    "y_axis": corr["variable2"],
                    "correlation": corr["correlation"],
                    "description": f"Shows relationship between {corr['variable1']} and {corr['variable2']}"
                })
            
            logger.info(f"DataAgent: Generated {len(visualizations)} visualization recommendations")
        
        except Exception as e:
            logger.error(f"DataAgent: Visualization generation failed: {e}", exc_info=True)
        
        return visualizations
    
    async def _perform_predictive_analytics(self, data: List[Dict[str, Any]], target_column: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform predictive analytics (simplified linear regression)
        """
        predictions = {
            "model": None,
            "predictions": [],
            "accuracy_metrics": {},
            "error": None
        }
        
        try:
            logger.info("DataAgent: Performing predictive analytics")
            
            if not data or len(data) < 10:
                predictions["error"] = "Insufficient data for predictive analytics (need at least 10 records)"
                return predictions
            
            # Extract numeric columns
            numeric_columns = {}
            for record in data:
                for key, value in record.items():
                    if isinstance(value, (int, float)):
                        if key not in numeric_columns:
                            numeric_columns[key] = []
                        numeric_columns[key].append(value)
            
            if not numeric_columns:
                predictions["error"] = "No numeric columns found for prediction"
                return predictions
            
            # Simple linear regression if we have 2+ numeric columns
            if len(numeric_columns) >= 2:
                column_names = list(numeric_columns.keys())
                
                # Use first column as target if not specified
                target = target_column or column_names[0]
                if target not in numeric_columns:
                    target = column_names[0]
                
                # Use second column as feature
                feature = column_names[1] if column_names[1] != target else (column_names[2] if len(column_names) > 2 else None)
                
                if feature:
                    target_values = numeric_columns[target]
                    feature_values = numeric_columns[feature]
                    
                    if len(target_values) == len(feature_values):
                        # Simple linear regression: y = mx + b
                        n = len(target_values)
                        mean_x = sum(feature_values) / n
                        mean_y = sum(target_values) / n
                        
                        numerator = sum((feature_values[i] - mean_x) * (target_values[i] - mean_y) for i in range(n))
                        denominator = sum((feature_values[i] - mean_x) ** 2 for i in range(n))
                        
                        if denominator > 0:
                            slope = numerator / denominator
                            intercept = mean_y - slope * mean_x
                            
                            # Calculate R-squared
                            ss_res = sum((target_values[i] - (slope * feature_values[i] + intercept)) ** 2 for i in range(n))
                            ss_tot = sum((target_values[i] - mean_y) ** 2 for i in range(n))
                            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                            
                            predictions["model"] = {
                                "type": "linear_regression",
                                "target": target,
                                "feature": feature,
                                "slope": round(slope, 4),
                                "intercept": round(intercept, 4),
                                "r_squared": round(r_squared, 4)
                            }
                            
                            predictions["accuracy_metrics"] = {
                                "r_squared": round(r_squared, 4),
                                "model_quality": "good" if r_squared > 0.7 else "moderate" if r_squared > 0.3 else "poor"
                            }
                            
                            # Generate sample predictions
                            if len(feature_values) > 0:
                                min_feature = min(feature_values)
                                max_feature = max(feature_values)
                                step = (max_feature - min_feature) / 5
                                
                                for i in range(6):
                                    x = min_feature + i * step
                                    y = slope * x + intercept
                                    predictions["predictions"].append({
                                        "feature_value": round(x, 2),
                                        "predicted_target": round(y, 2)
                                    })
            
            logger.info("DataAgent: Predictive analytics complete")
        
        except Exception as e:
            predictions["error"] = f"Predictive analytics failed: {str(e)}"
            logger.error(f"DataAgent: Predictive analytics failed: {e}", exc_info=True)
        
        return predictions
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced data analysis with statistical analysis, visualization, anomaly detection, and predictive analytics
        Overrides BaseAgent.execute to add comprehensive data analysis capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"DataAgent: Starting enhanced data analysis for {target}")
            
            # Get data from parameters
            data = parameters.get("data", [])
            analysis_type = parameters.get("analysis_type", "comprehensive")
            anomaly_method = parameters.get("anomaly_method", "iqr")
            target_column = parameters.get("target_column")
            
            # STEP 1: Perform statistical analysis
            statistical_analysis = {}
            if analysis_type in ["statistical", "comprehensive"]:
                statistical_analysis = await self._perform_statistical_analysis(data)
            
            # STEP 2: Detect anomalies
            anomalies = []
            if analysis_type in ["anomaly", "comprehensive"]:
                anomalies = await self._detect_anomalies(data, method=anomaly_method)
            
            # STEP 3: Generate visualizations
            visualizations = []
            if analysis_type in ["visualization", "comprehensive"]:
                visualizations = await self._generate_visualizations(data, statistical_analysis)
            
            # STEP 4: Perform predictive analytics
            predictions = {}
            if analysis_type in ["predictive", "comprehensive"] and len(data) >= 10:
                predictions = await self._perform_predictive_analytics(data, target_column)
            
            # STEP 5: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, statistical_analysis, anomalies, visualizations, predictions
            )
            
            # STEP 6: Call AI via router
            logger.info(f"DataAgent: Calling AI with comprehensive analysis data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"DataAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 7: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 8: Merge analysis results
            if parsed_result.get("success") and parsed_result.get("analysis"):
                analysis = parsed_result["analysis"]
                
                # Merge statistical analysis
                if statistical_analysis:
                    analysis["statistical_analysis"] = statistical_analysis
                
                # Merge anomalies
                if anomalies:
                    analysis["anomalies"] = anomalies
                    analysis["anomalies_count"] = len(anomalies)
                
                # Merge visualizations
                if visualizations:
                    analysis["visualizations"] = visualizations
                    analysis["visualization_count"] = len(visualizations)
                
                # Merge predictions
                if predictions:
                    analysis["predictive_analytics"] = predictions
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("analysis", {}),
                "output": parsed_result.get("analysis", {}),
                "quality_score": 0.85,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": f"Analyzed {len(data)} records: {len(statistical_analysis.get('summary', {}))} columns, {len(anomalies)} anomalies, {len(visualizations)} visualizations"
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"DataAgent: Execution failed: {e}", exc_info=True)
            
            self.executions += 1
            self.total_duration += execution_duration
            
            return {
                "success": False,
                "error": str(e),
                "duration": execution_duration,
                "quality_score": 0.0
            }
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any],
        statistical_analysis: Dict[str, Any] = None,
        anomalies: List[Dict[str, Any]] = None,
        visualizations: List[Dict[str, Any]] = None,
        predictions: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced data analysis prompt with all analysis results"""
        
        analysis_type = parameters.get("analysis_type", "comprehensive")
        data_summary = parameters.get("data_summary", {})
        questions = parameters.get("questions", [])
        data = parameters.get("data", [])
        
        # Build context from analysis results
        analysis_context = ""
        
        if statistical_analysis:
            analysis_context += f"\n=== STATISTICAL ANALYSIS RESULTS ===\n"
            analysis_context += f"Columns Analyzed: {len(statistical_analysis.get('summary', {}))}\n"
            for col, stats in list(statistical_analysis.get("summary", {}).items())[:5]:
                analysis_context += f"  {col}: mean={stats.get('mean')}, median={stats.get('median')}, std_dev={stats.get('std_dev')}\n"
            if statistical_analysis.get("correlations"):
                analysis_context += f"Correlations Found: {len(statistical_analysis.get('correlations', []))}\n"
        
        if anomalies:
            analysis_context += f"\n=== ANOMALY DETECTION RESULTS ===\n"
            analysis_context += f"Anomalies Detected: {len(anomalies)}\n"
            for anomaly in anomalies[:5]:
                analysis_context += f"  - {anomaly.get('column')}: value={anomaly.get('value')} (method: {anomaly.get('method')})\n"
        
        if visualizations:
            analysis_context += f"\n=== VISUALIZATION RECOMMENDATIONS ===\n"
            analysis_context += f"Visualizations: {len(visualizations)}\n"
            for viz in visualizations[:5]:
                analysis_context += f"  - {viz.get('type')}: {viz.get('title')}\n"
        
        if predictions:
            analysis_context += f"\n=== PREDICTIVE ANALYTICS RESULTS ===\n"
            if predictions.get("model"):
                model = predictions["model"]
                analysis_context += f"Model: {model.get('type')} (R²={model.get('r_squared')})\n"
                analysis_context += f"Target: {model.get('target')}, Feature: {model.get('feature')}\n"
        
        prompt = f"""Analyze data for: {target}

Analysis Type: {analysis_type}
Data Records: {len(data)}

{analysis_context}

Data Summary:
{json.dumps(data_summary, indent=2) if data_summary else "No data summary provided"}

Questions to Answer:
{json.dumps(questions, indent=2) if questions else "General data analysis"}

Based on the COMPREHENSIVE ANALYSIS RESULTS above (statistical analysis, anomaly detection, visualizations, predictive analytics), please provide:
1. Executive summary of findings
2. Key insights and patterns (reference statistical analysis)
3. Anomaly explanations (reference detected anomalies)
4. Visualization strategy (enhance recommended visualizations)
5. Predictive insights (use predictive model results)
6. Data quality assessment
7. Actionable recommendations
8. Business implications

IMPORTANT:
- Reference the statistical analysis results
- Explain detected anomalies
- Recommend visualizations based on generated recommendations
- Use predictive analytics for forecasting
- Provide clear, actionable insights

Format your response as JSON with the following structure:
{{
    "executive_summary": "...",
    "statistical_summary": {json.dumps(statistical_analysis.get('summary', {})) if statistical_analysis else {}},
    "patterns": ["...", "..."],
    "anomalies": {json.dumps(anomalies[:10]) if anomalies else []},
    "correlations": {json.dumps(statistical_analysis.get('correlations', [])) if statistical_analysis else []},
    "insights": ["...", "..."],
    "visualizations": {json.dumps(visualizations) if visualizations else []},
    "predictive_analytics": {json.dumps(predictions) if predictions else {}},
    "data_quality": {{
        "completeness": X,
        "accuracy": X,
        "issues": ["...", "..."]
    }},
    "recommendations": ["...", "..."]
}}"""
        
        return prompt

