# Build Flow Mode - Comprehensive Guide

## Overview

Build Flow Mode is a powerful feature that provides comprehensive, step-by-step guides for building ActivePieces workflows. Unlike regular mode, which is conversational and exploratory, Build Flow Mode is specialized for creating detailed, actionable flow building instructions.

## Features

### 🎯 Intelligent Flow Analysis
- Analyzes your flow request to understand the goal
- Identifies triggers and actions needed
- Determines complexity level
- Assesses confidence and information gaps

### 💬 Smart Clarification Questions
- Asks relevant clarifying questions (max 3)
- All questions are **optional** - the AI proceeds even if you don't answer
- Questions help refine the guide for your specific use case
- Questions are contextual and purpose-driven

### 🔍 Comprehensive Research
- Searches the ActivePieces knowledge base (433 pieces, 2,681 actions, 694 triggers)
- Retrieves detailed information about triggers, actions, and input properties
- Searches online for additional information if needed
- Finds best practices and common patterns

### 📋 Detailed Flow Guides
The generated guides include:
- **Flow Overview** - What the flow does and why
- **Prerequisites** - What you need before starting
- **Step-by-Step Instructions** - Detailed steps with ALL required inputs
- **Trigger Configuration** - Exact settings, input fields, authentication
- **Action Configuration** - For EACH action, lists ALL inputs (required & optional)
- **Data Mapping** - How to connect steps together
- **Testing & Validation** - How to test the flow
- **Common Issues & Solutions** - Potential problems and fixes
- **Pro Tips** - Advanced configurations or optimizations

## How to Use

### Step 1: Enable Build Flow Mode

In the UI, check the **🔧 Build Flow Mode** checkbox above the input area.

When enabled, you'll see:
- A confirmation message: "Build Flow Mode (Active)"
- A description: "Get comprehensive step-by-step flow building guides"
- The placeholder text changes to: "Describe the flow you want to build..."

### Step 2: Describe Your Flow

Enter a description of the flow you want to build. Examples:

**Simple Flows:**
- "Send an email when a new file is added to Google Drive"
- "Post to Slack when a new row is added to Google Sheets"
- "Create a Discord message when someone fills out a form"

**Moderate Flows:**
- "When I receive a payment in Stripe, send a welcome email and add them to Mailchimp"
- "Monitor RSS feeds and post new articles to Twitter and LinkedIn"
- "Create Trello cards from incoming webhooks"

**Complex Flows:**
- "Automate my customer onboarding process"
- "Build a lead management system"
- "Create an automated content publishing workflow"

### Step 3: Review and Follow the Guide

The AI will:
1. Analyze your request (🔍 Analyzing your flow request...)
2. Search for required pieces and information
3. Generate a comprehensive guide
4. Optionally provide clarifying questions at the end

The guide will be formatted in markdown with:
- Clear headers and sections
- Bullet points and numbered lists
- Code blocks for configuration examples
- Tables for input properties (when applicable)

### Step 4: Optional Clarifications

If the AI includes clarifying questions at the end, you can:
- **Answer them**: Simply respond with your answers in regular mode or Build Flow mode
- **Ignore them**: The guide is complete without answers; clarifications just add specificity

## Example Usage

### Example 1: Simple Email Notification

**User Input (with Build Flow Mode ON):**
```
Send an email when a new file is added to Google Drive
```

**AI Output:**
```markdown
# Flow Building Guide: Send Email Notification for New Google Drive Files

## Overview
This flow monitors your Google Drive for new files and automatically sends 
an email notification whenever a file is added.

## Prerequisites
- ActivePieces account
- Google Drive account with files you want to monitor
- Email account for sending notifications

## Step-by-Step Instructions

### Step 1: Create New Flow
1. Log into your ActivePieces instance
2. Click "Create Flow" button
3. Give your flow a descriptive name (e.g., "Google Drive File Alert")

### Step 2: Configure Trigger - Google Drive "New File"
1. Click "Select Trigger"
2. Search for "Google Drive"
3. Select "New File" trigger
4. Configure the following inputs:

**Required Inputs:**
- **Authentication**: Connect your Google Drive account
- **Drive**: Select the drive to monitor (default: My Drive)

**Optional Inputs:**
- **Folder**: Specific folder to monitor (leave empty for entire drive)
- **File Type Filter**: Filter by file type (e.g., .pdf, .docx)
- **Polling Interval**: How often to check (default: 5 minutes)

### Step 3: Configure Action - Send Email
1. Click "+" to add an action
2. Search for "Email" or "Gmail"
3. Select "Send Email" action
4. Configure the following inputs:

**Required Inputs:**
- **To**: Recipient email address(es)
- **Subject**: Email subject line (e.g., "New File Added: {{trigger.file.name}}")
- **Body**: Email content

**Example Body with Data Mapping:**
```
A new file has been added to Google Drive:

File Name: {{trigger.file.name}}
File Type: {{trigger.file.mimeType}}
Added By: {{trigger.file.owner.displayName}}
File Link: {{trigger.file.webViewLink}}
Added On: {{trigger.file.createdTime}}
```

**Optional Inputs:**
- **CC**: Carbon copy recipients
- **BCC**: Blind carbon copy recipients
- **Reply To**: Custom reply-to address

### Step 4: Test Your Flow
1. Click "Test Flow" button
2. Add a test file to your Google Drive
3. Wait for the polling interval (or trigger manually)
4. Check your email for the notification
5. Verify all data fields are populated correctly

### Step 5: Enable & Deploy
1. Click "Enable Flow" toggle
2. Your flow is now live and monitoring for new files!

## Common Issues & Solutions

**Issue**: Email not sending
- **Solution**: Check email action authentication and verify recipient address

**Issue**: Not detecting new files
- **Solution**: Verify folder path is correct and you have permissions

**Issue**: Trigger firing multiple times for same file
- **Solution**: Check polling interval and de-duplication settings

## Pro Tips
- Use filters to monitor specific file types only
- Include file thumbnails in email by using {{trigger.file.thumbnailLink}}
- Set up multiple actions (e.g., Slack notification + Email)
- Use conditional logic to handle different file types differently

---

**💡 Optional Clarifications** (you can provide these for more specific guidance):

1. Do you want to filter for specific file types or folders?
2. Should the email include the file link or content?
```

### Example 2: Complex Workflow

**User Input (with Build Flow Mode ON):**
```
Automate my customer onboarding
```

**AI Output:**
```markdown
# Flow Building Guide: Automated Customer Onboarding

## Overview
This flow automates your customer onboarding process by triggering when 
a new customer signs up and performing multiple onboarding actions.

[... comprehensive guide with all steps ...]

---

**💡 Optional Clarifications** (you can provide these for more specific guidance):

1. How do new customers enter your system? (e.g., form submission, Stripe payment, CRM entry)
2. What are the main steps in your onboarding? (e.g., send welcome email, create account, add to CRM)
3. Which tools/platforms do you use? (e.g., Mailchimp, Slack, Google Sheets)
```

## Technical Details

### Architecture

Build Flow Mode uses a specialized pipeline:

1. **Flow Analyzer** (GPT-5)
   - Analyzes the user request
   - Identifies triggers and actions
   - Determines clarity and confidence
   - Generates clarifying questions

2. **Component Searcher**
   - Searches SQLite database for pieces
   - Uses FAISS vector store for semantic search
   - Retrieves detailed piece information

3. **Flow Planner** (GPT-5)
   - Synthesizes all information
   - Creates comprehensive guide
   - Uses web search if needed
   - Formats output in markdown

### Configuration

Environment variables in `.env`:

```env
# Flow Builder Model (gpt-5, gpt-5-mini, or gpt-5-nano)
FLOW_BUILDER_MODEL=gpt-5-mini

# For complex flows, you can use the full model:
# FLOW_BUILDER_MODEL=gpt-5
```

**Recommended Settings:**
- `gpt-5-mini`: Best for most flows (fast, cost-effective)
- `gpt-5`: Use for very complex or critical flows (more reasoning power)
- `gpt-5-nano`: Use for simple flows (fastest, cheapest)

### API Integration

The build flow mode is integrated into the chat endpoint:

```javascript
// Frontend request
{
  "message": "Send an email when a new file is added to Google Drive",
  "session_id": "session_123...",
  "build_flow_mode": true  // ← Enable Build Flow Mode
}
```

## Best Practices

### For Users

1. **Be Specific**: Include details about your use case
   - ✅ "Send Gmail notification when Google Sheets row added with order details"
   - ❌ "Automate my stuff"

2. **Mention Tools**: Specify which integrations you want to use
   - ✅ "Use Slack and Trello to track support tickets"
   - ❌ "Track support tickets"

3. **State Goals**: Explain what you want to accomplish
   - ✅ "I want to automatically backup form submissions to Google Sheets and email me"
   - ❌ "Help with forms"

4. **Answer Questions**: If clarifying questions appear, answering them improves the guide

### For Developers

1. **Model Selection**: Use `gpt-5-mini` by default, `gpt-5` for complex flows
2. **Error Handling**: The flow builder gracefully handles missing pieces
3. **Caching**: Pieces are cached for performance
4. **Logging**: All flow building requests are logged for debugging

## Comparison: Build Flow Mode vs Regular Mode

| Feature | Regular Mode | Build Flow Mode |
|---------|-------------|-----------------|
| **Purpose** | General Q&A, exploration | Comprehensive flow guides |
| **Output Style** | Conversational | Structured, detailed |
| **Tool Usage** | Minimal, on-demand | Extensive research |
| **Detail Level** | Overview | ALL input properties |
| **Clarifications** | No | Yes (optional) |
| **Web Search** | As needed | Proactive |
| **Best For** | Quick questions, checking pieces | Building complete flows |
| **Response Time** | Fast (5-15s) | Moderate (15-30s) |

## Future Enhancements

Planned improvements:
- [ ] Multi-turn clarification conversations
- [ ] Flow export (JSON format for direct import)
- [ ] Visual flow diagrams
- [ ] Example data for testing
- [ ] Integration testing automation
- [ ] Flow templates library

## Support

If you encounter issues:
1. Check that Build Flow Mode is enabled (checkbox is checked)
2. Verify your OpenAI API key is configured
3. Check backend logs for errors
4. Try with a simpler flow request first
5. Ensure FLOW_BUILDER_MODEL is set in .env

## Examples

See `tests/test_flow_builder.py` for example usage and test cases.

