# Product Summary Concept - Alternative Approach

## Overview

Instead of truncating product descriptions at different stages, we could use a **preliminary summarization stage** to create a standardized, optimized product summary that all subsequent stages would use.

## Proposed Architecture

### Stage 0: Product Summarization (NEW)
- **Model**: `gpt-4.1-nano` (efficient for summarization)
- **Input**: Full product description (no truncation)
- **Prompt**: "Summarize this product in 100-150 words, focusing on: product type, main purpose, key features, and category-relevant details"
- **Output**: Standardized product summary
- **Benefits**:
  - Consistent information across all stages
  - AI extracts most relevant details upfront
  - Removes marketing fluff automatically
  - Could actually reduce total tokens across all stages

### Modified Classification Stages

1. **Stage 1**: L1 Selection
   - Uses the AI-generated summary
   - No additional truncation needed

2. **Stage 2A/2B**: Leaf Selection
   - Uses the same AI-generated summary
   - Consistent information for both L1 branches

3. **Stage 3**: Final Selection
   - Uses the same AI-generated summary
   - All stages work with the same optimized text

## Advantages

1. **Better Information Quality**: AI can identify and extract the most relevant details
2. **Consistency**: All stages see the same information
3. **Token Efficiency**: A 150-word summary might be more efficient than truncating at different lengths
4. **Removes Bias**: No arbitrary cutoff points that might miss important details
5. **Handles Various Formats**: Works well with poorly structured descriptions

## Disadvantages

1. **Extra API Call**: Adds one more stage (but might save tokens overall)
2. **Potential Information Loss**: Summary might miss nuanced details
3. **Added Latency**: One more round-trip to the API

## Example Implementation

```python
def generate_product_summary(self, product_info: str) -> str:
    """
    Generate a standardized product summary for classification.
    """
    prompt = """
    Summarize this product in 100-150 words, focusing on:
    - What type of product it is
    - Its main purpose or function
    - Key features or specifications
    - Brand and model (if mentioned)
    
    Product: {product_info}
    
    Summary:
    """
    
    response = self.client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "You are a product summarization assistant."},
            {"role": "user", "content": prompt.format(product_info=product_info)}
        ],
        temperature=0,
        max_tokens=200
    )
    
    return response.choices[0].message.content.strip()
```

## Cost Analysis

**Current Approach (with truncation):**
- Stage 1: 200 chars ≈ 50 tokens
- Stage 2A: 500 chars ≈ 125 tokens  
- Stage 2B: 500 chars ≈ 125 tokens
- Stage 3: 400 chars ≈ 100 tokens
- **Total**: ~400 tokens across stages

**Summary Approach:**
- Stage 0: Full description input + 150-word output ≈ 300-500 tokens
- Stages 1-3: Each uses 150-word summary ≈ 40 tokens × 4 = 160 tokens
- **Total**: ~460-660 tokens

The summary approach might use slightly more tokens but provides better information quality.

## Recommendation

This approach could be particularly valuable for:
- Long, detailed product descriptions
- Poorly structured product data
- Products with lots of marketing language
- When consistency across stages is critical

It might be worth implementing as an optional mode that users can enable based on their specific needs. 