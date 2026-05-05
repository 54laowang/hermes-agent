---
name: design-image-studio
description: Directly generate design-oriented AI images with strong creative direction and prompt engineering. Use this skill for posters, product visuals, PPT illustrations, infographics, teaching/demo diagrams, campaign key visuals, cover art, or when the user wants design-quality image generation rather than generic AI art. This skill turns a loose brief into a design brief, assembles a structured prompt, routes to the right Volcengine Seedream settings, and can generate the image immediately.
---

# Design Image Studio

Generate design-quality images directly. This skill preserves the full Claude design-system prompt as the upstream design brain, then compiles that design logic into a shorter image-model prompt.

## Primary Source of Truth

Do not treat `references/design-principles.md` as the whole design system. It is only an index.

The primary design source is:

- `references/claude-design-sys-prompt-full.txt`

Always read that file first for substantive design work. Then use:

- `references/claude-design-map.md`
- `references/design-compiler.md`
- the task-specific reference file for the current request

This skill should preserve as much of the original design-system prompt as possible at the reasoning layer, while stripping away HTML/tool-specific noise before handing a prompt to the image model.

## When to Use

Use this skill when the user wants any of the following:

- Poster generation
- Product hero images, ad visuals, or e-commerce scenes
- PPT cover art, chapter art, or slide illustrations
- Infographic-style visuals
- Teaching/demo diagrams or explanatory scenes
- Visual concept exploration with stronger art direction than a generic image prompt

Do not use this skill for pixel-accurate UI recreation, editable charts, or layouts that require precise text rendering. For those, generate HTML/SVG/PPT assets instead.

## Default Workflow

1. Classify the request into one of: `poster`, `product`, `ppt`, `infographic`, `teaching`, or `auto`
2. Read the full design system prompt:
   - `references/claude-design-sys-prompt-full.txt`
3. Read the compiler references:
   - `references/claude-design-map.md`
   - `references/design-compiler.md`
   - `references/model-routing.md`
4. Read the matching task file, such as `references/poster.md`
5. If the user wants refinement or the first result is weak, also read:
   - `references/anti-slop-and-failure-patterns.md`
6. Compile the full design system into a `design_reasoning` layer:
   - purpose
   - audience
   - channel
   - context/brand strategy
   - visual system
   - hierarchy strategy
   - safe-zone or text-zone logic
   - anti-filler rules
   - anti-slop rules
   - task-specific design constraints
7. Condense the reasoning into a `compiled_brief`
8. Translate the compiled brief into the shortest useful image prompt
9. **[CHECKPOINT]** Parameter Confirmation (see Parameter Validation Checkpoint section below)
10. Run `scripts/design_image.py` to generate directly, unless the user explicitly asks for prompt-only output
11. **[CHECKPOINT]** Handle API failures gracefully (see Error Handling section below)
12. Iterate by changing one major variable at a time: direction, hierarchy, palette, lighting, realism, or density

## What Must Be Preserved From the Full Prompt

These must survive the compilation process:

- Start from purpose, audience, and channel
- Create a coherent visual system up front
- Treat hierarchy and whitespace as design decisions
- Avoid filler content and decorative noise
- Avoid AI-slop tropes
- Respect brand/context when available
- If no context exists, still commit to a strong direction instead of averaging styles
- Prefer multiple directions for ambiguous work, usually `conservative`, `balanced`, and `bold`

## Parameter Validation Checkpoint

**BEFORE generating any image, verify these parameters:**

### Required Parameter Checks

| Parameter | Valid Values | Default | Validation |
|-----------|-------------|---------|------------|
| `--task` | `poster`, `product`, `ppt`, `infographic`, `teaching`, `auto` | `auto` | Must match task type |
| `--brief` | Non-empty string | **REQUIRED** | Reject if empty or < 5 chars |
| `--aspect` | `1:1`, `3:4`, `4:3`, `16:9`, `9:16`, `3:2`, `2:3`, `4:5` | Task-dependent | Must be valid ratio |
| `--direction` | `conservative`, `balanced`, `bold` | `balanced` | Must be valid option |
| `--quality` | `draft`, `final`, `premium` | `final` | Must be valid option |

### Boundary Conditions for User Preferences

**Audience Parameter**:
- If not specified: Default to "broad professional audience"
- If specified but vague (e.g., "everyone"): Prompt for clarification
- Maximum length: 200 characters (truncate with warning if exceeded)

**Style/Mood/Goal Overrides**:
- If user provides conflicting style and mood: Warn and prefer `--style`
- If `--goal` conflicts with task's default goal: Use user's `--goal`
- Empty string = treat as not specified (use default)

**Aspect Ratio Edge Cases**:
- If user requests aspect ratio incompatible with task: Warn and suggest default
  - Example: `--task ppt --aspect 1:1` → Warn "PPT typically uses 16:9, continue?"
- If aspect ratio string is malformed: Fall back to task default

**Budget Constraints**:
- `--budget-limit` must be positive number > 0
- If budget < estimated cost: Reject with cost estimate
- If budget not specified: No limit enforced (user responsibility)

**Image References**:
- `--image` paths must exist (validate before generation)
- URLs must be accessible (quick HEAD request check)
- Max reference images: 4 (warn if more provided)

### Confirmation Display

Before calling the API, display:

```
[GENERATION CONFIRMATION]
Task: {task}
Brief: {brief_preview}...
Direction: {direction}
Aspect: {aspect} → Size: {width}x{height}
Quality: {quality} → Model: {model_id}
Estimated Cost: ¥{cost} CNY
Output: {output_path or 'auto-generated'}

Proceed with generation? [Y/n]
```

If user has `--dry-run` set, skip generation and only show this summary.

## Error Handling

### API Failure Scenarios

**Network Errors**:
- Connection timeout → Retry with exponential backoff (max 3 attempts)
- DNS resolution failure → Check internet connection, suggest offline mode
- SSL certificate error → Suggest updating certificates or using `--insecure` flag

**Authentication Errors**:
- Invalid API key → Check `VOLCENGINE_ACCESS_KEY` and `VOLCENGINE_SECRET_KEY` environment variables
- Expired credentials → Suggest regenerating keys from Volcengine console
- Insufficient quota → Suggest upgrading plan or waiting for quota reset

**Model Errors**:
- Model not found → Fall back to `doubao-seedream-4-0-250828` (draft model)
- Model overloaded → Wait 30 seconds and retry, or use fallback model
- Content policy violation → Explain policy, suggest prompt modification

**Generation Errors**:
- Prompt too long → Truncate to 2000 characters with warning
- Invalid parameters → List specific invalid parameters and valid options
- Output write failure → Check disk space and permissions

### Error Response Format

```json
{
  "error_type": "network|auth|model|generation|user_input",
  "error_code": "SPECIFIC_ERROR_CODE",
  "message": "Human-readable error description",
  "suggestion": "Concrete next step to resolve",
  "retry_possible": true|false,
  "fallback_options": ["option1", "option2"]
}
```

### Automatic Recovery Actions

1. **First failure**: Log error, wait 5 seconds, retry same parameters
2. **Second failure**: Switch to fallback model if available
3. **Third failure**: Return detailed error report to user with suggestions
4. **Budget exceeded**: Stop immediately, show partial results if any

## User Preference Boundary Conditions

### Preference Storage Limits

- Max stored preferences per user: 50 key-value pairs
- Max key length: 50 characters
- Max value length: 500 characters
- Preferences older than 90 days: Auto-archive with notification

### Preference Validation Rules

**Style Preferences**:
- Must not contain profanity or restricted content
- Must be descriptive adjectives (reject arbitrary strings)
- Valid examples: "minimalist", "corporate", "playful", "vintage"

**Color Preferences**:
- Accept hex codes (e.g., "#FF5500")
- Accept named colors (e.g., "navy blue", "forest green")
- Reject ambiguous colors (e.g., "nice blue") → Prompt for hex code

**Output Preferences**:
- Default output directory: `~/Pictures/design-studio/`
- If custom directory doesn't exist: Create it with user permission
- If directory not writable: Fall back to temp directory

### Conflict Resolution

When user preferences conflict with current request:

| Preference Type | Conflict Resolution |
|----------------|---------------------|
| Style vs Direction | Direction takes precedence (explicit override) |
| Default quality vs Requested quality | Requested quality wins |
| Saved aspect vs Task-specific aspect | Task-specific wins |
| Multiple conflicting saved styles | Use most recently saved |

## Primary Command

Use the wrapper script first. It is the opinionated entry point for this skill.

```bash
python3 scripts/design_image.py \
  --task poster \
  --brief "为 AI 训练营生成一张高冲击力招生海报，强调增长、实战和速度" \
  --direction balanced \
  --aspect 3:4 \
  --quality final \
  --output training-poster.png
```

## Prompt-Only Mode

If the user only wants prompts, do:

```bash
python3 scripts/design_image.py \
  --task product \
  --brief "高端陶瓷咖啡杯广告图，适合电商首图" \
  --prompt-only
```

The wrapper prints:

- `design_reasoning`
- `compiled_brief`
- final `prompt`

Use those intermediate layers to judge whether the full design-system prompt has actually been preserved.

## Task References

- `references/poster.md` — posters, key visuals, covers
- `references/product-image.md` — product ads, hero shots, e-commerce visuals
- `references/ppt-visual.md` — slide cover art, chapter visuals, concept illustrations
- `references/infographic.md` — infographic-like visuals and structured information compositions
- `references/teaching-demo.md` — educational and explanatory diagrams/scenes
- `references/claude-design-map.md` — which sections of the full design prompt matter for image generation
- `references/design-compiler.md` — how to compile the full prompt into design reasoning, a compiled brief, and a final image prompt

## Execution Notes

- Prefer `Seedream 5.0 lite` as the default final model
- Use lower-cost draft settings before premium reruns when the direction is still unclear
- Use image-to-image or multi-image fusion when the user provides source materials
- For infographic or teaching visuals, avoid asking the model to render dense, tiny text accurately; prefer text placeholders or low-text compositions
- The wrapper script is not the design brain; it is the compiler between the full design system and the image model
- Do not collapse the full design prompt into a few style adjectives unless the user explicitly wants a minimal prompt

## Files

- `scripts/design_image.py` — design compiler and prompt builder
- `scripts/generate.py` — bundled Volcengine generation engine
- `references/claude-design-sys-prompt-full.txt` — full upstream design-system prompt
- `references/claude-design-map.md` — section map for image use
- `references/design-compiler.md` — compilation workflow
- `references/models.md` — model and resolution reference
- `references/troubleshooting.md` — common error handling
