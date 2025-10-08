#!/usr/bin/env python3
"""
AI Documentation Generator - Uses multiple AI providers to generate comprehensive documentation
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


class AIDocumentationGenerator:
    """AI-powered documentation generator"""

    def __init__(self):
        self.ai_service = None
        self.generated_docs = {}

    async def initialize(self):
        """Initialize the documentation generator"""
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
            logger.info("AI Documentation Generator initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI Documentation Generator: {e}")
            raise

    async def generate_documentation_for_file(
        self, file_path: str, doc_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate documentation for a single file"""
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

            # Generate documentation
            doc_response = await self._generate_file_documentation(
                content, language, doc_type
            )

            if not doc_response.success:
                return {
                    "file_info": file_info,
                    "error": doc_response.error,
                    "timestamp": datetime.now().isoformat(),
                }

            # Generate API documentation if applicable
            api_doc_response = await self._generate_api_documentation(content, language)

            # Generate usage examples
            examples_response = await self._generate_usage_examples(content, language)

            return {
                "file_info": file_info,
                "documentation": doc_response.content,
                "api_documentation": (
                    api_doc_response.content if api_doc_response.success else None
                ),
                "usage_examples": (
                    examples_response.content if examples_response.success else None
                ),
                "doc_type": doc_type,
                "provider_used": doc_response.provider,
                "response_time": doc_response.response_time,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error generating documentation for file {file_path}: {e}")
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

    async def _generate_file_documentation(
        self, code: str, language: str, doc_type: str
    ) -> Any:
        """Generate comprehensive file documentation"""
        try:
            prompt = f"""Generate comprehensive documentation for this {language} code:

```{language}
{code}
```

Documentation should include:
1. File overview and purpose
2. Function/class descriptions
3. Parameter documentation
4. Return value documentation
5. Usage examples
6. Error handling
7. Dependencies
8. Performance notes
9. Security considerations
10. Best practices

Format as Markdown with proper structure and code examples."""

            response = await self.ai_service.generate_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error generating file documentation: {e}")
            return type(
                "Response",
                (),
                {"success": False, "error": str(e), "content": "", "provider": "none"},
            )()

    async def _generate_api_documentation(self, code: str, language: str) -> Any:
        """Generate API documentation"""
        try:
            prompt = f"""Generate API documentation for this {language} code:

```{language}
{code}
```

Focus on:
1. API endpoints (if applicable)
2. Function signatures
3. Parameter types and descriptions
4. Return types and descriptions
5. Error codes and exceptions
6. Authentication requirements
7. Rate limiting
8. Response formats
9. Status codes
10. Example requests/responses

Format as structured API documentation."""

            response = await self.ai_service.generate_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error generating API documentation: {e}")
            return type(
                "Response",
                (),
                {"success": False, "error": str(e), "content": "", "provider": "none"},
            )()

    async def _generate_usage_examples(self, code: str, language: str) -> Any:
        """Generate usage examples"""
        try:
            prompt = f"""Generate comprehensive usage examples for this {language} code:

```{language}
{code}
```

Include:
1. Basic usage examples
2. Advanced usage scenarios
3. Error handling examples
4. Integration examples
5. Performance optimization examples
6. Security best practices
7. Common pitfalls and solutions
8. Testing examples

Provide complete, runnable examples with explanations."""

            response = await self.ai_service.generate_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error generating usage examples: {e}")
            return type(
                "Response",
                (),
                {"success": False, "error": str(e), "content": "", "provider": "none"},
            )()

    async def generate_documentation_for_directory(
        self,
        directory: str,
        output_dir: str,
        doc_type: str = "comprehensive",
        extensions: List[str] = None,
    ) -> Dict[str, Any]:
        """Generate documentation for all files in a directory"""
        if extensions is None:
            extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs"]

        results = {
            "directory": directory,
            "output_directory": output_dir,
            "files_documented": 0,
            "generated_docs": [],
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

            logger.info(f"Found {len(files)} files to document")

            for file_path in files:
                logger.info(f"Generating documentation for {file_path}")
                doc_result = await self.generate_documentation_for_file(
                    str(file_path), doc_type
                )
                results["generated_docs"].append(doc_result)

                if "documentation" in doc_result:
                    # Save documentation file
                    relative_path = file_path.relative_to(directory_path)
                    doc_file_name = f"{relative_path.stem}_documentation.md"
                    output_file = output_path / doc_file_name

                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(doc_result["documentation"])

                    # Save API documentation if available
                    if doc_result.get("api_documentation"):
                        api_doc_file = output_path / f"{relative_path.stem}_api.md"
                        with open(api_doc_file, "w", encoding="utf-8") as f:
                            f.write(doc_result["api_documentation"])

                    # Save usage examples if available
                    if doc_result.get("usage_examples"):
                        examples_file = (
                            output_path / f"{relative_path.stem}_examples.md"
                        )
                        with open(examples_file, "w", encoding="utf-8") as f:
                            f.write(doc_result["usage_examples"])

                    results["files_documented"] += 1

            # Generate summary
            results["summary"] = await self._generate_documentation_summary(
                results["generated_docs"]
            )

        except Exception as e:
            logger.error(
                f"Error generating documentation for directory {directory}: {e}"
            )
            results["error"] = str(e)

        return results

    async def _generate_documentation_summary(
        self, doc_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate documentation summary"""
        try:
            # Collect documentation analyses
            analyses = []
            for doc_result in doc_results:
                if "documentation" in doc_result:
                    analyses.append(doc_result["documentation"])

            if not analyses:
                return {"error": "No documentation available for summary"}

            # Create summary prompt
            summary_prompt = f"""Create a comprehensive documentation summary based on these generated docs:

{chr(10).join(analyses[:3])}  # Limit to first 3 for token efficiency

Provide:
1. Overall documentation quality assessment
2. Coverage analysis
3. Documentation completeness
4. Areas needing improvement
5. Documentation standards compliance
6. Recommendations for better documentation"""

            response = await self.ai_service.generate_response(summary_prompt)

            if response.success:
                return {
                    "summary": response.content,
                    "provider": response.provider,
                    "total_files": len(doc_results),
                }
            else:
                return {"error": response.error, "total_files": len(doc_results)}

        except Exception as e:
            logger.error(f"Error generating documentation summary: {e}")
            return {"error": str(e)}

    def save_documentation_report(self, results: Dict[str, Any], output_file: str):
        """Save documentation report to file"""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Documentation report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving documentation report: {e}")

    async def shutdown(self):
        """Shutdown the documentation generator"""
        if self.ai_service:
            await self.ai_service.shutdown()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Documentation Generator")
    parser.add_argument(
        "--files", nargs="+", help="Files to generate documentation for"
    )
    parser.add_argument("--directory", help="Directory to generate documentation for")
    parser.add_argument("--output", help="Output directory for documentation files")
    parser.add_argument(
        "--doc-type",
        default="comprehensive",
        choices=["comprehensive", "api", "usage", "technical"],
        help="Type of documentation to generate",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".py", ".js", ".ts"],
        help="File extensions to generate documentation for",
    )
    parser.add_argument(
        "--report", default="documentation_report.json", help="Report file"
    )

    args = parser.parse_args()

    generator = AIDocumentationGenerator()

    try:
        await generator.initialize()

        if args.files:
            # Generate documentation for specific files
            results = {
                "files_documented": 0,
                "generated_docs": [],
                "timestamp": datetime.now().isoformat(),
            }

            for file_path in args.files:
                logger.info(f"Generating documentation for {file_path}")
                doc_result = await generator.generate_documentation_for_file(
                    file_path, args.doc_type
                )
                results["generated_docs"].append(doc_result)
                if "documentation" in doc_result:
                    results["files_documented"] += 1

            # Generate summary
            results["summary"] = await generator._generate_documentation_summary(
                results["generated_docs"]
            )

        elif args.directory and args.output:
            # Generate documentation for directory
            results = await generator.generate_documentation_for_directory(
                args.directory, args.output, args.doc_type, args.extensions
            )

        else:
            logger.error("Please specify either --files or --directory with --output")
            return

        # Save report
        generator.save_documentation_report(results, args.report)

        # Print summary
        if "summary" in results and "summary" in results["summary"]:
            print("\n" + "=" * 50)
            print("AI DOCUMENTATION GENERATION SUMMARY")
            print("=" * 50)
            print(results["summary"]["summary"])
            print("=" * 50)

        logger.info(
            f"Generated {len(docs)} documentation files in {elapsed_time:.2f} seconds"
        )

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await generator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
