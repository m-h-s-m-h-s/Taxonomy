# Taxonomy Navigator - AI-Powered Product Categorization System

An intelligent, five-stage AI classification system that automatically categorizes products into appropriate taxonomy categories using OpenAI's GPT models with aggressive anti-hallucination measures.

## 🎯 System Overview

The Taxonomy Navigator uses a sophisticated five-stage progressive filtering approach that efficiently narrows down from thousands of categories to a single best match:

### **Five-Stage Classification Process**

🎯 **STAGE 1: L1 TAXONOMY SELECTION** (AI-Powered)
- **Purpose**: Identify the 3 most relevant top-level taxonomy categories
- **Model**: `gpt-4.1-mini` (enhanced model for critical L1 selection)
- **Input**: Product info + ALL unique L1 taxonomy categories (no duplicates)
- **Process**: AI selects 3 most relevant L1 categories (e.g., "Electronics", "Food, Beverages & Tobacco", "Apparel & Accessories")
- **Output**: List of 3 L1 category names
- **Anti-Hallucination**: Professional prompting with explicit constraints

🔍 **STAGE 2A: FIRST L1 LEAF SELECTION** (AI-Powered)
- **Purpose**: Select the first 10 best leaf nodes from the FIRST chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + ALL leaf nodes from the FIRST selected L1 category
- **Process**: AI selects top 10 most relevant leaf categories from the FIRST L1 taxonomy
- **Output**: List of up to 10 leaf node names from the FIRST L1 taxonomy
- **Anti-Hallucination**: Professional prompting + strict validation

🔍 **STAGE 2B: SECOND L1 LEAF SELECTION** (AI-Powered)
- **Purpose**: Select the second 10 best leaf nodes from the SECOND chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + ALL leaf nodes from the SECOND selected L1 category
- **Process**: AI selects top 10 most relevant leaf categories from the SECOND L1 taxonomy
- **Output**: List of up to 10 leaf node names from the SECOND L1 taxonomy
- **Anti-Hallucination**: Professional prompting + strict validation

🔍 **STAGE 2C: THIRD L1 LEAF SELECTION** (AI-Powered)
- **Purpose**: Select the third 10 best leaf nodes from the THIRD chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + ALL leaf nodes from the THIRD selected L1 category
- **Process**: AI selects top 10 most relevant leaf categories from the THIRD L1 taxonomy
- **Output**: List of up to 10 leaf node names from the THIRD L1 taxonomy
- **Anti-Hallucination**: Professional prompting + strict validation

🏆 **STAGE 3: FINAL SELECTION** (AI-Powered with Anti-Hallucination)
- **Purpose**: Make the final decision from the combined 30 leaf nodes from Stages 2A, 2B, 2C
- **Model**: `gpt-4.1-mini` (enhanced model for critical final selection)
- **Input**: Product info + up to 30 leaf nodes from combined Stage 2 results
- **Process**: 
  * Construct clear, professional prompt with specific constraints
  * Present up to 30 categories as numbered options (leaf names only)
  * AI identifies core product and selects best match
  * Parse AI response with robust validation and bounds checking
- **Output**: Index of selected category (0-based, guaranteed valid) OR -1 for complete failure
- **Anti-Hallucination**: Professional prompting + numeric validation + bounds checking + "False" for failures

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
- **Stage 2A/2B/2C**: Every returned leaf category is validated against the filtered leaf list
- **Stage 3**: AI response is validated to be numeric and within valid range
- **All hallucinations are logged as CRITICAL errors with full context**

## ⚡ System Architecture Benefits

✅ **Efficiency**: Progressive filtering (L1s → 3 L1s → 10 leaves per L1 → 30 leaves → 1)
✅ **Cost Optimization**: Only 5 API calls per classification (Stages 1, 2A, 2B, 2C, 3)
✅ **Improved Focus**: Each stage focuses on appropriate level of granularity
✅ **Accuracy**: Each L1 taxonomy is explored independently for better coverage
✅ **Scalability**: Handles large taxonomies without overwhelming the AI
✅ **Model Strategy**: Uses gpt-4.1-mini for critical stages (1&3), gpt-4.1-nano for efficiency (stage 2)
✅ **Manageable Chunks**: Stage 2 broken into 3 parts of 10 items each for better AI performance

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
| 2A | `gpt-4.1-nano` | First L1 leaf selection | Efficient processing of filtered categories |
| 2B | `gpt-4.1-nano` | Second L1 leaf selection | Efficient processing of filtered categories |
| 2C | `gpt-4.1-nano` | Third L1 leaf selection | Efficient processing of filtered categories |
| 3 | `gpt-4.1-mini` | Final selection | Critical final decision requires enhanced model |

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

- **API Calls**: 5 per classification (Stages 1, 2A, 2B, 2C, 3)
- **Processing Time**: ~3-7 seconds per product (depending on model response time)
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

