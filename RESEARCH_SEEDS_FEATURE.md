# 🔬 Research Seeds Feature - Director Home

## Overview

Enhanced the Director Home page to collect hashtags and reference creators/videos that seed the deep research process. When users don't provide custom seeds, we auto-fill with curated defaults based on the prompt type.

## User Experience

### 1. **Main Prompt Input**
Users describe what they want to create (same as before)

### 2. **Optional Research Seeds Section** (Collapsible)
Click "▶ Optional: Add Research Seeds" to expand and see:

- **Hashtags to analyze** (input field)
  - Example: `#startups #ycombinator #saas #productlaunch`
  - We analyze viral content using these hashtags
  
- **Reference creators/videos** (input field)
  - Example: `@cluely @tryskribe @notion`
  - Study specific creators/videos to extract their format

- **Info box** explaining:
  - How we analyze viral content
  - Extract successful patterns (hooks, pacing, format)
  - Apply to their video script & shot list

### 3. **Sample Prompt Behavior**
When clicking a sample prompt card:
- ✅ Prompt is filled
- ✅ Research seeds section auto-expands
- ✅ Hashtags and references are pre-filled with smart defaults
- ✅ User can edit or keep defaults
- ✅ Visual badge shows "⚡ Auto-fills hashtags & references"

### 4. **Behind the Scenes**
When creating a project, we append research context to the prompt:

```
[User's original prompt]

[Research Context for AI Director]:
Hashtags to analyze: #startups #ycombinator #saas
Reference creators/videos: @cluely @tryskribe @notion
Search keywords: cluely viral demo, YC demo day format
```

This context is **invisible to the user** but helps the Director AI agent:
1. Seed the deep research agent
2. Find relevant viral content
3. Extract successful patterns
4. Apply to the user's video

## Default Seeds by Prompt Type

### YC Demo Video (like Cluely)
```javascript
{
  hashtags: '#startups #ycombinator #saas #productlaunch #techstartup',
  references: '@cluely @tryskribe @notion @linear @superhuman',
  keywords: 'cluely viral demo, YC demo day format, product launch video'
}
```

### B2B Product Demo (YouTube)
```javascript
{
  hashtags: '#b2bsaas #productdemo #startups #enterprisesoftware #techexplained',
  references: '@loom @figma @notion @asana @slack',
  keywords: 'B2B product demo, software walkthrough, enterprise video'
}
```

### Educational Tutorial (Instagram)
```javascript
{
  hashtags: '#tutorial #howto #learnontiktok #educationalcontent #tiktoktutorial',
  references: '@mrbeast @mkbhd @levelstofame @teachingtech @skillshare',
  keywords: 'Instagram reels tutorial, educational short video, how-to content'
}
```

### Before/After Transformation (TikTok)
```javascript
{
  hashtags: '#beforeandafter #transformation #results #glowup #progresspics',
  references: '@ootdfash @fashionblogger @styleinfluencer @glowup @fitnesstransformation',
  keywords: 'before after video, transformation reel, results video'
}
```

## Implementation Details

### State Management
```javascript
const [showAdvanced, setShowAdvanced] = useState(false);
const [hashtags, setHashtags] = useState('');
const [references, setReferences] = useState('');
```

### Sample Prompt Click Handler
```javascript
const handleSamplePromptClick = (sample) => {
  setPrompt(sample.text);
  
  // Auto-fill with default seeds
  if (sample.seedType && defaultSeeds[sample.seedType]) {
    const seeds = defaultSeeds[sample.seedType];
    setHashtags(seeds.hashtags);
    setReferences(seeds.references);
    setShowAdvanced(true); // Expand to show
  }
};
```

### Enhanced Prompt Builder
```javascript
let enhancedPrompt = promptText;

if (seeds || userHashtags || userReferences) {
  enhancedPrompt += '\n\n[Research Context for AI Director]:';
  
  if (userHashtags) {
    enhancedPrompt += `\nHashtags to analyze: ${userHashtags}`;
  } else if (seeds?.hashtags) {
    enhancedPrompt += `\nHashtags to analyze: ${seeds.hashtags}`;
  }
  
  // ... similar for references and keywords
}
```

## UI Components

### Advanced Section Toggle
```jsx
<button onClick={() => setShowAdvanced(!showAdvanced)}>
  <Sparkles className="w-4 h-4" />
  <span>{showAdvanced ? '▼' : '▶'} Optional: Add Research Seeds</span>
  <span className="text-xs">(auto-filled for sample prompts)</span>
</button>
```

### Input Fields
- Clean, bordered text inputs
- Placeholder examples
- Helper text below each field
- Disabled during project creation

### Info Box
- Explains how research seeds work
- Bullet points for clarity
- Accent colors for visibility

### Sample Prompt Cards
Enhanced with:
- ⚡ Zap icon
- "Auto-fills hashtags & references" badge
- Border separator above badge

## Use Cases

### Use Case 1: Sample Prompt User
1. User clicks "Build me a YC demo video like Cluely"
2. Prompt fills: "Build me a YC demo video like Cluely"
3. Advanced section auto-expands
4. Hashtags filled: `#startups #ycombinator #saas #productlaunch #techstartup`
5. References filled: `@cluely @tryskribe @notion @linear @superhuman`
6. User sees the seeds and can edit or keep them
7. Clicks "Start Project"
8. Behind scenes: Research context appended to prompt

### Use Case 2: Custom Prompt User (No Seeds)
1. User types: "Create a cooking tutorial for TikTok"
2. User doesn't expand advanced section
3. Clicks "Start Project"
4. No research seeds added (or smart defaults based on keywords)

### Use Case 3: Custom Prompt User (With Seeds)
1. User types: "Create a fitness transformation video"
2. User expands advanced section
3. Adds custom hashtags: `#fitness #transformation #gains`
4. Adds custom references: `@davidgoggins @athleanx`
5. Clicks "Start Project"
6. Custom seeds used instead of defaults

## Future Enhancements

### For Deep Research Agent Integration
When the deep research agent is ready, it will receive:
- User's goal/prompt
- Hashtags to scrape from TikTok/Instagram/YouTube
- Creator accounts to analyze
- Search keywords for additional context

The agent can then:
1. **Scrape Content**: Fetch videos using hashtags
2. **Analyze Patterns**: Extract hooks, pacing, format structure
3. **Score Success**: Identify high-performing elements
4. **Generate Insights**: Create recommendations based on findings
5. **Apply to User**: Customize shot list and scripts

### Potential UI Improvements
- **Preview Mode**: Show what will be researched before creating
- **Seed Library**: Save favorite hashtag/reference combos
- **Trending Seeds**: Suggest currently viral hashtags
- **Auto-Complete**: Suggest creators as user types
- **Validation**: Check if hashtags/creators exist
- **Visual Examples**: Show thumbnail of reference videos

## Benefits

### For Users
✅ **Control**: Can specify exact content to analyze
✅ **Guidance**: Smart defaults help if they're unsure
✅ **Transparency**: See what will be researched
✅ **Flexibility**: Edit defaults or leave as-is
✅ **Learning**: Discover relevant creators in their niche

### For AI Director
✅ **Context**: Better understanding of desired style
✅ **Examples**: Concrete content to analyze
✅ **Accuracy**: More targeted recommendations
✅ **Relevance**: Format matches user's niche
✅ **Data**: Rich research corpus to draw from

## Testing Checklist

- [ ] Click sample prompt → Seeds auto-fill
- [ ] Edit auto-filled seeds → Changes persist
- [ ] Clear seeds → Empty fields work
- [ ] Custom prompt + custom seeds → Both used
- [ ] Custom prompt + no seeds → Works without seeds
- [ ] Toggle advanced section → Smooth animation
- [ ] Keyboard shortcut (⌘ Enter) → Creates project with seeds
- [ ] Sample prompt badge → Shows "Auto-fills" indicator
- [ ] Info box → Clear explanation visible

## Files Modified

- `/app/frontend/src/components/DirectorHome.jsx`
  - Added state for hashtags, references, showAdvanced
  - Added defaultSeeds mapping
  - Enhanced handleCreateProject to append research context
  - Updated handleSamplePromptClick to auto-fill seeds
  - Added collapsible advanced section UI
  - Added info box with explanation
  - Enhanced sample prompt cards with badge

## Summary

This feature bridges the gap between user intent and AI research by:
1. **Collecting** specific hashtags/creators to analyze
2. **Auto-filling** smart defaults for common use cases
3. **Appending** research context behind the scenes
4. **Empowering** users to guide the AI's research process

Perfect for seeding the deep research agent when it's ready! 🚀
