"""
Search Engine Tools
Implementations for multiple search engines: SearxNG, DuckDuckGo, Startpage, Bing, etc.
"""

import logging
import os
from typing import Any, Dict, List, Optional
import aiohttp
from bs4 import BeautifulSoup

from . import AgentTool

logger = logging.getLogger(__name__)


class SearxNGTool(AgentTool):
    """SearxNG privacy-focused meta-search engine"""
    
    def __init__(self):
        super().__init__(
            name="searxng",
            description="Privacy-focused meta-search engine aggregator"
        )
        self.category = "web_research"
        self.base_url = os.getenv("SEARXNG_URL", "https://searx.space")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10, "description": "Maximum results"}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SearxNG search"""
        try:
            query = params.get("query")
            max_results = params.get("max_results", 10)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/search",
                    params={"q": query, "format": "json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])[:max_results]
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"SearxNG search failed: {e}")
            return {"success": False, "error": str(e)}


class DuckDuckGoTool(AgentTool):
    """DuckDuckGo privacy-first search engine"""
    
    def __init__(self):
        super().__init__(
            name="duckduckgo",
            description="Privacy-first search engine"
        )
        self.category = "web_research"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DuckDuckGo search"""
        try:
            query = params.get("query")
            # Use DuckDuckGo API if available, otherwise HTML
            # Try API first (no key required for basic searches)
            api_url = "https://api.duckduckgo.com/"
            
            async with aiohttp.ClientSession() as session:
                # Try API first
                try:
                    async with session.get(
                        api_url,
                        params={"q": query, "format": "json", "no_html": "1"},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as api_response:
                        if api_response.status == 200:
                            data = await api_response.json()
                            results = []
                            for item in data.get("RelatedTopics", [])[:params.get("max_results", 10)]:
                                if isinstance(item, dict) and "Text" in item:
                                    results.append({
                                        "title": item.get("Text", ""),
                                        "url": item.get("FirstURL", ""),
                                        "snippet": item.get("Text", "")
                                    })
                            if results:
                                return {
                                    "success": True,
                                    "result": {
                                        "query": query,
                                        "results": results,
                                        "count": len(results)
                                    }
                                }
                except Exception:
                    pass  # Fall back to HTML
                
                # Fallback to HTML search
                url = f"https://html.duckduckgo.com/html/?q={query}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        
                        # Try multiple selectors for DuckDuckGo HTML
                        selectors = [
                            ('div', 'result'),
                            ('div', 'web-result'),
                            ('a', 'result__a'),
                        ]
                        
                        for selector_type, selector_class in selectors:
                            elements = soup.find_all(selector_type, class_=selector_class)
                            if elements:
                                for result in elements[:params.get("max_results", 10)]:
                                    title_elem = result.find('a') if selector_type == 'div' else result
                                    if title_elem:
                                        title = title_elem.get_text(strip=True)
                                        url = title_elem.get('href', '')
                                        snippet_elem = result.find('a', class_='result__snippet') or result.find('span')
                                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                                        
                                        if title:
                                            results.append({
                                                "title": title,
                                                "url": url,
                                                "snippet": snippet
                                            })
                                break
                        
                        if results:
                            return {
                                "success": True,
                                "result": {
                                    "query": query,
                                    "results": results,
                                    "count": len(results)
                                }
                            }
                        else:
                            # Return minimal success if we got HTML but couldn't parse
                            return {
                                "success": True,
                                "result": {
                                    "query": query,
                                    "results": [],
                                    "count": 0,
                                    "message": "Search executed but no results parsed (HTML structure may have changed)"
                                }
                            }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except aiohttp.ClientError as e:
            logger.error(f"DuckDuckGo search network error: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return {"success": False, "error": str(e)}


class StartpageTool(AgentTool):
    """Startpage anonymous search frontend"""
    
    def __init__(self):
        super().__init__(
            name="startpage",
            description="Anonymous search frontend"
        )
        self.category = "web_research"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Startpage search"""
        try:
            query = params.get("query")
            url = f"https://www.startpage.com/sp/search?query={query}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        
                        for result in soup.find_all('div', class_='w-gl__result')[:params.get("max_results", 10)]:
                            title_elem = result.find('h3')
                            link_elem = result.find('a')
                            snippet_elem = result.find('p', class_='w-gl__description')
                            
                            if title_elem and link_elem:
                                results.append({
                                    "title": title_elem.get_text(strip=True),
                                    "url": link_elem.get('href', ''),
                                    "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                                })
                        
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except aiohttp.ClientError as e:
            logger.error(f"Startpage search network error: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Startpage search failed: {e}")
            return {"success": False, "error": str(e)}


class BingSearchTool(AgentTool):
    """Bing search engine"""
    
    def __init__(self):
        super().__init__(
            name="bing",
            description="Comprehensive web search"
        )
        self.category = "web_research"
        self.api_key = os.getenv("BING_API_KEY")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Bing search"""
        try:
            query = params.get("query")
            
            # Use Bing HTML search if no API key
            if not self.api_key:
                url = f"https://www.bing.com/search?q={query}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            results = []
                            
                            for result in soup.find_all('li', class_='b_algo')[:params.get("max_results", 10)]:
                                title_elem = result.find('h2')
                                link_elem = result.find('a')
                                snippet_elem = result.find('p')
                                
                                if title_elem and link_elem:
                                    results.append({
                                        "title": title_elem.get_text(strip=True),
                                        "url": link_elem.get('href', ''),
                                        "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                                    })
                            
                            return {
                                "success": True,
                                "result": {
                                    "query": query,
                                    "results": results,
                                    "count": len(results)
                                }
                            }
                return {"success": False, "error": "No API key and HTML parsing failed"}
            
            # Use Bing API if available
            api_url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    api_url,
                    params={"q": query, "count": params.get("max_results", 10)},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = [
                            {
                                "title": r.get("name", ""),
                                "url": r.get("url", ""),
                                "snippet": r.get("snippet", "")
                            }
                            for r in data.get("webPages", {}).get("value", [])
                        ]
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"API returned {response.status}"}
        except Exception as e:
            logger.error(f"Bing search failed: {e}")
            return {"success": False, "error": str(e)}


class GoogleCSETool(AgentTool):
    """Google Custom Search Engine"""
    
    def __init__(self):
        super().__init__(
            name="google_cse",
            description="Google Custom Search Engine (100 queries/day free)"
        )
        self.category = "web_research"
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google CSE search"""
        try:
            if not self.api_key or not self.cse_id:
                return {"success": False, "error": "Google API key and CSE ID required"}
            
            query = params.get("query")
            url = "https://www.googleapis.com/customsearch/v1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params={
                        "key": self.api_key,
                        "cx": self.cse_id,
                        "q": query,
                        "num": min(params.get("max_results", 10), 10)
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("link", ""),
                                "snippet": r.get("snippet", "")
                            }
                            for r in data.get("items", [])
                        ]
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"API returned {response.status}"}
        except Exception as e:
            logger.error(f"Google CSE search failed: {e}")
            return {"success": False, "error": str(e)}


class QwantTool(AgentTool):
    """Qwant EU-friendly privacy search"""
    
    def __init__(self):
        super().__init__(
            name="qwant",
            description="EU-friendly privacy search"
        )
        self.category = "web_research"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Qwant search"""
        try:
            query = params.get("query")
            url = f"https://www.qwant.com/?q={query}&t=web"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        
                        for result in soup.find_all('div', class_='result')[:params.get("max_results", 10)]:
                            title_elem = result.find('a', class_='result-title')
                            snippet_elem = result.find('p', class_='result-description')
                            
                            if title_elem:
                                results.append({
                                    "title": title_elem.get_text(strip=True),
                                    "url": title_elem.get('href', ''),
                                    "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                                })
                        
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except aiohttp.ClientError as e:
            logger.error(f"Qwant search network error: {e}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Qwant search failed: {e}")
            return {"success": False, "error": str(e)}


class BraveSearchTool(AgentTool):
    """Brave Search privacy-first search"""
    
    def __init__(self):
        super().__init__(
            name="brave_search",
            description="Privacy-first search with free API"
        )
        self.category = "web_research"
        self.api_key = os.getenv("BRAVE_API_KEY")
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Brave search"""
        try:
            if not self.api_key:
                return {"success": False, "error": "Brave API key required"}
            
            query = params.get("query")
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {"X-Subscription-Token": self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params={"q": query, "count": params.get("max_results", 10)},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("url", ""),
                                "snippet": r.get("description", "")
                            }
                            for r in data.get("web", {}).get("results", [])
                        ]
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"API returned {response.status}"}
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return {"success": False, "error": str(e)}


class YandexTool(AgentTool):
    """Yandex Russian/CIS region search"""
    
    def __init__(self):
        super().__init__(
            name="yandex",
            description="Russian/CIS region search"
        )
        self.category = "web_research"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10}
            },
            "required": ["query"]
        }
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Yandex search"""
        try:
            query = params.get("query")
            url = f"https://yandex.com/search/?text={query}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        results = []
                        
                        for result in soup.find_all('li', class_='serp-item')[:params.get("max_results", 10)]:
                            title_elem = result.find('h2', class_='organic__title-wrapper')
                            link_elem = result.find('a', class_='organic__url')
                            snippet_elem = result.find('div', class_='text-container')
                            
                            if title_elem and link_elem:
                                results.append({
                                    "title": title_elem.get_text(strip=True),
                                    "url": link_elem.get('href', ''),
                                    "snippet": snippet_elem.get_text(strip=True) if snippet_elem else ""
                                })
                        
                        return {
                            "success": True,
                            "result": {
                                "query": query,
                                "results": results,
                                "count": len(results)
                            }
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Yandex search failed: {e}")
            return {"success": False, "error": str(e)}

