#!/usr/bin/env python3
"""
AI Test Generator - Uses multiple AI providers to generate comprehensive tests
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from services.ai_service_manager import AIServiceManager, AIProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AITestGenerator:
    """AI-powered test generator"""

    def __init__(self):
        self.ai_service = None
        self.generated_tests = {}

    async def initialize(self):
        """Initialize the test generator"""
        try:
            config = {
                'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
                'glm_api_key': os.getenv('GLM_API_KEY'),
                'grok_api_key': os.getenv('GROK_API_KEY'),
                'kimi_api_key': os.getenv('KIMI_API_KEY'),
                'qwen_api_key': os.getenv('QWEN_API_KEY'),
                'gptoss_api_key': os.getenv('GPTOSS_API_KEY')
            }

            self.ai_service = AIServiceManager(config)
            await self.ai_service.initialize()
            logger.info("AI Test Generator initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI Test Generator: {e}")
            raise

    async def generate_tests_for_file(self, file_path: str, test_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate tests for a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_ext = Path(file_path).suffix.lower()
            language = self._get_language_from_extension(file_ext)

            # Get file info
            file_info = {
                'path': file_path,
                'language': language,
                'size': len(content),
                'lines': len(content.splitlines())
            }

            # Generate tests
            test_response = await self.ai_service.generate_tests(content, language)

            if not test_response.success:
                return {
                    'file_info': file_info,
                    'error': test_response.error,
                    'timestamp': datetime.now().isoformat()
                }

            # Extract test code from response
            test_content = self._extract_code_from_response(test_response.content, language)

            # Generate test analysis
            analysis_response = await self.ai_service.analyze_code(test_content, language)

            return {
                'file_info': file_info,
                'original_content': content,
                'test_content': test_content,
                'test_analysis': analysis_response.content if analysis_response.success else analysis_response.error,
                'test_type': test_type,
                'provider_used': test_response.provider,
                'response_time': test_response.response_time,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating tests for file {file_path}: {e}")
            return {
                'file_info': {'path': file_path, 'error': str(e)},
                'timestamp': datetime.now().isoformat()
            }

    def _get_language_from_extension(self, ext: str) -> str:
        """Get programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.sh': 'bash',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini'
        }
        return language_map.get(ext, 'unknown')

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

    async def generate_tests_for_directory(self, directory: str, output_dir: str,
                                         test_type: str = "comprehensive",
                                         extensions: List[str] = None) -> Dict[str, Any]:
        """Generate tests for all files in a directory"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']

        results = {
            'directory': directory,
            'output_directory': output_dir,
            'files_tested': 0,
            'generated_tests': [],
            'summary': {},
            'timestamp': datetime.now().isoformat()
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

            logger.info(f"Found {len(files)} files to generate tests for")

            for file_path in files:
                logger.info(f"Generating tests for {file_path}")
                test_result = await self.generate_tests_for_file(str(file_path), test_type)
                results['generated_tests'].append(test_result)

                if 'test_content' in test_result:
                    # Save test file
                    relative_path = file_path.relative_to(directory_path)
                    test_file_name = f"test_{relative_path.stem}.py"
                    output_file = output_path / test_file_name

                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(test_result['test_content'])

                    results['files_tested'] += 1

            # Generate summary
            results['summary'] = await self._generate_test_summary(results['generated_tests'])

        except Exception as e:
            logger.error(f"Error generating tests for directory {directory}: {e}")
            results['error'] = str(e)

        return results

    async def _generate_test_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of test generation"""
        try:
            # Collect test analyses
            analyses = []
            for test_result in test_results:
                if 'test_analysis' in test_result:
                    analyses.append(test_result['test_analysis'])

            if not analyses:
                return {'error': 'No tests available for summary'}

            # Create summary prompt
            summary_prompt = f"""Create a comprehensive summary of generated tests:

{chr(10).join(analyses[:3])}  # Limit to first 3 for token efficiency

Provide:
1. Overall test coverage assessment
2. Test quality evaluation
3. Coverage gaps identified
4. Test types generated
5. Recommendations for additional testing
6. Test execution strategy"""

            response = await self.ai_service.generate_response(summary_prompt)

            if response.success:
                return {
                    'summary': response.content,
                    'provider': response.provider,
                    'total_files': len(test_results)
                }
            else:
                return {
                    'error': response.error,
                    'total_files': len(test_results)
                }

        except Exception as e:
            logger.error(f"Error generating test summary: {e}")
            return {'error': str(e)}

    def save_test_report(self, results: Dict[str, Any], output_file: str):
        """Save test generation report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Test report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving test report: {e}")

    async def shutdown(self):
        """Shutdown the test generator"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Test Generator')
    parser.add_argument('--files', nargs='+', help='Files to generate tests for')
    parser.add_argument('--directory', help='Directory to generate tests for')
    parser.add_argument('--output', help='Output directory for test files')
    parser.add_argument('--test-type', default='comprehensive',
                      choices=['comprehensive', 'unit', 'integration', 'performance', 'security'],
                      help='Type of tests to generate')
    parser.add_argument('--extensions', nargs='+', default=['.py', '.js', '.ts'],
                      help='File extensions to generate tests for')
    parser.add_argument('--report', default='test_generation_report.json', help='Report file')

    args = parser.parse_args()

    generator = AITestGenerator()

    try:
        await generator.initialize()

        if args.files:
            # Generate tests for specific files
            results = {
                'files_tested': 0,
                'generated_tests': [],
                'timestamp': datetime.now().isoformat()
            }

            for file_path in args.files:
                logger.info(f"Generating tests for {file_path}")
                test_result = await generator.generate_tests_for_file(file_path, args.test_type)
                results['generated_tests'].append(test_result)
                if 'test_content' in test_result:
                    results['files_tested'] += 1

            # Generate summary
            results['summary'] = await generator._generate_test_summary(results['generated_tests'])

        elif args.directory and args.output:
            # Generate tests for directory
            results = await generator.generate_tests_for_directory(
                args.directory, args.output, args.test_type, args.extensions
            )

        else:
            logger.error("Please specify either --files or --directory with --output")
            return

        # Save report
        generator.save_test_report(results, args.report)

        # Print summary
        if 'summary' in results and 'summary' in results['summary']:
            print("\n" + "="*50)
            print("AI TEST GENERATION SUMMARY")
            print("="*50)
            print(results['summary']['summary'])
            print("="*50)

        logger.info(f"Test generation complete. {results['files_tested']} test files generated.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await generator.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
