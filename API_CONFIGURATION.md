# API Provider Configuration Guide

This project now supports both Google Gemini and OpenAI as backend language model providers. You can switch between them by configuring environment variables.

## Configuration Options

### 1. API Provider Selection

Set the `API_PROVIDER` environment variable to choose your preferred provider:

```bash
# Use Google Gemini (default)
API_PROVIDER=gemini

# Use OpenAI
API_PROVIDER=openai
```

### 2. API Keys

Depending on your chosen provider, you'll need to set the corresponding API key:

#### For Gemini:
```bash
GEMINI_API_KEY=your-gemini-api-key-here
```
Get your API key from: https://ai.google.dev/

#### For OpenAI:
```bash
OPENAI_API_KEY=your-openai-api-key-here
```
Get your API key from: https://platform.openai.com/account/api-keys

### 3. Model Configuration (Optional)

If you don't specify models, the system will use sensible defaults based on your provider choice.

#### Default Models for Gemini:
- Query Generator: `gemini-2.0-flash-exp`
- Reflection: `gemini-2.0-flash-thinking-exp`
- Answer: `gemini-2.0-flash-thinking-exp`

#### Default Models for OpenAI:
- Query Generator: `gpt-3.5-turbo`
- Reflection: `gpt-4`
- Answer: `gpt-4`

#### Custom Model Configuration:
You can override these defaults by setting:
```bash
QUERY_GENERATOR_MODEL=your-preferred-model
REFLECTION_MODEL=your-preferred-model
ANSWER_MODEL=your-preferred-model
```

## Setup Instructions

### Option 1: Environment Variables
1. Copy `.env.example` to `.env`
2. Set your preferred `API_PROVIDER`
3. Set the corresponding API key
4. Optionally customize model names

### Option 2: Docker Compose
1. Edit `docker-compose.yml`
2. Update the `API_PROVIDER` environment variable
3. Uncomment and set the appropriate API key
4. Run with `docker-compose up`

## Search Functionality

- **Gemini**: Uses Google's native search API when available, falls back to DuckDuckGo
- **OpenAI**: Uses DuckDuckGo search (Google search not available with OpenAI)

## Dependencies

The system will automatically detect which dependencies are available:
- If using Gemini but `langchain-google-genai` is not installed, it will show an error
- If using OpenAI but `openai` is not installed, it will show an error

## Example Configurations

### Gemini Configuration (.env):
```bash
API_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
```

### OpenAI Configuration (.env):
```bash
API_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
```

### Mixed Configuration (Custom Models):
```bash
API_PROVIDER=openai
OPENAI_API_KEY=your-openai-key
QUERY_GENERATOR_MODEL=gpt-3.5-turbo
REFLECTION_MODEL=gpt-4o
ANSWER_MODEL=gpt-4o
```

## Migration from Gemini-only Version

If you're upgrading from the Gemini-only version:
1. Add `API_PROVIDER=gemini` to maintain current behavior
2. Your existing `GEMINI_API_KEY` will continue to work
3. No other changes needed

## Troubleshooting

1. **"API key not set" error**: Make sure you've set the correct API key for your chosen provider
2. **"Provider not supported" error**: Check that `API_PROVIDER` is set to either "gemini" or "openai"
3. **Import errors**: Install the required packages with `pip install -r requirements.txt`
