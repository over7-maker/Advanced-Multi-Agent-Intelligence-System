#!/usr/bin/env python3
"""
AI Security Auditor - Uses multiple AI providers to perform comprehensive security audits
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

class AISecurityAuditor:
    """AI-powered security auditor"""
    
    def __init__(self):
        self.ai_service = None
        self.security_reports = {}
    
    async def initialize(self):
        """Initialize the security auditor"""
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
            logger.info("AI Security Auditor initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Security Auditor: {e}")
            raise
    
    async def audit_file(self, file_path: str, audit_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform security audit on a single file"""
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
            
            # Perform security audit
            security_audit = await self._perform_security_audit(content, language, audit_type)
            
            if not security_audit.success:
                return {
                    'file_info': file_info,
                    'error': security_audit.error,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Generate vulnerability report
            vulnerability_report = await self._generate_vulnerability_report(content, language)
            
            # Generate security recommendations
            security_recommendations = await self._generate_security_recommendations(content, language)
            
            # Calculate security score
            security_score = await self._calculate_security_score(security_audit.content, vulnerability_report.content if vulnerability_report.success else "")
            
            return {
                'file_info': file_info,
                'security_audit': security_audit.content,
                'vulnerability_report': vulnerability_report.content if vulnerability_report.success else None,
                'security_recommendations': security_recommendations.content if security_recommendations.success else None,
                'security_score': security_score,
                'audit_type': audit_type,
                'provider_used': security_audit.provider,
                'response_time': security_audit.response_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error auditing file {file_path}: {e}")
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
    
    async def _perform_security_audit(self, code: str, language: str, audit_type: str) -> Any:
        """Perform comprehensive security audit"""
        try:
            prompt = f"""Perform a comprehensive security audit of this {language} code:

```{language}
{code}
```

Focus on:
1. SQL injection vulnerabilities
2. Cross-site scripting (XSS) vulnerabilities
3. Authentication and authorization issues
4. Input validation problems
5. Sensitive data exposure
6. Cryptographic issues
7. Insecure direct object references
8. Security misconfigurations
9. Insecure deserialization
10. Using components with known vulnerabilities
11. Insufficient logging and monitoring
12. Business logic flaws
13. Race conditions
14. Memory corruption issues
15. Code injection vulnerabilities

Provide:
1. Security score (1-10)
2. Critical vulnerabilities found
3. High-risk issues
4. Medium-risk issues
5. Low-risk issues
6. Security best practices violations
7. Specific recommendations for each issue
8. Code examples of fixes

Format as a detailed security audit report."""
            
            response = await self.ai_service.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error performing security audit: {e}")
            return type('Response', (), {'success': False, 'error': str(e), 'content': '', 'provider': 'none'})()
    
    async def _generate_vulnerability_report(self, code: str, language: str) -> Any:
        """Generate detailed vulnerability report"""
        try:
            prompt = f"""Generate a detailed vulnerability report for this {language} code:

```{language}
{code}
```

Include:
1. CVE-style vulnerability descriptions
2. Severity ratings (Critical, High, Medium, Low)
3. CVSS scores where applicable
4. Exploit scenarios
5. Impact assessment
6. Proof of concept examples
7. Remediation steps
8. Prevention measures
9. References to security standards
10. Compliance implications

Format as a professional vulnerability report."""
            
            response = await self.ai_service.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating vulnerability report: {e}")
            return type('Response', (), {'success': False, 'error': str(e), 'content': '', 'provider': 'none'})()
    
    async def _generate_security_recommendations(self, code: str, language: str) -> Any:
        """Generate security recommendations"""
        try:
            prompt = f"""Generate comprehensive security recommendations for this {language} code:

```{language}
{code}
```

Provide:
1. Immediate security fixes
2. Long-term security improvements
3. Security architecture recommendations
4. Best practices implementation
5. Security testing recommendations
6. Monitoring and logging improvements
7. Access control enhancements
8. Data protection measures
9. Secure coding guidelines
10. Security training recommendations

Format as actionable security recommendations."""
            
            response = await self.ai_service.generate_response(prompt)
            return response
            
        except Exception as e:
            logger.error(f"Error generating security recommendations: {e}")
            return type('Response', (), {'success': False, 'error': str(e), 'content': '', 'provider': 'none'})()
    
    async def _calculate_security_score(self, audit_content: str, vulnerability_content: str) -> int:
        """Calculate security score based on audit results"""
        try:
            prompt = f"""Based on this security audit and vulnerability report, calculate a security score (1-10):

Security Audit:
{audit_content}

Vulnerability Report:
{vulnerability_content}

Consider:
1. Number and severity of vulnerabilities
2. Security best practices compliance
3. Code quality and security patterns
4. Risk assessment
5. Overall security posture

Return only a single number between 1-10 representing the security score."""
            
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
            logger.error(f"Error calculating security score: {e}")
            return 5  # Default score on error
    
    async def audit_directory(self, directory: str, output_dir: str, 
                            audit_type: str = "comprehensive",
                            extensions: List[str] = None) -> Dict[str, Any]:
        """Perform security audit on all files in a directory"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
        
        results = {
            'directory': directory,
            'output_directory': output_dir,
            'files_audited': 0,
            'security_reports': [],
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
            
            logger.info(f"Found {len(files)} files to audit")
            
            for file_path in files:
                logger.info(f"Auditing {file_path}")
                audit_result = await self.audit_file(str(file_path), audit_type)
                results['security_reports'].append(audit_result)
                
                if 'security_audit' in audit_result:
                    # Save security report
                    relative_path = file_path.relative_to(directory_path)
                    security_file_name = f"{relative_path.stem}_security_report.md"
                    output_file = output_path / security_file_name
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Security Audit Report for {relative_path}\n\n")
                        f.write(f"**Security Score:** {audit_result.get('security_score', 'N/A')}/10\n\n")
                        f.write("## Security Audit\n\n")
                        f.write(audit_result['security_audit'])
                        
                        if audit_result.get('vulnerability_report'):
                            f.write("\n\n## Vulnerability Report\n\n")
                            f.write(audit_result['vulnerability_report'])
                        
                        if audit_result.get('security_recommendations'):
                            f.write("\n\n## Security Recommendations\n\n")
                            f.write(audit_result['security_recommendations'])
                    
                    results['files_audited'] += 1
            
            # Generate summary
            results['summary'] = await self._generate_security_summary(results['security_reports'])
            
        except Exception as e:
            logger.error(f"Error auditing directory {directory}: {e}")
            results['error'] = str(e)
        
        return results
    
    async def _generate_security_summary(self, security_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate security audit summary"""
        try:
            # Collect security analyses
            analyses = []
            scores = []
            for report in security_reports:
                if 'security_audit' in report:
                    analyses.append(report['security_audit'])
                if 'security_score' in report:
                    scores.append(report['security_score'])
            
            if not analyses:
                return {'error': 'No security audits available for summary'}
            
            # Create summary prompt
            summary_prompt = f"""Create a comprehensive security audit summary based on these reports:

{chr(10).join(analyses[:3])}  # Limit to first 3 for token efficiency

Security Scores: {scores}

Provide:
1. Overall security posture assessment
2. Common vulnerabilities found
3. Critical security issues
4. Security score analysis
5. Priority recommendations
6. Security improvement roadmap"""
            
            response = await self.ai_service.generate_response(summary_prompt)
            
            if response.success:
                return {
                    'summary': response.content,
                    'provider': response.provider,
                    'total_files': len(security_reports),
                    'average_score': sum(scores) / len(scores) if scores else 0,
                    'scores': scores
                }
            else:
                return {
                    'error': response.error,
                    'total_files': len(security_reports)
                }
                
        except Exception as e:
            logger.error(f"Error generating security summary: {e}")
            return {'error': str(e)}
    
    def save_security_report(self, results: Dict[str, Any], output_file: str):
        """Save security audit report to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Security report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving security report: {e}")
    
    async def shutdown(self):
        """Shutdown the security auditor"""
        if self.ai_service:
            await self.ai_service.shutdown()

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='AI Security Auditor')
    parser.add_argument('--files', nargs='+', help='Files to audit')
    parser.add_argument('--directory', help='Directory to audit')
    parser.add_argument('--output', help='Output directory for security reports')
    parser.add_argument('--audit-type', default='comprehensive',
                      choices=['comprehensive', 'vulnerability', 'compliance', 'penetration'],
                      help='Type of security audit to perform')
    parser.add_argument('--extensions', nargs='+', default=['.py', '.js', '.ts'],
                      help='File extensions to audit')
    parser.add_argument('--report', default='security_report.md', help='Report file')
    
    args = parser.parse_args()
    
    auditor = AISecurityAuditor()
    
    try:
        await auditor.initialize()
        
        if args.files:
            # Audit specific files
            results = {
                'files_audited': 0,
                'security_reports': [],
                'timestamp': datetime.now().isoformat()
            }
            
            for file_path in args.files:
                logger.info(f"Auditing {file_path}")
                audit_result = await auditor.audit_file(file_path, args.audit_type)
                results['security_reports'].append(audit_result)
                if 'security_audit' in audit_result:
                    results['files_audited'] += 1
            
            # Generate summary
            results['summary'] = await auditor._generate_security_summary(results['security_reports'])
            
        elif args.directory and args.output:
            # Audit directory
            results = await auditor.audit_directory(
                args.directory, args.output, args.audit_type, args.extensions
            )
        
        else:
            logger.error("Please specify either --files or --directory with --output")
            return
        
        # Save report
        auditor.save_security_report(results, args.report)
        
        # Print summary
        if 'summary' in results and 'summary' in results['summary']:
            print("\n" + "="*50)
            print("AI SECURITY AUDIT SUMMARY")
            print("="*50)
            print(results['summary']['summary'])
            if 'average_score' in results['summary']:
                print(f"\nAverage Security Score: {results['summary']['average_score']:.1f}/10")
            print("="*50)
        
        logger.info(f"Security audit complete. {results['files_audited']} files audited.")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)
    
    finally:
        await auditor.shutdown()

if __name__ == "__main__":
    asyncio.run(main())