#!/usr/bin/env python3
"""
AI Continuous Developer - Uses multiple AI providers for continuous development
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

class AIContinuousDeveloper:
    """AI-powered continuous developer"""
    
    def __init__(self):
        self.ai_service = None
        self.development_plan = {}
    
    async def initialize(self):
        """Initialize the continuous developer"""
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
            logger.info("AI Continuous Developer initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Continuous Developer: {e}")
            raise
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze the entire project for improvements"""
        try:
            project_path = Path(project_path)
            
            # Get project structure
            project_structure = self._get_project_structure(project_path)
            
            # Analyze code quality
            quality_analysis = await self._analyze_project_quality(project_path)
            
            # Analyze architecture
            architecture_analysis = await self._analyze_architecture(project_structure)
            
            # Analyze security
            security_analysis = await self._analyze_security(project_path)
            
            # Analyze performance
            performance_analysis = await self._analyze_performance(project_path)
            
            # Generate improvement plan
            improvement_plan = await self._generate_improvement_plan(
                quality_analysis, architecture_analysis, security_analysis, performance_analysis
            )
            
            return {
                'project_structure': project_structure,
                'quality_analysis': quality_analysis,
                'architecture_analysis': architecture_analysis,
                'security_analysis': security_analysis,
                'performance_analysis': performance_analysis,
                'improvement_plan': improvement_plan,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing project: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _get_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Get project structure information"""
        try:
            structure = {
                'root': str(project_path),
                'directories': [],
                'files': [],
                'file_types': {},
                'total_files': 0,
                'total_lines': 0
            }
            
            for item in project_path.rglob('*'):
                if item.is_file():
                    structure['files'].append(str(item.relative_to(project_path)))
                    structure['total_files'] += 1
                    
                    # Count lines
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                            structure['total_lines'] += lines
                    except:
                        pass
                    
                    # Count file types
                    ext = item.suffix.lower()
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                
                elif item.is_dir():
                    structure['directories'].append(str(item.relative_to(project_path)))
            
            return structure
            
        except Exception as e:
            logger.error(f"Error getting project structure: {e}")
            return {'error': str(e)}
    
    async def _analyze_project_quality(self, project_path: Path) -> Dict[str, Any]:
        """Analyze overall project quality"""
        try:
            # Get key files
            key_files = []
            for ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                key_files.extend(project_path.rglob(f"*{ext}"))
            
            # Limit to first 10 files for analysis
            key_files = key_files[:10]
            
            if not key_files:
                return {'error': 'No code files found'}
            
            # Analyze each file
            file_analyses = []
            for file_path in key_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_ext = file_path.suffix.lower()
                    language = self._get_language_from_extension(file_ext)
                    
                    # Quick quality analysis
                    quality_prompt = f"""Analyze the quality of this {language} code:
1. Code quality score (1-10)
2. Main issues
3. Best practices violations
4. Improvement suggestions

Code:
```{language}
{content[:2000]}  # Limit content for token efficiency
```

Provide a concise analysis."""
                    
                    response = await self.ai_service.generate_response(quality_prompt)
                    
                    if response.success:
                        file_analyses.append({
                            'file': str(file_path.relative_to(project_path)),
                            'language': language,
                            'analysis': response.content,
                            'provider': response.provider
                        })
                
                except Exception as e:
                    logger.warning(f"Error analyzing {file_path}: {e}")
                    continue
            
            # Generate overall quality summary
            if file_analyses:
                # Create file analysis summary
                file_summaries = []
                for fa in file_analyses[:3]:
                    file_summaries.append(f"File: {fa['file']}\nAnalysis: {fa['analysis']}")
                
                summary_prompt = f"""Create a project-wide quality assessment based on these file analyses:

{'\n'.join(file_summaries)}

Provide:
1. Overall project quality score
2. Common issues across files
3. Priority improvements
4. Quality trends
5. Recommendations"""
                
                summary_response = await self.ai_service.generate_response(summary_prompt)
                
                return {
                    'file_analyses': file_analyses,
                    'overall_summary': summary_response.content if summary_response.success else summary_response.error,
                    'total_files_analyzed': len(file_analyses)
                }
            else:
                return {'error': 'No files could be analyzed'}
                
        except Exception as e:
            logger.error(f"Error analyzing project quality: {e}")
            return {'error': str(e)}
    
    async def _analyze_architecture(self, project_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project architecture"""
        try:
            architecture_prompt = f"""Analyze the architecture of this project based on its structure:

Directories: {project_structure.get('directories', [])[:20]}
File types: {project_structure.get('file_types', {})}
Total files: {project_structure.get('total_files', 0)}
Total lines: {project_structure.get('total_lines', 0)}

Provide:
1. Architecture assessment
2. Design patterns identified
3. Structural issues
4. Scalability concerns
5. Improvement suggestions"""
            
            response = await self.ai_service.generate_response(architecture_prompt)
            
            if response.success:
                return {
                    'analysis': response.content,
                    'provider': response.provider
                }
            else:
                return {'error': response.error}
                
        except Exception as e:
            logger.error(f"Error analyzing architecture: {e}")
            return {'error': str(e)}
    
    async def _analyze_security(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project security"""
        try:
            # Look for common security files
            security_files = []
            for pattern in ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.go', '*.rs']:
                security_files.extend(project_path.rglob(pattern))
            
            # Limit to first 5 files
            security_files = security_files[:5]
            
            if not security_files:
                return {'error': 'No code files found for security analysis'}
            
            # Analyze security
            security_content = ""
            for file_path in security_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    security_content += f"\n--- {file_path.name} ---\n{content[:1000]}\n"
                except:
                    continue
            
            security_prompt = f"""Analyze the security of this codebase:

{security_content}

Focus on:
1. Security vulnerabilities
2. Authentication/authorization issues
3. Input validation problems
4. Sensitive data exposure
5. Cryptographic issues
6. Security best practices violations

Provide a comprehensive security assessment."""
            
            response = await self.ai_service.generate_response(security_prompt)
            
            if response.success:
                return {
                    'analysis': response.content,
                    'provider': response.provider,
                    'files_analyzed': len(security_files)
                }
            else:
                return {'error': response.error}
                
        except Exception as e:
            logger.error(f"Error analyzing security: {e}")
            return {'error': str(e)}
    
    async def _analyze_performance(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project performance"""
        try:
            # Look for performance-critical files
            perf_files = []
            for pattern in ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.go', '*.rs']:
                perf_files.extend(project_path.rglob(pattern))
            
            # Limit to first 5 files
            perf_files = perf_files[:5]
            
            if not perf_files:
                return {'error': 'No code files found for performance analysis'}
            
            # Analyze performance
            perf_content = ""
            for file_path in perf_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    perf_content += f"\n--- {file_path.name} ---\n{content[:1000]}\n"
                except:
                    continue
            
            performance_prompt = f"""Analyze the performance of this codebase:

{perf_content}

Focus on:
1. Performance bottlenecks
2. Inefficient algorithms
3. Memory usage issues
4. CPU optimization opportunities
5. Scalability concerns
6. Performance best practices

Provide a comprehensive performance assessment."""
            
            response = await self.ai_service.generate_response(performance_prompt)
            
            if response.success:
                return {
                    'analysis': response.content,
                    'provider': response.provider,
                    'files_analyzed': len(perf_files)
                }
            else:
                return {'error': response.error}
                
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {'error': str(e)}
    
    async def _generate_improvement_plan(self, quality_analysis: Dict[str, Any], 
                                      architecture_analysis: Dict[str, Any],
                                      security_analysis: Dict[str, Any],
                                      performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive improvement plan"""
        try:
            improvement_prompt = f"""Create a comprehensive improvement plan based on these analyses:

Quality Analysis: {quality_analysis.get('overall_summary', 'N/A')}
Architecture Analysis: {architecture_analysis.get('analysis', 'N/A')}
Security Analysis: {security_analysis.get('analysis', 'N/A')}
Performance Analysis: {performance_analysis.get('analysis', 'N/A')}

Provide:
1. Priority improvement areas
2. Specific action items
3. Implementation timeline
4. Resource requirements
5. Success metrics
6. Risk assessment"""
            
            response = await self.ai_service.generate_response(improvement_prompt)
            
            if response.success:
                return {
                    'plan': response.content,
                    'provider': response.provider,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': response.error}
                
        except Exception as e:
            logger.error(f"Error generating improvement plan: {e}")
            return {'error': str(e)}
    
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
    
    def save_analysis_report(self, results: Dict[str, Any], output_file: str):
        """Save analysis report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Analysis report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving analysis report: {e}")
    
    async def shutdown(self):
        """Shutdown the continuous developer"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Continuous Developer')
    parser.add_argument('--project-path', default='.', help='Project path to analyze')
    parser.add_argument('--mode', choices=['full_analysis', 'quality_only', 'security_only', 'performance_only'], 
                      default='full_analysis', help='Analysis mode')
    parser.add_argument('--output', default='continuous_improvements.md', help='Output file')
    
    args = parser.parse_args()
    
    developer = AIContinuousDeveloper()
    
    try:
        await developer.initialize()
        
        # Analyze project
        results = await developer.analyze_project(args.project_path)
        
        # Save report
        developer.save_analysis_report(results, args.output)
        
        # Print summary
        if 'improvement_plan' in results and 'plan' in results['improvement_plan']:
            print("\n" + "="*50)
            print("AI CONTINUOUS DEVELOPMENT ANALYSIS")
            print("="*50)
            print(results['improvement_plan']['plan'])
            print("="*50)
        
        logger.info("Continuous development analysis complete.")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
    
    finally:
        await developer.shutdown()

if __name__ == "__main__":
    asyncio.run(main())