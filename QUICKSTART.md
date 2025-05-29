# Quick Start Guide - Taxonomy Navigator v12.4

Welcome! This guide will get you up and running with the Taxonomy Navigator in under 5 minutes.

## What is Taxonomy Navigator?

An AI-powered system that automatically categorizes products into Google Product Taxonomy categories. It uses a smart 5-stage process to narrow down from 5,000+ categories to the single best match.

## Key Innovation in v12.4

- **Numeric Selection**: AI selects by number, eliminating misspellings
- **Batch Processing**: All 5,000+ categories are accessible, not just the first 100
- **Expanded Selection**: Up to 15 selections PER BATCH (v12.4) instead of 15 total
- **Smart Summaries**: AI creates 40-60 word summaries optimized for categorization

## Installation (2 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-repo/taxonomy-navigator.git
   cd taxonomy-navigator
   ```

2. **Install dependencies**
   ```bash
   pip install openai
   ```

3. **Set up your OpenAI API key** (choose one method):
   ```bash
   # Method 1: Environment variable
   export OPENAI_API_KEY="sk-..."
   
   # Method 2: Create file
   echo "sk-..." > data/api_key.txt
   ```

## First Test (1 minute)

Run the interactive tester:

```bash
cd tests
python3 simple_batch_tester.py
```

When prompted, enter `3` to test 3 random products. Watch as the AI:
1. Creates a summary
2. Picks 2 main categories
3. Selects specific categories (by number!)
4. Makes the final choice

## Understanding the Output

```
📝 GENERATING AI SUMMARY
   Television (TV, flat-screen display). A display device for viewing video content...

📋 STAGE 2A: Finding Specific Categories in 'Electronics'
   Processing batch 1: options 1-100
   Processing batch 2: options 101-200
   Processing batch 3: options 201-300
   Processing batch 4: options 301-339
   ✅ Batch 4: Selected option 15: 'Televisions'
```

Notice how:
- The AI summary starts with "Television" and includes synonyms "(TV, flat-screen display)"
- Stage 2 processes categories in batches of 100
- "Televisions" is at position 315 (batch 4, option 15)
- AI selects by number (15) not by typing "Televisions"

## The Logic Behind Our Design Choices

### Why 5 Stages?

**The Challenge**: Google Product Taxonomy has 5,000+ categories organized in a hierarchy. Asking AI to pick one from 5,000 in a single step would be:
- Expensive (huge prompts)
- Inaccurate (too many options)
- Prone to hallucination

**Our Solution**: Progressive filtering through 5 stages:

1. **AI Summary Stage** (Why?)
   - **Problem**: Product descriptions are often long with marketing fluff
   - **Solution**: Create a 40-60 word summary focused on categorization
   - **Example**: A 500-word iPhone description becomes "Smartphone (mobile phone, cell phone). Mobile device for communication..."
   - **Benefit**: Consistent, focused input for stages 1-2 with clarifying synonyms

2. **Stage 1: Pick 2 Main Categories** (Why 2?)
   - **Problem**: Products often fit multiple top-level categories
   - **Solution**: Pick 2 to explore both paths
   - **Example**: A smartwatch could be in "Electronics" OR "Apparel & Accessories"
   - **Benefit**: Don't miss the best category by being too narrow early

3. **Stage 2A/2B: Batch Processing** (Why batches?)
   - **Problem**: Some L1 categories have 900+ subcategories
   - **Solution**: Process in batches of 100
   - **Example**: Home & Garden has 903 categories = 10 batches
   - **Benefit**: Every category is accessible, not just the first 100

4. **Stage 3: Final Decision**
   - **What**: Picks the ONE best category
   - **Why**: Need to make the final choice from all candidates
   - **How**: Shows all selected categories with AI-generated summary
   - **Model**: gpt-4.1-mini (balanced intelligence and cost)

### Why Numeric Selection?

**The Problem We Solved**:
```
❌ OLD WAY - AI returns text:
User: "Select categories for this TV"
AI: "Television" (WRONG - should be "Televisions")
AI: "TV Mount" (WRONG - should be "TV Mounts")
Result: Hallucination errors!
```

**Our Solution**:
```
✅ NEW WAY - AI returns numbers:
1. Home Theater Systems
2. TV Mounts
...
315. Televisions

User: "Select categories for this TV"
AI: "315"
Result: Perfect match every time!
```

### Why Batch Processing?

**The Problem**:
- Original design showed only first 100 categories to AI
- "Televisions" is at position 315 in Electronics (invisible!)
- Many important categories were unreachable

**Our Solution**:
- Batch 1: Show options 1-100
- Batch 2: Show options 101-200
- Batch 3: Show options 201-300
- Batch 4: Show options 301-339 (includes "Televisions" at 315!)

**The Logic**:
- We can't show 900+ options in one prompt (token limits)
- Breaking into batches makes every category reachable
- AI evaluates each batch independently

### Why 15 Per Batch (v12.4)?

**Original Design (v12.3)**:
- 15 total across ALL batches
- Problem: Complex products need more options
- Example: A multi-tool could match 50+ categories

**New Design (v12.4)**:
- 15 per batch (e.g., 4 batches = up to 60 selections)
- Logic: Let AI be comprehensive in each batch
- Benefit: Stage 3 has more options for better final selection

**Real Example**:
- Product: "Smart Home Security Camera"
- Could match: Security Cameras, Home Automation, Surveillance Systems, Smart Home Hubs, etc.
- Old way: Limited to 15 total
- New way: Could select 40+ relevant categories

### Why Different Models?

**Our Model Strategy**:
- **Summary + Stages 1-2**: `gpt-4.1-nano` (fast, cheap)
- **Stage 3**: `gpt-4.1-mini` (balanced accuracy and cost)

**The Logic**:
1. Early stages are simpler tasks (pick from lists)
2. Final selection needs good intelligence without excessive cost
3. Using nano for most stages saves money
4. Using mini for Stage 3 provides strong accuracy at reasonable cost

### Why Skip Stages?

**Conditional Logic**:
- Skip Stage 2B if only 1 L1 category selected
- Skip Stage 3 if only 1 leaf category found

**The Reasoning**:
- No point checking a second L1 if only one was relevant
- No point doing final selection if there's only one option
- Saves API calls (cost) and time
- Example: "iPhone" → Electronics → Smartphones (done in 3 calls)

4. **Stage 3: Final Decision** (Why use summary?)
   - **Problem**: Need to pick the single best category from many options
   - **Solution**: Use the same AI-generated summary for consistency
   - **Example**: Choose between "Smartphones", "Mobile Phone Cases", "Screen Protectors"
   - **Benefit**: Consistent context across all stages, more predictable results

## How It Works - Complete Flow

### 5-Stage Process with Design Rationale

1. **AI Summary** 
   - **What**: Creates 40-60 word category-focused summary
   - **Why**: Removes noise, focuses on category-relevant features
   - **How**: Instructs AI to start with product type, then key features
   - **Model**: gpt-4.1-nano (sufficient for extraction tasks)

2. **Stage 1: L1 Selection**
   - **What**: Picks 2 main categories from ~21 options
   - **Why**: Products often fit multiple top-level categories
   - **How**: Shows all L1 categories, AI picks 2 most relevant
   - **Model**: gpt-4.1-nano (simple selection task)

3. **Stage 2A/2B: Leaf Selection**
   - **What**: Selects specific categories from each L1
   - **Why**: Need to explore all possibilities under each L1
   - **How**: 
     - Processes in batches of 100 (token limits)
     - AI selects by number (no misspellings)
     - Up to 15 per batch (comprehensive coverage)
   - **Model**: gpt-4.1-nano (list selection task)

4. **Stage 3: Final Decision**
   - **What**: Picks the ONE best category
   - **Why**: Need to make the final choice from all candidates
   - **How**: Shows all selected categories with AI-generated summary
   - **Model**: gpt-4.1-mini (balanced intelligence and cost)

### Why This Architecture?

**Alternative Approaches We Considered**:

1. **Single-Stage Approach** ❌
   - Show all 5,000 categories at once
   - Problems: Token limits, accuracy, cost

2. **Keyword Search First** ❌
   - Use keywords to filter categories
   - Problems: Misses relevant categories, depends on exact wording

3. **Fixed Category Limits** ❌
   - Always select exactly 15 categories
   - Problems: Some products need 5, others need 50

4. **Same Model Throughout** ❌
   - Use gpt-4.1-mini for everything
   - Problems: 3x more expensive, not needed for simple tasks

**Why Our Approach Works** ✅:
- Progressive filtering (5000 → 2 → 60 → 1)
- Adaptive (skips unnecessary stages)
- Cost-optimized (nano for simple, mini for complex)
- Comprehensive (every category is reachable)
- Accurate (numeric selection, no misspellings)

## Python Usage

```python
from src.taxonomy_navigator_engine import TaxonomyNavigator

# Initialize
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    api_key="sk-..."  # Optional if set in environment
)

# Classify a product
product = "Samsung 65-inch QLED 4K Smart TV with HDR"
paths, best_idx = navigator.navigate_taxonomy(product)

# Get result
if paths[0][0] != "False":
    category = paths[best_idx][-1]  # "Televisions"
    full_path = " > ".join(paths[best_idx])  # "Electronics > Video > Televisions"
    print(f"Category: {category}")
    print(f"Full path: {full_path}")
else:
    print("Classification failed")
```

## Common Use Cases

### Batch Processing
```python
products = [
    "iPhone 14 Pro",
    "Nike Air Max",
    "KitchenAid Mixer"
]

for product in products:
    paths, idx = navigator.navigate_taxonomy(product)
    if paths[0][0] != "False":
        print(f"{product}: {paths[idx][-1]}")
```

### With Error Handling
```python
try:
    paths, idx = navigator.navigate_taxonomy(product)
    if paths[0][0] != "False":
        category = paths[idx][-1]
    else:
        category = "Unknown"
except Exception as e:
    print(f"Error: {e}")
    category = "Error"
```

## Performance & Cost Analysis

### API Calls Breakdown
- **Summary**: 1 call (nano)
- **Stage 1**: 1 call (nano)
- **Stage 2A**: 1-10 calls depending on category size (nano)
- **Stage 2B**: 0-10 calls (skipped if 1 L1) (nano)
- **Stage 3**: 0-1 call (skipped if 1 leaf) (mini)

### Cost Example
For a typical product:
- 5 nano calls + 1 mini call
- Cost: ~$0.001-0.0015 total
- Without our optimizations: ~$0.006 (6x more)

### Time Breakdown
- Summary: ~0.5 seconds
- Stage 1: ~0.3 seconds
- Stage 2: ~1-3 seconds (depends on batches)
- Stage 3: ~0.5 seconds
- Total: 3-5 seconds typical

## Debugging Tips

1. **Enable verbose logging**:
   ```python
   import logging
   logging.getLogger("taxonomy_navigator").setLevel(logging.INFO)
   ```

2. **Check API calls**:
   - Look for "Processing batch X" messages
   - Verify all batches are processed

3. **Common issues**:
   - API key not set: Check environment or api_key.txt
   - Slow response: Normal for large categories (10+ batches)
   - Wrong category: Check if it's an accessory vs main product issue

## Architecture Overview

```
Product Description
    ↓
[AI Summary] - 40-60 words, starts with product type
    ↓
[Stage 1] - Pick 2 main categories (from ~21)
    ↓
[Stage 2A] - Pick ≤15 per batch from first category (e.g., up to 60 for Electronics)
[Stage 2B] - Pick ≤15 per batch from second category (if applicable)
    ↓
[Stage 3] - Final selection (using AI summary)
    ↓
Final Category
```

## Design Philosophy

Our system is built on these principles:

1. **Progressive Refinement**: Start broad, narrow down gradually
2. **Adaptive Processing**: Skip unnecessary work
3. **Cost Optimization**: Use cheaper models where possible
4. **Comprehensive Coverage**: Every category must be reachable
5. **Accuracy First**: Numeric selection eliminates errors
6. **Transparent Process**: Show what's happening at each stage

## Next Steps

1. **Read the full documentation**: See README.md for detailed info
2. **Check the architecture**: See docs/ARCHITECTURE.md for technical details
3. **Run more tests**: Try different products to see the system in action
4. **Customize**: Adjust models, prompts, or batch sizes in the code

## Questions?

- **Why not use embeddings?** We need exact category matches, not similarity
- **Why not fine-tune a model?** Taxonomy changes; our approach adapts automatically
- **Can I use different models?** Yes, just change the model parameters
- **Can I adjust batch size?** Yes, but 100 is optimal for token limits

Happy categorizing! 🎯 