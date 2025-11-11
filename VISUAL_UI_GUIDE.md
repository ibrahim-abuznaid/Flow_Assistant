# 🎨 Visual UI Guide - Flow Builder Version Selector

## What You'll See in the UI

### Before Enabling Build Flow Mode

```
┌─────────────────────────────────────────────────────┐
│ Input Area                                           │
├─────────────────────────────────────────────────────┤
│                                                       │
│ ☐ 🔧 Build Flow Mode                                │
│                                                       │
│ ☐ 🌐 Enable Web Search                              │
│                                                       │
│ 🤖 Primary Model: [gpt-5-mini ▼]                    │
│                                                       │
│ ☐ 🔀 Use 2 Models                                   │
│                                                       │
├─────────────────────────────────────────────────────┤
│ [Type your message here...            ] [📤 Send]   │
└─────────────────────────────────────────────────────┘
```

---

### After Enabling Build Flow Mode (NEW VERSION SELECTOR APPEARS!)

```
┌─────────────────────────────────────────────────────┐
│ Input Area                                           │
├─────────────────────────────────────────────────────┤
│                                                       │
│ ☑ 🔧 Build Flow Mode (Active)                       │
│     ┌───────────────────────────────────────────┐  │
│     │ Guide Style:                              │  │
│     │ [📝 Concise (V2) - Quick & Structured  ▼]│  │ ← NEW!
│     └───────────────────────────────────────────┘  │
│     ⚡ Fast, organized steps with emojis -          │
│     best for experienced users                      │
│                                                       │
│ ☐ 🌐 Enable Web Search                              │
│                                                       │
│ 🤖 Primary Model: [gpt-5-mini ▼]                    │
│                                                       │
│ ☐ 🔀 Use 2 Models                                   │
│                                                       │
├─────────────────────────────────────────────────────┤
│ [Describe the flow you want to build...] [📤 Send] │
└─────────────────────────────────────────────────────┘
```

---

### When You Click the Dropdown

```
┌─────────────────────────────────────────────────────┐
│ ☑ 🔧 Build Flow Mode (Active)                       │
│     ┌───────────────────────────────────────────┐  │
│     │ Guide Style:                              │  │
│     │ ┌───────────────────────────────────────┐│  │
│     │ │📝 Concise (V2) - Quick & Structured ✓││  │ ← Selected
│     │ │📚 Detailed (V1) - Comprehensive       ││  │
│     │ └───────────────────────────────────────┘│  │
│     └───────────────────────────────────────────┘  │
│     ⚡ Fast, organized steps with emojis -          │
│     best for experienced users                      │
└─────────────────────────────────────────────────────┘
```

---

### If You Select V1 (Detailed)

```
┌─────────────────────────────────────────────────────┐
│ ☑ 🔧 Build Flow Mode (Active)                       │
│     ┌───────────────────────────────────────────┐  │
│     │ Guide Style:                              │  │
│     │ [📚 Detailed (V1) - Comprehensive      ▼]│  │
│     └───────────────────────────────────────────┘  │
│     📖 Detailed explanations with examples -        │
│     best for learning                               │ ← Description changed!
│                                                       │
│ ☐ 🌐 Enable Web Search                              │
└─────────────────────────────────────────────────────┘
```

---

## 📱 Mobile View

### Compact Layout on Mobile

```
┌──────────────────────────┐
│ Input Area               │
├──────────────────────────┤
│                          │
│ ☑ 🔧 Build Flow Mode     │
│   (Active)               │
│                          │
│ Guide Style:             │
│ [📝 Concise (V2)... ▼]  │
│                          │
│ ⚡ Fast, organized steps │
│ with emojis - best for   │
│ experienced users        │
│                          │
│ ☐ 🌐 Enable Web Search  │
│                          │
│ 🤖 Primary Model:       │
│ [gpt-5-mini ▼]          │
│                          │
└──────────────────────────┘
```

---

## 🎨 Color Scheme

### Normal State
- **Dropdown border:** Light gray (#e0e0e0)
- **Text color:** Dark gray (#333)
- **Background:** White

### Hover State
- **Dropdown border:** Purple (#667eea) ← Accent color
- **Smooth transition:** 0.2s

### Focus State
- **Dropdown border:** Purple (#667eea)
- **Glow effect:** Purple shadow (rgba(102, 126, 234, 0.1))

### Disabled State (While Generating)
- **Opacity:** 50%
- **Cursor:** Not allowed
- **No hover effects**

---

## ✨ Interactive Elements

### 1. Dropdown Selector
```
┌─────────────────────────────────────────┐
│ [📝 Concise (V2) - Quick & Structured ▼]│ ← Click to open
└─────────────────────────────────────────┘
         ↓ Opens dropdown
┌─────────────────────────────────────────┐
│ 📝 Concise (V2) - Quick & Structured ✓ │ ← Currently selected
│ 📚 Detailed (V1) - Comprehensive        │ ← Click to switch
└─────────────────────────────────────────┘
```

### 2. Dynamic Description
```
V2 Selected:
  ⚡ Fast, organized steps with emojis - best for experienced users

V1 Selected:
  📖 Detailed explanations with examples - best for learning
```

---

## 🔄 Animation Flow

### When Enabling Build Flow Mode

```
Frame 1:    ☐ 🔧 Build Flow Mode
            [No version selector]

Frame 2:    ☑ 🔧 Build Flow Mode (Active)
            [Fade in animation...]

Frame 3:    ☑ 🔧 Build Flow Mode (Active)
            Guide Style: [📝 Concise (V2)... ▼]
            ⚡ Fast, organized...
            [Fully visible]
```

**Animation:** Smooth fade-in (0.3s ease-in)

---

## 📊 Complete UI Layout

### Full Input Area with All Features

```
┌─────────────────────────────────────────────────────────┐
│                     INPUT AREA                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ☑ 🔧 Build Flow Mode (Active)                       ││ ← Toggle
│ │   ┌───────────────────────────────────────────────┐││
│ │   │ Guide Style:                                  │││
│ │   │ [📝 Concise (V2) - Quick & Structured      ▼]│││ ← NEW!
│ │   └───────────────────────────────────────────────┘││
│ │   ⚡ Fast, organized steps with emojis -            ││
│ │   best for experienced users                        ││
│ └─────────────────────────────────────────────────────┘│
│                                                           │
│ ┌─────────────────────────────────────────────────────┐│
│ │ ☑ 🌐 Enable Web Search (Active)                    ││ ← Toggle
│ │   Allow agent to search the internet if needed     ││
│ └─────────────────────────────────────────────────────┘│
│                                                           │
│ ┌─────────────────────────────────────────────────────┐│
│ │ 🤖 Primary Model: [gpt-5-mini ▼]                   ││ ← Dropdown
│ │                                                      ││
│ │ ☑ 🔀 Use 2 Models                                  ││ ← Toggle
│ │                                                      ││
│ │ 🤖 Secondary Model: [gpt-5 ▼]                      ││ ← Dropdown
│ │   Primary for analysis, Secondary for planning     ││
│ └─────────────────────────────────────────────────────┘│
│                                                           │
├─────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐  ┌──────┐ │
│ │ Describe the flow you want to build...  │  │ 📤  │ │ ← Input
│ │                                          │  │Send  │ │
│ └─────────────────────────────────────────┘  └──────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Visual Features

### 1. Consistent Styling
- Matches existing UI theme
- Purple accent colors (#667eea)
- Clean, modern design
- Smooth transitions

### 2. Clear Hierarchy
```
Level 1: Build Flow Mode Toggle (Primary)
  └─ Level 2: Version Selector (Secondary)
       └─ Level 3: Description (Tertiary)
```

### 3. Visual Feedback
- ✅ Hover effects (border color change)
- ✅ Focus states (glow effect)
- ✅ Disabled states (grayed out)
- ✅ Active indicators (checkmarks)

### 4. Emojis for Quick Scanning
- 📝 = V2 (Concise/Quick)
- 📚 = V1 (Detailed/Learning)
- ⚡ = Fast/Speed
- 📖 = Educational/Learning

---

## 💡 Usage Visual Flow

### Step-by-Step Visual Guide

**Step 1:** Enable Build Flow Mode
```
☐ → ☑ 🔧 Build Flow Mode (Active)
```

**Step 2:** Version selector appears
```
     ↓ Smooth fade-in animation
Guide Style: [📝 Concise (V2) - Quick & Structured ▼]
⚡ Fast, organized steps...
```

**Step 3:** Click dropdown to see options
```
     ↓ Click
┌─────────────────────────────────────┐
│ 📝 Concise (V2) - Quick & Struct. ✓│
│ 📚 Detailed (V1) - Comprehensive    │
└─────────────────────────────────────┘
```

**Step 4:** Select your preference
```
     ↓ Click V1
Guide Style: [📚 Detailed (V1) - Comprehensive ▼]
📖 Detailed explanations with examples...
      ↑ Description updates instantly
```

**Step 5:** Send your request
```
[Your flow request...] → [📤 Send]
```

**Step 6:** Get formatted response
```
V2 Output:                    V1 Output:
┌───────────────────┐        ┌────────────────────┐
│ 📋 Requirements   │        │ # Flow Guide       │
│ - Item 1          │        │ ## Overview        │
│ - Item 2          │        │ [Detailed intro]   │
│                   │        │                    │
│ 🔄 Flow Steps     │        │ ## Prerequisites   │
│                   │        │ [Complete list]    │
│ 🎯 TRIGGER        │        │                    │
│ **Piece:** Gmail  │        │ ## Instructions    │
│ ...               │        │ [Step-by-step]     │
└───────────────────┘        └────────────────────┘
   ~800 chars                   ~15,000 chars
```

---

## 🎨 Design Principles

### 1. **Progressive Disclosure**
- Version selector only shows when needed
- Keeps UI clean when not using Build Flow Mode

### 2. **Clear Defaults**
- V2 (Concise) is pre-selected
- Best for most users
- Easy to change if needed

### 3. **Visual Hierarchy**
- Emojis for quick identification
- Bold labels for importance
- Italic descriptions for context

### 4. **Responsive Design**
- Works on all screen sizes
- Touch-friendly on mobile
- Optimized for tablets

### 5. **Accessible Design**
- High contrast text
- Clear focus indicators
- Keyboard navigable

---

## 🔍 Comparison View

### Side-by-Side: Before vs After

**Before (No Version Selector):**
```
┌─────────────────────────────┐
│ ☑ 🔧 Build Flow Mode        │
│   (Active)                  │
│                             │
│ Get comprehensive guides    │ ← Generic description
└─────────────────────────────┘
```

**After (With Version Selector):**
```
┌─────────────────────────────────────┐
│ ☑ 🔧 Build Flow Mode (Active)       │
│   ┌───────────────────────────────┐│
│   │ Guide Style:                  ││
│   │ [📝 Concise (V2) - Quick... ▼]││ ← NEW CONTROL!
│   └───────────────────────────────┘│
│   ⚡ Fast, organized steps with    │ ← Dynamic description
│   emojis - best for experienced    │
│   users                             │
└─────────────────────────────────────┘
```

---

## ✅ Visual Checklist

What to look for when testing:

- [x] Version selector appears when Build Flow Mode is ON
- [x] Version selector hides when Build Flow Mode is OFF
- [x] Dropdown is properly styled (border, padding, colors)
- [x] Options show emojis (📝 and 📚)
- [x] Hover effect changes border color to purple
- [x] Focus effect shows purple glow
- [x] Description updates when selection changes
- [x] Smooth fade-in animation when appearing
- [x] Works on mobile (responsive)
- [x] Disabled state shows when generating
- [x] Text is readable and clear

---

## 🎉 Final Result

You now have a **beautiful, intuitive version selector** that:
- ✨ Looks professional
- 🎯 Is easy to understand
- 💨 Loads smoothly
- 📱 Works everywhere
- 🎨 Matches the design system
- ⚡ Provides instant feedback

**Try it yourself!** Enable Build Flow Mode and see the version selector in action! 🚀

---

## 📸 Quick Reference

### What Each Version Looks Like in UI

**V2 (Concise) - Default:**
```
📝 Concise (V2) - Quick & Structured
⚡ Fast, organized steps with emojis - best for experienced users
```

**V1 (Detailed):**
```
📚 Detailed (V1) - Comprehensive
📖 Detailed explanations with examples - best for learning
```

**That's it!** Simple, clear, and effective. 🎯

