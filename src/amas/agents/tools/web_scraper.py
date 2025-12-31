"""
Web Scraper Tool
Tool for scraping web pages and extracting data
"""

import logging
from typing import Any, Dict
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup

from . import AgentTool

logger = logging.getLogger(__name__)


class WebScraperTool(AgentTool):
    """Tool for web scraping"""
    
    def __init__(self):
        super().__init__(
            name="web_scraper",
            description="Scrape web pages and extract HTML content, headers, and metadata"
        )
        self.category = "data_collection"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to scrape"
                },
                "extract_text": {
                    "type": "boolean",
                    "description": "Extract text content",
                    "default": True
                },
                "extract_links": {
                    "type": "boolean",
                    "description": "Extract all links",
                    "default": False
                },
                "extract_metadata": {
                    "type": "boolean",
                    "description": "Extract meta tags",
                    "default": True
                },
                "timeout": {
                    "type": "number",
                    "description": "Request timeout in seconds",
                    "default": 30
                }
            },
            "required": ["url"]
        }
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        if "url" not in params:
            return False
        url = params["url"]
        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            # Try to normalize
            if not url.startswith(('http://', 'https://')):
                params["url"] = f"https://{url}"
        return True
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web scraping"""
        try:
            if not self.validate_params(params):
                return {
                    "success": False,
                    "error": "Invalid parameters: url is required"
                }
            
            url = params["url"]
            extract_text = params.get("extract_text", True)
            extract_links = params.get("extract_links", False)
            extract_metadata = params.get("extract_metadata", True)
            timeout = params.get("timeout", 30)
            
            logger.info(f"WebScraperTool: Scraping {url}")
            
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            result = {
                "url": url,
                "status_code": None,
                "headers": {},
                "html_content": None,
                "text_content": None,
                "links": [],
                "metadata": {},
                "technology_indicators": []
            }
            
            async with aiohttp.ClientSession(timeout=timeout_obj, headers=headers) as session:
                try:
                    async with session.get(url, allow_redirects=True, ssl=False) as response:
                        result["status_code"] = response.status
                        result["headers"] = dict(response.headers)
                        
                        html_content = await response.text()
                        result["html_content"] = html_content
                        
                        # Parse HTML
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Extract text
                        if extract_text:
                            result["text_content"] = soup.get_text(separator=' ', strip=True)
                        
                        # Extract links
                        if extract_links:
                            links = []
                            for link in soup.find_all('a', href=True):
                                href = link['href']
                                absolute_url = urljoin(url, href)
                                links.append({
                                    "text": link.get_text(strip=True),
                                    "url": absolute_url
                                })
                            result["links"] = links
                        
                        # Extract metadata
                        if extract_metadata:
                            metadata = {}
                            # Meta tags
                            for meta in soup.find_all('meta'):
                                name = meta.get('name') or meta.get('property')
                                content = meta.get('content')
                                if name and content:
                                    metadata[name] = content
                            
                            # Title
                            title_tag = soup.find('title')
                            if title_tag:
                                metadata['title'] = title_tag.get_text(strip=True)
                            
                            result["metadata"] = metadata
                        
                        # Technology indicators
                        tech_indicators = []
                        
                        # Check for generator
                        meta_generator = soup.find('meta', attrs={'name': 'generator'})
                        if meta_generator and meta_generator.get('content'):
                            tech_indicators.append(f"Generator: {meta_generator.get('content')}")
                        
                        # Check for frameworks
                        for script in soup.find_all('script', src=True):
                            src = script['src'].lower()
                            if 'jquery' in src:
                                tech_indicators.append("jQuery")
                            elif 'react' in src:
                                tech_indicators.append("React")
                            elif 'angular' in src:
                                tech_indicators.append("Angular")
                            elif 'vue' in src:
                                tech_indicators.append("Vue.js")
                        
                        # Check for WordPress
                        if soup.find('link', href=lambda x: x and '/wp-content/' in x) or \
                           soup.find('script', src=lambda x: x and '/wp-content/' in x):
                            tech_indicators.append("WordPress")
                        
                        # Server header
                        server = result["headers"].get('Server', '')
                        if server:
                            tech_indicators.append(f"Server: {server}")
                        
                        # X-Powered-By
                        powered_by = result["headers"].get('X-Powered-By', '')
                        if powered_by:
                            tech_indicators.append(f"Powered By: {powered_by}")
                        
                        result["technology_indicators"] = list(set(tech_indicators))
                        
                        logger.info(f"WebScraperTool: Successfully scraped {url}, status={response.status}")
                        
                        return {
                            "success": True,
                            "result": result,
                            "metadata": {
                                "url": url,
                                "status_code": response.status,
                                "content_length": len(html_content)
                            }
                        }
                
                except aiohttp.ClientError as e:
                    logger.warning(f"WebScraperTool: HTTP client error for {url}: {e}")
                    return {
                        "success": False,
                        "error": f"HTTP client error: {str(e)}",
                        "result": result
                    }
                except Exception as e:
                    logger.error(f"WebScraperTool: Error scraping {url}: {e}", exc_info=True)
                    return {
                        "success": False,
                        "error": f"Scraping error: {str(e)}",
                        "result": result
                    }
        
        except Exception as e:
            logger.error(f"WebScraperTool: Failed to scrape {params.get('url', 'unknown')}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to scrape: {str(e)}"
            }

