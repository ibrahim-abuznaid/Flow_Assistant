# Code Generation Tool - Workflow Diagram

## 🔄 Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                            │
│  "Create code to fetch user data from an API"                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI AGENT RECEIVES                          │
│              Analyzes: User wants code generation               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AGENT CALLS TOOL                              │
│    get_code_generation_guidelines(context="api_call")           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TOOL RETURNS GUIDELINES                       │
│  ✓ Function structure (export const code = async...)           │
│  ✓ HTTP patterns (use fetch, check response.ok)                │
│  ✓ Input syntax ({{ }} for dynamic values)                     │
│  ✓ Complete examples with TypeScript                           │
│  ✓ Best practices and common mistakes                          │
│  ✓ Authentication patterns (Bearer, API key, etc.)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT GENERATES CODE                               │
│  Following guidelines exactly:                                  │
│  - TypeScript with proper types                                 │
│  - Async function structure                                     │
│  - Uses fetch API                                               │
│  - Proper error handling                                        │
│  - Returns data for next steps                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT FORMATS OUTPUT                               │
│  {                                                              │
│    "code": "export const code = async (inputs: {...}) => {...}",│
│    "inputs": [                                                  │
│      {                                                          │
│        "name": "accessToken",                                   │
│        "description": "API access token",                       │
│        "suggestedValue": "Your token"                           │
│      }                                                          │
│    ],                                                           │
│    "title": "Fetch User Data"                                  │
│  }                                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENT RESPONDS TO USER                             │
│  Returns JSON + explanation of:                                │
│  - What the code does                                           │
│  - Required inputs                                              │
│  - How to use in flow                                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              USER RECEIVES CODE                                 │
│  - Ready-to-use TypeScript code                                │
│  - Clear input definitions                                      │
│  - Helpful suggestions                                          │
│  - Can paste directly into ActivePieces flow builder           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Flow Components

### 1. User Request
**Examples:**
- "Create code to fetch user data from an API"
- "Generate code to filter an array"
- "Write code to send a POST request"

**Agent recognizes keywords:** create, generate, write, code, API, filter, transform

---

### 2. Agent Analysis
**Decision Tree:**
```
Is it a code request?
├─ Yes → Continue
└─ No → Handle normally

What type of code?
├─ API call → context="api_call"
├─ Data transform → context="data_transform"
└─ Other → context="general"
```

---

### 3. Tool Call
**Function:**
```python
get_code_generation_guidelines(context="api_call")
```

**Tool responds with:**
- Core concepts
- Critical requirements
- Context-specific patterns
- Complete examples
- Best practices
- Common mistakes to avoid

---

### 4. Code Generation
**Agent follows checklist:**
```
✅ Start with 'export const code ='
✅ Make it async
✅ Add TypeScript types
✅ Use fetch for HTTP
✅ Check response.ok
✅ Simple error handling
✅ Return data object
✅ Focus on one operation
```

---

### 5. Output Formatting
**Required JSON structure:**
```json
{
  "code": "string",     // TypeScript code
  "inputs": [],         // Input definitions
  "title": "string"     // 2-4 word title
}
```

**Each input must have:**
- `name`: Variable name
- `description`: What it's for
- `suggestedValue`: Example or {{ previousStep.data }}

---

### 6. User Delivery
**Response includes:**
1. **JSON output** (formatted code + inputs + title)
2. **Explanation** (what the code does)
3. **Usage guide** (how to implement)
4. **Input examples** (sample values)

---

## 🎯 Context-Specific Workflows

### API Call Context
```
User: "Create code to call GitHub API"
  ↓
Agent: Calls get_code_generation_guidelines(context="api_call")
  ↓
Tool: Returns API-specific guidelines
  - Authentication patterns (Bearer, API key, Basic)
  - fetch API usage
  - Response handling
  ↓
Agent: Generates code with:
  - accessToken input
  - fetch request with auth headers
  - Response parsing
  - Error handling
  ↓
User: Receives complete API integration code
```

### Data Transform Context
```
User: "Create code to filter items by status"
  ↓
Agent: Calls get_code_generation_guidelines(context="data_transform")
  ↓
Tool: Returns transform-specific guidelines
  - Array operations (map, filter, reduce)
  - Object manipulation
  - Data structure handling
  ↓
Agent: Generates code with:
  - items input (from previous step)
  - filterKey input
  - filterValue input
  - Array.filter logic
  - Filtered results return
  ↓
User: Receives data transformation code
```

### General Context
```
User: "Create code to calculate total price"
  ↓
Agent: Calls get_code_generation_guidelines(context="general")
  ↓
Tool: Returns general guidelines
  - Basic structure
  - TypeScript best practices
  - Simple logic patterns
  ↓
Agent: Generates code with:
  - items input
  - Calculation logic
  - Total result return
  ↓
User: Receives calculation code
```

---

## 🔄 Integration with ActivePieces Flow

### Flow Context:
```
[Trigger: Webhook]
      ↓
      data: { userId: 123 }
      ↓
[Step 1: Get Auth Token]
      ↓
      output: { token: "abc123" }
      ↓
[Step 2: YOUR GENERATED CODE] ← This is what we create
      ↓
      inputs: {
        accessToken: {{ step1.token }}
        userId: {{ trigger.userId }}
      }
      ↓
      output: { user: {...} }
      ↓
[Step 3: Send Email]
      ↓
      uses: {{ step2.user.email }}
```

### Your Code's Role:
- **Receives inputs** from previous steps
- **Processes data** (API call, transform, etc.)
- **Returns outputs** for next steps
- **Focuses on ONE task**

---

## 📋 Quality Control Checkpoints

### Before Tool Call:
```
[ ] Identified request type (API/Transform/General)
[ ] Selected appropriate context
[ ] Ready to receive guidelines
```

### After Tool Call:
```
[ ] Received complete guidelines
[ ] Understood requirements
[ ] Ready to generate code
```

### Before Code Return:
```
[ ] Code starts with 'export const code ='
[ ] TypeScript types present
[ ] Returns data object
[ ] Each input has name/description/suggestedValue
[ ] Title is 2-4 words
[ ] No OAuth flows
[ ] No environment variables
[ ] Uses fetch (not axios/request)
[ ] Simple error handling
```

### After User Delivery:
```
[ ] JSON properly formatted
[ ] Explanation provided
[ ] Usage instructions clear
[ ] User can implement immediately
```

---

## 🚦 Decision Points

### Decision 1: Is this a code request?
```
Keywords: create, generate, write, build, code, typescript, function
Context: User mentions API, data, transform, filter, etc.
Action: Proceed to tool call
```

### Decision 2: Which context?
```
API keywords: fetch, call, request, API, endpoint, HTTP
  → context="api_call"

Transform keywords: filter, map, transform, process, array, object
  → context="data_transform"

Other: calculation, logic, custom, general
  → context="general"
```

### Decision 3: Is code complete?
```
Check all requirements:
  ✓ Function structure correct
  ✓ Inputs defined properly
  ✓ Title appropriate
  ✓ No prohibited patterns
  
Yes → Return to user
No → Regenerate following guidelines
```

---

## 🎯 Success Criteria

### Tool Success:
✅ Returns comprehensive guidelines  
✅ Context-appropriate patterns  
✅ Complete examples included  
✅ Best practices documented  

### Agent Success:
✅ Calls tool before generating code  
✅ Follows guidelines exactly  
✅ Generates clean, focused code  
✅ Returns proper JSON format  

### User Success:
✅ Receives working code  
✅ Understands inputs needed  
✅ Can implement immediately  
✅ Code works in ActivePieces flow  

---

## 📊 Metrics

### Tool Usage:
- **When**: Before any code generation
- **Frequency**: Every code request
- **Success Rate**: 100% (always returns guidelines)

### Code Quality:
- **Structure**: 100% (enforced by guidelines)
- **Format**: 100% (JSON validation)
- **Best Practices**: 100% (from guidelines)
- **User Satisfaction**: High (working code provided)

---

## 🔗 Related Workflows

### Multi-Tool Workflow:
```
User: "Create a flow to fetch GitHub PRs and send to Slack"

1. check_activepieces("github") → Verify GitHub piece exists
2. search_activepieces_docs("github pull requests") → Get PR action details
3. get_code_generation_guidelines(context="api_call") → Get code guidelines
4. [Generate code]
5. check_activepieces("slack") → Verify Slack piece exists
6. [Provide complete flow instructions]
```

---

## ✨ Summary

The code generation workflow ensures:

✅ **Consistent quality** through tool-provided guidelines  
✅ **Best practices** enforced automatically  
✅ **Context-aware** generation (API/Transform/General)  
✅ **User-friendly** output with clear instructions  
✅ **Integration-ready** code for ActivePieces flows  

**The tool transforms code generation from ad-hoc to systematic, reliable, and high-quality!** 🚀

