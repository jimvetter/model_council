---
name: "model-council"
description: >
  Multi-model research and synthesis. Queries multiple frontier LLMs (GPT-4o, Gemini, Claude,
  DeepSeek, Grok, Mistral) with a research question, then synthesizes their responses into a
  unified answer highlighting consensus, disagreements, and unique insights. Use when the user
  says "model council", "ask multiple models", "multi-model research", "cross-reference with
  other models", "get a second opinion", "what do other models think", or wants to verify
  important research across multiple AI perspectives.
---

# Model Council

Multi-model research and synthesis — like Perplexity's Model Council, but running locally through Claude Code.

## When to Apply

Use this skill when the user:
- Says "model council" or "run the council"
- Asks to "query multiple models" or "ask other models"
- Wants to "cross-reference" or "verify" research across models
- Says "get a second opinion" or "what do other models think"
- Needs high-confidence answers on important decisions
- Wants diverse AI perspectives on a complex topic
- Is doing investment research, strategic analysis, or technical evaluation

## How It Works


┌─────────────────────────────────────────────────────────┐
│ MODEL COUNCIL                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. RESEARCH (optional)                                  │
│    Claude gathers web context on the topic              │
│                                                         │
│ 2. QUERY                                                │
│    council.py sends question to multiple LLMs           │
│    concurrently via their APIs                          │
│                                                         │
│ 3. SYNTHESIZE                                           │
│    Claude analyzes all responses and produces           │
│    a unified answer with:                               │
│    - Consensus areas (models agree)                     │
│    - Unique insights (one model found something)        │
│    - Disagreements (models conflict)                    │
│    - Confidence assessment                              │
│    - Claude's own analysis and judgment                 │
│                                                         │
└─────────────────────────────────────────────────────────┘


## Workflow

### Phase 1: Clarify the Question

Before querying models, make sure the question is well-formed:
- If the user's question is vague, ask for clarification
- Identify whether this needs web research context first
- Determine if specific models should be targeted (or use all available)

### Phase 2: Gather Context (Optional)

If the question benefits from current information:
1. Use **WebSearch** to find relevant, up-to-date information
2. Summarize key facts that will help models give better answers
3. This context will be passed to all models alongside the question

### Phase 3: Query the Council

Run the council script to query all available models concurrently:

```bash
# Basic query - uses all models with API keys set
python skills/model-council/scripts/council.py "the research question"

# With context from Phase 2
python skills/model-council/scripts/council.py --context "relevant context here" "the question"

# Specific models only
python skills/model-council/scripts/council.py --models openai,google,deepseek "the question"

# Check which models are available
python skills/model-council/scripts/council.py --list-providers
```

Important: Always use `--raw` flag when you need to parse the output programmatically. The default output is formatted markdown for human reading.

### Phase 4: Synthesize

After collecting all model responses, produce a synthesis using this structure:

**SYNTHESIS TEMPLATE**

```markdown
# Council Synthesis: [Topic]

## Question
[The original question]

## Models Consulted
[List which models responded successfully]

## Consensus
[Where 2+ models agree. These are the highest-confidence findings.]
- **Finding 1:** [What they agree on] (Models: GPT-4o, Gemini, DeepSeek)
- **Finding 2:** [What they agree on] (Models: all)

## Unique Insights
[Valuable points raised by only one model — not contradicted, just not mentioned by others.]
- **[Model Name]:** [The unique insight and why it's valuable]

## Disagreements
[Where models directly conflict. Present both sides fairly.]
- **Topic:** [What they disagree about]
  - [Model A] argues: [position]
  - [Model B] argues: [position]
  - **Assessment:** [Which position is better supported and why]

## My Analysis
[Claude's own assessment integrating all perspectives. This is where you add value beyond
what any individual model said — connecting dots, identifying gaps, applying judgment.]

## Confidence Level
[Overall confidence in the synthesized answer: High / Medium / Low]
- **High confidence areas:** [topics where evidence is strong]
- **Lower confidence areas:** [topics that need further research]

## Recommended Next Steps
[If applicable — what the user should do with this information]
```

### Synthesis Guidelines

When writing the synthesis:

- **Be honest about disagreements** — Don't paper over conflicts. If models disagree, that's valuable signal about where uncertainty exists.

- **Weight by reasoning quality** — A well-reasoned minority opinion can be more valuable than a poorly-reasoned consensus. Evaluate the logic, not just the vote count.

- **Add your own analysis** — You (Claude) are not just a summarizer. You are another expert voice. Contribute your own reasoning, especially where you can connect insights across models.

- **Flag hallucination risk** — If a model makes a specific factual claim that others don't corroborate, note that it may need verification.

- **Distinguish fact from opinion** — Some disagreements are factual (one model is wrong) and some are legitimate differences in perspective. Label them accordingly.

- **Preserve nuance** — Don't flatten a complex multi-model discussion into oversimplified bullet points. The value is in the nuance.

## Examples

### Example 1: Strategic Decision
**User:** "Model council: Should we migrate from PostgreSQL to MongoDB for our event-driven architecture?"

**Workflow:**
1. No web research needed (technical question)
2. Query council with context about the user's architecture
3. Synthesize — expect disagreements on this one

### Example 2: Research Question
**User:** "Run the council on: What are the most promising approaches to AI alignment in 2026?"

**Workflow:**
1. Web search for latest alignment research papers and developments
2. Pass research context + question to council
3. Synthesize with emphasis on unique insights each model brings

### Example 3: Investment Research
**User:** "Ask multiple models: What's the bull and bear case for NVIDIA stock?"

**Workflow:**
1. Web search for latest NVIDIA financials, news, competitive landscape
2. Query council with all the context
3. Synthesize with heavy emphasis on disagreements and confidence levels

## Provider Setup

See `references/setup.md` for detailed instructions on obtaining API keys and configuring providers.

Quick check — Run this to see which providers are ready:
```bash
python skills/model-council/scripts/council.py --list-providers
```

### Supported Providers

| Provider   | Model            | Env Variable        | API Format        |
|-----------|------------------|---------------------|-------------------|
| openai    | GPT-4o           | OPENAI_API_KEY      | OpenAI            |
| google    | Gemini 2.5 Pro   | GOOGLE_API_KEY      | Google            |
| anthropic | Claude Sonnet 4  | ANTHROPIC_API_KEY   | Anthropic         |
| deepseek  | DeepSeek V3      | DEEPSEEK_API_KEY    | OpenAI-compatible |
| xai       | Grok 3           | XAI_API_KEY         | OpenAI-compatible |
| mistral   | Mistral Large    | MISTRAL_API_KEY     | OpenAI-compatible |

You need at least 2 providers configured for the council to be useful. The more providers, the stronger the consensus signal.

## Advanced Usage

### Custom Model Selection

Override the default model for any provider:

```bash
python skills/model-council/scripts/council.py \
  --model-override openai=gpt-4-turbo \
  --model-override google=gemini-2.0-flash \
  "Your question"
```

### Context from File

Pass a document as context:

```bash
python skills/model-council/scripts/council.py \
  --context-file ./research-notes.md \
  "Evaluate the approach described in the context"
```

### Default Provider Configuration

Set your preferred models via environment variable:

```bash
export MODEL_COUNCIL_MODELS="openai,google,deepseek"
```

## Tips for Best Results

- **Ask specific questions** — "What are the trade-offs of X vs Y for use case Z?" works better than "Tell me about X"
- **Provide context** — The more context you give, the better each model can tailor its response
- **Use for high-stakes decisions** — The council is most valuable when accuracy matters and you want to reduce blind spots
- **Don't over-rely on consensus** — Sometimes the minority model is right. Use consensus as signal, not gospel
- **Iterate** — If the first round reveals interesting disagreements, run a follow-up council focused on those specific points
