"""
Enhanced Security middleware for AMAS
Implements comprehensive security headers, input validation, and sanitization
"""

import re
import html
import json
import logging
from typing import Callable, Dict, List, Optional, Any
from urllib.parse import unquote

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import ValidationError

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware for comprehensive security protection"""

    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        
        # Dangerous patterns for input validation
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'vbscript:',  # VBScript URLs
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>',  # Iframe tags
            r'<object[^>]*>',  # Object tags
            r'<embed[^>]*>',  # Embed tags
            r'<form[^>]*>',  # Form tags
            r'<input[^>]*>',  # Input tags
            r'<textarea[^>]*>',  # Textarea tags
            r'<select[^>]*>',  # Select tags
            r'<option[^>]*>',  # Option tags
            r'<link[^>]*>',  # Link tags
            r'<meta[^>]*>',  # Meta tags
            r'<style[^>]*>',  # Style tags
            r'<link[^>]*>',  # Link tags
            r'<base[^>]*>',  # Base tags
            r'<applet[^>]*>',  # Applet tags
            r'<param[^>]*>',  # Param tags
            r'<source[^>]*>',  # Source tags
            r'<track[^>]*>',  # Track tags
            r'<video[^>]*>',  # Video tags
            r'<audio[^>]*>',  # Audio tags
            r'<canvas[^>]*>',  # Canvas tags
            r'<svg[^>]*>',  # SVG tags
            r'<math[^>]*>',  # Math tags
            r'<details[^>]*>',  # Details tags
            r'<summary[^>]*>',  # Summary tags
            r'<dialog[^>]*>',  # Dialog tags
            r'<menu[^>]*>',  # Menu tags
            r'<menuitem[^>]*>',  # Menuitem tags
            r'<command[^>]*>',  # Command tags
            r'<keygen[^>]*>',  # Keygen tags
            r'<output[^>]*>',  # Output tags
            r'<progress[^>]*>',  # Progress tags
            r'<meter[^>]*>',  # Meter tags
            r'<datalist[^>]*>',  # Datalist tags
            r'<fieldset[^>]*>',  # Fieldset tags
            r'<legend[^>]*>',  # Legend tags
            r'<label[^>]*>',  # Label tags
            r'<button[^>]*>',  # Button tags
            r'<optgroup[^>]*>',  # Optgroup tags
            r'<colgroup[^>]*>',  # Colgroup tags
            r'<col[^>]*>',  # Col tags
            r'<thead[^>]*>',  # Thead tags
            r'<tbody[^>]*>',  # Tbody tags
            r'<tfoot[^>]*>',  # Tfoot tags
            r'<tr[^>]*>',  # Tr tags
            r'<td[^>]*>',  # Td tags
            r'<th[^>]*>',  # Th tags
            r'<table[^>]*>',  # Table tags
            r'<caption[^>]*>',  # Caption tags
            r'<div[^>]*>',  # Div tags
            r'<span[^>]*>',  # Span tags
            r'<p[^>]*>',  # P tags
            r'<h[1-6][^>]*>',  # Heading tags
            r'<ul[^>]*>',  # Ul tags
            r'<ol[^>]*>',  # Ol tags
            r'<li[^>]*>',  # Li tags
            r'<dl[^>]*>',  # Dl tags
            r'<dt[^>]*>',  # Dt tags
            r'<dd[^>]*>',  # Dd tags
            r'<blockquote[^>]*>',  # Blockquote tags
            r'<q[^>]*>',  # Q tags
            r'<cite[^>]*>',  # Cite tags
            r'<code[^>]*>',  # Code tags
            r'<pre[^>]*>',  # Pre tags
            r'<kbd[^>]*>',  # Kbd tags
            r'<samp[^>]*>',  # Samp tags
            r'<var[^>]*>',  # Var tags
            r'<sub[^>]*>',  # Sub tags
            r'<sup[^>]*>',  # Sup tags
            r'<del[^>]*>',  # Del tags
            r'<ins[^>]*>',  # Ins tags
            r'<mark[^>]*>',  # Mark tags
            r'<small[^>]*>',  # Small tags
            r'<strong[^>]*>',  # Strong tags
            r'<em[^>]*>',  # Em tags
            r'<b[^>]*>',  # B tags
            r'<i[^>]*>',  # I tags
            r'<u[^>]*>',  # U tags
            r'<s[^>]*>',  # S tags
            r'<strike[^>]*>',  # Strike tags
            r'<big[^>]*>',  # Big tags
            r'<tt[^>]*>',  # Tt tags
            r'<font[^>]*>',  # Font tags
            r'<center[^>]*>',  # Center tags
            r'<marquee[^>]*>',  # Marquee tags
            r'<blink[^>]*>',  # Blink tags
            r'<nobr[^>]*>',  # Nobr tags
            r'<wbr[^>]*>',  # Wbr tags
            r'<br[^>]*>',  # Br tags
            r'<hr[^>]*>',  # Hr tags
            r'<img[^>]*>',  # Img tags
            r'<area[^>]*>',  # Area tags
            r'<map[^>]*>',  # Map tags
            r'<a[^>]*>',  # Anchor tags
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.dangerous_patterns]

    def _sanitize_input(self, value: str) -> str:
        """Sanitize input by removing dangerous patterns and HTML encoding"""
        if not isinstance(value, str):
            return value
        
        # HTML encode special characters
        sanitized = html.escape(value, quote=True)
        
        # Remove dangerous patterns
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub('', sanitized)
        
        # Remove null bytes and control characters
        sanitized = sanitized.replace('\x00', '')
        sanitized = re.sub(r'[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        return sanitized

    def _validate_json_input(self, body: bytes) -> Optional[Dict[str, Any]]:
        """Validate and sanitize JSON input"""
        try:
            data = json.loads(body.decode('utf-8'))
            return self._sanitize_json_data(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Invalid JSON input: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON format")

    def _sanitize_json_data(self, data: Any) -> Any:
        """Recursively sanitize JSON data"""
        if isinstance(data, dict):
            return {key: self._sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            return self._sanitize_input(data)
        else:
            return data

    def _validate_query_params(self, query_params: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Validate and sanitize query parameters"""
        sanitized = {}
        for key, values in query_params.items():
            sanitized_key = self._sanitize_input(key)
            sanitized_values = [self._sanitize_input(value) for value in values]
            sanitized[sanitized_key] = sanitized_values
        return sanitized

    def _validate_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Validate and sanitize headers"""
        sanitized = {}
        for key, value in headers.items():
            sanitized_key = self._sanitize_input(key)
            sanitized_value = self._sanitize_input(value)
            sanitized[sanitized_key] = sanitized_value
        return sanitized

    def _add_security_headers(self, response: Response) -> None:
        """Add comprehensive security headers"""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS (HTTP Strict Transport Security)
        if self.settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "bluetooth=(), "
            "clipboard-read=(), "
            "clipboard-write=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(), "
            "gamepad=(), "
            "layout-animations=(), "
            "legacy-image-formats=(), "
            "midi=(), "
            "notifications=(), "
            "oversized-images=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "unoptimized-images=(), "
            "unsized-media=(), "
            "vibrate=(), "
            "wake-lock=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "media-src 'self'; "
            "object-src 'none'; "
            "child-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'; "
            "manifest-src 'self'; "
            "worker-src 'self'; "
            "frame-src 'none'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Add custom security header
        response.headers["X-AMAS-Security"] = "enabled"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive security checks"""
        try:
            # Validate and sanitize query parameters
            if request.query_params:
                sanitized_params = self._validate_query_params(dict(request.query_params))
                # Note: FastAPI doesn't allow direct modification of query_params
                # This is a limitation, but we log suspicious parameters
                for key, values in sanitized_params.items():
                    if any(pattern.search(value) for pattern in self.compiled_patterns for value in values):
                        logger.warning(f"Suspicious query parameter detected: {key}={values}")
            
            # Validate and sanitize headers
            sanitized_headers = self._validate_headers(dict(request.headers))
            for key, value in sanitized_headers.items():
                if any(pattern.search(value) for pattern in self.compiled_patterns):
                    logger.warning(f"Suspicious header detected: {key}={value}")
            
            # Validate request body for JSON requests
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    body = await request.body()
                    if body:
                        try:
                            self._validate_json_input(body)
                        except HTTPException:
                            raise
                        except Exception as e:
                            logger.warning(f"JSON validation error: {e}")
                            raise HTTPException(status_code=400, detail="Invalid request data")
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            self._add_security_headers(response)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
