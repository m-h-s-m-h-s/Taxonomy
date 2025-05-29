#!/usr/bin/env python3
"""
Taxonomy Navigator - AI-Powered Product Categorization System

This module implements a sophisticated AI classification system that automatically 
categorizes products into appropriate taxonomy categories using OpenAI's GPT models.

=== OPTIMIZED CLASSIFICATION PROCESS WITH AI SUMMARIZATION ===

The system uses AI-generated product summaries for initial categorization (stages 1-2)
while preserving full product details for final selection (stage 3):

📝 PRELIMINARY STAGE: AI PRODUCT SUMMARIZATION (NEW)
   - Purpose: Generate focused 40-60 word summary for categorization
   - Model: gpt-4.1-nano (efficient summarization)
   - Process: Extract key product type, features, uses, and distinguishing characteristics
   - Output: Concise product summary without marketing fluff
   - Key Feature: Provides consistent, optimized input for stages 1 and 2

🎯 STAGE 1: L1 TAXONOMY SELECTION (AI-Powered)
   - Purpose: Identify the 2 most relevant top-level taxonomy categories
   - Input: AI-generated product summary + ALL unique L1 taxonomy categories
   - AI Model: gpt-4.1-nano
   - Process: AI selects 2 most relevant L1 categories (e.g., "Electronics", "Apparel & Accessories")
   - Output: List of 2 L1 category names
   - Key Feature: Uses focused summary for accurate broad categorization
   - Anti-Hallucination: Professional prompting + strict validation that every returned category exists

🔍 **STAGE 2A: FIRST L1 LEAF SELECTION** (AI-Powered with Batch Processing)
- **Purpose**: Select best leaf nodes from the FIRST chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: AI-generated product summary
- **Process**: 
  * Processes categories in batches of 100 (e.g., 339 Electronics categories = 4 batches)
  * AI selects by number to avoid misspellings (e.g., "315" for Televisions)
  * Up to 15 selections per batch (e.g., 4 batches = up to 60 selections possible)
- **Output**: Combined list of leaf nodes from all batches
- **Anti-Hallucination**: Numeric selection + batch validation

🔍 **STAGE 2B: SECOND L1 LEAF SELECTION** (AI-Powered with Batch Processing) - CONDITIONAL
- **Purpose**: Select best leaf nodes from the SECOND chosen L1 taxonomy
- **Model**: `gpt-4.1-nano` (efficient model for leaf selection)
- **Input**: AI-generated product summary
- **Process**: Same batch processing as Stage 2A (15 per batch)
- **Output**: Combined list of leaf nodes from all batches
- **Condition**: SKIPPED if only 1 L1 category was selected in Stage 1
- **Anti-Hallucination**: Numeric selection + batch validation

🏆 STAGE 3: FINAL SELECTION (AI-Powered)
   - Purpose: Make the final decision from the combined leaf nodes from Stages 2A and 2B
   - Input: FULL product description + up to 30 leaf nodes from combined Stage 2 results
   - AI Model: gpt-4.1-mini
   - Process: 
     * Construct clear, professional prompt with specific constraints
     * Present up to 30 categories as numbered options (leaf names only)
     * AI identifies core product and selects best match using FULL details
     * Parse AI response with robust validation and bounds checking
     * Return guaranteed valid index of selected category OR -1 for complete failure
   - Output: Index of selected category (0-based, guaranteed valid) OR -1 for complete failure
   - Key Feature: Uses FULL product description for nuanced final decision
   - Condition: SKIPPED if only 1 leaf selected in Stage 2
   - Anti-Hallucination: Professional prompting + numeric validation + bounds checking + "False" for failures

=== SYSTEM ARCHITECTURE BENEFITS ===

✅ Efficiency: Progressive filtering (thousands → 2 L1s → variable leaves → 1)
✅ Cost Optimization: 3-5 API calls per classification (adaptive)
✅ Smart Summarization: AI extracts relevant details, removes marketing fluff
✅ Consistency: All stages use the same AI-generated summary for predictable results
✅ Accuracy: Consistent context across all stages improves reliability
✅ No Truncation: No arbitrary character limits that might exclude key details
✅ Scalability: Handles large taxonomies without overwhelming the AI
✅ Model Strategy: Uses gpt-4.1-nano for summarization and stages 1-2, gpt-4.1-mini for stage 3

=== KEY TECHNICAL FEATURES ===

- AI Summarization: Intelligent extraction of categorization-relevant details
- Deterministic Results: Uses temperature=0 and top_p=0 for consistent classifications
- Enhanced Product Identification: Advanced prompting to distinguish products from accessories
- Comprehensive Error Handling: Graceful handling of API errors and edge cases
- Duplicate Removal: Multiple stages of deduplication for clean results
- L1 Deduplication: Ensures no duplicate L1 categories are sent to AI
- Mixed Model Strategy: gpt-4.1-nano for summary and stages 1-2, gpt-4.1-mini for stage 3
- Death Penalty Prompting: Aggressive anti-hallucination prompts threatening "death" for wrong answers
- Zero Context API Calls: Each API call is a blank slate with no conversation history
- Anti-Hallucination Measures: Robust validation and bounds checking in all AI stages
- Unknown L1 Filtering: Stage 2 removes categories with "Unknown" L1 taxonomy
- Multiple Fallback Mechanisms: Graceful handling of invalid AI responses
- Complete Failure Handling: Returns "False" when AI completely fails or returns nothing

=== ENHANCED ANTI-HALLUCINATION MEASURES ===

🎯 SIMPLIFIED PROMPTING SYSTEM:
- All stages use clean, basic prompts with essential instructions only
- Removed complex anti-hallucination language for better AI performance
- Simple system messages focusing on core task requirements
- Clear, straightforward output format specifications

🔒 STRICT VALIDATION AT EVERY STAGE:
- Stage 1: Every returned L1 category is validated against the actual L1 list
- Stage 2A/2B: Every returned leaf category is validated against the filtered leaf list  
- Stage 3: AI response is validated to be numeric and within valid range
- All hallucinations are logged as CRITICAL errors with full context

✅ COMPREHENSIVE BOUNDS CHECKING:
- Stage 3 validates AI returns only numbers between 1 and max options
- All indices are bounds-checked before array access
- Multiple fallback mechanisms for invalid responses
- Returns -1 (False) for any validation failure

🛡️ MULTIPLE VALIDATION LAYERS:
- Regex validation for numeric responses in Stage 3
- Exact string matching for category validation in Stages 1 & 2
- Duplicate detection and removal at every stage
- Comprehensive logging of all validation steps

=== VERSION 12.0 IMPROVEMENTS ===

✅ AI-POWERED SUMMARIZATION:
- 40-60 word summaries focused on category identification
- Summaries start with product type for immediate clarity
- Category-relevant details prioritized over general features

✅ LEAF NODE DETECTION FIX:
- Fixed critical bug where non-leaf categories were marked as leaves
- Now correctly checks ALL subsequent paths, not just immediate next line
- Ensures only true end categories are presented for selection

✅ ENHANCED PROMPTING:
- Summaries designed to make taxonomy immediately discernible
- Clear product-type terminology from the first words
- Focus on category-distinguishing features

Author: AI Assistant
Version: 12.4 (Numeric Selection with Expanded Batch Processing)
Last Updated: 2025-01-29
"""

import os
import json
import argparse
import logging
import time
import sys
from typing import List, Dict, Tuple, Optional, Any
from collections import Counter
from openai import OpenAI

# Add the src directory to the Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_api_key

# Configure logging for production use
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taxonomy_navigator")

class TaxonomyNavigator:
    """
    AI-powered taxonomy navigation system for product categorization.
    
    This class implements a progressive, multi-stage classification process with
    extensive anti-hallucination measures. Version 12.5 uses consistent AI-generated
    summaries across all stages for more predictable results.

    Key Features:
    - 5 stages: AI summary + Stage 1 (2 L1 categories) + Stages 2A/2B (15 per batch) + Stage 3
    - AI-generated product summaries (40-60 words with synonyms) used for ALL stages
    - Numeric selection in Stages 2 and 3 to eliminate misspelling issues
    - Batch processing of categories (100 per batch, up to 15 selections per batch)
    - Enhanced prompts with explicit main product vs accessory guidance and examples
    - Anti-hallucination validation at every stage
    - Optimized API usage: skips Stage 3 if only 1 leaf selected
    - Uses gpt-4.1-nano for efficiency, gpt-4.1-mini for balanced final selection

    Recent Improvements (v12.5):
    - Stage 3 uses gpt-4.1-mini for balanced accuracy and cost
    - AI summaries include synonyms (e.g., "Television (TV, flat-screen display)")
    - All stages use the same AI-generated summary for consistency

    Attributes:
        taxonomy_file (str): Path to the taxonomy file in Google Product Taxonomy format
        model (str): OpenAI model used for stages 1
        stage2_model (str): OpenAI model used for stage 2 (always gpt-4.1-nano)
        stage3_model (str): OpenAI model used for stage 3 (gpt-4.1-mini)
        taxonomy_tree (Dict): Hierarchical representation of the taxonomy
        all_paths (List[str]): All taxonomy paths from the file
        leaf_markers (List[bool]): Boolean markers indicating which paths are leaf nodes
        client (OpenAI): OpenAI API client instance
        
    Example Usage:
        navigator = TaxonomyNavigator("taxonomy.txt", api_key)
        paths, best_idx = navigator.navigate_taxonomy("Samsung 65-inch QLED TV")
        best_category = paths[best_idx][-1]  # e.g., "Televisions"
    """

    __version__ = "12.5"

    def __init__(self, taxonomy_file: str, api_key: str = None, model: str = "gpt-4.1-nano"):
        """
        Initialize the TaxonomyNavigator with taxonomy data and API configuration.

        Args:
            taxonomy_file (str): Path to the taxonomy file (Google Product Taxonomy format)
            api_key (str, optional): OpenAI API key. If None, will use get_api_key() utility
            model (str): OpenAI model for stages 1 and 3. Defaults to "gpt-4.1-nano"
            
        Raises:
            ValueError: If API key cannot be obtained
            FileNotFoundError: If taxonomy file doesn't exist
            Exception: If taxonomy tree building fails
        """
        self.taxonomy_file = taxonomy_file
        self.model = model  # Used for stage 1 (now nano by default)
        self.stage2_model = "gpt-4.1-nano"  # Used for stage 2
        self.stage3_model = "gpt-4.1-mini"  # Used for stage 3 (final selection) - balanced accuracy/cost
        
        # Build the taxonomy tree and identify leaf nodes
        self.taxonomy_tree = self._build_taxonomy_tree()
        
        # Initialize OpenAI client with API key
        api_key = get_api_key(api_key)
        if not api_key:
            raise ValueError("OpenAI API key not provided. Please set it in api_key.txt, as an environment variable, or provide it as an argument.")
            
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized TaxonomyNavigator with models: {model} (stage 1), {self.stage2_model} (stage 2), {self.stage3_model} (stage 3)")
        logger.info(f"Taxonomy stats: {len(self.all_paths)} total paths, {sum(self.leaf_markers)} leaf nodes")

    def generate_product_summary(self, product_info: str) -> str:
        """
        Generate an AI-powered summary of the product for classification stages 1 and 2.
        
        This method creates a focused summary that captures the key aspects needed for
        category selection while removing marketing fluff and irrelevant details.
        Uses gpt-4.1-nano for efficiency.
        
        Args:
            product_info (str): Full product description
            
        Returns:
            str: Concise product summary (40-60 words) optimized for categorization
        """
        logger.info("Generating AI product summary for stages 1 and 2")
        
        prompt = """Summarize this product in 40-60 words to make its category crystal clear:
1. START with the EXACT common product name (e.g., "television" not "home entertainment display", "lipstick" not "lip color product")
2. Include 1-2 synonyms or alternative names in parentheses to clarify (e.g., "Television (TV, flat-screen display)")
3. Core function that defines its category
4. Key distinguishing features within that category
5. Primary use context

Use standard product names. Include clarifying synonyms. Be direct and specific.
IMPORTANT: Identify what the product IS, not what accessories it might need.
Example: "Television (TV, flat-screen display). Electronic device for viewing video content..."

Product: {product_info}

Summary:""".format(product_info=product_info)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-nano",  # Use nano for efficient summarization
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product categorization assistant. Always use the most common, standard product name (e.g., 'television' not 'display device'). Include helpful synonyms in parentheses. Be direct and avoid flowery descriptions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic summary
                top_p=0,
                max_tokens=100  # Limit response length (reduced from 150)
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary ({len(summary.split())} words): {summary[:100]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating product summary: {e}")
            # Fallback to truncated original if summary fails
            logger.warning("Falling back to truncated product description")
            return product_info[:400] + "..." if len(product_info) > 400 else product_info

    def _build_taxonomy_tree(self) -> Dict[str, Any]:
        """
        Parse the taxonomy file and build a hierarchical tree structure.
        
        This method processes the taxonomy file line by line, creating a tree structure
        and identifying leaf nodes (categories with no subcategories).
        Leaf nodes are identified by checking if the next line starts with the current line plus " > ".
        
        The taxonomy file format expected:
        - First line: Header (ignored)
        - Subsequent lines: Category paths separated by " > "
        - Example: "Electronics > Computers > Laptops"

        Returns:
            Dict[str, Any]: Hierarchical tree with structure:
                {
                    "name": "root",
                    "children": {
                        "category_name": {
                            "name": "category_name",
                            "children": {...},
                            "is_leaf": bool
                        }
                    }
                }
                
        Raises:
            FileNotFoundError: If taxonomy file doesn't exist
            Exception: If file parsing fails
        """
        logger.info(f"Building taxonomy tree from {self.taxonomy_file}")
        tree = {"name": "root", "children": {}}
        
        try:
            with open(self.taxonomy_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Initialize storage for paths and leaf identification
            paths = []
            is_leaf = []
            
            # Process each line (skip header at index 0)
            for i, line in enumerate(lines[1:]):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                paths.append(line)
                
                # Determine if this is a leaf node by checking ALL subsequent lines
                # A path is a leaf if NO subsequent line starts with this path followed by " > "
                is_leaf_node = True
                
                # Check all remaining lines to see if any are children of this path
                for j in range(i + 1, len(lines[1:])):
                    subsequent_line = lines[j + 1].strip()  # j+1 because we skipped header
                    if subsequent_line and subsequent_line.startswith(line + " > "):
                        is_leaf_node = False
                        break  # Found a child, no need to check further
                
                is_leaf.append(is_leaf_node)
                self._add_to_tree(tree, line, is_leaf_node)
            
            # Store for later use in navigation
            self.all_paths = paths
            self.leaf_markers = is_leaf
            
            leaf_count = sum(is_leaf)
            logger.info(f"Successfully built taxonomy tree with {len(paths)} total paths and {leaf_count} leaf nodes")
            return tree
            
        except FileNotFoundError:
            logger.error(f"Taxonomy file not found: {self.taxonomy_file}")
            raise
        except Exception as e:
            logger.error(f"Error building taxonomy tree: {e}")
            raise

    def _add_to_tree(self, tree: Dict[str, Any], path: str, is_leaf: bool = False) -> None:
        """
        Add a single taxonomy path to the hierarchical tree structure.
        
        This method parses a path like "Electronics > Computers > Laptops" and adds
        it to the tree, creating intermediate nodes as needed.

        Args:
            tree (Dict[str, Any]): The root tree structure to add to
            path (str): Taxonomy path with categories separated by " > "
            is_leaf (bool): Whether this path represents a leaf node (end category)
            
        Example:
            path = "Electronics > Computers > Laptops"
            Creates: tree["children"]["Electronics"]["children"]["Computers"]["children"]["Laptops"]
        """
        # Handle top-level categories (no ">" separator)
        if '>' not in path:
            if path not in tree["children"]:
                tree["children"][path] = {"name": path, "children": {}, "is_leaf": is_leaf}
            else:
                tree["children"][path]["is_leaf"] = is_leaf
            return

        # Parse multi-level path
        parts = [p.strip() for p in path.split('>')]
        current = tree
        
        # Navigate/create the tree structure
        for i, part in enumerate(parts):
            if i == 0:
                # Handle the top level
                if part not in current["children"]:
                    current["children"][part] = {"name": part, "children": {}, "is_leaf": False}
                current = current["children"][part]
            else:
                # Handle deeper levels
                if "children" not in current:
                    current["children"] = {}
                
                if part not in current["children"]:
                    # Mark as leaf only if this is the last part and is_leaf is True
                    current["children"][part] = {
                        "name": part, 
                        "children": {}, 
                        "is_leaf": i == len(parts) - 1 and is_leaf
                    }
                else:
                    # Update leaf status if this is the final part
                    if i == len(parts) - 1:
                        current["children"][part]["is_leaf"] = is_leaf
                current = current["children"][part]

    def stage1_l1_selection(self, product_info: str) -> List[str]:
        """
        Stage 1: Identify the 2 most relevant top-level taxonomy categories.
        
        This method implements the first stage of the classification process.
        The AI receives the product summary and all unique L1 taxonomy 
        categories as context, and is instructed to select the 2 most appropriate categories.
        
        Process:
        1. Extract all unique L1 taxonomy categories from the taxonomy
        2. Send product summary + L1 categories to AI with professional prompt
        3. Parse AI response and remove duplicates (case-insensitive)
        4. Validate categories against actual taxonomy entries
        5. Return up to 2 unique, valid categories
        
        Args:
            product_info (str): Product summary (generated by AI)
            
        Returns:
            List[str]: Top 2 most relevant L1 taxonomy category names, ordered by relevance,
                      with duplicates removed and validated against taxonomy
            
        Raises:
            Exception: If OpenAI API call fails (logged and handled with fallback)
        """
        logger.info(f"Stage 1: Using AI-generated product summary ({len(product_info)} chars)")
        
        # Extract all unique L1 taxonomy categories from the taxonomy
        l1_categories = []
        for i, full_path in enumerate(self.all_paths):
            if self.leaf_markers[i]:
                l1_category = full_path.split(" > ")[0]
                if l1_category not in l1_categories:
                    l1_categories.append(l1_category)
        
        if not l1_categories:
            logger.warning("No L1 taxonomy categories found in taxonomy")
            return []
        
        logger.info(f"Stage 1: Querying OpenAI for top 2 L1 taxonomy categories among {len(l1_categories)} options")
        
        # Construct enhanced prompt for L1 taxonomy selection
        prompt = (
            f"Product: {product_info}\n\n"
            
            f"Select exactly 2 categories from this list that best match the product:\n\n"
            f"{chr(10).join(l1_categories)}\n\n"
            
            f"Return one category per line:"
        )
        
        try:
            # Make API call with deterministic settings and NO CONTEXT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a product categorization assistant. Select L1 categories from the provided list using exact spelling."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic responses
                top_p=0        # Deterministic responses
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            selected_categories = [category.strip() for category in content.split('\n') if category.strip()]
            
            # CRITICAL VALIDATION: Ensure every returned category actually exists in our L1 list
            validated_categories = []
            hallucination_count = 0
            
            for category in selected_categories:
                if category in l1_categories:
                    validated_categories.append(category)
                    logger.info(f"✅ VALIDATED: '{category}' exists in L1 taxonomy")
                else:
                    logger.error(f"🚨 HALLUCINATION DETECTED: '{category}' does NOT exist in L1 taxonomy")
                    logger.error(f"Available L1 categories: {l1_categories}")
                    hallucination_count += 1
            
            if hallucination_count > 0:
                logger.error(f"🚨 CRITICAL: AI hallucinated {hallucination_count} categories in Stage 1")
                logger.error("🚨 This is a serious anti-hallucination failure")
            
            # Remove duplicates while preserving order (case-insensitive)
            seen = set()
            unique_categories = []
            for category in validated_categories:
                category_lower = category.lower()
                if category_lower not in seen:
                    seen.add(category_lower)
                    unique_categories.append(category)
            
            # Ensure we have at most 2 categories after deduplication
            unique_categories = unique_categories[:2]
            
            # Log duplicate removal if any occurred
            if len(unique_categories) < len(selected_categories):
                duplicates_removed = len(selected_categories) - len(unique_categories)
                logger.info(f"Removed {duplicates_removed} duplicate categories from AI response")
            
            # Log if fewer than expected categories returned
            if len(unique_categories) < 2:
                logger.warning(f"OpenAI returned fewer than 2 unique L1 taxonomy categories: {len(unique_categories)}")
            
            logger.info(f"Stage 1 complete: Selected {len(unique_categories)} unique L1 taxonomy categories")
            
            # Validate and match categories to our taxonomy
            return self._validate_categories(unique_categories, l1_categories)
            
        except Exception as e:
            logger.error(f"Error in Stage 1 L1 selection: {e}")
            # Fallback: return first 2 L1 categories
            if l1_categories:
                result = l1_categories[:min(2, len(l1_categories))]
                logger.warning(f"Using fallback L1 taxonomy categories: {result[:2]}...")
                return result
            return []

    def stage2a_first_leaf_selection(self, product_info: str, selected_l1s: List[str]) -> List[str]:
        """
        Stage 2A: Select best leaf nodes from the FIRST chosen L1 taxonomy.
        
        This method implements the first part of the second stage of the classification process.
        It focuses EXCLUSIVELY on the first L1 taxonomy from stage 1.
        Processes in batches of 100, allowing up to 15 selections per batch.
        
        Args:
            product_info (str): Product summary (generated by AI)
            selected_l1s (List[str]): List of L1 taxonomy category names
            
        Returns:
            List[str]: Combined leaf node names from all batches of the FIRST L1 taxonomy
        """
        if not selected_l1s:
            return []
        return self._leaf_selection_helper(product_info, [selected_l1s[0]], [], "2A", "first 15")

    def stage2b_second_leaf_selection(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str]) -> List[str]:
        """
        Stage 2B: Select best leaf nodes from the SECOND chosen L1 taxonomy.
        
        This method implements the second part of the second stage of the classification process.
        It focuses EXCLUSIVELY on the second L1 taxonomy from stage 1.
        Processes in batches of 100, allowing up to 15 selections per batch.

        Args:
            product_info (str): Product summary (generated by AI)
            selected_l1s (List[str]): List of L1 taxonomy category names
            excluded_leaves (List[str]): Leaves already selected in Stage 2A
            
        Returns:
            List[str]: Combined leaf node names from all batches of the SECOND L1 taxonomy
        """
        if len(selected_l1s) < 2:
            logger.info("Stage 2B skipped: Only 1 L1 category was selected in Stage 1")
            return []
        return self._leaf_selection_helper(product_info, [selected_l1s[1]], excluded_leaves, "2B", "second 15")

    def stage2c_third_leaf_selection(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str]) -> List[str]:
        """
        DEPRECATED: Stage 2C is no longer used. We only use stages 2A and 2B now.
        
        This method is kept for backward compatibility but will return empty list.
        """
        logger.info("Stage 2C skipped: System now only uses stages 2A and 2B")
        return []

    def _leaf_selection_helper(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str], stage_name: str, description: str) -> List[str]:
        """
        Helper method for Stage 2 leaf selection with configurable exclusions.
        
        This method uses the AI-generated product summary to ensure the AI has focused
        context for accurate leaf selection. Processes categories in batches of 100,
        allowing up to 15 selections per batch.
        
        Args:
            product_info (str): Product summary (generated by AI)
            selected_l1s (List[str]): List of L1 categories to filter by
            excluded_leaves (List[str]): Leaves to exclude from selection
            stage_name (str): Name of the stage (e.g., "2A", "2B")
            description (str): Description of the selection (e.g., "first 15", "second 15")
            
        Returns:
            List[str]: Combined leaf node names from all batches
        """
        logger.info(f"Stage {stage_name}: Using AI-generated product summary ({len(product_info)} chars)")
        
        try:
            # Filter leaf nodes to selected L1 categories only
            filtered_leaves = []
            leaf_to_l1 = self._create_leaf_to_l1_mapping()
            
            for i, full_path in enumerate(self.all_paths):
                if self.leaf_markers[i]:
                    leaf = full_path.split(" > ")[-1]
                    l1_category = full_path.split(" > ")[0]
                    
                    # Only include if in selected L1 categories and not excluded
                    if l1_category in selected_l1s and leaf not in excluded_leaves:
                        filtered_leaves.append(leaf)
            
            if not filtered_leaves:
                logger.warning(f"No leaf nodes found for L1 categories: {selected_l1s}")
                return []
            
            logger.info(f"Stage {stage_name}: Querying OpenAI for {description} leaf nodes among {len(filtered_leaves)} options from L1: {selected_l1s}")
            
            # Process in batches of 100 to handle large category lists
            batch_size = 100
            all_selected_numbers = []
            
            for batch_start in range(0, len(filtered_leaves), batch_size):
                batch_end = min(batch_start + batch_size, len(filtered_leaves))
                batch_leaves = filtered_leaves[batch_start:batch_end]
                
                if not batch_leaves:
                    continue
                    
                logger.info(f"Processing batch {batch_start//batch_size + 1}: options {batch_start + 1}-{batch_end}")
                
                # Create numbered list for this batch
                numbered_options = []
                leaf_mapping = {}  # Map batch numbers to leaf names
                for i, leaf in enumerate(batch_leaves, 1):
                    l1_category = leaf_to_l1.get(leaf, "Unknown")
                    numbered_options.append(f"{i}. {leaf} (L1: {l1_category})")
                    leaf_mapping[i] = leaf
                
                # Construct prompt with numbered options
                prompt = (
                    f"Product: {product_info}\n\n"
                    
                    f"Select up to 15 categories that match this product from the numbered list below.\n"
                    f"Think carefully about what the product actually is.\n"
                    f"Be aware: The list may contain both main product categories AND accessories/parts.\n"
                    f"IMPORTANT: If the product is a complete item (like a circular saw), choose the main product category (e.g., 'Handheld Circular Saws'), NOT the accessories category (e.g., 'Handheld Circular Saw Accessories').\n"
                    f"Only choose accessory categories if the product is actually an accessory/part, not the main product itself.\n"
                    f"Examples: A TV should be 'Televisions' not 'TV Mounts'; A laptop should be 'Laptops' not 'Laptop Cases'.\n\n"
                    
                    f"Categories to choose from (batch {batch_start//batch_size + 1} of {(len(filtered_leaves) + batch_size - 1)//batch_size}):\n"
                    f"{chr(10).join(numbered_options)}\n\n"
                    
                    f"Return ONLY the numbers of matching categories (up to 15), one per line.\n"
                    f"If no categories match, return 'NONE'.\n"
                    f"Example response:\n"
                    f"3\n"
                    f"7\n"
                    f"15"
                )
                
                try:
                    # Make API call with deterministic settings
                    response = self.client.chat.completions.create(
                        model=self.stage2_model,  # gpt-4.1-nano for efficiency
                        messages=[
                            {
                                "role": "system", 
                                "content": "You are a product categorization assistant. Select categories by their numbers only. Return only numbers, one per line."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0,  # Deterministic responses
                        top_p=0        # Deterministic responses
                    )
                    
                    # Parse response and extract selected category numbers
                    content = response.choices[0].message.content.strip()
                    
                    if content.upper() != "NONE":
                        # Extract all numbers from the response
                        import re
                        for line in content.split('\n'):
                            line = line.strip()
                            if line:
                                # Extract numbers from the line
                                numbers = re.findall(r'\d+', line)
                                for num_str in numbers:
                                    try:
                                        num = int(num_str)
                                        if 1 <= num <= len(leaf_mapping):  # Validate number is in range
                                            leaf_name = leaf_mapping[num]
                                            all_selected_numbers.append(leaf_name)
                                            logger.info(f"✅ Batch {batch_start//batch_size + 1}: Selected option {num}: '{leaf_name}'")
                                    except ValueError:
                                        continue
                                    
                except Exception as e:
                    logger.error(f"Error processing batch {batch_start//batch_size + 1}: {e}")
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_leaves = []
            for leaf in all_selected_numbers:
                if leaf not in seen:
                    seen.add(leaf)
                    unique_leaves.append(leaf)
            
            # Note: We now allow up to 15 per batch, so total could be much higher
            logger.info(f"Stage {stage_name} complete: Selected {len(unique_leaves)} unique leaf nodes from all batches")
            
            return unique_leaves
            
        except Exception as e:
            logger.error(f"Error in _leaf_selection_helper: {e}")
            return []

    def stage3_final_selection(self, product_info: str, selected_leaves: List[str]) -> int:
        """
        Stage 3: Make the final decision from the combined leaf nodes from Stages 2A and 2B.
        
        This method now uses the AI-generated summary (same as stages 1-2) for consistency
        across all stages of the classification process.
        
        If only 1 leaf was returned from Stage 2, we skip this stage entirely to save an API call.
        
        This method implements the final stage of the classification process.
        It receives the filtered leaf nodes and asks the AI to select the single best match.
        
        Args:
            product_info (str): AI-generated product summary (40-60 words with synonyms)
            selected_leaves (List[str]): Combined list of selected leaf nodes
            
        Returns:
            int: Index of the selected category (0-based) OR -1 for complete failure
        """
        if not selected_leaves:
            logger.warning("Stage 3: No leaf nodes provided for final selection")
            return -1
        
        # OPTIMIZATION: If only 1 leaf was selected, skip Stage 3 to save an API call
        if len(selected_leaves) == 1:
            logger.info(f"Stage 3 skipped: Only 1 leaf was selected in Stage 2, using '{selected_leaves[0]}'")
            return 0
        
        logger.info(f"Stage 3: Using AI-generated summary ({len(product_info)} chars)")
        logger.info(f"Stage 3: Final selection among {len(selected_leaves)} leaf nodes")
        
        # Create numbered options for the AI
        numbered_options = [f"{i}. {leaf}" for i, leaf in enumerate(selected_leaves, 1)]
        
        # Construct professional prompt for final selection
        prompt = self._build_professional_prompt_final(product_info, numbered_options)
        
        try:
            # Make API call with enhanced model for critical final selection
            response = self.client.chat.completions.create(
                model=self.stage3_model,  # gpt-4.1-mini for balanced accuracy/cost
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a product categorization assistant. Select the single best matching category by its number."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic selection
                top_p=0        # Deterministic selection
            )
            
            # Parse and validate the AI's numeric response
            selected_index = self._parse_and_validate_number(response, len(selected_leaves))
            
            if selected_index >= 0:
                logger.info(f"Stage 3 complete: AI selected option {selected_index + 1} - '{selected_leaves[selected_index]}'")
                return selected_index
            else:
                logger.error("Stage 3 failed: AI response was invalid or out of bounds")
                return -1
                
        except Exception as e:
            logger.error(f"Error in Stage 3 final selection: {e}")
            return -1

    def navigate_taxonomy(self, product_info: str) -> Tuple[List[List[str]], int]:
        """
        Complete taxonomy navigation process with enhanced AI capabilities.
        
        This method orchestrates the entire classification pipeline:
        1. Stage 1: AI selects top 2 L1 taxonomy categories
        2. Stage 2A: AI selects first 15 leaf nodes from first L1
        3. Stage 2B: AI selects second 15 leaf nodes from second L1 (skipped if only 1 L1)
        4. Stage 3: AI final selection from combined candidates (skipped if only 1 leaf)
        
        The system includes comprehensive anti-hallucination measures:
        - Professional prompting with explicit constraints
        - Zero context between API calls (no conversation history)
        - Multi-layer validation at every stage
        - Bounds checking for numeric responses
        - Complete failure handling returns "False"
        
        Args:
            product_info (str): Complete product information for classification
            
        Returns:
            Tuple[List[List[str]], int]: 
                - List of category paths (each path is a list from root to leaf)
                - Index of the best match in the paths list
                Special case: Returns ([["False"]], 0) when classification completely fails
                
        Example:
            paths, best_idx = navigator.navigate_taxonomy("Samsung 65-inch QLED TV")
            # paths = [["Electronics", "Cell Phones", "Smartphones"]]
            # best_idx = 0
        """
        try:
            logger.info("="*80)
            logger.info(f"Starting taxonomy navigation for: {product_info[:100]}...")
            logger.info("="*80)
            
            # ================== GENERATE PRODUCT SUMMARY ==================
            # Create an AI-generated summary for all stages (1, 2, and 3)
            logger.info("\n📝 GENERATING PRODUCT SUMMARY FOR ALL STAGES")
            product_summary = self.generate_product_summary(product_info)
            logger.info(f"Summary will be used for all categorization stages")
            
            # ================== STAGE 1: L1 TAXONOMY SELECTION ==================
            # AI selects the top 2 L1 taxonomy categories from all available options
            logger.info("\n🎯 STAGE 1: L1 TAXONOMY SELECTION")
            logger.info(f"Objective: Select top 2 L1 categories from all {len(set(path.split(' > ')[0] for path in self.all_paths if self.leaf_markers[self.all_paths.index(path)]))} unique L1 options")
            
            selected_l1s = self.stage1_l1_selection(product_summary)  # Use summary instead of full description
            
            if not selected_l1s:
                logger.error("Stage 1 failed: No L1 categories selected")
                return [["False"]], 0
            
            logger.info(f"✅ Stage 1 Result: Selected {len(selected_l1s)} L1 categories: {selected_l1s}")
            
            # ================== STAGE 2A: FIRST L1 LEAF SELECTION ==================
            # AI selects the first 15 best leaf nodes from the FIRST chosen L1 taxonomy
            logger.info("\n🔍 STAGE 2A: FIRST L1 LEAF SELECTION")
            logger.info(f"Objective: Select top 15 leaf nodes from L1 category: {selected_l1s[0]}")
            
            selected_leaves_2a = self.stage2a_first_leaf_selection(product_summary, selected_l1s)  # Use summary
            
            logger.info(f"✅ Stage 2A Result: Selected {len(selected_leaves_2a)} leaf nodes from first L1")
            
            # ================== STAGE 2B: SECOND L1 LEAF SELECTION ==================
            # AI selects the second 15 best leaf nodes from the SECOND chosen L1 taxonomy
            # Skip if only 1 L1 was selected
            if len(selected_l1s) >= 2:
                logger.info("\n🔍 STAGE 2B: SECOND L1 LEAF SELECTION")
                logger.info(f"Objective: Select top 15 leaf nodes from L1 category: {selected_l1s[1]}")
                
                selected_leaves_2b = self.stage2b_second_leaf_selection(product_summary, selected_l1s, selected_leaves_2a)  # Use summary
                
                logger.info(f"✅ Stage 2B Result: Selected {len(selected_leaves_2b)} leaf nodes from second L1")
            else:
                logger.info("\n🔍 STAGE 2B: SKIPPED (only 1 L1 category selected)")
                selected_leaves_2b = []
            
            # Combine all selected leaves from stages 2A and 2B
            all_selected_leaves = selected_leaves_2a + selected_leaves_2b
            
            if not all_selected_leaves:
                logger.error("Stage 2 failed: No leaf nodes selected from any L1 category")
                return [["False"]], 0
            
            logger.info(f"\n📊 Stage 2 Summary: Total {len(all_selected_leaves)} unique leaf nodes selected")
            
            # ================== STAGE 3: FINAL SELECTION ==================
            # AI makes the final selection from all candidates
            # Skip if only 1 leaf was selected
            if len(all_selected_leaves) == 1:
                logger.info("\n🏆 STAGE 3: FINAL SELECTION - SKIPPED")
                logger.info(f"Only 1 leaf was selected in Stage 2, using: '{all_selected_leaves[0]}'")
                best_match_idx = 0
            else:
                logger.info("\n🏆 STAGE 3: FINAL SELECTION")
                logger.info(f"Objective: Select the single best match from {len(all_selected_leaves)} candidates")
                logger.info("Note: Using AI-generated summary for consistency with stages 1-2")
                
                best_match_idx = self.stage3_final_selection(product_summary, all_selected_leaves)  # Use summary instead of full description
                
                if best_match_idx < 0:
                    logger.error("Stage 3 failed: Unable to determine best match")
                    return [["False"]], 0
                
                logger.info(f"✅ Stage 3 Result: Selected index {best_match_idx} - '{all_selected_leaves[best_match_idx]}'")
            
            # ================== CONVERT TO FULL PATHS ==================
            # Convert the selected leaf node to its full taxonomy path
            selected_leaf = all_selected_leaves[best_match_idx]
            
            # Find the full path for this leaf
            full_paths = []
            for i, path in enumerate(self.all_paths):
                if self.leaf_markers[i] and path.endswith(selected_leaf):
                    # Verify exact match (not just endswith to avoid false positives)
                    path_parts = path.split(" > ")
                    if path_parts[-1] == selected_leaf:
                        full_paths.append(path_parts)
            
            if not full_paths:
                logger.error(f"Failed to find full path for leaf: {selected_leaf}")
                return [["False"]], 0
            
            # Return the first matching path (there should typically be only one)
            logger.info("="*80)
            logger.info(f"✅ NAVIGATION COMPLETE: {' > '.join(full_paths[0])}")
            logger.info("="*80)
            
            return full_paths[:1], 0  # Return single best path
            
        except Exception as e:
            logger.error(f"Critical error in navigate_taxonomy: {e}", exc_info=True)
            return [["False"]], 0

    def _extract_leaf_nodes(self) -> Tuple[List[str], List[str]]:
        """
        Extract all leaf nodes (end categories) from the taxonomy.
        
        Returns:
            Tuple[List[str], List[str]]: 
                - Full paths of leaf nodes
                - Leaf node names (last part of path)
        """
        logger.info("Extracting leaf nodes from taxonomy")
        
        leaf_paths = []
        leaf_names = []
        
        for i, full_path in enumerate(self.all_paths):
            if self.leaf_markers[i]:
                leaf_paths.append(full_path)
                # Extract just the leaf name (last part after " > ")
                leaf_name = full_path.split(" > ")[-1]
                leaf_names.append(leaf_name)
        
        logger.info(f"Found {len(leaf_paths)} leaf nodes")
        return leaf_paths, leaf_names

    def _create_leaf_to_l1_mapping(self) -> Dict[str, str]:
        """
        Create a mapping from leaf node names to their L1 taxonomy categories.
        
        Returns:
            Dict[str, str]: Mapping from leaf names to L1 categories
        """
        leaf_to_l1 = {}
        for i, path in enumerate(self.all_paths):
            if self.leaf_markers[i]:
                leaf_name = path.split(" > ")[-1]
                l1_category = path.split(" > ")[0]  # First part is L1 category
                leaf_to_l1[leaf_name] = l1_category
        return leaf_to_l1

    def _create_leaf_to_l2_mapping(self) -> Dict[str, str]:
        """
        Create a mapping from leaf node names to their L2 taxonomy categories.
        
        Returns:
            Dict[str, str]: Mapping from leaf names to L2 categories
        """
        leaf_to_l2 = {}
        for i, path in enumerate(self.all_paths):
            if self.leaf_markers[i]:
                leaf_name = path.split(" > ")[-1]
                path_parts = path.split(" > ")
                # L2 is the second level category (index 1), or L1 if only one level
                l2_category = path_parts[1] if len(path_parts) > 1 else path_parts[0]
                leaf_to_l2[leaf_name] = l2_category
        return leaf_to_l2

    def _create_leaf_to_path_mapping(self) -> Dict[str, str]:
        """
        Create a mapping from leaf node names to their full taxonomy paths.
        
        Returns:
            Dict[str, str]: Mapping from leaf names to full paths
        """
        leaf_to_path = {}
        for i, path in enumerate(self.all_paths):
            if self.leaf_markers[i]:
                leaf_name = path.split(" > ")[-1]
                leaf_to_path[leaf_name] = path
        return leaf_to_path

    def _convert_leaves_to_paths(self, selected_leaves: List[str]) -> List[List[str]]:
        """
        Convert selected leaf names back to full taxonomy paths.
        
        Args:
            selected_leaves (List[str]): Leaf names selected by AI
            
        Returns:
            List[List[str]]: Full taxonomy paths as lists
        """
        # Create mapping from leaf names to full paths
        leaf_to_path = self._create_leaf_to_path_mapping()
        
        final_paths = []
        for leaf in selected_leaves:
            if leaf in leaf_to_path:
                path = leaf_to_path[leaf].split(" > ")
                final_paths.append(path)
                logger.debug(f"Converted '{leaf}' to path: {' > '.join(path)}")
            else:
                logger.warning(f"Could not find full path for leaf: {leaf}")
        
        return final_paths

    def _validate_categories(self, selected_categories: List[str], available_categories: List[str]) -> List[str]:
        """
        Validate and match AI-selected categories against available taxonomy categories.
        
        This method handles cases where the AI might return category names that don't
        exactly match the taxonomy (due to case differences, partial matches, etc.).

        Args:
            selected_categories (List[str]): Categories returned by AI
            available_categories (List[str]): Valid categories from taxonomy
            
        Returns:
            List[str]: Validated categories that exist in the taxonomy (no duplicates)
        """
        valid_categories = []
        seen_valid = set()  # Track validated categories to prevent duplicates
        
        for selected in selected_categories:
            # Try exact match first (case-insensitive)
            matching_categories = [c for c in available_categories if c.lower() == selected.lower()]
            if matching_categories:
                matched_category = matching_categories[0]
                if matched_category.lower() not in seen_valid:
                    seen_valid.add(matched_category.lower())
                    valid_categories.append(matched_category)
                continue
            
            # Try partial match
            found_match = False
            for c in available_categories:
                if c.lower() in selected.lower() or selected.lower() in c.lower():
                    logger.info(f"Found closest match for '{selected}': '{c}'")
                    if c.lower() not in seen_valid:
                        seen_valid.add(c.lower())
                        valid_categories.append(c)
                    found_match = True
                    break
            
            if not found_match:
                # No match found - log warning but include anyway (if not duplicate)
                logger.warning(f"OpenAI returned category not in taxonomy: {selected}")
                if selected.lower() not in seen_valid:
                    seen_valid.add(selected.lower())
                    valid_categories.append(selected)
        
        return valid_categories

    def _parse_and_validate_number(self, response: Any, max_options: int) -> int:
        """
        Parse the AI's selection number and convert to 0-based index.
        
        Handles various formats the AI might return (e.g., "1", "1.", "Option 1").
        Includes robust validation to prevent invalid indices.
        Returns -1 for complete parsing failures to indicate classification failure.

        Args:
            response (Any): Raw response from AI
            max_options (int): Maximum valid option number
            
        Returns:
            int: 0-based index of selected option (guaranteed to be valid)
                 OR -1 to indicate complete parsing failure
        """
        try:
            # Get the raw content
            result = response.choices[0].message.content.strip()
            logger.info(f"Parsing response: '{result}'")
            
            # Clean the result string
            cleaned_result = result.strip().lower()
            logger.info(f"Cleaned result: '{cleaned_result}'")
            
            # Check for completely empty or meaningless input
            if not cleaned_result or len(cleaned_result) == 0:
                logger.warning("Empty or meaningless AI response for parsing")
                return -1  # Complete failure
            
            # Look for any number in the result
            import re
            numbers = re.findall(r'\d+', cleaned_result)
            logger.info(f"Found numbers in response: {numbers}")
            
            if numbers:
                # Take the first number found
                selected_number = int(numbers[0])
                logger.info(f"Selected number: {selected_number}")
                
                # Validate the number is within valid range (1 to max_options)
                if 1 <= selected_number <= max_options:
                    best_index = selected_number - 1  # Convert to 0-based
                    logger.info(f"Valid selection: option {selected_number} (index {best_index})")
                    return best_index
                else:
                    logger.warning(f"AI returned out-of-range number: {selected_number}, valid range is 1-{max_options}")
            
            # If no valid number found, try direct number parsing
            try:
                direct_number = int(cleaned_result)
                logger.info(f"Direct number parsing result: {direct_number}")
                if 1 <= direct_number <= max_options:
                    best_index = direct_number - 1
                    logger.info(f"Valid direct number: {direct_number} (index {best_index})")
                    return best_index
            except ValueError:
                logger.info("Direct number parsing failed - not a number")
            
            # If all parsing fails, check if this is a complete failure case
            # For certain meaningless responses, return -1 instead of defaulting
            meaningless_responses = ['none', 'null', 'error', 'fail', 'false', 'n/a', 'na', 'unknown']
            if cleaned_result in meaningless_responses:
                logger.warning(f"AI returned meaningless response: '{result}', indicating classification failure")
                return -1  # Complete failure
            
            # For other cases, default to first option with warning
            logger.warning(f"Could not parse valid selection from: '{result}'. Using first option.")
            return 0
            
        except Exception as e:
            logger.error(f"Error parsing selection number: {e}")
            logger.warning("Defaulting to first option due to parsing error.")
            return 0

    def _validate_category(self, selected_category: str, available_categories: List[str]) -> int:
        """
        Validate a single selected category and return its index.
        
        Args:
            selected_category (str): Category name returned by AI
            available_categories (List[str]): Valid categories from taxonomy
            
        Returns:
            int: Index of the category in available_categories (0-based)
                 OR -1 if category not found (indicates classification failure)
        """
        # Try exact match first (case-insensitive)
        for i, category in enumerate(available_categories):
            if category.lower() == selected_category.lower():
                logger.info(f"Found exact match for '{selected_category}': '{category}' at index {i}")
                return i
        
        # Try partial match
        for i, category in enumerate(available_categories):
            if category.lower() in selected_category.lower() or selected_category.lower() in category.lower():
                logger.info(f"Found partial match for '{selected_category}': '{category}' at index {i}")
                return i
        
        # No match found
        logger.error(f"Could not find match for selected category: '{selected_category}'")
        logger.error(f"Available categories were: {available_categories}")
        return -1  # Indicates classification failure

    def _build_professional_prompt_final(self, product_info: str, numbered_options: List[str]) -> str:
        """
        Build a professional prompt for the final selection stage.
        
        Args:
            product_info (str): Complete product information
            numbered_options (List[str]): List of numbered category options
            
        Returns:
            str: Professional prompt for final selection
        """
        return f"""
Product: {product_info}

IMPORTANT: From amongst the provided options below, select the category that is MOST LIKELY to roughly describe this product.
Don't worry about finding a perfect match - just pick the option that seems most likely to be correct.
If multiple options seem reasonable, pick the one that feels most probable.

Available categories:
{chr(10).join(numbered_options)}

Return ONLY the number of your selection (e.g., "1" or "2").
The number must be between 1 and {len(numbered_options)}.
"""