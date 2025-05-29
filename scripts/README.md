# Taxonomy Navigator - Script Usage Guide

## 🚀 Quick Start - Understanding the System

**New to this project? Start here:**

```bash
# First, see how the system works:
cd tests
python3 simple_batch_tester.py

# Enter 3 when prompted
# Watch the AI classify products step-by-step!
```

This shows you exactly how the AI:
- Starts with thousands of categories
- Narrows down to 2 main sections
- Finds specific categories in each section
- Makes the final choice

## 📚 Understanding the Classification Process

The system works like a smart librarian organizing books:

1. **Stage 1**: "Is this Electronics or Toys?" (picks 2 main categories)
2. **Stage 2A**: "Which type of electronics?" (picks up to 15 specific categories)
3. **Stage 2B**: "Any toy categories?" (picks up to 15 more, if needed)
4. **Stage 3**: "Pick the best match" (final selection, if needed)

The system can skip stages when the answer is obvious (e.g., only 1 category found).

## 🔧 Available Scripts

### 1. `tests/simple_batch_tester.py` (Start Here!)
**Purpose**: See the classification process in action

**Interactive Mode (Recommended):**
```bash
cd tests
python3 simple_batch_tester.py

# When prompted, enter how many products to test (e.g., 3)
# Products are randomly selected from sample_products.txt
```

**What You'll See:**
- Each stage of the classification process
- How many categories the AI considers
- Why certain stages are skipped
- The final category selection

### 2. `scripts/classify_single_product.sh`
**Purpose**: Classify individual products with detailed analysis

**Basic Usage:**
```bash
./scripts/classify_single_product.sh \
  --product-name "iPhone 14 Pro" \
  --product-description "Smartphone with advanced camera system"
```

**Interactive Mode:**
```bash
./scripts/classify_single_product.sh --interactive
# Test multiple products in one session
```

### 3. `scripts/analyze_batch_products.sh`
**Purpose**: Process multiple products from a file

```bash
# Process all products in sample file
./scripts/analyze_batch_products.sh

# Use your own product list
./scripts/analyze_batch_products.sh --products my_products.txt
```

## 📁 File Structure Explained

```
project-root/
├── tests/
│   ├── simple_batch_tester.py    # 👈 START HERE - See the system in action
│   └── sample_products.txt       # Example products to test
│
├── scripts/
│   ├── classify_single_product.sh  # For classifying individual products
│   └── analyze_batch_products.sh   # For batch processing
│
├── src/
│   └── taxonomy_navigator_engine.py  # The brain of the system
│
└── data/
    └── taxonomy.en-US.txt  # The 5,000+ categories to choose from
```

## 🎯 Common Use Cases

| **What you want to do** | **Use this** | **Command** |
|-------------------------|--------------|-------------|
| See how it works | `simple_batch_tester.py` | `cd tests && python3 simple_batch_tester.py` |
| Test one product | `classify_single_product.sh` | See examples above |
| Process many products | `analyze_batch_products.sh` | See examples above |
| Debug issues | Any script with `--verbose` | Add `--verbose` flag |

## 💡 Understanding the Output

When you run the simple batch tester, you'll see:

```
📋 STAGE 1: Identifying Main Product Categories
   Goal: Pick 2 broad categories from all 469 options

   ✅ AI Selected 2 Main Categories:
      1. Electronics
      2. Software
```

This tells you:
- What the AI is trying to do
- What the AI decided

## 📝 Products File Format

Create a text file with one product per line:
```
iPhone 14 Pro: Smartphone with advanced camera system
Xbox Controller: Wireless gaming controller
Nike Air Max: Running shoes with air cushioning
```

## ❓ FAQ

**Q: Why does it sometimes skip stages?**
A: If there's only 1 option left, there's no need to choose!

**Q: How does the AI decide which category?**
A: It analyzes the full product description at each stage to make the best match.

**Q: Why use multiple stages?**
A: Breaking it down helps the AI focus on the right level of detail at each step.

## 🚨 Troubleshooting

If classification seems wrong:
1. Run with `--verbose` to see detailed logs
2. Check if the product description is clear
3. Ensure the product name and description accurately describe the item
4. Try the interactive mode to test variations

Need help? The simple batch tester output shows exactly what the AI sees and decides at each step! 