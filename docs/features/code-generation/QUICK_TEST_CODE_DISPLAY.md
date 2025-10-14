# Quick Test - Code Display Fix

## 🚀 Test It Right Now!

### Step 1: Start the App

**Terminal 1 - Backend:**
```bash
uvicorn src.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Step 2: Test Questions

Try these in the chat:

#### Test 1: Code Generation
```
Create code to fetch user data from an API
```
**Expected:** TypeScript code with syntax highlighting

#### Test 2: JSON Display
```
Show me a JSON example of code inputs
```
**Expected:** Formatted JSON in code box

#### Test 3: Multiple Code Blocks
```
Create code to filter an array and show the JSON inputs
```
**Expected:** Both TypeScript and JSON with highlighting

#### Test 4: Inline Code
```
How do I use the fetch API?
```
**Expected:** Inline code like `fetch()` with gray background

---

## ✅ What to Look For

### Code Blocks Should Have:
- ✅ Dark theme (VS Code Dark Plus)
- ✅ Syntax highlighting (colored keywords)
- ✅ Proper spacing
- ✅ Rounded corners
- ✅ Shadow effect
- ✅ Scrollable if long

### Inline Code Should Have:
- ✅ Gray background
- ✅ Monospace font
- ✅ Padding around text

### Markdown Should Work:
- ✅ **Bold text**
- ✅ *Italic text*
- ✅ Headers
- ✅ Lists
- ✅ Links

---

## 🎯 Quick Examples

### Example 1:
**Ask:** "Create code to send a POST request"

**You'll See:**
```typescript
export const code = async (inputs: { apiUrl: string, data: any }) => {
  const response = await fetch(inputs.apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(inputs.data)
  });
  
  if (!response.ok) {
    throw new Error(`Request failed: ${response.statusText}`);
  }
  
  return await response.json();
}
```

### Example 2:
**Ask:** "Show me JSON for code inputs"

**You'll See:**
```json
{
  "inputs": [
    {
      "name": "apiUrl",
      "description": "API endpoint URL",
      "suggestedValue": "https://api.example.com/data"
    }
  ],
  "title": "Send POST Request"
}
```

---

## 🔥 Pro Tips

1. **Code will auto-scroll** if longer than 600px
2. **Copy works perfectly** - just select and copy
3. **Works in dark/light** messages
4. **Session viewer** also has highlighting

---

## ❌ If Something's Wrong

### Code Not Highlighted?
**Check:** Agent should wrap in \`\`\`typescript or \`\`\`json

### Plain Text?
**Restart:** Both backend and frontend

### Still Issues?
**Check Console:** Open browser DevTools (F12)

---

## ✅ Success Indicators

You know it's working when:
- Code has colors (not just black text)
- Code boxes have dark background
- JSON is properly formatted
- You can copy code easily
- No weird formatting errors

---

**Ready to test? Start the app and ask for code!** 🚀

