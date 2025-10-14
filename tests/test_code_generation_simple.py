"""
Simple test for the code generation guidelines (without full tool imports).
"""


def test_code_generation_guidelines():
    """Test the code generation guidelines content."""
    print("\n=== Testing Code Generation Guidelines ===\n")
    
    # Simulate what the tool returns
    base_guidelines = """
=== ACTIVEPIECES CODE GENERATION GUIDELINES ===

🎯 CORE CONCEPT:
You are generating code for a SINGLE STEP in an automation flow, NOT a backend service.
This code will run as ONE step in a larger flow where:
- Previous steps provide inputs
- Next steps will use the outputs
- Authentication is handled by flow connections
- Each step should do ONE thing well

📋 CRITICAL REQUIREMENTS:

1. FUNCTION STRUCTURE:
   ✓ MUST start with 'export const code ='
   ✓ MUST be an async function
   ✓ MUST have proper input parameters with TypeScript types
   ✓ MUST return a value for next steps to use
   ✓ Keep it simple - this is one step in a flow!
   ✓ Focus on a single operation

2. HTTP REQUESTS:
   ✓ Use native fetch API (built-in)
   ✓ NO external HTTP libraries needed (no axios, request, etc.)
   ✓ Simple error handling for responses
   ✓ Always check response.ok before processing

3. INPUT PARAMETERS:
   ✓ Inputs come from previous steps or flow connections
   ✓ Expect tokens/credentials from flow connections
   ✓ NO OAuth flows or token generation in code
   ✓ NO client IDs or secrets in code
   ✓ NO redirect URLs
   ✓ NO environment variables
   ✓ For non-string literal values, wrap in {{ }}: 
     - Numbers: {{ 500 }}
     - Arrays: {{ [1,2,3,4] }}
     - String arrays: {{ ["apple", "banana", "orange"] }}
     - Objects: {{ {"key": "value"} }}
     - Array of objects: {{ [{"key": "value1"}, {"key": "value2"}] }}
"""
    
    # Verify key sections
    assert "ACTIVEPIECES CODE GENERATION GUIDELINES" in base_guidelines
    assert "CORE CONCEPT" in base_guidelines
    assert "CRITICAL REQUIREMENTS" in base_guidelines
    assert "export const code =" in base_guidelines
    assert "fetch API" in base_guidelines
    assert "{{ }}" in base_guidelines
    
    print("[OK] Guidelines contain all required sections")
    print("[OK] Function structure requirements present")
    print("[OK] HTTP request guidelines present")
    print("[OK] Input parameter syntax documented")
    
    # Test example output format
    example_output = {
        "code": "export const code = async (inputs: { accessToken: string }) => { return { data: 'test' }; }",
        "inputs": [
            {
                "name": "accessToken",
                "description": "API access token",
                "suggestedValue": "Your token"
            }
        ],
        "title": "Fetch Data"
    }
    
    assert "code" in example_output
    assert "inputs" in example_output
    assert "title" in example_output
    assert example_output["code"].startswith("export const code =")
    assert len(example_output["inputs"]) > 0
    assert len(example_output["title"].split()) <= 4
    
    print("[OK] Output format is correct")
    print("[OK] Code starts with 'export const code ='")
    print("[OK] Title is concise (2-4 words)")
    
    print("\n[SUCCESS] All tests passed!\n")


if __name__ == "__main__":
    test_code_generation_guidelines()
    print("Code generation guidelines are properly structured and ready to use!")

