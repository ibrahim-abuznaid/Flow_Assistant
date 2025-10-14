# Code Generation Tool for ActivePieces

## Overview

The AI assistant now has a dedicated tool for generating TypeScript code pieces for ActivePieces automation flows. This ensures all generated code follows best practices and ActivePieces conventions.

## How It Works

### 1. **Automatic Code Generation**
When a user asks to create code for a flow step, the agent automatically calls the `get_code_generation_guidelines` tool to retrieve comprehensive guidelines before generating code.

### 2. **Context-Aware Guidelines**
The tool provides different guidelines based on the type of code being generated:
- `general` - Standard code generation guidelines
- `api_call` - Specific guidance for API integrations
- `data_transform` - Guidelines for data transformation steps

### 3. **Tool Usage**

```python
# The agent calls this tool before generating code
get_code_generation_guidelines(context="api_call")
```

## Key Guidelines Provided

### Core Concepts
✅ Code is for a SINGLE STEP in a flow, not a backend service  
✅ Previous steps provide inputs  
✅ Next steps use outputs  
✅ Authentication comes from flow connections  
✅ Each step does ONE thing well  

### Function Requirements
- Must start with `export const code =`
- Must be an async function
- Must have proper TypeScript input types
- Must return data for next steps
- Keep it simple and focused

### HTTP Requests
- Use native `fetch` API (no external libraries)
- Check `response.ok` before processing
- Simple, clear error handling
- Return structured data

### Input Parameters
- Accept inputs from previous steps
- Expect tokens/credentials from connections
- NO OAuth flows in code
- NO environment variables
- Use `{{ }}` syntax for dynamic values:
  - Numbers: `{{ 500 }}`
  - Arrays: `{{ [1,2,3] }}`
  - Objects: `{{ {"key": "value"} }}`

### Output Format

All code generations return JSON with:

```json
{
  "code": "export const code = async (inputs: { ... }) => { ... }",
  "inputs": [
    {
      "name": "inputName",
      "description": "What this input is for",
      "suggestedValue": "Example value or hint"
    }
  ],
  "title": "Short Action Name"
}
```

## Examples

### Example 1: API Call
```json
{
  "code": "export const code = async (inputs: { accessToken: string, userId: string }) => {\n  const response = await fetch(`https://api.example.com/users/${inputs.userId}`, {\n    headers: {\n      'Authorization': `Bearer ${inputs.accessToken}`,\n      'Content-Type': 'application/json'\n    }\n  });\n\n  if (!response.ok) {\n    throw new Error(`API error: ${response.statusText}`);\n  }\n\n  const data = await response.json();\n  return { user: data };\n}",
  "inputs": [
    {
      "name": "accessToken",
      "description": "API access token from connection",
      "suggestedValue": "Your API access token"
    },
    {
      "name": "userId",
      "description": "User ID to fetch",
      "suggestedValue": "{{ trigger.userId }}"
    }
  ],
  "title": "Fetch User Data"
}
```

### Example 2: Data Transformation
```json
{
  "code": "export const code = async (inputs: { items: any[], filterKey: string, filterValue: any }) => {\n  const filtered = inputs.items.filter(item => \n    item[inputs.filterKey] === inputs.filterValue\n  );\n  \n  return { \n    filtered: filtered,\n    count: filtered.length \n  };\n}",
  "inputs": [
    {
      "name": "items",
      "description": "Array of items to filter",
      "suggestedValue": "{{ previousStep.data }}"
    },
    {
      "name": "filterKey",
      "description": "Property name to filter by",
      "suggestedValue": "status"
    },
    {
      "name": "filterValue",
      "description": "Value to match",
      "suggestedValue": "active"
    }
  ],
  "title": "Filter Items"
}
```

## Agent Workflow

When a user requests code generation:

1. **Agent receives request** to create code for a flow step
2. **Agent calls** `get_code_generation_guidelines(context="appropriate_context")`
3. **Tool returns** comprehensive guidelines and examples
4. **Agent generates code** following the guidelines exactly
5. **Agent returns** properly formatted JSON with code, inputs, and title

## Common Use Cases

### API Integration
```
User: "Create code to fetch user data from an API"
Agent: 
  1. Calls get_code_generation_guidelines(context="api_call")
  2. Gets API-specific guidelines
  3. Generates code with proper fetch, auth headers, error handling
  4. Returns formatted JSON
```

### Data Processing
```
User: "Create code to filter an array of objects"
Agent:
  1. Calls get_code_generation_guidelines(context="data_transform")
  2. Gets data transformation guidelines
  3. Generates simple filter code
  4. Returns formatted JSON
```

### Custom Logic
```
User: "Create code to calculate total from items"
Agent:
  1. Calls get_code_generation_guidelines(context="general")
  2. Gets general guidelines
  3. Generates calculation code
  4. Returns formatted JSON
```

## Best Practices

### DO ✅
- Call the tool BEFORE generating any code
- Use the appropriate context ("api_call", "data_transform", "general")
- Follow the guidelines exactly
- Keep code simple and focused on one operation
- Return data that next steps can use
- Use descriptive input names and descriptions
- Provide helpful suggestedValue hints

### DON'T ❌
- Generate code without calling the tool first
- Try to do multiple operations in one step
- Use external libraries unnecessarily
- Implement OAuth flows in code
- Use environment variables
- Create overly complex error handling
- Make titles too long or vague

## Integration with Frontend

The frontend (Build Flow mode) expects this exact JSON format:

```typescript
interface CodeResponse {
  code: string;        // TypeScript code starting with "export const code ="
  inputs: Array<{
    name: string;
    description: string;
    suggestedValue: string;
  }>;
  title: string;       // 2-4 words, action-oriented
}
```

## Testing the Tool

### Test 1: Basic Code Generation
```
User: "Create code to send a POST request"
Expected: Agent calls get_code_generation_guidelines, generates proper code
```

### Test 2: With Context
```
User: "Create code to transform JSON data"
Expected: Agent uses context="data_transform", gets specific guidelines
```

### Test 3: Complex Example
```
User: "Create code to fetch Gmail messages using the Google API"
Expected: Agent follows examples, generates proper SDK usage with auth
```

## Troubleshooting

### Issue: Code doesn't start with "export const code ="
**Solution**: Agent must call the tool first to get requirements

### Issue: Missing input descriptions
**Solution**: Tool provides template with description requirements

### Issue: OAuth flow in generated code
**Solution**: Guidelines explicitly forbid this - auth comes from connections

### Issue: Using external libraries incorrectly
**Solution**: Guidelines specify to use native fetch API

## Future Enhancements

Potential improvements:
1. Add more context types (database, file operations, etc.)
2. Include library availability checker
3. Add code validation before returning
4. Provide code optimization suggestions
5. Support for other languages (Python, Go, etc.)

## Summary

The `get_code_generation_guidelines` tool ensures:
- ✅ Consistent code quality
- ✅ Proper ActivePieces conventions
- ✅ Best practices for flow steps
- ✅ Correct input/output handling
- ✅ User-friendly code with helpful hints

This makes the AI assistant a reliable code generation partner for ActivePieces automation flows.

