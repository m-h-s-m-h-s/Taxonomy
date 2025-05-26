# Taxonomy Navigator - System Architecture

## Overview

The Taxonomy Navigator implements a sophisticated five-stage AI classification system designed to efficiently categorize products into appropriate taxonomy categories while preventing AI hallucinations through professional prompting strategies.

## Core Architecture Principles

### 🎯 Progressive Filtering Strategy
The system uses a progressive filtering approach that efficiently narrows down from thousands of categories to a single best match:
- **Stage 1**: L1s → 3 L1s (domain targeting)
- **Stage 2A**: First L1 → 10 leaves (focused selection)
- **Stage 2B**: Second L1 → 10 leaves (focused selection)
- **Stage 2C**: Third L1 → 10 leaves (focused selection)
- **Stage 3**: 30 leaves → 1 (final selection)

### 🚨 Anti-Hallucination First Design
Every AI interaction is designed with professional anti-hallucination measures:
- **Professional Prompting**: Clear instructions and constraints
- **Zero Context**: Each API call is a blank slate with no conversation history
- **Multi-Layer Validation**: Multiple validation steps to catch and filter hallucinations
- **Explicit Constraints**: Clear prohibitions and instructions

### ⚡ Mixed Model Strategy
Optimizes cost and performance by using different models for different stages:
- **Critical Stages (1&3)**: `gpt-4.1-mini` for enhanced accuracy
- **Efficiency Stages (2A/B/C)**: `gpt-4.1-nano` for cost-effective processing

## Five-Stage Classification Process

### Stage 1: L1 Taxonomy Selection (AI-Powered)

**Purpose**: Identify the 3 most relevant top-level taxonomy categories

**Technical Implementation**:
```python
def stage1_l1_selection(self, product_info: str) -> List[str]:
    # Extract unique L1 categories from taxonomy
    l1_categories = self._extract_unique_l1_categories()
    
    # Construct professional prompt
    prompt = self._build_professional_prompt_l1(product_info, l1_categories)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.model,  # gpt-4.1-mini
        messages=[
            {"role": "system", "content": "You are a product categorization assistant..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        top_p=0
    )
    
    # Parse and validate response
    return self._validate_and_deduplicate(response, l1_categories)
```

**Key Features**:
- **Model**: `gpt-4.1-mini` (enhanced model for critical domain targeting)
- **Input**: Product info + ALL unique L1 taxonomy categories
- **Output**: 3 validated L1 category names
- **Anti-Hallucination**: Professional prompting with explicit constraints
- **Validation**: Case-insensitive deduplication and taxonomy matching

### Stage 2A: First L1 Leaf Selection (AI-Powered)

**Purpose**: Select the first 10 best leaf nodes from the FIRST chosen L1 taxonomy

**Technical Implementation**:
```python
def stage2a_first_leaf_selection(self, product_info: str, selected_l1s: List[str]) -> List[str]:
    # Filter leaf nodes to first L1 category only
    filtered_leaves = self._filter_leaves_by_l1([selected_l1s[0]])
    
    # Create L1 context for each leaf
    category_list_with_context = [
        f"{leaf} (L1: {l1_category})" 
        for leaf in filtered_leaves
    ]
    
    # Construct professional prompt
    prompt = self._build_professional_prompt_leaves(product_info, category_list_with_context)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.stage2_model,  # gpt-4.1-nano
        messages=[
            {"role": "system", "content": "You are a product categorization assistant..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        top_p=0
    )
    
    # Parse, validate, and filter hallucinations
    validated = self._validate_categories(response, filtered_leaves)
    return self._filter_unknown_l1_categories(validated)
```

**Key Features**:
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + leaf nodes from FIRST selected L1 category
- **Output**: Up to 10 validated leaf node names
- **Anti-Hallucination**: Professional prompting + strict validation
- **Context**: Shows L1 taxonomy for each leaf to help AI understand relationships

### Stage 2B: Second L1 Leaf Selection (AI-Powered)

**Purpose**: Select the second 10 best leaf nodes from the SECOND chosen L1 taxonomy

**Technical Implementation**:
```python
def stage2b_second_leaf_selection(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str]) -> List[str]:
    # Filter leaf nodes to second L1 category only
    filtered_leaves = self._filter_leaves_by_l1([selected_l1s[1]])
    
    # Create L1 context for each leaf
    category_list_with_context = [
        f"{leaf} (L1: {l1_category})" 
        for leaf in filtered_leaves
    ]
    
    # Construct professional prompt
    prompt = self._build_professional_prompt_leaves(product_info, category_list_with_context)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.stage2_model,  # gpt-4.1-nano
        messages=[
            {"role": "system", "content": "You are a product categorization assistant..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        top_p=0
    )
    
    # Parse, validate, and filter hallucinations
    validated = self._validate_categories(response, filtered_leaves)
    return self._filter_unknown_l1_categories(validated)
```

**Key Features**:
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + leaf nodes from SECOND selected L1 category
- **Output**: Up to 10 validated leaf node names
- **Anti-Hallucination**: Professional prompting + strict validation
- **Context**: Shows L1 taxonomy for each leaf to help AI understand relationships

### Stage 2C: Third L1 Leaf Selection (AI-Powered)

**Purpose**: Select the third 10 best leaf nodes from the THIRD chosen L1 taxonomy

**Technical Implementation**:
```python
def stage2c_third_leaf_selection(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str]) -> List[str]:
    # Filter leaf nodes to third L1 category only
    filtered_leaves = self._filter_leaves_by_l1([selected_l1s[2]])
    
    # Create L1 context for each leaf
    category_list_with_context = [
        f"{leaf} (L1: {l1_category})" 
        for leaf in filtered_leaves
    ]
    
    # Construct professional prompt
    prompt = self._build_professional_prompt_leaves(product_info, category_list_with_context)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.stage2_model,  # gpt-4.1-nano
        messages=[
            {"role": "system", "content": "You are a product categorization assistant..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        top_p=0
    )
    
    # Parse, validate, and filter hallucinations
    validated = self._validate_categories(response, filtered_leaves)
    return self._filter_unknown_l1_categories(validated)
```

**Key Features**:
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: Product info + leaf nodes from THIRD selected L1 category
- **Output**: Up to 10 validated leaf node names
- **Anti-Hallucination**: Professional prompting + strict validation
- **Context**: Shows L1 taxonomy for each leaf to help AI understand relationships

### Stage 3: Final Selection (AI-Powered with Anti-Hallucination)

**Purpose**: Make the final decision from the combined 30 leaf nodes from Stages 2A, 2B, 2C

**Technical Implementation**:
```python
def stage3_final_selection(self, product_info: str, selected_leaves: List[str]) -> int:
    # Create numbered options
    numbered_options = [f"{i}. {leaf}" for i, leaf in enumerate(selected_leaves, 1)]
    
    # Construct professional prompt for number selection
    prompt = self._build_professional_prompt_final(product_info, numbered_options)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.stage3_model,  # gpt-4.1
        messages=[
            {"role": "system", "content": "You are a product categorization assistant..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,  # Deterministic selection
        top_p=1        # Allow full token distribution
    )
    
    # Parse number and validate bounds
    selected_index = self._parse_and_validate_number(response, len(selected_leaves))
    
    # Return -1 for complete failures (indicates "False")
    return selected_index if selected_index >= 0 else -1
```

**Key Features**:
- **Model**: `gpt-4.1` (enhanced model for critical final selection)
- **Input**: Product info + numbered list of filtered leaf nodes
- **Output**: Index of selected category (0-based) OR -1 for complete failure
- **Anti-Hallucination**: Professional prompting + robust bounds checking
- **Model Settings**: temperature=0 for deterministic selection, top_p=1 for full token distribution
- **Failure Handling**: Returns "False" when AI completely fails

## Anti-Hallucination Architecture

### Professional Prompting Strategy

**Core Philosophy**: Use clear, professional language to guide AI responses and prevent hallucinations.

**Implementation Pattern**:
```python
def _build_professional_prompt(self, task_description: str, valid_options: List[str]) -> str:
    return f"""
You are a product categorization assistant. Your task is to select categories from the provided list.

IMPORTANT CONSTRAINTS:
- You must select ONLY from the categories in the list below
- Use EXACT spelling, capitalization, and punctuation
- Return EXACTLY the requested number of categories
- One category per line, no numbering, no extra text

TASK: {task_description}

MANDATORY CATEGORY LIST (you MUST choose from these ONLY):
{chr(10).join(valid_options)}

Remember: Select ONLY from the categories listed above.
"""
```

### Zero Context Architecture

**Implementation**: Each API call starts fresh with no conversation history:
```python
# CORRECT: Zero context - each call is independent
response = self.client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0,
    top_p=0
)

# WRONG: Would carry context between calls
# conversation_history.append({"role": "user", "content": prompt})
```

### Multi-Layer Validation

**Layer 1: Prompt-Level Prevention**
- Professional language in prompts
- Explicit constraints
- Clear output format requirements

**Layer 2: Response Validation**
- Case-insensitive matching against valid options
- Bounds checking for numerical responses
- Format validation (e.g., single number vs. text)

**Layer 3: Taxonomy Validation**
- Stage 1: Every returned L1 category is validated against the actual L1 list
- Stage 2A/2B/2C: Every returned leaf category is validated against the filtered leaf list
- Stage 3: AI response is validated to be numeric and within valid range
- All hallucinations are logged as CRITICAL errors with full context

## Data Flow Architecture

```
Product Input
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: L1 TAXONOMY SELECTION (gpt-4.1-mini)              │
│ Input: Product + All L1 Categories                         │
│ Output: 3 L1 Categories                                     │
│ Anti-Hallucination: Professional Prompting + Validation     │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2A: FIRST L1 LEAF SELECTION (gpt-4.1-nano)            │
│ Input: Product + Leaves from FIRST L1                       │
│ Output: 10 Leaf Nodes                                      │
│ Anti-Hallucination: Professional Prompting + Validation     │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2B: SECOND L1 LEAF SELECTION (gpt-4.1-nano)           │
│ Input: Product + Leaves from SECOND L1                      │
│ Output: 10 Leaf Nodes                                     │
│ Anti-Hallucination: Professional Prompting + Validation     │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2C: THIRD L1 LEAF SELECTION (gpt-4.1-nano)            │
│ Input: Product + Leaves from THIRD L1                       │
│ Output: 10 Leaf Nodes                                      │
│ Anti-Hallucination: Professional Prompting + Validation     │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: FINAL SELECTION (gpt-4.1)                         │
│ Input: Product + Numbered Filtered Leaves                  │
│ Output: Index of Best Match OR -1 (False)                  │
│ Anti-Hallucination: Professional Prompting + Bounds Checking│
└─────────────────────────────────────────────────────────────┘
     ↓
Final Classification Result
```

## Performance Characteristics

### API Call Optimization
- **Total API Calls**: 3 per classification (Stages 1, 2A, 2B, 2C, 3)
- **Stage 3**: Pure algorithmic processing (0 API calls)
- **Cost Efficiency**: Mixed model strategy optimizes cost vs. performance

### Model Selection Rationale

| Stage | Model | Reasoning |
|-------|-------|-----------|
| 1 | `gpt-4.1-mini` | Critical domain targeting requires enhanced reasoning |
| 2A | `gpt-4.1-nano` | Efficient processing of pre-filtered categories |
| 2B | `gpt-4.1-nano` | Efficient processing of pre-filtered categories |
| 2C | `gpt-4.1-nano` | Efficient processing of pre-filtered categories |
| 3 | `gpt-4.1` | Enhanced model for critical final selection |

### Scalability Features
- **Progressive Filtering**: Reduces complexity at each stage
- **L1 Pre-filtering**: Stages 2A, 2B, 2C only process relevant categories
- **Algorithmic Stage 3**: No AI overhead for counting
- **Bounded Final Stage**: Stage 3 works with small, filtered set

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