# Model Council Setup Guide

## Overview

Model Council queries multiple LLM providers concurrently and returns their responses for synthesis. It requires no external dependencies beyond Python 3.

## Installation

The skill is installed at: `~/.claude/skills/model-council/`

Structure:
```
~/.claude/skills/model-council/
├── SKILL.md              # Skill definition for Claude Code
├── references/
│   ├── mac-setup.md      # Mac-specific setup
│   └── setup.md          # This file
└── scripts/
    └── council.py        # Main script
```

## Configuration

### Required: API Keys

Set environment variables for each provider you want to use. You need at least 2 for meaningful comparison.

```bash
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
export ANTHROPIC_API_KEY="sk-ant-..."
export DEEPSEEK_API_KEY="sk-..."
export XAI_API_KEY="xai-..."
export MISTRAL_API_KEY="..."
```

### Optional: Default Providers

```bash
export MODEL_COUNCIL_MODELS="openai,google,anthropic,deepseek"
```

## Supported Providers

| Key | Provider | Default Model |
|-----|----------|---------------|
| openai | OpenAI | gpt-4o |
| google | Google | gemini-2.5-pro-preview-06-05 |
| anthropic | Anthropic | claude-sonnet-4-20250514 |
| deepseek | DeepSeek | deepseek-chat |
| xai | xAI | grok-3 |
| mistral | Mistral | mistral-large-latest |

## Usage Examples

### Basic Query
```bash
python3 ~/.claude/skills/model-council/scripts/council.py "What is the best approach to error handling in distributed systems?"
```

### Specific Providers
```bash
python3 ~/.claude/skills/model-council/scripts/council.py --models openai,google "Explain CQRS pattern"
```

### With Context
```bash
python3 ~/.claude/skills/model-council/scripts/council.py \
  --context "Building a real-time chat application with 10M users" \
  "What database and message queue should we use?"
```

### JSON Output
```bash
python3 ~/.claude/skills/model-council/scripts/council.py --raw "Your question" | jq .
```

## Interpreting Results

The script returns:
- **Question**: The original question
- **Models queried/succeeded**: Count of providers contacted
- **Wall time**: Total execution time (concurrent)
- **Per-model responses**: Each model's answer with timing

Look for:
1. **Consensus**: Points where multiple models agree
2. **Unique insights**: Perspectives only one model provides
3. **Disagreements**: Areas of conflict worth investigating
4. **Quality signals**: Reasoning depth, citations, caveats
