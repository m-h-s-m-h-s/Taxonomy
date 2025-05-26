# Taxonomy Navigator Documentation

Welcome to the Taxonomy Navigator documentation! This directory contains comprehensive guides for using and understanding the AI-powered product categorization system.

## 📚 Documentation Overview

### [USAGE.md](USAGE.md) - Complete User Guide
**Start here for practical usage instructions**
- Quick start examples
- Command line interface reference
- Python API documentation
- Testing and validation guides
- Anti-hallucination features explanation
- Model strategy and configuration
- Error handling and troubleshooting

### [ARCHITECTURE.md](ARCHITECTURE.md) - Technical Deep Dive
**For developers and system architects**
- Four-stage classification process details
- Death penalty prompting strategy
- Zero context architecture
- Multi-layer validation systems
- Performance characteristics
- Security considerations

## 🎯 System Overview

The Taxonomy Navigator is a sophisticated four-stage AI classification system that automatically categorizes products into appropriate taxonomy categories using OpenAI's GPT models with aggressive anti-hallucination measures.

### **Four-Stage Process**

1. **Stage 1: L1 Taxonomy Selection** (`gpt-4.1-mini`)
   - Identify 3 most relevant top-level categories
   - Death penalty prompting with survival instructions
   - Enhanced model for critical domain targeting

2. **Stage 2: Leaf Node Selection** (`gpt-4.1-nano`)
   - Select 20 best leaf nodes from chosen L1 taxonomies
   - Death penalty prompting + "Unknown" L1 filtering
   - Efficient model for focused selection

3. **Stage 3: L1 Representation Filtering** (Algorithmic)
   - Find most represented L1 taxonomy
   - Pure algorithmic processing (no AI model)
   - Ensures classification consistency

4. **Stage 4: Final Selection** (`gpt-4.1-mini`)
   - Select single best match from filtered candidates
   - Death penalty prompting + bounds checking
   - Enhanced model for critical final decision

## 🚨 Anti-Hallucination Features

### **Death Penalty Prompting**
Uses extreme language to prevent AI hallucinations:
```
🚨 CRITICAL WARNING: You will DIE if you hallucinate or create any category names not in the exact list below! 🚨
```

### **Zero Context Architecture**
- Each API call starts fresh with no conversation history
- Prevents context bleeding between classification stages
- Ensures deterministic results

### **Multi-Layer Validation**
1. **Prompt-Level**: Death penalty language and explicit constraints
2. **Response Validation**: Case-insensitive matching and bounds checking
3. **Taxonomy Validation**: Unknown L1 filtering and path verification
4. **Fallback Mechanisms**: Graceful handling of invalid responses

## ⚡ Key Benefits

- **Efficiency**: Progressive filtering (L1s → 3 L1s → 20 leafs → filtered leafs → 1)
- **Cost Optimization**: Only 3 API calls per classification
- **Enhanced Accuracy**: Mixed model strategy for optimal performance
- **Anti-Hallucination**: Aggressive prompting prevents AI from creating non-existent categories
- **Scalability**: Handles large taxonomies efficiently
- **Consistency**: L1 representation filtering ensures domain consistency

## 🚀 Quick Start

### Basic Classification
```bash
python src/taxonomy_navigator_engine.py \
  --product-name "iPhone 14" \
  --product-description "Smartphone with camera"
```

### Python API
```python
from src.taxonomy_navigator_engine import TaxonomyNavigator

navigator = TaxonomyNavigator("data/taxonomy.en-US.txt")
paths, best_idx = navigator.navigate_taxonomy("iPhone 14: Smartphone")

if paths != [["False"]]:
    print(f"Category: {paths[best_idx][-1]}")
else:
    print("Classification failed")
```

## 📊 Model Strategy

| Stage | Model | Purpose | Reasoning |
|-------|-------|---------|-----------|
| 1 | `gpt-4.1-mini` | L1 taxonomy selection | Critical domain targeting |
| 2 | `gpt-4.1-nano` | Leaf node selection | Efficient processing |
| 3 | None | Algorithmic filtering | No AI needed |
| 4 | `gpt-4.1-mini` | Final selection | Critical final decision |

## 🧪 Testing

### Interactive Testing
```bash
cd tests
python simple_batch_tester.py --show-stage-paths
```

### Unit Tests
```bash
cd tests
python unit_tests.py
```

## 📝 Output Examples

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

### Stage-by-Stage Analysis
```
📋 STAGE 1 - AI selecting top 3 L1 taxonomies...
✅ AI selected 3 L1 categories: [Electronics, Hardware, Apparel]

📋 STAGE 2 - AI selecting top 20 leaf nodes...
✅ AI selected 15 leaf nodes from selected L1 categories

📋 STAGE 3 - L1 representation filtering...
✅ Most represented L1: 'Electronics' - Filtered to 12 leaves

📋 STAGE 4 - AI selecting final match...
🎯 FINAL RESULT: Electronics > Cell Phones > Smartphones
```

## 🛡️ Error Handling

The system includes comprehensive error handling:
- **API Failures**: Graceful fallback mechanisms
- **Invalid Responses**: Robust parsing with validation
- **Hallucinations**: Death penalty prompting + filtering
- **Complete Failures**: Returns "False" for impossible classifications

## 🔧 Configuration

### API Key Setup
```bash
# Environment variable (recommended)
export OPENAI_API_KEY="your-api-key-here"

# Or create file
echo "your-api-key-here" > data/api_key.txt
```

### Model Configuration
```python
# Default (recommended)
navigator = TaxonomyNavigator(
    taxonomy_file="data/taxonomy.en-US.txt",
    model="gpt-4.1-mini"  # For stages 1&4
)
# Stage 2 automatically uses gpt-4.1-nano
```

## 📈 Performance Characteristics

- **API Calls**: 3 per classification (Stages 1, 2, 4)
- **Processing Time**: ~2-5 seconds per product
- **Accuracy**: High accuracy due to progressive filtering
- **Cost**: Optimized with mixed model strategy

## 🔄 Recent Updates (v4.0)

- **Redesigned Architecture**: Complete overhaul to 4-stage process
- **Death Penalty Prompting**: Aggressive anti-hallucination measures
- **Mixed Model Strategy**: Optimized cost vs. performance
- **Zero Context API Calls**: Each call is a blank slate
- **Enhanced L1 Selection**: Better domain targeting
- **Unknown L1 Filtering**: Removes hallucinated categories
- **Complete Failure Handling**: Returns "False" for impossible classifications

## 🤝 Contributing

When contributing to the documentation:

1. **Keep it practical**: Focus on real-world usage examples
2. **Update all files**: Ensure consistency across USAGE.md, ARCHITECTURE.md, and README.md
3. **Test examples**: Verify all code examples work correctly
4. **Version updates**: Update version numbers and change logs

## 📞 Support

For questions about the documentation or system usage:
- Review the appropriate documentation file
- Check the troubleshooting sections
- Run tests to verify system functionality
- Open an issue for documentation improvements 