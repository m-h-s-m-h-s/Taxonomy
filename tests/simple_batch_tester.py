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
2. Stage 1: AI-selected L1 taxonomy categories (up to 3)
3. Stage 2: AI-selected leaf nodes from chosen L1 taxonomies (up to 10)
4. Stage 3: Final AI selection from the 10 candidates
5. Final result: [Product Description] followed by Final Category

Example Output:
  ==================== ANALYZING PRODUCT 1 ====================
  📦 iPhone 14 Pro: Smartphone with camera...
  
  📋 STAGE 1 - AI selecting top 3 L1 taxonomies from all categories...
  ✅ AI selected 3 L1 categories: [Electronics, Hardware, Apparel]
  
  📋 STAGE 2 - AI selecting top 10 leaf nodes from chosen L1 taxonomies...
  ✅ AI selected 10 leaf nodes from selected L1 categories
  
  📋 STAGE 3 - AI selecting final match from 10 candidates...
  🎯 FINAL RESULT: Electronics > Cell Phones > Smartphones
  
  [iPhone 14 Pro: Smartphone with camera...]
  Smartphones

Recent Improvements (v10.0):
- Simplified all prompting to basic, clean instructions
- Removed complex anti-hallucination language for better AI performance
- Stage prompts now use straightforward, essential instructions only
- System messages focus on core task requirements without threats
- Maintained 5-stage classification process with manageable 10-item chunks
- Enhanced AI performance through cleaner, more direct communication
- Preserved all validation and bounds checking mechanisms

Author: AI Assistant
Version: 10.0
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

def classify_product_with_stage_display(navigator: TaxonomyNavigator, product_line: str, show_stage_paths: bool = False) -> str:
    """
    Classify a single product and optionally display the AI's selections at each stage.
    
    This function performs the full classification and can display
    the AI's actual selections at each stage for debugging purposes.
    
    Args:
        navigator (TaxonomyNavigator): Initialized taxonomy navigator
        product_line (str): Product description to classify
        show_stage_paths (bool): Whether to display AI selections at each stage
        
    Returns:
        str: Final leaf category name, or "False" if no classification found
    """
    try:
        if show_stage_paths:
            print(f"\n🔍 CLASSIFICATION PROCESS VISUALIZATION")
            print("=" * 80)
            
            # Stage 1: Get the AI's top 2 L1 taxonomy selections
            print(f"\n📋 STAGE 1: Identifying Main Product Categories")
            print(f"   Goal: Pick 2 broad categories from all {len(set(path.split(' > ')[0] for i, path in enumerate(navigator.all_paths) if navigator.leaf_markers[i]))} options")
            
            selected_l1s = navigator.stage1_l1_selection(product_line)
            
            print(f"\n   ✅ AI Selected {len(selected_l1s)} Main Categories:")
            for i, l1_category in enumerate(selected_l1s, 1):
                print(f"      {i}. {l1_category}")
            
            # Stage 2A: Show first leaf selection from chosen L1 taxonomies
            print(f"\n📋 STAGE 2A: Finding Specific Categories in '{selected_l1s[0] if selected_l1s else 'None'}'")
            print(f"   Goal: Select up to 15 specific product categories")
            
            selected_leaves_2a = navigator.stage2a_first_leaf_selection(product_line, selected_l1s)
            
            if selected_leaves_2a:
                print(f"\n   ✅ Found {len(selected_leaves_2a)} Relevant Categories:")
                # Show the leaves with their L1 context
                leaf_to_l1 = navigator._create_leaf_to_l1_mapping()
                for i, leaf in enumerate(selected_leaves_2a[:10], 1):  # Show max 10 for readability
                    print(f"      {i}. {leaf}")
                if len(selected_leaves_2a) > 10:
                    print(f"      ... and {len(selected_leaves_2a) - 10} more")
            else:
                print(f"\n   ⚠️ No specific categories found in '{selected_l1s[0]}' section")
            
            # Stage 2B: Show second leaf selection (only if 2 L1s were selected)
            if len(selected_l1s) >= 2:
                print(f"\n📋 STAGE 2B: Finding Specific Categories in '{selected_l1s[1]}'")
                print(f"   Goal: Select up to 15 specific product categories")
                
                selected_leaves_2b = navigator.stage2b_second_leaf_selection(product_line, selected_l1s, selected_leaves_2a)
                
                if selected_leaves_2b:
                    print(f"\n   ✅ Found {len(selected_leaves_2b)} Additional Categories:")
                    for i, leaf in enumerate(selected_leaves_2b[:10], 1):
                        print(f"      {i}. {leaf}")
                    if len(selected_leaves_2b) > 10:
                        print(f"      ... and {len(selected_leaves_2b) - 10} more")
                else:
                    print(f"\n   ⚠️ No specific categories found in '{selected_l1s[1]}' section")
            else:
                print(f"\n📋 STAGE 2B: SKIPPED")
                print(f"   Reason: Only 1 main category was selected, no need to check a second")
                selected_leaves_2b = []
            
            # Combine all Stage 2 results
            all_selected_leaves = selected_leaves_2a + selected_leaves_2b
            
            # Stage 3 info
            if len(all_selected_leaves) == 0:
                print(f"\n📋 STAGE 3: CANNOT PROCEED")
                print(f"   Reason: No specific categories were found")
            elif len(all_selected_leaves) == 1:
                print(f"\n📋 STAGE 3: SKIPPED - Using Single Result")
                print(f"   Reason: Only 1 category found, no need to choose")
                print(f"   🎯 Final Category: {all_selected_leaves[0]}")
            else:
                print(f"\n📋 STAGE 3: Making Final Decision")
                print(f"   Goal: Choose the single best category from {len(all_selected_leaves)} options")
            print("=" * 80)
        
        # Perform the full classification
        paths, best_match_idx = navigator.navigate_taxonomy(product_line)
        
        if show_stage_paths and paths != [["False"]]:
            print(f"\n🎯 FINAL CLASSIFICATION RESULT:")
            print(f"   Full Category Path: {' > '.join(paths[best_match_idx])}")
            print(f"   Product Category: {paths[best_match_idx][-1]}")
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
  %(prog)s --model gpt-4.1-mini                     # Use different model for stages 1&4
  %(prog)s --show-stage-paths                       # Display AI selections at each stage
  
Updated Classification Process:
  Stage 1: AI selects top 2 L1 taxonomy categories (gpt-4.1-nano)
  Stage 2A: AI selects first 15 leaf nodes from first L1 (gpt-4.1-nano)
  Stage 2B: AI selects next 15 leaf nodes from second L1 (gpt-4.1-nano) - skipped if only 1 L1
  Stage 3: AI final selection from combined candidates (gpt-4.1-mini) - skipped if only 1 leaf
  
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
                       help='OpenAI model for all stages (default: gpt-4.1-nano)')
    parser.add_argument('--api-key', 
                       help='OpenAI API key (optional if set in environment or file)')
    
    # Display options
    parser.add_argument('--show-stage-paths', action='store_true',
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
    
    # Override show_stage_paths if running directly
    if len(sys.argv) == 1:
        args.show_stage_paths = show_stage_paths_default
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
                print(f"📝 Note: Requested {num_products} products, but only {len(products)} available. Using all products.")
                selected_products = products
            else:
                selected_products = random.sample(products, num_products)
                print(f"🎲 Randomly selected {len(selected_products)} products from {len(products)} total")
        else:
            # Use all products when run with command line arguments
            selected_products = products
        
        print(f"\n🚀 Starting Classification Process...")
        print(f"   Total Products: {len(selected_products)}")
        print(f"   Taxonomy Categories: ~5,000+ options to choose from")
        print("=" * 80)
        
        # Process each selected product and display in the requested format
        for i, product_line in enumerate(selected_products):
            # Show Stage paths for every product if requested (not just the first one)
            show_paths = args.show_stage_paths
            
            if show_paths:
                print(f"\n{'='*20} PRODUCT {i+1} of {len(selected_products)} {'='*20}")
                print(f"\n📦 PRODUCT DESCRIPTION:")
                # Show truncated version to demonstrate what AI sees
                print(f"   Full: {product_line[:100]}..." if len(product_line) > 100 else f"   Full: {product_line}")
                print(f"   Stage 1 sees: {product_line[:50]}..." if len(product_line) > 50 else f"   Stage 1 sees: {product_line}")
                print("=" * 100)
            
            # Classify the product
            final_leaf = classify_product_with_stage_display(navigator, product_line, show_paths)
            
            # Display in the exact format requested: [Input] then Leaf Category
            print(f"\n[PRODUCT INPUT]")
            print(f"{product_line}")
            print(f"\n[FINAL CATEGORY]") 
            print(final_leaf)
            
            # More prominent separation between products
            if i < len(selected_products) - 1:  # Don't add separator after the last product
                print("\n" + "="*100 + "\n")
        
    except KeyboardInterrupt:
        print("\n❌ Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 