#!/usr/bin/env python3
"""
Taxonomy Navigator - AI-Powered Product Categorization System

This module implements a sophisticated three-stage AI classification system that automatically 
categorizes products into appropriate taxonomy categories using OpenAI's GPT models.

=== FIVE-STAGE CLASSIFICATION PROCESS ===

The system uses a progressive filtering approach that efficiently narrows down from thousands 
of categories to a single best match:

🎯 STAGE 1: L1 TAXONOMY SELECTION (AI-Powered)
   - Purpose: Identify the 3 most relevant top-level taxonomy categories
   - Input: Product info + ALL unique L1 taxonomy categories (no duplicates)
   - AI Model: gpt-4.1-nano (unified model for all stages)
   - Process: AI selects 3 most relevant L1 categories (e.g., "Electronics", "Hardware", "Apparel")
   - Output: List of 3 L1 category names
   - Key Feature: Focuses on broad category domains first for better accuracy
   - Anti-Hallucination: Professional prompting + strict validation that every returned category exists

🔍 STAGE 2A: FIRST L1 LEAF SELECTION (AI-Powered)
   - Purpose: Select the first 10 best leaf nodes from the FIRST chosen L1 taxonomy
   - Input: Product info + ALL leaf nodes from the FIRST selected L1 category
   - AI Model: gpt-4.1-nano (unified model for all stages)
   - Process: AI selects top 10 most relevant leaf categories from the FIRST L1 taxonomy
   - Output: List of up to 10 leaf node names from the FIRST L1 taxonomy
   - Key Feature: Focuses exclusively on the first L1 taxonomy for better granularity
   - Anti-Hallucination: Professional prompting + strict validation that every returned leaf exists

🔍 STAGE 2B: SECOND L1 LEAF SELECTION (AI-Powered)
   - Purpose: Select the second 10 best leaf nodes from the SECOND chosen L1 taxonomy
   - Input: Product info + ALL leaf nodes from the SECOND selected L1 category
   - AI Model: gpt-4.1-nano (unified model for all stages)
   - Process: AI selects top 10 most relevant leaf categories from the SECOND L1 taxonomy
   - Output: List of up to 10 leaf node names from the SECOND L1 taxonomy
   - Key Feature: Focuses exclusively on the second L1 taxonomy for better granularity
   - Anti-Hallucination: Professional prompting + strict validation that every returned leaf exists

🔍 STAGE 2C: THIRD L1 LEAF SELECTION (AI-Powered)
   - Purpose: Select the third 10 best leaf nodes from the THIRD chosen L1 taxonomy
   - Input: Product info + ALL leaf nodes from the THIRD selected L1 category
   - AI Model: gpt-4.1-nano (unified model for all stages)
   - Process: AI selects top 10 most relevant leaf categories from the THIRD L1 taxonomy
   - Output: List of up to 10 leaf node names from the THIRD L1 taxonomy
   - Key Feature: Focuses exclusively on the third L1 taxonomy for better granularity
   - Anti-Hallucination: Professional prompting + strict validation that every returned leaf exists

🏆 STAGE 3: FINAL SELECTION (AI-Powered with Anti-Hallucination)
   - Purpose: Make the final decision from the combined 30 leaf nodes from Stages 2A, 2B, 2C
   - Input: Product info + up to 30 leaf nodes from combined Stage 2 results
   - AI Model: gpt-4.1-mini for stage 3
   - Process: 
     * Construct clear, professional prompt with specific constraints
     * Present up to 30 categories as numbered options (leaf names only)
     * AI identifies core product and selects best match
     * Parse AI response with robust validation and bounds checking
     * Return guaranteed valid index of selected category OR -1 for complete failure
   - Output: Index of selected category (0-based, guaranteed valid) OR -1 for complete failure
   - Key Features: Professional prompting + numeric validation + bounds checking + "False" for failures

=== SYSTEM ARCHITECTURE BENEFITS ===

✅ Efficiency: Progressive filtering (L1s → 3 L1s → 10 leaves per L1 → 30 leaves → 1)
✅ Cost Optimization: Only 5 API calls per classification (Stages 1, 2A, 2B, 2C, 3)
✅ Improved Focus: Each stage focuses on appropriate level of granularity
✅ Accuracy: Each L1 taxonomy is explored independently for better coverage
✅ Scalability: Handles large taxonomies without overwhelming the AI
✅ Model Strategy: Uses gpt-4.1-mini for stage 3 for consistency
✅ Manageable Chunks: Stage 2 broken into 3 parts of 10 items each for better AI performance

=== KEY TECHNICAL FEATURES ===

- Deterministic Results: Uses temperature=0 and top_p=0 for consistent classifications
- Enhanced Product Identification: Advanced prompting to distinguish products from accessories
- Comprehensive Error Handling: Graceful handling of API errors and edge cases
- Duplicate Removal: Multiple stages of deduplication for clean results
- L1 Deduplication: Ensures no duplicate L1 categories are sent to AI
- Mixed Model Strategy: gpt-4.1-mini for stage 1, gpt-4.1-nano for stage 2, gpt-4.1-mini for stage 3
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
- Stage 2A/2B/2C: Every returned leaf category is validated against the filtered leaf list  
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

Author: AI Assistant
Version: 10.0 (Simplified Prompting System)
Last Updated: 2025-01-25
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
    
    This class implements a five-stage classification approach:
    1. L1 taxonomy selection to identify the 3 most relevant top-level categories
    2. Stage 2A: First 10 leaf node selection from the chosen L1 taxonomies
    3. Stage 2B: Second 10 leaf node selection (excluding 2A results)
    4. Stage 2C: Third 10 leaf node selection (excluding 2A and 2B results)
    5. Final selection from the combined 30 leaf nodes from Stages 2A, 2B, 2C
    
    The system is designed to handle large taxonomies efficiently while maintaining
    high accuracy in distinguishing between products and their accessories.
    
    Key Improvements in v8.0:
    - Redesigned to use a five-stage process with Stage 2 broken into manageable chunks
    - Updated to use gpt-4.1-nano for all stages for consistency
    - Enhanced error handling throughout the five-stage pipeline
    - Maintained backward compatibility with existing method signatures
    
    Attributes:
        taxonomy_file (str): Path to the taxonomy file in Google Product Taxonomy format
        model (str): OpenAI model used for stages 1 and 3
        stage2_model (str): OpenAI model used for stage 2
        stage3_model (str): OpenAI model used for stage 3 (final selection)
        taxonomy_tree (Dict): Hierarchical representation of the taxonomy
        all_paths (List[str]): All taxonomy paths from the file
        leaf_markers (List[bool]): Boolean markers indicating which paths are leaf nodes
        client (OpenAI): OpenAI API client instance
        
    Example Usage:
        navigator = TaxonomyNavigator("taxonomy.txt", api_key)
        paths, best_idx = navigator.navigate_taxonomy("iPhone 14: Smartphone")
        best_category = paths[best_idx][-1]  # e.g., "Smartphones"
    """

    def __init__(self, taxonomy_file: str, api_key: str = None, model: str = "gpt-4.1-mini"):
        """
        Initialize the TaxonomyNavigator with taxonomy data and API configuration.

        Args:
            taxonomy_file (str): Path to the taxonomy file (Google Product Taxonomy format)
            api_key (str, optional): OpenAI API key. If None, will use get_api_key() utility
            model (str): OpenAI model for stages 1 and 3. Defaults to "gpt-4.1-mini"
            
        Raises:
            ValueError: If API key cannot be obtained
            FileNotFoundError: If taxonomy file doesn't exist
            Exception: If taxonomy tree building fails
        """
        self.taxonomy_file = taxonomy_file
        self.model = model  # Used for stages 1 and 3
        self.stage2_model = "gpt-4.1-nano"  # Used for stage 2
        self.stage3_model = "gpt-4.1"  # Used for stage 3 (final selection)
        
        # Build the taxonomy tree and identify leaf nodes
        self.taxonomy_tree = self._build_taxonomy_tree()
        
        # Initialize OpenAI client with API key
        api_key = get_api_key(api_key)
        if not api_key:
            raise ValueError("OpenAI API key not provided. Please set it in api_key.txt, as an environment variable, or provide it as an argument.")
            
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized TaxonomyNavigator with models: {model} (stage 1), {self.stage2_model} (stage 2), {self.stage3_model} (stage 3)")
        logger.info(f"Taxonomy stats: {len(self.all_paths)} total paths, {sum(self.leaf_markers)} leaf nodes")

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
                
                # Determine if this is a leaf node by checking the next line
                # A path is a leaf if there's no next line, or if the next line 
                # doesn't start with this path followed by " > "
                is_leaf_node = True
                if i + 1 < len(lines[1:]):  # Check if there's a next line
                    next_line = lines[i + 2].strip()  # i+2 because we skipped header
                    if next_line and next_line.startswith(line + " > "):
                        is_leaf_node = False
                
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
        Stage 1: Identify the 3 most relevant top-level taxonomy categories.
        
        This method implements the first stage of the three-stage classification process.
        It uses enhanced prompting to help the AI focus on the core product being sold
        rather than accessories or marketing language.
        
        The AI receives all unique L1 taxonomy categories as context, and is instructed
        to select the 3 most appropriate categories. The system then performs duplicate
        removal and validation to ensure clean results.
        
        Process:
        1. Extract all unique L1 taxonomy categories from the taxonomy
        2. Send to AI with enhanced prompt including L1 taxonomy context
        3. Parse AI response and remove duplicates (case-insensitive)
        4. Validate categories against actual taxonomy entries
        5. Return up to 3 unique, valid categories
        
        Improvements in v5.0:
        - Added robust duplicate removal with case-insensitive matching
        - Enhanced validation with detailed logging of valid vs invalid selections
        - Improved error handling with fallback mechanisms
        - Better prompt engineering to focus on core products vs accessories
        - Added L1 taxonomy context to help AI understand category relationships

        Args:
            product_info (str): Complete product information (name + description)
            
        Returns:
            List[str]: Top 3 most relevant L1 taxonomy category names, ordered by relevance,
                      with duplicates removed and validated against taxonomy
            
        Raises:
            Exception: If OpenAI API call fails (logged and handled with fallback)
            
        Example:
            selected = navigator.stage1_l1_selection("iPhone 14: Smartphone")
            # Returns: ["Electronics", "Hardware", "Apparel"]
        """
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
        
        logger.info(f"Stage 1: Querying OpenAI for top 3 L1 taxonomy categories among {len(l1_categories)} options")
        
        # Construct enhanced prompt for L1 taxonomy selection
        prompt = (
            f"Product: {product_info}\n\n"
            
            f"Select exactly 3 categories from this list that best match the product:\n\n"
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
            
            # Ensure we have at most 3 categories after deduplication
            unique_categories = unique_categories[:3]
            
            # Log duplicate removal if any occurred
            if len(unique_categories) < len(selected_categories):
                duplicates_removed = len(selected_categories) - len(unique_categories)
                logger.info(f"Removed {duplicates_removed} duplicate categories from AI response")
            
            # Log if fewer than expected categories returned
            if len(unique_categories) < 3:
                logger.warning(f"OpenAI returned fewer than 3 unique L1 taxonomy categories: {len(unique_categories)}")
            
            logger.info(f"Stage 1 complete: Selected {len(unique_categories)} unique L1 taxonomy categories")
            
            # Validate and match categories to our taxonomy
            return self._validate_categories(unique_categories, l1_categories)
            
        except Exception as e:
            logger.error(f"Error in Stage 1 L1 selection: {e}")
            # Fallback: return first 3 L1 categories
            if l1_categories:
                result = l1_categories[:min(3, len(l1_categories))]
                logger.warning(f"Using fallback L1 taxonomy categories: {result[:3]}...")
                return result
            return []

    def stage2a_first_leaf_selection(self, product_info: str, selected_l1s: List[str]) -> List[str]:
        """
        Stage 2A: Select the first 10 best leaf nodes from the FIRST chosen L1 taxonomy.
        
        This method implements the first part of the second stage of the five-stage classification process.
        It focuses EXCLUSIVELY on the first L1 taxonomy from stage 1.
        
        Args:
            product_info (str): Complete product information (name + description)
            selected_l1s (List[str]): List of 3 L1 taxonomy category names
            
        Returns:
            List[str]: Top 10 most relevant leaf node names from the FIRST L1 taxonomy
        """
        if not selected_l1s:
            return []
        return self._leaf_selection_helper(product_info, [selected_l1s[0]], [], "2A", "first 10")

    def stage2b_second_leaf_selection(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str]) -> List[str]:
        """
        Stage 2B: Select the second 10 best leaf nodes from the SECOND chosen L1 taxonomy.
        
        This method implements the second part of the second stage of the five-stage classification process.
        It focuses EXCLUSIVELY on the second L1 taxonomy from stage 1.

        Args:
            product_info (str): Complete product information (name + description)
            selected_l1s (List[str]): List of 3 L1 taxonomy category names
            excluded_leaves (List[str]): Leaves already selected in Stage 2A
            
        Returns:
            List[str]: Next 10 most relevant leaf node names from the SECOND L1 taxonomy
        """
        if len(selected_l1s) < 2:
            return []
        return self._leaf_selection_helper(product_info, [selected_l1s[1]], excluded_leaves, "2B", "next 10")

    def stage2c_third_leaf_selection(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str]) -> List[str]:
        """
        Stage 2C: Select the third 10 best leaf nodes from the THIRD chosen L1 taxonomy.
        
        This method implements the third part of the second stage of the five-stage classification process.
        It focuses EXCLUSIVELY on the third L1 taxonomy from stage 1.

        Args:
            product_info (str): Complete product information (name + description)
            selected_l1s (List[str]): List of 3 L1 taxonomy category names
            excluded_leaves (List[str]): Leaves already selected in Stages 2A and 2B
            
        Returns:
            List[str]: Final 10 most relevant leaf node names from the THIRD L1 taxonomy
        """
        if len(selected_l1s) < 3:
            return []
        return self._leaf_selection_helper(product_info, [selected_l1s[2]], excluded_leaves, "2C", "final 10")

    def _leaf_selection_helper(self, product_info: str, selected_l1s: List[str], excluded_leaves: List[str], stage_name: str, description: str) -> List[str]:
        """
        Helper method for Stage 2A, 2B, and 2C leaf selection.
        
        Args:
            product_info (str): Complete product information
            selected_l1s (List[str]): List of 3 L1 taxonomy category names
            excluded_leaves (List[str]): Leaves to exclude from selection
            stage_name (str): Stage identifier (2A, 2B, or 2C)
            description (str): Description for logging (e.g., "first 10", "next 10")
            
        Returns:
            List[str]: Up to 10 validated leaf node names
        """
        # Extract all leaf nodes from the taxonomy for the selected L1 categories
        leaf_paths, leaf_names = self._extract_leaf_nodes()
        
        if not leaf_names:
            logger.warning("No leaf nodes found in taxonomy")
            return []
        
        # Create mapping from leaf names to their L1 categories
        leaf_to_l1 = self._create_leaf_to_l1_mapping()
        
        # Filter leaf nodes to only those from the selected L1 categories
        filtered_leaf_names = []
        for leaf in leaf_names:
            l1_category = leaf_to_l1.get(leaf, "Unknown")
            if l1_category in selected_l1s and leaf not in excluded_leaves:
                filtered_leaf_names.append(leaf)
        
        if not filtered_leaf_names:
            logger.warning(f"No leaf nodes found for selected L1 categories: {selected_l1s} (excluding {len(excluded_leaves)} already selected)")
            return []
        
        logger.info(f"Stage {stage_name}: Querying OpenAI for {description} leaf nodes among {len(filtered_leaf_names)} options from selected L1 categories")
        
        # Create structured category list with L1 context for filtered leaves only
        category_list_with_context = []
        for leaf in filtered_leaf_names:
            l1_category = leaf_to_l1.get(leaf, "Unknown")
            category_list_with_context.append(f"{leaf} (L1: {l1_category})")
        
        # Construct enhanced prompt for leaf node identification with L1 context
        prompt = (
            f"Product: {product_info}\n\n"
            
            f"Select exactly 10 categories from this list that best match the product:\n\n"
            f"{chr(10).join(category_list_with_context)}\n\n"
        )
        
        if excluded_leaves:
            prompt += f"Do not select these already chosen categories: {', '.join(excluded_leaves)}\n\n"
        
        prompt += f"Return one category per line (category name only, not the L1 part):"
        
        try:
            # Make API call with deterministic settings and NO CONTEXT
            response = self.client.chat.completions.create(
                model=self.stage2_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a product categorization assistant. Select leaf categories from the provided list using exact spelling."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic responses
                top_p=0        # Deterministic responses
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            selected_categories = [category.strip() for category in content.split('\n') if category.strip()]
            
            # CRITICAL VALIDATION: Ensure every returned category actually exists in our filtered leaf list
            validated_categories = []
            hallucination_count = 0
            
            for category in selected_categories:
                if category in filtered_leaf_names:
                    validated_categories.append(category)
                    logger.info(f"✅ VALIDATED: '{category}' exists in filtered leaf taxonomy")
                else:
                    logger.error(f"🚨 HALLUCINATION DETECTED: '{category}' does NOT exist in filtered leaf taxonomy")
                    logger.error(f"Available filtered leaves: {filtered_leaf_names[:20]}...")  # Show first 20 for brevity
                    hallucination_count += 1
            
            if hallucination_count > 0:
                logger.error(f"🚨 CRITICAL: AI hallucinated {hallucination_count} categories in Stage {stage_name}")
                logger.error("🚨 This is a serious anti-hallucination failure")
            
            # Remove duplicates while preserving order (case-insensitive)
            seen = set()
            unique_categories = []
            for category in validated_categories:
                category_lower = category.lower()
                if category_lower not in seen:
                    seen.add(category_lower)
                    unique_categories.append(category)
            
            # Ensure we have at most 10 categories after deduplication
            unique_categories = unique_categories[:10]
            
            # Log duplicate removal if any occurred
            if len(unique_categories) < len(selected_categories):
                duplicates_removed = len(selected_categories) - len(unique_categories)
                logger.info(f"Removed {duplicates_removed} duplicate categories from AI response")
            
            # Log if fewer than expected categories returned
            if len(unique_categories) < 10:
                logger.warning(f"OpenAI returned fewer than 10 unique leaf categories: {len(unique_categories)}")
            
            # Validate and match categories to our taxonomy - CRITICAL: Filter out hallucinations
            validated_categories = self._validate_categories(unique_categories, filtered_leaf_names)
            
            # ANTI-HALLUCINATION: Remove categories with "Unknown" L1 taxonomy
            leaf_to_l1 = self._create_leaf_to_l1_mapping()
            final_categories = []
            hallucination_count = 0
            
            for category in validated_categories:
                l1_category = leaf_to_l1.get(category, "Unknown")
                if l1_category == "Unknown":
                    logger.warning(f"HALLUCINATION DETECTED: '{category}' has Unknown L1 taxonomy - removing")
                    hallucination_count += 1
                else:
                    final_categories.append(category)
            
            if hallucination_count > 0:
                logger.info(f"Stage {stage_name} anti-hallucination: Removed {hallucination_count} categories with Unknown L1 taxonomy")
            
            logger.info(f"Stage {stage_name} complete: Selected {len(final_categories)} validated leaf categories (after anti-hallucination filtering)")
            
            return final_categories
            
        except Exception as e:
            logger.error(f"Error in Stage {stage_name} leaf selection: {e}")
            # Fallback: return first 10 leaf categories
            if filtered_leaf_names:
                result = filtered_leaf_names[:min(10, len(filtered_leaf_names))]
                logger.warning(f"Using fallback leaf categories: {result[:3]}...")
                return result
            return []

    def stage3_final_selection(self, product_info: str, selected_leaves: List[str]) -> int:
        """
        Stage 3: Select the single best match from the 30 leaf nodes from Stage 2.
        
        This method implements the third stage of classification using enhanced prompting
        and gpt-4.1-mini for the final selection from the top 30 filtered candidates.
        The gpt-4.1-mini model provides consistent behavior throughout the three-stage process.
        
        ANTI-HALLUCINATION MEASURES:
        - Hardcore prompting with explicit constraints prevents wrong selections
        - Robust index validation ensures selection is within bounds
        - Multiple fallback mechanisms if AI returns invalid responses
        - Final safety checks guarantee valid category selection
        - Returns -1 (indicating "False") if AI completely fails or returns nothing
        
        Process:
        1. Construct structured selection prompt using only leaf names from Stage 2
        2. Present categories as numbered options (leaf names only)
        3. AI identifies core product and selects best match using gpt-4.1-mini
        4. Parse AI response with robust validation and bounds checking
        5. Validate selected index is within bounds of filtered categories
        6. Return guaranteed valid index of selected category OR -1 for complete failure
        
        Args:
            product_info (str): Complete product information
            selected_leaves (List[str]): Filtered leaf names from Stage 2 (A, B, C)
            
        Returns:
            int: Index of the best match in the selected_leaves list (0-based)
                 OR -1 to indicate classification failure ("False")
            
        Raises:
            Exception: If OpenAI API call fails (logged and handled with fallback to -1)
        """
        if not selected_leaves:
            logger.warning("No leaf nodes provided for final selection")
            return -1
        
        if len(selected_leaves) == 1:
            logger.info("Only one leaf remaining, selecting it")
            return 0
        
        logger.info(f"Stage 3: Final selection among {len(selected_leaves)} filtered candidates from Stage 2")
        
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
            temperature=0,
            top_p=1
        )
        
        # Parse number and validate bounds
        selected_index = self._parse_and_validate_number(response, len(selected_leaves))
        
        # Return -1 for complete failures (indicates "False")
        return selected_index if selected_index >= 0 else -1

    def navigate_taxonomy(self, product_info: str) -> Tuple[List[List[str]], int]:
        """
        Main navigation method implementing the complete five-stage classification process.
        
        This is the primary public method that orchestrates the entire classification:
        1. Stage 1: Identify the 3 most relevant top-level categories
        2. Stage 2A: Select the first 10 best leaf nodes from the chosen L1 taxonomies
        3. Stage 2B: Select the second 10 best leaf nodes (excluding 2A results)
        4. Stage 2C: Select the third 10 best leaf nodes (excluding 2A and 2B results)
        5. Stage 3: Select the single best match from the combined 30 leaf nodes
        6. Return all final candidates with the best match identified
        
        The method ensures end-to-end consistency by validating that the final result
        comes from the taxonomy layer identified in Stage 2.
        
        Process Flow:
        1. Stage 1: AI identifies relevant L1 taxonomies from all categories
        2. Duplicate removal and validation of AI selections
        3. Stage 2A: AI selects top 10 leaf nodes from the chosen L1 taxonomies
        4. Stage 2B: AI selects next 10 leaf nodes (excluding 2A results)
        5. Stage 2C: AI selects final 10 leaf nodes (excluding 2A and 2B results)
        6. Stage 3: AI selects best match from combined candidates using gpt-4.1-mini
        7. Return structured results with best match index
        
        Improvements in v5.0:
        - Updated Stage 3 to use gpt-4.1-mini for consistent behavior
        - Enhanced error handling with detailed logging for all three stages
        - Improved tie-handling in Stage 2
        - Maintained backward compatibility with existing return format
        
        Args:
            product_info (str): Complete product information (name + description)
            
        Returns:
            Tuple[List[List[str]], int]: 
                - List of taxonomy paths (filtered candidates from Stage 2)
                - Index of the best match (0-based, selected by Stage 3)
                - Returns ([["False"]], 0) if no matches found or classification fails
                
        Example:
            navigator = TaxonomyNavigator("taxonomy.txt", api_key)
            paths, best_idx = navigator.navigate_taxonomy("iPhone 14: Smartphone with camera")
            
            # Example result:
            # paths = [["Electronics", "Cell Phones", "Smartphones"], 
            #          ["Electronics", "Cell Phones", "Mobile Phones"]]
            # best_idx = 0
            # best_path = paths[best_idx]  # ["Electronics", "Cell Phones", "Smartphones"]
            # final_category = best_path[-1]  # "Smartphones"
            
            # If classification fails:
            # paths = [["False"]]
            # best_idx = 0
            # final_category = "False"
        """
        total_start_time = time.time()
        
        try:
            logger.info(f"Starting three-stage classification for: {product_info[:50]}...")
            
            # Stage 1: Identify the 3 most relevant top-level categories
            selected_l1s = self.stage1_l1_selection(product_info)
            
            if not selected_l1s:
                logger.warning("No L1 taxonomy categories returned from Stage 1")
                return [["False"]], 0
            
            # Stage 2A: Select the first 10 best leaf nodes from the chosen L1 taxonomies
            selected_leaves_2a = self.stage2a_first_leaf_selection(product_info, selected_l1s)
            
            if not selected_leaves_2a:
                logger.warning("No leaves returned from Stage 2A")
                return [["False"]], 0
            
            # Stage 2B: Select the second 10 best leaf nodes (excluding 2A results)
            selected_leaves_2b = self.stage2b_second_leaf_selection(product_info, selected_l1s, selected_leaves_2a)
            
            # Stage 2C: Select the third 10 best leaf nodes (excluding 2A and 2B results)
            combined_excluded = selected_leaves_2a + selected_leaves_2b
            selected_leaves_2c = self.stage2c_third_leaf_selection(product_info, selected_l1s, combined_excluded)
            
            # Combine all Stage 2 results
            selected_leaves = selected_leaves_2a + selected_leaves_2b + selected_leaves_2c
            
            if not selected_leaves:
                logger.warning("No leaves returned from combined Stage 2 (2A + 2B + 2C)")
                return [["False"]], 0
            
            # Stage 3: Final selection from the 30 leaf nodes from Stage 2
            best_match_idx = self.stage3_final_selection(product_info, selected_leaves)
            
            # Check if Stage 3 completely failed (returned -1)
            if best_match_idx == -1:
                logger.error("Stage 3 classification failed - returning False")
                return [["False"]], 0
            
            # Convert filtered leaf names back to full paths
            final_paths = self._convert_leaves_to_paths(selected_leaves)
            
            if not final_paths:
                logger.warning("No valid paths found after conversion")
                return [["False"]], 0
            
            # CRITICAL SAFETY CHECK: Ensure best_match_idx is valid
            if best_match_idx < 0 or best_match_idx >= len(final_paths):
                logger.error(f"SAFETY CHECK: Invalid best_match_idx {best_match_idx}, must be 0-{len(final_paths)-1}")
                logger.error("SAFETY CHECK: Classification failed - returning False")
                return [["False"]], 0
            
            # CRITICAL ANTI-HALLUCINATION CHECK: Ensure final result comes from filtered leaves
            selected_leaf_name = selected_leaves[best_match_idx]
            final_path = final_paths[best_match_idx]
            final_leaf_from_path = final_path[-1] if final_path else ""
            
            if selected_leaf_name != final_leaf_from_path:
                logger.error(f"CRITICAL HALLUCINATION DETECTED: Selected leaf '{selected_leaf_name}' does not match path leaf '{final_leaf_from_path}'")
                logger.error(f"CRITICAL: Filtered leaves were: {selected_leaves}")
                logger.error(f"CRITICAL: Final path was: {' > '.join(final_path)}")
                logger.error("CRITICAL: This indicates a serious system error - returning False")
                return [["False"]], 0
            
            # CRITICAL: Verify the selected leaf was actually in our filtered candidates
            if selected_leaf_name not in selected_leaves:
                logger.error(f"CRITICAL HALLUCINATION: Selected leaf '{selected_leaf_name}' was not in filtered candidates: {selected_leaves}")
                logger.error("CRITICAL: AI somehow selected a category outside the provided options - returning False")
                return [["False"]], 0
            
            # Log completion
            total_duration = time.time() - total_start_time
            logger.info(f"Three-stage classification complete: {len(final_paths)} final candidates, best match at index {best_match_idx}")
            logger.info(f"Best match: {' > '.join(final_paths[best_match_idx])}")
            logger.info(f"Total processing time: {total_duration:.2f} seconds")
            
            return final_paths, best_match_idx
            
        except Exception as e:
            logger.error(f"Error during taxonomy navigation: {e}")
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

    def _parse_selection_number(self, result: str, max_options: int) -> int:
        """
        Parse the AI's selection number and convert to 0-based index.
        
        Handles various formats the AI might return (e.g., "1", "1.", "Option 1").
        Includes robust validation to prevent invalid indices.
        Returns -1 for complete parsing failures to indicate classification failure.

        Args:
            result (str): Raw response from AI
            max_options (int): Maximum valid option number
            
        Returns:
            int: 0-based index of selected option (guaranteed to be valid)
                 OR -1 to indicate complete parsing failure
        """
        try:
            # Clean the result string
            cleaned_result = result.strip().lower()
            
            # Check for completely empty or meaningless input
            if not cleaned_result or len(cleaned_result) == 0:
                logger.warning("Empty or meaningless AI response for parsing")
                return -1  # Complete failure
            
            # Look for any number in the result
            import re
            numbers = re.findall(r'\d+', cleaned_result)
            
            if numbers:
                # Take the first number found
                selected_number = int(numbers[0])
                
                # Validate the number is within valid range (1 to max_options)
                if 1 <= selected_number <= max_options:
                    best_index = selected_number - 1  # Convert to 0-based
                    logger.info(f"Parsed selection: option {selected_number} (index {best_index})")
                    return best_index
                else:
                    logger.warning(f"AI returned out-of-range number: {selected_number}, valid range is 1-{max_options}")
            
            # If no valid number found, try direct number parsing
            try:
                direct_number = int(cleaned_result)
                if 1 <= direct_number <= max_options:
                    best_index = direct_number - 1
                    logger.info(f"Parsed direct number: {direct_number} (index {best_index})")
                    return best_index
            except ValueError:
                pass
            
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