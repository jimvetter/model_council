#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if required API keys are set
if [ -z "$OPENAI_API_KEY" ] || [ -z "$GOOGLE_API_KEY" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: Required API keys not set. Please create a .env file with:"
    echo "OPENAI_API_KEY=your_key_here"
    echo "GOOGLE_API_KEY=your_key_here"
    echo "ANTHROPIC_API_KEY=your_key_here"
    exit 1
fi

python3 ~/.claude/skills/model-council/scripts/council.py "$@"
