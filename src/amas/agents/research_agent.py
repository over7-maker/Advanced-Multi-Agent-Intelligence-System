"""
Research Agent - Specialized agent for research and information gathering
Implements PART_3 requirements
"""

import json
import logging
import os
from typing import Any, Dict, List

import aiohttp

from src.amas.agents.base_agent import BaseAgent
from src.amas.agents.tools import get_tool_registry
from src.amas.agents.utils.json_parser import JSONParser
from src.amas.agents.schemas import ResearchReport

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent
    
    Specializes in:
    - Technical research
    - Information synthesis
    - Literature review
    - Technology evaluation
    - Best practices research
    """
    
    def __init__(self):
        super().__init__(
            agent_id="research_agent",
            name="Research Agent",
            agent_type="research",
            system_prompt="""You are an expert researcher with 15+ years of experience 
            in technical research, information synthesis, and technology evaluation.
            
            Your expertise includes:
            • Technical research methodologies
            • Information gathering and synthesis
            • Literature review
            • Technology stack evaluation
            • Best practices research
            • Competitive analysis
            • Trend analysis
            • Academic paper analysis
            • Documentation review
            • Knowledge synthesis
            
            When conducting research, you:
            1. Gather information from multiple sources
            2. Synthesize findings clearly
            3. Provide citations and references
            4. Evaluate pros and cons
            5. Make evidence-based recommendations
            
            Always produce thorough, well-researched reports.""",
            model_preference=None,  # Use local models first
            strategy="quality_first"
        )
        
        # Get tool registry
        tool_registry = get_tool_registry()
        self.research_tools = [
            "web_scraper",
            "api_fetcher",
            "github_api"
        ]
        
        # Web search API key (optional)
        self.serpapi_key = os.getenv("SERPAPI_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare research prompt"""
        
        research_topic = parameters.get("research_topic", target)
        research_type = parameters.get("research_type", "technology_evaluation")
        scope = parameters.get("scope", "comprehensive")
        sources = parameters.get("sources", [])
        
        prompt = f"""Conduct research on: {research_topic}

Research Type: {research_type}
Scope: {scope}

Sources to Consider:
{json.dumps(sources, indent=2) if sources else "Use general knowledge and best practices"}

Please provide comprehensive research report including:
1. Executive summary
2. Key findings
3. Detailed analysis
4. Pros and cons evaluation
5. Best practices identified
6. Recommendations
7. References and sources

Format your response as JSON with the following structure:
{{
    "executive_summary": "...",
    "key_findings": ["...", "..."],
    "detailed_analysis": "...",
    "pros_cons": {{
        "pros": ["...", "..."],
        "cons": ["...", "..."]
    }},
    "best_practices": ["...", "..."],
    "recommendations": ["...", "..."],
    "references": ["...", "..."]
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
                "research_report": result,
                "findings_count": len(result.get("key_findings", [])),
                "recommendations_count": len(result.get("recommendations", [])),
                "has_references": len(result.get("references", [])) > 0
            }
        except json.JSONDecodeError:
            # Fallback: return raw response
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "success": True,
                "research_report": {
                    "executive_summary": response[:500],
                    "detailed_analysis": response,
                    "key_findings": []
                },
                "findings_count": 0,
                "recommendations_count": 0,
                "has_references": False
            }
    
    async def _perform_web_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Perform web search using available APIs or basic scraping
        """
        search_results = {
            "query": query,
            "results": [],
            "sources": [],
            "error": None
        }
        
        try:
            logger.info(f"ResearchAgent: Performing web search for: {query}")
            
            # Try SerpAPI first
            if self.serpapi_key:
                try:
                    async with aiohttp.ClientSession() as session:
                        params = {
                            "q": query,
                            "api_key": self.serpapi_key,
                            "num": num_results
                        }
                        async with session.get("https://serpapi.com/search", params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                if "organic_results" in data:
                                    for result in data["organic_results"][:num_results]:
                                        search_results["results"].append({
                                            "title": result.get("title", ""),
                                            "url": result.get("link", ""),
                                            "snippet": result.get("snippet", ""),
                                            "source": "serpapi"
                                        })
                                    logger.info(f"ResearchAgent: SerpAPI search returned {len(search_results['results'])} results")
                                    return search_results
                except Exception as e:
                    logger.debug(f"SerpAPI search failed: {e}")
            
            # Try Google Custom Search
            if self.google_cse_id and self.google_api_key:
                try:
                    async with aiohttp.ClientSession() as session:
                        params = {
                            "key": self.google_api_key,
                            "cx": self.google_cse_id,
                            "q": query,
                            "num": num_results
                        }
                        async with session.get("https://www.googleapis.com/customsearch/v1", params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                if "items" in data:
                                    for item in data["items"][:num_results]:
                                        search_results["results"].append({
                                            "title": item.get("title", ""),
                                            "url": item.get("link", ""),
                                            "snippet": item.get("snippet", ""),
                                            "source": "google_cse"
                                        })
                                    logger.info(f"ResearchAgent: Google CSE returned {len(search_results['results'])} results")
                                    return search_results
                except Exception as e:
                    logger.debug(f"Google CSE search failed: {e}")
            
            # Fallback: Use web scraper to search via DuckDuckGo or similar
            tool_registry = get_tool_registry()
            web_scraper = tool_registry.get("web_scraper")
            
            if web_scraper:
                # Try DuckDuckGo HTML search
                try:
                    duckduckgo_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
                    result = await web_scraper.execute({"url": duckduckgo_url, "extract_text": True})
                    if result.get("success"):
                        # Basic parsing of DuckDuckGo results (simplified)
                        search_results["results"].append({
                            "title": "DuckDuckGo Search Results",
                            "url": duckduckgo_url,
                            "snippet": result.get("result", {}).get("text_content", "")[:500],
                            "source": "duckduckgo"
                        })
                except Exception as e:
                    logger.debug(f"DuckDuckGo search failed: {e}")
            
            # Extract sources
            search_results["sources"] = [r["source"] for r in search_results["results"]]
            
            logger.info(f"ResearchAgent: Web search completed: {len(search_results['results'])} results")
        
        except Exception as e:
            search_results["error"] = f"Web search failed: {str(e)}"
            logger.error(f"ResearchAgent: Web search failed: {e}", exc_info=True)
        
        return search_results
    
    async def _search_academic_papers(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search for academic papers (arXiv, Google Scholar)
        """
        academic_results = {
            "query": query,
            "papers": [],
            "sources": [],
            "error": None
        }
        
        try:
            logger.info(f"ResearchAgent: Searching academic papers for: {query}")
            
            # Search arXiv
            try:
                async with aiohttp.ClientSession() as session:
                    # arXiv API
                    params = {
                        "search_query": query,
                        "start": 0,
                        "max_results": max_results
                    }
                    async with session.get("http://export.arxiv.org/api/query", params=params) as response:
                        if response.status == 200:
                            import xml.etree.ElementTree as ET
                            content = await response.text()
                            root = ET.fromstring(content)
                            
                            # Parse arXiv entries
                            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                                title = entry.find("{http://www.w3.org/2005/Atom}title")
                                summary = entry.find("{http://www.w3.org/2005/Atom}summary")
                                link = entry.find("{http://www.w3.org/2005/Atom}id")
                                
                                academic_results["papers"].append({
                                    "title": title.text if title is not None else "",
                                    "abstract": summary.text if summary is not None else "",
                                    "url": link.text if link is not None else "",
                                    "source": "arxiv"
                                })
                            
                            academic_results["sources"].append("arxiv")
                            logger.info(f"ResearchAgent: Found {len(academic_results['papers'])} papers from arXiv")
            except Exception as e:
                logger.debug(f"arXiv search failed: {e}")
            
            # Note: Google Scholar requires scraping or paid API
            # For now, we'll use arXiv results
            
            logger.info(f"ResearchAgent: Academic search completed: {len(academic_results['papers'])} papers")
        
        except Exception as e:
            academic_results["error"] = f"Academic paper search failed: {str(e)}"
            logger.error(f"ResearchAgent: Academic paper search failed: {e}", exc_info=True)
        
        return academic_results
    
    async def _analyze_technology_trends(self, technology: str) -> Dict[str, Any]:
        """
        Analyze technology trends using GitHub and web search
        """
        trend_analysis = {
            "technology": technology,
            "trends": [],
            "github_stats": {},
            "adoption_indicators": {},
            "error": None
        }
        
        try:
            logger.info(f"ResearchAgent: Analyzing trends for {technology}")
            
            tool_registry = get_tool_registry()
            github_tool = tool_registry.get("github_api")
            
            # Search GitHub for repositories using this technology
            if github_tool:
                try:
                    # Search for repositories
                    github_result = await github_tool.execute({
                        "endpoint": "search/repositories",
                        "method": "GET",
                        "params": {
                            "q": technology,
                            "sort": "stars",
                            "order": "desc",
                            "per_page": 10
                        }
                    })
                    
                    if github_result.get("success"):
                        repos_data = github_result.get("result", {})
                        items = repos_data.get("items", [])
                        
                        trend_analysis["github_stats"] = {
                            "total_repos": repos_data.get("total_count", 0),
                            "top_repos": [
                                {
                                    "name": item.get("full_name", ""),
                                    "stars": item.get("stargazers_count", 0),
                                    "forks": item.get("forks_count", 0),
                                    "url": item.get("html_url", "")
                                }
                                for item in items[:5]
                            ],
                            "total_stars": sum(item.get("stargazers_count", 0) for item in items)
                        }
                        
                        # Calculate adoption indicators
                        if items:
                            avg_stars = sum(item.get("stargazers_count", 0) for item in items) / len(items)
                            trend_analysis["adoption_indicators"] = {
                                "popularity_score": "High" if avg_stars > 1000 else "Medium" if avg_stars > 100 else "Low",
                                "active_development": len([r for r in items if r.get("updated_at")]) > 0,
                                "community_size": trend_analysis["github_stats"]["total_stars"]
                            }
                except Exception as e:
                    logger.debug(f"GitHub trend analysis failed: {e}")
            
            # Web search for technology trends
            web_search = await self._perform_web_search(f"{technology} trends 2024", num_results=5)
            if web_search.get("results"):
                trend_analysis["trends"] = [
                    {
                        "source": r.get("source", "web"),
                        "title": r.get("title", ""),
                        "snippet": r.get("snippet", "")
                    }
                    for r in web_search["results"]
                ]
            
            logger.info(f"ResearchAgent: Trend analysis completed for {technology}")
        
        except Exception as e:
            trend_analysis["error"] = f"Trend analysis failed: {str(e)}"
            logger.error(f"ResearchAgent: Trend analysis failed: {e}", exc_info=True)
        
        return trend_analysis
    
    async def _perform_competitive_analysis(self, target: str, competitors: List[str] = None) -> Dict[str, Any]:
        """
        Perform competitive analysis
        """
        competitive_analysis = {
            "target": target,
            "competitors": competitors or [],
            "comparison": {},
            "error": None
        }
        
        try:
            logger.info(f"ResearchAgent: Performing competitive analysis for {target}")
            
            # Use web search to gather information about competitors
            all_entities = [target] + (competitors or [])
            
            for entity in all_entities:
                search_results = await self._perform_web_search(f"{entity} features benefits", num_results=3)
                competitive_analysis["comparison"][entity] = {
                    "search_results": search_results.get("results", []),
                    "sources": search_results.get("sources", [])
                }
            
            logger.info(f"ResearchAgent: Competitive analysis completed")
        
        except Exception as e:
            competitive_analysis["error"] = f"Competitive analysis failed: {str(e)}"
            logger.error(f"ResearchAgent: Competitive analysis failed: {e}", exc_info=True)
        
        return competitive_analysis
    
    async def execute(
        self,
        task_id: str,
        target: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute enhanced research with web search and academic paper search
        Overrides BaseAgent.execute to add comprehensive research capabilities
        """
        execution_start = time.time()
        
        try:
            logger.info(f"ResearchAgent: Starting enhanced research for {target}")
            
            research_topic = parameters.get("research_topic", target)
            research_type = parameters.get("research_type", "technology_evaluation")
            
            # STEP 1: Perform web search
            web_search_data = {}
            if parameters.get("web_search", True):
                web_search_data = await self._perform_web_search(research_topic, num_results=10)
            
            # STEP 2: Search academic papers (if requested)
            academic_data = {}
            if parameters.get("academic_search", False):
                academic_data = await self._search_academic_papers(research_topic, max_results=5)
            
            # STEP 3: Analyze technology trends (if technology research)
            trend_data = {}
            if research_type == "technology_evaluation" and parameters.get("trend_analysis", True):
                trend_data = await self._analyze_technology_trends(research_topic)
            
            # STEP 4: Competitive analysis (if requested)
            competitive_data = {}
            competitors = parameters.get("competitors")
            if competitors:
                competitive_data = await self._perform_competitive_analysis(research_topic, competitors)
            
            # STEP 5: Prepare enhanced prompt
            prompt = await self._prepare_prompt(
                target, parameters, web_search_data, academic_data, trend_data, competitive_data
            )
            
            # STEP 6: Call AI via router
            logger.info(f"ResearchAgent: Calling AI with research data")
            
            ai_response = await self.ai_router.generate_with_fallback(
                prompt=prompt,
                model_preference=self.model_preference,
                max_tokens=4000,
                temperature=0.3,
                system_prompt=self.system_prompt,
                strategy=self.strategy
            )
            
            logger.info(f"ResearchAgent: Got response from {ai_response.provider} "
                       f"({ai_response.tokens_used} tokens, ${ai_response.cost_usd:.4f})")
            
            # STEP 7: Parse response
            parsed_result = await self._parse_response(ai_response.content)
            
            # STEP 8: Merge research data with AI results
            if parsed_result.get("success") and parsed_result.get("research_report"):
                research_report = parsed_result["research_report"]
                
                # Add web search results
                if web_search_data:
                    research_report["web_sources"] = web_search_data.get("results", [])
                
                # Add academic papers
                if academic_data:
                    research_report["academic_sources"] = academic_data.get("papers", [])
                
                # Add trend analysis
                if trend_data:
                    research_report["trend_analysis"] = trend_data
                
                # Add competitive analysis
                if competitive_data:
                    research_report["competitive_analysis"] = competitive_data
                
                # Enhance references
                references = research_report.get("references", [])
                if web_search_data.get("results"):
                    for result in web_search_data["results"][:5]:
                        references.append({
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "source": result.get("source", "web_search")
                        })
                if academic_data.get("papers"):
                    for paper in academic_data["papers"]:
                        references.append({
                            "title": paper.get("title", ""),
                            "url": paper.get("url", ""),
                            "source": "academic"
                        })
                research_report["references"] = references
            
            execution_duration = time.time() - execution_start
            
            # Update stats
            self.executions += 1
            self.successes += 1
            self.total_duration += execution_duration
            
            return {
                "success": parsed_result.get("success", True),
                "result": parsed_result.get("research_report", {}),
                "output": parsed_result.get("research_report", {}),
                "quality_score": 0.8,
                "duration": execution_duration,
                "tokens_used": ai_response.tokens_used,
                "cost_usd": ai_response.cost_usd,
                "provider": ai_response.provider,
                "summary": parsed_result.get("research_report", {}).get("executive_summary", "Research completed")
            }
        
        except Exception as e:
            execution_duration = time.time() - execution_start
            logger.error(f"ResearchAgent: Execution failed: {e}", exc_info=True)
            
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
        web_search_data: Dict[str, Any] = None,
        academic_data: Dict[str, Any] = None,
        trend_data: Dict[str, Any] = None,
        competitive_data: Dict[str, Any] = None
    ) -> str:
        """Prepare enhanced research prompt with all collected data"""
        
        research_topic = parameters.get("research_topic", target)
        research_type = parameters.get("research_type", "technology_evaluation")
        scope = parameters.get("scope", "comprehensive")
        sources = parameters.get("sources", [])
        
        # Build context from collected data
        research_context = ""
        
        if web_search_data:
            research_context += f"\n=== WEB SEARCH RESULTS ===\n"
            research_context += f"Results Found: {len(web_search_data.get('results', []))}\n"
            for i, result in enumerate(web_search_data.get("results", [])[:5], 1):
                research_context += f"\n{i}. {result.get('title', 'N/A')}\n"
                research_context += f"   URL: {result.get('url', 'N/A')}\n"
                research_context += f"   Snippet: {result.get('snippet', '')[:200]}...\n"
        
        if academic_data:
            research_context += f"\n=== ACADEMIC PAPERS ===\n"
            research_context += f"Papers Found: {len(academic_data.get('papers', []))}\n"
            for i, paper in enumerate(academic_data.get("papers", [])[:3], 1):
                research_context += f"\n{i}. {paper.get('title', 'N/A')}\n"
                research_context += f"   Abstract: {paper.get('abstract', '')[:200]}...\n"
                research_context += f"   Source: {paper.get('source', 'N/A')}\n"
        
        if trend_data:
            research_context += f"\n=== TECHNOLOGY TRENDS ===\n"
            if trend_data.get("github_stats"):
                github = trend_data["github_stats"]
                research_context += f"GitHub Repositories: {github.get('total_repos', 0)}\n"
                research_context += f"Total Stars: {github.get('total_stars', 0)}\n"
            if trend_data.get("adoption_indicators"):
                indicators = trend_data["adoption_indicators"]
                research_context += f"Popularity: {indicators.get('popularity_score', 'Unknown')}\n"
        
        if competitive_data:
            research_context += f"\n=== COMPETITIVE ANALYSIS ===\n"
            research_context += f"Competitors Analyzed: {len(competitive_data.get('comparison', {}))}\n"
        
        prompt = f"""Conduct comprehensive research on: {research_topic}

Research Type: {research_type}
Scope: {scope}

{research_context}

Additional Sources to Consider:
{json.dumps(sources, indent=2) if sources else "Use the search results and academic papers provided above"}

Based on the REAL RESEARCH DATA collected above (web search results, academic papers, trend analysis), please provide:
1. Executive summary (synthesize findings from all sources)
2. Key findings (reference specific sources)
3. Detailed analysis (use data from web search and academic papers)
4. Pros and cons evaluation (based on research data)
5. Best practices identified (from sources)
6. Recommendations (evidence-based from research)
7. References and sources (include all sources used)

IMPORTANT: 
- Reference specific sources from the web search results and academic papers provided
- Cite sources when making claims
- Use trend analysis data for technology evaluation
- Include competitive analysis findings if provided

Format your response as JSON with the following structure:
{{
    "executive_summary": "...",
    "key_findings": [
        {{
            "finding": "...",
            "source": "Reference to specific source",
            "confidence": "High|Medium|Low"
        }}
    ],
    "detailed_analysis": "...",
    "pros_cons": {{
        "pros": ["...", "..."],
        "cons": ["...", "..."]
    }},
    "best_practices": ["...", "..."],
    "recommendations": [
        {{
            "recommendation": "...",
            "evidence": "Reference to source",
            "priority": "High|Medium|Low"
        }}
    ],
    "references": [
        {{
            "title": "...",
            "url": "...",
            "source": "..."
        }}
    ],
    "trends": {trend_data.get('trends', []) if trend_data else []}
}}"""
        
        return prompt

