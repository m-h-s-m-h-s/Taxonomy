# Taxonomy Navigator - Complete Usage Guide

## 🚀 Getting Started - See It In Action First!

Before diving into details, **see the system work**:

```bash
# Watch the AI classify 3 random products step-by-step
cd tests
python3 simple_batch_tester.py

# When prompted, enter: 3
# Watch how the AI narrows down from 5,000+ categories to 1!
```

This visual demonstration shows you:
- How the AI progressively filters categories
- Why certain stages are skipped
- How truncation saves money
- The actual decision-making process

## 📚 How The System Works

Think of it like a smart filing system:

1. **Stage 1**: "Which department?" (Electronics? Clothing? Toys?)
   - Character limit: First 300 characters
   - Picks 2 main categories from ~469 options

2. **Stage 2A**: "What type in department 1?"
   - Character limit: First 1000 characters
   - Picks up to 15 specific products

3. **Stage 2B**: "What type in department 2?" (if needed)
   - Character limit: First 1000 characters
   - Skipped if only 1 department selected

4. **Stage 3**: "Final choice?" (if needed)
   - Character limit: First 700 characters
   - Picks the single best match
   - Skipped if only 1 option remains

## 🎮 Usage Options

### Option 1: Interactive Testing (Recommended for Beginners)

```bash
cd tests
python3 simple_batch_tester.py
```

**What happens:**
1. You'll be asked how many products to test
2. Products are randomly selected from examples
3. You see the complete classification process
4. Results show both the process and final category

**Example output:**
```
📋 STAGE 1: Identifying Main Product Categories
   Goal: Pick 2 broad categories from all 469 options
   
   ✅ AI Selected 2 Main Categories:
      1. Electronics
      2. Software
```

### Option 2: Command Line Classification

```bash
# Basic usage
python3 src/taxonomy_navigator_engine.py \
  --product-name "iPhone 14" \
  --product-description "Smartphone with camera"

# With verbose output
python3 src/taxonomy_navigator_engine.py \
  --product-name "Nike Shoes" \
  --product-description "Running shoes" \
  --verbose
```

### Option 3: Batch Processing

```bash
# Process a file of products
cd scripts
./analyze_batch_products.sh --products ../tests/sample_products.txt
```

### Option 4: Python API

```python
from src.taxonomy_navigator_engine import TaxonomyNavigator

# Initialize
navigator = TaxonomyNavigator("data/taxonomy.en-US.txt")

# Classify a product
product = "iPhone 14: Smartphone with advanced camera"
paths, best_idx = navigator.navigate_taxonomy(product)

# Get result
if paths != [["False"]]:
    category = paths[best_idx][-1]
    print(f"Category: {category}")
```

## 📊 Understanding Output

### Stage-by-Stage Display

When you run with `--show-stage-paths`, you see:

```
📋 STAGE 1: Identifying Main Product Categories
   Goal: Pick 2 broad categories from all 469 options
   
   ✅ AI Selected 2 Main Categories:
      1. Electronics
      2. Apparel & Accessories
```

This tells you:
- **Goal**: What the AI is trying to do
- **Character Limit**: How much of the product description the AI sees
- **Results**: What the AI decided

### When Stages Are Skipped

```
📋 STAGE 2B: SKIPPED
   Reason: Only 1 main category was selected, no need to check a second
```

The system is smart enough to skip unnecessary work!

### Final Results

```
🎯 FINAL CLASSIFICATION RESULT:
   Full Category Path: Electronics > Cell Phones > Smartphones
   Product Category: Smartphones
```

## 💰 Character Truncation Strategy

The system truncates product descriptions to optimize AI processing:

| Stage | Characters Used | Why This Amount? |
|-------|----------------|------------------|
| 1 | 300 | Just enough to identify broad category |
| 2A/2B | 1000 | More detail needed for specific product selection |
| 3 | 700 | Balanced amount for final decision making |

**Why truncate?**
- Reduces AI token usage and costs
- Focuses on essential product information
- Improves processing speed
- Most product descriptions have key info at the beginning

## 🔧 Advanced Configuration

### Custom Taxonomy File

```bash
python3 src/taxonomy_navigator_engine.py \
  --taxonomy-file my_taxonomy.txt \
  --product-name "Custom Product"
```

### Different AI Models

```bash
# Use different model for stages 1 & 3
python3 src/taxonomy_navigator_engine.py \
  --model gpt-4 \
  --product-name "Complex Product"
```

### Environment Variables

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Set default taxonomy
export TAXONOMY_FILE="/path/to/taxonomy.txt"
```

## 📝 Input Format Tips

### Good Product Descriptions

✅ **Good**: "iPhone 14 Pro: Smartphone with 48MP camera, A16 chip"
- Product name first
- Key features upfront
- Clear and concise

❌ **Bad**: "Amazing deal! Limited time! The newest sensation..."
- Marketing fluff first
- Product details buried
- Unclear what it is

### Batch File Format

Create `products.txt`:
```
iPhone 14: Smartphone with ProMotion display
Nike Air Max: Running shoes with air cushioning
LEGO Star Wars: Building set with 500 pieces
```

## 🚨 Troubleshooting

### "Classification returned False"

**Causes:**
1. Product description too vague
2. Product type not in first 300 chars
3. Unusual product not in taxonomy

**Solutions:**
1. Make description clearer
2. Put product type early in description
3. Check if category exists in taxonomy

### "Stage returned 0 categories"

**Causes:**
1. Very specific product
2. Mismatched category selection

**Solutions:**
1. Use more general description
2. Check verbose output to see why

### Unexpected Categories

**Causes:**
1. Ambiguous product description
2. Multiple valid categories

**Solutions:**
1. Be more specific in description
2. Include distinguishing features

## 📊 Performance Tips

### For Fastest Classification

1. **Clear product names**: "iPhone 14" not "Latest Apple device"
2. **Front-load key info**: Put product type in first 300 chars
3. **Avoid marketing text**: Skip "Amazing deal!" type content
4. **Use standard terms**: "Laptop" not "Portable computing device"

### For Best Accuracy

1. **Include key features**: Brand, model, main purpose
2. **Be specific**: "Running shoes" not just "shoes"
3. **Mention category**: "Smartphone" for phones
4. **Avoid ambiguity**: Clear single purpose

## 🎯 Example Workflows

### Testing New Products

```bash
# 1. Test with visualization
cd tests
python3 simple_batch_tester.py

# 2. If results look wrong, try verbose mode
python3 ../src/taxonomy_navigator_engine.py \
  --product-name "Your Product" \
  --product-description "Description" \
  --verbose

# 3. Adjust description based on what you learn
```

### Processing Product Catalog

```bash
# 1. Prepare products file
echo "Product1: Description" > products.txt
echo "Product2: Description" >> products.txt

# 2. Run batch processing
./scripts/analyze_batch_products.sh --products products.txt

# 3. Check results
cat results/taxonomy_results.json
```

## 📚 Further Resources

- **README.md**: Project overview and quick start
- **ARCHITECTURE.md**: Technical implementation details
- **scripts/README.md**: Script-specific documentation

Need help? Start with the simple batch tester - it shows you exactly what the AI sees and decides!

## How the AI Classification Works

The system uses a multi-stage approach to narrow down from thousands of categories to one:

### Stage 1: Main Category Selection
The AI looks at your product and selects 2 broad categories where it might belong.
- **Example**: For an iPhone, it might select "Electronics" and "Mobile Phones"
- **Why it works**: Starting broad helps ensure we don't miss the right category

### Stage 2: Specific Category Selection  
For each main category, the AI finds up to 15 specific product types.
- **Stage 2A**: Searches in the first main category
- **Stage 2B**: Searches in the second main category (if applicable)
- **Example**: Finds "Smartphones", "Phone Cases", "Screen Protectors", etc.

### Stage 3: Final Decision
The AI picks the single best match from all candidates.
- **Example**: Selects "Smartphones" as the best match for iPhone
- **Smart feature**: Skips this step if only 1 category was found

### Understanding the Stage Details

When you run the batch tester with stage details enabled, you'll see:

```
📋 STAGE 1: Identifying Main Product Categories
   Goal: Pick 2 broad categories from all 43 options
   
   ✅ AI Selected 2 Main Categories:
      1. Electronics
      2. Cell Phones & Accessories

📋 STAGE 2A: Finding Specific Categories in 'Electronics'
   Goal: Select up to 15 specific product categories
   
   ✅ Found 15 Relevant Categories:
      1. Smartphones
      2. Tablet Computers
      ... (more categories)

📋 STAGE 3: Making Final Decision
   Goal: Choose the single best category from 28 options
```

Each stage shows:
- **Goal**: What the AI is trying to accomplish
- **Results**: What the AI found