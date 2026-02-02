# BMAD Forge - User Training Guide
## Inline Editing Feature

**Training Version:** 1.0  
**Feature Version:** 1.2.0  
**Target Audience:** End Users  
**Duration:** 30 minutes

---

## Training Objectives

By the end of this training, you will be able to:

✅ Navigate the step-by-step wizard  
✅ Edit section headings and content  
✅ Use the rich text editor effectively  
✅ Understand real-time validation feedback  
✅ Generate compliant BMAD prompts  
✅ Troubleshoot common issues  

---

## Module 1: Introduction (5 minutes)

### What's New?

**Before:** Templates were static - you could only fill in variables.

**Now:** You can edit EVERYTHING:
- ✏️ Section headings
- 📝 Section content (with formatting!)
- 🔤 Variables
- 🎨 Rich text formatting

### Why This Matters

**Better Customization:**
- Adapt templates to your specific needs
- Add your organization's terminology
- Include project-specific details

**Professional Output:**
- Format text for readability
- Emphasize key points
- Create structured lists

**Still BMAD Compliant:**
- Real-time validation
- Guidance and suggestions
- Compliance checking

---

## Module 2: Getting Started (5 minutes)

### Starting a New Prompt

1. **Login to BMAD Forge**
   ```
   https://bmad-forge.example.com
   ```

2. **Go to Dashboard**
   - Click "Dashboard" in navigation

3. **Choose "Generate Document"**
   - Big blue button or navigation menu

4. **Select Your Template**
   - Browse by category:
     - Agent Prompts (Architect, Developer, QA, etc.)
     - Document Templates (PRD, Design Spec, etc.)
   - Click "Generate" on chosen template

5. **Wizard Starts**
   - You'll see Step 1 of N
   - Progress bar shows your position

### Understanding the Interface

```
┌─────────────────────────────────────────────┐
│  Progress:  ███████░░░░░░░░░░  40% (2/5)   │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│  Step 2: Your Role                          │
│  ┌───────────────────────────────────────┐  │
│  │ Section Heading:                      │  │
│  │ [Your Role as System Architect     ]  │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Section Content:                           │
│  ┌───────────────────────────────────────┐  │
│  │ [Rich Text Editor with Toolbar]       │  │
│  │ Act as an **elite** system architect  │  │
│  │ who transforms requirements into...    │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  [Reset] [Previous] [Next]                  │
└─────────────────────────────────────────────┘
```

---

## Module 3: Editing Section Headings (3 minutes)

### How to Edit Headings

**Step 1:** Find the "Section Heading" field at the top

**Step 2:** Click in the field

**Step 3:** Edit the text
```
Original:  "Your Role"
Custom:    "Your Role as Senior Backend Developer"
```

**Step 4:** Press Tab or click outside to save

### Best Practices

✅ **DO:**
- Make headings descriptive
- Use consistent capitalization
- Keep headings concise (< 60 characters)
- Reflect your actual content

❌ **DON'T:**
- Use ALL CAPS (except acronyms)
- Include special characters unnecessarily
- Make headings too long
- Use vague terms

### Examples

**Good:**
- "Your Role as Healthcare Data Architect"
- "Input: Patient Data Requirements"
- "Output: HIPAA-Compliant Analysis Report"

**Bad:**
- "ROLE" (too generic)
- "Your Role as a Super Amazing Awesome Developer!!!" (too long, unprofessional)
- "Input/Output/Everything" (unclear)

---

## Module 4: Using the Rich Text Editor (10 minutes)

### The Toolbar

```
[B] [I] [U] [▼] [≡] [1.] ["] [</>] [∞] [✓]
 │   │   │   │   │   │    │   │    │   │
 │   │   │   │   │   │    │   │    │   └─ Clear formatting
 │   │   │   │   │   │    │   │    └───── Insert link
 │   │   │   │   │   │    │   └────────── Code block
 │   │   │   │   │   │    └───────────── Blockquote
 │   │   │   │   │   └─────────────────── Numbered list
 │   │   │   │   └───────────────────────── Bulleted list
 │   │   │   └─────────────────────────────── Heading level
 │   │   └──────────────────────────────────── Underline
 │   └───────────────────────────────────────── Italic
 └────────────────────────────────────────────── Bold
```

### Formatting Text

#### Making Text Bold

1. Select the text
2. Click **[B]** button (or Ctrl/Cmd + B)
3. Text becomes **bold**

**Use for:** Key terms, important concepts, headings

#### Making Text Italic

1. Select the text
2. Click **[I]** button (or Ctrl/Cmd + I)
3. Text becomes *italic*

**Use for:** Emphasis, examples, foreign words

#### Creating Lists

**Bulleted List:**
1. Click **[≡]** button
2. Type first item, press Enter
3. Type next item, press Enter
4. Press Enter twice to exit list

**Numbered List:**
1. Click **[1.]** button
2. Type first item, press Enter
3. Type next item (auto-numbers)
4. Press Enter twice to exit list

#### Adding Headers

1. Place cursor on line
2. Click **[▼]** dropdown
3. Select Header 1, 2, or 3
4. Line becomes a heading

**Use for:** Sub-sections within your content

### Practical Exercise

**Task:** Format this text

```
Original:
You will receive patient data including demographics, vital signs, and test results. The data will be in HL7 FHIR format. You must validate the data structure and check for completeness.

Formatted:
You will receive patient data including:
- Demographics
- Vital signs
- Test results

The data will be in **HL7 FHIR** format.

You must:
1. Validate the data structure
2. Check for completeness
```

### Tips & Tricks

**Keyboard Shortcuts:**
- **Ctrl/Cmd + B** = Bold
- **Ctrl/Cmd + I** = Italic
- **Ctrl/Cmd + Z** = Undo
- **Ctrl/Cmd + Y** = Redo
- **Ctrl/Cmd + K** = Insert link

**Copy-Paste:**
- Paste from Word/Docs works!
- Formatting may need adjustment
- Use "Clear formatting" if needed

**Undo/Redo:**
- Made a mistake? Use Undo
- Unlimited undo levels
- Works across editing session

---

## Module 5: Variables and Real-Time Validation (5 minutes)

### Filling in Variables

Some sections have **variables** - placeholders for your specific info.

**Example:**
```
Variable field shown above editor:

Project Name: [_____________________]
Technology:   [_____________________]

These will replace {{PROJECT_NAME}} and {{TECHNOLOGY}} in your content.
```

**How to Fill:**
1. Type in each field
2. Values auto-save as you move
3. See real-time updates in content

### Understanding Validation

**Validation Box:** Appears below editor as you type

**Types of Feedback:**

**✅ Success (Green):**
```
✓ Content looks good!
Section completion: 95%
```
**Action:** None needed, you're good!

**⚠️ Warning (Yellow):**
```
⚠ Section seems short (12 words). 
  Consider adding more detail.
```
**Action:** Optional - add more if appropriate

**❌ Error (Red):**
```
✗ Unreplaced variables found: PROJECT_NAME
```
**Action:** Required - fix before generating

**💡 Suggestion (Blue):**
```
💡 Consider specifying output format
💡 Add examples for clarity
```
**Action:** Helpful tips - use if relevant

### Word Count

```
Section Content:     [Editor]     45 words

Minimum 10 words recommended.
```

**What it means:**
- Shows current word count
- Compares to minimum recommendation
- Helps ensure complete content

---

## Module 6: Navigation and Workflow (3 minutes)

### Moving Between Steps

**Next Button:**
- Saves current step automatically
- Moves to next section
- Available when validation passes

**Previous Button:**
- Go back to review/edit
- Your changes are saved
- Can navigate freely

**Progress Indicator:**
- Shows current step (2 of 5)
- Click on completed steps to jump there
- Visual progress bar

### Resetting Content

**Reset Button:** Restores original template

1. Click **[Reset]** button
2. Confirm dialog appears
3. Click "Yes" to reset
4. Both heading and content restored

**When to use:**
- Started over with approach
- Want template default back
- Made errors and want fresh start

**Warning:** This deletes all your edits for this section!

---

## Module 7: Generating Your Prompt (3 minutes)

### Final Step

When you reach the last section:

1. Review the "Generate Document" button
2. Check overall progress (should be 100%)
3. Review any warnings/errors
4. Click **[Generate Document]**

### What Happens

```
Generating your document...
├─ Converting rich text to Markdown
├─ Replacing all variables
├─ Validating BMAD compliance
└─ Creating final document

✓ Success!
```

### Viewing Results

**Result Page Shows:**
- Your generated prompt (Markdown)
- Compliance status
- Validation details
- Export options

**Actions You Can Take:**
- **Copy to Clipboard** - Use in ChatGPT/Claude
- **Download as .md** - Save locally
- **Export to PDF** - Share with team
- **Save to Library** - Reuse later

---

## Module 8: Troubleshooting (3 minutes)

### Common Issues

#### Issue: Editor Not Loading

**Symptoms:** White box instead of editor

**Solutions:**
1. Refresh the page (F5)
2. Check internet connection (Quill loads from CDN)
3. Disable browser extensions temporarily
4. Try different browser (Chrome, Firefox, Safari)

#### Issue: Content Not Saving

**Symptoms:** Changes disappear when navigating

**Solutions:**
1. Check if session timed out (2 hours)
2. Ensure cookies enabled
3. Click "Next" to save (don't just navigate away)
4. Check browser console for errors (F12)

#### Issue: Validation Errors Won't Clear

**Symptoms:** Red errors remain after fixing

**Solutions:**
1. Wait 1 second (validation is debounced)
2. Click outside editor to trigger check
3. Ensure all variables filled in
4. Check for {{BRACKETS}} in content

#### Issue: Formatting Not Showing

**Symptoms:** Bold/italic buttons don't work

**Solutions:**
1. Select text first, then click button
2. Use keyboard shortcuts instead
3. Refresh page if toolbar frozen
4. Check if text already has formatting

### Getting Help

**In-App Support:**
- Click **[?]** icon for context help
- Hover over labels for tooltips
- Check validation suggestions

**Documentation:**
- User Guide (comprehensive)
- FAQ section
- Video tutorials (if available)

**Contact Support:**
- Email: support@bmad-forge.example.com
- Use feedback button (thumbs down)
- Include screenshot if possible

---

## Module 9: Best Practices (3 minutes)

### Content Quality

✅ **Be Specific**
```
Bad:  "Handle data"
Good: "Process patient demographic data using HL7 FHIR standards"
```

✅ **Use Examples**
```
Include examples when helpful:
- Input example: "Patient ID: P12345"
- Output example: "Validated: true, Errors: []"
```

✅ **Be Concise**
```
Bad:  "You need to make absolutely certain that you are carefully 
       and thoroughly validating each and every piece of data..."
Good: "Validate all data fields for completeness and format compliance."
```

### Formatting Guidelines

**Use Bold For:**
- Key terms (first mention)
- Important concepts
- Section sub-headings
- Critical requirements

**Use Italic For:**
- Emphasis
- Examples
- Technical terms
- Foreign words

**Use Lists For:**
- Multiple items
- Steps/procedures
- Requirements
- Features/capabilities

**Use Headers For:**
- Major sub-sections
- Organizing long content
- Topic breaks

### Workflow Tips

**Start → Finish:**
- Complete wizard in one sitting (2-hour session)
- Or: Note where you stopped (can't resume later)

**Review Before Generating:**
- Navigate back through steps
- Check each section
- Verify variables filled
- Fix any warnings

**Save Your Work:**
- Generated prompt is saved automatically
- Download backup copy
- Bookmark for future reference

---

## Module 10: Hands-On Practice (Optional)

### Practice Exercise 1: Basic Editing

**Task:** Create a simple Developer Agent prompt

1. Select "Developer Agent" template
2. Edit heading: "Your Role as Python Developer"
3. Add bold text: "You are a **Python expert**"
4. Create bulleted list of skills
5. Fill in PROJECT_NAME variable
6. Generate document

**Time:** 5 minutes

### Practice Exercise 2: Advanced Formatting

**Task:** Create an Input section with complex formatting

1. Use **bold** for data types
2. Use *italic* for examples
3. Create numbered steps
4. Add a code snippet (inline code)
5. Include a validation rule list

**Time:** 5 minutes

### Practice Exercise 3: Full Workflow

**Task:** Complete entire wizard

1. Choose any template
2. Customize all section headings
3. Edit all section content
4. Use various formatting options
5. Fill all variables
6. Review and fix validation issues
7. Generate final document

**Time:** 15 minutes

---

## Quick Reference Card

### Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Bold | Ctrl + B | Cmd + B |
| Italic | Ctrl + I | Cmd + I |
| Underline | Ctrl + U | Cmd + U |
| Undo | Ctrl + Z | Cmd + Z |
| Redo | Ctrl + Y | Cmd + Y |
| Link | Ctrl + K | Cmd + K |

### Toolbar Quick Guide

| Icon | Function | Use |
|------|----------|-----|
| **B** | Bold | Emphasis, key terms |
| *I* | Italic | Examples, emphasis |
| U | Underline | Rarely needed |
| ▼ | Headers | Sub-sections |
| ≡ | Bullet List | Unordered items |
| 1. | Numbered List | Steps, sequences |
| " | Blockquote | Quotes, callouts |
| </> | Code Block | Code examples |
| ∞ | Link | URLs, references |
| ✓ | Clear Format | Remove formatting |

### Validation Icons

| Icon | Meaning | Action |
|------|---------|--------|
| ✓ | Success | Continue |
| ⚠️ | Warning | Review, optional fix |
| ✗ | Error | Must fix |
| 💡 | Suggestion | Consider tip |

---

## Assessment Questions

### Knowledge Check

1. **What can you edit in the new wizard?**
   - [ ] Only variables
   - [x] Section headings, content, and variables
   - [ ] Only content
   - [ ] Template structure

2. **What happens when you click Reset?**
   - [ ] Deletes the entire document
   - [ ] Clears only variables
   - [x] Restores section heading and content to template default
   - [ ] Goes back to previous step

3. **How long does a wizard session last?**
   - [ ] 30 minutes
   - [ ] Forever
   - [x] 2 hours
   - [ ] Until you close browser

4. **What does yellow validation mean?**
   - [ ] Critical error
   - [x] Warning - should review but optional
   - [ ] Success
   - [ ] Suggestion

5. **What format is the final output?**
   - [ ] HTML
   - [ ] Word document
   - [x] Markdown
   - [ ] Plain text

**Answers:** 1-b, 2-c, 3-c, 4-b, 5-c

---

## Training Complete! 🎉

### What You Learned

✅ How to navigate the wizard  
✅ Editing headings and content  
✅ Using the rich text editor  
✅ Understanding validation  
✅ Generating compliant prompts  
✅ Troubleshooting issues  

### Next Steps

1. **Practice:** Try creating a few prompts
2. **Explore:** Test different templates
3. **Share:** Show colleagues
4. **Feedback:** Use the feedback button
5. **Learn More:** Read comprehensive User Guide

### Resources

📖 **Comprehensive User Guide**
- INLINE_EDITING_USER_GUIDE.md
- Detailed explanations
- More examples
- Complete FAQ

🎥 **Video Tutorials** (if available)
- Visual walkthroughs
- Screen recordings
- Step-by-step demos

💬 **Support**
- Email: support@bmad-forge.example.com
- In-app help: Click [?] icon
- Documentation: /docs/

---

**Thank you for attending this training!**

**Training Version:** 1.0  
**Last Updated:** February 2, 2026  
**Feedback:** training-feedback@bmad-forge.example.com
