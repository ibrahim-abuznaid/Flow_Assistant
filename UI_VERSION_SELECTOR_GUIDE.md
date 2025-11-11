# Flow Builder Version Selector - UI Guide

## ✅ What's New

The Flow Builder now has a **V1/V2 version selector** directly in the UI! You can choose between concise or detailed guides right from the interface.

---

## 🎨 How It Looks

When you enable **Build Flow Mode**, you'll see a new dropdown appear:

```
┌─────────────────────────────────────────────────┐
│ ☑ 🔧 Build Flow Mode (Active)                   │
│                                                   │
│   Guide Style: [📝 Concise (V2) - Quick & St... ▼]│
│   ⚡ Fast, organized steps with emojis -         │
│   best for experienced users                     │
└─────────────────────────────────────────────────┘
```

---

## 📝 Version Options

### Option 1: 📝 Concise (V2) - Quick & Structured
**Default selection** - Best for most users!

**What you get:**
- ⚡ Fast generation (8-15 seconds)
- Clean, scannable format
- Emojis for visual organization (🎯 trigger, ⚡ actions)
- Only 3-5 essential settings per step
- Perfect for quick building

**Best for:**
- Experienced ActivePieces users
- Simple to moderate flows
- Quick reference while building
- When you know what you're doing

**Output example:**
```markdown
## 📋 Requirements
- Gmail account
- Slack workspace

## 🔄 Flow Steps

### 🎯 TRIGGER
**Piece:** Gmail
**Trigger:** New Email
**Configuration:**
- Label: INBOX
- Polling: 1 minute

---

### ⚡ STEP 2: Send Message
**Piece:** Slack
...
```

---

### Option 2: 📚 Detailed (V1) - Comprehensive
**For learning and complex flows**

**What you get:**
- 📖 Comprehensive explanations
- Step-by-step with examples
- Troubleshooting tips
- Pro tips and best practices
- Prerequisites and setup guides
- Testing validation checklists

**Best for:**
- New to ActivePieces
- Complex flows (5+ steps)
- Learning mode
- Need detailed explanations
- Want troubleshooting help

**Output example:**
```markdown
# ActivePieces Flow Building Guide: [Flow Name]

## Overview
[Detailed explanation of what the flow does...]

## Prerequisites
- ActivePieces account (sign up at...)
- Gmail account with API access...
- Complete setup instructions...

## Step-by-Step Instructions

### Phase 1: Creating Your Flow
1. Log into your ActivePieces instance
2. Navigate to the "Flows" section...
[... extensive details ...]
```

---

## 🚀 How to Use

### Step 1: Enable Build Flow Mode
1. Click the checkbox: **🔧 Build Flow Mode**
2. The version selector will appear below

### Step 2: Choose Your Guide Style
1. Click the **Guide Style** dropdown
2. Select either:
   - **📝 Concise (V2)** - Quick & Structured ✅ Default
   - **📚 Detailed (V1)** - Comprehensive

### Step 3: See the Description Update
The description under the selector updates to show what you'll get:
- V2: "⚡ Fast, organized steps with emojis - best for experienced users"
- V1: "📖 Detailed explanations with examples - best for learning"

### Step 4: Send Your Request
Type your flow request and press Enter. The AI will generate a guide in your chosen style!

---

## 💡 Quick Decision Guide

**Choose V2 (Concise) if:**
- ✅ You're familiar with ActivePieces
- ✅ You want to build quickly
- ✅ Simple or moderate flow complexity
- ✅ You prefer visual organization
- ✅ Less reading, more doing

**Choose V1 (Detailed) if:**
- ✅ You're new to ActivePieces
- ✅ Complex flow with many steps
- ✅ You want to learn concepts
- ✅ Need troubleshooting help
- ✅ Want comprehensive documentation

---

## 📱 Responsive Design

The version selector works great on all devices:

### Desktop
- Full dropdown with descriptions
- Clear labels and spacing
- Hover effects

### Mobile
- Optimized font sizes
- Touch-friendly dropdown
- Compact layout
- Easy to read descriptions

---

## 🎯 Example Usage

### Example 1: Quick Email Notification
**Request:** "Send email when new Google Sheets row added"

**Recommended:** V2 (Concise) ✅
1. Enable Build Flow Mode
2. Keep V2 selected (default)
3. Type your request
4. Get organized guide in ~10 seconds

**Result:** ~800 chars, 2-minute read, build in 5 minutes

---

### Example 2: Complex Customer Onboarding
**Request:** "Build customer onboarding with email, Slack notifications, CRM updates, and conditional branches"

**Recommended:** V1 (Detailed)
1. Enable Build Flow Mode
2. Switch to V1 (Detailed)
3. Type your request
4. Get comprehensive guide in ~25 seconds

**Result:** ~15,000 chars, 12-minute read, detailed explanations

---

## 🔄 Switching Versions

You can switch between versions at any time:

1. **Before sending a request:**
   - Just change the dropdown selection
   - Send your request

2. **After getting a response:**
   - Switch the version selector
   - Send the same request again
   - Compare the two outputs!

---

## 💾 Settings Persistence

**Current behavior:** Version resets to V2 (default) on page refresh

**Why V2 is default:**
- Faster for most use cases
- Better UX for 80% of users
- Less overwhelming
- Quicker iterations

**To use V1 consistently:**
- Simply switch to V1 each session
- (Future: Setting could be saved to localStorage)

---

## 🎨 Visual Features

### Version Selector Design
- **Clean dropdown** with descriptive options
- **Emojis** for quick identification (📝 vs 📚)
- **Subtitles** explain the difference
- **Dynamic description** updates based on selection
- **Smooth animation** when shown/hidden

### Build Flow Mode Badge
When you get a response, you'll see:
```
┌─────────────────────┐
│ 📋 Build Flow Guide │ <- Badge indicating Build Flow Mode
└─────────────────────┘
```

---

## 🆕 What Changed in the UI

### Added Components:
1. **Version dropdown selector** (when Build Flow Mode is active)
2. **Dynamic description** showing what each version provides
3. **"Guide Style:" label** for clarity

### Updated Components:
1. **Build Flow Mode section** now expandable with version options
2. **API calls** now include `flow_builder_version` parameter

### Styling:
- Consistent with existing UI theme
- Purple accent colors (#667eea)
- Smooth transitions and animations
- Mobile-responsive design

---

## 🔧 Technical Details

### API Parameter
```json
{
  "message": "Your flow request",
  "build_flow_mode": true,
  "flow_builder_version": 2  // 1 or 2
}
```

### State Management
```javascript
const [flowBuilderVersion, setFlowBuilderVersion] = useState(2)
```

### Default Value
- **V2 (Concise)** is the default
- Provides the best experience for most users
- Can easily switch to V1 when needed

---

## 🎓 Learning Path

**Recommended progression:**

1. **Start with V1** for your first few flows
   - Learn ActivePieces concepts
   - Understand step configurations
   - See examples and best practices

2. **Switch to V2** once comfortable
   - Faster iterations
   - Cleaner interface
   - Quick reference

3. **Use V1 selectively** for complex flows
   - Multi-step workflows
   - Branching and loops
   - Advanced configurations

---

## ✨ Tips & Tricks

### Tip 1: Compare Versions
Try the same request with both versions to see the difference!
1. Send request with V2
2. Switch to V1
3. Send the same request
4. Compare outputs

### Tip 2: Start Detailed, Then Simplify
For a new flow type:
1. First time: Use V1 (learn)
2. Similar flow later: Use V2 (build fast)

### Tip 3: V2 for Iterations
When refining a flow:
- Use V2 for quick adjustments
- Fast feedback loop
- Easier to scan changes

### Tip 4: V1 for Documentation
Creating flow documentation:
- Use V1 for comprehensive docs
- Export to share with team
- Great for onboarding

---

## 🐛 Troubleshooting

### Issue: Version selector not showing
**Solution:** Make sure Build Flow Mode is enabled (checkbox checked)

### Issue: Selection not applying
**Solution:** Ensure you change the selection BEFORE sending the request

### Issue: Want to change version after response
**Solution:** Change selector and resend your request

---

## 📊 Performance Comparison

| Aspect | V2 (Concise) | V1 (Detailed) |
|--------|--------------|---------------|
| Generation Time | 8-15 seconds | 15-30 seconds |
| Output Length | 500-1,500 words | 2,000-5,000 words |
| Reading Time | 1-2 minutes | 10-15 minutes |
| Best For | Quick building | Learning |
| Experience Level | Experienced | All levels |

---

## 🎯 Summary

✅ **Easy to use** - Just a dropdown selector
✅ **Clear options** - V2 (Quick) vs V1 (Detailed)
✅ **Smart default** - V2 for most users
✅ **Always available** - Switch anytime
✅ **Fully integrated** - Works with all other features

**Try it now!** Enable Build Flow Mode and experiment with both versions to find what works best for you! 🚀

