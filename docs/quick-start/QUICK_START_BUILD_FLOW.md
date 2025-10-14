# Quick Start: Build Flow Mode

## 🚀 Get Started in 3 Steps

### Step 1: Configure (One-time setup)

Add to your `.env` file:
```env
FLOW_BUILDER_MODEL=gpt-5-mini
```

### Step 2: Enable Build Flow Mode

In the web UI:
1. Find the **🔧 Build Flow Mode** checkbox above the input
2. Check it to enable
3. You'll see: "Build Flow Mode (Active)"

### Step 3: Ask!

Describe the flow you want to build:

**Simple Examples:**
```
Send an email when a new file is added to Google Drive
```
```
Post to Slack when a new row is added to Google Sheets
```

**Complex Examples:**
```
Automate my customer onboarding when they sign up through a form
```

## What You Get

The AI generates a comprehensive guide with:
- ✅ **Complete trigger setup** - All input properties, auth, etc.
- ✅ **Complete action setup** - Every field you need to fill
- ✅ **Data mapping examples** - How to connect steps
- ✅ **Testing instructions** - How to validate your flow
- ✅ **Troubleshooting** - Common issues and fixes
- ✅ **Pro tips** - Advanced optimizations

## Tips for Best Results

1. **Be specific about tools**:
   - ✅ "Use Gmail and Google Drive"
   - ❌ "Send notifications"

2. **Describe the trigger**:
   - ✅ "When a new Stripe payment is received"
   - ❌ "Handle payments"

3. **Explain the goal**:
   - ✅ "I want to automatically backup form submissions to Google Sheets"
   - ❌ "Help with forms"

## Optional Features

**Clarifying Questions**: The AI may ask up to 3 optional questions at the end to refine the guide. You can:
- Answer them for more specific guidance
- Ignore them - the guide is complete without answers

**Follow-up**: You can ask follow-up questions in regular mode or Build Flow mode.

## Testing

To test the feature works correctly:
```bash
python tests/test_flow_builder.py
```

## Documentation

For complete documentation, see:
- `docs/features/BUILD_FLOW_MODE_GUIDE.md` - Full user guide
- `BUILD_FLOW_FEATURE_SUMMARY.md` - Implementation details

## Toggle Back to Regular Mode

Just uncheck the **🔧 Build Flow Mode** checkbox to return to normal Q&A mode.

---

**Ready to build some flows? Check that checkbox and let's go! 🎉**

