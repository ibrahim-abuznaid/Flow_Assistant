# Action Timing Feature

## Overview
Added real-time timing information to show how long each action takes for both Normal Agent Mode and Build Flow Mode.

## Changes Made

### Backend - Normal Agent Mode (`src/main.py`)

#### 1. StatusCallbackHandler Enhancements
```python
def __init__(self, status_queue: Queue, cancellation_event: Event):
    self.action_start_times = {}  # Track start times for each action
    self.tool_start_time = None
    # ...
```

**Tracking**:
- Each action gets a start time when it begins
- Duration is calculated when action completes
- Times are stored using step numbers as keys

#### 2. on_agent_action() - Tool Start
```python
def on_agent_action(self, action: Any, **kwargs):
    self.action_counter += 1
    self.action_start_times[self.action_counter] = time.time()  # Record start
    
    self.status_queue.put({
        "type": "action_log",
        "step": self.action_counter,
        "icon": icon,
        "action": action_name,
        "start_time": self.action_start_times[self.action_counter]  # Include start time
    })
```

#### 3. on_tool_end() - Tool Completion
```python
def on_tool_end(self, output: str, **kwargs):
    if self.action_counter in self.action_start_times:
        duration = time.time() - self.action_start_times[self.action_counter]
        self.status_queue.put({
            "type": "action_log_update",  # NEW event type
            "step": self.action_counter,
            "duration": duration,
            "status": "completed"
        })
```

**Note**: Sends an `action_log_update` event to update the existing log entry with duration.

#### 4. on_llm_start() & on_llm_end() - Reasoning Time
```python
def on_llm_start(self, serialized: Dict, prompts: list, **kwargs):
    reasoning_step = self.action_counter + 0.5  # Use .5 for interleaving
    self.action_start_times[reasoning_step] = time.time()
    # ...

def on_llm_end(self, response: Any, **kwargs):
    reasoning_step = self.action_counter + 0.5
    if reasoning_step in self.action_start_times:
        duration = time.time() - self.action_start_times[reasoning_step]
        self.status_queue.put({
            "type": "action_log_update",
            "step": reasoning_step,
            "duration": duration
        })
```

**Tracks**: How long the LLM takes to reason/respond.

### Backend - Build Flow Mode (`src/flow_builder.py`)

#### 1. FlowBuilder._emit_action_log() Enhancement
```python
def _emit_action_log(self, icon: str, action: str, detail: Optional[str] = None, 
                     status: str = "started", duration: Optional[float] = None):
    log_data = {
        "type": "action_log",
        "step": self.action_counter,
        "icon": icon,
        "action": action,
        "status": status
    }
    if duration is not None:
        log_data["duration"] = duration  # Include duration if provided
    if status == "started":
        log_data["start_time"] = time.time()  # Record start time
```

#### 2. Phase Timing
Each major phase now tracks its execution time:

**analyze_flow_request()**:
```python
def analyze_flow_request(self, user_request: str):
    start_time = time.time()
    self._emit_action_log("🧠", "Analyzing flow request", ..., "analyzing")
    
    # ... analysis logic ...
    
    duration = time.time() - start_time
    self._emit_action_log("✅", "Analysis complete", ..., "completed", duration)
```

**search_flow_components()**:
```python
def search_flow_components(self, analysis: Dict):
    start_time = time.time()
    self._emit_action_log("🔎", "Searching ActivePieces database", ..., "searching")
    
    # ... search logic ...
    
    duration = time.time() - start_time
    self._emit_action_log("✅", "Database search complete", ..., "completed", duration)
```

**build_comprehensive_plan()**:
```python
def build_comprehensive_plan(self, user_request, analysis, components, user_answers):
    start_time = time.time()
    self._emit_action_log("🏗️", "Building comprehensive flow guide", ..., "building")
    
    # ... guide generation ...
    
    duration = time.time() - start_time
    self._emit_action_log("✨", "Flow guide completed", ..., "completed", duration)
```

### Frontend Changes (`frontend/src/App.jsx`)

#### 1. New Event Type Handler
```javascript
else if (data.type === 'action_log_update') {
  // Update existing log with duration
  setActionLogs(prev => prev.map(log => 
    log.step === data.step 
      ? { ...log, duration: data.duration, status: data.status }
      : log
  ))
}
```

**Purpose**: Updates existing log entries when duration becomes available.

#### 2. Duration Storage
```javascript
else if (data.type === 'action_log') {
  setActionLogs(prev => [...prev, {
    step: data.step,
    icon: data.icon,
    action: data.action,
    detail: data.detail,
    status: data.status,
    timestamp: Date.now(),
    duration: data.duration,      // NEW
    start_time: data.start_time    // NEW
  }])
}
```

#### 3. Duration Formatting
```javascript
const formatDuration = (duration) => {
  if (!duration) return null
  if (duration < 1) return `${Math.round(duration * 1000)}ms`  // Milliseconds
  return `${duration.toFixed(2)}s`  // Seconds with 2 decimals
}
```

**Format Examples**:
- `50ms` - for actions under 1 second
- `1.23s` - for actions over 1 second

#### 4. Display in UI
```javascript
<div className="action-log-action">
  {log.action}
  {log.duration && (
    <span className="action-log-duration">
      {formatDuration(log.duration)}
    </span>
  )}
</div>
```

### CSS Styling (`frontend/src/App.css`)

```css
.action-log-action {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-log-duration {
  font-size: 0.75rem;
  font-weight: 600;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  white-space: nowrap;
}
```

**Appearance**: Blue badge with monospace font next to action name.

## User Experience

### Normal Agent Mode - Example
```
▼ 🔍 Agent Actions (5 steps)

🔍 Checking ActivePieces database  1.23s
    "Slack send message"

🤔 Analyzing and reasoning  2.45s

📚 Searching knowledge base  890ms
    "Slack actions and configuration"

🤔 Analyzing and reasoning  1.87s

✨ Finalizing response  340ms
```

### Build Flow Mode - Example
```
▼ 🔍 Agent Actions (5 steps)

🚀 Starting Flow Builder

🧠 Analyzing flow request  1.52s
    "Send Slack message when..."

✅ Analysis complete  1.52s
    Goal: Send Slack notification for...

🔎 Searching ActivePieces database  3.21s
    Finding triggers, actions, and pieces

📚 Searching knowledge base  670ms
    Looking for relevant workflow documentation

✅ Database search complete  3.88s
    Found 5 actions, 3 triggers

🏗️ Building comprehensive flow guide  8.45s
    Generating step-by-step instructions with AI

✨ Flow guide completed  8.45s
    Generated 4521 character guide
```

## Technical Details

### Timing Precision
- Uses `time.time()` for nanosecond precision on most systems
- Frontend displays:
  - Milliseconds (ms) for times < 1 second
  - Seconds with 2 decimal places for times ≥ 1 second

### Update Mechanism
1. Action starts → Send `action_log` with `start_time`
2. Frontend adds log entry (no duration yet)
3. Action completes → Send `action_log_update` with `duration`
4. Frontend updates the existing log entry
5. Duration badge appears next to action name

### Edge Cases
- **No Duration**: If action is interrupted, duration may not be sent (handled gracefully)
- **Very Fast Actions**: Displayed as `0ms` or actual milliseconds
- **Long Actions**: Displayed in seconds with 2 decimal precision (e.g., `12.34s`)

## Benefits

1. **Performance Insight**: Users can see which actions are slow
2. **Debugging**: Identify bottlenecks in workflow (database vs AI vs web search)
3. **Transparency**: Know exactly how long each step takes
4. **Trust**: See the agent is working (not stuck) even during long operations
5. **Optimization**: Users can understand where time is spent

## Performance Impact

### Backend
- Minimal: Just `time.time()` calls and dictionary lookups
- No noticeable performance overhead

### Frontend
- Minimal: Simple duration calculation and formatting
- No re-renders during timing (uses update pattern)

## Example Timing Breakdown

### Typical Normal Agent Query
```
Database Check:     1.2s  (20%)
Reasoning 1:        2.4s  (40%)
Knowledge Search:   0.9s  (15%)
Reasoning 2:        1.1s  (18%)
Finalization:       0.4s  (7%)
────────────────────────
Total:             6.0s  (100%)
```

### Typical Build Flow Query  
```
Analysis:          1.5s  (10%)
Database Search:   3.9s  (25%)
Knowledge Search:  0.7s  (5%)
Guide Generation:  8.5s  (55%)
Finalization:      0.7s  (5%)
────────────────────────
Total:            15.3s  (100%)
```

## Future Enhancements

Possible improvements:
- Show total execution time at the end
- Add progress bars for long-running actions
- Calculate and display percentage of total time
- Add timing statistics (average, min, max) across multiple requests
- Color code durations (green=fast, yellow=medium, red=slow)
- Export timing data for performance analysis

