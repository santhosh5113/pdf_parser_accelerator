# Analyzer Switching Guide

This guide shows you how to easily switch between different PDF analyzers in the pipeline.

## Quick Switching Method

### 1. Change Default Analyzer (Recommended)

Edit `database/run_pipeline.py` and modify the `DEFAULT_ANALYZER` variable at the top of the `main()` function:

```python
# ===== QUICK SWITCHING: Change default analyzer here =====
# Uncomment the analyzer you want to use as default:
DEFAULT_ANALYZER = "openai_vlm"  # OpenAI VLM (requires API key)
# DEFAULT_ANALYZER = "ollama"     # Ollama (local, no API key needed)
# DEFAULT_ANALYZER = "clip"       # CLIP (local, no API key needed)
```

**To switch to Ollama:**
```python
# DEFAULT_ANALYZER = "openai_vlm"  # OpenAI VLM (requires API key)
DEFAULT_ANALYZER = "ollama"     # Ollama (local, no API key needed)
# DEFAULT_ANALYZER = "clip"       # CLIP (local, no API key needed)
```

**To switch to CLIP:**
```python
# DEFAULT_ANALYZER = "openai_vlm"  # OpenAI VLM (requires API key)
# DEFAULT_ANALYZER = "ollama"     # Ollama (local, no API key needed)
DEFAULT_ANALYZER = "clip"       # CLIP (local, no API key needed)
```

### 2. Command Line Override

You can also override the default analyzer using command line arguments:

```bash
# Use OpenAI VLM (default)
python -m database.run_pipeline input.pdf output.json

# Use Ollama
python -m database.run_pipeline input.pdf output.json --analyzer ollama

# Use CLIP
python -m database.run_pipeline input.pdf output.json --analyzer clip
```

## Analyzer Comparison

| Analyzer | Pros | Cons | Requirements |
|----------|------|------|--------------|
| **OpenAI VLM** | Most accurate, handles complex documents | Requires API key, costs money | `OPENAI_API_KEY` environment variable |
| **Ollama** | Free, local, no API key needed | Requires Ollama server running | Ollama server with appropriate model |
| **CLIP** | Free, local, fast | Less accurate for complex documents | CLIP model installed |

## Prerequisites for Each Analyzer

### OpenAI VLM
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### Ollama
```bash
# Install and start Ollama server
ollama serve

# Pull a model (in another terminal)
ollama pull llama2
```

### CLIP
```bash
# CLIP dependencies are included in pipeline_env
# No additional setup required
```

## Usage Examples

### Using OpenAI VLM (Default)
```bash
python -m database.run_pipeline \
  shared/input_pdfs/only_text.pdf \
  output.json \
  --openai-model gpt-4o
```

### Using Ollama
```bash
python -m database.run_pipeline \
  shared/input_pdfs/only_text.pdf \
  output.json \
  --analyzer ollama
```

### Using CLIP
```bash
python -m database.run_pipeline \
  shared/input_pdfs/only_text.pdf \
  output.json \
  --analyzer clip
```

## Troubleshooting

### OpenAI VLM Issues
- **"API key not set"**: Set `OPENAI_API_KEY` environment variable
- **"Rate limit exceeded"**: Wait a few minutes or use `gpt-4o-mini` model
- **"Invalid model"**: Check available models in OpenAI dashboard

### Ollama Issues
- **"Connection refused"**: Start Ollama server with `ollama serve`
- **"Model not found"**: Pull the model with `ollama pull <model_name>`

### CLIP Issues
- **"CUDA out of memory"**: Use `device="cpu"` in the code
- **"Model not found"**: CLIP models are downloaded automatically 