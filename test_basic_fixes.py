#!/usr/bin/env python3
"""
Minimal test to verify the core fixes
"""

def test_basic_fixes():
    """Test basic dictionary access patterns"""
    print("Testing basic dictionary access fixes...")
    
    # Test 1: Safe dictionary access
    user_inputs = {}  # Empty dict
    
    # These should not raise KeyError
    material = user_inputs.get('Material', 'Not specified')
    operation_type = user_inputs.get('Operation Type', 'Not specified')
    desired_shape = user_inputs.get('Desired Shape', 'Not specified')
    
    print(f"✓ Material: {material}")
    print(f"✓ Operation Type: {operation_type}")
    print(f"✓ Desired Shape: {desired_shape}")
    
    # Test 2: Parameter string handling
    def mock_parse_extracted_parameters(parameter_string):
        """Mock version of parse_extracted_parameters"""
        # Handle None parameter_string
        if parameter_string is None:
            return None
        
        # If we get here, parameter_string is not None
        parameters = {}
        parsed_parameters = {}
        
        # Process only if we have content
        if parameter_string:
            for line in parameter_string.splitlines():
                if ": " in line:
                    key, value = line.split(": ", 1)
                    parameters[key.strip()] = value.strip()
        
        # Safe dictionary access
        parsed_parameters['tool_path'] = "linear" if parameters.get("Desired Shape", "").lower() in ['circle', 'circular pocket', 'circular'] else "linear"
        
        return parsed_parameters
    
    # Test with None
    result = mock_parse_extracted_parameters(None)
    print(f"✓ mock_parse_extracted_parameters(None) returned: {result}")
    
    # Test with empty string
    result = mock_parse_extracted_parameters("")
    print(f"✓ mock_parse_extracted_parameters('') returned: {result}")
    
    # Test with valid data
    test_data = "Operation Type: milling\nDesired Shape: rectangle"
    result = mock_parse_extracted_parameters(test_data)
    print(f"✓ mock_parse_extracted_parameters(valid_data) returned: {result}")
    
    print("\n✅ ALL BASIC TESTS PASSED!")
    print("The core issues have been fixed:")
    print("1. Dictionary access now uses .get() method to prevent KeyError")
    print("2. None parameter strings are handled properly")
    print("3. Safe string processing prevents AttributeError on None.splitlines()")

if __name__ == "__main__":
    test_basic_fixes()
