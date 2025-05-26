# Taxonomy Navigator - AI-Powered Product Categorization System

An intelligent, four-stage AI classification system that automatically categorizes products into appropriate taxonomy categories using OpenAI's GPT models with aggressive anti-hallucination measures.

## 🎯 System Overview

The Taxonomy Navigator uses a sophisticated four-stage progressive filtering approach that efficiently narrows down from thousands of categories to a single best match:

### **Four-Stage Classification Process**

🎯 **STAGE 1: L1 TAXONOMY SELECTION** (AI-Powered)
- **Purpose**: Identify the 3 most relevant top-level taxonomy categories
- **Model**: `gpt-4.1-mini` (enhanced model for critical L1 selection)
- **Input**: Product info + ALL unique L1 taxonomy categories (no duplicates)
- **Process**: AI selects 3 most relevant L1 categories (e.g., "Electronics", "Food, Beverages & Tobacco", "Apparel & Accessories")
- **Output**: List of 3 L1 category names
- **Anti-Hallucination**: Death penalty prompting with explicit survival instructions

🔍 **STAGE 2: LEAF NODE SELECTION** (AI-Powered)
- **Purpose**: Select the best leaf nodes from the chosen L1 taxonomies
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + ALL leaf nodes from the 3 selected L1 categories
- **Process**: AI selects top 20 most relevant leaf categories from the filtered set
- **Output**: List of 20 leaf node names from the selected L1 taxonomies
- **Anti-Hallucination**: Death penalty prompting + "Unknown" L1 filtering

📊 **STAGE 3: L1 REPRESENTATION FILTERING** (Algorithmic)
- **Purpose**: Identify which L1 taxonomy is most represented in the leaf selections
- **Process**: 
  * Map each leaf to its L1 taxonomy category
  * Count occurrences of each L1 category
  * Keep only leaves from the most represented L1 taxonomy
- **Output**: Filtered list of leaf nodes from the dominant L1 taxonomy
- **Cost**: No API calls - purely algorithmic processing

🏆 **STAGE 4: FINAL SELECTION** (AI-Powered with Anti-Hallucination)
- **Purpose**: Make the final decision from the most represented L1 taxonomy leaves
- **Model**: `gpt-4.1-mini` (enhanced model for critical final selection)
- **Input**: Product info + filtered leaf nodes from Stage 3
- **Process**: 
  * Construct death penalty prompt with explicit constraints
  * Present filtered categories as numbered options (leaf names only)
  * AI identifies core product and selects best match
  * Parse AI response with robust validation and bounds checking
- **Output**: Index of selected category (0-based, guaranteed valid) OR -1 for complete failure
- **Anti-Hallucination**: Death penalty prompting + robust validation + "False" for failures

## 🚨 Anti-Hallucination Measures

### **Death Penalty Prompting Strategy**
- **Extreme Language**: Uses phrases like "You will DIE if you hallucinate" to make consequences crystal clear
- **Explicit Prohibitions**: Lists exactly what will cause "death" (hallucinations, modifications, creativity)
- **Survival Instructions**: Clear, positive instructions on exactly what to do to "survive"
- **Constant Reminders**: Reinforces the death penalty throughout each prompt

### **Zero Context Between API Calls**
- **Blank Slate**: Each API call starts fresh with no conversation history
- **No Memory**: Prevents context bleeding between different classification stages
- **Deterministic**: Uses temperature=0 and top_p=0 for consistent results

### **Multi-Layer Validation**
- **Unknown L1 Filtering**: Stage 2 removes categories with "Unknown" L1 taxonomy
- **Bounds Checking**: Stage 4 validates AI selections are within valid ranges
- **Fallback Mechanisms**: Graceful handling of invalid AI responses
- **Complete Failure Handling**: Returns "False" when AI completely fails

## ⚡ System Architecture Benefits

✅ **Efficiency**: Progressive filtering (L1s → 3 L1s → leafs from 3 L1s → 20 leafs → most represented L1 → 1)
✅ **Cost Optimization**: Only 3 API calls per classification (Stages 1, 2, 4)
✅ **Improved Focus**: Stage 1 L1 selection provides better domain targeting
✅ **Accuracy**: Each stage focuses on appropriate level of granularity
✅ **Consistency**: L1 representation filtering ensures results stay within same domain
✅ **Scalability**: Handles large taxonomies without overwhelming the AI
✅ **Model Strategy**: Uses gpt-4.1-mini for critical stages (1&4), gpt-4.1-nano for efficiency (stage 2)
✅ **Anti-Hallucination**: Death penalty prompting prevents AI from creating non-existent categories

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

## 🚀 Usage

### Command Line Interface
```bash
# Basic classification
python src/taxonomy_navigator_engine.py \
  --product-name "iPhone 14" \
  --product-description "Smartphone with camera"

# With custom model for stages 1&4
python src/taxonomy_navigator_engine.py \
  --product-name "Xbox Controller" \
  --product-description "Wireless gaming controller" \
  --model gpt-4.1-mini

# Verbose logging
python src/taxonomy_navigator_engine.py \
  --product-name "Nike Air Max" \
  --product-description "Athletic running shoes" \
  --verbose
```

### Python API
```python
from src.taxonomy_navigator_engine import TaxonomyNavigator

# Initialize with mixed model strategy
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    model="gpt-4.1-mini"  # For stages 1&4 (stage 2 uses gpt-4.1-nano automatically)
)

# Classify a product
product_info = "iPhone 14: Smartphone with camera"
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

| Stage | Model | Purpose | Reasoning |
|-------|-------|---------|-----------|
| 1 | `gpt-4.1-mini` | L1 taxonomy selection | Critical domain targeting requires enhanced model |
| 2 | `gpt-4.1-nano` | Leaf node selection | Efficient processing of filtered categories |
| 3 | None (Algorithmic) | L1 representation filtering | No AI needed for counting |
| 4 | `gpt-4.1-mini` | Final selection | Critical final decision requires enhanced model |

## 🔧 Configuration Options

### Model Configuration
- **Default**: `gpt-4.1-mini` for stages 1&4, `gpt-4.1-nano` for stage 2
- **Customizable**: Can specify different model for stages 1&4 via `--model` parameter
- **Stage 2 Model**: Always uses `gpt-4.1-nano` for efficiency

### Anti-Hallucination Settings
- **Death Penalty Prompting**: Always enabled (cannot be disabled)
- **Zero Context**: Always enabled (cannot be disabled)
- **Unknown L1 Filtering**: Always enabled (cannot be disabled)
- **Bounds Checking**: Always enabled (cannot be disabled)

## 📈 Performance Characteristics

- **API Calls**: 3 per classification (Stages 1, 2, 4)
- **Processing Time**: ~2-5 seconds per product (depending on model response time)
- **Accuracy**: High accuracy due to progressive filtering and anti-hallucination measures
- **Scalability**: Handles taxonomies with thousands of categories efficiently
- **Cost**: Optimized with mixed model strategy (mini for critical stages, nano for efficiency)

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

## 🔄 Recent Updates (v4.0)

- **Redesigned Architecture**: Complete overhaul to 4-stage process
- **Death Penalty Prompting**: Aggressive anti-hallucination measures
- **Mixed Model Strategy**: gpt-4.1-mini for critical stages, gpt-4.1-nano for efficiency
- **Zero Context API Calls**: Each call is a blank slate
- **Enhanced L1 Selection**: Stage 1 focuses on domain targeting
- **Unknown L1 Filtering**: Stage 2 removes hallucinated categories
- **Robust Validation**: Multiple layers of anti-hallucination protection
- **Complete Failure Handling**: Returns "False" for impossible classifications

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

