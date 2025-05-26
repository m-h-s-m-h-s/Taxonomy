# Taxonomy Navigator - Script Usage Guide

This project has a clean, logical script structure with just **2 main scripts** that cover all use cases:

## 🔧 Available Scripts

### 1. `scripts/classify_single_product.sh`
**Purpose**: Classify individual products with detailed analysis using 5-stage AI process

**Two Modes Available:**

#### Command-Line Mode (Default)
Classify a single product via command-line arguments:
```bash
./scripts/classify_single_product.sh \
  --product-name "iPhone 14 Pro" \
  --product-description "Smartphone with advanced camera system"
```

#### Interactive Mode
Launch an interactive interface for testing multiple products in a session:
```bash
./scripts/classify_single_product.sh --interactive
```

**Key Features:**
- ✅ Single product classification with detailed results using 5-stage process
- ✅ Interactive mode for real-time testing
- ✅ Session statistics and result saving (interactive mode)
- ✅ JSON output with comprehensive metadata
- ✅ Configurable AI models and taxonomy files
- ✅ Uses gpt-4.1-nano for initial stages, gpt-4.1-nano for final precision
- ✅ Stage 4 validation prevents AI hallucinations

---

### 2. `scripts/analyze_batch_products.sh`
**Purpose**: Simple batch testing of multiple products using 5-stage classification

**Simple Output Mode:**
Clean, minimal output perfect for demonstrations and quick validation:
```bash
./scripts/analyze_batch_products.sh --products my_products.txt
```

**Key Features:**
- ✅ Batch processing from text files using 5-stage AI process
- ✅ Clean, minimal output showing "Product: Category"
- ✅ No timing overhead or complex metrics
- ✅ Perfect for demonstrations and quick validation
- ✅ Configurable AI models and taxonomy files
- ✅ Progressive filtering: 4,722 → 20 → filtered L1 → 10 → validated → 1

---

## 🚀 Quick Start Examples

### Single Product Classification (Detailed)
```bash
# Basic single product with detailed 5-stage results
./scripts/classify_single_product.sh -n "Xbox Controller" -d "Wireless gaming controller"

# Interactive mode for multiple products with detailed analysis
./scripts/classify_single_product.sh --interactive --save-results
```

### Batch Product Testing (Simple)
```bash
# Simple batch testing with clean output using 5-stage process
./scripts/analyze_batch_products.sh

# Custom products file
./scripts/analyze_batch_products.sh --products my_products.txt --verbose
```

---

## 📁 File Structure

```
scripts/
├── classify_single_product.sh    # Single product classification (CLI + Interactive)
└── analyze_batch_products.sh     # Simple batch testing

src/
├── taxonomy_navigator_engine.py  # Core classification engine
├── interactive_interface.py      # Interactive interface
└── config.py                     # Configuration management

tests/
├── simple_batch_tester.py      # Simple batch testing tool
├── unit_tests.py               # Unit tests
└── sample_products.txt         # Sample products for testing

results/
└── taxonomy_results.json       # Classification results output
```

---

## 🎯 Use Case Guide

| **What you want to do** | **Use this script** | **Mode/Options** |
|--------------------------|---------------------|------------------|
| Classify one product with details | `classify_single_product.sh` | Command-line mode |
| Test multiple products interactively | `classify_single_product.sh` | `--interactive` |
| Quick batch validation | `analyze_batch_products.sh` | Default |
| Get clean output for demo | `analyze_batch_products.sh` | Default |
| Debug classification issues | `classify_single_product.sh` | `--verbose` |
| Save detailed results | `classify_single_product.sh` | `--interactive --save-results` |
| Performance benchmarking | `classify_single_product.sh` | `--interactive` mode |

---

## 🔧 Common Options

Both scripts support these common options:
- `--taxonomy FILE` - Custom taxonomy file
- `--model MODEL` - Different AI model for Stages 1&3 (gpt-4.1-nano, gpt-4.1-nano, etc.)
- `--verbose` - Detailed logging for debugging
- `--help` - Show usage information

**Note**: Stage 5 (final selection) always uses gpt-4.1-nano for enhanced precision.

---

## 📝 Products File Format

For batch processing, create a text file with one product per line:
```
iPhone 14 Pro: Smartphone with advanced camera system
Xbox Wireless Controller: Gaming controller with Bluetooth connectivity
Nike Air Max 270: Running shoes with air cushioning technology
MacBook Pro: Laptop computer for professional use
```

---

## 💡 Design Philosophy

**Simple & Focused:**
- **Single Product Script**: Handles detailed analysis, metrics, JSON output, interactive mode
- **Batch Script**: Handles simple, clean batch testing for quick validation

## Five-Stage Classification Process

The Taxonomy Navigator uses a sophisticated five-stage approach for maximum efficiency and accuracy:

1. **Initial Leaf Node Matching** (gpt-4.1-nano): AI selects top 20 relevant categories from all 4,722 options
2. **Layer Filtering** (algorithmic): Filters to most popular L1 taxonomy layer
3. **Refined Selection** (gpt-4.1-nano): AI refines to top 10 categories from filtered L1 taxonomy candidates
4. **Validation** (algorithmic): Ensures AI didn't hallucinate any category names that don't exist
5. **Final Selection** (gpt-4.1-mini): AI selects best match using enhanced model with anti-hallucination measures

### Anti-Hallucination Protection

The system includes comprehensive protection against AI hallucinations:
- **Stage 4 Validation**: Removes any category names that don't exist in the taxonomy
- **Stage 5 Robust Validation**: Multiple layers of index validation and bounds checking
- **Fallback Mechanisms**: Graceful handling of invalid AI responses
- **Guaranteed Valid Results**: Final safety checks ensure valid category selection
- **Complete Failure Handling**: Returns "False" when AI completely fails or returns nothing

This simplified structure eliminates confusion and provides clear, logical choices for any classification task! 