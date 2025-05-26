# Taxonomy Navigator

A comprehensive AI-powered product categorization system that uses OpenAI's GPT models to automatically classify products into appropriate taxonomy categories.

## Overview

The Taxonomy Navigator implements a sophisticated **five-stage AI classification system** that efficiently processes products through large taxonomy structures. Unlike traditional hierarchical navigation, this system uses progressive filtering combined with AI refinement and validation to achieve maximum efficiency and accuracy.

## 🚀 **Key Features**

- **Five-Stage AI Classification**: Uses gpt-4.1-nano and gpt-4.1-nano with progressive filtering and validation
- **Leaf Node Matching**: Efficiently identifies the most relevant end categories first  
- **Layer Filtering**: Focuses on the most popular top-level taxonomy category
- **Refined Selection**: AI narrows down to top 10 candidates from filtered L1 taxonomy results
- **Validation**: Ensures AI didn't hallucinate any category names that don't exist
- **Enhanced Product Identification**: Advanced prompting to distinguish products from accessories
- **Deterministic Results**: Uses temperature=0 and top_p=0 for consistent classifications
- **Comprehensive Error Handling**: Graceful handling of API errors and edge cases
- **Simplified Interface Options**: Two focused scripts for all use cases
- **Secure API Key Management**: Multiple secure methods for API key configuration
- **Detailed Result Storage**: JSON output with complete classification metadata
- **Scalable Architecture**: Handles taxonomies with thousands of categories

## 🏗️ **Five-Stage Classification Process**

### **Stage 1: Initial Leaf Node Matching (gpt-4.1-nano)**
- AI selects top 20 most relevant leaf nodes from all 4,722 categories
- Enhanced prompting focuses on identifying the "core product being sold" vs accessories

### **Stage 2: Layer Filtering (Algorithmic)**
- Analyzes the 20 selected categories to find the most popular 1st-level taxonomy layer
- Filters results to only include categories from the dominant layer (e.g., "Electronics")
- Handles ties by including all categories from tied layers
- **No API calls** - purely algorithmic processing

### **Stage 3: Refined Selection (gpt-4.1-nano)**
- AI refines selection to top 10 most relevant categories from filtered L1 taxonomy candidates
- This is essentially Stage 1 repeated, but only with leaf nodes from the dominant L1 taxonomy layer
- Provides better focus for the validation and final selection stages
- Uses enhanced prompting focused on core product identification

### **Stage 4: Validation (Algorithmic)**
- Validates that all AI-selected category names actually exist in the taxonomy
- Removes any hallucinated or invalid category names
- Ensures data integrity before final selection
- **No API calls** - purely validation processing

### **Stage 5: Final Selection (gpt-4.1-nano)**
- AI selects the single best match from the validated candidates
- Uses enhanced model (gpt-4.1-nano) for better precision in final decision
- Structured prompting with 3-step reasoning process
- Focuses on distinguishing main products from accessories

