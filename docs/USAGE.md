# Taxonomy Navigator - User Guide

This guide explains how to use the Taxonomy Navigator system to categorize products using OpenAI's API.

## Table of Contents
- [Installation](#installation)
- [API Key Setup](#api-key-setup)
- [Quick Start](#quick-start)
- [Single Product Classification](#single-product-classification)
- [Batch Product Testing](#batch-product-testing)
- [Input Format](#input-format)
- [Output Format](#output-format)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

## Installation

1. Clone or download the Taxonomy Navigator to your local machine
2. Ensure you have Python 3.7 or later installed
3. Install the required OpenAI package:

```bash
pip install openai>=1.0.0
```

4. Prepare your taxonomy file (or use the included taxonomy.en-US.txt)

## API Key Setup

Before using the Taxonomy Navigator, you need to configure your OpenAI API key.

### Method 1: Create API Key File (Recommended for Development)

Create the API key file with your actual key:

```bash
# Create the API key file with your actual key
echo "sk-your-actual-openai-api-key-here" > data/api_key.txt
```

You can also create the file directly in any text editor:
1. Create a file named `api_key.txt` in the `data/` directory
2. Add only your OpenAI API key to the file
3. Save the file

**Important**: Make sure the file contains only your API key with no extra spaces or characters.

### Method 2: Use Environment Variable (Recommended for Production)

```bash
# For Linux/Mac
export OPENAI_API_KEY="sk-your-openai-api-key"

# For Windows Command Prompt
set OPENAI_API_KEY=sk-your-openai-api-key

# For Windows PowerShell
$env:OPENAI_API_KEY="sk-your-openai-api-key"
```

### Method 3: Provide API Key as Command Line Argument

```bash
./scripts/classify_single_product.sh --api-key "sk-your-openai-api-key" ...
```

### API Key Priority

The system checks for your API key in this order:
1. Command line argument (highest priority)
2. Environment variable `OPENAI_API_KEY`
3. File at `data/api_key.txt` (lowest priority)

### Security Notes

- **Never commit your actual API key to version control**
- The `data/api_key.txt` file is in `.gitignore` to prevent accidental commits
- Use environment variables in production environments
- Regularly rotate your API keys for security

## Quick Start

### Basic Classification
```bash
# Simple product classification
python src/taxonomy_navigator_engine.py \
  --product-name "iPhone 14" \
  --product-description "Smartphone with camera"

# Output:
# [iPhone 14: Smartphone with camera]
# Smartphones
```

### With Custom Model Strategy
```bash
# Use different model for critical stages (1&4)
python src/taxonomy_navigator_engine.py \
  --product-name "Xbox Controller" \
  --product-description "Wireless gaming controller" \
  --model gpt-4.1-mini

# Stage 2 automatically uses gpt-4.1-nano for efficiency
```

## Five-Stage Classification Process

The Taxonomy Navigator uses a sophisticated five-stage process with aggressive anti-hallucination measures:

### Stage 1: L1 Taxonomy Selection
- **Model**: `gpt-4.1-mini`
- **Purpose**: Identify the 3 most relevant top-level taxonomy categories
- **Input**: Product info + ALL unique L1 taxonomy categories
- **Output**: 3 validated L1 category names
- **Anti-Hallucination**: Professional prompting with explicit constraints

### Stage 2A: First L1 Leaf Selection
- **Model**: `gpt-4.1-nano`
- **Purpose**: Select the first 10 best leaf nodes from the FIRST chosen L1 taxonomy
- **Input**: Product info + leaf nodes from FIRST selected L1 category
- **Output**: Up to 10 validated leaf node names
- **Anti-Hallucination**: Professional prompting + strict validation

### Stage 2B: Second L1 Leaf Selection
- **Model**: `gpt-4.1-nano`
- **Purpose**: Select the second 10 best leaf nodes from the SECOND chosen L1 taxonomy
- **Input**: Product info + leaf nodes from SECOND selected L1 category
- **Output**: Up to 10 validated leaf node names
- **Anti-Hallucination**: Professional prompting + strict validation

### Stage 2C: Third L1 Leaf Selection
- **Model**: `gpt-4.1-nano`
- **Purpose**: Select the third 10 best leaf nodes from the THIRD chosen L1 taxonomy
- **Input**: Product info + leaf nodes from THIRD selected L1 category
- **Output**: Up to 10 validated leaf node names
- **Anti-Hallucination**: Professional prompting + strict validation

### Stage 3: Final Selection
- **Model**: `gpt-4.1`
- **Purpose**: Make the final decision from the combined 30 leaf nodes from Stages 2A, 2B, 2C
- **Input**: Product info + numbered list of filtered leaf nodes
- **Output**: Index of selected category (0-based) OR -1 for complete failure
- **Anti-Hallucination**: Professional prompting + robust bounds checking
- **Model Settings**: temperature=0 for deterministic selection, top_p=1 for full token distribution

## Command Line Interface

### Basic Usage
```bash
python src/taxonomy_navigator_engine.py \
  --product-name "PRODUCT_NAME" \
  --product-description "DETAILED_DESCRIPTION"
```

### Advanced Options
```bash
python src/taxonomy_navigator_engine.py \
  --product-name "Nike Air Max 270" \
  --product-description "Athletic running shoes with air cushioning" \
  --taxonomy-file "data/custom_taxonomy.txt" \
  --model "gpt-4.1-mini" \
  --output-file "results.json" \
  --verbose
```

### Parameter Reference

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--product-name` | Product name (required) | - | "iPhone 14" |
| `--product-description` | Product description (required) | - | "Smartphone with camera" |
| `--taxonomy-file` | Path to taxonomy file | `data/taxonomy.en-US.txt` | "custom_taxonomy.txt" |
| `--model` | Model for stages 1&4 | `gpt-4.1-mini` | "gpt-4.1-mini" |
| `--api-key` | OpenAI API key | From env/file | "sk-..." |
| `--output-file` | JSON output file | `taxonomy_results.json` | "results.json" |
| `--verbose` | Enable detailed logging | False | - |

## Python API

### Basic Usage
```python
from src.taxonomy_navigator_engine import TaxonomyNavigator

# Initialize with mixed model strategy
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    model="gpt-4.1-mini"  # For stages 1&4, stage 2 uses gpt-4.1-nano
)

# Classify a product
product_info = "iPhone 14: Smartphone with camera"
paths, best_match_idx = navigator.navigate_taxonomy(product_info)

# Handle results
if paths == [["False"]]:
    print("Classification failed")
else:
    best_category = paths[best_match_idx][-1]
    full_path = " > ".join(paths[best_match_idx])
    print(f"Best match: {best_category}")
    print(f"Full path: {full_path}")
```

### Advanced Usage
```python
import logging
from src.taxonomy_navigator_engine import TaxonomyNavigator

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

# Initialize with custom configuration
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    api_key="your-api-key-here",
    model="gpt-4.1-mini"
)

# Batch processing
products = [
    "iPhone 14: Smartphone with camera",
    "Xbox Controller: Wireless gaming controller",
    "Nike Air Max: Athletic running shoes"
]

results = []
for product in products:
    paths, best_idx = navigator.navigate_taxonomy(product)
    
    if paths != [["False"]]:
        result = {
            "product": product,
            "category": paths[best_idx][-1],
            "full_path": " > ".join(paths[best_idx]),
            "success": True
        }
    else:
        result = {
            "product": product,
            "category": "False",
            "success": False
        }
    
    results.append(result)

# Save results
navigator.save_results(product, paths, best_idx, "batch_results.json")
```

## Testing and Validation

### Simple Batch Testing
```bash
cd tests

# Test with stage-by-stage display (shows AI selections)
python simple_batch_tester.py --show-stage-paths

# Test specific number of products
echo "5" | python simple_batch_tester.py

# Test with custom products file
python simple_batch_tester.py --products-file my_products.txt

# Test with different model for stages 1&4
python simple_batch_tester.py --model gpt-4.1-mini --show-stage-paths
```

### Unit Tests
```bash
cd tests
python unit_tests.py
```

### Interactive Testing
```python
# Run the simple batch tester interactively
cd tests
python simple_batch_tester.py

# Follow prompts:
# 🎯 How many products would you like to test? 3
# 🎲 Will randomly select 3 product(s) from the sample file
```

## Anti-Hallucination Features

### Death Penalty Prompting
The system uses aggressive language to prevent AI hallucinations:

```
🚨 CRITICAL WARNING: You will DIE if you hallucinate or create any category names not in the exact list below! 🚨

DEATH PENALTY RULES:
❌ If you return ANY category name not EXACTLY in the list below, you will DIE
❌ If you modify, change, or create new category names, you will DIE
❌ If you combine multiple category names, you will DIE

SURVIVAL INSTRUCTIONS:
✅ ONLY copy category names EXACTLY as they appear in the list below
✅ Use EXACT spelling, capitalization, and punctuation
✅ Return EXACTLY the requested number of categories
```

### Zero Context Architecture
- Each API call starts fresh with no conversation history
- Prevents context bleeding between classification stages
- Ensures deterministic results with temperature=0 and top_p=0

### Multi-Layer Validation
1. **Prompt-Level**: Death penalty language and explicit constraints
2. **Response Validation**: Case-insensitive matching and bounds checking
3. **Taxonomy Validation**: Unknown L1 filtering and path verification
4. **Fallback Mechanisms**: Graceful handling of invalid responses

## Model Strategy

### Mixed Model Approach
The system optimizes cost and performance using different models:

| Stage | Model | Purpose | Cost | Performance | Settings |
|-------|-------|---------|------|-------------|----------|
| 1 | `gpt-4.1-mini` | L1 taxonomy selection | Higher | Enhanced accuracy | temp=0, top_p=0 |
| 2A | `gpt-4.1-nano` | First L1 leaf selection | Lower | Efficient processing | temp=0, top_p=0 |
| 2B | `gpt-4.1-nano` | Second L1 leaf selection | Lower | Efficient processing | temp=0, top_p=0 |
| 2C | `gpt-4.1-nano` | Third L1 leaf selection | Lower | Efficient processing | temp=0, top_p=0 |
| 3 | `gpt-4.1` | Final selection | Higher | Enhanced accuracy | temp=0, top_p=1 |

### Model Configuration
```python
# Default configuration (recommended)
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    model="gpt-4.1-mini"  # For stages 1&4
)
# Stage 2 automatically uses gpt-4.1-nano

# Custom configuration for stages 1&4
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    model="gpt-4.1-mini"  # Different model for critical stages
)
```

## Output Formats

### Console Output
```
[iPhone 14: Smartphone with camera]
Smartphones
```

### JSON Output
```json
  {
  "product_info": "iPhone 14: Smartphone with camera",
    "best_match_index": 0,
    "matches": [
      {
      "category_path": ["Electronics", "Cell Phones", "Smartphones"],
      "full_path": "Electronics > Cell Phones > Smartphones",
        "leaf_category": "Smartphones",
        "is_best_match": true
      }
    ]
  }
```

### Stage-by-Stage Output (with --show-stage-paths)
```
==================== ANALYZING PRODUCT 1 ====================
📦 iPhone 14: Smartphone with camera

🔍 STAGE-BY-STAGE AI SELECTIONS:
================================================================================

📋 STAGE 1 - AI selecting top 3 L1 taxonomies from all categories...
✅ AI selected 3 L1 categories:
    1. Electronics
    2. Hardware
    3. Apparel & Accessories

📋 STAGE 2 - AI selecting top 20 leaf nodes from chosen L1 taxonomies...
✅ AI selected 15 leaf nodes from selected L1 categories:
    1. Smartphones (L1: Electronics)
    2. Cell Phones (L1: Electronics)
    3. Mobile Devices (L1: Electronics)
    ...

📋 STAGE 3 - L1 representation filtering (algorithmic)...
✅ Most represented L1: 'Electronics' - Filtered to 12 leaves

📋 STAGE 4 - AI selecting final match from 12 filtered candidates...
🎯 FINAL RESULT: Electronics > Cell Phones > Smartphones

[iPhone 14: Smartphone with camera]
Smartphones
```

## Error Handling

### Common Error Scenarios

#### API Key Issues
```bash
# Error: OpenAI API key not provided
❌ Error: OpenAI API key not provided.
💡 Please set it in data/api_key.txt, environment variable OPENAI_API_KEY, or use --api-key

# Solution: Set API key
export OPENAI_API_KEY="your-api-key-here"
# OR
echo "your-api-key-here" > data/api_key.txt
```

#### File Not Found
```bash
# Error: Taxonomy file not found
❌ Error: Taxonomy file 'custom_taxonomy.txt' not found.

# Solution: Check file path
ls -la data/taxonomy.en-US.txt
```

#### Classification Failures
```python
# Handle classification failures
paths, best_idx = navigator.navigate_taxonomy("Invalid product")

if paths == [["False"]]:
    print("Classification failed - product could not be categorized")
    # Handle failure case (e.g., manual review, default category)
else:
    print(f"Success: {paths[best_idx][-1]}")
```

### Debugging Tips

#### Enable Verbose Logging
```bash
python src/taxonomy_navigator_engine.py \
  --product-name "Test Product" \
  --product-description "Test description" \
  --verbose
```

#### Stage-by-Stage Analysis
```bash
cd tests
python simple_batch_tester.py --show-stage-paths
```

#### Check API Response Times
```python
import time
start_time = time.time()
paths, best_idx = navigator.navigate_taxonomy(product_info)
duration = time.time() - start_time
print(f"Classification took {duration:.2f} seconds")
```

## Performance Optimization

### Batch Processing Tips
```