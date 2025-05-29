# Taxonomy Navigator - AI-Powered Product Categorization System

An intelligent, optimized AI classification system that automatically categorizes products into appropriate taxonomy categories using OpenAI's GPT models with aggressive anti-hallucination measures and smart truncation.

## 🚀 Quick Start - See It In Action!

**Want to understand how this works? Start here:**

```bash
# First, see the system in action with 3 random products:
cd tests
python3 simple_batch_tester.py

# When prompted, enter the number of products to test (e.g., 3)
# Watch as the AI classifies products step-by-step!
```

This will show you:
- How the AI progressively narrows down from thousands of categories to one
- The actual AI decision-making process at each stage
- How truncation saves tokens while maintaining accuracy
- Why some stages are skipped for efficiency

## 🎯 System Overview

The Taxonomy Navigator uses a sophisticated progressive filtering approach with intelligent optimizations that efficiently narrows down from thousands of categories to a single best match:

## How It Works

The Taxonomy Navigator uses a smart 4-stage process to categorize products:

### 🎯 Stage 1: Finding Main Categories
**What it does:** The AI looks at your product and picks the 2 most relevant main sections of the catalog.
- **Example:** For an iPhone, it might pick "Electronics" and "Mobile Phones & Accessories"
- **Why 2?** Sometimes products fit in multiple categories, so we explore both to find the best match

### 🔍 Stage 2: Finding Specific Categories  
**What it does:** For each main category from Stage 1, the AI picks the 15 most relevant specific categories.
- **Stage 2A:** Looks through all specific categories in the first main section
- **Stage 2B:** Looks through all specific categories in the second main section (skipped if only 1 main category was found)
- **Example:** In "Electronics", it might find "Smartphones", "Phone Cases", "Chargers", etc.

### 🏆 Stage 3: Making the Final Choice
**What it does:** The AI looks at all the specific categories found (up to 30) and picks the single best match.
- **Example:** From all options, it picks "Smartphones" as the best match for an iPhone
- **Smart Skip:** If only 1 category was found in Stage 2, this stage is skipped to save time

### Why This Approach?
- **Efficient:** Instead of checking thousands of categories at once, we narrow down progressively
- **Accurate:** By exploring multiple paths, we don't miss the best category
- **Smart:** The system knows when to skip unnecessary steps (like when there's only 1 option)

## 🎯 System Overview

The Taxonomy Navigator uses a sophisticated progressive filtering approach with intelligent optimizations that efficiently narrows down from thousands of categories to a single best match:

### **Optimized Classification Process**

🎯 **STAGE 1: L1 TAXONOMY SELECTION** (AI-Powered)
- **Purpose**: Identify the 2 most relevant top-level taxonomy categories
- **Model**: `gpt-4.1-nano` (efficient model for L1 selection)
- **Character Limit**: First 200 characters of product description
- **Process**: AI selects 2 most relevant L1 categories (e.g., "Electronics", "Apparel & Accessories")
- **Output**: List of 2 L1 category names
- **Anti-Hallucination**: Professional prompting with explicit constraints

🔍 **STAGE 2A: FIRST L1 LEAF SELECTION** (AI-Powered)
- **Purpose**: Select the first 15 best leaf nodes from the FIRST chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Character Limit**: First 500 characters of product description
- **Process**: AI selects top 15 most relevant leaf categories from the FIRST L1 taxonomy
- **Output**: List of up to 15 leaf node names from the FIRST L1 taxonomy
- **Anti-Hallucination**: Professional prompting + strict validation

🔍 **STAGE 2B: SECOND L1 LEAF SELECTION** (AI-Powered) - CONDITIONAL
- **Purpose**: Select the second 15 best leaf nodes from the SECOND chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Character Limit**: First 500 characters of product description
- **Process**: AI selects top 15 most relevant leaf categories from the SECOND L1 taxonomy
- **Output**: List of up to 15 leaf node names from the SECOND L1 taxonomy
- **Condition**: SKIPPED if only 1 L1 category was selected in Stage 1
- **Anti-Hallucination**: Professional prompting + strict validation

🏆 **STAGE 3: FINAL SELECTION** (AI-Powered with Anti-Hallucination) - CONDITIONAL
- **Purpose**: Make the final decision from the combined leaf nodes from Stages 2A and 2B
- **Model**: `gpt-4.1-mini` (enhanced model for critical final selection)
- **Character Limit**: First 400 characters of product description
- **Process**: 
  * Construct clear, professional prompt with specific constraints
  * Present leaf categories as numbered options
  * AI identifies core product and selects best match
  * Parse AI response with robust validation and bounds checking
- **Output**: Index of selected category (0-based, guaranteed valid) OR -1 for complete failure
- **Condition**: SKIPPED if only 1 leaf was selected in Stage 2
- **Anti-Hallucination**: Professional prompting + numeric validation + bounds checking + "False" for failures

## 🚨 Key Optimizations

### **Character Truncation Strategy**
- **Stage 1**: 200 characters - Just enough for AI to identify broad category
- **Stage 2**: 500 characters - Moderate detail for specific leaf selection
- **Stage 3**: 400 characters - Balanced detail for final decision

### **Conditional Execution**
- **Stage 2B**: Only runs if 2 L1 categories selected (saves 1 API call)
- **Stage 3**: Only runs if >1 leaf selected (saves 1 API call)
- **Efficiency**: Can complete in as few as 2 API calls for simple products

### **Progressive Filtering**
- **Initial**: Thousands of categories
- **After Stage 1**: 2 L1 categories
- **After Stage 2**: Up to 30 leaf candidates (15 per L1)
- **Final**: 1 best match

## 🚨 Anti-Hallucination Measures

### **Professional Prompting Strategy**
- **Clear Instructions**: Uses professional language to guide AI responses
- **Explicit Constraints**: Lists exactly what is allowed and what is not
- **Structured Output**: Clear format requirements for responses
- **Constant Validation**: Multiple validation steps at each stage

### **Zero Context Between API Calls**
- **Blank Slate**: Each API call starts fresh with no conversation history
- **No Memory**: Prevents context bleeding between different classification stages
- **Deterministic**: Uses temperature=0 and top_p=0 for consistent results

### **Multi-Layer Validation**
- **Stage 1**: Every returned L1 category is validated against the actual L1 list
- **Stage 2A/2B**: Every returned leaf category is validated against the filtered leaf list
- **Stage 3**: AI response is validated to be numeric and within valid range
- **All hallucinations are logged as CRITICAL errors with full context**

## ⚡ System Architecture Benefits

✅ **Efficiency**: Progressive filtering with smart optimizations
✅ **Cost Optimization**: 2-5 API calls per classification (adaptive)
✅ **Character Limits**: Strategic truncation focuses on essential information
✅ **Accuracy**: Each L1 taxonomy is explored independently
✅ **Scalability**: Handles large taxonomies without overwhelming the AI
✅ **Model Strategy**: Uses gpt-4.1-mini for critical stages (1&3), gpt-4.1-nano for efficiency (stage 2)
✅ **Smart Truncation**: Different character limits optimize each stage

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation
```bash
git clone https://github.com/your-repo/taxonomy-navigator.git
cd taxonomy-navigator
pip install -r requirements.txt
```

### Configuration
1. **API Key Setup** (choose one method):
   ```bash
   # Method 1: Environment variable
   export OPENAI_API_KEY="your-api-key-here"
   
   # Method 2: Create api_key.txt file
   echo "your-api-key-here" > data/api_key.txt
   ```

2. **Taxonomy File**: Place your taxonomy file at `data/taxonomy.en-US.txt`

Update classification settings in `config.yaml`:
```yaml
api:
  model_stage1: "gpt-4.1-nano"    # Fast model for initial categorization
  model_stage2: "gpt-4.1-nano"    # Fast model for leaf selection
  model_stage3: "gpt-4.1-mini"    # Better model for final decision
  temperature: 0                   # Deterministic (consistent) results
  
processing:
  stage1_categories: 2             # Number of L1 categories to select
  stage2_categories_per_l1: 15     # Number of leaves per L1 category
```

## 🎮 Try It Yourself!

### 1. Interactive Testing (Recommended for First-Time Users)
```bash
cd tests
python3 simple_batch_tester.py

# Enter number of products when prompted
# Watch the AI classify products step-by-step!
```

### 2. Command Line Classification
```bash
# Classify a single product
python3 src/taxonomy_navigator_engine.py \
  --product-name "iPhone 14" \
  --product-description "Smartphone with camera"

# See step-by-step AI decisions
python3 tests/simple_batch_tester.py --show-stage-paths
```

### 3. Python API
```python
from src.taxonomy_navigator_engine import TaxonomyNavigator

# Initialize with mixed model strategy
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    model="gpt-4.1-mini"  # For stages 1&3 (stage 2 uses gpt-4.1-nano automatically)
)

# Classify a product
product_info = "iPhone 14: Smartphone with camera and advanced features for photography"
paths, best_match_idx = navigator.navigate_taxonomy(product_info)

# Get the result
if paths == [["False"]]:
    print("Classification failed")
else:
    best_category = paths[best_match_idx][-1]
    print(f"Best match: {best_category}")
    print(f"Full path: {' > '.join(paths[best_match_idx])}")
```

## 🧪 Testing

### Simple Batch Testing
```bash
# Test with stage-by-stage display
cd tests
python simple_batch_tester.py --show-stage-paths

# Test specific products file
python simple_batch_tester.py --products-file my_products.txt

# Test with different model for stages 1&4
python simple_batch_tester.py --model gpt-4.1-mini
```

### Unit Tests
```bash
cd tests
python unit_tests.py
```

## 📊 Model Strategy

| Stage | Model | Purpose | Character Limit | Reasoning |
|-------|-------|---------|-----------------|-----------|
| 1 | `gpt-4.1-nano` | L1 taxonomy selection | 200 chars | Efficient model for broad categorization |
| 2A | `gpt-4.1-nano` | First L1 leaf selection | 500 chars | Efficient processing of filtered categories |
| 2B | `gpt-4.1-nano` | Second L1 leaf selection | 500 chars | Efficient processing of filtered categories |
| 3 | `gpt-4.1-mini` | Final selection | 400 chars | Enhanced model for critical final decision |

## 🔧 Configuration Options

### Model Configuration
- **Default**: `gpt-4.1-mini` for stages 1&3, `gpt-4.1-nano` for stage 2
- **Customizable**: Can specify different model for stages 1&3 via `--model` parameter
- **Stage 2 Model**: Always uses `gpt-4.1-nano` for efficiency

### Anti-Hallucination Settings
- **Professional Prompting**: Always enabled (cannot be disabled)
- **Zero Context**: Always enabled (cannot be disabled)
- **Validation**: Always enabled (cannot be disabled)
- **Bounds Checking**: Always enabled (cannot be disabled)

## 📈 Performance Characteristics

- **API Calls**: 2-5 per classification (adaptive based on complexity)
  - Minimum: 2 calls (1 L1 category → 1 leaf)
  - Typical: 4 calls (2 L1s → multiple leaves → final selection)
  - Maximum: 4 calls (2 L1s → 2x15 leaves → final selection)
- **Processing Time**: ~2-5 seconds per product (depending on complexity)
- **Accuracy**: High accuracy due to progressive filtering and anti-hallucination measures
- **Scalability**: Handles taxonomies with thousands of categories efficiently
- **Cost**: Optimized with mixed model strategy and conditional execution

## 🛡️ Error Handling

The system includes comprehensive error handling:
- **API Failures**: Graceful fallback mechanisms
- **Invalid Responses**: Robust parsing with multiple validation layers
- **Hallucinations**: Death penalty prompting + validation filtering
- **Complete Failures**: Returns "False" when classification is impossible
- **Edge Cases**: Handles empty inputs, malformed data, and network issues

## 📝 Output Format

### Success Case
```json
{
  "product_info": "iPhone 14: Smartphone with camera and advanced features for photography",
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

### Failure Case
```json
{
  "product_info": "Invalid product description",
  "best_match_index": 0,
  "matches": [
    {
      "category_path": "False",
      "full_path": "False",
      "leaf_category": "False"
    }
  ]
}
```

## 🔄 Recent Updates (v11.0)

- **Optimized Process**: Reduced to 2 L1 categories and stages 2A/2B only
- **Smart Truncation**: Different character limits for each stage (200/500/400)
- **Conditional Execution**: Stages 2B and 3 skipped when not needed
- **Increased Leaf Selection**: 15 leaves per stage (up from 10)
- **Adaptive API Calls**: 2-4 calls based on product complexity
- **Enhanced Efficiency**: Can complete simple products in just 2 API calls
- **Maintained Accuracy**: All validation and anti-hallucination measures preserved

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub or contact the development team.

