# Active Action Logs Collapsible Update

## Summary

Made the active/live action logs (during agent execution) collapsible with the following features:
- ✅ **Default closed** - Logs start collapsed
- ✅ **Real-time expandable** - Users can expand during execution to watch live
- ✅ **Persistent** - Logs remain visible after response completes
- ✅ **Live indicator** - Shows "• Live" badge when agent is actively running

## Changes Made

### Frontend (`frontend/src/App.jsx`)

#### 1. New State Variables
```javascript
const [showActiveActionLogs, setShowActiveActionLogs] = useState(true)
const [activeLogsExpanded, setActiveLogsExpanded] = useState(false) // Default: closed
```

**Purpose**:
- `showActiveActionLogs`: Controls visibility of the active logs container
- `activeLogsExpanded`: Controls whether logs are expanded or collapsed (default: **false/closed**)

#### 2. Initialize on New Request
```javascript
const sendMessage = async () => {
  setActionLogs([]) // Clear logs
  setShowActiveActionLogs(true) // Show container
  setActiveLogsExpanded(false) // Start collapsed (closed)
  // ...
}
```

**Behavior**: Every new request starts with logs closed

#### 3. New Collapsible Active Logs UI
```javascript
{/* Active Action Logs - Show during and after loading if there are logs */}
{showActiveActionLogs && actionLogs.length > 0 && (
  <div className="active-action-logs-container">
    <button 
      className="action-logs-toggle active"
      onClick={() => setActiveLogsExpanded(!activeLogsExpanded)}
    >
      <span className="toggle-icon">{activeLogsExpanded ? '▼' : '▶'}</span>
      <span className="toggle-text">
        🔍 Agent Actions ({actionLogs.length} steps)
        {isLoading && <span className="live-indicator"> • Live</span>}
      </span>
    </button>
    {activeLogsExpanded && (
      <div className="action-logs-list active">
        {/* Action log items */}
      </div>
    )}
  </div>
)}
```

**Features**:
- Shows collapsed button by default
- Displays step count
- Shows "• Live" badge when `isLoading` is true (pulsing red indicator)
- User can click to expand/collapse anytime
- Logs render in real-time when expanded

#### 4. Keep Logs After Response
```javascript
if (data.type === 'done') {
  // Save completed logs
  setCompletedActionLogs(prev => [...prev, {
    id: Date.now(),
    logs: [...actionLogs],
    timestamp: Date.now()
  }])
  // Keep active logs visible
  setShowActiveActionLogs(true)
}
```

**Behavior**: 
- Active logs remain visible after response
- "• Live" indicator disappears when `isLoading` becomes false
- Logs can still be expanded/collapsed

#### 5. Clear Logs on Session Reset
```javascript
const resetConversation = async () => {
  setActionLogs([])
  setShowActiveActionLogs(false) // Hide active logs
  // ...
}
```

### CSS Styles (`frontend/src/App.css`)

#### Active Logs Container
```css
.active-action-logs-container {
  margin: 1rem 0;
  border-radius: 12px;
  overflow: hidden;
  animation: slideInLeft 0.3s ease-out;
}
```

**Design**: Clean, animated entrance

#### Active Toggle Button
```css
.action-logs-toggle.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 2px solid #667eea;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
}
```

**Features**:
- Stronger visual presence than completed logs toggle
- Gradient background
- Border and shadow
- Hover effects

#### Live Indicator
```css
.live-indicator {
  color: #ff4757;
  font-weight: 700;
  animation: pulse-text 1.5s ease-in-out infinite;
}

@keyframes pulse-text {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

**Effect**: Pulsing red text that draws attention when agent is running

#### Active Logs List
```css
.action-logs-list.active {
  margin-top: 0.8rem;
  padding: 1rem;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03) 0%, rgba(118, 75, 162, 0.03) 100%);
  border-radius: 8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  max-height: 400px;
  overflow-y: auto;
}
```

**Features**:
- Scrollable when logs exceed 400px
- Custom scrollbar styling
- Subtle gradient background
- Border for containment

## User Experience Flow

### 1. User Asks Question

**Initial State (Closed):**
```
▶ 🔍 Agent Actions (0 steps) • Live
```

### 2. Agent Starts Working (Still Closed)

**Logs accumulating but hidden:**
```
▶ 🔍 Agent Actions (3 steps) • Live
```

### 3. User Clicks to Expand (Real-time View)

**Expanded during execution:**
```
▼ 🔍 Agent Actions (5 steps) • Live

━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting agent

🤖 Processing your query
    "what actions are there for slack"

🔍 Checking ActivePieces database
    "Slack actions"

🤔 Analyzing and reasoning

📚 Searching knowledge base
    "Slack send message action inputs"

[New logs appear here in real-time as agent works...]
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Note**: Logs update live while expanded! User sees each action as it happens.

### 4. Response Completes

**After completion (collapsed again):**
```
▶ 🔍 Agent Actions (7 steps)    [No more "• Live" badge]
```

**Important**: 
- Logs STAY visible after response
- User can still expand to review what agent did
- "• Live" indicator disappears
- Logs remain until next question

### 5. User Expands After Completion

**Full action history available:**
```
▼ 🔍 Agent Actions (7 steps)

━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Starting agent
🤖 Processing your query
🔍 Checking ActivePieces database
🤔 Analyzing and reasoning
📚 Searching knowledge base
🤔 Analyzing and reasoning
✨ Finalizing response
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6. Next Question Starts

- Previous active logs are hidden
- New collapsed logs appear for new question
- Cycle repeats

## Key Differences: Active vs Completed Logs

### Active Logs (Real-time)
- 📍 **Location**: Standalone container above response
- 🎨 **Style**: Stronger border, gradient background, more prominent
- 🔴 **Live Indicator**: Shows "• Live" with pulsing red text when running
- 🔄 **Updates**: Real-time updates as agent works
- 📊 **State**: Default **closed**, can expand anytime
- ⏰ **Persistence**: Stays visible after response until next question

### Completed Logs (Historical)
- 📍 **Location**: Inside assistant message content
- 🎨 **Style**: Subtle, less prominent
- 🔵 **No Indicator**: Static, no live badge
- 📝 **Updates**: Fixed at time of response
- 📊 **State**: Default **closed**
- ⏰ **Persistence**: Permanently attached to that message

## Benefits

1. **Clean Default View**: No clutter - logs hidden by default
2. **User Control**: Can expand anytime - during or after execution
3. **Real-time Monitoring**: Watch agent work live when desired
4. **Debugging**: Full action history available for review
5. **Transparency**: Clear indicator when agent is actively working
6. **Persistence**: Logs don't disappear, allowing post-execution review
7. **Visual Clarity**: "• Live" badge clearly indicates active execution

## Testing Scenarios

### Test 1: Collapsed by Default
1. Ask a question
2. Verify logs start **collapsed** (closed)
3. Verify "• Live" indicator appears
4. Response completes without user expanding
5. Verify logs remain visible (without "• Live")

### Test 2: Expand During Execution
1. Ask a question
2. Click arrow to expand while agent is running
3. Verify logs appear in real-time
4. Watch new actions appear as they happen
5. Verify "• Live" badge is present
6. Wait for completion
7. Verify "• Live" disappears but logs stay

### Test 3: Expand After Completion
1. Ask a question
2. Don't expand during execution
3. Wait for response to complete
4. Click arrow to expand
5. Verify all actions are visible
6. Verify no "• Live" badge

### Test 4: Multiple Questions
1. Ask first question, expand logs
2. Ask second question
3. Verify first logs disappear
4. Verify new logs appear (collapsed)
5. Expand second logs
6. Verify showing second question's actions

### Test 5: Collapse/Expand Toggle
1. Ask a question
2. Expand logs (▼)
3. Collapse logs (▶)
4. Expand again
5. Verify smooth toggle behavior
6. Verify state persists until next question

## Technical Notes

### State Management
- `showActiveActionLogs`: Controls container visibility
- `activeLogsExpanded`: Controls expanded/collapsed state
- `actionLogs`: Array of current action log entries
- `isLoading`: Determines if "• Live" indicator shows

### Lifecycle
1. **Start**: `showActiveActionLogs=true`, `activeLogsExpanded=false`
2. **During**: Logs accumulate, user can toggle expansion
3. **Complete**: `isLoading=false` (removes "• Live"), logs persist
4. **Next Request**: `showActiveActionLogs=true`, reset expansion

### Performance
- Logs only render when expanded (conditional rendering)
- Max height with scroll prevents layout issues
- Smooth animations don't impact performance

## UI Screenshots Description

### Closed (Default)
```
┌─────────────────────────────────────┐
│ ▶ 🔍 Agent Actions (5 steps) • Live│
└─────────────────────────────────────┘
```

### Expanded (During Execution)
```
┌─────────────────────────────────────┐
│ ▼ 🔍 Agent Actions (5 steps) • Live│
├─────────────────────────────────────┤
│                                     │
│ 🚀 Starting agent                   │
│                                     │
│ 🤖 Processing your query           │
│     "what actions..."               │
│                                     │
│ 🔍 Checking database                │
│                                     │
│ 🤔 Analyzing and reasoning          │
│                                     │
│ 📚 Searching knowledge base         │
│                                     │
└─────────────────────────────────────┘
```

### Expanded (After Completion)
```
┌─────────────────────────────────────┐
│ ▼ 🔍 Agent Actions (7 steps)       │  [No "• Live"]
├─────────────────────────────────────┤
│ [All 7 action steps shown]          │
└─────────────────────────────────────┘
```

## Future Enhancements

Possible improvements:
- Auto-scroll to bottom when expanded and new logs arrive
- Persist expansion state across questions
- Add "Always expanded" user preference
- Show progress percentage
- Add copy logs button
- Export logs as JSON

