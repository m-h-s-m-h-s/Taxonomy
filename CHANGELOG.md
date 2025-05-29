# Changelog

All notable changes to the Taxonomy Navigator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [12.5] - 2025-01-29

### Changed
- **Stage 3 Model**: Now uses `gpt-4.1-mini` for balanced accuracy and cost
  - Provides strong accuracy for the critical final selection
  - Better cost efficiency than gpt-4.1 while maintaining quality
  - Cost: ~$0.0005 per Stage 3 call (vs ~$0.002 for gpt-4.1)

- **Enhanced Summary Generation**: AI now includes synonyms and alternative names
  - Format: "Television (TV, flat-screen display). Electronic device..."
  - Helps clarify product types with multiple common names
  - Improves category matching by providing alternative terms
  - Example: "Smartphone (mobile phone, cell phone)" helps match various category naming conventions

- **Stage 3 Now Uses Summary**: All stages now use the same AI-generated summary
  - Previously: Stages 1-2 used summary, Stage 3 used full description
  - Now: All stages use the 40-60 word summary with synonyms
  - Benefits: More consistent classification, faster processing, same context across all stages
  - Trade-off: Potentially less nuance in final selection, but more predictable results

### Impact
- Strong accuracy in final category selection with better cost efficiency
- Better disambiguation between similar categories
- More reliable handling of edge cases and complex products
- Improved category matching through synonym inclusion
- More consistent classification behavior across all stages

## [12.4] - 2025-01-29

### Changed
- **Stage 2 Batch Limits**: Now allows up to 15 selections PER BATCH instead of 15 total
  - Previous: 15 total across all batches (limiting for large taxonomies)
  - New: 15 per batch (e.g., 4 batches = up to 60 selections possible)
  - Electronics example: 4 batches × 15 = up to 60 leaves
  - Home & Garden example: 10 batches × 15 = up to 150 leaves
  - Provides much better coverage for products that match many categories

### Impact
- More comprehensive category selection for complex products
- Better handling of products that fit multiple subcategories
- Stage 3 now handles larger candidate sets (60-150+ instead of max 30)

## [12.3] - 2025-01-29

### Added
- **Numeric Selection in Stage 2**: AI now selects categories by number instead of typing names
  - Eliminates misspelling issues (e.g., "Television" vs "Televisions")
  - 100% accurate category identification
  - Consistent with Stage 3's existing numeric approach

- **Batch Processing for Large Taxonomies**: Categories processed in batches of 100
  - Solves issue where categories beyond position 100 were inaccessible
  - Example: "Televisions" at position 315 in Electronics now reachable
  - Handles taxonomies with 900+ categories (e.g., Home & Garden)
  - Processes all batches and combines results (limited to 15 total)

### Changed
- Stage 2 prompt format now presents numbered options like Stage 3
- System prompts updated to instruct AI to return only numbers
- API call count now varies based on taxonomy size (3-20+ calls possible)

### Fixed
- Important categories in large taxonomies (like "Televisions") now accessible
- No more hallucination errors from misspelled category names

## [12.2] - 2025-01-29

### Added
- Enhanced Stage 2 prompts with specific examples
  - "A TV should be 'Televisions' not 'TV Mounts'"
  - "A laptop should be 'Laptops' not 'Laptop Cases'"
- Explicit main product vs accessory guidance in prompts

### Fixed
- Improved distinction between main products and accessories
- TVs now correctly classified as "Televisions" instead of "Home Theater Systems"
- Better handling of product/accessory ambiguity

## [12.1] - 2025-01-29

### Added
- Explicit prompt guidance for choosing main products over accessories
- Warning about accessory categories in Stage 2 prompts

### Fixed
- Circular saws correctly classified as "Handheld Circular Saws" not "Handheld Circular Saw Accessories"

## [12.0] - 2025-01-25

### Added
- **AI-Powered Product Summarization**: 40-60 word summaries for stages 1-2
  - Category-focused summaries starting with exact product type
  - Removes marketing language and irrelevant details
  - Consistent input for initial categorization stages

### Changed
- Stage 1 and 2 now use AI-generated summaries instead of truncated text
- Stage 3 now also uses AI-generated summaries for consistency
- Model strategy: gpt-4.1-nano for summary/stages 1-2, gpt-4.1-mini for stage 3
- Removed character truncation limits

### Fixed
- **Critical Leaf Detection Bug**: Categories with subcategories were incorrectly marked as leaves
  - Old algorithm only checked immediate next line
  - Now checks ALL subsequent lines to identify true leaf nodes
  - Significantly improves classification accuracy

### Performance
- API calls: 3-5 per classification (summary + stages)
- Processing time: ~3-5 seconds per product

## [11.0] - 2025-01-24

### Added
- Initial multi-stage classification system
- Progressive filtering from thousands to one category
- Anti-hallucination measures

### Features
- 3 L1 categories selection in Stage 1
- 10 leaves per L1 in Stage 2 (2A, 2B, 2C)
- Character truncation for different stages
- Professional prompting strategies
- Zero context between API calls

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/taxonomy-navigator.git
cd taxonomy-navigator

# Install dependencies
pip install -r requirements.txt

# Set up API key
export OPENAI_API_KEY="your-api-key-here"
# OR
echo "your-api-key-here" > data/api_key.txt
```

## Quick Test

```bash
# Test with the latest improvements
cd tests
python3 simple_batch_tester.py

# When prompted, enter number of products (e.g., 3)
# Watch the classification process with numeric selection
```

## Key Features in v12.3

1. **No More Misspellings**: AI selects by number (e.g., "315") not text
2. **Complete Coverage**: All categories accessible through batch processing
3. **Efficient**: Still limits to 15 selections total across all batches
4. **Accurate**: Combines AI summarization with numeric selection

## Migration Notes

### From v12.2 to v12.3
- No code changes required
- API usage may increase for large taxonomies due to batch processing
- Classification accuracy improved for products in large categories

### From v11.x to v12.x
- Character truncation removed in favor of AI summarization
- API calls increased by 1 (for summary generation)
- Significantly improved accuracy with category-focused summaries 