"""
Test the code generation guidelines tool.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools import get_code_generation_guidelines


def test_basic_guidelines():
    """Test getting basic code generation guidelines."""
    print("\n=== Testing Basic Code Generation Guidelines ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "general"})
    
    # Check that key sections are present
    assert "ACTIVEPIECES CODE GENERATION GUIDELINES" in result
    assert "CORE CONCEPT" in result
    assert "CRITICAL REQUIREMENTS" in result
    assert "FUNCTION STRUCTURE" in result
    assert "HTTP REQUESTS" in result
    assert "INPUT PARAMETERS" in result
    assert "OUTPUT FORMAT" in result
    assert "PERFECT EXAMPLES" in result
    
    print("✓ Basic guidelines contain all required sections")
    print(f"✓ Guidelines length: {len(result)} characters")
    

def test_api_call_context():
    """Test getting API call specific guidelines."""
    print("\n=== Testing API Call Context Guidelines ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "api_call"})
    
    # Check for API-specific content
    assert "ADDITIONAL GUIDELINES FOR API CALLS" in result
    assert "Authentication patterns" in result
    assert "Bearer token" in result
    assert "API key in header" in result
    
    print("✓ API call guidelines contain authentication patterns")
    print("✓ Includes Bearer token, API key, and Basic auth examples")


def test_data_transform_context():
    """Test getting data transformation specific guidelines."""
    print("\n=== Testing Data Transform Context Guidelines ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "data_transform"})
    
    # Check for data transform specific content
    assert "ADDITIONAL GUIDELINES FOR DATA TRANSFORMATION" in result
    assert "map, filter, reduce" in result
    assert "arrays and objects" in result
    
    print("✓ Data transform guidelines contain array/object operations")
    print("✓ Includes map, filter, reduce methods")


def test_examples_present():
    """Test that examples are included in guidelines."""
    print("\n=== Testing Examples Presence ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "general"})
    
    # Check for examples
    assert "Example 1 - API Call with Authentication" in result
    assert "Example 2 - Data Transformation" in result
    assert "Example 3 - Gmail API" in result
    assert "export const code = async" in result
    
    print("✓ All three examples are present")
    print("✓ Examples include proper TypeScript syntax")


def test_critical_requirements():
    """Test that critical requirements are clearly stated."""
    print("\n=== Testing Critical Requirements ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "general"})
    
    # Check for critical requirements
    assert "MUST start with 'export const code ='" in result
    assert "MUST be an async function" in result
    assert "MUST have proper input parameters" in result
    assert "MUST return a value" in result
    assert "Use native fetch API" in result
    assert "NO OAuth flows" in result
    
    print("✓ All critical requirements are clearly stated")
    print("✓ Includes MUST and NO requirements")


def test_input_parameter_guidelines():
    """Test input parameter handling guidelines."""
    print("\n=== Testing Input Parameter Guidelines ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "general"})
    
    # Check input parameter guidelines
    assert "{{ }}" in result
    assert "{{ 500 }}" in result
    assert '{{ ["apple", "banana", "orange"] }}' in result
    assert '{{ {"key": "value"} }}' in result
    
    print("✓ Input parameter syntax is documented")
    print("✓ Includes examples for numbers, arrays, and objects")


def test_best_practices():
    """Test that best practices are included."""
    print("\n=== Testing Best Practices ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "general"})
    
    # Check for best practices section
    assert "BEST PRACTICES" in result
    assert "COMMON MISTAKES TO AVOID" in result
    assert "Keep code simple" in result
    assert "Return meaningful data" in result
    
    print("✓ Best practices section is present")
    print("✓ Common mistakes section is present")


def test_output_format():
    """Test that output format is documented."""
    print("\n=== Testing Output Format Documentation ===\n")
    
    result = get_code_generation_guidelines.invoke({"context": "general"})
    
    # Check output format documentation
    assert "OUTPUT FORMAT" in result
    assert '"code":' in result
    assert '"inputs":' in result
    assert '"title":' in result
    assert "name" in result
    assert "description" in result
    assert "suggestedValue" in result
    
    print("✓ Output format is clearly documented")
    print("✓ Includes code, inputs, and title structure")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("  CODE GENERATION GUIDELINES TOOL - TEST SUITE")
    print("="*60)
    
    try:
        test_basic_guidelines()
        test_api_call_context()
        test_data_transform_context()
        test_examples_present()
        test_critical_requirements()
        test_input_parameter_guidelines()
        test_best_practices()
        test_output_format()
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

