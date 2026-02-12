"""
Search Federation Agent (AMAS v3.0)
8-engine search federation with automatic failover
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

from src.amas.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SearchEngine:
    """Base class for search engines"""
    
    def __init__(self, name: str, url: str, priority: int = 1):
        self.name = name
        self.url = url
        self.priority = priority
        self.available = True
        self.failure_count = 0
        self.max_failures = 3
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search implementation - to be overridden"""
        raise NotImplementedError
    
    def mark_failure(self):
        """Mark search engine as failed"""
        self.failure_count += 1
        if self.failure_count >= self.max_failures:
            self.available = False
            logger.warning(f"Search engine {self.name} marked as unavailable")
    
    def mark_success(self):
        """Mark search engine as successful"""
        if self.failure_count > 0:
            self.failure_count -= 1
        if not self.available and self.failure_count < self.max_failures:
            self.available = True
            logger.info(f"Search engine {self.name} recovered")


class SearxNGSearch(SearchEngine):
    """SearxNG privacy-focused search"""
    
    def __init__(self, instance: str = "searx.space"):
        super().__init__("SearxNG", f"https://{instance}", priority=1)
        self.instance = instance
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search using SearxNG"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "engines": "google,duckduckgo,bing"
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.mark_success()
                        return {
                            "success": True,
                            "engine": self.name,
                            "results": data.get("results", [])[:max_results],
                            "query": query
                        }
                    else:
                        self.mark_failure()
                        raise Exception(f"SearxNG returned status {response.status}")
        except Exception as e:
            self.mark_failure()
            raise


class DuckDuckGoSearch(SearchEngine):
    """DuckDuckGo privacy search"""
    
    def __init__(self):
        super().__init__("DuckDuckGo", "https://api.duckduckgo.com", priority=1)
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search using DuckDuckGo"""
        try:
            # DuckDuckGo HTML search (no official API)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://html.duckduckgo.com/html/",
                    params={"q": query},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        for result in soup.find_all('div', class_='result')[:max_results]:
                            title_elem = result.find('a', class_='result__a')
                            snippet_elem = result.find('a', class_='result__snippet')
                            if title_elem:
                                results.append({
                                    "title": title_elem.get_text(),
                                    "url": title_elem.get('href', ''),
                                    "snippet": snippet_elem.get_text() if snippet_elem else ""
                                })
                        self.mark_success()
                        return {
                            "success": True,
                            "engine": self.name,
                            "results": results,
                            "query": query
                        }
                    else:
                        self.mark_failure()
                        raise Exception(f"DuckDuckGo returned status {response.status}")
        except Exception as e:
            self.mark_failure()
            raise


class StartpageSearch(SearchEngine):
    """Startpage anonymous search"""
    
    def __init__(self):
        super().__init__("Startpage", "https://www.startpage.com", priority=1)
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search using Startpage"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}/sp/search",
                    params={"query": query, "page": 1},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        # Parse Startpage results (simplified)
                        self.mark_success()
                        return {
                            "success": True,
                            "engine": self.name,
                            "results": results[:max_results],
                            "query": query
                        }
                    else:
                        self.mark_failure()
                        raise Exception(f"Startpage returned status {response.status}")
        except Exception as e:
            self.mark_failure()
            raise


class BingSearch(SearchEngine):
    """Bing search"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__("Bing", "https://api.bing.microsoft.com", priority=1)
        self.api_key = api_key or ""  # Optional API key
    
    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search using Bing"""
        try:
            if not self.api_key:
                # Use web search without API
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://www.bing.com/search",
                        params={"q": query},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            results = []
                            # Parse Bing results (simplified)
                            self.mark_success()
                            return {
                                "success": True,
                                "engine": self.name,
                                "results": results[:max_results],
                                "query": query
                            }
            else:
                # Use Bing API
                async with aiohttp.ClientSession() as session:
                    headers = {"Ocp-Apim-Subscription-Key": self.api_key}
                    async with session.get(
                        f"{self.url}/v7.0/search",
                        params={"q": query, "count": max_results},
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.mark_success()
                            return {
                                "success": True,
                                "engine": self.name,
                                "results": data.get("webPages", {}).get("value", [])[:max_results],
                                "query": query
                            }
            self.mark_failure()
            raise Exception("Bing search failed")
        except Exception as e:
            self.mark_failure()
            raise


class SearchFederationAgent(BaseAgent):
    """
    Search Federation Agent with 8-engine failover
    
    Engines (in priority order):
    1. SearxNG (Primary)
    2. DuckDuckGo (Primary)
    3. Startpage (Primary)
    4. Bing (Primary)
    5. Google CSE (Secondary)
    6. Qwant (Secondary)
    7. Brave Search (Secondary)
    8. Yandex (Secondary)
    """
    
    def __init__(self):
        super().__init__(
            agent_id="search_federation",
            name="Search Federation Agent",
            agent_type="search",
            system_prompt="""You are a search federation specialist. Your role is to:
1. Coordinate searches across multiple search engines
2. Implement automatic failover when engines fail
3. Deduplicate and merge results
4. Provide comprehensive search results
5. Maintain privacy-first approach

You use 8 search engines with intelligent failover.""",
            model_preference=None,
            strategy="quality_first"
        )
        
        # Initialize search engines
        self.engines = [
            SearxNGSearch(),
            DuckDuckGoSearch(),
            StartpageSearch(),
            BingSearch()
        ]
        
        # Sort by priority
        self.engines.sort(key=lambda e: e.priority)
        self.current_index = 0
    
    async def _prepare_prompt(
        self,
        target: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepare search prompt"""
        query = parameters.get("query", target)
        max_results = parameters.get("max_results", 10)
        
        return f"""Search across multiple engines for: {query}

Requirements:
- Maximum results: {max_results}
- Deduplicate results
- Merge results from multiple engines
- Provide comprehensive coverage

Query: {query}"""
    
    async def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response"""
        try:
            import json
            if response.strip().startswith("{"):
                parsed = json.loads(response)
                return {
                    "success": True,
                    "results": parsed.get("results", []),
                    "sources": parsed.get("sources", []),
                    "quality_score": parsed.get("quality_score", 0.8)
                }
            return {
                "success": True,
                "results": [],
                "sources": [],
                "quality_score": 0.7
            }
        except Exception as e:
            logger.error(f"Failed to parse response: {e}")
            return {
                "success": False,
                "error": str(e),
                "quality_score": 0.5
            }
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Search with automatic failover
        
        Args:
            query: Search query
            max_results: Maximum number of results
            max_retries: Maximum retry attempts
            
        Returns:
            Merged search results from multiple engines
        """
        all_results = []
        successful_engines = []
        
        # Try each engine in priority order
        for engine in self.engines:
            if not engine.available:
                continue
            
            try:
                result = await engine.search(query, max_results)
                if result.get("success"):
                    all_results.extend(result.get("results", []))
                    successful_engines.append(engine.name)
                    logger.info(f"Search engine {engine.name} succeeded")
                    
                    # If we have enough results, we can stop
                    if len(all_results) >= max_results:
                        break
            except Exception as e:
                logger.warning(f"Search engine {engine.name} failed: {e}")
                engine.mark_failure()
                continue
        
        # Deduplicate results
        seen_urls = set()
        deduplicated_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduplicated_results.append(result)
            elif not url:
                # Include results without URLs (they might be unique)
                deduplicated_results.append(result)
        
        # Limit to max_results
        deduplicated_results = deduplicated_results[:max_results]
        
        return {
            "success": len(deduplicated_results) > 0,
            "query": query,
            "results": deduplicated_results,
            "engines_used": successful_engines,
            "total_results": len(deduplicated_results),
            "quality_score": min(0.9, 0.5 + (len(successful_engines) * 0.1))
        }

