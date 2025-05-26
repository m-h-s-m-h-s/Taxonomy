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

The Taxonomy Navigator has two main scripts:

### For Single Products (with detailed analysis):
```bash
./scripts/classify_single_product.sh -n "iPhone 14" -d "Smartphone with camera"
```

### For Batch Testing (simple, clean output):
```bash
./scripts/analyze_batch_products.sh
```

## How It Works

### Five-Stage AI Classification Process

The system uses a sophisticated five-stage approach for maximum efficiency and accuracy:

1. **Initial Leaf Node Matching** (gpt-4.1-nano):
   - Identifies the top 20 most relevant leaf nodes from all categories in the taxonomy
   - Uses enhanced prompting to focus on the core product being sold
   - Efficiently selects specific end categories from thousands of options

2. **Layer Filtering** (algorithmic):
   - Analyzes the selected leaf nodes to identify the most popular 1st taxonomy layer
   - Filters the 20 selected leaves to only those from the dominant top-level category
   - Ensures classification consistency within the same product domain

3. **Refined Selection** (gpt-4.1-nano):
   - Takes the filtered candidates and refines selection to top 10 most relevant categories
   - This is essentially Stage 1 repeated, but only with leaves from the dominant L1 taxonomy layer
   - Uses AI to provide better focus for the validation and final selection stages
   - Applies enhanced prompting focused on core product identification

4. **Validation** (algorithmic):
   - Validates that all AI-selected category names actually exist in the taxonomy
   - Removes any hallucinated or invalid category names
   - Ensures data integrity before final selection
   - Logs validation statistics (valid vs invalid categories)

5. **Final Selection** (gpt-4.1-nano):
   - Uses sophisticated prompting to identify the exact product type
   - AI selects the single best match from the validated candidates
   - Enhanced model provides better precision for final decision
   - Returns the full taxonomy path to that category

## Single Product Classification

Use this script when you need detailed analysis of individual products.

### Command-Line Mode

Classify a single product with detailed results:

```bash
./scripts/classify_single_product.sh \
  --product-name "iPhone 14 Pro" \
  --product-description "Smartphone with advanced camera system"
```

**Required Arguments:**
- `--product-name NAME` or `-n NAME`: Product name to classify
- `--product-description DESC` or `-d DESC`: Detailed product description

**Optional Arguments:**
- `--taxonomy-file FILE` or `-t FILE`: Path to taxonomy file (default: ../data/taxonomy.en-US.txt)
- `--model MODEL` or `-m MODEL`: OpenAI model for all stages (default: gpt-4.1-nano)
- `--output-file FILE` or `-o FILE`: Output JSON file for results (default: ../results/taxonomy_results.json)
- `--verbose` or `-v`: Enable detailed logging
- `--help` or `-h`: Show help message

### Interactive Mode

Launch an interactive interface for testing multiple products in a session:

```bash
./scripts/classify_single_product.sh --interactive
```

**Interactive Mode Options:**
- `--interactive` or `-i`: Launch interactive interface
- `--save-results` or `-s`: Save session results to JSON file
- `--verbose` or `-v`: Enable detailed logging

**Example Interactive Session:**
```
🔍 TAXONOMY NAVIGATOR - INTERACTIVE INTERFACE
======================================================================

Welcome to the AI-powered product classification system!

🔍 Enter product info (or 'help' for commands): iPhone 14 Pro: Smartphone with camera

🔍 Classifying: iPhone 14 Pro: Smartphone with camera
⏳ Processing... (this may take a few seconds)

[iPhone 14 Pro: Smartphone with camera]
Smartphones
--------------------------------------------------

🔍 Enter product info (or 'help' for commands): help
🔍 Enter product info (or 'help' for commands): quit

👋 Thank you for using Taxonomy Navigator!
```

## Batch Product Testing

Use this script for simple batch testing with clean output.

### Basic Usage

Test with default sample products:

```bash
./scripts/analyze_batch_products.sh
```

### Custom Products File

Test with your own products file:

```bash
./scripts/analyze_batch_products.sh --products my_products.txt
```

**Options:**
- `--products FILE` or `-p FILE`: Products file to test (default: ../tests/sample_products.txt)
- `--taxonomy-file FILE` or `-t FILE`: Taxonomy file path (default: ../data/taxonomy.en-US.txt)
- `--model MODEL` or `-m MODEL`: OpenAI model for all stages (default: gpt-4.1-nano)
- `--verbose` or `-v`: Enable verbose logging
- `--help` or `-h`: Show help message

## Input Format

### Product Information

When using command-line mode, provide both name and description:

```bash
--product-name "Apple iPhone 12 Pro Max" \
--product-description "6.7-inch Super Retina XDR display, 5G capability, and pro camera system"
```

When using interactive mode, you can enter combined information:

```
iPhone 14 Pro: Smartphone with advanced camera system
```

### Products File Format (for Batch Testing)

Create a text file with one product per line:

```
iPhone 14 Pro: Smartphone with advanced camera system
Xbox Wireless Controller: Gaming controller with Bluetooth
Nike Air Max 270: Running shoes with air cushioning
Samsung 4K TV: 55-inch Ultra HD Smart television
MacBook Pro: Laptop computer for professional use
```

### Taxonomy File Format

The taxonomy file should follow the Google Product Taxonomy format:
- Each line represents a path in the taxonomy
- Categories are separated by " > "
- The first line is treated as a header (ignored)

Example:
```
# Taxonomy Version 1.0
Electronics
Electronics > Computers
Electronics > Computers > Laptops
Electronics > Computers > Desktops
Electronics > Cell Phones & Accessories
Electronics > Cell Phones & Accessories > Cell Phones
Electronics > Cell Phones & Accessories > Cell Phones > Smartphones
```

## Output Format

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
[Nike Air Max 270: Running shoes with air cushioning]
Athletic Shoes
--------------------------------------------------
```

### JSON Output (Single Product Mode)

Results are saved to a JSON file with detailed metadata:

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

## Examples

### Example 1: Electronics Product

```bash
./scripts/classify_single_product.sh \
  -n "Samsung 4K Smart TV" \
  -d "55-inch Ultra HD LED television with smart features"
```

### Example 2: Clothing Item

```bash
./scripts/classify_single_product.sh \
  -n "Men's Cotton T-Shirt" \
  -d "Casual short-sleeve crew neck t-shirt in navy blue"
```

### Example 3: Interactive Session with Multiple Products

```bash
./scripts/classify_single_product.sh --interactive --save-results
```

### Example 4: Batch Testing Custom Products

```bash
./scripts/analyze_batch_products.sh --products my_products.txt --verbose
```

### Example 5: Using Different AI Model

```bash
./scripts/classify_single_product.sh \
  -n "Gaming Laptop" \
  -d "High-performance laptop for gaming" \
  --model gpt-4o
```

## Troubleshooting

### API Key Issues

**Problem**: "Error: OpenAI API key not provided."

**Solutions**: 
- Create the API key file: `echo "sk-your-key" > data/api_key.txt`
- Verify that the API key is valid and has not expired
- Try using the environment variable method instead
- Check that the file contains only your API key with no extra spaces

### Model Issues

**Problem**: "Error querying OpenAI: The model `gpt-4.1-nano` does not exist"

**Solutions**: 
- Specify a different model: `--model gpt-4o`
- Check your OpenAI account has access to the model
- Verify model name spelling

### File Path Issues

**Problem**: "Taxonomy file not found"

**Solutions**: 
- Run scripts from the project root directory
- Verify taxonomy file exists at `data/taxonomy.en-US.txt`
- Check file permissions
- Use absolute paths if needed

### "False" Results

**Problem**: Getting "False" for products that should match

**Solutions**:
- Check if your taxonomy file covers the product category
- Try providing more specific product information
- Verify the taxonomy file format is correct
- Use `--verbose` to see detailed processing information

### File Format Issues

**Problem**: "Error building taxonomy tree"

**Solutions**: 
- Ensure your taxonomy file uses the correct format with " > " separators
- Check for any special characters or encoding issues in the file
- Verify the file is UTF-8 encoded

## Advanced Usage

### Custom Models

You can specify different OpenAI models:

```bash
./scripts/classify_single_product.sh --model "gpt-4o" ...
```

### Verbose Logging

For debugging, use the verbose flag:

```bash
./scripts/classify_single_product.sh --verbose ...
```

### Custom Taxonomy Files

Use your own taxonomy file:

```bash
./scripts/classify_single_product.sh --taxonomy-file my-taxonomy.txt ...
```

### Custom Output Files

Specify where to save the results:

```bash
./scripts/classify_single_product.sh --output-file my-results.json ...
```

## Integration with Other Systems

### Command Line Integration

The system can be easily integrated into other workflows:

```bash
# Process a single product and capture output
./scripts/classify_single_product.sh \
  -n "iPhone" \
  -d "Smartphone" > classification_result.txt
```

### JSON Output Processing

The detailed JSON output can be processed by other tools:

```bash
# Get the best match from JSON output
python3 -c "
import json
with open('results/taxonomy_results.json') as f:
    data = json.load(f)
    if data and data[-1]['matches']:
        best_match = data[-1]['matches'][data[-1]['best_match_index']]
        print(best_match['full_path'])
"
```

### Environment Variables for Production

For production deployments:

```bash
export OPENAI_API_KEY="your-key"
export TAXONOMY_FILE="/path/to/taxonomy.txt"
export OUTPUT_DIR="/path/to/results"

./scripts/classify_single_product.sh \
  -n "$PRODUCT_NAME" \
  -d "$PRODUCT_DESC" \
  --taxonomy-file "$TAXONOMY_FILE" \
  --output-file "$OUTPUT_DIR/result_$(date +%s).json"
```

## Performance Tips

1. **Choose the right script**:
   - Use `classify_single_product.sh` for detailed analysis
   - Use `analyze_batch_products.sh` for quick batch validation

2. **Model selection**: 
   - gpt-4.1-nano is fast and economical (default for all stages)
   - gpt-4o provides higher accuracy for complex products but costs more

3. **Batch processing**: Use the batch script for multiple products

4. **Monitoring**: Use `--verbose` to monitor performance bottlenecks

5. **Interactive mode**: Use for testing and development

## Security Best Practices

1. **API Key Management**:
   - Use environment variables in production
   - Never commit API keys to version control
   - Regularly rotate API keys
   - Monitor usage and billing

2. **Input Validation**:
   - Validate product descriptions before processing
   - Sanitize file paths
   - Check file permissions

3. **Output Security**:
   - Secure result files appropriately
   - Consider encryption for sensitive data
   - Implement proper access controls

## Use Case Guide

| **What you want to do** | **Use this script** | **Command** |
|--------------------------|---------------------|-------------|
| Classify one product with details | `classify_single_product.sh` | `-n "Product" -d "Description"` |
| Test multiple products interactively | `classify_single_product.sh` | `--interactive` |
| Quick batch validation | `analyze_batch_products.sh` | `--products file.txt` |
| Get clean output for demo | `analyze_batch_products.sh` | Default |
| Debug classification issues | `classify_single_product.sh` | `--verbose` |
| Save detailed results | `classify_single_product.sh` | `--interactive --save-results` |
| Performance benchmarking | `classify_single_product.sh` | `--interactive` mode |