# Context for AI Agent: Code Generation for ActivePieces

## 🤖 When to Use This Context

Use this information whenever a user asks you to:
- Generate code for ActivePieces
- Create a code piece/step
- Write TypeScript for a flow
- Build custom logic for automation
- Create API integrations via code

## 🔧 Tool to Call First

**ALWAYS** call `get_code_generation_guidelines` before generating any code:

```python
# Example tool call
get_code_generation_guidelines(context="api_call")  # For API calls
get_code_generation_guidelines(context="data_transform")  # For data processing
get_code_generation_guidelines(context="general")  # For general code
```

## 📋 Core Principles

### 1. What You're Creating
- ✅ Code for ONE STEP in a flow
- ✅ Part of a larger automation
- ❌ NOT a standalone backend service
- ❌ NOT a complete application

### 2. Flow Context
```
[Trigger] → [Step 1] → [YOUR CODE] → [Step 3] → ...
                           ↑
                    This is what you create
```

- Previous steps provide inputs
- Your code processes data
- Next steps use your outputs
- Authentication comes from connections

## 🎯 Required Output Format

**ALWAYS return JSON with exactly 3 fields:**

```json
{
  "code": "export const code = async (inputs: { ... }) => { ... }",
  "inputs": [
    {
      "name": "inputName",
      "description": "Clear description of what this is",
      "suggestedValue": "Example value or {{ previousStep.data }}"
    }
  ],
  "title": "Action Name"
}
```

## ✅ Code Requirements Checklist

### Function Structure
- [ ] Starts with `export const code =`
- [ ] Is an async function
- [ ] Has TypeScript types: `inputs: { param: type }`
- [ ] Returns an object with data for next steps
- [ ] Focuses on ONE operation

### HTTP Requests (if needed)
- [ ] Uses native `fetch` API (NOT axios, request, etc.)
- [ ] Checks `response.ok` before processing
- [ ] Has simple error handling
- [ ] Returns parsed JSON

### Input Parameters
- [ ] Accept from previous steps or connections
- [ ] Use correct syntax for values:
  - String literals: `"hello"`
  - Numbers: `{{ 500 }}`
  - Arrays: `{{ [1,2,3] }}`
  - Objects: `{{ {"key": "value"} }}`
- [ ] Each input has name, description, suggestedValue

### Title
- [ ] 2-4 words maximum
- [ ] Action-oriented (verb + noun)
- [ ] Examples: "Send Email", "Fetch Data", "Transform JSON"

## ❌ What NOT to Include

**NEVER add these to generated code:**
- ❌ OAuth flows or token generation
- ❌ Environment variables (`process.env.*`)
- ❌ Client IDs or secrets
- ❌ Redirect URLs
- ❌ Multiple operations in one function
- ❌ External HTTP libraries (axios, request)
- ❌ Complex error handling
- ❌ Database connections (unless specifically requested)

## 📝 Template Examples

### Template 1: API Call
```typescript
export const code = async (inputs: { 
  accessToken: string, 
  userId: string 
}) => {
  const response = await fetch(`https://api.example.com/users/${inputs.userId}`, {
    headers: {
      'Authorization': `Bearer ${inputs.accessToken}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  const data = await response.json();
  return { user: data };
}
```

**Inputs:**
```json
[
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
]
```

**Title:** `"Fetch User Data"`

### Template 2: Data Transformation
```typescript
export const code = async (inputs: { 
  items: any[], 
  filterKey: string, 
  filterValue: any 
}) => {
  const filtered = inputs.items.filter(item => 
    item[inputs.filterKey] === inputs.filterValue
  );
  
  return { 
    filtered: filtered,
    count: filtered.length 
  };
}
```

**Inputs:**
```json
[
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
]
```

**Title:** `"Filter Items"`

### Template 3: POST Request
```typescript
export const code = async (inputs: { 
  apiUrl: string, 
  apiKey: string, 
  data: any 
}) => {
  const response = await fetch(inputs.apiUrl, {
    method: 'POST',
    headers: {
      'X-API-Key': inputs.apiKey,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(inputs.data)
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.statusText}`);
  }

  return await response.json();
}
```

**Inputs:**
```json
[
  {
    "name": "apiUrl",
    "description": "API endpoint URL",
    "suggestedValue": "https://api.example.com/endpoint"
  },
  {
    "name": "apiKey",
    "description": "API key for authentication",
    "suggestedValue": "Your API key"
  },
  {
    "name": "data",
    "description": "Data to send in request body",
    "suggestedValue": "{{ previousStep.result }}"
  }
]
```

**Title:** `"Send POST Request"`

## 🔄 Your Workflow as AI Agent

1. **User asks for code** (e.g., "Create code to fetch user data")

2. **Call the tool:**
   ```python
   get_code_generation_guidelines(context="api_call")
   ```

3. **Read the guidelines** returned by the tool

4. **Generate code** following the guidelines exactly

5. **Return formatted JSON** with:
   - `code` field (TypeScript starting with `export const code =`)
   - `inputs` array (each with name, description, suggestedValue)
   - `title` string (2-4 words, action-oriented)

6. **Explain to user:**
   - What the code does
   - What inputs they need to provide
   - How to use it in their flow

## 🎯 Input Value Syntax Reference

| Type | Example | Syntax |
|------|---------|--------|
| String literal | "hello" | `"hello"` |
| Number | 500 | `{{ 500 }}` |
| Boolean | true | `{{ true }}` |
| Array of numbers | [1,2,3] | `{{ [1,2,3,4] }}` |
| Array of strings | ["a","b"] | `{{ ["apple", "banana"] }}` |
| Object | {key:"val"} | `{{ {"key": "value"} }}` |
| Array of objects | [{...}] | `{{ [{"key": "v1"}] }}` |
| Previous step data | - | `{{ previousStep.data }}` |
| Trigger data | - | `{{ trigger.userId }}` |

## 💡 Common Scenarios

### Scenario 1: User wants to call an external API
1. Call `get_code_generation_guidelines(context="api_call")`
2. Generate code using `fetch`
3. Accept `accessToken` from connection input
4. Accept API-specific parameters
5. Return parsed response data

### Scenario 2: User wants to transform data
1. Call `get_code_generation_guidelines(context="data_transform")`
2. Generate code using map/filter/reduce
3. Accept data from previous step: `{{ previousStep.output }}`
4. Return transformed data

### Scenario 3: User wants custom logic
1. Call `get_code_generation_guidelines(context="general")`
2. Keep logic simple and focused
3. Accept necessary inputs
4. Return result for next step

## 🚫 Common Mistakes to Avoid

1. **Forgetting to call the tool first** ❌
   - Always call `get_code_generation_guidelines` before generating code

2. **Wrong function start** ❌
   ```typescript
   // WRONG
   async function code(inputs) { }
   
   // CORRECT
   export const code = async (inputs: { ... }) => { }
   ```

3. **Missing TypeScript types** ❌
   ```typescript
   // WRONG
   (inputs) => { }
   
   // CORRECT
   (inputs: { accessToken: string, data: any }) => { }
   ```

4. **Not returning data** ❌
   ```typescript
   // WRONG
   const result = data.filter(...);
   // function ends without return
   
   // CORRECT
   const result = data.filter(...);
   return { filtered: result };
   ```

5. **Using external libraries** ❌
   ```typescript
   // WRONG
   import axios from 'axios';
   const response = await axios.get(url);
   
   // CORRECT
   const response = await fetch(url);
   ```

6. **Complex error handling** ❌
   ```typescript
   // WRONG
   try {
     // complex retry logic
     // multiple error types
     // logging, alerts, etc.
   }
   
   // CORRECT
   if (!response.ok) {
     throw new Error(`API error: ${response.statusText}`);
   }
   ```

## ✅ Quality Checklist

Before returning code to user, verify:

- [ ] Called `get_code_generation_guidelines` tool first
- [ ] Code starts with `export const code =`
- [ ] Code is an async function
- [ ] TypeScript types for all inputs
- [ ] Returns data for next steps
- [ ] Uses `fetch` for HTTP (not axios/request)
- [ ] Simple error handling (check response.ok)
- [ ] Each input has name, description, suggestedValue
- [ ] SuggestedValue uses correct `{{ }}` syntax
- [ ] Title is 2-4 words, action-oriented
- [ ] No OAuth flows in code
- [ ] No environment variables
- [ ] No hardcoded secrets
- [ ] Focuses on ONE operation

## 📚 Additional Resources

- **Full Guide**: `docs/features/CODE_GENERATION_GUIDE.md`
- **Quick Reference**: `QUICK_CODE_GENERATION_REFERENCE.md`
- **Implementation**: `CODE_GENERATION_TOOL_SUMMARY.md`

## 🎓 Remember

**You are generating code for a STEP in a flow, not a complete application.**

- Keep it simple
- Focus on one task
- Accept inputs from previous steps
- Return data for next steps
- Let the flow orchestrate complexity

**Always call the tool first, follow the guidelines, and generate clean, focused code!**

