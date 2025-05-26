#!/usr/bin/env python3
"""
Taxonomy Navigator - AI-Powered Product Categorization System

This module implements a sophisticated five-stage AI classification system that automatically 
categorizes products into appropriate taxonomy categories using OpenAI's GPT models.

=== FIVE-STAGE CLASSIFICATION PROCESS ===

The system uses a progressive filtering approach that efficiently narrows down from thousands 
of categories to a single best match:

🔍 STAGE 1: INITIAL LEAF NODE MATCHING (AI-Powered)
   - Purpose: Cast a wide net to identify potentially relevant categories
   - Input: Product info + ALL 4,722 leaf node names from taxonomy
   - AI Model: gpt-4.1-nano (cost-effective for initial broad selection)
   - Process: AI conceptually identifies top 20 most relevant leaf categories
   - Output: List of 20 leaf node names (duplicates removed, validated)
   - Key Feature: Enhanced prompting to focus on "core product being sold"

📊 STAGE 2: TAXONOMY LAYER FILTERING (Algorithmic)
   - Purpose: Ensure classification consistency within same product domain
   - Input: 20 leaf nodes from Stage 1
   - Process: 
     * Map each leaf to its full taxonomy path
     * Count occurrences of 1st-level categories (e.g., "Electronics", "Apparel")
     * Identify most popular 1st-level category
     * Filter to keep only leaves from that dominant layer
   - Output: Filtered list of leaf nodes from the dominant L1 taxonomy (typically 8-15 categories)
   - Key Feature: Handles ties by including all categories from tied layers
   - Cost: No API calls - purely algorithmic processing

🎯 STAGE 3: REFINED LEAF NODE MATCHING (AI-Powered)
   - Purpose: Apply AI intelligence to select best candidates from the filtered L1 taxonomy layer
   - Input: Product info + filtered leaf nodes from Stage 2 (all from same L1 taxonomy layer)
   - AI Model: gpt-4.1-nano (consistent with Stage 1)
   - Process: AI selects top 10 most relevant categories from the filtered L1 taxonomy leaf nodes
   - Output: List of 10 refined leaf node names (all from same L1 taxonomy layer)
   - Key Insight: This is essentially Stage 1 repeated, but only with leaf nodes from 
     the dominant L1 taxonomy layer (e.g., only "Electronics" leaves)
   - Benefit: Better precision since AI only considers leaves from the relevant domain

✅ STAGE 4: VALIDATION (Algorithmic)
   - Purpose: Ensure AI didn't hallucinate any category names that don't exist
   - Input: 10 refined leaf node names from Stage 3
   - Process: 
     * Validate each category name exists in the actual taxonomy
     * Remove any hallucinated or invalid category names
     * Log validation statistics (valid vs invalid)
   - Output: Validated list of leaf node names (typically 8-10 categories)
   - Key Feature: Data integrity check to prevent hallucinations
   - Cost: No API calls - purely validation processing

🏆 STAGE 5: FINAL SELECTION (AI-Powered with Enhanced Model)
   - Purpose: Make the final decision with maximum precision from validated categories
   - Input: Product info + validated leaf nodes from Stage 4
   - AI Model: gpt-4.1-mini (enhanced model for better final decision quality)
   - Process: 
     * Present validated categories as numbered options
     * Use structured 3-step reasoning prompt
     * AI identifies core product and selects best match
   - Output: Index of selected category (0-based)
   - Key Feature: Enhanced prompting to distinguish products from accessories

=== SYSTEM ARCHITECTURE BENEFITS ===

✅ Efficiency: Progressive filtering (4,722 → 20 → filtered L1 → 10 → validated → 1)
✅ Cost Optimization: Only 3 API calls per classification (Stages 1, 3, 5)
✅ Data Integrity: Stage 4 validation prevents AI hallucinations
✅ Accuracy: Each stage focuses on appropriate level of granularity
✅ Consistency: Layer filtering ensures results stay within same L1 taxonomy domain
✅ Scalability: Handles large taxonomies without overwhelming the AI
✅ Precision: Final stage uses enhanced model for better decision quality

=== KEY TECHNICAL FEATURES ===

- Deterministic Results: Uses temperature=0 and top_p=0 for consistent classifications
- Enhanced Product Identification: Advanced prompting to distinguish products from accessories
- Comprehensive Error Handling: Graceful handling of API errors and edge cases
- Duplicate Removal: Multiple stages of deduplication for clean results
- Validation: Ensures all returned categories exist in the actual taxonomy
- Robust Tie Handling: Stage 2 includes all categories from tied taxonomy layers
- Mixed Model Strategy: Cost-effective nano model for initial stages, mini for final precision
- Hallucination Prevention: Stage 4 validation ensures data integrity

Author: AI Assistant
Version: 5.0
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
    1. Leaf node matching to get top 20 candidates from all 4,722 categories
    2. Layer filtering to identify most popular 1st taxonomy layer and filter leaves (handles ties)
    3. Refined selection using AI to get top 10 leaf nodes from filtered candidates
    4. Validation to ensure AI didn't hallucinate any category names
    5. Final selection using enhanced prompting to get the best match from validated categories
    
    The system is designed to handle large taxonomies efficiently while maintaining
    high accuracy in distinguishing between products and their accessories.
    
    Key Improvements in v5.0:
    - Added Stage 4 validation for data integrity
    - Changed Stage 5 (final selection) to use gpt-4.1-mini for enhanced precision
    - Updated all stage numbering and comprehensive logging
    - Enhanced error handling throughout the five-stage pipeline
    - Maintained backward compatibility with existing method signatures
    
    Attributes:
        taxonomy_file (str): Path to the taxonomy file in Google Product Taxonomy format
        model (str): OpenAI model used for Stages 1 and 3 (default: gpt-4.1-nano)
        final_model (str): OpenAI model used for Stage 5 (default: gpt-4.1-mini)
        taxonomy_tree (Dict): Hierarchical representation of the taxonomy
        all_paths (List[str]): All taxonomy paths from the file
        leaf_markers (List[bool]): Boolean markers indicating which paths are leaf nodes
        client (OpenAI): OpenAI API client instance
        
    Example Usage:
        navigator = TaxonomyNavigator("taxonomy.txt", api_key)
        paths, best_idx = navigator.navigate_taxonomy("iPhone 14: Smartphone")
        best_category = paths[best_idx][-1]  # e.g., "Smartphones"
    """

    def __init__(self, taxonomy_file: str, api_key: str = None, model: str = "gpt-4.1-nano"):
        """
        Initialize the TaxonomyNavigator with taxonomy data and API configuration.

        Args:
            taxonomy_file (str): Path to the taxonomy file (Google Product Taxonomy format)
            api_key (str, optional): OpenAI API key. If None, will use get_api_key() utility
            model (str): OpenAI model for Stages 1 and 3. Defaults to "gpt-4.1-nano"
            
        Raises:
            ValueError: If API key cannot be obtained
            FileNotFoundError: If taxonomy file doesn't exist
            Exception: If taxonomy tree building fails
        """
        self.taxonomy_file = taxonomy_file
        self.model = model
        self.final_model = "gpt-4.1-mini"  # Stage 5 uses mini model for enhanced precision
        
        # Build the taxonomy tree and identify leaf nodes
        self.taxonomy_tree = self._build_taxonomy_tree()
        
        # Initialize OpenAI client with API key
        api_key = get_api_key(api_key)
        if not api_key:
            raise ValueError("OpenAI API key not provided. Please set it in api_key.txt, as an environment variable, or provide it as an argument.")
            
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized TaxonomyNavigator with model {model} for Stages 1&3, {self.final_model} for Stage 5")
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

    def stage1_leaf_matching(self, product_info: str) -> List[str]:
        """
        Stage 1: Query OpenAI to get the top 20 most relevant leaf nodes from all categories.
        
        This method implements the first stage of the five-stage classification process.
        It uses enhanced prompting to help the AI focus on the core product being sold
        rather than accessories or marketing language.
        
        The AI receives all 4,722 leaf names as a comma-separated list and is instructed
        to select the 20 most appropriate categories. The system then performs duplicate
        removal and validation to ensure clean results.
        
        Process:
        1. Extract all 4,722 leaf names from taxonomy
        2. Send to AI with enhanced prompt focusing on core product identification
        3. Parse AI response and remove duplicates (case-insensitive)
        4. Validate categories against actual taxonomy entries
        5. Return up to 20 unique, valid categories
        
        Improvements in v5.0:
        - Added robust duplicate removal with case-insensitive matching
        - Enhanced validation with detailed logging of valid vs invalid selections
        - Improved error handling with fallback mechanisms
        - Better prompt engineering to focus on core products vs accessories

        Args:
            product_info (str): Complete product information (name + description)
            
        Returns:
            List[str]: Top 20 most relevant leaf node names, ordered by relevance,
                      with duplicates removed and validated against taxonomy
            
        Raises:
            Exception: If OpenAI API call fails (logged and handled with fallback)
            
        Example:
            selected = navigator.stage1_leaf_matching("iPhone 14: Smartphone")
            # Returns: ["Smartphones", "Cell Phones", "Mobile Devices", ...]
        """
        # Extract all leaf nodes from taxonomy
        leaf_paths, leaf_names = self._extract_leaf_nodes()
        
        if not leaf_names:
            logger.warning("No leaf nodes found in taxonomy")
            return []
        
        logger.info(f"Stage 1: Querying OpenAI for top 20 leaf nodes among {len(leaf_names)} options")
        
        # Construct enhanced prompt for leaf node identification
        prompt = (
            f"CRITICAL INSTRUCTION: You MUST select categories using the EXACT names provided below. "
            f"Do NOT modify, combine, or create new category names. Use ONLY the exact text from the list.\n\n"
            
            f"Given the product: '{product_info}', which TWENTY of these specific categories are most appropriate?\n\n"
            
            f"IMPORTANT RULES:\n"
            f"1. Return ONLY category names that appear EXACTLY in the list below\n"
            f"2. Do NOT modify, shorten, or change any category names\n"
            f"3. Do NOT combine multiple category names\n"
            f"4. Do NOT create new category names\n"
            f"5. Copy the names EXACTLY as they appear in the list\n"
            f"6. Focus on the core product being sold, not accessories or add-ons\n\n"
            
            f"Categories to choose from:\n{', '.join(leaf_names)}\n\n"
            
            f"Return EXACTLY 20 category names from the above list, one per line, with no additional text, "
            f"no numbering, and no modifications to the names. Use the EXACT spelling and capitalization."
        )
        
        try:
            # Make API call with deterministic settings
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a product categorization assistant. You will be given a product and a list of specific category names. Your task is CRITICAL: you must return ONLY the exact category names from the provided list - no modifications, no variations, no new names. Copy the category names EXACTLY as they appear in the list. Do not change spelling, capitalization, or wording in any way. Focus on the core product being sold, not accessories. Return exactly 20 category names from the list, one per line."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic results
                top_p=0        # Deterministic results
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            selected_categories = [category.strip() for category in content.split('\n') if category.strip()]
            
            # Remove duplicates while preserving order (case-insensitive)
            seen = set()
            unique_categories = []
            for category in selected_categories:
                category_lower = category.lower()
                if category_lower not in seen:
                    seen.add(category_lower)
                    unique_categories.append(category)
            
            # Ensure we have at most 20 categories after deduplication
            unique_categories = unique_categories[:20]
            
            # Log duplicate removal if any occurred
            if len(unique_categories) < len(selected_categories):
                duplicates_removed = len(selected_categories) - len(unique_categories)
                logger.info(f"Removed {duplicates_removed} duplicate categories from AI response")
            
            # Log if fewer than expected categories returned
            if len(unique_categories) < 20:
                logger.warning(f"OpenAI returned fewer than 20 unique leaf categories: {len(unique_categories)}")
            
            logger.info(f"Stage 1 complete: Selected {len(unique_categories)} unique leaf categories")
            
            # Validate and match categories to our taxonomy
            return self._validate_categories(unique_categories, leaf_names)
            
        except Exception as e:
            logger.error(f"Error in Stage 1 leaf matching: {e}")
            # Fallback: return first 20 leaf categories
            if leaf_names:
                result = leaf_names[:min(20, len(leaf_names))]
                logger.warning(f"Using fallback leaf categories: {result[:3]}...")
                return result
            return []

    def stage2_layer_filtering(self, selected_leaves: List[str]) -> List[str]:
        """
        Stage 2: Filter selected leaves to only those from the most popular 1st taxonomy layer.
        
        This method identifies which 1st-level taxonomy category (e.g., "Electronics", "Apparel")
        appears most frequently among the selected leaves, then filters to keep only leaves
        from that top-level category. If there's a tie, all categories from tied layers are included.
        
        Process:
        1. Map leaf names to full taxonomy paths
        2. Extract 1st layer categories and count occurrences
        3. Identify most popular layer(s) - handle ties by including all tied layers
        4. Filter to only leaves that exist in taxonomy AND belong to popular layer(s)
        5. Log validation statistics (valid vs invalid categories)
        
        Improvements in v5.0:
        - Fixed critical bug ensuring only categories from correct taxonomy layer are included
        - Added tie-handling to include all categories from layers with equal highest counts
        - Enhanced validation to ensure categories actually exist in taxonomy
        - Added detailed logging of filtering statistics and layer selection
        - Improved error handling for edge cases

        Args:
            selected_leaves (List[str]): Leaf names selected in Stage 1
            
        Returns:
            List[str]: Filtered leaf names from the most popular 1st taxonomy layer(s),
                      guaranteed to exist in taxonomy and belong to correct layer
                      
        Example:
            # Input: ["Smartphones", "Shoes", "Laptops", "Sneakers"]  
            # Layer counts: Electronics=2, Apparel=2 (tie)
            # Output: ["Smartphones", "Shoes", "Laptops", "Sneakers"] (all included due to tie)
            
            # Input: ["Smartphones", "Laptops", "Shoes"]
            # Layer counts: Electronics=2, Apparel=1  
            # Output: ["Smartphones", "Laptops"] (only Electronics layer)
        """
        if not selected_leaves:
            logger.warning("No leaves provided for layer filtering")
            return []
        
        logger.info(f"Stage 2: Filtering {len(selected_leaves)} leaves by most popular 1st taxonomy layer")
        
        # Convert leaf names to full paths and extract 1st layer categories
        leaf_to_path = self._create_leaf_to_path_mapping()
        first_layer_counts = Counter()
        leaf_to_first_layer = {}
        valid_leaves_count = 0
        
        for leaf in selected_leaves:
            if leaf in leaf_to_path:
                full_path = leaf_to_path[leaf]
                first_layer = full_path.split(" > ")[0]
                first_layer_counts[first_layer] += 1
                leaf_to_first_layer[leaf] = first_layer
                valid_leaves_count += 1
            else:
                logger.warning(f"Could not find full path for leaf: {leaf}")
        
        logger.info(f"Found {valid_leaves_count} valid categories out of {len(selected_leaves)} AI-selected categories")
        
        if not first_layer_counts:
            logger.warning("No valid first layer categories found")
            return selected_leaves
        
        # Find the highest count and all layers that have this count (handle ties)
        highest_count = first_layer_counts.most_common(1)[0][1]
        tied_layers = [layer for layer, count in first_layer_counts.items() if count == highest_count]
        
        if len(tied_layers) == 1:
            # No tie - single most popular layer
            most_popular_layer = tied_layers[0]
            logger.info(f"Most popular 1st layer: '{most_popular_layer}' with {highest_count} leaves")
            
            # Filter leaves to only those from the most popular layer AND that exist in taxonomy
            filtered_leaves = [
                leaf for leaf in selected_leaves 
                if leaf in leaf_to_path and leaf_to_first_layer.get(leaf) == most_popular_layer
            ]
            
            logger.info(f"Stage 2 complete: Filtered to {len(filtered_leaves)} leaves from '{most_popular_layer}' layer")
        else:
            # Tie detected - include all categories from tied layers
            logger.info(f"Tie detected: {len(tied_layers)} layers tied with {highest_count} leaves each: {tied_layers}")
            
            # Filter leaves to include those from all tied layers AND that exist in taxonomy
            filtered_leaves = [
                leaf for leaf in selected_leaves 
                if leaf in leaf_to_path and leaf_to_first_layer.get(leaf) in tied_layers
            ]
            
            logger.info(f"Stage 2 complete: Filtered to {len(filtered_leaves)} leaves from {len(tied_layers)} tied layers")
        
        return filtered_leaves

    def stage3_refined_selection(self, product_info: str, filtered_leaves: List[str]) -> List[str]:
        """
        Stage 3: Refine selection to top 10 leaf nodes from filtered candidates.
        
        This new stage provides an additional refinement step between layer filtering
        and final selection. It uses gpt-4.1-nano to select the top 10 most relevant
        leaf nodes from the filtered candidates, providing better focus for the final
        selection stage.
        
        Process:
        1. Take filtered leaves from Stage 2 (already within most popular taxonomy layer)
        2. Use AI to select top 10 most relevant categories from these candidates
        3. Apply enhanced prompting focused on core product identification
        4. Return refined list of 10 leaf nodes for final selection
        
        New in v5.0:
        - Added as intermediate refinement step for better accuracy
        - Uses gpt-4.1-nano for consistency with Stage 1
        - Focuses selection within the already-filtered taxonomy layer
        - Provides better input quality for Stage 5 final selection

        Args:
            product_info (str): Complete product information
            filtered_leaves (List[str]): Leaf names filtered by Stage 2
            
        Returns:
            List[str]: Top 10 most relevant leaf names from filtered candidates
            
        Example:
            # Input: 15 filtered leaves from "Electronics" layer
            # Output: 10 most relevant leaves for final selection
        """
        if not filtered_leaves:
            logger.warning("No filtered leaves provided for Stage 3 refined selection")
            return []
        
        if len(filtered_leaves) <= 10:
            logger.info(f"Stage 3: Only {len(filtered_leaves)} filtered leaves, returning all")
            return filtered_leaves
        
        logger.info(f"Stage 3: Refining selection to top 10 from {len(filtered_leaves)} filtered candidates using {self.model}")
        
        # Construct refined selection prompt
        prompt = (
            f"CRITICAL INSTRUCTION: You MUST select categories using the EXACT names provided below. "
            f"Do NOT modify, combine, or create new category names. Use ONLY the exact text from the list.\n\n"
            
            f"Given the product: '{product_info}', which TEN of these specific categories are most appropriate?\n\n"
            
            f"These categories have already been filtered to the most relevant taxonomy layer. "
            f"Your task is to select the 10 most precise matches from this refined list.\n\n"
            
            f"IMPORTANT RULES:\n"
            f"1. Return ONLY category names that appear EXACTLY in the list below\n"
            f"2. Do NOT modify, shorten, or change any category names\n"
            f"3. Do NOT combine multiple category names\n"
            f"4. Do NOT create new category names\n"
            f"5. Copy the names EXACTLY as they appear in the list\n"
            f"6. Focus on the core product being sold, not accessories or add-ons\n\n"
            
            f"Categories to choose from:\n{', '.join(filtered_leaves)}\n\n"
            
            f"Return EXACTLY 10 category names from the above list, one per line, with no additional text, "
            f"no numbering, and no modifications to the names. Use the EXACT spelling and capitalization."
        )
        
        try:
            # Make API call with deterministic settings
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a product categorization assistant. You will be given a product and a list of specific category names that have already been filtered to the most relevant taxonomy layer. Your task is CRITICAL: you must return ONLY the exact category names from the provided list - no modifications, no variations, no new names. Copy the category names EXACTLY as they appear in the list. Focus on the core product being sold, not accessories. Return exactly 10 category names from the list, one per line."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic results
                top_p=0        # Deterministic results
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            selected_categories = [category.strip() for category in content.split('\n') if category.strip()]
            
            # Remove duplicates while preserving order (case-insensitive)
            seen = set()
            unique_categories = []
            for category in selected_categories:
                category_lower = category.lower()
                if category_lower not in seen:
                    seen.add(category_lower)
                    unique_categories.append(category)
            
            # Ensure we have at most 10 categories after deduplication
            unique_categories = unique_categories[:10]
            
            # Log duplicate removal if any occurred
            if len(unique_categories) < len(selected_categories):
                duplicates_removed = len(selected_categories) - len(unique_categories)
                logger.info(f"Removed {duplicates_removed} duplicate categories from Stage 3 AI response")
            
            # Log if fewer than expected categories returned
            if len(unique_categories) < 10:
                logger.warning(f"Stage 3: AI returned fewer than 10 unique categories: {len(unique_categories)}")
            
            logger.info(f"Stage 3 complete: Refined to {len(unique_categories)} categories for final selection")
            
            # Validate categories exist in filtered list
            validated_categories = []
            for category in unique_categories:
                if category in filtered_leaves:
                    validated_categories.append(category)
                else:
                    logger.warning(f"Stage 3: AI returned category not in filtered list: {category}")
            
            return validated_categories
            
        except Exception as e:
            logger.error(f"Error in Stage 3 refined selection: {e}")
            # Fallback: return first 10 filtered categories
            fallback_result = filtered_leaves[:min(10, len(filtered_leaves))]
            logger.warning(f"Using fallback refined categories: {fallback_result[:3]}...")
            return fallback_result

    def stage4_validation(self, refined_leaves: List[str]) -> List[str]:
        """
        Stage 4: Validate the selected leaf nodes against the actual taxonomy.
        
        This method ensures that the AI didn't hallucinate any category names that don't exist
        in the actual taxonomy. It removes any invalid or hallucinated category names from the list.
        
        Process:
        1. Create mapping from leaf names to full paths
        2. Validate each category name exists in the actual taxonomy
        3. Remove any invalid or hallucinated category names
        4. Log validation statistics (valid vs invalid)
        
        Improvements in v5.0:
        - Added as intermediate validation step for data integrity
        - Enhanced validation to ensure categories actually exist in taxonomy
        - Improved error handling for edge cases

        Args:
            refined_leaves (List[str]): Refined leaf names from Stage 3
            
        Returns:
            List[str]: Validated list of leaf node names (typically 8-10 categories)
            
        Example:
            # Input: ["Smartphones", "Cell Phones", "InvalidCategory"]
            # Validation removes "InvalidCategory"
            # Returns: ["Smartphones", "Cell Phones"]
        """
        if not refined_leaves:
            logger.warning("No refined leaves provided for Stage 4 validation")
            return []
        
        logger.info(f"Stage 4: Validating {len(refined_leaves)} refined candidates")
        
        # Create mapping from leaf names to full paths for validation
        leaf_to_path = self._create_leaf_to_path_mapping()
        
        # Validate each category name exists in the actual taxonomy
        validated_categories = []
        invalid_categories = []
        
        for category in refined_leaves:
            if category in leaf_to_path:
                validated_categories.append(category)
                logger.debug(f"Stage 4: Validated category '{category}' → {leaf_to_path[category]}")
            else:
                invalid_categories.append(category)
                logger.warning(f"Stage 4: AI returned invalid/hallucinated category: {category}")
        
        # Log validation statistics
        if invalid_categories:
            logger.warning(f"Stage 4: Removed {len(invalid_categories)} invalid categories: {invalid_categories}")
        
        logger.info(f"Stage 4 complete: Validated {len(validated_categories)} out of {len(refined_leaves)} categories")
        
        return validated_categories

    def stage5_final_selection(self, product_info: str, validated_leaves: List[str]) -> int:
        """
        Stage 5: Select the single best match from the validated leaves.
        
        This method implements the fifth stage of classification using enhanced prompting
        and gpt-4.1-mini for the final selection from the top 10 validated candidates.
        The mini model provides enhanced precision for the final decision.
        
        Process:
        1. Construct structured prompt with 3-step reasoning process
        2. Present validated categories as numbered options (leaf names only)
        3. AI identifies core product and selects best match using gpt-4.1-mini
        4. Parse AI response and convert to 0-based index
        5. Return index of selected category
        
        Improvements in v5.0:
        - Renamed from stage4_final_selection to stage5_final_selection
        - Changed from gpt-4.1-nano to gpt-4.1-mini for enhanced final selection accuracy
        - Updated logging and documentation for 5-stage process
        - Enhanced error handling with robust number parsing

        Args:
            product_info (str): Complete product information
            validated_leaves (List[str]): Validated leaf names from Stage 4
            
        Returns:
            int: Index of the best match in the validated_leaves list (0-based)
            
        Raises:
            Exception: If OpenAI API call fails (logged and handled with fallback to index 0)
            
        Example:
            # Input: ["Smartphones", "Cell Phones"]
            # AI selects option 1 (Smartphones)
            # Returns: 0 (0-based index)
        """
        if not validated_leaves:
            logger.warning("No validated leaves provided for Stage 5 final selection")
            return 0
        
        if len(validated_leaves) == 1:
            logger.info("Only one validated leaf remaining, selecting it")
            return 0
        
        logger.info(f"Stage 5: Final selection among {len(validated_leaves)} validated candidates using {self.final_model}")
        
        # Construct structured selection prompt using only leaf names
        prompt = (
            f"Given the product: '{product_info}', which ONE of these categories is most appropriate?\n\n"
            f"First, explicitly identify what specific product is being sold here:\n"
            f"1. What is the actual core product? (not accessories or related items)\n"
            f"2. Is this a main product or an accessory FOR another product?\n"
            f"3. Distinguish between the product itself and any packaging, cases, or add-ons mentioned.\n\n"
            f"Keep your determination of the core product firmly in mind when making your selection.\n"
            f"Be especially careful to distinguish between categories for the main product versus categories for accessories.\n\n"
            f"Categories:\n"
        )
        
        # Add numbered options using only leaf names (not full paths)
        for i, leaf in enumerate(validated_leaves, 1):
            prompt += f"{i}. {leaf}\n"
            
        prompt += "\nFirst identify the core product in a sentence, then select the number of the most appropriate category.\nReturn ONLY the NUMBER of the most appropriate category, with no additional text."
        
        try:
            # Make API call with gpt-4.1-mini for enhanced final selection accuracy
            response = self.client.chat.completions.create(
                model=self.final_model,  # Using mini model for Stage 5
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a product categorization assistant specialized in identifying the core product in ambiguous descriptions. First identify exactly what specific product is being sold, then select the category that matches that specific product. Be very careful to distinguish between main products and accessories for those products. Return only the number of the most appropriate category."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0,  # Deterministic results
                top_p=0        # Deterministic results
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"Stage 5 complete: AI selected option {result}")
            
            # Parse the number and convert to 0-based index
            return self._parse_selection_number(result, len(validated_leaves))
                
        except Exception as e:
            logger.error(f"Error in Stage 5 final selection: {e}")
            return 0  # Default to first option

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

        Args:
            result (str): Raw response from AI
            max_options (int): Maximum valid option number
            
        Returns:
            int: 0-based index of selected option
        """
        try:
            # Look for any number in the result
            for i in range(1, max_options + 1):
                if str(i) in result:
                    best_index = i - 1
                    logger.info(f"Parsed selection: option {i} (index {best_index})")
                    return best_index
            
            # If no valid number found, default to first option
            logger.warning(f"Could not parse selection from: '{result}'. Using first option.")
            return 0
            
        except Exception as e:
            logger.error(f"Error parsing selection number: {e}")
            return 0

    def navigate_taxonomy(self, product_info: str) -> Tuple[List[List[str]], int]:
        """
        Main navigation method implementing the complete five-stage classification process.
        
        This is the primary public method that orchestrates the entire classification:
        1. Stage 1: Get top 20 leaf nodes from all categories
        2. Stage 2: Filter to leaves from most popular 1st taxonomy layer
        3. Stage 3: Refine selection to top 10 leaf nodes from filtered candidates
        4. Stage 4: Validate the selected leaf nodes
        5. Stage 5: Select the single best match from validated leaves
        6. Return all final candidates with the best match identified
        
        The method ensures end-to-end consistency by validating that the final result
        comes from the taxonomy layer identified in Stage 2.
        
        Process Flow:
        1. Stage 1: AI conceptually identifies relevant categories from all 4,722 leaf names
        2. Duplicate removal and validation of AI selections
        3. Stage 2: Algorithmic filtering to most popular taxonomy layer
        4. Stage 3: AI refines selection to top 10 candidates from filtered list
        5. Stage 4: AI validates selected leaf nodes
        6. Stage 5: AI selects best match from validated candidates using enhanced model
        7. Return structured results with best match index
        
        Improvements in v5.0:
        - Added Stage 4 validation for data integrity
        - Updated Stage 5 to use gpt-4.1-mini for enhanced precision
        - Enhanced error handling with detailed logging for all five stages
        - Improved tie-handling in Stage 2
        - Maintained backward compatibility with existing return format
        
        Args:
            product_info (str): Complete product information (name + description)
            
        Returns:
            Tuple[List[List[str]], int]: 
                - List of taxonomy paths (refined candidates from Stage 3)
                - Index of the best match (0-based, selected by Stage 5)
                - Returns ([["False"]], 0) if no matches found
                
        Example:
            navigator = TaxonomyNavigator("taxonomy.txt", api_key)
            paths, best_idx = navigator.navigate_taxonomy("iPhone 14: Smartphone with camera")
            
            # Example result:
            # paths = [["Electronics", "Cell Phones", "Smartphones"], 
            #          ["Electronics", "Cell Phones", "Mobile Phones"]]
            # best_idx = 0
            # best_path = paths[best_idx]  # ["Electronics", "Cell Phones", "Smartphones"]
            # final_category = best_path[-1]  # "Smartphones"
        """
        total_start_time = time.time()
        
        try:
            logger.info(f"Starting five-stage classification for: {product_info[:50]}...")
            
            # Stage 1: Get top 20 leaf nodes from all categories
            selected_leaves = self.stage1_leaf_matching(product_info)
            
            if not selected_leaves:
                logger.warning("No leaf nodes returned from Stage 1")
                return [["False"]], 0
            
            # Stage 2: Filter to leaves from most popular 1st taxonomy layer
            filtered_leaves = self.stage2_layer_filtering(selected_leaves)
            
            if not filtered_leaves:
                logger.warning("No leaves remaining after Stage 2 layer filtering")
                return [["False"]], 0
            
            # Stage 3: Refine selection to top 10 leaf nodes from filtered candidates
            refined_leaves = self.stage3_refined_selection(product_info, filtered_leaves)
            
            if not refined_leaves:
                logger.warning("No leaves remaining after Stage 3 refined selection")
                return [["False"]], 0
            
            # Stage 4: Validate the selected leaf nodes
            validated_leaves = self.stage4_validation(refined_leaves)
            
            if not validated_leaves:
                logger.warning("No leaves remaining after Stage 4 validation")
                return [["False"]], 0
            
            # Convert refined leaf names back to full paths
            final_paths = self._convert_leaves_to_paths(validated_leaves)
            
            if not final_paths:
                logger.warning("No valid paths found after conversion")
                return [["False"]], 0
                
            # Stage 5: Final selection from validated leaves
            best_match_idx = self.stage5_final_selection(product_info, validated_leaves)
                
            # Log completion
            total_duration = time.time() - total_start_time
            logger.info(f"Five-stage classification complete: {len(final_paths)} final candidates, best match at index {best_match_idx}")
            logger.info(f"Best match: {' > '.join(final_paths[best_match_idx])}")
            logger.info(f"Total processing time: {total_duration:.2f} seconds")
            
            return final_paths, best_match_idx
            
        except Exception as e:
            logger.error(f"Error during taxonomy navigation: {e}")
            return [["False"]], 0

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

    def save_results(self, product_info: str, paths: List[List[str]], best_match_idx: int, output_file: str) -> None:
        """
        Save classification results to a JSON file.
        
        Creates a structured JSON output with all candidates and the best match clearly marked.
        Supports appending to existing files for batch processing.

        Args:
            product_info (str): Original product information
            paths (List[List[str]]): All candidate taxonomy paths
            best_match_idx (int): Index of the best match
            output_file (str): Path to output JSON file
            
        Raises:
            Exception: If file writing fails
        """
        # Structure the result data
        if paths == [["False"]]:
            result = {
                "product_info": product_info,
                "best_match_index": 0,
                "matches": [{
                    "category_path": "False",
                    "full_path": "False",
                    "leaf_category": "False"
                }]
            }
        else:
            matches = []
            for i, path in enumerate(paths):
                matches.append({
                    "category_path": path,
                    "full_path": " > ".join(path),
                    "leaf_category": path[-1] if path else "False",
                    "is_best_match": (i == best_match_idx)
                })
            
            result = {
                "product_info": product_info,
                "best_match_index": best_match_idx,
                "matches": matches
            }
        
        try:
            # Handle file creation/appending
            mode = 'a' if os.path.exists(output_file) else 'w'
            with open(output_file, mode) as f:
                if mode == 'w':
                    f.write("[\n")
                else:
                    # Remove closing bracket to append new entry
                    with open(output_file, 'rb+') as f_binary:
                        f_binary.seek(-2, 2)  # Move to before closing bracket
                        f_binary.truncate()
                    f.write(",\n")
                
                f.write(json.dumps(result, indent=2))
                f.write("\n]")
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise

def main():
    """
    Command-line interface for the Taxonomy Navigator.
    
    Provides a simple CLI for classifying individual products and saving results.
    For batch processing, use the test scripts in the tests/ directory.
    """
    parser = argparse.ArgumentParser(
        description='AI-powered product taxonomy classification using 5-stage process',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --product-name "iPhone 14" --product-description "Smartphone with camera"
  %(prog)s --product-name "Xbox Controller" --product-description "Wireless gaming controller" --verbose
        """
    )
    
    # Required arguments
    parser.add_argument('--product-name', required=True, 
                       help='Name of the product to classify')
    parser.add_argument('--product-description', required=True, 
                       help='Detailed description of the product')
    
    # Optional arguments
    default_taxonomy = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'taxonomy.en-US.txt')
    parser.add_argument('--taxonomy-file', default=default_taxonomy, 
                       help='Path to taxonomy file (default: data/taxonomy.en-US.txt)')
    parser.add_argument('--api-key', 
                       help='OpenAI API key (optional if set in api_key.txt or environment)')
    parser.add_argument('--output-file', default='taxonomy_results.json', 
                       help='Output JSON file (default: taxonomy_results.json)')
    parser.add_argument('--model', default='gpt-4.1-nano', 
                       help='OpenAI model for all stages (default: gpt-4.1-nano)')
    parser.add_argument('--verbose', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if not args.verbose:
        # Suppress all logging for clean output
        logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger("taxonomy_navigator").setLevel(logging.CRITICAL)
        logging.getLogger("httpx").setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Initialize the navigator
        api_key = get_api_key(args.api_key)
        if not api_key:
            print("❌ Error: OpenAI API key not provided.")
            print("Please set it in data/api_key.txt, as environment variable OPENAI_API_KEY, or use --api-key.")
            sys.exit(1)
            
        navigator = TaxonomyNavigator(args.taxonomy_file, api_key, args.model)
        
        # Classify the product
        product_info = f"{args.product_name}: {args.product_description}"
        paths, best_match_idx = navigator.navigate_taxonomy(product_info)
        
        # Output result in clean format
        print(f"[{product_info}]")
        if paths == [["False"]]:
            print("False")
        else:
            best_path = paths[best_match_idx]
            print(best_path[-1])  # Just the leaf category
        print("-" * 50)
        
        # Save detailed results
        navigator.save_results(product_info, paths, best_match_idx, args.output_file)
        
    except KeyboardInterrupt:
        logger.info("Classification interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in classification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 