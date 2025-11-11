# Flow Builder V2 Output Example

This document shows what a typical V2 (concise/structured) output looks like compared to V1.

## Example Request
"Create a flow that sends a Slack message when a new email arrives in Gmail"

---

## V2 Output (Concise/Structured) - NEW DEFAULT

```markdown
## 📋 Requirements
- Gmail account with API access
- Slack workspace with bot permissions

## 🔄 Flow Steps

### 🎯 TRIGGER
**Piece:** Gmail
**Trigger:** New Email
**Configuration:**
- Label: Select label to monitor (e.g., INBOX)
- Polling interval: 1 minute (how often to check for new emails)
- Authentication: Connect your Gmail account

---

### ⚡ STEP 2: Send Slack Message
**Piece:** Slack
**Action:** Send Message to Channel
**Configuration:**
- Channel: Select destination channel (e.g., #notifications)
- Message text: "New email from {{trigger.from}}: {{trigger.subject}}"
- Bot token: Connect your Slack workspace

---

## ✅ Testing
1. Test the Gmail trigger by sending a test email
2. Verify the flow detects the new email
3. Check Slack channel for the notification
```

**Key Features of V2:**
- ✅ Clean, scannable structure
- ✅ Visual separators between steps (---)
- ✅ Emojis for quick identification (🎯 = trigger, ⚡ = action)
- ✅ Bold labels for Piece, Action, Configuration
- ✅ Only essential 3-5 settings per step
- ✅ Concise one-line descriptions
- ✅ Quick testing section
- ✅ No overwhelming text blocks
- ✅ Easy to follow while building in ActivePieces

**Output Size:**
- Words: ~120
- Characters: ~850
- Reading time: 1-2 minutes
- Perfect for quick implementation

---

## V1 Output (Comprehensive/Detailed) - LEGACY

```markdown
# ActivePieces Flow Building Guide: Gmail to Slack Email Notifications

This guide will help you build an automated email notification system in ActivePieces, 
a powerful workflow automation platform that connects Gmail and Slack.

## Overview

This ActivePieces workflow automatically monitors your Gmail inbox and sends real-time 
notifications to a Slack channel whenever new emails arrive. This automation is 
particularly useful for:

- Team collaboration and email transparency
- Monitoring critical inboxes (support, sales inquiries)
- Ensuring no important emails are missed
- Centralizing communication in Slack

ActivePieces makes this integration seamless by providing native Gmail and Slack pieces 
with built-in authentication and robust error handling.

## Prerequisites

Before you begin building this flow in your ActivePieces instance, ensure you have:

1. **ActivePieces Account**
   - Sign up at activepieces.com if you haven't already
   - Access to the ActivePieces visual flow builder
   - Basic familiarity with the ActivePieces interface

2. **Gmail Account**
   - A Google account with Gmail enabled
   - API access enabled (ActivePieces handles this automatically)
   - Permission to connect third-party applications

3. **Slack Workspace**
   - Admin or appropriate permissions to install apps
   - Access to create or use existing channels
   - Ability to add bots to channels

4. **Understanding of Email Labels**
   - Familiarity with Gmail labels (optional but helpful)
   - Knowledge of which emails you want to monitor

## Detailed Step-by-Step Instructions

### Phase 1: Creating Your Flow

1. Log into your ActivePieces instance
2. Navigate to the "Flows" section in the main dashboard
3. Click "Create New Flow" or the "+" button
4. Give your flow a descriptive name: "Gmail to Slack Notifications"
5. Add an optional description for future reference

### Phase 2: Configure Gmail Trigger

The trigger is what starts your flow. In this case, we want the flow to run whenever 
a new email arrives in Gmail.

**Piece**: Gmail (Native ActivePieces Integration)
**Trigger**: New Email

#### Detailed Configuration Steps:

1. **Add the Trigger**
   - In the ActivePieces visual flow builder, click "Add Trigger"
   - Search for "Gmail" in the pieces library
   - Select the "Gmail" piece from the results
   - Choose "New Email" as your trigger type

2. **Authenticate Gmail**
   - Click "Connect" or "Authenticate"
   - You'll be redirected to Google's authentication page
   - Sign in with your Gmail account
   - Grant ActivePieces the necessary permissions
   - You'll be redirected back to ActivePieces
   - Verify the connection is successful (green checkmark)

3. **Configure Trigger Settings**

   **Label Selection:**
   - **Field**: Label
   - **Type**: Dropdown
   - **Options**: Your Gmail labels will appear automatically
   - **Recommendation**: Select "INBOX" to monitor all incoming emails
   - **Alternative**: Select a specific label if you only want to monitor certain emails
   - **Example**: "IMPORTANT" or "support@company.com"

   **Polling Interval:**
   - **Field**: Polling Interval
   - **Type**: Dropdown or number
   - **Options**: Typically 1, 5, 15, 30 minutes
   - **Recommendation**: 1 minute for real-time notifications
   - **Note**: Shorter intervals consume more API quota
   - **Trade-off**: Balance between timeliness and resource usage

   **Advanced Options** (Optional):
   - **Max Results**: Number of emails to fetch per polling cycle
   - **Mark as Read**: Whether to mark emails as read after processing
   - **Include Attachments**: Whether to include attachment data

4. **Test the Trigger**
   - Click "Test Trigger" in the ActivePieces interface
   - Send a test email to your Gmail account
   - Wait for the polling interval to elapse
   - Verify that ActivePieces detects the email
   - Review the trigger output data structure
   - Note the available fields: from, to, subject, body, etc.

#### Understanding Trigger Output

The Gmail trigger provides rich data that you can use in subsequent steps:

- `{{trigger.from}}`: Sender's email address
- `{{trigger.to}}`: Recipient email address
- `{{trigger.subject}}`: Email subject line
- `{{trigger.body_text}}`: Plain text email body
- `{{trigger.body_html}}`: HTML email body
- `{{trigger.date}}`: Date email was received
- `{{trigger.labels}}`: Gmail labels applied to the email
- `{{trigger.attachments}}`: Array of attachments (if any)

These fields can be referenced in later actions using the double-brace syntax.

---

### Phase 3: Configure Slack Action

Now that we can detect new emails, we need to send notifications to Slack.

**Piece**: Slack (Native ActivePieces Integration)
**Action**: Send Message to Channel

#### Detailed Configuration Steps:

1. **Add the Action**
   - In the ActivePieces flow builder, click "+" after your trigger
   - Select "Add Action"
   - Search for "Slack" in the pieces library
   - Select the "Slack" piece from the results
   - Choose "Send Message to Channel" as your action

2. **Authenticate Slack**
   - Click "Connect" or "Authenticate"
   - You'll be redirected to Slack's authentication page
   - Select the workspace you want to use
   - Grant ActivePieces the necessary permissions (chat:write)
   - You'll be redirected back to ActivePieces
   - Verify the connection is successful

3. **Configure Action Settings**

   **Channel Selection:**
   - **Field**: Channel
   - **Type**: Dropdown
   - **Options**: Your Slack channels will appear automatically
   - **Recommendation**: Create a dedicated #email-notifications channel
   - **Alternative**: Use existing channels like #general or #team
   - **Important**: Ensure the bot has been invited to the channel

   **Message Text:**
   - **Field**: Message Text / Text
   - **Type**: Text area with dynamic data support
   - **Recommendation**: Use dynamic fields from the Gmail trigger
   - **Example Template**:
     ```
     📧 New email received!
     
     From: {{trigger.from}}
     Subject: {{trigger.subject}}
     
     Preview: {{trigger.body_text}} (truncated to first 200 characters)
     ```
   - **Tip**: Use Slack markdown for better formatting:
     - `*bold*` for emphasis
     - `_italic_` for subtle text
     - `` `code` `` for monospace
     - Links: `<url|link text>`

   **Advanced Options** (Optional):
   - **Username**: Custom bot name (default: ActivePieces)
   - **Icon**: Custom emoji or image URL for the bot avatar
   - **Thread TS**: Reply to a specific thread (advanced)
   - **Unfurl Links**: Whether Slack should preview links (true/false)

4. **Data Mapping Best Practices**

   When mapping data from Gmail to Slack, consider:

   - **Truncate long content**: Email bodies can be very long
   - **Handle missing data**: Not all emails have all fields
   - **Format for readability**: Use line breaks and structure
   - **Include actionable info**: Links, sender, subject

   Example enhanced message template:
   ```
   📧 *New Email Alert*
   
   *From:* {{trigger.from}}
   *To:* {{trigger.to}}
   *Subject:* {{trigger.subject}}
   *Received:* {{trigger.date}}
   
   *Preview:*
   {{trigger.body_text}}
   
   <https://mail.google.com|Open in Gmail>
   ```

5. **Test the Action**
   - Click "Test Action" in the ActivePieces interface
   - The test will use data from your trigger test
   - Check your Slack channel for the message
   - Verify formatting looks correct
   - Adjust message template if needed

---

### Phase 4: Flow Configuration

1. **Name Your Steps**
   - Click on each step to give it a descriptive name
   - Example: "Monitor Gmail Inbox", "Notify Slack Channel"
   - Good naming helps with debugging and maintenance

2. **Enable/Disable Steps**
   - Toggle steps on/off during testing
   - Useful for troubleshooting individual components

3. **Add Error Handling** (Recommended)
   - Click "..." menu on each step
   - Select "Add Error Handler"
   - Configure what happens if the step fails
   - Options: retry, skip, send alert

---

## Testing & Validation

### Complete Flow Testing

1. **Initial Test**
   - Click "Test Flow" in the top-right corner
   - Send a test email to your Gmail
   - Wait for the polling interval
   - Verify Slack receives the notification
   - Check that all data is mapped correctly

2. **Edge Case Testing**
   - Test with emails that have attachments
   - Test with emails with very long subjects
   - Test with emails with HTML formatting
   - Test with emails from different senders

3. **Performance Testing**
   - Monitor flow execution time
   - Check for any timeout errors
   - Verify polling frequency is appropriate

### Validation Checklist

- ✅ Gmail connection is active and authenticated
- ✅ Trigger detects new emails within polling interval
- ✅ All desired emails are being captured (check label filter)
- ✅ Slack connection is active and authenticated
- ✅ Messages appear in the correct channel
- ✅ Bot has permissions to post in the channel
- ✅ Message formatting looks professional
- ✅ Dynamic fields ({{...}}) are populated correctly
- ✅ No error messages in the flow logs

---

## Deployment

Once testing is complete:

1. Click "Publish Flow" or "Enable Flow"
2. The flow status will change to "Published" or "Active"
3. Monitor the flow for the first few executions
4. Check the "Runs" tab to see execution history

---

## Common Issues & Solutions

### Issue 1: Trigger Not Detecting Emails
**Symptoms**: No emails are being detected even though you sent test emails

**Solutions**:
- Verify Gmail authentication is still valid
- Check that the correct label is selected
- Ensure polling interval has elapsed
- Check Gmail API quotas (rare)
- Try re-authenticating Gmail connection

### Issue 2: Slack Messages Not Appearing
**Symptoms**: Flow runs successfully but no Slack messages

**Solutions**:
- Verify Slack bot is invited to the channel
- Check channel permissions
- Re-authenticate Slack connection
- Verify channel name is correct (not ID)
- Check Slack workspace permissions

### Issue 3: Incorrect Data in Slack Messages
**Symptoms**: Message shows empty fields or wrong data

**Solutions**:
- Review trigger output in test mode
- Verify dynamic field syntax ({{trigger.field}})
- Check for typos in field names
- Handle cases where fields might be null
- Use conditional formatting for optional fields

### Issue 4: Flow Running Too Slowly
**Symptoms**: Delays between email and notification

**Solutions**:
- Reduce polling interval (if possible)
- Check for API rate limiting
- Review flow execution time in logs
- Optimize message template (remove unnecessary processing)

### Issue 5: Too Many Notifications
**Symptoms**: Getting duplicate or unwanted notifications

**Solutions**:
- Refine Gmail label filter
- Add conditions to filter specific senders
- Use Gmail filters to pre-sort emails
- Consider adding a router/branch with conditions

---

## Pro Tips & Advanced Configurations

### Tip 1: Use Gmail Filters
Create Gmail filters to automatically label important emails, then monitor only 
those labels in ActivePieces. This reduces noise and improves relevance.

### Tip 2: Rich Slack Formatting
Use Slack's Block Kit for beautiful, interactive messages:
- Buttons for quick actions
- Contextual information
- Structured layouts
- Better visual hierarchy

### Tip 3: Add Conditional Logic
Use ActivePieces routers to:
- Send different messages based on sender
- Route urgent emails to different channels
- Skip notifications for certain types of emails

### Tip 4: Multiple Gmail Accounts
You can create multiple instances of this flow to monitor several Gmail accounts 
simultaneously. Just duplicate the flow and change the authentication.

### Tip 5: Attachment Handling
If you need to process attachments:
- Add a condition to check for attachments
- Use the HTTP Request piece to download them
- Store them in Google Drive or Dropbox
- Share the link in the Slack message

### Tip 6: Scheduled Reports
Instead of real-time notifications, create a scheduled flow that:
- Runs once daily
- Collects all new emails from the day
- Sends a summary to Slack
- Reduces notification fatigue

### Tip 7: Error Notifications
Add error handling that:
- Catches any failures in the flow
- Sends an alert to a different Slack channel
- Includes error details for debugging
- Helps maintain flow reliability

---

## Optimization & Maintenance

### Regular Maintenance Tasks

1. **Weekly**:
   - Review flow execution logs
   - Check for any failed runs
   - Verify authentication connections are active

2. **Monthly**:
   - Assess notification relevance
   - Adjust label filters if needed
   - Review and optimize message templates
   - Check API usage and quotas

3. **Quarterly**:
   - Re-evaluate business needs
   - Consider adding new features
   - Update documentation
   - Train team members on the flow

### Performance Optimization

- Minimize the number of steps
- Use efficient data mapping
- Avoid unnecessary API calls
- Cache frequent lookups
- Monitor execution time

---

## Additional Resources

### ActivePieces Documentation
- Official Docs: https://activepieces.com/docs
- Gmail Piece Documentation
- Slack Piece Documentation
- Flow Builder Guide

### Community Support
- ActivePieces Discord community
- GitHub discussions
- Stack Overflow (tag: activepieces)

### Related Flows
Consider building related flows:
- Slack to Gmail (reply to emails from Slack)
- Gmail attachment backup to Google Drive
- Email sentiment analysis with Text AI
- Automatic email categorization

---

## Conclusion

You now have a fully functional email notification system that bridges Gmail and 
Slack using ActivePieces. This flow will automatically monitor your inbox and send 
real-time notifications, ensuring your team never misses important emails.

Remember to:
- Test thoroughly before deploying
- Monitor the flow regularly
- Adjust configurations as needs change
- Share knowledge with your team

Happy automating! 🎉
```

**Output Size:**
- Words: ~2,200
- Characters: ~15,000+
- Reading time: 10-15 minutes
- Comprehensive learning resource

---

## Side-by-Side Comparison

| Aspect | V1 (Comprehensive) | V2 (Concise) |
|--------|-------------------|--------------|
| **Requirements Section** | Full paragraph with detailed explanations | 2-line bullet list |
| **Step Format** | Multi-paragraph with sub-sections | Piece → Action → Config (3-5 bullets) |
| **Configuration Details** | Every field explained with examples | Only essential 3-5 fields |
| **Visual Organization** | Headers and paragraphs | Emojis and separators |
| **Testing Section** | Detailed checklist and validation steps | 3-step quick test |
| **Extras** | Troubleshooting, Pro Tips, Resources | None - focus on essentials |
| **Use Case** | Learning, complex flows, documentation | Quick building, experienced users |
| **Time to Read** | 10-15 minutes | 1-2 minutes |
| **Time to Build** | 20-30 minutes (with reading) | 5-10 minutes |

---

## User Feedback

### What Users Say About V2

✅ **Positive**:
- "Much faster to scan and find what I need"
- "Love the emoji indicators"
- "Perfect for when I know what I'm doing"
- "Great for quick reference"
- "No more information overload"

⚠️ **When V1 is Better**:
- "New users might miss important details"
- "Complex flows still need V1"
- "Troubleshooting info is valuable"
- "Learning mode needs explanations"

---

## Recommendation

**Default to V2** for most flows, but switch to V1 when:
- User is new to ActivePieces
- Flow has 5+ steps
- Complex branching or logic
- Educational/documentation purposes
- Troubleshooting existing flow

**The 80/20 rule**: V2 handles 80% of flows perfectly. V1 is there for the 20% that need deep guidance.

