# Flow Builder Detailed Action Logs

## Problem
In Build Flow Mode, only 3-4 static action logs were shown (like "Starting Flow Builder", "Analyzing request", "Building guide", "Completed"). All the real work (database searches, knowledge base lookups, web searches, code generation, etc.) was hidden inside the `build_flow()` function.

## Solution
Added detailed action logging throughout the flow builder to show every step of the process.

## Changes Made

### 1. Enhanced FlowBuilder Class (`src/flow_builder.py`)

#### Added Status Callback Support
```python
def __init__(self, model: str = "gpt-5-mini", status_callback=None):
    self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    self.model = model
    self.status_callback = status_callback  # NEW
    self.action_counter = 0  # NEW
    
def _emit_action_log(self, icon: str, action: str, detail: Optional[str] = None, status: str = "started"):
    """Emit an action log if callback is available."""
    if self.status_callback:
        self.action_counter += 1
        self.status_callback({
            "type": "action_log",
            "step": self.action_counter,
            "icon": icon,
            "action": action,
            "detail": detail,
            "tool": None,
            "status": status
        })
```

#### Added Logging to Key Methods

**1. analyze_flow_request()** - Flow Analysis
```python
def analyze_flow_request(self, user_request: str):
    self._emit_action_log("🧠", "Analyzing flow request", 
                         user_request[:80] + "...", "analyzing")
    # ... analysis logic ...
    self._emit_action_log("✅", "Analysis complete", 
                         f"Goal: {analysis.get('flow_goal', '')[:60]}...", "completed")
```

**Logs:**
- 🧠 Analyzing flow request
- ✅ Analysis complete (with goal summary)

**2. search_flow_components()** - Database Search
```python
def search_flow_components(self, analysis: Dict[str, Any]):
    self._emit_action_log("🔎", "Searching ActivePieces database", 
                         "Finding triggers, actions, and pieces", "searching")
    # ... search logic ...
    self._emit_action_log("✅", "Database search complete", 
                         f"Found {len(actions)} actions, {len(triggers)} triggers", "completed")
```

**Logs:**
- 🔎 Searching ActivePieces database
- 📚 Searching knowledge base (when vector search is performed)
- ✅ Database search complete (with counts)

**3. build_comprehensive_plan()** - Guide Generation
```python
def build_comprehensive_plan(self, user_request, analysis, components, user_answers):
    self._emit_action_log("🏗️", "Building comprehensive flow guide", 
                         "Generating step-by-step instructions with AI", "building")
    # ... guide generation ...
    self._emit_action_log("✨", "Flow guide completed", 
                         f"Generated {len(guide)} character guide", "completed")
```

**Logs:**
- 🏗️ Building comprehensive flow guide
- ✨ Flow guide completed (with character count)

**4. Vector Search** - Knowledge Base
```python
def perform_vector_search():
    self._emit_action_log("📚", "Searching knowledge base", 
                         "Looking for relevant workflow documentation", "searching")
    # ... vector search ...
```

**Logs:**
- 📚 Searching knowledge base

**5. Web Search** - Additional Information
```python
def _search_for_missing_info(self, analysis, components):
    if search_queries:
        self._emit_action_log("🌐", "Searching web for additional info", 
                             f"Looking for {len(search_queries)} queries", "searching")
```

**Logs:**
- 🌐 Searching web for additional info

### 2. Updated build_flow() Function

#### Added status_callback Parameter
```python
def build_flow(
    user_request: str, 
    user_answers: Optional[str] = None,
    primary_model: str = "gpt-5-mini",
    secondary_model: Optional[str] = None,
    use_dual_models: bool = False,
    status_callback = None  # NEW PARAMETER
) -> Dict[str, Any]:
    # Create builder with callback
    builder = FlowBuilder(model=primary_model, status_callback=status_callback)
    
    # For dual models, also pass callback to secondary builder
    if use_dual_models and secondary_model:
        planning_builder = FlowBuilder(model=secondary_model, status_callback=status_callback)
```

### 3. Updated main.py to Pass Callback

```python
if build_flow_mode:
    from src.flow_builder import build_flow

    # Create a callback to emit logs
    def flow_status_callback(log_data):
        status_queue.put(log_data)
    
    # Send initial log
    flow_status_callback({
        "type": "action_log",
        "step": 0,
        "icon": "🚀",
        "action": "Starting Flow Builder",
        ...
    })
    
    flow_result = build_flow(
        contextual_request,
        primary_model=primary_model,
        secondary_model=secondary_model,
        use_dual_models=use_dual_models,
        status_callback=flow_status_callback  # Pass callback
    )
```

## Action Log Types

| Icon | Action | When | Details |
|------|--------|------|---------|
| 🚀 | Starting Flow Builder | Initial | Flow builder starts |
| 🧠 | Analyzing flow request | Phase 1 | AI analyzes user request |
| ✅ | Analysis complete | Phase 1 | Shows flow goal |
| 🔎 | Searching ActivePieces database | Phase 2 | Searches for components |
| 📚 | Searching knowledge base | Phase 2 | Vector store lookup |
| ✅ | Database search complete | Phase 2 | Shows action/trigger counts |
| 🌐 | Searching web for additional info | Phase 2 | Web search if needed |
| 🏗️ | Building comprehensive flow guide | Phase 3 | AI generates guide |
| ✨ | Flow guide completed | Phase 3 | Shows character count |

## Example Flow Logs

### Simple Flow Request
```
🚀 Starting Flow Builder

🧠 Analyzing flow request
    "Send Slack message when new email arrives"

✅ Analysis complete
    Goal: Send Slack notification for new Gmail messages

🔎 Searching ActivePieces database
    Finding triggers, actions, and pieces

📚 Searching knowledge base
    Looking for relevant workflow documentation

✅ Database search complete
    Found 5 actions, 3 triggers

🏗️ Building comprehensive flow guide
    Generating step-by-step instructions with AI

✨ Flow guide completed
    Generated 4521 character guide
```

### Complex Flow with Web Search
```
🚀 Starting Flow Builder

🧠 Analyzing flow request
    "Create automated customer onboarding system with CRM..."

✅ Analysis complete
    Goal: Automated multi-step customer onboarding workflow

🔎 Searching ActivePieces database
    Finding triggers, actions, and pieces

📚 Searching knowledge base
    Looking for relevant workflow documentation

🌐 Searching web for additional info
    Looking for 2 queries

✅ Database search complete
    Found 12 actions, 4 triggers

🏗️ Building comprehensive flow guide
    Generating step-by-step instructions with AI

✨ Flow guide completed
    Generated 8943 character guide
```

## Benefits

1. **Full Transparency**: Users see every step the flow builder takes
2. **Real-time Updates**: Actions appear as they happen
3. **Debugging**: Can identify where process is slow or stuck
4. **Educational**: Users learn what goes into building a flow guide
5. **Progress Tracking**: See how many components were found
6. **Confidence**: Users know the system is working

## Testing

To see the detailed logs:

1. Enable Build Flow Mode
2. Ask a flow building question:
   - "Create a flow to send Slack notifications for new Gmail"
   - "Build a workflow to sync Google Sheets with Airtable"
   - "Make an automated customer support system"

3. Expand the action logs and watch them appear in real-time:
   ```
   ▼ 🔍 Agent Actions (8 steps) • Live
   ```

4. See all the detailed steps instead of just 3 static messages

## Technical Notes

### Threading-Safe
The callback function is thread-safe since it just puts items into a queue that's already being monitored.

### Performance
Minimal overhead - logs are only emitted if callback is provided, and the action counter is lightweight.

### Backward Compatibility
The `status_callback` parameter is optional, so existing code calling `build_flow()` without it continues to work.

## Future Enhancements

Possible improvements:
- Add timing information (how long each phase takes)
- Add more granular logs for parallel component searches
- Log specific pieces/actions being searched
- Add success/failure indicators for each search
- Show which model is being used for each step

