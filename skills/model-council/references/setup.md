# Model Council Setup Guide

## Quick Start

1. Get API keys from at least 2 providers (see below)
2. Set them as environment variables
3. Run `python skills/model-council/scripts/council.py --list-providers` to verify

## Getting API Keys

### OpenAI (GPT-4o)
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Set: `export OPENAI_API_KEY="sk-..."`
4. Pricing: ~$2.50/1M input tokens, ~$10/1M output tokens (GPT-4o)

### Google (Gemini)
1. Go to https://aistudio.google.com/apikey
2. Create an API key
3. Set: `export GOOGLE_API_KEY="AI..."`
4. Pricing: Free tier available, then ~$1.25/1M input tokens (Gemini 2.5 Pro)

### Anthropic (Claude)
1. Go to https://console.anthropic.com/settings/keys
2. Create a new API key
3. Set: `export ANTHROPIC_API_KEY="sk-ant-..."`
4. Pricing: ~$3/1M input tokens, ~$15/1M output tokens (Claude Sonnet 4)

### DeepSeek
1. Go to https://platform.deepseek.com/api_keys
2. Create an API key
3. Set: `export DEEPSEEK_API_KEY="sk-..."`
4. Pricing: ~$0.27/1M input tokens, ~$1.10/1M output tokens (DeepSeek V3)

### xAI (Grok)
1. Go to https://console.x.ai/
2. Create an API key
3. Set: `export XAI_API_KEY="xai-..."`
4. Pricing: ~$3/1M input tokens, ~$15/1M output tokens (Grok 3)

### Mistral
1. Go to https://console.mistral.ai/api-keys
2. Create an API key
3. Set: `export MISTRAL_API_KEY="..."`
4. Pricing: ~$2/1M input tokens, ~$6/1M output tokens (Mistral Large)

## Persisting API Keys

Add your exports to your shell profile so they persist across sessions:

```bash
# Add to ~/.bashrc, ~/.zshrc, or ~/.profile
export OPENAI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export DEEPSEEK_API_KEY="your-key-here"
# ... etc
```

Then reload: `source ~/.bashrc` (or restart your terminal).

## Setting Default Providers

If you only want to query specific models by default:

```bash
export MODEL_COUNCIL_MODELS="openai,google,deepseek"
```

Without this, the script auto-detects all providers that have API keys set.

## Cost Estimation

Each council query sends the same prompt to all configured models. Typical costs per query (assuming ~500 input tokens, ~2000 output tokens):

| Provider                    | Approximate Cost Per Query |
|-----------------------------|---------------------------|
| OpenAI (GPT-4o)            | ~$0.02                    |
| Google (Gemini 2.5 Pro)    | ~$0.01                    |
| Anthropic (Claude Sonnet 4)| ~$0.03                    |
| DeepSeek V3                | ~$0.002                   |
| xAI (Grok 3)              | ~$0.03                    |
| Mistral Large              | ~$0.01                    |

- **Full 6-model council:** ~$0.10 per query
- **3-model council (OpenAI + Google + DeepSeek):** ~$0.03 per query

## Recommended Configurations

### Budget-Friendly (3 models, ~$0.03/query)
```bash
export MODEL_COUNCIL_MODELS="openai,google,deepseek"
```

### Balanced (4 models, ~$0.06/query)
```bash
export MODEL_COUNCIL_MODELS="openai,google,deepseek,mistral"
```

### Maximum Coverage (all 6 models, ~$0.10/query)
Set all API keys and don't set `MODEL_COUNCIL_MODELS` (auto-detect).

## Troubleshooting

### "No API keys found"
Make sure environment variables are set in the current shell session. Run `echo $OPENAI_API_KEY` to check.

### HTTP 401 / 403 errors
Your API key is invalid or expired. Generate a new one from the provider's console.

### HTTP 429 errors
You've hit a rate limit. Wait a moment and try again, or check your provider's rate limit settings.

### Timeout errors
The default timeout is 120 seconds. Some models (especially reasoning models) may need longer. Check your network connection.

### A model returns low-quality responses
Try overriding with a different model variant:

```bash
python council.py --model-override openai=gpt-4-turbo "your question"
```
