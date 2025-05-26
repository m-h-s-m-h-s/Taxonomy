# Taxonomy Navigator - API Documentation

A comprehensive AI-powered product categorization system that uses OpenAI's GPT models to automatically classify products into appropriate taxonomy categories.

## Overview

The Taxonomy Navigator implements a sophisticated five-stage AI classification system that efficiently processes products through large taxonomy structures. Unlike traditional hierarchical navigation, this system uses progressive filtering combined with AI refinement and validation to achieve maximum efficiency and accuracy.

## Key Features

- **Five-Stage AI Classification**: Uses gpt-4.1-nano and gpt-4.1-mini with progressive filtering and validation
- **Leaf Node Matching**: Efficiently identifies the most relevant end categories first
- **Layer Filtering**: Focuses on the most popular top-level taxonomy category
- **Refined Selection**: AI narrows down to top 10 candidates from filtered L1 taxonomy results
- **Validation**: Ensures AI didn't hallucinate any category names that don't exist
- **Enhanced Product Identification**: Advanced prompting to distinguish products from accessories
- **Deterministic Results**: Uses temperature=0 and top_p=0 for consistent classifications
- **Comprehensive Error Handling**: Graceful handling of API errors and edge cases
- **Simplified Interface Options**: Two focused scripts for all use cases
- **Secure API Key Management**: Multiple secure methods for API key configuration
- **Detailed Result Storage**: JSON output with complete classification metadata
- **Scalable Architecture**: Handles taxonomies with thousands of categories

## Requirements

- Python 3.7+
- OpenAI Python library (`openai>=1.0.0`)
- Valid OpenAI API key with sufficient quota

## Installation

1. Clone or download the project to your local machine
2. Navigate to the project directory
3. Install the required Python package:

```bash
pip install openai>=1.0.0
```

## 🔑 API Key Configuration (REQUIRED)

**IMPORTANT**: You must configure your OpenAI API key before using the system. The system checks for your API key in the following order:

### Method 1: API Key File (Recommended for Development)

Create or edit the API key file:

```bash
# Create the API key file with your actual key
echo "sk-your-actual-openai-api-key-here" > data/api_key.txt
```

### Method 2: Environment Variable (Recommended for Production)

Set the environment variable:

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-your-actual-openai-api-key-here"

# Windows Command Prompt
set OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
```

### Method 3: Command Line Argument

Pass the API key directly when running commands:

```bash
./scripts/classify_single_product.sh --api-key "sk-your-actual-openai-api-key-here" ...
```

### Security Best Practices

- **Never commit API keys to version control**
- The `data/api_key.txt` file is automatically ignored by git
- Use environment variables in production environments
- Regularly rotate your API keys
- Monitor your OpenAI usage and billing

## System Architecture

### Five-Stage Classification Process

The Taxonomy Navigator uses a sophisticated five-stage approach:

#### Stage 1: Initial Leaf Node Matching (gpt-4.1-nano)
1. Identifies all leaf nodes (end categories) in the taxonomy
2. Sends product information + all leaf nodes to OpenAI
3. Uses enhanced prompting to focus on the core product being sold
4. Returns the top 20 most relevant leaf nodes from all categories

#### Stage 2: Layer Filtering (algorithmic)
1. Analyzes the selected leaf nodes to identify the most popular 1st taxonomy layer
2. Counts occurrences of each top-level category (e.g., "Electronics", "Apparel")
3. Filters the 20 selected leaves to only those from the dominant top-level category
4. Ensures classification consistency within the same product domain

#### Stage 3: Refined Selection (gpt-4.1-nano)
1. Takes the filtered candidates from Stage 2 (all from same L1 taxonomy layer)
2. Uses AI to refine selection to the top 10 most relevant categories
3. Applies enhanced prompting focused on core product identification
4. This is essentially Stage 1 repeated, but only with leaves from the dominant L1 taxonomy layer

#### Stage 4: Validation (algorithmic)
1. Validates that all AI-selected category names actually exist in the taxonomy
2. Removes any hallucinated or invalid category names
3. Ensures data integrity before final selection
4. Logs validation statistics (valid vs invalid categories)

#### Stage 5: Final Selection (gpt-4.1-mini)
1. Takes the validated candidates from Stage 4
2. Uses structured prompting to identify the exact product type
3. Distinguishes between main products and accessories
4. Selects the single best match from validated candidates using enhanced model

### Enhanced Prompting Strategy

The system uses carefully crafted prompts that:
- Instruct the AI to identify the "core product being sold"
- Distinguish between main products and accessories
- Ignore marketing language and focus on product fundamentals
- Provide structured decision-making steps at each stage

## Usage Modes

### 1. Single Product Classification

Classify individual products with detailed analysis:

#### Command-Line Mode
```bash
./scripts/classify_single_product.sh \
  --product-name "iPhone 14 Pro" \
  --product-description "Smartphone with advanced camera system"
```

#### Interactive Mode
```bash
./scripts/classify_single_product.sh --interactive
```

**Options:**
- `--product-name NAME`: Product name to classify (required for CLI mode)
- `--product-description DESC`: Detailed product description (required for CLI mode)
- `--interactive`: Launch interactive interface for multiple products
- `--save-results`: Save session results to JSON file (interactive mode)
- `--taxonomy-file FILE`: Path to taxonomy file (default: ../data/taxonomy.en-US.txt)
- `--model MODEL`: OpenAI model for Stages 1&3 (default: gpt-4.1-nano)
- `--output-file FILE`: Output JSON file for results
- `--verbose`: Enable detailed logging

**Examples:**
```bash
# Single product with detailed results
./scripts/classify_single_product.sh \
  -n "Xbox Controller" \
  -d "Wireless gaming controller with Bluetooth"

# Interactive mode with result saving
./scripts/classify_single_product.sh --interactive --save-results --verbose
```

### 2. Batch Product Testing

Process multiple products with simple, clean output:

```bash
./scripts/analyze_batch_products.sh [options]
```

**Options:**
- `--products-file FILE`: Products file to test (default: ../tests/sample_products.txt)
- `--taxonomy-file FILE`: Taxonomy file path (default: ../data/taxonomy.en-US.txt)
- `--model MODEL`: OpenAI model for classification (default: gpt-4.1-nano)
- `--verbose`: Enable verbose logging

**Examples:**
```bash
# Simple batch testing with default products
./scripts/analyze_batch_products.sh

# Custom products file with verbose logging
./scripts/analyze_batch_products.sh --products my_products.txt --verbose
```

## Input Formats

### Product Information

Products should be described with both name and description:

**Format**: `"Product Name: Detailed description"`

**Examples:**
- `"iPhone 14 Pro: Smartphone with 6.1-inch display and A16 chip"`
- `"Xbox Wireless Controller: Gaming controller with Bluetooth connectivity"`
- `"Nike Air Max 270: Running shoes with air cushioning technology"`

### Products File Format

For batch processing, create a text file with one product per line:

```
iPhone 14 Pro: Smartphone with advanced camera system
Xbox Wireless Controller: Gaming controller with Bluetooth
Nike Air Max 270: Running shoes with air cushioning
Samsung 4K TV: 55-inch Ultra HD Smart television
```

### Taxonomy File Format

The system supports Google Product Taxonomy format:
- First line: Header (ignored)
- Subsequent lines: Category paths separated by " > "
- Example: `"Electronics > Computers > Laptops"`

## Output Formats

### Console Output

#### Single Product (Detailed)
```
[iPhone 14 Pro: Smartphone with advanced camera system]
Smartphones
--------------------------------------------------
```

#### Batch Testing (Simple)
```
[iPhone 14 Pro: Smartphone with advanced camera system]
Smartphones
--------------------------------------------------
[Xbox Wireless Controller: Gaming controller with Bluetooth]
Game Controllers
--------------------------------------------------
```

### JSON Output (Single Product Mode)

Detailed results with metadata:

```json
[
  {
    "product_info": "iPhone 14 Pro: Smartphone with advanced camera system",
    "best_match_index": 0,
    "matches": [
      {
        "category_path": ["Electronics", "Cell Phones & Accessories", "Cell Phones", "Smartphones"],
        "full_path": "Electronics > Cell Phones & Accessories > Cell Phones > Smartphones",
        "leaf_category": "Smartphones",
        "is_best_match": true
      }
    ]
  }
]
```

### Failed Classification

When no suitable category is found:
```
[Unknown Product: Not in any category]
False
--------------------------------------------------
```

## Performance Considerations

- **Processing Speed**: ~4-5 seconds per product (including five stages with three API calls)
- **API Usage**: Three API calls per product (Stages 1, 3, and 5)
- **Cost Optimization**: Uses gpt-4.1-nano for initial stages, gpt-4.1-mini for final precision
- **Deterministic Results**: temperature=0 and top_p=0 for consistency
- **Data Integrity**: Stage 4 validation prevents AI hallucinations

## Error Handling

The system handles various error conditions:

- **API Key Missing**: Clear error messages with setup instructions
- **API Failures**: Graceful degradation with fallback responses
- **File Not Found**: Helpful error messages with file location guidance
- **Invalid Taxonomy**: Validation and error reporting
- **Network Issues**: Retry logic and timeout handling
- **AI Hallucinations**: Stage 4 validation removes invalid category names

## Troubleshooting

### API Key Issues

**Error**: "OpenAI API key not provided"

**Solutions**:
1. Create the API key file: `echo "sk-your-key" > data/api_key.txt`
2. Check the file contains only your API key (no extra spaces)
3. Try using environment variable method
4. Verify your API key is valid and has quota

### File Path Issues

**Error**: "Taxonomy file not found"

**Solutions**:
1. Run scripts from the project root directory
2. Verify taxonomy file exists at `data/taxonomy.en-US.txt`
3. Check file permissions
4. Use absolute paths if needed

### Model Issues

**Error**: "The model does not exist"

**Solutions**:
1. Use a different model: `--model gpt-4o`
2. Check your OpenAI account has access to the model
3. Verify model name spelling

## Advanced Configuration

### Custom Models

Specify different OpenAI models:

```bash
./scripts/classify_single_product.sh --model "gpt-4o" ...
```

### Custom Taxonomy Files

Use your own taxonomy:

```bash
./scripts/classify_single_product.sh --taxonomy-file "custom_taxonomy.txt" ...
```

### Verbose Logging

Enable detailed logging for debugging:

```bash
./scripts/classify_single_product.sh --verbose ...
```

## Project Structure

```
Taxonomy/
├── src/                              # Core classification logic
│   ├── taxonomy_navigator_engine.py  # Main classification engine (5-stage)
│   ├── interactive_interface.py      # Interactive interface
│   └── config.py                     # Configuration management
├── scripts/                          # Command-line tools
│   ├── README.md                     # Scripts documentation
│   ├── classify_single_product.sh    # Single product classification
│   └── analyze_batch_products.sh     # Batch product testing
├── tests/                            # Testing utilities
│   ├── simple_batch_tester.py        # Simple batch testing tool
│   ├── unit_tests.py                 # Unit tests
│   └── sample_products.txt           # Sample products for testing
├── data/                             # Configuration and taxonomy files
│   ├── api_key.txt                   # Your API key (create this)
│   └── taxonomy.en-US.txt            # Taxonomy file
├── docs/                             # Documentation
│   ├── README.md                     # This file
│   ├── USAGE.md                      # Usage examples
│   └── ARCHITECTURE.md               # Technical architecture
└── results/                          # Output files
    └── taxonomy_results.json         # Classification results
```

## Use Case Guide

| **What you want to do** | **Use this script** | **Mode/Options** |
|--------------------------|---------------------|------------------|
| Classify one product with details | `classify_single_product.sh` | Command-line mode |
| Test multiple products interactively | `classify_single_product.sh` | `--interactive` |
| Quick batch validation | `analyze_batch_products.sh` | Default |
| Get clean output for demo | `analyze_batch_products.sh` | Default |
| Debug classification issues | `classify_single_product.sh` | `--verbose` |
| Save detailed results | `classify_single_product.sh` | `--interactive --save-results` |
| Performance benchmarking | `classify_single_product.sh` | `--interactive` mode |

## Security Considerations

1. **API Key Protection**:
   - Never commit API keys to version control
   - Use environment variables in production
   - Regularly rotate API keys
   - Monitor usage and billing

2. **Input Validation**:
   - Validates all file paths and inputs
   - Sanitizes user input
   - Handles malformed data gracefully

3. **Error Information**:
   - Logs errors without exposing sensitive data
   - Provides helpful error messages
   - Maintains audit trails

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check this documentation
2. Run commands with `--help` for usage information
3. Use `--verbose` for detailed logging
4. Review the troubleshooting section above 