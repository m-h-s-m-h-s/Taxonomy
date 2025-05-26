#!/usr/bin/env python3
"""
Simple Taxonomy Test - Streamlined Product Classification Display

This module provides a simplified testing interface for the Taxonomy Navigator that
focuses on clean, readable output. It displays only the essential information:
product titles and their final taxonomy leaf categories.

Purpose:
- Quick validation of classification results with stage-by-stage AI selections
- Clean output for demonstrations and presentations
- Simplified testing without verbose logging or detailed metrics
- Easy-to-read format for manual review of classifications
- Validation statistics showing AI accuracy (valid vs invalid selections)

Key Features:
- Minimal output format: "[Product Description]" followed by "Final Category"
- Automatic title extraction from product descriptions
- Batch processing with clean console output
- Stage-by-stage display of AI selections at each classification stage
- Validation statistics showing how many AI selections actually exist in taxonomy
- Random product selection for varied testing
- Prominent visual separation between products for easy reading
- Ideal for quick spot-checks and demonstrations

Use Cases:
- Quick testing of product classification accuracy
- Generating clean output for reports or presentations
- Validating specific product sets without detailed metrics
- Demonstrating system capabilities with minimal noise
- Manual review of classification results
- Debugging AI selection quality and taxonomy coverage

Output Format:
Each classification shows:
1. Product analysis header with product description
2. Stage 1: AI-selected leaf nodes (up to 20, duplicates removed)
3. Stage 2: Filtering statistics and most popular taxonomy layer
4. Stage 3: AI-refined selection (up to 10 from filtered L1 taxonomy candidates)
5. Stage 4: Validation of AI selections (remove hallucinations)
6. Stage 5: Final AI selection from validated candidates
7. Final result: [Product Description] followed by Final Category

Example Output:
  ==================== ANALYZING PRODUCT 1 ====================
  📦 iPhone 14 Pro: Smartphone with camera...
  
  📋 STAGE 1 - AI selecting top 20 leaf nodes from 4722 total...
  ✅ AI selected 15 leaf nodes: [list of categories]
  
  📋 STAGE 2 - Filtering to most popular 1st taxonomy layer...
  📊 Found 12 valid categories out of 15 AI-selected categories
  ✅ Most popular layer: 'Electronics' - Filtered to 8 leaves
  
  📋 STAGE 3 - AI refining selection to top 10 from 8 L1 taxonomy candidates...
  ✅ AI refined selection - selected 8 leaf nodes from Electronics layer
  
  📋 STAGE 4 - Validating AI selections against taxonomy...
  ✅ Validated 8 categories (no hallucinations detected)
  
  📋 STAGE 5 - AI selecting final match from 8 validated candidates...
  🎯 FINAL RESULT: Electronics > Cell Phones > Smartphones
  
  [iPhone 14 Pro: Smartphone with camera...]
  Smartphones

Recent Improvements (v5.0):
- Updated for new 5-stage classification process
- Added Stage 4 validation to prevent AI hallucinations
- Enhanced visual separation between products for better readability
- Updated stage numbering and documentation throughout
- Improved error handling and user input validation
- Better integration with updated taxonomy navigator engine

Author: AI Assistant
Version: 5.0
Last Updated: 2025-01-25
"""

import os
import sys
import argparse
import logging
import random

# Add the src directory to the Python path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.taxonomy_navigator_engine import TaxonomyNavigator
from src.config import get_api_key

def read_products_file(filename: str) -> list:
    """
    Read products from a text file, one product per line.
    
    This function reads products from a file and filters out empty lines.
    It's designed for simple, straightforward file reading without extensive
    error handling since this is a simplified testing tool.
    
    Args:
        filename (str): Path to the products file
        
    Returns:
        list: List of product descriptions (strings), with empty lines removed
        
    Example:
        products = read_products_file("sample_products.txt")
        # Returns: ["iPhone 14: Smartphone", "Xbox Controller: Gaming device"]
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Read all lines, strip whitespace, and filter out empty lines
            products = [line.strip() for line in f if line.strip()]
        return products
    except FileNotFoundError:
        print(f"Error: Products file '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading products file: {e}")
        sys.exit(1)

def extract_product_title(product_line: str) -> str:
    """
    Extract the product title from a product description line.
    
    Many product descriptions follow the format "Product Name: Description".
    This function extracts just the product name part for cleaner display.
    If no colon is found, it returns the entire line as the title.
    
    Args:
        product_line (str): Full product description line
        
    Returns:
        str: Product title (part before the first colon, or entire line)
        
    Examples:
        extract_product_title("iPhone 14 Pro: Smartphone with camera")
        # Returns: "iPhone 14 Pro"
        
        extract_product_title("Xbox Controller")
        # Returns: "Xbox Controller"
    """
    if ':' in product_line:
        # Split on first colon and return the title part
        return product_line.split(':', 1)[0].strip()
    else:
        # No colon found, return the entire line as title
        return product_line.strip()

def classify_product_with_stage1_display(navigator: TaxonomyNavigator, product_line: str, show_stage1_paths: bool = False) -> str:
    """
    Classify a single product and optionally display the AI's selections at each stage.
    
    This function performs the full four-stage classification and can display
    the AI's actual selections at each stage for debugging purposes.
    
    Args:
        navigator (TaxonomyNavigator): Initialized taxonomy navigator
        product_line (str): Product description to classify
        show_stage1_paths (bool): Whether to display AI selections at each stage
        
    Returns:
        str: Final leaf category name, or "False" if no classification found
    """
    try:
        if show_stage1_paths:
            print(f"\n🔍 STAGE-BY-STAGE AI SELECTIONS:")
            print("=" * 80)
            
            # Stage 1: Get the AI's top 20 leaf selections
            print(f"\n📋 STAGE 1 - AI selecting top 20 leaf nodes from {len(navigator._extract_leaf_nodes()[0])} total...")
            selected_leaves = navigator.stage1_leaf_matching(product_line)
            
            print(f"\n✅ AI selected {len(selected_leaves)} leaf nodes:")
            for i, leaf in enumerate(selected_leaves, 1):
                print(f"   {i:2d}. {leaf}")
            
            # Stage 2: Show layer filtering results
            print(f"\n📋 STAGE 2 - Filtering to most popular 1st taxonomy layer...")
            
            # Count how many of the AI-selected categories actually exist
            leaf_to_path = navigator._create_leaf_to_path_mapping()
            valid_count = sum(1 for leaf in selected_leaves if leaf in leaf_to_path)
            print(f"📊 Found {valid_count} valid categories out of {len(selected_leaves)} AI-selected categories")
            
            filtered_leaves = navigator.stage2_layer_filtering(selected_leaves)
            
            # Show which layer was selected and the filtered results
            if filtered_leaves:
                # Get the layer name from the first filtered leaf
                leaf_to_path = navigator._create_leaf_to_path_mapping()
                if filtered_leaves[0] in leaf_to_path:
                    first_layer = leaf_to_path[filtered_leaves[0]].split(" > ")[0]
                    print(f"\n✅ Most popular layer: '{first_layer}' - Filtered to {len(filtered_leaves)} leaves:")
                    for i, leaf in enumerate(filtered_leaves, 1):
                        if leaf in leaf_to_path:
                            full_path = leaf_to_path[leaf]
                            print(f"   {i:2d}. {leaf} → {full_path}")
                        else:
                            print(f"   {i:2d}. {leaf}")
                else:
                    print(f"\n✅ Filtered to {len(filtered_leaves)} leaves:")
                    for i, leaf in enumerate(filtered_leaves, 1):
                        print(f"   {i:2d}. {leaf}")
            else:
                print("\n❌ No leaves remaining after filtering")
            
            # Stage 3: Show refined selection results with AI's actual selections
            print(f"\n📋 STAGE 3 - AI refining selection to top 10 from {len(filtered_leaves)} L1 taxonomy candidates...")
            print(f"💡 This is like Stage 1, but only with the filtered leaves from the dominant L1 taxonomy layer")
            refined_leaves = navigator.stage3_refined_selection(product_line, filtered_leaves)
            
            if refined_leaves:
                print(f"\n✅ AI refined selection - selected {len(refined_leaves)} leaf nodes:")
                for i, leaf in enumerate(refined_leaves, 1):
                    print(f"   {i:2d}. {leaf}")
                
                # Also show the full paths for context
                print(f"\n📍 Full paths of AI-selected refined categories:")
                for i, leaf in enumerate(refined_leaves, 1):
                    if leaf in leaf_to_path:
                        full_path = leaf_to_path[leaf]
                        print(f"   {i:2d}. {leaf} → {full_path}")
                    else:
                        print(f"   {i:2d}. {leaf} → [Path not found]")
            else:
                print("\n❌ No leaves remaining after refined selection")
            
            # Stage 4: Show validation results
            print(f"\n📋 STAGE 4 - Validating AI selections against taxonomy...")
            print(f"💡 Ensuring AI didn't hallucinate any category names that don't exist")
            validated_leaves = navigator.stage4_validation(refined_leaves)
            
            if validated_leaves:
                invalid_count = len(refined_leaves) - len(validated_leaves)
                if invalid_count > 0:
                    print(f"\n⚠️  Validation removed {invalid_count} invalid/hallucinated categories")
                    print(f"✅ Validated {len(validated_leaves)} categories:")
                else:
                    print(f"\n✅ Validated {len(validated_leaves)} categories (no hallucinations detected):")
                
                for i, leaf in enumerate(validated_leaves, 1):
                    print(f"   {i:2d}. {leaf}")
            else:
                print("\n❌ No leaves remaining after validation")
            
            print(f"\n📋 STAGE 5 - AI selecting final match from {len(validated_leaves)} validated candidates...")
            print("=" * 80)
        
        # Perform the full four-stage classification
        paths, best_match_idx = navigator.navigate_taxonomy(product_line)
        
        if show_stage1_paths and paths != [["False"]]:
            print(f"\n🎯 FINAL RESULT: {' > '.join(paths[best_match_idx])}")
            print("=" * 80)
        
        # Extract the final leaf category
        if paths == [["False"]]:
            return "False"
        else:
            best_path = paths[best_match_idx]
            return best_path[-1] if best_path else "False"
            
    except Exception as e:
        # Return error indicator for any classification failures
        return f"Error: {str(e)[:30]}..."

def main():
    """
    Command-line interface for simple taxonomy testing.
    
    This function provides a minimal CLI focused on clean output and ease of use.
    It processes products and displays results in the format "Title: Category".
    """
    parser = argparse.ArgumentParser(
        description='Simple taxonomy test showing only product titles and final leaf categories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                          # Use default files
  %(prog)s --products-file my_products.txt          # Custom products file
  %(prog)s --model gpt-4.1-mini                     # Use different model for Stages 1&3
  %(prog)s --show-stage1-paths                      # Display AI selections at each stage
  
5-Stage Classification Process:
  Stage 1: AI selects top 20 leaf nodes from all 4,722 categories
  Stage 2: Algorithmic filtering to most popular taxonomy layer
  Stage 3: AI refines to top 10 categories from filtered L1 taxonomy candidates
  Stage 4: Validation of AI selections against taxonomy
  Stage 5: AI final selection using enhanced model (gpt-4.1-mini)
  
Output Format:
  Each line shows: "Product Title: Leaf Category"
  
  Example output:
    iPhone 14 Pro: Smartphones
    Xbox Wireless Controller: Game Controllers
    Nike Air Max 270: Athletic Shoes
        """
    )
    
    # File configuration
    default_taxonomy = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'taxonomy.en-US.txt')
    parser.add_argument('--products-file', default='sample_products.txt', 
                       help='Products file to test (default: sample_products.txt)')
    parser.add_argument('--taxonomy-file', default=default_taxonomy, 
                       help='Taxonomy file path (default: data/taxonomy.en-US.txt)')
    
    # Model configuration
    parser.add_argument('--model', default='gpt-4.1-nano', 
                       help='OpenAI model for classification (default: gpt-4.1-nano)')
    parser.add_argument('--api-key', 
                       help='OpenAI API key (optional if set in environment or file)')
    
    # Display options
    parser.add_argument('--show-stage1-paths', action='store_true',
                       help='Display AI selections at each stage of classification')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging for debugging')
    
    # Check if running directly (no command line args) - show stage paths by default
    if len(sys.argv) == 1:
        # Running directly in Python/IDLE - enable stage display by default
        print("🔍 Running in direct mode - showing AI selections at each stage by default")
        print("=" * 80)
        show_stage_paths_default = True
        verbose_default = False
        
        # Ask user how many products to run
        try:
            num_products = int(input("\n🎯 How many products would you like to test? "))
            if num_products <= 0:
                print("❌ Number must be greater than 0. Using 1.")
                num_products = 1
        except (ValueError, KeyboardInterrupt):
            print("❌ Invalid input. Using 1 product.")
            num_products = 1
        
        print(f"🎲 Will randomly select {num_products} product(s) from the sample file")
        print("=" * 80)
    else:
        # Running with command line arguments - use provided flags
        show_stage_paths_default = False
        verbose_default = False
        num_products = None  # Use all products when run with command line args
    
    args = parser.parse_args()
    
    # Override show_stage1_paths if running directly
    if len(sys.argv) == 1:
        args.show_stage1_paths = show_stage_paths_default
        args.verbose = verbose_default
    
    # Configure logging based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger("taxonomy_navigator").setLevel(logging.INFO)
    else:
        # Suppress verbose logging for clean output
        logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger("taxonomy_navigator").setLevel(logging.CRITICAL)
        logging.getLogger("httpx").setLevel(logging.CRITICAL)
    
    try:
        # Validate and get API key
        api_key = get_api_key(args.api_key)
        if not api_key:
            print("❌ Error: OpenAI API key not provided.")
            print("💡 Please set it in data/api_key.txt, environment variable OPENAI_API_KEY, or use --api-key")
            sys.exit(1)
        
        # Validate files exist
        if not os.path.exists(args.products_file):
            print(f"❌ Error: Products file '{args.products_file}' not found.")
            sys.exit(1)
            
        if not os.path.exists(args.taxonomy_file):
            print(f"❌ Error: Taxonomy file '{args.taxonomy_file}' not found.")
            sys.exit(1)
        
        # Initialize the taxonomy navigator
        navigator = TaxonomyNavigator(args.taxonomy_file, api_key, args.model)
        
        # Read products from file
        products = read_products_file(args.products_file)
        
        if not products:
            print("❌ No products found in the file.")
            sys.exit(1)
        
        # If running in direct mode, randomly select the specified number of products
        if len(sys.argv) == 1 and num_products is not None:
            if num_products >= len(products):
                print(f"📝 Requested {num_products} products, but only {len(products)} available. Using all products.")
                selected_products = products
            else:
                selected_products = random.sample(products, num_products)
                print(f"🎲 Randomly selected {len(selected_products)} products from {len(products)} total")
        else:
            # Use all products when run with command line arguments
            selected_products = products
        
        print(f"\n🚀 Processing {len(selected_products)} product(s)...")
        print("=" * 80)
        
        # Process each selected product and display in the requested format
        for i, product_line in enumerate(selected_products):
            # Show Stage 1 paths for every product if requested (not just the first one)
            show_paths = args.show_stage1_paths
            
            if show_paths:
                print(f"\n{'='*20} ANALYZING PRODUCT {i+1} {'='*20}")
                print(f"📦 {product_line}")
                print("=" * 100)
            
            # Classify the product
            final_leaf = classify_product_with_stage1_display(navigator, product_line, show_paths)
            
            # Display in the exact format requested: [Input] then Leaf Category
            print(f"[{product_line}]")
            print(final_leaf)
            
            # More prominent separation between products
            if i < len(selected_products) - 1:  # Don't add separator after the last product
                print("\n" + "█" * 100)
                print("█" + " " * 98 + "█")
                print("█" + " " * 98 + "█")
                print("█" * 100 + "\n")
        
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 