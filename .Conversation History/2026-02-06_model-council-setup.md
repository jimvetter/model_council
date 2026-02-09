# Model Council Skill Setup - Conversation Summary
**Date:** February 6, 2026  
**Platform:** Cursor IDE on Mac

---

## What is Model Council?

**Model Council** is a skill that sends your question to multiple AI models simultaneously (GPT-5.2, Gemini 3.0 Pro, Claude Sonnet 4.5, and optionally DeepSeek, Grok, Mistral) and collects their responses for comparison.

### Why Use It?
- **Get diverse perspectives** on complex questions
- **Identify consensus** - when multiple models agree, you can have higher confidence
- **Spot disagreements** - see where models differ and why
- **Reduce bias** - no single model's blind spots dominate
- **Research & fact-checking** - compare answers across different knowledge bases

### How It Works
1. You ask a question
2. The skill sends it to all configured models in parallel
3. Each model responds independently
4. You receive all responses plus a synthesis showing:
   - What models agree on (consensus)
   - Where they disagree (different perspectives)
   - Unique insights from each model
   - A combined recommendation

### When to Use It
- Research questions with multiple valid approaches
- Topics where you want multiple expert opinions
- Fact-checking or verification
- Complex decisions with trade-offs
- Brainstorming where different perspectives help

---

## How to Use Model Council

### In Claude Code (Natural Language)
Just ask naturally:
- "Ask the council about [topic]"
- "Query multiple models about [question]"
- "Do deep research on [topic]"
- "Get perspectives from different AIs on [question]"

### Command Line (Direct)
```bash
# Basic query
python3 ~/.claude/skills/model-council/scripts/council.py "Your question here"

# Deep research mode (more thorough)
python3 ~/.claude/skills/model-council/scripts/council.py --deep-research "Your question"

# Limit response length
python3 ~/.claude/skills/model-council/scripts/council.py --max-tokens 2000 "Your question"

# Query specific models only
python3 ~/.claude/skills/model-council/scripts/council.py --models openai,anthropic "Your question"

# Add context
python3 ~/.claude/skills/model-council/scripts/council.py --context "Background info" "Your question"

# Check which providers are configured
python3 ~/.claude/skills/model-council/scripts/council.py --list-providers
```

### Available Options
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--models` | `-m` | Choose specific providers | All with API keys |
| `--context` | `-c` | Add background context | None |
| `--max-tokens` | `-t` | Token limit per response | 4096 |
| `--temperature` | | Randomness 0.0-1.5 | 0.7 |
| `--deep-research` | `-d` | Thorough multi-perspective analysis | Off |
| `--list-providers` | `-l` | Show configured providers | |
| `--raw` | | Output JSON instead of markdown | |

### Deep Research Mode
Add `--deep-research` (or `-d`) for complex questions. Models will:
- Provide more detailed analysis with specific facts
- Explore multiple perspectives and counterarguments
- Acknowledge limitations and uncertainty
- Structure responses with clear sections
- Go beyond surface-level answers

---

## Setup Summary (What Was Done)

### 1. Repository Setup
- Cloned from `https://github.com/jimvetter/model_council.git`
- Original repo had skill files in `skills/model-council/`

### 2. Skill Installation (Claude Code)
Installed skill to `~/.claude/skills/model-council/` with:
- `SKILL.md` - Skill definition and instructions
- `scripts/council.py` - Main Python script (no dependencies required)
- `references/mac-setup.md` - Mac setup guide
- `references/setup.md` - General setup documentation

### 3. API Keys Configured
Added to `~/.zprofile`:
```bash
export OPENAI_API_KEY="sk-proj-x-..."
export GOOGLE_API_KEY="AIza..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### 4. Model Configuration
Updated to use current model IDs:
| Provider | Model Name | API Model ID |
|----------|------------|--------------|
| OpenAI | GPT-5.2 | `gpt-5.2` |
| Google | Gemini 3.0 Pro | `gemini-3-pro-preview` |
| Anthropic | Claude Sonnet 4.5 | `claude-sonnet-4-5` |
| DeepSeek | DeepSeek V3 | `deepseek-chat` |
| xAI | Grok 3 | `grok-3` |
| Mistral | Mistral Large | `mistral-large-latest` |

**Note:** Google free tier quota was exhausted; needs billing enabled to work.

### 5. Features Added
- Command-line options for `--max-tokens`, `--temperature`, `--deep-research`
- Deep research mode for thorough multi-perspective analysis
- Required synthesis summary (consensus, disagreements, unique insights, recommendation)

### 6. Python Compatibility Fix
Fixed `str | None` type hints to use `Optional[str]` for compatibility with older Python versions.

### 7. OpenAI API Fix
Added `openai_new` format that uses `max_completion_tokens` instead of `max_tokens` for GPT-5.2.

---

## Test Queries Run
1. "Top 10 pizza places in Nashville TN" - Worked (2/3 models)
2. "Top 10 music therapy programs in the US" - Worked (2/3 models)
3. "Top 5 marketing strategies for corporate event photography" - Worked (2/3 models)

---

## Pending Issues

### 1. Google API Quota
Gemini 3.0 Pro returns HTTP 429 (quota exceeded). Needs:
- Enable billing on Google Cloud/AI Studio, OR
- Wait for free tier quota to reset

### 2. Cowork Integration
Skill is installed for Claude Code (`~/.claude/skills/`) but Cowork uses different paths:
- Cowork looks at `/mnt/.skills/skills/` (container/cloud environment)
- Local Mac files not accessible from Cowork
- **Solution needed:** Sync via GitHub or manually copy to Cowork

### 3. Multi-Device Sync
Need to sync skill files between home Mac and laptop without hardcoded paths.

---

## File Locations

### On Mac (Claude Code)
```
~/.claude/skills/model-council/
├── SKILL.md
├── scripts/
│   └── council.py
└── references/
    ├── mac-setup.md
    └── setup.md
```

### Local Workspace Copy
```
~/Projects/model_council/.skills/skills/model-council/
├── SKILL.md
├── scripts/
│   └── council.py
└── references/
    ├── mac-setup.md
    └── setup.md
```

### API Keys
```
~/.zprofile
```

---

## Next Steps

1. **Sync devices** - Set up sync between home Mac and laptop
2. **Fix Cowork access** - Push to GitHub and pull into Cowork, or copy files manually
3. **Enable Google billing** - To get Gemini 3.0 Pro working
4. **Optional:** Add more API keys (DeepSeek, xAI, Mistral) for broader council
