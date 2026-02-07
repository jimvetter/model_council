# Model Council Setup Guide for Mac

## Prerequisites

- **Python 3.10+** — Check with `python3 --version`. If missing: `brew install python@3.12`
- **Claude Code** — Check with `claude --version`. If missing: `npm install -g @anthropic-ai/claude-code`

## Step 1: Get API Keys

You need at least 2 providers. Recommended starting set (best value at ~$0.03/query total):

| Provider              | Sign Up / Get Key                          | Approx Cost Per Query |
|-----------------------|--------------------------------------------|-----------------------|
| OpenAI (GPT-4o)      | https://platform.openai.com/api-keys       | ~$0.02                |
| Google (Gemini 2.5 Pro) | https://aistudio.google.com/apikey       | ~$0.01                |
| DeepSeek (V3)        | https://platform.deepseek.com/api_keys     | ~$0.002               |

For each provider:
1. Create an account (if you don't have one)
2. Navigate to the API keys page
3. Generate a new API key
4. Copy the key — you'll need it in the next step

### Optional Additional Providers

| Provider              | Sign Up / Get Key                              | Approx Cost Per Query |
|-----------------------|------------------------------------------------|-----------------------|
| xAI (Grok 3)        | https://console.x.ai/                          | ~$0.03                |
| Mistral (Large)      | https://console.mistral.ai/api-keys            | ~$0.01                |
| Anthropic (Claude Sonnet 4) | https://console.anthropic.com/settings/keys | ~$0.03               |

A full 6-model council costs ~$0.10 per query.

## Step 2: Set Environment Variables

Open your shell profile in a text editor:

```bash
open ~/.zshrc
```

> If you use bash instead of zsh, use `open ~/.bashrc`

Add the following lines at the bottom of the file (replace with your actual keys):

```bash
# ----- Model Council API Keys -----
export OPENAI_API_KEY="sk-your-key-here"
export GOOGLE_API_KEY="AIyour-key-here"
export DEEPSEEK_API_KEY="sk-your-key-here"

# Optional additional providers (uncomment and fill in as needed):
# export XAI_API_KEY="xai-your-key-here"
# export MISTRAL_API_KEY="your-key-here"
# export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Optional: restrict which providers are used by default
# (without this, all providers with keys set will be queried)
# export MODEL_COUNCIL_MODELS="openai,google,deepseek"
```

Save the file, then reload your shell:

```bash
source ~/.zshrc
```

## Step 3: Deploy the Skill to Claude Code

```bash
cd ~/Claude_Skills/skills
bash ../scripts/deploy_to_claude_code.sh model-council global
```

This copies the skill to `~/.claude/skills/model-council/` so it's available in every Claude Code session.

## Step 4: Verify Setup

Confirm your API keys are detected:

```bash
python3 ~/.claude/skills/model-council/scripts/council.py --list-providers
```

Expected output (for the 3-provider setup):

```
## Available Providers

Provider     Model                     API Key Env Var           Status
--------------------------------------------------------------------------------
anthropic    Claude Sonnet 4           ANTHROPIC_API_KEY         [-] NOT SET
deepseek     DeepSeek V3              DEEPSEEK_API_KEY          [+] SET
google       Gemini 2.5 Pro           GOOGLE_API_KEY            [+] SET
mistral      Mistral Large            MISTRAL_API_KEY           [-] NOT SET
openai       GPT-4o                   OPENAI_API_KEY            [+] SET
xai          Grok 3                   XAI_API_KEY               [-] NOT SET
```

## Step 5: Test It

Start a fresh Claude Code session:

```bash
claude
```

Then try any of these prompts:

```
Model council: What are the most important considerations when choosing
between REST and GraphQL for a new API?

Run the council on: What's the bull and bear case for investing in AI
infrastructure companies in 2026?

Ask multiple models: What are the three most promising approaches to
reducing LLM hallucinations?
```

Claude will:
1. Optionally gather web research context
2. Run `council.py` to query your configured models concurrently
3. Collect all responses
4. Synthesize a unified answer highlighting consensus, unique insights,
   disagreements, and Claude's own analysis

## How It Works

```
You ask a question
    |
    v
Claude Code (orchestrator)
    |
    |-- Optional: WebSearch for current context
    |
    |-- council.py fires parallel API calls:
    |       |-->  OpenAI (GPT-4o)
    |       |-->  Google (Gemini 2.5 Pro)
    |       \-->  DeepSeek (V3)
    |
    |-- All responses collected
    |
    \-- Claude synthesizes into unified answer:
            * Consensus (where models agree)
            * Unique insights (only one model found)
            * Disagreements (models conflict)
            * Claude's own analysis
            * Confidence assessment
```

## Advanced Usage

### Query specific models only

```
Model council with just OpenAI and Google: Is Rust or Go better for
building microservices?
```

Claude will pass `--models openai,google` to the script.

### Provide context from a file

```
Run the council on the approach described in ./architecture-proposal.md —
is this the right direction?
```

Claude will read the file and pass it as `--context` to all models.

### Override model versions

```
Run the council using GPT-4-turbo and Gemini Flash instead of the
defaults: What's the fastest way to implement auth in a Next.js app?
```

Claude will use `--model-override` flags.

## Troubleshooting

### "No API keys found"
Your environment variables aren't loaded. Run `echo $OPENAI_API_KEY` to check.
Fix: `source ~/.zshrc` or open a new terminal window.

### HTTP 401 or 403 errors
Your API key is invalid or expired. Generate a new one from the provider's console.

### HTTP 429 errors (rate limit)
Wait a moment and try again. Check your usage/billing on the provider's dashboard.
Some providers require adding a payment method before API access works.

### Timeout errors
Default timeout is 120 seconds. If a model is slow, it may be experiencing high load.
Try again, or exclude that provider for now.

### Skill not recognized by Claude
Make sure you deployed globally and restarted Claude Code:

```bash
ls ~/.claude/skills/model-council/SKILL.md   # should exist
claude   # start fresh session
```

### A model gives low-quality responses
Override with a different model variant. For example, to use GPT-4-turbo
instead of GPT-4o, Claude will pass `--model-override openai=gpt-4-turbo`.

## Cost Management

| Configuration  | Models                       | Cost Per Query |
|---------------|------------------------------|----------------|
| Budget        | OpenAI + Google + DeepSeek   | ~$0.03         |
| Balanced      | + Mistral                    | ~$0.04         |
| Full coverage | All 6 providers              | ~$0.10         |

At $0.03/query, you could run 33 council queries for $1. Compare to Perplexity
Max at $200/year — you'd need to run ~6,600 queries/year to match that cost
with the budget setup, or about 18 per day.
