# Mac Setup for Model Council

## Quick Start

1. **Verify Python 3 is installed:**
   ```bash
   python3 --version
   ```

2. **Set up API keys in your shell profile** (`~/.zshrc` for zsh or `~/.bash_profile` for bash):
   ```bash
   # Model Council API Keys
   export OPENAI_API_KEY="your-openai-key"
   export GOOGLE_API_KEY="your-google-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export DEEPSEEK_API_KEY="your-deepseek-key"
   export XAI_API_KEY="your-xai-key"
   export MISTRAL_API_KEY="your-mistral-key"
   
   # Optional: Set default providers
   export MODEL_COUNCIL_MODELS="openai,google,anthropic"
   ```

3. **Reload your shell:**
   ```bash
   source ~/.zshrc
   ```

4. **Test the installation:**
   ```bash
   python3 ~/.claude/skills/model-council/scripts/council.py --list-providers
   ```

## Getting API Keys

| Provider | Get API Key |
|----------|-------------|
| OpenAI | https://platform.openai.com/api-keys |
| Google | https://aistudio.google.com/app/apikey |
| Anthropic | https://console.anthropic.com/settings/keys |
| DeepSeek | https://platform.deepseek.com/api_keys |
| xAI | https://console.x.ai/ |
| Mistral | https://console.mistral.ai/api-keys |

## Troubleshooting

### "No API keys found" error
- Verify your API keys are exported in your shell profile
- Run `source ~/.zshrc` to reload
- Check with `echo $OPENAI_API_KEY` (should show your key)

### Permission denied
- Make the script executable: `chmod +x ~/.claude/skills/model-council/scripts/council.py`

### Python not found
- Install Python 3: `brew install python3`
