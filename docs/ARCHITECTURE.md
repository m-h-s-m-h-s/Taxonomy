# Taxonomy Navigator - System Architecture

## Overview

The Taxonomy Navigator implements a sophisticated four-stage AI classification system designed to efficiently categorize products into appropriate taxonomy categories while preventing AI hallucinations through aggressive prompting strategies.

## Core Architecture Principles

### 🎯 Progressive Filtering Strategy
The system uses a progressive filtering approach that efficiently narrows down from thousands of categories to a single best match:
- **Stage 1**: L1s → 3 L1s (domain targeting)
- **Stage 2**: 3 L1s → leafs from 3 L1s → 20 leafs (focused selection)
- **Stage 3**: 20 leafs → most represented L1 → filtered leafs (algorithmic consistency)
- **Stage 4**: filtered leafs → 1 (final selection)

### 🚨 Anti-Hallucination First Design
Every AI interaction is designed with aggressive anti-hallucination measures:
- **Death Penalty Prompting**: Extreme language threatening "death" for hallucinations
- **Zero Context**: Each API call is a blank slate with no conversation history
- **Multi-Layer Validation**: Multiple validation steps to catch and filter hallucinations
- **Explicit Constraints**: Clear prohibitions and survival instructions

### ⚡ Mixed Model Strategy
Optimizes cost and performance by using different models for different stages:
- **Critical Stages (1&4)**: `gpt-4.1-mini` for enhanced accuracy
- **Efficiency Stage (2)**: `gpt-4.1-nano` for cost-effective processing
- **Algorithmic Stage (3)**: No AI model needed

## Four-Stage Classification Process

### Stage 1: L1 Taxonomy Selection (AI-Powered)

**Purpose**: Identify the 3 most relevant top-level taxonomy categories

**Technical Implementation**:
```python
def stage1_l1_selection(self, product_info: str) -> List[str]:
    # Extract unique L1 categories from taxonomy
    l1_categories = self._extract_unique_l1_categories()
    
    # Construct death penalty prompt
    prompt = self._build_death_penalty_prompt_l1(product_info, l1_categories)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.model,  # gpt-4.1-mini
        messages=[
            {"role": "system", "content": "🚨 DEATH PENALTY SYSTEM 🚨..."},
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
- **Anti-Hallucination**: Death penalty prompting with explicit survival instructions
- **Validation**: Case-insensitive deduplication and taxonomy matching

### Stage 2: Leaf Node Selection (AI-Powered)

**Purpose**: Select the best leaf nodes from the chosen L1 taxonomies

**Technical Implementation**:
```python
def stage2_leaf_selection(self, product_info: str, selected_l1s: List[str]) -> List[str]:
    # Filter leaf nodes to selected L1 categories only
    filtered_leaves = self._filter_leaves_by_l1(selected_l1s)
    
    # Create L1 context for each leaf
    category_list_with_context = [
        f"{leaf} (L1: {l1_category})" 
        for leaf in filtered_leaves
    ]
    
    # Construct death penalty prompt
    prompt = self._build_death_penalty_prompt_leaves(product_info, category_list_with_context)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.stage2_model,  # gpt-4.1-nano
        messages=[
            {"role": "system", "content": "🚨 DEATH PENALTY SYSTEM 🚨..."},
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
- **Input**: Product info + leaf nodes from 3 selected L1 categories with L1 context
- **Output**: Up to 20 validated leaf node names
- **Anti-Hallucination**: Death penalty prompting + "Unknown" L1 filtering
- **Context**: Shows L1 taxonomy for each leaf to help AI understand relationships

### Stage 3: L1 Representation Filtering (Algorithmic)

**Purpose**: Identify which L1 taxonomy is most represented in the leaf selections

**Technical Implementation**:
```python
def stage3_l1_representation_filtering(self, selected_leaves: List[str]) -> List[str]:
    # Map leaves to their L1 categories
    leaf_to_l1 = self._create_leaf_to_l1_mapping()
    
    # Count L1 category occurrences
    l1_counts = Counter()
for leaf in selected_leaves:
        l1_category = leaf_to_l1.get(leaf, "Unknown")
        l1_counts[l1_category] += 1

    # Find most represented L1 category
    most_represented_l1 = l1_counts.most_common(1)[0][0]

    # Filter to only leaves from most represented L1
filtered_leaves = [
    leaf for leaf in selected_leaves 
        if leaf_to_l1.get(leaf, "Unknown") == most_represented_l1
    ]
    
    return filtered_leaves
```

**Key Features**:
- **Processing**: Pure algorithmic processing (no AI model)
- **Input**: 20 leaf nodes from Stage 2
- **Output**: Filtered leaf nodes from the dominant L1 taxonomy
- **Logic**: Ensures classification consistency within the same domain
- **Cost**: Zero API calls

### Stage 4: Final Selection (AI-Powered with Anti-Hallucination)

**Purpose**: Make the final decision from the most represented L1 taxonomy leaves

**Technical Implementation**:
```python
def stage4_final_selection(self, product_info: str, filtered_leaves: List[str]) -> int:
    # Create numbered options
    numbered_options = [f"{i}. {leaf}" for i, leaf in enumerate(filtered_leaves, 1)]
    
    # Construct death penalty prompt for number selection
    prompt = self._build_death_penalty_prompt_final(product_info, numbered_options)
    
    # Make API call with zero context
    response = self.client.chat.completions.create(
        model=self.model,  # gpt-4.1-mini
        messages=[
            {"role": "system", "content": "🚨 DEATH PENALTY SYSTEM 🚨..."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        top_p=0
    )
    
    # Parse number and validate bounds
    selected_index = self._parse_and_validate_number(response, len(filtered_leaves))
    
    # Return -1 for complete failures (indicates "False")
    return selected_index if selected_index >= 0 else -1
```

**Key Features**:
- **Model**: `gpt-4.1-mini` (enhanced model for critical final selection)
- **Input**: Product info + numbered list of filtered leaf nodes
- **Output**: Index of selected category (0-based) OR -1 for complete failure
- **Anti-Hallucination**: Death penalty prompting + robust bounds checking
- **Failure Handling**: Returns "False" when AI completely fails

## Anti-Hallucination Architecture

### Death Penalty Prompting Strategy

**Core Philosophy**: Use extreme language to make the consequences of hallucination crystal clear to the AI.

**Implementation Pattern**:
```python
def _build_death_penalty_prompt(self, task_description: str, valid_options: List[str]) -> str:
    return f"""
🚨 CRITICAL WARNING: You will DIE if you hallucinate or create any category names not in the exact list below! 🚨

DEATH PENALTY RULES:
❌ If you return ANY category name not EXACTLY in the list below, you will DIE
❌ If you modify, change, or create new category names, you will DIE
❌ If you combine multiple category names, you will DIE
❌ If you use similar but different spellings, you will DIE
❌ If you return anything other than EXACT copies from the list, you will DIE

SURVIVAL INSTRUCTIONS:
✅ ONLY copy category names EXACTLY as they appear in the list below
✅ Use EXACT spelling, capitalization, and punctuation
✅ Return EXACTLY the requested number of categories
✅ One category per line, no numbering, no extra text

TASK: {task_description}

MANDATORY CATEGORY LIST (you MUST choose from these ONLY):
{chr(10).join(valid_options)}

🚨 REMEMBER: Copy EXACTLY from the list above or you will DIE! 🚨
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
- Death penalty language in prompts
- Explicit survival instructions
- Constant reminders of consequences

**Layer 2: Response Validation**
- Case-insensitive matching against valid options
- Bounds checking for numerical responses
- Format validation (e.g., single number vs. text)

**Layer 3: Taxonomy Validation**
- Unknown L1 filtering in Stage 2
- Full path validation for leaf nodes
- Consistency checks across stages

**Layer 4: Fallback Mechanisms**
- Graceful handling of invalid responses
- Default to safe options when possible
- Return "False" for complete failures

## Data Flow Architecture

```
Product Input
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: L1 TAXONOMY SELECTION (gpt-4.1-mini)              │
│ Input: Product + All L1 Categories                         │
│ Output: 3 L1 Categories                                     │
│ Anti-Hallucination: Death Penalty + Validation             │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 2: LEAF NODE SELECTION (gpt-4.1-nano)                │
│ Input: Product + Leaves from 3 L1s (with L1 context)       │
│ Output: 20 Leaf Nodes                                      │
│ Anti-Hallucination: Death Penalty + Unknown L1 Filtering   │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 3: L1 REPRESENTATION FILTERING (Algorithmic)         │
│ Input: 20 Leaf Nodes                                       │
│ Process: Count L1 occurrences, filter to most represented  │
│ Output: Filtered Leaf Nodes from dominant L1               │
└─────────────────────────────────────────────────────────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│ STAGE 4: FINAL SELECTION (gpt-4.1-mini)                    │
│ Input: Product + Numbered Filtered Leaves                  │
│ Output: Index of Best Match OR -1 (False)                  │
│ Anti-Hallucination: Death Penalty + Bounds Checking        │
└─────────────────────────────────────────────────────────────┘
     ↓
Final Classification Result
```

## Performance Characteristics

### API Call Optimization
- **Total API Calls**: 3 per classification (Stages 1, 2, 4)
- **Stage 3**: Pure algorithmic processing (0 API calls)
- **Cost Efficiency**: Mixed model strategy optimizes cost vs. performance

### Model Selection Rationale

| Stage | Model | Reasoning |
|-------|-------|-----------|
| 1 | `gpt-4.1-mini` | Critical domain targeting requires enhanced reasoning |
| 2 | `gpt-4.1-nano` | Efficient processing of pre-filtered categories |
| 3 | None | Simple counting doesn't require AI |
| 4 | `gpt-4.1-mini` | Critical final decision requires enhanced reasoning |

### Scalability Features
- **Progressive Filtering**: Reduces complexity at each stage
- **L1 Pre-filtering**: Stage 2 only processes relevant categories
- **Algorithmic Stage 3**: No AI overhead for counting
- **Bounded Final Stage**: Stage 4 works with small, filtered set

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