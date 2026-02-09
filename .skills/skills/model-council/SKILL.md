# Model Council Skill

A multi-model prompt and synthesis skill that queries multiple LLM APIs concurrently to gather diverse perspectives on research questions.

## Description

Model Council allows you to send a question to multiple AI models simultaneously (GPT-5.2, Gemini 3.0 Pro, Claude Sonnet 4.5, DeepSeek V3, Grok 3, Mistral Large) and collect their responses for comparison and synthesis. This is useful for:

- Getting diverse perspectives on complex questions
- Fact-checking by comparing responses across models
- Research where multiple viewpoints are valuable
- Identifying consensus or disagreement between models

## Usage

When the user asks to "query the council", "ask multiple models", "get perspectives from different AIs", or similar requests, use this skill.

### Running the Council

Execute the council script with the user's question:

```bash
python3 ~/.claude/skills/model-council/scripts/council.py "Your question here"
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--models` | `-m` | Comma-separated providers to query | All with API keys |
| `--context` | `-c` | Add background context to the question | None |
| `--context-file` | | Read context from a file | None |
| `--max-tokens` | `-t` | Maximum tokens per response | 4096 |
| `--temperature` | | Response randomness (0.0-1.5) | 0.7 |
| `--deep-research` | `-d` | Enable deep research mode for thorough analysis | Off |
| `--list-providers` | `-l` | Show available providers and API key status | |
| `--raw` | | Output raw JSON instead of formatted markdown | |
| `--model-override` | | Override model for a provider (provider=model) | |

### Deep Research Mode

When `--deep-research` is enabled, models are instructed to:
- Provide more detailed analysis with specific facts and data points
- Explore multiple perspectives and counterarguments
- Acknowledge limitations and areas of uncertainty
- Structure responses with clear sections
- Go beyond surface-level answers into nuances and implications

Use deep research for complex questions where thoroughness matters more than speed.

### Temperature Guide

| Value | Behavior | Use For |
|-------|----------|---------|
| 0.0-0.3 | Factual, deterministic | Code, math, factual lookups |
| 0.4-0.6 | Balanced, focused | Technical writing, analysis |
| 0.7 | Default - creative + accurate | General research |
| 0.8-1.0 | More creative, varied | Brainstorming, creative writing |
| 1.0+ | Highly random | Experimental ideas |

### Max Tokens Guide

| Tokens | Approximate Length | Use For |
|--------|-------------------|---------|
| 256-512 | 1 paragraph | Quick answers |
| 1024 | 2-3 paragraphs | Concise responses |
| 4096 | 3-4 pages (default) | Detailed research |
| 8192+ | Long-form | Deep dives, essays |

### Examples

```bash
# Query all available models (default)
python3 ~/.claude/skills/model-council/scripts/council.py "What are the key considerations for microservices architecture?"

# Query specific providers only
python3 ~/.claude/skills/model-council/scripts/council.py --models openai,anthropic "Explain quantum entanglement"

# Add context to the question
python3 ~/.claude/skills/model-council/scripts/council.py --context "We are building a fintech startup" "What database should we use?"

# Short, factual responses
python3 ~/.claude/skills/model-council/scripts/council.py --max-tokens 1024 --temperature 0.3 "What is the capital of France?"

# Long, creative brainstorming
python3 ~/.claude/skills/model-council/scripts/council.py --max-tokens 8192 --temperature 0.9 "Brainstorm startup ideas for AI in healthcare"

# Check which providers are configured
python3 ~/.claude/skills/model-council/scripts/council.py --list-providers
```

### Natural Language Examples

Users may request variations like:
- "Ask the council about X" → Run with default settings
- "Query the council with short responses" → Use `--max-tokens 1024`
- "Get factual answers from multiple models" → Use `--temperature 0.3`
- "Brainstorm with the council, be creative" → Use `--temperature 0.9`
- "Ask only OpenAI and Anthropic about X" → Use `--models openai,anthropic`
- "Deep dive research on X" → Use `--max-tokens 8192`
- "Do deep research on X" → Use `--deep-research`
- "Have the council thoroughly analyze X" → Use `--deep-research`
- "Get comprehensive analysis from multiple models" → Use `--deep-research`
- "Explore multiple perspectives on X" → Use `--deep-research`

## Requirements

### API Keys

Set the following environment variables for each provider you want to use:

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | GPT-5.2 |
| Google | `GOOGLE_API_KEY` | Gemini 3.0 Pro |
| Anthropic | `ANTHROPIC_API_KEY` | Claude Sonnet 4.5 |
| DeepSeek | `DEEPSEEK_API_KEY` | DeepSeek V3 |
| xAI | `XAI_API_KEY` | Grok 3 |
| Mistral | `MISTRAL_API_KEY` | Mistral Large |

You need at least 2 API keys configured for meaningful comparison.

## No Dependencies Required

This skill uses only Python standard library - no pip install needed.

## Synthesizing Results (REQUIRED)

**IMPORTANT: After running the council and displaying the raw results, you MUST always provide a synthesis summary with the following sections:**

### 1. Consensus
Identify and list the key points where multiple models agree. These represent higher-confidence insights.

### 2. Disagreements & Different Perspectives
Highlight any areas where models disagree, provide different recommendations, or emphasize different aspects. Explain the nature of the disagreement so the user understands multiple viewpoints.

### 3. Unique Insights
Note any valuable points that only one model mentioned. These may represent specialized knowledge or creative angles worth considering.

### 4. Combined Recommendation
Provide a synthesized answer that:
- Prioritizes consensus points
- Acknowledges areas of uncertainty or debate
- Combines the strongest reasoning from each model
- Gives the user a clear, actionable takeaway

**Example synthesis format:**

```
## Council Synthesis

### Consensus (High Confidence)
- Point A (mentioned by all models)
- Point B (GPT-5.2 and Claude agree)

### Different Perspectives
- On topic X: GPT-5.2 recommends Y, while Claude suggests Z because...

### Unique Insights
- GPT-5.2 uniquely mentioned...
- Claude uniquely mentioned...

### Recommendation
Based on the council's input, the strongest approach is... [combined insight]
```

This synthesis is the primary value of the Model Council - helping the user understand not just what each model said, but what the collective intelligence suggests.
