#!/usr/bin/env python3
"""
AI Performance Analyzer - Uses multiple AI providers to analyze and optimize performance
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

class AIPerformanceAnalyzer:
    """AI-powered performance analyzer"""

    def __init__(self):
        self.ai_service = None
        self.performance_reports = {}

    async def initialize(self):
        """Initialize the performance analyzer"""
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
            logger.info("AI Performance Analyzer initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing AI Performance Analyzer: {e}")
            raise

    async def analyze_file_performance(self, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze performance of a single file"""
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

            # Perform performance analysis
            performance_analysis = await self._analyze_performance(content, language, analysis_type)

            if not performance_analysis.success:
                return {
                    'file_info': file_info,
                    'error': performance_analysis.error,
                    'timestamp': datetime.now().isoformat()
                }

            # Generate optimization recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(content, language)

            # Generate performance metrics
            performance_metrics = await self._generate_performance_metrics(content, language)

            # Calculate performance score
            performance_score = await self._calculate_performance_score(performance_analysis.content, optimization_recommendations.content if optimization_recommendations.success else "")

            return {
                'file_info': file_info,
                'performance_analysis': performance_analysis.content,
                'optimization_recommendations': optimization_recommendations.content if optimization_recommendations.success else None,
                'performance_metrics': performance_metrics.content if performance_metrics.success else None,
                'performance_score': performance_score,
                'analysis_type': analysis_type,
                'provider_used': performance_analysis.provider,
                'response_time': performance_analysis.response_time,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing performance of file {file_path}: {e}")
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

    async def _analyze_performance(self, code: str, language: str, analysis_type: str) -> Any:
        """Perform comprehensive performance analysis"""
        try:
            prompt = f"""Perform a comprehensive performance analysis of this {language} code:

```{language}
{code}
```

Focus on:
1. Time complexity analysis
2. Space complexity analysis
3. Memory usage patterns
4. CPU usage optimization
5. I/O performance issues
6. Algorithm efficiency
7. Data structure choices
8. Loop optimization opportunities
9. Function call overhead
10. Caching opportunities
11. Parallel processing potential
12. Database query optimization
13. Network performance
14. Resource utilization
15. Scalability concerns

Provide:
1. Performance score (1-10)
2. Bottlenecks identified
3. Optimization opportunities
4. Performance metrics
5. Specific recommendations
6. Code examples of optimizations
7. Performance testing suggestions

Format as a detailed performance analysis report."""

            response = await self.ai_service.generate_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return type('Response', (), {'success': False, 'error': str(e), 'content': '', 'provider': 'none'})()

    async def _generate_optimization_recommendations(self, code: str, language: str) -> Any:
        """Generate optimization recommendations"""
        try:
            prompt = f"""Generate comprehensive optimization recommendations for this {language} code:

```{language}
{code}
```

Include:
1. Immediate performance improvements
2. Algorithm optimizations
3. Data structure improvements
4. Memory optimization techniques
5. CPU optimization strategies
6. I/O optimization methods
7. Caching strategies
8. Parallel processing opportunities
9. Database optimization
10. Network optimization
11. Resource management improvements
12. Performance monitoring setup
13. Load testing recommendations
14. Scalability improvements
15. Code refactoring suggestions

Provide specific, actionable recommendations with code examples."""

            response = await self.ai_service.generate_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error generating optimization recommendations: {e}")
            return type('Response', (), {'success': False, 'error': str(e), 'content': '', 'provider': 'none'})()

    async def _generate_performance_metrics(self, code: str, language: str) -> Any:
        """Generate performance metrics"""
        try:
            prompt = f"""Generate performance metrics and monitoring recommendations for this {language} code:

```{language}
{code}
```

Include:
1. Key performance indicators (KPIs)
2. Metrics to monitor
3. Performance benchmarks
4. Load testing scenarios
5. Stress testing recommendations
6. Performance profiling tools
7. Monitoring setup
8. Alerting thresholds
9. Performance dashboards
10. Bottleneck detection
11. Resource utilization tracking
12. Response time monitoring
13. Throughput measurement
14. Error rate tracking
15. Performance regression detection

Provide specific metrics and monitoring strategies."""

            response = await self.ai_service.generate_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error generating performance metrics: {e}")
            return type('Response', (), {'success': False, 'error': str(e), 'content': '', 'provider': 'none'})()

    async def _calculate_performance_score(self, analysis_content: str, optimization_content: str) -> int:
        """Calculate performance score based on analysis results"""
        try:
            prompt = f"""Based on this performance analysis and optimization recommendations, calculate a performance score (1-10):

Performance Analysis:
{analysis_content}

Optimization Recommendations:
{optimization_content}

Consider:
1. Code efficiency
2. Algorithm complexity
3. Resource utilization
4. Scalability potential
5. Optimization opportunities
6. Performance bottlenecks
7. Overall performance posture

Return only a single number between 1-10 representing the performance score."""

            response = await self.ai_service.generate_response(prompt)

            if response.success:
                # Try to extract number from response
                import re
                numbers = re.findall(r'\b(?:10|[1-9])\b', response.content)
                if numbers:
                    return int(numbers[0])
                else:
                    return 5  # Default score if no number found
            else:
                return 5  # Default score on error

        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 5  # Default score on error

    async def analyze_directory_performance(self, directory: str, output_dir: str,
                                          analysis_type: str = "comprehensive",
                                          extensions: List[str] = None) -> Dict[str, Any]:
        """Analyze performance of all files in a directory"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']

        results = {
            'directory': directory,
            'output_directory': output_dir,
            'files_analyzed': 0,
            'performance_reports': [],
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

            logger.info(f"Found {len(files)} files to analyze")

            for file_path in files:
                logger.info(f"Analyzing performance of {file_path}")
                analysis_result = await self.analyze_file_performance(str(file_path), analysis_type)
                results['performance_reports'].append(analysis_result)

                if 'performance_analysis' in analysis_result:
                    # Save performance report
                    relative_path = file_path.relative_to(directory_path)
                    performance_file_name = f"{relative_path.stem}_performance_report.md"
                    output_file = output_path / performance_file_name

                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Performance Analysis Report for {relative_path}\n\n")
                        f.write(f"**Performance Score:** {analysis_result.get('performance_score', 'N/A')}/10\n\n")
                        f.write("## Performance Analysis\n\n")
                        f.write(analysis_result['performance_analysis'])

                        if analysis_result.get('optimization_recommendations'):
                            f.write("\n\n## Optimization Recommendations\n\n")
                            f.write(analysis_result['optimization_recommendations'])

                        if analysis_result.get('performance_metrics'):
                            f.write("\n\n## Performance Metrics\n\n")
                            f.write(analysis_result['performance_metrics'])

                    results['files_analyzed'] += 1

            # Generate summary
            results['summary'] = await self._generate_performance_summary(results['performance_reports'])

        except Exception as e:
            logger.error(f"Error analyzing directory performance {directory}: {e}")
            results['error'] = str(e)

        return results

    async def _generate_performance_summary(self, performance_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance analysis summary"""
        try:
            # Collect performance analyses
            analyses = []
            scores = []
            for report in performance_reports:
                if 'performance_analysis' in report:
                    analyses.append(report['performance_analysis'])
                if 'performance_score' in report:
                    scores.append(report['performance_score'])

            if not analyses:
                return {'error': 'No performance analyses available for summary'}

            # Create summary prompt
            summary_prompt = f"""Create a comprehensive performance analysis summary based on these reports:

{chr(10).join(analyses[:3])}  # Limit to first 3 for token efficiency

Performance Scores: {scores}

Provide:
1. Overall performance assessment
2. Common performance issues
3. Critical bottlenecks
4. Performance score analysis
5. Priority optimization recommendations
6. Performance improvement roadmap"""

            response = await self.ai_service.generate_response(summary_prompt)

            if response.success:
                return {
                    'summary': response.content,
                    'provider': response.provider,
                    'total_files': len(performance_reports),
                    'average_score': sum(scores) / len(scores) if scores else 0,
                    'scores': scores
                }
            else:
                return {
                    'error': response.error,
                    'total_files': len(performance_reports)
                }

        except Exception as e:
            logger.error(f"Error generating performance summary: {e}")
            return {'error': str(e)}

    def save_performance_report(self, results: Dict[str, Any], output_file: str):
        """Save performance analysis report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Performance report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving performance report: {e}")

    async def shutdown(self):
        """Shutdown the performance analyzer"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Performance Analyzer')
    parser.add_argument('--files', nargs='+', help='Files to analyze')
    parser.add_argument('--directory', help='Directory to analyze')
    parser.add_argument('--output', help='Output directory for performance reports')
    parser.add_argument('--analysis-type', default='comprehensive',
                      choices=['comprehensive', 'cpu', 'memory', 'io', 'network'],
                      help='Type of performance analysis to perform')
    parser.add_argument('--extensions', nargs='+', default=['.py', '.js', '.ts'],
                      help='File extensions to analyze')
    parser.add_argument('--report', default='performance_report.md', help='Report file')

    args = parser.parse_args()

    analyzer = AIPerformanceAnalyzer()

    try:
        await analyzer.initialize()

        if args.files:
            # Analyze specific files
            results = {
                'files_analyzed': 0,
                'performance_reports': [],
                'timestamp': datetime.now().isoformat()
            }

            for file_path in args.files:
                logger.info(f"Analyzing {file_path}")
                analysis_result = await analyzer.analyze_file_performance(file_path, args.analysis_type)
                results['performance_reports'].append(analysis_result)
                if 'performance_analysis' in analysis_result:
                    results['files_analyzed'] += 1

            # Generate summary
            results['summary'] = await analyzer._generate_performance_summary(results['performance_reports'])

        elif args.directory and args.output:
            # Analyze directory
            results = await analyzer.analyze_directory_performance(
                args.directory, args.output, args.analysis_type, args.extensions
            )

        else:
            logger.error("Please specify either --files or --directory with --output")
            return

        # Save report
        analyzer.save_performance_report(results, args.report)

        # Print summary
        if 'summary' in results and 'summary' in results['summary']:
            print("\n" + "="*50)
            print("AI PERFORMANCE ANALYSIS SUMMARY")
            print("="*50)
            print(results['summary']['summary'])
            if 'average_score' in results['summary']:
                print(f"\nAverage Performance Score: {results['summary']['average_score']:.1f}/10")
            print("="*50)

        logger.info(f"Performance analysis complete. {results['files_analyzed']} files analyzed.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

    finally:
        await analyzer.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
