#!/usr/bin/env python3
"""
Model Council - Query multiple LLM APIs concurrently and collect responses.

Uses only Python stdlib (no pip install required).

Usage:
    python council.py "Your research question here"
    python council.py --models openai,google,deepseek "Your question"
    python council.py --context "background info" "Your question"
    echo "Your question" | python council.py --stdin

Environment variables for API keys:
    OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY,
    DEEPSEEK_API_KEY, XAI_API_KEY, MISTRAL_API_KEY

Set MODEL_COUNCIL_MODELS to a comma-separated list of providers to use by default.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict

# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

PROVIDERS = {
    "openai": {
        "name": "GPT-5.2",
        "url": "https://api.openai.com/v1/chat/completions",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-5.2",
        "format": "openai_new",
    },
    "google": {
        "name": "Gemini 3.0 Pro",
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "env_key": "GOOGLE_API_KEY",
        "default_model": "gemini-3-pro-preview",
        "format": "google",
    },
    "anthropic": {
        "name": "Claude Sonnet 4.5",
        "url": "https://api.anthropic.com/v1/messages",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-5",
        "format": "anthropic",
    },
    "deepseek": {
        "name": "DeepSeek V3",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "env_key": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
        "format": "openai",
    },
    "xai": {
        "name": "Grok 3",
        "url": "https://api.x.ai/v1/chat/completions",
        "env_key": "XAI_API_KEY",
        "default_model": "grok-3",
        "format": "openai",
    },
    "mistral": {
        "name": "Mistral Large",
        "url": "https://api.mistral.ai/v1/chat/completions",
        "env_key": "MISTRAL_API_KEY",
        "default_model": "mistral-large-latest",
        "format": "openai",
    },
}

TIMEOUT_SECONDS = 120

# ---------------------------------------------------------------------------
# API request builders
# ---------------------------------------------------------------------------

def _build_openai_request(provider: dict, api_key: str, prompt: str, model: str, max_tokens: int = 4096, temperature: float = 0.7) -> tuple:
    """Build request for OpenAI-compatible APIs (DeepSeek, xAI, Mistral, older OpenAI models)."""
    url = provider["url"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }).encode()
    return url, headers, body


def _build_openai_new_request(provider: dict, api_key: str, prompt: str, model: str, max_tokens: int = 4096, temperature: float = 0.7) -> tuple:
    """Build request for newer OpenAI models (GPT-5.2+) that use max_completion_tokens."""
    url = provider["url"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": max_tokens,
        "temperature": temperature,
    }).encode()
    return url, headers, body


def _build_anthropic_request(provider: dict, api_key: str, prompt: str, model: str, max_tokens: int = 4096, temperature: float = 0.7) -> tuple:
    """Build request for the Anthropic Messages API."""
    url = provider["url"]
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    return url, headers, body


def _build_google_request(provider: dict, api_key: str, prompt: str, model: str, max_tokens: int = 4096, temperature: float = 0.7) -> tuple:
    """Build request for the Google Gemini API."""
    url = provider["url_template"].format(model=model) + f"?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        },
    }).encode()
    return url, headers, body


# ---------------------------------------------------------------------------
# Response parsers
# ---------------------------------------------------------------------------

def _parse_openai_response(data: dict) -> str:
    return data["choices"][0]["message"]["content"]


def _parse_anthropic_response(data: dict) -> str:
    return "".join(block["text"] for block in data["content"] if block["type"] == "text")


def _parse_google_response(data: dict) -> str:
    return data["candidates"][0]["content"]["parts"][0]["text"]


# ---------------------------------------------------------------------------
# Core query function
# ---------------------------------------------------------------------------

REQUEST_BUILDERS = {
    "openai": _build_openai_request,
    "openai_new": _build_openai_new_request,
    "anthropic": _build_anthropic_request,
    "google": _build_google_request,
}

RESPONSE_PARSERS = {
    "openai": _parse_openai_response,
    "openai_new": _parse_openai_response,
    "anthropic": _parse_anthropic_response,
    "google": _parse_google_response,
}


def query_model(provider_key: str, prompt: str, model_override: Optional[str] = None, max_tokens: int = 4096, temperature: float = 0.7) -> dict:
    """Query a single model provider. Returns a result dict."""
    provider = PROVIDERS[provider_key]
    api_key = os.environ.get(provider["env_key"], "")
    if not api_key:
        return {
            "provider": provider_key,
            "model_name": provider["name"],
            "status": "skipped",
            "error": f"No API key found (set {provider['env_key']})",
            "response": None,
            "elapsed_seconds": 0,
        }

    model = model_override or provider["default_model"]
    fmt = provider["format"]
    build_fn = REQUEST_BUILDERS[fmt]
    parse_fn = RESPONSE_PARSERS[fmt]

    url, headers, body = build_fn(provider, api_key, prompt, model, max_tokens, temperature)

    start = time.time()
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode())
        text = parse_fn(data)
        elapsed = time.time() - start
        return {
            "provider": provider_key,
            "model_name": provider["name"],
            "model_id": model,
            "status": "success",
            "response": text,
            "elapsed_seconds": round(elapsed, 2),
        }
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        error_body = ""
        try:
            error_body = e.read().decode()[:500]
        except Exception:
            pass
        return {
            "provider": provider_key,
            "model_name": provider["name"],
            "model_id": model,
            "status": "error",
            "error": f"HTTP {e.code}: {error_body}",
            "response": None,
            "elapsed_seconds": round(elapsed, 2),
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            "provider": provider_key,
            "model_name": provider["name"],
            "model_id": model,
            "status": "error",
            "error": str(e),
            "response": None,
            "elapsed_seconds": round(elapsed, 2),
        }


def query_council(
    question: str,
    context: Optional[str] = None,
    providers: Optional[List[str]] = None,
    model_overrides: Optional[Dict[str, str]] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    deep_research: bool = False,
) -> dict:
    """Query multiple models concurrently and return structured results."""

    # Determine which providers to query
    if providers is None:
        env_models = os.environ.get("MODEL_COUNCIL_MODELS", "")
        if env_models:
            providers = [p.strip() for p in env_models.split(",") if p.strip()]
        else:
            # Auto-detect: use all providers that have API keys set
            providers = [
                key for key, cfg in PROVIDERS.items()
                if os.environ.get(cfg["env_key"])
            ]

    if not providers:
        return {
            "question": question,
            "context_provided": bool(context),
            "providers_queried": 0,
            "providers_succeeded": 0,
            "total_elapsed_seconds": 0,
            "error": "No API keys found. Set at least 2 provider API keys as environment variables. See --list-providers.",
            "results": [],
        }

    # Build the full prompt
    parts = []
    if context:
        parts.append(f"## Background Context\n{context}\n")
    parts.append(f"## Research Question\n{question}")
    
    if deep_research:
        parts.append(
            "\n## Instructions (Deep Research Mode)\n"
            "Provide an exceptionally thorough and comprehensive analysis of the question above. "
            "Your response should:\n\n"
            "1. **Provide detailed analysis** with specific facts, data points, and concrete examples\n"
            "2. **Explore multiple perspectives** - consider different viewpoints, approaches, and schools of thought\n"
            "3. **Address counterarguments** - what are the opposing views or potential downsides?\n"
            "4. **Acknowledge limitations and uncertainty** - be explicit about what you don't know or where evidence is mixed\n"
            "5. **Structure your response clearly** with distinct sections and headers\n"
            "6. **Go beyond surface-level answers** - dig into the nuances, edge cases, and deeper implications\n\n"
            "Take your time to think through this comprehensively. Depth and thoroughness are valued over brevity."
        )
    else:
        parts.append(
            "\n## Instructions\n"
            "Provide a thorough, well-researched answer to the question above. "
            "Structure your response clearly. Include specific facts, data points, "
            "and reasoning. If you are uncertain about something, say so explicitly "
            "rather than guessing."
        )
    full_prompt = "\n".join(parts)

    # Query all models concurrently
    model_overrides = model_overrides or {}
    results = []

    with ThreadPoolExecutor(max_workers=len(providers)) as pool:
        futures = {
            pool.submit(
                query_model,
                provider_key,
                full_prompt,
                model_overrides.get(provider_key),
                max_tokens,
                temperature,
            ): provider_key
            for provider_key in providers
        }
        for future in as_completed(futures):
            results.append(future.result())

    # Sort results by provider name for consistency
    results.sort(key=lambda r: r["provider"])

    successful = [r for r in results if r["status"] == "success"]

    return {
        "question": question,
        "context_provided": bool(context),
        "providers_queried": len(providers),
        "providers_succeeded": len(successful),
        "total_elapsed_seconds": round(max((r["elapsed_seconds"] for r in results), default=0), 2),
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Model Council: Query multiple LLMs and collect responses for synthesis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python council.py "What are the pros and cons of microservices?"
  python council.py --models openai,google "Explain quantum computing"
  python council.py --context "We're evaluating cloud providers" "Compare AWS vs GCP vs Azure"
  python council.py --list-providers
""",
    )
    parser.add_argument("question", nargs="?", help="The research question")
    parser.add_argument(
        "--models", "-m",
        help="Comma-separated list of providers to query (default: all with API keys set)",
    )
    parser.add_argument(
        "--context", "-c",
        help="Additional context to include with the question",
    )
    parser.add_argument(
        "--context-file",
        help="Read additional context from a file",
    )
    parser.add_argument(
        "--stdin", action="store_true",
        help="Read the question from stdin",
    )
    parser.add_argument(
        "--list-providers", "-l", action="store_true",
        help="List available providers and their API key status",
    )
    parser.add_argument(
        "--model-override",
        action="append",
        help="Override model for a provider: provider=model (e.g., openai=gpt-4-turbo)",
    )
    parser.add_argument(
        "--raw", action="store_true",
        help="Output raw JSON (default: formatted markdown)",
    )
    parser.add_argument(
        "--max-tokens", "-t",
        type=int,
        default=4096,
        help="Maximum tokens per response (default: 4096)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for response randomness, 0.0-1.5 (default: 0.7)",
    )
    parser.add_argument(
        "--deep-research", "-d",
        action="store_true",
        help="Enable deep research mode for more thorough, multi-perspective analysis",
    )

    args = parser.parse_args()

    # List providers mode
    if args.list_providers:
        print("\n## Available Providers\n")
        print(f"{'Provider':<12} {'Model':<25} {'API Key Env Var':<25} {'Status'}")
        print("-" * 80)
        for key, cfg in sorted(PROVIDERS.items()):
            has_key = "SET" if os.environ.get(cfg["env_key"]) else "NOT SET"
            status_marker = "+" if has_key == "SET" else "-"
            print(f"{key:<12} {cfg['name']:<25} {cfg['env_key']:<25} [{status_marker}] {has_key}")
        print(f"\nSet MODEL_COUNCIL_MODELS env var to configure defaults (e.g., 'openai,google,deepseek')")
        sys.exit(0)

    # Get the question
    question = args.question
    if args.stdin:
        question = sys.stdin.read().strip()
    if not question:
        parser.print_help()
        sys.exit(1)

    # Get context
    context = args.context
    if args.context_file:
        with open(args.context_file, "r") as f:
            file_context = f.read().strip()
        context = f"{context}\n\n{file_context}" if context else file_context

    # Parse providers
    providers = None
    if args.models:
        providers = [p.strip() for p in args.models.split(",")]
        invalid = [p for p in providers if p not in PROVIDERS]
        if invalid:
            print(f"Error: Unknown providers: {', '.join(invalid)}", file=sys.stderr)
            print(f"Valid providers: {', '.join(sorted(PROVIDERS.keys()))}", file=sys.stderr)
            sys.exit(1)

    # Parse model overrides
    model_overrides = {}
    if args.model_override:
        for override in args.model_override:
            if "=" not in override:
                print(f"Error: Invalid model override format: {override} (use provider=model)", file=sys.stderr)
                sys.exit(1)
            prov, model = override.split("=", 1)
            model_overrides[prov] = model

    # Run the council
    if args.deep_research:
        print(f"Querying models (deep research mode)...", file=sys.stderr)
    else:
        print(f"Querying models...", file=sys.stderr)
    result = query_council(question, context, providers, model_overrides, args.max_tokens, args.temperature, args.deep_research)

    if args.raw:
        print(json.dumps(result, indent=2))
    else:
        # Formatted output
        print(f"\n# Model Council Results\n")
        print(f"**Question:** {result['question']}\n")
        print(f"**Models queried:** {result['providers_queried']} | "
              f"**Succeeded:** {result['providers_succeeded']} | "
              f"**Wall time:** {result.get('total_elapsed_seconds', 'N/A')}s\n")

        if result.get("error"):
            print(f"\n**Error:** {result['error']}\n")

        print("---\n")

        for r in result["results"]:
            if r["status"] == "success":
                print(f"## {r['model_name']} ({r['provider']})")
                print(f"*Model: {r.get('model_id', 'N/A')} | Time: {r['elapsed_seconds']}s*\n")
                print(r["response"])
                print("\n---\n")
            elif r["status"] == "skipped":
                print(f"## {r['model_name']} ({r['provider']}) - SKIPPED")
                print(f"*{r['error']}*\n")
                print("---\n")
            else:
                print(f"## {r['model_name']} ({r['provider']}) - ERROR")
                print(f"*{r.get('error', 'Unknown error')}*\n")
                print("---\n")


if __name__ == "__main__":
    main()
