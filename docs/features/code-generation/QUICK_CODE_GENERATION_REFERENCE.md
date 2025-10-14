# Quick Code Generation Reference

## 🎯 One-Line Summary
**The AI assistant now has a built-in tool that provides guidelines for generating TypeScript code for ActivePieces automation flows.**

---

## 🔧 Tool Name
`get_code_generation_guidelines`

## 📥 Input
- `context` (optional): `"general"`, `"api_call"`, or `"data_transform"`

## 📤 Output Format
```json
{
  "code": "export const code = async (inputs: { ... }) => { ... }",
  "inputs": [
    {
      "name": "inputName",
      "description": "What this input is for",
      "suggestedValue": "Example value"
    }
  ],
  "title": "Action Name"
}
```

---

## ✅ Must Have

### Function Structure
- Start with `export const code =`
- Async function
- TypeScript input types
- Return value for next steps

### HTTP Requests
- Use native `fetch` API
- Check `response.ok`
- Simple error handling

### Input Values Syntax
| Type | Syntax | Example |
|------|--------|---------|
| Number | `{{ number }}` | `{{ 500 }}` |
| Array | `{{ [items] }}` | `{{ [1,2,3,4] }}` |
| String Array | `{{ ["items"] }}` | `{{ ["a", "b"] }}` |
| Object | `{{ {key: val} }}` | `{{ {"key": "value"} }}` |
| Object Array | `{{ [{...}] }}` | `{{ [{"k": "v1"}] }}` |

---

## ❌ Never Include

- ❌ OAuth flows or token generation
- ❌ Environment variables
- ❌ Client IDs or secrets
- ❌ Redirect URLs
- ❌ Multiple operations in one step
- ❌ External HTTP libraries (axios, request, etc.)

---

## 🚀 Quick Examples

### API Call
```typescript
export const code = async (inputs: { accessToken: string, userId: string }) => {
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

### Data Transform
```typescript
export const code = async (inputs: { items: any[], filterKey: string, filterValue: any }) => {
  const filtered = inputs.items.filter(item => 
    item[inputs.filterKey] === inputs.filterValue
  );
  
  return { 
    filtered: filtered,
    count: filtered.length 
  };
}
```

---

## 🎯 Title Guidelines
- **2-4 words**
- **Action-oriented** (verb + noun)
- Examples: `"Send Email"`, `"Query Database"`, `"Transform JSON"`, `"Fetch User Data"`

---

## 💡 How to Use

### As a User
Just ask the AI:
- "Create code to fetch user data"
- "Generate code to filter an array"
- "Write code to send a POST request"

### As a Developer
```python
from src.tools import get_code_generation_guidelines

# Get guidelines
guidelines = get_code_generation_guidelines.invoke({
    "context": "api_call"  # or "data_transform" or "general"
})
```

---

## 📋 Checklist for Generated Code

- [ ] Starts with `export const code =`
- [ ] Is an async function
- [ ] Has TypeScript types for inputs
- [ ] Returns data for next steps
- [ ] Uses fetch API (if making HTTP calls)
- [ ] Has simple error handling
- [ ] Inputs use correct `{{ }}` syntax for non-literals
- [ ] Title is 2-4 words, action-oriented
- [ ] Focuses on ONE operation
- [ ] No hardcoded secrets

---

## 🔗 Related Files

- **Full Guide**: `docs/features/CODE_GENERATION_GUIDE.md`
- **Implementation**: `src/tools.py` (line 355+)
- **Summary**: `CODE_GENERATION_TOOL_SUMMARY.md`
- **Tests**: `tests/test_code_generation_simple.py`

---

## 🆘 Common Issues

| Issue | Solution |
|-------|----------|
| Code doesn't start correctly | Must start with `export const code =` |
| Missing input descriptions | Each input needs name, description, suggestedValue |
| OAuth in code | Auth comes from connections, not code |
| Using axios/request | Use native `fetch` API instead |
| Long title | Keep to 2-4 words, action-oriented |

---

**Last Updated**: Based on the original TypeScript prompt from the frontend code generation system

