"""
Prompt Maker Methodology
Structured approach to prompt engineering for intelligence operations
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class PromptMaker:
    """Prompt Maker for structured prompt engineering"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prompt_library = {}
        self.version_control = {}
        self.test_results = {}
        
    async def create_prompt(self, task_type: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt for a specific task type"""
        try:
            # Get base template for task type
            template = await self._get_template(task_type)
            
            # Customize template based on requirements
            customized_prompt = await self._customize_template(template, requirements)
            
            # Generate prompt ID
            prompt_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store in library
            self.prompt_library[prompt_id] = {
                'id': prompt_id,
                'task_type': task_type,
                'prompt': customized_prompt,
                'requirements': requirements,
                'created_at': datetime.now().isoformat(),
                'version': 1
            }
            
            logger.info(f"Created prompt {prompt_id} for task type {task_type}")
            return self.prompt_library[prompt_id]
            
        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            return {'error': str(e)}
    
    async def test_prompt(self, prompt_id: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test a prompt with various test cases"""
        try:
            if prompt_id not in self.prompt_library:
                return {'error': 'Prompt not found'}
            
            prompt_data = self.prompt_library[prompt_id]
            test_results = []
            
            for test_case in test_cases:
                # Execute prompt with test case
                result = await self._execute_prompt_test(prompt_data['prompt'], test_case)
                test_results.append({
                    'test_case': test_case,
                    'result': result,
                    'score': await self._score_result(result, test_case.get('expected'))
                })
            
            # Calculate overall score
            overall_score = sum(t['score'] for t in test_results) / len(test_results)
            
            # Store test results
            self.test_results[prompt_id] = {
                'test_results': test_results,
                'overall_score': overall_score,
                'tested_at': datetime.now().isoformat()
            }
            
            return {
                'prompt_id': prompt_id,
                'overall_score': overall_score,
                'test_results': test_results
            }
            
        except Exception as e:
            logger.error(f"Error testing prompt: {e}")
            return {'error': str(e)}
    
    async def refine_prompt(self, prompt_id: str, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Refine a prompt based on feedback"""
        try:
            if prompt_id not in self.prompt_library:
                return {'error': 'Prompt not found'}
            
            current_prompt = self.prompt_library[prompt_id]
            
            # Apply refinements
            refined_prompt = await self._apply_refinements(current_prompt['prompt'], feedback)
            
            # Create new version
            new_version = current_prompt['version'] + 1
            new_prompt_id = f"{prompt_id}_v{new_version}"
            
            self.prompt_library[new_prompt_id] = {
                'id': new_prompt_id,
                'task_type': current_prompt['task_type'],
                'prompt': refined_prompt,
                'requirements': current_prompt['requirements'],
                'created_at': datetime.now().isoformat(),
                'version': new_version,
                'parent_id': prompt_id
            }
            
            logger.info(f"Refined prompt {prompt_id} to version {new_version}")
            return self.prompt_library[new_prompt_id]
            
        except Exception as e:
            logger.error(f"Error refining prompt: {e}")
            return {'error': str(e)}
    
    async def _get_template(self, task_type: str) -> str:
        """Get base template for task type"""
        templates = {
            'osint': """
            You are an OSINT intelligence agent. Your task is to:
            1. Collect information from open sources
            2. Analyze the collected data
            3. Identify key entities and relationships
            4. Generate intelligence insights
            
            Task: {task_description}
            Sources: {sources}
            Keywords: {keywords}
            
            Provide a comprehensive analysis.
            """,
            'investigation': """
            You are an investigation agent. Your task is to:
            1. Analyze evidence and data
            2. Identify connections and patterns
            3. Reconstruct timelines
            4. Assess threats and risks
            
            Task: {task_description}
            Evidence: {evidence}
            Timeline: {timeline}
            
            Provide detailed investigation findings.
            """,
            'forensics': """
            You are a forensics agent. Your task is to:
            1. Acquire digital evidence
            2. Analyze artifacts and metadata
            3. Reconstruct events
            4. Preserve chain of custody
            
            Task: {task_description}
            Evidence: {evidence}
            Artifacts: {artifacts}
            
            Provide forensics analysis report.
            """
        }
        
        return templates.get(task_type, "You are an intelligence agent. Complete the following task: {task_description}")
    
    async def _customize_template(self, template: str, requirements: Dict[str, Any]) -> str:
        """Customize template based on requirements"""
        customized = template
        
        # Replace placeholders with actual values
        for key, value in requirements.items():
            placeholder = f"{{{key}}}"
            if placeholder in customized:
                customized = customized.replace(placeholder, str(value))
        
        return customized
    
    async def _execute_prompt_test(self, prompt: str, test_case: Dict[str, Any]) -> str:
        """Execute prompt with test case"""
        # Mock implementation - would use actual LLM service
        return f"Test result for: {test_case.get('input', '')}"
    
    async def _score_result(self, result: str, expected: Optional[str]) -> float:
        """Score the result against expected output"""
        if not expected:
            return 0.5  # Default score if no expected output
        
        # Simple scoring based on keyword matching
        result_lower = result.lower()
        expected_lower = expected.lower()
        
        # Count matching words
        result_words = set(result_lower.split())
        expected_words = set(expected_lower.split())
        
        if not expected_words:
            return 0.5
        
        matches = len(result_words.intersection(expected_words))
        score = matches / len(expected_words)
        
        return min(score, 1.0)
    
    async def _apply_refinements(self, prompt: str, feedback: Dict[str, Any]) -> str:
        """Apply refinements to prompt based on feedback"""
        refined = prompt
        
        # Add clarity improvements
        if feedback.get('clarity_issues'):
            refined += "\n\nBe more specific and clear in your responses."
        
        # Add accuracy improvements
        if feedback.get('accuracy_issues'):
            refined += "\n\nEnsure accuracy and cite sources when possible."
        
        # Add structure improvements
        if feedback.get('structure_issues'):
            refined += "\n\nStructure your response with clear sections and bullet points."
        
        return refined
    
    async def get_prompt_library(self) -> Dict[str, Any]:
        """Get all prompts in the library"""
        return self.prompt_library
    
    async def get_prompt_versions(self, base_id: str) -> List[Dict[str, Any]]:
        """Get all versions of a prompt"""
        versions = []
        for prompt_id, prompt_data in self.prompt_library.items():
            if prompt_data.get('parent_id') == base_id or prompt_id == base_id:
                versions.append(prompt_data)
        
        return sorted(versions, key=lambda x: x['version'])
    
    async def get_best_prompt(self, task_type: str) -> Optional[Dict[str, Any]]:
        """Get the best performing prompt for a task type"""
        best_prompt = None
        best_score = 0.0
        
        for prompt_id, prompt_data in self.prompt_library.items():
            if prompt_data['task_type'] == task_type:
                if prompt_id in self.test_results:
                    score = self.test_results[prompt_id]['overall_score']
                    if score > best_score:
                        best_score = score
                        best_prompt = prompt_data
        
        return best_prompt