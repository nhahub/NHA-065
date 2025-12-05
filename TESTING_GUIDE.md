# Quick Testing Guide - Enhanced Context Awareness

## 🧪 Test the New Features

### **Test 1: Direct Search (High Confidence)**
```
Enable web search ✓
Type: "Show me the Nike logo"
Expected: Direct search, Nike logo displayed
Intent: search (confidence: 0.85)
```

### **Test 2: Direct Generation (High Confidence)**
```
Type: "Create a logo for my tech startup"
Expected: Logo Reference Agent activated
Intent: generate (confidence: 0.95)
```

### **Test 3: Context Follow-Up Search**
```
1. "Search for Apple logo"
   → Apple logo shown
   
2. "Show me Microsoft too"
   → Microsoft logo shown (understands context!)
   
3. "What about Tesla"
   → Tesla logo shown (still searching)
```

### **Test 4: Context Follow-Up Generation**
```
1. "I'm working on a fitness brand"
   → Conversation response
   
2. "Modern and energetic style"
   → Confirms style preference
   
3. "Create it"
   → Generates fitness logo (understands "it" = the logo)
```

### **Test 5: Search → Generate Workflow**
```
1. "Find Nike logo"
   → Shows Nike logo
   
2. "Now create something similar for my sportswear brand"
   → Generates Nike-inspired logo
```

### **Test 6: Ambiguous Input Clarification**
```
Type: "logo"
Expected: AI asks: "Create new or search existing?"
Intent: conversation (low confidence)
```

### **Test 7: Implicit Confirmation**
```
1. "Design a coffee shop logo"
   → Shows preview with references
   
2. "yes"
   → Starts generation (understands confirmation)
```

### **Test 8: Negation Detection**
```
Type: "I don't want to create a logo yet"
Expected: Conversation, not generation
Intent: conversation (negation detected)
```

### **Test 9: Brand Name Recognition**
```
Type: "Tesla logo"
Expected: Searches for Tesla logo
Intent: search (capitalized brand detected)
```

### **Test 10: Multi-Part Request**
```
Type: "Search for inspiration from Starbucks, then create a cafe logo"
Expected: 
  1. Starbucks search first
  2. Then generation flow
Intent: search → generate (temporal order)
```

## 📊 Check Intent Detection

Watch the console for debug output:
```
🎯 Detected intent: search (confidence: 0.85)
💭 Intent: generate (confidence: 0.95)
🔍 Direct search triggered: Nike logo
🎨 High-confidence generation detected
```

## ✅ Success Indicators

**Good Intent Detection:**
- ✓ Search requests trigger searches immediately
- ✓ Generation requests show preview/references
- ✓ Conversations get helpful responses
- ✓ Follow-ups maintain context

**Poor Intent Detection:**
- ✗ Searches trigger generation
- ✗ Generation requests search instead
- ✗ AI asks to repeat context
- ✗ Follow-ups lose context

## 🐛 Debugging

If intent detection seems wrong, check:
1. Console logs for confidence scores
2. Conversation history being passed correctly
3. Web search toggle state
4. Pattern matching in classify_user_intent()

## 🎯 Performance Check

**Response Speed:**
- High-confidence requests: < 2 seconds
- Mistral consultations: 2-5 seconds
- Search + display: 3-7 seconds

**Accuracy:**
- Intent detection: Should be > 90%
- Context follow-ups: Should be > 85%
- Brand name recognition: Should be > 95%

## 💡 Tips

1. **Test with web search ON** - Full functionality
2. **Test with web search OFF** - Should gracefully handle
3. **Vary your language** - Test different phrasings
4. **Use conversation history** - Test follow-ups
5. **Mix intents** - Test complex workflows

## 📝 Report Issues

If you find issues, note:
- User input
- Expected intent
- Detected intent (from console)
- Confidence score
- Actual behavior
- Expected behavior

---

Happy testing! 🚀
