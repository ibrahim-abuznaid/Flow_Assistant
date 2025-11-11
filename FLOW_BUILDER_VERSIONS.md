# Flow Builder Versions Guide

The Flow Builder now supports two versions of guide generation, allowing you to choose between comprehensive detailed guides or concise structured guides.

## Version Comparison

| Feature | V1 (Comprehensive) | V2 (Concise/Structured) |
|---------|-------------------|------------------------|
| **Default** | No | ✅ Yes (default) |
| **Guide Length** | Long, detailed | Short, focused |
| **Format** | Paragraphs + lists | Structured cards/blocks |
| **Target User** | Beginners, detailed learners | Experienced users, quick reference |
| **Reasoning Effort** | High | Low to Medium |
| **Verbosity** | High | Low |
| **Best For** | Learning, complex flows | Quick building, simple flows |

---

## Version 1: Comprehensive & Detailed

### Description
V1 provides an extensive, educational guide with detailed explanations, best practices, troubleshooting tips, and comprehensive documentation.

### When to Use V1
- ✅ You're new to ActivePieces
- ✅ You need detailed explanations for each step
- ✅ You want to understand WHY, not just HOW
- ✅ Complex flows with many decision points
- ✅ Learning and educational purposes
- ✅ Need troubleshooting and pro tips

### Output Structure
```markdown
# ActivePieces Flow Building Guide: [Flow Name]

This guide will help you build [description] in ActivePieces, a workflow automation platform.

## Flow Overview
[Detailed explanation of what the flow does and why]

## Prerequisites
- Detailed list of requirements
- Account setup instructions
- Authentication guides
- Required integrations

## Step-by-Step Instructions

### Trigger Configuration
[Detailed explanation of the trigger]
- Complete input field descriptions
- Example values
- Authentication details
- Testing instructions
- Common issues

### Action 1: [Action Name]
[Detailed explanation of the action]
- Complete input field descriptions
- Data mapping examples
- Configuration options
- Best practices

[... continues with all actions ...]

## Testing & Validation
[Comprehensive testing guide]

## Common Issues & Solutions
[Detailed troubleshooting section]

## Pro Tips
[Advanced configurations and optimizations]
```

### Example Output Length
- **Typical Length**: 2,000 - 5,000+ words
- **Character Count**: 10,000 - 30,000+ characters
- **Reading Time**: 10-20 minutes

---

## Version 2: Concise & Structured (Default)

### Description
V2 provides a clean, scannable guide with organized UI components. Focuses on essential information in a structured format that's easy to follow.

### When to Use V2
- ✅ You're familiar with ActivePieces (default)
- ✅ You want quick, actionable steps
- ✅ You prefer visual organization
- ✅ Simple to moderate complexity flows
- ✅ Quick reference while building
- ✅ Less reading, more doing

### Output Structure
```markdown
## 📋 Requirements
[Short bullet list of prerequisites ONLY if needed]
- Requirement 1
- Requirement 2

## 🔄 Flow Steps

### 🎯 TRIGGER
**Piece:** [Piece Name]
**Trigger:** [Trigger Name]
**Configuration:**
- Key setting 1: [value/description]
- Key setting 2: [value/description]
- Key setting 3: [value/description]

---

### ⚡ STEP 2: [Action Name]
**Piece:** [Piece Name]
**Action:** [Action Name]
**Configuration:**
- Key setting 1: [value/description]
- Key setting 2: [value/description]
- Key setting 3: [value/description]

---

### ⚡ STEP 3: [Action Name]
**Piece:** [Piece Name]
**Action:** [Action Name]
**Configuration:**
- Key setting 1: [value/description]
- Key setting 2: [value/description]

---

## ✅ Testing
1. Test the trigger
2. Run the complete flow
3. Verify outputs
```

### Key Features
- **Visual Separators**: Uses `---` to clearly separate steps
- **Emojis**: Visual icons for quick scanning (🎯 trigger, ⚡ actions)
- **Structured Format**: Consistent Piece → Action → Configuration pattern
- **Concise**: Only 3-5 most important settings per step
- **Scannable**: Easy to skim and find information quickly

### Example Output Length
- **Typical Length**: 500 - 1,500 words
- **Character Count**: 2,000 - 8,000 characters
- **Reading Time**: 2-5 minutes

---

## How to Choose the Version

### Use V1 (Comprehensive) When:
```python
# For beginners or complex flows
flow_result = build_flow(
    user_request="Build a complex multi-step workflow",
    version=1  # Comprehensive guide
)
```

### Use V2 (Concise) When:
```python
# For quick reference (default)
flow_result = build_flow(
    user_request="Send email when new row added to Google Sheets",
    version=2  # Concise guide (default)
)

# Or simply omit version parameter
flow_result = build_flow(
    user_request="Send email when new row added to Google Sheets"
    # Defaults to version=2
)
```

---

## API Usage

### Via API Endpoint

#### V1 Request (Comprehensive)
```json
{
  "message": "Create a flow to post to Slack when new Trello cards are added",
  "build_flow_mode": true,
  "flow_builder_version": 1
}
```

#### V2 Request (Concise - Default)
```json
{
  "message": "Create a flow to post to Slack when new Trello cards are added",
  "build_flow_mode": true,
  "flow_builder_version": 2
}
```

Or simply omit `flow_builder_version` to use V2 (default):
```json
{
  "message": "Create a flow to post to Slack when new Trello cards are added",
  "build_flow_mode": true
}
```

---

## Version Comparison Example

### Same Request, Different Versions

**Request**: "Create a flow to send email notifications when new rows are added to Google Sheets"

#### V1 Output Preview
```markdown
# ActivePieces Flow Building Guide: Send Email Notifications for New Google Sheets Rows

This guide will help you build an automated email notification system...

## Overview
This ActivePieces workflow automatically monitors a Google Sheets spreadsheet 
and sends email notifications whenever new rows are added. This is particularly 
useful for scenarios such as...

## Prerequisites
Before you begin building this flow in ActivePieces, ensure you have:
- An ActivePieces account (sign up at activepieces.com)
- A Google account with access to Google Sheets
- Access to an email service (Gmail, SendGrid, or SMTP)
- Basic understanding of spreadsheet structures

## Detailed Step-by-Step Instructions

### Step 1: Configure Google Sheets Trigger
The first step is to set up the trigger that monitors your Google Sheets...

**Piece**: Google Sheets
**Trigger**: New Row

To configure this trigger in ActivePieces:

1. Click "Add Trigger" in the ActivePieces visual flow builder
2. Search for "Google Sheets" in the pieces library
3. Select the "New Row" trigger from the available options
4. Authenticate your Google account...

[... continues with extensive details ...]
```

**Length**: ~3,500 words, 20,000+ characters

#### V2 Output Preview
```markdown
## 📋 Requirements
- Google account with Sheets access
- Email service (Gmail/SMTP)

## 🔄 Flow Steps

### 🎯 TRIGGER
**Piece:** Google Sheets
**Trigger:** New Row
**Configuration:**
- Spreadsheet: Select your spreadsheet
- Worksheet: Select the worksheet to monitor
- Polling interval: How often to check (e.g., 5 minutes)

---

### ⚡ STEP 2: Send Email
**Piece:** Gmail
**Action:** Send Email
**Configuration:**
- To: Recipient email address
- Subject: "New row added: {{trigger.values.Column A}}"
- Body: Map fields from the trigger (e.g., {{trigger.values}})

---

## ✅ Testing
1. Test the trigger with your Google Sheet
2. Add a test row to verify detection
3. Check that email is received
```

**Length**: ~120 words, 800 characters

---

## Migration from V1 to V2

If you were using the default flow builder before this update:

**Before** (always used V1):
```python
flow_result = build_flow(user_request)
```

**After** (now defaults to V2):
```python
# V2 is now the default (concise/structured)
flow_result = build_flow(user_request)

# To keep V1 behavior, explicitly request it:
flow_result = build_flow(user_request, version=1)
```

---

## UI/UX Design Philosophy

### V1 Philosophy
- **Educational First**: Teach users how to build flows
- **Comprehensive**: Cover all edge cases and options
- **Narrative Style**: Tell a story about building the flow
- **Hand-Holding**: Guide users through every decision

### V2 Philosophy
- **Action First**: Get users building quickly
- **Essential Only**: Focus on what's needed, skip the rest
- **Visual Structure**: Use design to organize information
- **Scannable**: Users can find what they need at a glance
- **Card-Based**: Each step is a self-contained component

---

## Performance Characteristics

| Metric | V1 | V2 |
|--------|----|----|
| **Generation Time** | 15-30 seconds | 8-15 seconds |
| **Token Usage** | High | Low-Medium |
| **Reasoning Effort** | High | Low-Medium |
| **AI Verbosity** | High | Low |
| **Database Queries** | Comprehensive | Essential only |

---

## Tips for Best Results

### For V1 (Comprehensive)
- Use for flows with 4+ steps
- Best when complexity is "complex"
- Enable web search for latest docs
- Use dual models for complex flows

### For V2 (Concise)
- Use for flows with 2-5 steps
- Best when complexity is "simple" or "moderate"
- Fast mode works great with V2
- Single model is sufficient

---

## Examples by Use Case

### Simple Flow (Use V2)
❌ **Don't use V1**: "Send a Slack message when email arrives"
✅ **Use V2**: Quick, 2-step flow with clear structure

### Moderate Flow (V2 Recommended)
✅ **Use V2**: "Post to Twitter when new blog published"
⚠️ **V1 Optional**: If you need detailed explanations

### Complex Flow (V1 Recommended)
⚠️ **V2 Possible**: "Multi-step customer onboarding with branches"
✅ **Use V1**: Detailed guide helps navigate complexity

### Learning/Educational (Use V1)
✅ **Use V1**: Understanding ActivePieces concepts
❌ **Don't use V2**: V2 assumes familiarity

---

## Future Enhancements

Planned improvements for both versions:

### V3 (Potential Future Version)
- Interactive UI components
- Step-by-step wizard format
- Real-time validation
- Visual flow diagram generation

### V2 Improvements
- Table-based configuration display
- Collapsible sections for optional settings
- Color-coded step types
- Quick-copy configuration snippets

---

## Feedback & Improvements

Both versions are designed based on user feedback. The system is flexible and can be adjusted based on:

- User preferences
- Flow complexity
- Use case scenarios
- Time constraints
- Learning goals

Default to V2 for most users, but V1 remains available for those who need comprehensive guidance.

---

## Summary

**Choose V1 if**: You want to learn, need details, complex flow
**Choose V2 if**: You want speed, know basics, simple flow (DEFAULT)

**Quick Decision Tree**:
```
Are you new to ActivePieces?
├─ Yes → V1 (Comprehensive)
└─ No → Is the flow complex (5+ steps)?
    ├─ Yes → V1 (Comprehensive)
    └─ No → V2 (Concise) ✅ DEFAULT
```

