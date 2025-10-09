#!/usr/bin/env python3
"""
AI Code Improver - Uses multiple AI providers to improve code quality
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


class AICodeImprover:
    """AI-powered code improver"""

    def __init__(self):
        self.ai_service = None
        self.improvements = {}

    async def initialize(self):
        """Initialize the improver"""
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
            logger.info("AI Code Improver initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI Code Improver: {e}")
            raise

    async def improve_file(
        self, file_path: str, improvement_type: str = "general"
    ) -> Dict[str, Any]:
        """Improve a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            file_ext = Path(file_path).suffix.lower()
            language = self._get_language_from_extension(file_ext)

            # Get file info
            file_info = {
                "path": file_path,
                "language": language,
                "original_size": len(original_content),
                "original_lines": len(original_content.splitlines()),
            }

            # Generate improved code
            improved_response = await self.ai_service.improve_code(
                original_content, language, improvement_type
            )

            if not improved_response.success:
                return {
                    "file_info": file_info,
                    "error": improved_response.error,
                    "timestamp": datetime.now().isoformat(),
                }

            # Extract improved code from response
            improved_content = self._extract_code_from_response(
                improved_response.content, language
            )

            # Generate analysis of improvements
            analysis_response = await self.ai_service.analyze_code(
                improved_content, language
            )

            return {
                "file_info": file_info,
                "original_content": original_content,
                "improved_content": improved_content,
                "improvement_analysis": (
                    analysis_response.content
                    if analysis_response.success
                    else analysis_response.error
                ),
                "improvement_type": improvement_type,
                "provider_used": improved_response.provider,
                "response_time": improved_response.response_time,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error improving file {file_path}: {e}")
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

    def _extract_code_from_response(self, response_content: str, language: str) -> str:
        """Extract code from AI response"""
        try:
            # Look for code blocks
            if f"```{language}" in response_content:
                start = response_content.find(f"```{language}") + len(f"```{language}")
                end = response_content.find("```", start)
                if end != -1:
                    return response_content[start:end].strip()

            # Look for generic code blocks
            if "```" in response_content:
                start = response_content.find("```") + 3
                end = response_content.find("```", start)
                if end != -1:
                    return response_content[start:end].strip()

            # Return the whole response if no code blocks found
            return response_content.strip()

        except Exception as e:
            logger.warning(f"Error extracting code: {e}")
            return response_content

    async def improve_directory(
        self,
        directory: str,
        output_dir: str,
        improvement_type: str = "general",
        extensions: List[str] = None,
    ) -> Dict[str, Any]:
        """Improve all files in a directory"""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]

        results = {
            "directory": directory,
            "output_directory": output_dir,
            "files_improved": 0,
            "improvements": [],
            "summary": {},
            "timestamp": datetime.now().isoformat(),
        }

        try:
            directory_path = Path(directory)
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            if not directory_path.exists():
                logger.error(f"Directory {directory} does not exist")
                return results

            files = []
            for ext in extensions:
                files.extend(directory_path.rglob(f"*{ext}"))

            logger.info(f"Found {len(files)} files to improve")

            for file_path in files:
                logger.info(f"Improving {file_path}")
                improvement = await self.improve_file(str(file_path), improvement_type)
                results["improvements"].append(improvement)

                if "improved_content" in improvement:
                    # Save improved file
                    relative_path = file_path.relative_to(directory_path)
                    output_file = output_path / relative_path
                    output_file.parent.mkdir(parents=True, exist_ok=True)

                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(improvement["improved_content"])

                    results["files_improved"] += 1

            # Generate summary
            results["summary"] = await self._generate_improvement_summary(
                results["improvements"]
            )

        except Exception as e:
            logger.error(f"Error improving directory {directory}: {e}")
            results["error"] = str(e)

        return results

    async def _generate_improvement_summary(
        self, improvements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate summary of improvements"""
        try:
            # Collect improvement analyses
            analyses = []
            for improvement in improvements:
                if "improvement_analysis" in improvement:
                    analyses.append(improvement["improvement_analysis"])

            if not analyses:
                return {"error": "No improvements available for summary"}

            # Create summary prompt
            summary_prompt = f"""Create a comprehensive summary of code improvements:

{chr(10).join(analyses[:3])}  # Limit to first 3 for token efficiency

Provide:
1. Overall improvement assessment
2. Common improvements made
3. Quality improvements achieved
4. Performance optimizations
5. Security enhancements
6. Best practices implemented"""

            response = await self.ai_service.generate_response(summary_prompt)

            if response.success:
                return {
                    "summary": response.content,
                    "provider": response.provider,
                    "total_files": len(improvements),
                }
            else:
                return {"error": response.error, "total_files": len(improvements)}

        except Exception as e:
            logger.error(f"Error generating improvement summary: {e}")
            return {"error": str(e)}

    def save_improvements(self, results: Dict[str, Any], output_file: str):
        """Save improvement report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Improvement report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving improvement report: {e}")

    async def shutdown(self):
        """Shutdown the improver"""
        if self.ai_service:
            await self.ai_service.shutdown()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Code Improver")
    parser.add_argument("--files", nargs="+", help="Files to improve")
    parser.add_argument("--directory", help="Directory to improve")
    parser.add_argument("--output", help="Output directory for improved files")
    parser.add_argument(
        "--improvement-type",
        default="general",
        choices=[
            "general",
            "performance",
            "security",
            "readability",
            "maintainability",
        ],
        help="Type of improvement to apply",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".py", ".js", ".ts"],
        help="File extensions to improve",
    )
    parser.add_argument(
        "--report", default="improvement_report.json", help="Report file"
    )

    args = parser.parse_args()

    improver = AICodeImprover()

    try:
        await improver.initialize()

        if args.files:
            # Improve specific files
            results = {
                "files_improved": 0,
                "improvements": [],
                "timestamp": datetime.now().isoformat(),
            }

            for file_path in args.files:
                logger.info(f"Improving {file_path}")
                improvement = await improver.improve_file(
                    file_path, args.improvement_type
                )
                results["improvements"].append(improvement)
                if "improved_content" in improvement:
                    results["files_improved"] += 1

            # Generate summary
            results["summary"] = await improver._generate_improvement_summary(
                results["improvements"]
            )

        elif args.directory and args.output:
            # Improve directory
            results = await improver.improve_directory(
                args.directory, args.output, args.improvement_type, args.extensions
            )

        else:
            logger.error("Please specify either --files or --directory with --output")
            return

        # Save report
        improver.save_improvements(results, args.report)

        # Print summary
        if "summary" in results and "summary" in results["summary"]:
            print("\n" + "=" * 50)
            print("AI CODE IMPROVEMENT SUMMARY")
            print("=" * 50)
            print(results["summary"]["summary"])
            print("=" * 50)

        logger.info(
            f"Improvement complete. {results['files_improved']} files improved."
        )

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await improver.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
