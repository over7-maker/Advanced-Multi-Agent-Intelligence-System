#!/usr/bin/env python3
"""
AI Code Analyzer - Uses multiple AI providers to analyze code quality
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.ai_service_manager import AIProvider, AIServiceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AICodeAnalyzer:
    """AI-powered code analyzer"""

    def __init__(self):
        self.ai_service = None
        self.analysis_results = {}

    async def initialize(self):
        """Initialize the analyzer"""
        try:
            config = {
                "deepseek_api_key": os.getenv("DEEPSEEK_API_KEY"),
                "glm_api_key": os.getenv("GLM_API_KEY"),
                "grok_api_key": os.getenv("GROK_API_KEY"),
                "kimi_api_key": os.getenv("KIMI_API_KEY"),
                "qwen_api_key": os.getenv("QWEN_API_KEY"),
                "gptoss_api_key": os.getenv("GPTOSS_API_KEY"),
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("AI Code Analyzer initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI Code Analyzer: {e}")
            raise

    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_ext = Path(file_path).suffix.lower()
            language = self._get_language_from_extension(file_ext)

            # Get file info
            file_info = {
                "path": file_path,
                "language": language,
                "size": len(content),
                "lines": len(content.splitlines()),
            }

            # Analyze code quality
            quality_analysis = await self._analyze_code_quality(content, language)

            # Analyze security
            security_analysis = await self._analyze_security(content, language)

            # Analyze performance
            performance_analysis = await self._analyze_performance(content, language)

            # Analyze maintainability
            maintainability_analysis = await self._analyze_maintainability(
                content, language
            )

            return {
                "file_info": file_info,
                "quality_analysis": quality_analysis,
                "security_analysis": security_analysis,
                "performance_analysis": performance_analysis,
                "maintainability_analysis": maintainability_analysis,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                "file_info": {"path": file_path, "error": str(e)},
                "timestamp": datetime.now().isoformat(),
            }

    def _get_language_from_extension(self, ext: str) -> str:
        """Get programming language from file extension"""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".r": "r",
            ".m": "matlab",
            ".sh": "bash",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".less": "less",
            ".xml": "xml",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
            ".cfg": "ini",
            ".conf": "ini",
        }
        return language_map.get(ext, "unknown")

    async def _analyze_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code quality using AI"""
        try:
            prompt = f"""Analyze the code quality of this {language} code and provide:
1. Code quality score (1-10)
2. Main issues found
3. Best practices violations
4. Code style issues
5. Specific recommendations for improvement

Code:
```{language}
{code}
```

Provide a detailed analysis with specific examples."""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                return {
                    "analysis": response.content,
                    "provider": response.provider,
                    "response_time": response.response_time,
                }
            else:
                return {"error": response.error, "provider": response.provider}

        except Exception as e:
            logger.error(f"Error in code quality analysis: {e}")
            return {"error": str(e)}

    async def _analyze_security(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze security issues using AI"""
        try:
            prompt = f"""Analyze this {language} code for security vulnerabilities:
1. Security score (1-10)
2. Potential security issues
3. Vulnerabilities found
4. Security best practices violations
5. Recommendations for security improvements

Code:
```{language}
{code}
```

Focus on common security issues like:
- SQL injection
- XSS vulnerabilities
- Authentication/authorization issues
- Input validation problems
- Sensitive data exposure
- Cryptographic issues"""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                return {
                    "analysis": response.content,
                    "provider": response.provider,
                    "response_time": response.response_time,
                }
            else:
                return {"error": response.error, "provider": response.provider}

        except Exception as e:
            logger.error(f"Error in security analysis: {e}")
            return {"error": str(e)}

    async def _analyze_performance(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze performance issues using AI"""
        try:
            prompt = f"""Analyze this {language} code for performance issues:
1. Performance score (1-10)
2. Performance bottlenecks
3. Inefficient algorithms
4. Memory usage issues
5. CPU optimization opportunities
6. Recommendations for performance improvements

Code:
```{language}
{code}
```

Focus on:
- Time complexity
- Space complexity
- Memory leaks
- Inefficient loops
- Unnecessary computations
- Resource management"""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                return {
                    "analysis": response.content,
                    "provider": response.provider,
                    "response_time": response.response_time,
                }
            else:
                return {"error": response.error, "provider": response.provider}

        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return {"error": str(e)}

    async def _analyze_maintainability(
        self, code: str, language: str
    ) -> Dict[str, Any]:
        """Analyze maintainability using AI"""
        try:
            prompt = f"""Analyze this {language} code for maintainability:
1. Maintainability score (1-10)
2. Code readability issues
3. Documentation quality
4. Code organization
5. Complexity issues
6. Recommendations for better maintainability

Code:
```{language}
{code}
```

Focus on:
- Code clarity
- Documentation
- Modularity
- Complexity
- Naming conventions
- Code structure"""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                return {
                    "analysis": response.content,
                    "provider": response.provider,
                    "response_time": response.response_time,
                }
            else:
                return {"error": response.error, "provider": response.provider}

        except Exception as e:
            logger.error(f"Error in maintainability analysis: {e}")
            return {"error": str(e)}

    async def analyze_directory(
        self, directory: str, extensions: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze all files in a directory"""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]

        results = {
            "directory": directory,
            "files_analyzed": 0,
            "analysis_results": [],
            "summary": {},
            "timestamp": datetime.now().isoformat(),
        }

        try:
            directory_path = Path(directory)
            if not directory_path.exists():
                logger.error(f"Directory {directory} does not exist")
                return results

            files = []
            for ext in extensions:
                files.extend(directory_path.rglob(f"*{ext}"))

            logger.info(f"Found {len(files)} files to analyze")

            for file_path in files:
                logger.info(f"Analyzing {file_path}")
                analysis = await self.analyze_file(str(file_path))
                results["analysis_results"].append(analysis)
                results["files_analyzed"] += 1

            # Generate summary
            results["summary"] = await self._generate_summary(
                results["analysis_results"]
            )

        except Exception as e:
            logger.error(f"Error analyzing directory {directory}: {e}")
            results["error"] = str(e)

        return results

    async def _generate_summary(
        self, analysis_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of all analyses"""
        try:
            # Collect all analyses
            all_analyses = []
            for result in analysis_results:
                if (
                    "quality_analysis" in result
                    and "analysis" in result["quality_analysis"]
                ):
                    all_analyses.append(result["quality_analysis"]["analysis"])

            if not all_analyses:
                return {"error": "No analyses available for summary"}

            # Create summary prompt
            summary_prompt = f"""Create a comprehensive summary of code analysis results:

{chr(10).join(all_analyses[:5])}  # Limit to first 5 for token efficiency

Provide:
1. Overall code quality assessment
2. Common issues found across files
3. Priority recommendations
4. General improvement suggestions
5. Risk assessment"""

            response = await self.ai_service.generate_response(summary_prompt)

            if response.success:
                return {
                    "summary": response.content,
                    "provider": response.provider,
                    "total_files": len(analysis_results),
                }
            else:
                return {"error": response.error, "total_files": len(analysis_results)}

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}

    def save_report(self, results: Dict[str, Any], output_file: str):
        """Save analysis report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")

    async def shutdown(self):
        """Shutdown the analyzer"""
        if self.ai_service:
            await self.ai_service.shutdown()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Code Analyzer")
    parser.add_argument(
        "--mode",
        choices=["analysis", "summary"],
        default="analysis",
        help="Analysis mode",
    )
    parser.add_argument("--files", nargs="+", help="Files to analyze")
    parser.add_argument("--directory", help="Directory to analyze")
    parser.add_argument("--output", default="analysis_report.md", help="Output file")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".py", ".js", ".ts"],
        help="File extensions to analyze",
    )

    args = parser.parse_args()

    analyzer = AICodeAnalyzer()

    try:
        await analyzer.initialize()

        if args.files:
            # Analyze specific files
            results = {
                "files_analyzed": 0,
                "analysis_results": [],
                "timestamp": datetime.now().isoformat(),
            }

            for file_path in args.files:
                logger.info(f"Analyzing {file_path}")
                analysis = await analyzer.analyze_file(file_path)
                results["analysis_results"].append(analysis)
                results["files_analyzed"] += 1

            # Generate summary
            results["summary"] = await analyzer._generate_summary(
                results["analysis_results"]
            )

        elif args.directory:
            # Analyze directory
            results = await analyzer.analyze_directory(args.directory, args.extensions)

        else:
            logger.error("Please specify either --files or --directory")
            return

        # Save report
        analyzer.save_report(results, args.output)

        # Print summary
        if "summary" in results and "summary" in results["summary"]:
            print("\n" + "=" * 50)
            print("AI CODE ANALYSIS SUMMARY")
            print("=" * 50)
            print(results["summary"]["summary"])
            print("=" * 50)

        logger.info(f"Analysis complete. {results['files_analyzed']} files analyzed.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await analyzer.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
