"""
Result Aggregator
Merges, deduplicates, and synthesizes results from multiple tools
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict

from src.amas.agents.tools.multi_tool_executor import ToolExecutionResult
from src.amas.ai.enhanced_router_class import get_ai_router

logger = logging.getLogger(__name__)


@dataclass
class AggregatedResult:
    """Aggregated result from multiple tools"""
    primary_findings: Dict[str, Any]
    supporting_evidence: Dict[str, Any]  # Tool name -> result
    confidence_scores: Dict[str, float]  # Tool name -> confidence
    tool_attribution: List[str]  # Tools that contributed
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    synthesis: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResultAggregator:
    """Aggregates and synthesizes results from multiple tools"""
    
    def __init__(self):
        self.ai_router = get_ai_router()
        logger.info("ResultAggregator initialized")
    
    async def aggregate_results(
        self,
        tool_results: List[ToolExecutionResult],
        task_description: str,
        use_ai_synthesis: bool = True
    ) -> AggregatedResult:
        """
        Aggregate results from multiple tools
        
        Args:
            tool_results: List of tool execution results
            task_description: Original task description
            use_ai_synthesis: Whether to use AI for final synthesis
            
        Returns:
            Aggregated result with merged findings
        """
        if not tool_results:
            logger.warning("No tool results to aggregate")
            return AggregatedResult(
                primary_findings={},
                supporting_evidence={},
                confidence_scores={},
                tool_attribution=[]
            )
        
        logger.info(f"Aggregating results from {len(tool_results)} tools")
        
        # Step 1: Filter successful results
        successful_results = [r for r in tool_results if r.success]
        
        if not successful_results:
            logger.warning("No successful tool results to aggregate")
            return AggregatedResult(
                primary_findings={"error": "All tools failed"},
                supporting_evidence={},
                confidence_scores={},
                tool_attribution=[r.tool_name for r in tool_results]
            )
        
        # Step 2: Extract and merge data
        merged_data = self._merge_results(successful_results)
        
        # Step 3: Deduplicate information
        deduplicated = self._deduplicate(merged_data)
        
        # Step 4: Identify conflicts
        conflicts = self._identify_conflicts(successful_results)
        
        # Step 5: Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(successful_results)
        
        # Step 6: Create supporting evidence map
        supporting_evidence = {
            r.tool_name: r.result for r in successful_results if r.result
        }
        
        # Step 7: AI synthesis (if enabled)
        synthesis = None
        if use_ai_synthesis:
            synthesis = await self._synthesize_with_ai(
                deduplicated,
                task_description,
                successful_results
            )
        
        # Step 8: Extract primary findings
        primary_findings = self._extract_primary_findings(
            deduplicated,
            confidence_scores
        )
        
        return AggregatedResult(
            primary_findings=primary_findings,
            supporting_evidence=supporting_evidence,
            confidence_scores=confidence_scores,
            tool_attribution=[r.tool_name for r in successful_results],
            conflicts=conflicts,
            synthesis=synthesis,
            metadata={
                "total_tools": len(tool_results),
                "successful_tools": len(successful_results),
                "failed_tools": len(tool_results) - len(successful_results)
            }
        )
    
    def _merge_results(
        self,
        results: List[ToolExecutionResult]
    ) -> Dict[str, Any]:
        """Merge results from multiple tools"""
        merged = {}
        
        for result in results:
            if not result.result:
                continue
            
            tool_data = result.result
            
            # Handle different result formats
            if isinstance(tool_data, dict):
                # Merge dictionaries
                for key, value in tool_data.items():
                    if key not in merged:
                        merged[key] = []
                    if isinstance(merged[key], list):
                        merged[key].append({
                            "value": value,
                            "source": result.tool_name,
                            "metadata": result.metadata
                        })
                    else:
                        # Convert to list
                        merged[key] = [
                            {"value": merged[key], "source": "previous"},
                            {"value": value, "source": result.tool_name}
                        ]
            elif isinstance(tool_data, list):
                # Merge lists
                if "items" not in merged:
                    merged["items"] = []
                merged["items"].extend([
                    {"value": item, "source": result.tool_name}
                    for item in tool_data
                ])
            else:
                # Scalar value
                if "results" not in merged:
                    merged["results"] = []
                merged["results"].append({
                    "value": tool_data,
                    "source": result.tool_name
                })
        
        return merged
    
    def _deduplicate(self, merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate information"""
        deduplicated = {}
        seen_values: Set[str] = set()
        
        for key, value in merged_data.items():
            if isinstance(value, list):
                # Deduplicate list items
                unique_items = []
                for item in value:
                    if isinstance(item, dict):
                        item_value = str(item.get("value", ""))
                        item_hash = hash(item_value)
                        if item_hash not in seen_values:
                            seen_values.add(item_hash)
                            unique_items.append(item)
                    else:
                        item_hash = hash(str(item))
                        if item_hash not in seen_values:
                            seen_values.add(item_hash)
                            unique_items.append(item)
                
                if unique_items:
                    deduplicated[key] = unique_items
            else:
                deduplicated[key] = value
        
        return deduplicated
    
    def _identify_conflicts(
        self,
        results: List[ToolExecutionResult]
    ) -> List[Dict[str, Any]]:
        """Identify conflicts between tool results"""
        conflicts = []
        
        # Compare results from different tools
        for i, result1 in enumerate(results):
            if not result1.result:
                continue
            
            for result2 in results[i+1:]:
                if not result2.result:
                    continue
                
                conflict = self._compare_results(result1, result2)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _compare_results(
        self,
        result1: ToolExecutionResult,
        result2: ToolExecutionResult
    ) -> Optional[Dict[str, Any]]:
        """Compare two results for conflicts"""
        # Simple conflict detection - can be enhanced
        if not isinstance(result1.result, dict) or not isinstance(result2.result, dict):
            return None
        
        conflicts = []
        
        # Check for contradictory values
        for key in set(result1.result.keys()) & set(result2.result.keys()):
            val1 = result1.result[key]
            val2 = result2.result[key]
            
            if val1 != val2:
                # Check if it's a meaningful conflict (not just different formats)
                if isinstance(val1, (str, int, float, bool)) and \
                   isinstance(val2, (str, int, float, bool)):
                    conflicts.append({
                        "field": key,
                        "tool1_value": val1,
                        "tool2_value": val2,
                        "tool1": result1.tool_name,
                        "tool2": result2.tool_name
                    })
        
        if conflicts:
            return {
                "type": "value_conflict",
                "conflicts": conflicts,
                "tools": [result1.tool_name, result2.tool_name]
            }
        
        return None
    
    def _calculate_confidence_scores(
        self,
        results: List[ToolExecutionResult]
    ) -> Dict[str, float]:
        """Calculate confidence scores for each tool's results"""
        scores = {}
        
        for result in results:
            score = 0.5  # Base score
            
            # Bonus for fast execution
            if result.execution_time < 5.0:
                score += 0.2
            elif result.execution_time < 10.0:
                score += 0.1
            
            # Bonus for having result data
            if result.result:
                score += 0.2
            
            # Bonus for metadata
            if result.metadata:
                score += 0.1
            
            # Check if result is from failover
            if result.metadata and result.metadata.get("failover_from"):
                score -= 0.1  # Slight penalty for failover
            
            scores[result.tool_name] = min(1.0, max(0.0, score))
        
        return scores
    
    def _extract_primary_findings(
        self,
        deduplicated: Dict[str, Any],
        confidence_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """Extract primary findings from aggregated data"""
        primary = {}
        
        # Sort by confidence and extract top findings
        sorted_tools = sorted(
            confidence_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Extract findings from highest confidence tools first
        for key, value in deduplicated.items():
            if isinstance(value, list) and value:
                # Get value from highest confidence source
                best_item = None
                best_confidence = 0.0
                
                for item in value:
                    if isinstance(item, dict):
                        source = item.get("source", "")
                        confidence = confidence_scores.get(source, 0.5)
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_item = item.get("value")
                
                if best_item is not None:
                    primary[key] = best_item
                else:
                    # Use first item if no confidence data
                    primary[key] = value[0].get("value") if isinstance(value[0], dict) else value[0]
            else:
                primary[key] = value
        
        return primary
    
    async def _synthesize_with_ai(
        self,
        deduplicated: Dict[str, Any],
        task_description: str,
        results: List[ToolExecutionResult]
    ) -> str:
        """Use AI to synthesize final result from all tool outputs"""
        
        # Prepare synthesis prompt
        tool_summaries = []
        for result in results:
            if result.result:
                tool_summaries.append(
                    f"- {result.tool_name}: {self._summarize_result(result.result)}"
                )
        
        prompt = f"""Synthesize the following results from multiple tools into a comprehensive answer.

Original Task: {task_description}

Tool Results:
{chr(10).join(tool_summaries)}

Aggregated Data:
{self._format_data_for_ai(deduplicated)}

Provide a clear, comprehensive synthesis that:
1. Combines findings from all tools
2. Resolves any conflicts or contradictions
3. Highlights the most important insights
4. Maintains accuracy and avoids speculation

Synthesis:"""

        try:
            response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=None,
                max_tokens=2000,
                temperature=0.3,
                system_prompt="You are an expert at synthesizing information from multiple sources. Provide clear, accurate, and comprehensive summaries.",
                strategy="quality_first"
            )
            
            return response.content
        
        except Exception as e:
            logger.warning(f"AI synthesis failed: {e}")
            return self._fallback_synthesis(deduplicated, results)
    
    def _summarize_result(self, result: Any) -> str:
        """Summarize a tool result for AI prompt"""
        if isinstance(result, dict):
            # Extract key fields
            keys = list(result.keys())[:5]
            summary = ", ".join(f"{k}: {str(result[k])[:50]}" for k in keys)
            return summary[:200]
        elif isinstance(result, list):
            return f"List with {len(result)} items"
        else:
            return str(result)[:200]
    
    def _format_data_for_ai(self, data: Dict[str, Any]) -> str:
        """Format data for AI prompt"""
        lines = []
        for key, value in list(data.items())[:20]:  # Limit to 20 items
            if isinstance(value, list):
                lines.append(f"{key}: {len(value)} items")
            else:
                lines.append(f"{key}: {str(value)[:100]}")
        return "\n".join(lines)
    
    def _fallback_synthesis(
        self,
        deduplicated: Dict[str, Any],
        results: List[ToolExecutionResult]
    ) -> str:
        """Fallback synthesis without AI"""
        summary_parts = []
        
        summary_parts.append(
            f"Results from {len(results)} tools were aggregated."
        )
        
        if deduplicated:
            summary_parts.append(
                f"Key findings: {', '.join(list(deduplicated.keys())[:5])}"
            )
        
        return " ".join(summary_parts)


# Global aggregator instance
_aggregator: Optional[ResultAggregator] = None


def get_result_aggregator() -> ResultAggregator:
    """Get the global result aggregator"""
    global _aggregator
    if _aggregator is None:
        _aggregator = ResultAggregator()
    return _aggregator


__all__ = [
    'AggregatedResult',
    'ResultAggregator',
    'get_result_aggregator',
]

