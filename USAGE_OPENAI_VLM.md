# OpenAI VLM Integration Usage Guide

The PDF parser pipeline now uses OpenAI's Vision Language Model (GPT-4V) as the default analyzer for classifying PDF documents.

## Prerequisites

1. **OpenAI API Key**: Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

2. **Dependencies**: The required packages are included in the `pipeline_env` environment:
   - `openai>=1.0.0`
   - `PyMuPDF>=1.23.0` (already included)
   - `Pillow>=10.0.0` (already included)

## Usage

### Basic Usage (OpenAI VLM as default)
```bash
python -m database.run_pipeline input.pdf output.json
```

### Specify OpenAI Model
```bash
python -m database.run_pipeline input.pdf output.json --openai-model gpt-4o
```

### Available OpenAI Models
- `gpt-4o` (default) - Latest and most capable model
- `gpt-4o-mini` - Faster and more cost-effective
- `gpt-4-vision-preview` - Legacy vision model

### Complete Example
```bash
python -m database.run_pipeline \
  shared/input_pdfs/only_text.pdf \
  output.json \
  --vector-store faiss \
  --chunk-size 512 \
  --chunk-overlap 64 \
  --openai-model gpt-4o
```

## Classification Categories

The OpenAI VLM analyzer classifies PDFs into these categories:

1. **NATIVE TEXT** - Digital PDF with mostly text paragraphs
2. **NATIVE TABLE** - Digital PDF with tables as main content
3. **NATIVE MATH HEAVY** - Digital PDF with many mathematical equations
4. **SCANNED TEXT** - Scanned image of text document
5. **SCANNED TABLE** - Scanned image where tables are the main content
6. **SCANNED MATH HEAVY** - Scanned image with significant mathematical content

## Priority Rules

The analyzer applies these priority rules for multi-page documents:
- If ANY page contains math-heavy content → Overall: MATH HEAVY
- If ANY page contains tables (and no math-heavy) → Overall: TABLE
- MATH HEAVY has higher priority than TABLE
- Only classify as TEXT if no pages contain tables or math-heavy content

## Fallback Options

If you need to use other analyzers, you can still specify them:

```bash
# Use Ollama analyzer
python -m database.run_pipeline input.pdf output.json --analyzer ollama

# Use CLIP analyzer
python -m database.run_pipeline input.pdf output.json --analyzer clip
```

## Error Handling

The pipeline will:
- Check for OpenAI API key availability
- Handle API rate limits with automatic delays
- Provide detailed error messages for debugging
- Clean up temporary files automatically

## Cost Considerations

- GPT-4o is more expensive but more accurate
- GPT-4o-mini is more cost-effective for bulk processing
- Each page requires one API call
- Consider using `--openai-model gpt-4o-mini` for large documents 