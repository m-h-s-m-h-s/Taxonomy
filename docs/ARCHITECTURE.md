# Taxonomy Navigator - System Architecture

## Overview

The Taxonomy Navigator implements a sophisticated AI classification system with intelligent product summarization and numeric selection designed to efficiently categorize products into appropriate taxonomy categories while preventing AI hallucinations through professional prompting strategies.

## Core Architecture Principles

### 🎯 Progressive Filtering Strategy
The system uses a progressive filtering approach that efficiently narrows down from thousands of categories to a single best match:
- **Preliminary**: AI Summarization (40-60 words)
- **Stage 1**: All L1s → 2 L1s (domain targeting)
- **Stage 2A**: First L1 → up to 15 per batch (e.g., 60+ possible)
- **Stage 2B**: Second L1 → up to 15 per batch (e.g., 150+ possible)
- **Stage 3**: All selected leaves → 1 (numeric final selection)

### 📝 AI-Powered Summarization
The system generates focused summaries optimized for categorization:
- **Category-First**: Summaries start with exact product type
- **Concise**: 40-60 words focusing on taxonomy-relevant details
- **Consistent**: Same summary used for stages 1 and 2

### 🔢 Numeric Selection (NEW in v12.3)
Eliminates misspelling issues through numeric selection:
- **Stage 2**: AI selects categories by number (e.g., "315" not "Televisions")
- **Stage 3**: Already uses numeric selection
- **Benefit**: 100% accurate category identification

### 📦 Batch Processing (NEW in v12.3, Enhanced in v12.4)
Handles large taxonomies efficiently:
- **Problem**: Important categories beyond position 100 were inaccessible
- **Solution**: Process categories in batches of 100
- **Example**: Electronics (339 categories) = 4 batches
- **v12.4 Enhancement**: Up to 15 selections per batch (was 15 total)
- **Result**: ALL categories accessible with comprehensive selection

### 🚨 Anti-Hallucination First Design
Every AI interaction is designed with professional anti-hallucination measures:
- **Professional Prompting**: Clear instructions and constraints
- **Zero Context**: Each API call is a blank slate with no conversation history
- **Numeric Validation**: Numbers eliminate spelling/naming errors
- **Explicit Constraints**: Clear prohibitions and instructions

### ⚡ Mixed Model Strategy
Optimizes cost and performance by using different models for different stages:
- **Summarization**: `gpt-4.1-nano` for efficient summary generation
- **Initial Stages (1&2)**: `gpt-4.1-nano` for cost-effective processing  
- **Final Stage (3)**: `gpt-4.1-mini` for critical final selection

## Classification Process with AI Summarization

### Preliminary Stage: AI Product Summarization

**Purpose**: Generate a focused 40-60 word summary optimized for categorization

**Technical Implementation**:
```python
def generate_product_summary(self, product_info: str) -> str:
    prompt = """Summarize this product in 40-60 words to make its category crystal clear:
1. START with exactly what type/category of product this is
2. Core function that defines its category (what makes it that type of product)
3. Key category-distinguishing features (what separates it from similar products)
4. Primary use context (home/office/outdoor/etc)

Focus on category-relevant details. Use clear product-type terminology.

Product: {product_info}

Summary:"""
    
    response = self.client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": "You are a product categorization assistant. Create summaries that make the product's category immediately obvious. Start with the specific product type and use clear category terminology."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        top_p=0,
        max_tokens=100
    )
    
    return response.choices[0].message.content.strip()
```

**Key Features**:
- **Model**: `gpt-4.1-nano` (efficient summarization)
- **Output**: 40-60 word category-focused summary
- **Focus**: Product type first, then category-defining features
- **Purpose**: Provides consistent input for stages 1 and 2

### Stage 1: L1 Taxonomy Selection (AI-Powered)

**Purpose**: Identify the 2 most relevant top-level taxonomy categories

**Key Features**:
- Uses AI-generated summary instead of truncated text
- Reduced from 3 to 2 L1 categories for efficiency
- Professional prompting with validation

### Stages 2A & 2B: Leaf Selection with Batch Processing (AI-Powered)

**Purpose**: Select up to 15 leaf nodes from each selected L1 taxonomy

**Technical Implementation (NEW in v12.3)**:
```python
def _leaf_selection_helper(self, product_info: str, selected_l1s: List[str], 
                          excluded_leaves: List[str], stage_name: str, 
                          description: str) -> List[str]:
    # Process in batches of 100 to handle large category lists
    batch_size = 100
    all_selected_numbers = []
    
    for batch_start in range(0, len(filtered_leaves), batch_size):
        batch_end = min(batch_start + batch_size, len(filtered_leaves))
        batch_leaves = filtered_leaves[batch_start:batch_end]
        
        # Create numbered list for this batch
        numbered_options = []
        leaf_mapping = {}  # Map batch numbers to leaf names
        for i, leaf in enumerate(batch_leaves, 1):
            numbered_options.append(f"{i}. {leaf} (L1: {l1_category})")
            leaf_mapping[i] = leaf
        
        prompt = f"""Product: {product_info}

Select any categories that match this product from the numbered list below.
Return ONLY the numbers of matching categories, one per line.
If no categories match, return 'NONE'.

Categories to choose from (batch {batch_start//batch_size + 1}):
{chr(10).join(numbered_options)}"""
        
        # AI selects by number, results combined across batches
```

**Key Improvements**:
- **Numeric Selection**: AI returns numbers instead of category names
- **Batch Processing**: All categories accessible, not just first 100
- **No Misspellings**: "315" instead of typing "Televisions"
- **Complete Coverage**: 900+ category taxonomies fully supported

### Stage 3: Final Selection (AI-Powered)

**Purpose**: Make the final decision from combined leaf nodes

**Key Features**:
- Uses AI-generated summary (same as stages 1-2) for consistency
- Already uses numeric selection (unchanged from v12.0)
- Conditional execution (skipped if only 1 leaf selected)

## Critical Bug Fixes in v12.0

### Leaf Node Detection Fix

**Problem**: Categories with subcategories were incorrectly marked as leaf nodes

**Root Cause**: The algorithm only checked the immediate next line in the taxonomy file:
```python
# OLD (BUGGY) CODE:
if next_line and next_line.startswith(line + " > "):
    is_leaf_node = False
```

**Solution**: Check ALL subsequent lines to properly identify parent categories:
```python
# NEW (FIXED) CODE:
# Check all remaining lines to see if any are children of this path
for j in range(i + 1, len(lines[1:])):
    subsequent_line = lines[j + 1].strip()
    if subsequent_line and subsequent_line.startswith(line + " > "):
        is_leaf_node = False
        break  # Found a child, no need to check further
```

**Impact**: Ensures only true end categories are presented for selection, significantly improving accuracy

## Data Flow Architecture with Summarization and Batch Processing

```
Product Input
     ↓
┌─────────────────────────────────────────────────────────────┐
│ PRELIMINARY: AI SUMMARIZATION (gpt-4.1-nano)                │
│ Input: Full Product Description                             │
│ Output: 40-60 word category-focused summary with synonyms  │
│ Focus: Product type + category-relevant features            │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: L1 TAXONOMY SELECTION (gpt-4.1-nano)              │
│ Input: AI Summary + All L1 Categories                      │
│ Output: 2 L1 Categories                                    │
│ Anti-Hallucination: Professional Prompting + Validation     │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2A: FIRST L1 LEAF SELECTION (gpt-4.1-nano)           │
│ Input: AI Summary + Leaves from FIRST L1                   │
│ Process: Batch processing (100 per batch) + Numeric selection│
│ Output: Up to 15 per batch (e.g., 60+ leaves possible)     │
│ Example: Electronics (339) = 4 batches × 15 = 60 max       │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2B: SECOND L1 LEAF SELECTION (gpt-4.1-nano)          │
│ Input: AI Summary + Leaves from SECOND L1                  │
│ Process: Same batch processing + numeric selection          │
│ Output: Up to 15 per batch (combined with 2A results)      │
│ Condition: SKIPPED if only 1 L1 selected in Stage 1        │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: FINAL SELECTION (gpt-4.1-mini)                    │
│ Input: AI Summary + Combined Leaves from 2A & 2B           │
│ Process: Select best match from numbered options           │
│ Output: Single best category (index)                       │
│ Condition: SKIPPED if only 1 leaf selected in Stage 2      │
│ Anti-Hallucination: Numeric selection + bounds checking    │
└─────────────────────────────────────────────────────────────┘
     ↓
Final Category Path
```

## Performance Characteristics

### API Call Optimization
- **Total API Calls**: Variable based on taxonomy size
  - Summarization: 1 call
  - Stage 1: 1 call
  - Stage 2A: 1-10 calls (depends on batch count)
  - Stage 2B: 1-10 calls (conditional, depends on batch count)
  - Stage 3: 1 call (conditional)
- **Minimum**: 3 calls (1 L1 → 1 leaf)
- **Typical**: 5-7 calls (2 L1s → multiple batches → final)
- **Maximum**: 20+ calls (large taxonomies like Home & Garden with 900+ categories)

### Batch Processing Examples
| L1 Category | Total Categories | Batches | API Calls |
|-------------|-----------------|---------|-----------|
| Electronics | 339 | 4 | 4 |
| Hardware | 451 | 5 | 5 |
| Home & Garden | 903 | 10 | 10 |
| Apparel | 150 | 2 | 2 |

### Model Selection Rationale

| Stage | Model | Reasoning | Key Feature |
|-------|-------|-----------|-------------|
| Summary | `gpt-4.1-nano` | Efficient extraction of category-relevant details | 40-60 words with synonyms |
| 1 | `gpt-4.1-nano` | Cost-effective L1 selection with summary context | Text selection |
| 2A/2B | `gpt-4.1-nano` | Efficient batch processing with numeric selection | Number selection |
| 3 | `gpt-4.1-mini` | Balanced accuracy/cost for final selection | Number selection |

## Future Architecture Considerations

### Potential Enhancements
- **Dynamic Summary Length**: Adjust summary length based on product complexity
- **Category-Specific Prompts**: Tailor summarization for different product types
- **Confidence Scoring**: Add confidence metrics to classifications
- **Batch Summarization**: Optimize for multiple product processing

### Monitoring and Analytics
- **Summary Quality Tracking**: Monitor how well summaries capture category essence
- **Classification Accuracy**: Compare pre/post summarization accuracy
- **Token Usage Analysis**: Track cost optimization from summarization
- **Performance Profiling**: Measure time savings from conditional execution

## Error Handling Architecture

### Graceful Degradation Strategy
1. **API Failures**: Fallback to safe defaults
2. **Invalid Responses**: Multiple parsing attempts
3. **Hallucinations**: Validation filtering
4. **Complete Failures**: Return "False" classification

### Logging and Monitoring
- **Stage-by-stage logging**: Track progress through pipeline
- **Validation statistics**: Monitor hallucination detection rates
- **Performance metrics**: Track API call times and success rates
- **Error categorization**: Classify failure types for analysis

## Security Considerations

### Input Validation
- **Product Info Sanitization**: Clean input before processing
- **Taxonomy File Validation**: Verify file format and content
- **API Key Protection**: Secure storage and access patterns

### Output Validation
- **Result Verification**: Ensure outputs match expected formats
- **Path Validation**: Verify taxonomy paths exist in source data
- **Bounds Checking**: Validate all indices and array accesses

## Future Architecture Considerations

### Potential Enhancements
- **Caching Layer**: Cache L1 mappings and common classifications
- **Batch Processing**: Optimize for multiple product classifications
- **Model Fine-tuning**: Custom models trained on taxonomy data
- **Confidence Scoring**: Add confidence metrics to classifications

### Monitoring and Analytics
- **Classification Accuracy Tracking**: Monitor real-world performance
- **Hallucination Rate Analysis**: Track anti-hallucination effectiveness
- **Cost Optimization**: Monitor API usage and optimize model selection
- **Performance Profiling**: Identify bottlenecks and optimization opportunities 