# Quick Test Guide for Planning Layer Improvements

## What Was Improved

The planning layer now enforces **strict efficiency rules** to prevent the agent from:
- ❌ Making redundant searches
- ❌ Chasing perfect information endlessly
- ❌ Retrying failed connections forever
- ❌ Exceeding iteration limits

## Test the Improvements

### 1. Start PostgreSQL (if available)

If you have PostgreSQL running:
```bash
# Check if it's running
psql -U postgres -c "SELECT 1"

# If not running, start it (varies by OS)
# Windows: pg_ctl start
# Linux: sudo systemctl start postgresql
# Mac: brew services start postgresql
```

### 2. Start the Server

```bash
python run.py
```

Watch for:
```
✓ Planner initialized with GPT-5 model: gpt-5-mini
✓ Agent created successfully
```

### 3. Test Simple Query (Should use 1 tool call)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is Slack available in ActivePieces?"}'
```

**Expected in Console:**
```
============================================================
📋 PLANNER OUTPUT:
Intent: Check if Slack integration exists
Query Type: simple_check
Action Plan: 1-2 steps
============================================================

⚠️ MAXIMUM TOOL CALLS ALLOWED: 1

Invoking: check_activepieces with {'query': 'Slack'}

[Agent responds immediately after 1 tool call]
```

### 4. Test Flow Building (Should use 2 tool calls)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I want to send an email when a new file is added to Google Drive"}'
```

**Expected in Console:**
```
============================================================
📋 PLANNER OUTPUT:
Intent: Build workflow with Google Drive trigger and email action
Query Type: flow_building
Action Plan: 3-4 steps
============================================================

⚠️ MAXIMUM TOOL CALLS ALLOWED: 2

Invoking: search_activepieces_docs with {'query': 'Google Drive new file trigger...'}
Invoking: search_activepieces_docs with {'query': 'send email action...'}

[Agent stops after 2 tool calls and compiles response]
```

### 5. Test Database Failure Handling

**Stop PostgreSQL temporarily:**
```bash
# Stop PostgreSQL (varies by OS)
# Windows: pg_ctl stop
# Linux: sudo systemctl stop postgresql
# Mac: brew services stop postgresql
```

**Send query:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is Gmail available?"}'
```

**Expected in Console:**
```
⚠️ Database connection failed: connection timeout expired

[Agent uses fallback strategy immediately, doesn't retry]
```

**Expected Response:**
```json
{
  "reply": "⚠️ Database connection failed. Unable to verify if 'Gmail' exists in ActivePieces.\n\nFallback: Please check the ActivePieces web UI directly at your ActivePieces instance.\nMost common integrations include: Gmail, Slack, Google Drive, Google Sheets, Discord, Telegram, HTTP Request, Webhooks, Email, and 400+ more."
}
```

### 6. Test Stopping Condition

**Send a complex query:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I build a flow that monitors Twitter, analyzes sentiment with AI, sends to Slack if negative, and logs to Google Sheets?"}'
```

**Expected:**
- Agent makes 3-4 tool calls max
- Stops when hitting max_tool_calls
- Responds with what it found
- Suggests user check UI for complete details

**Watch for this in console:**
```
⚠️ MAXIMUM TOOL CALLS ALLOWED: 4

[Makes 4 tool calls]

🛑 STOPPING CONDITION:
After 4 searches, STOP and respond with available information.

[Agent stops and compiles response]
```

---

## Success Criteria

### ✅ Good Signs:

1. **Tool Call Limits Respected**
   - Simple queries: 1 tool call
   - Flow building: 2-3 tool calls
   - Complex queries: 4-6 tool calls max

2. **Fast Responses**
   - Simple queries: < 5 seconds
   - Flow building: < 15 seconds
   - Complex queries: < 30 seconds

3. **Graceful Failures**
   - Database failures don't cause retries
   - Partial information is provided
   - Helpful suggestions given

4. **No Max Iteration Errors**
   - Agent stays within 10 iterations
   - Generates response when hitting limit

### ❌ Warning Signs:

1. **Too Many Tool Calls**
   - More than 6 tool calls for any query
   - Repeated searches with similar queries

2. **Slow Responses**
   - Taking > 60 seconds
   - Agent seems stuck in loops

3. **Max Iteration Errors**
   - "Maximum iterations reached" errors
   - Agent doesn't generate response

4. **Database Retry Loops**
   - Multiple database connection attempts
   - Hanging on connection failures

---

## Monitoring Console Output

### Look for Planning Output:

```
============================================================
📋 PLANNER OUTPUT:
Intent: [What user wants]
Query Type: [Classification]
Action Plan: [Number] steps
============================================================

⚠️ MAXIMUM TOOL CALLS ALLOWED: [Number]

🛑 STOPPING CONDITION:
[Clear condition describing when to stop]

🔄 FALLBACK STRATEGY:
[What to do if tools fail]

============================================================
⚡ CRITICAL: Follow this plan EXACTLY. Do NOT make extra searches.
⚡ CRITICAL: STOP after reaching max tool calls or stopping condition.
⚡ CRITICAL: If a tool fails, use fallback strategy immediately.
============================================================
```

### Count Tool Invocations:

```
Invoking: check_activepieces with {...}
Invoking: search_activepieces_docs with {...}
Invoking: search_activepieces_docs with {...}

[Should stop here if max_tool_calls = 2]
```

### Check Response Quality:

Agent should provide:
- ✅ Clear answer based on info found
- ✅ List of required inputs (for flow building)
- ✅ Suggestions if info incomplete
- ✅ No apologizing for not having "perfect" information

---

## Before vs After Comparison

### Before Improvements:

**Query:** "Is Slack available?"

Console:
```
Invoking: check_activepieces with 'Slack'
Invoking: search_activepieces_docs with 'Slack'
Invoking: search_activepieces_docs with 'Slack integration'
Invoking: search_activepieces_docs with 'Slack actions'
Invoking: check_activepieces with 'Slack bot'
...
[15 tool calls later]
```

### After Improvements:

**Query:** "Is Slack available?"

Console:
```
📋 PLANNER OUTPUT:
Max tool calls: 1
Stopping condition: After 1 check, respond immediately

Invoking: check_activepieces with 'Slack'

✓ Yes, ActivePieces has Slack integration...
[Immediate response after 1 tool call]
```

---

## Troubleshooting

### Issue: Agent still making too many tool calls

**Check:**
1. Is planning output showing in console?
2. Does the plan have clear `max_tool_calls`?
3. Is agent system prompt updated with efficiency rules?

**Fix:**
```bash
# Restart server to reload changes
python run.py
```

### Issue: Database connection still hanging

**Check:**
```bash
# Test connection directly
python db_config.py
```

**Fix:**
- Ensure PostgreSQL is running
- Check DB_HOST, DB_PORT in .env
- Connection timeout is now 5 seconds (fails fast)

### Issue: Plans seem vague

**Check planner output:**
- Should have specific steps with "MAX ATTEMPTS = 1"
- Should have clear stopping condition
- Should have fallback strategy

**If not:**
- GPT-5 model might need better prompting
- Try increasing reasoning effort to "high" in planner.py

---

## Configuration Tweaks

### Make Agent Even Stricter:

Edit `agent.py`:
```python
max_iterations=5  # From 10 to 5 (very strict)
max_execution_time=30  # From 60 to 30 seconds
```

### Allow More Flexibility:

Edit `agent.py`:
```python
max_iterations=15  # From 10 to 15
max_execution_time=90  # From 60 to 90 seconds
```

### Adjust Planning Model:

Edit `.env`:
```env
# For faster planning (less thinking)
PLANNER_MODEL=gpt-5-nano

# For better planning quality (more thinking)
PLANNER_MODEL=gpt-5
```

---

## Next Steps

1. ✅ **Run basic tests** (simple query, flow building)
2. ✅ **Monitor console output** for tool call counts
3. ✅ **Test database failure** handling
4. ✅ **Verify stopping conditions** are working
5. 📊 **Track metrics** over time:
   - Average tool calls per query
   - Response times
   - User satisfaction
   - Error rates

---

## Expected Results

With these improvements, you should see:

- **60-80% reduction** in tool calls
- **2-3x faster** response times
- **Zero max iteration errors** (or < 1%)
- **Graceful handling** of database failures
- **More focused** agent behavior

The agent now operates under **"efficiency over perfection"** - providing good answers quickly rather than perfect answers slowly.

---

## Questions?

See detailed explanations in:
- `PLANNER_IMPROVEMENTS_SUMMARY.md` - What changed and why
- `PLANNING_LAYER_GUIDE.md` - Full technical guide
- `ENABLE_PLANNING_LAYER.md` - Setup instructions

Happy testing! 🚀

