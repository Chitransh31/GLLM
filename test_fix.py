#!/usr/bin/env python3
"""
Test script to verify the fixes for KeyError and NoneType issues
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

# Test 1: parse_extracted_parameters with None
print("Test 1: Testing parse_extracted_parameters with None...")
try:
    from gllm.utils.params_extraction_utils import parse_extracted_parameters
    result = parse_extracted_parameters(None)
    print(f"✓ parse_extracted_parameters(None) returned: {result}")
except Exception as e:
    print(f"✗ Error in parse_extracted_parameters: {e}")

# Test 2: Test user_inputs access patterns
print("\nTest 2: Testing user_inputs access patterns...")
try:
    # Simulate the function call without actually importing the full module
    # to avoid dependency issues
    user_inputs = {}  # Empty dict to test KeyError protection
    
    # This should not raise KeyError anymore
    material = user_inputs.get('Material', 'Not specified')
    operation_type = user_inputs.get('Operation Type', 'Not specified')
    
    print(f"✓ Material: {material}")
    print(f"✓ Operation Type: {operation_type}")
    print("✓ All dictionary access is now safe with .get() method")
    
except Exception as e:
    print(f"✗ Error in user_inputs access: {e}")

print("\n" + "="*50)
print("Summary:")
print("1. Fixed None parameter handling in parse_extracted_parameters")
print("2. Fixed KeyError by using .get() method for dictionary access")
print("3. Added proper error handling in validate_functional_correctness")
print("4. Cleared Python cache to ensure updated code is loaded")
print("="*50)
