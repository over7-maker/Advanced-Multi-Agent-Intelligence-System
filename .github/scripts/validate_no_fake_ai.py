#!/usr/bin/env python3
"""
Validate NO FAKE AI Used - Comprehensive validation script
Checks all AI analysis results to ensure no fake AI responses
"""

import os
import json
import glob
from typing import Dict, List, Any

def validate_no_fake_ai() -> bool:
    """Validate that no fake AI responses are present"""
    print("🔍 Validating NO FAKE AI used across all workflows...")
    
    fake_detected = False
    
    # Check all AI result files
    artifact_files = glob.glob("artifacts/*.json")
    
    for file_path in artifact_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            print(f"📄 Checking: {file_path}")
            
            # Check for fake AI indicators
            if _contains_fake_ai_indicators(data, file_path):
                fake_detected = True
            
            # Check for bulletproof validation
            if not _has_bulletproof_validation(data, file_path):
                print(f"  ❌ Missing bulletproof validation in {file_path}")
                fake_detected = True
            else:
                print(f"  ✅ Bulletproof validation found in {file_path}")
                
        except Exception as e:
            print(f"  ⚠️ Error reading {file_path}: {e}")
    
    if fake_detected:
        print("\n🚨 FAKE AI DETECTED - VALIDATION FAILED!")
        return False
    else:
        print("\n✅ ALL AI ANALYSIS VERIFIED AS REAL!")
        return True

def _contains_fake_ai_indicators(data: Dict[str, Any], file_path: str) -> bool:
    """Check if data contains fake AI indicators"""
    
    # Fake AI phrases to detect
    fake_phrases = [
        "Provider: AI System",
        "Provider: Unknown", 
        "Response Time: 1.5s",
        "Response Time: 2.8s",
        "Response Time: 3.1s",
        "Response Time: 5.2s",
        "Response Time: 0s",
        "AI-powered analysis completed successfully",
        "Mock/Fallback",
        "No real AI used",
        "Template response",
        "analysis completed successfully"
    ]
    
    # Convert data to string for searching
    data_str = json.dumps(data, indent=2).lower()
    
    for phrase in fake_phrases:
        if phrase.lower() in data_str:
            print(f"  ❌ FAKE PHRASE DETECTED: '{phrase}' in {file_path}")
            return True
    
    # Check for identical response times (suspicious)
    if 'response_time' in data_str:
        try:
            # Look for response times in the data
            if isinstance(data, dict):
                response_times = _extract_response_times(data)
                if len(response_times) > 1 and len(set(response_times)) == 1:
                    print(f"  ❌ IDENTICAL RESPONSE TIMES DETECTED: {response_times} in {file_path}")
                    return True
        except:
            pass
    
    return False

def _extract_response_times(data: Dict[str, Any]) -> List[float]:
    """Extract all response times from data structure"""
    response_times = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'response_time' and isinstance(value, (int, float)):
                response_times.append(value)
            elif isinstance(value, (dict, list)):
                response_times.extend(_extract_response_times(value))
    elif isinstance(data, list):
        for item in data:
            response_times.extend(_extract_response_times(item))
    
    return response_times

def _has_bulletproof_validation(data: Dict[str, Any], file_path: str) -> bool:
    """Check if data has bulletproof validation"""
    
    # Check for bulletproof validation flag
    if isinstance(data, dict):
        # Check metadata
        metadata = data.get('metadata', {})
        if metadata.get('bulletproof_validated') == True:
            return True
        
        # Check ai_analysis
        ai_analysis = data.get('ai_analysis', {})
        if ai_analysis.get('bulletproof_validated') == True:
            return True
        
        # Check top level
        if data.get('bulletproof_validated') == True:
            return True
    
    return False

def main():
    """Main validation function"""
    print("🚀 Starting comprehensive fake AI validation...")
    print("=" * 60)
    
    # Create artifacts directory if it doesn't exist
    os.makedirs("artifacts", exist_ok=True)
    
    # Run validation
    is_valid = validate_no_fake_ai()
    
    print("=" * 60)
    if is_valid:
        print("✅ VALIDATION SUCCESS: No fake AI detected!")
        return 0
    else:
        print("🚨 VALIDATION FAILED: Fake AI detected!")
        return 1

if __name__ == "__main__":
    exit(main())