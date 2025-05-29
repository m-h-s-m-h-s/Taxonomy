#!/bin/bash
#
# Taxonomy Navigator - Batch Product Analysis Tool
#
# This script provides simple batch testing of multiple products using the
# Taxonomy Navigator's 3-stage AI classification system with detailed explanations
# at each step of the process.
#
# Features:
# - Batch processing from text files using 3-stage AI process
# - Detailed explanations of what's happening at each stage
# - Clean output with visual hierarchy and progress indicators
# - Perfect for understanding the classification process
# - Configurable AI models and taxonomy files
#
# 3-Stage Classification Process:
# 1. AI selects top 2 L1 (top-level) taxonomy categories
# 2. AI finds up to 30 leaf nodes from selected L1 categories (15 each)
# 3. AI final selection from all candidate leaf nodes
#
# Use Cases:
# - Understanding how the classification system works
# - Quick validation of classification accuracy
# - Educational demonstrations and presentations
# - Manual review of specific product sets
# - Debugging classification issues
#
# Usage Examples:
#   # Simple batch testing with default products
#   ./analyze_batch_products.sh
#
#   # Show detailed stage-by-stage classification
#   ./analyze_batch_products.sh --show-stages
#
# Author: AI Assistant
# Version: 6.0
# Last Updated: 2025-01-25
#

# Script configuration and default values
PRODUCTS_FILE="../tests/sample_products.txt"
TAXONOMY_FILE="../data/taxonomy.en-US.txt"
NUM_PRODUCTS=""
SHOW_STAGES=""
INTERACTIVE_MODE="true"

# Color codes for enhanced output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Function to display usage information
usage() {
    echo -e "${BLUE}${BOLD}Taxonomy Navigator - Batch Product Analysis Tool${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --products FILE            Products file to test"
    echo "                                 (default: ../tests/sample_products.txt)"
    echo "  -t, --taxonomy FILE            Taxonomy file path"
    echo "                                 (default: ../data/taxonomy.en-US.txt)"
    echo "  -n, --num-products NUM         Number of products to test"
    echo "                                 (default: interactive selection)"
    echo "  -s, --show-stages              Show detailed stage-by-stage classification"
    echo "  -q, --quick                    Quick mode (5 products, no interaction)"
    echo "  -h, --help                     Show this help message"
    echo ""
    echo -e "${CYAN}${BOLD}How Classification Works:${NC}"
    echo -e "${CYAN}========================${NC}"
    echo ""
    echo -e "${GREEN}Stage 1: Top-Level Category Selection${NC}"
    echo "  The AI analyzes the product and selects 1-2 broad categories"
    echo "  (e.g., Electronics, Apparel, Home & Garden)"
    echo ""
    echo -e "${GREEN}Stage 2: Subcategory Discovery${NC}"
    echo "  Within each top-level category, the AI finds specific"
    echo "  subcategories that match the product (up to 15 per category)"
    echo ""
    echo -e "${GREEN}Stage 3: Final Selection${NC}"
    echo "  From all candidates, the AI selects the single best match"
    echo "  using a more sophisticated model for accuracy"
    echo ""
    echo -e "${CYAN}${BOLD}Examples:${NC}"
    echo -e "${CYAN}=========${NC}"
    echo "  # Interactive mode (default)"
    echo "  $0"
    echo ""
    echo "  # Quick test with 5 products"
    echo "  $0 --quick"
    echo ""
    echo "  # Test 10 products with detailed stages"
    echo "  $0 --num-products 10 --show-stages"
    echo ""
    echo "  # Custom products file"
    echo "  $0 --products my_products.txt --show-stages"
    echo ""
    exit 1
}

# Function to validate file existence with helpful error messages
validate_file() {
    local file_path="$1"
    local file_type="$2"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${RED}❌ Error: $file_type file '$file_path' not found.${NC}"
        
        case "$file_type" in
            "Products")
                echo -e "${YELLOW}💡 Make sure you have a products file with one product per line.${NC}"
                echo -e "${YELLOW}   Example format: 'Product Name: Description'${NC}"
                echo -e "${YELLOW}   Sample file available at: tests/sample_products.txt${NC}"
                ;;
            "Taxonomy")
                echo -e "${YELLOW}💡 Make sure you have the taxonomy file in the data/ directory.${NC}"
                echo -e "${YELLOW}   You can download it from Google Product Taxonomy.${NC}"
                ;;
        esac
        
        exit 1
    fi
}

# Function to check API key availability
check_api_key() {
    local api_key_file="../data/api_key.txt"
    
    if [ ! -f "$api_key_file" ] && [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  No API key found!${NC}"
        echo ""
        echo -e "${YELLOW}To use this tool, you need an OpenAI API key.${NC}"
        echo -e "${YELLOW}You can provide it using one of these methods:${NC}"
        echo ""
        echo -e "${GREEN}Option 1: Create a file${NC}"
        echo "  echo 'your-api-key-here' > ../data/api_key.txt"
        echo ""
        echo -e "${GREEN}Option 2: Set environment variable${NC}"
        echo "  export OPENAI_API_KEY=your-api-key-here"
        echo ""
        echo -e "${GREEN}Option 3: Create .env file${NC}"
        echo "  echo 'OPENAI_API_KEY=your-api-key-here' > ../.env"
        echo ""
        return 1
    fi
    return 0
}

# Function to count products in file for preview
count_products() {
    local file_path="$1"
    local count=$(grep -c "^[[:space:]]*[^[:space:]]" "$file_path" 2>/dev/null || echo "0")
    echo "$count"
}

# Function to display welcome banner
display_welcome() {
    echo ""
    echo -e "${BLUE}${"="*80}${NC}"
    echo -e "${BLUE}${BOLD}      🚀 TAXONOMY NAVIGATOR - BATCH PRODUCT CLASSIFIER 🚀${NC}"
    echo -e "${BLUE}${"="*80}${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}What This Tool Does:${NC}"
    echo -e "${CYAN}===================${NC}"
    echo "This tool uses AI to automatically classify products into categories."
    echo "It analyzes product descriptions and finds the best matching category"
    echo "from a taxonomy of over 5,000 possible categories."
    echo ""
}

# Parse command line arguments with comprehensive validation
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--products)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --products requires a file path${NC}"
                exit 1
            fi
            PRODUCTS_FILE="$2"
            shift 2
            ;;
        -t|--taxonomy)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --taxonomy requires a file path${NC}"
                exit 1
            fi
            TAXONOMY_FILE="$2"
            shift 2
            ;;
        -n|--num-products)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --num-products requires a number${NC}"
                exit 1
            fi
            NUM_PRODUCTS="$2"
            INTERACTIVE_MODE="false"
            shift 2
            ;;
        -s|--show-stages)
            SHOW_STAGES="--show-stage-paths"
            shift
            ;;
        -q|--quick)
            NUM_PRODUCTS="5"
            INTERACTIVE_MODE="false"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Display welcome banner
display_welcome

# Pre-flight checks and validation
echo -e "${PURPLE}${BOLD}Step 1: Checking Requirements${NC}"
echo -e "${PURPLE}============================${NC}"

echo -e "\n${CYAN}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✅ Python is installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo -e "${YELLOW}   Please install Python 3.8 or higher.${NC}"
    exit 1
fi

echo -e "\n${CYAN}Checking OpenAI API key...${NC}"
if ! check_api_key; then
    exit 1
fi
echo -e "${GREEN}✅ API key configured${NC}"

echo -e "\n${CYAN}Checking input files...${NC}"
validate_file "$PRODUCTS_FILE" "Products"
validate_file "$TAXONOMY_FILE" "Taxonomy"
echo -e "${GREEN}✅ All files found${NC}"

# Count products for preview
product_count=$(count_products "$PRODUCTS_FILE")

# Display configuration summary
echo ""
echo -e "${PURPLE}${BOLD}Step 2: Configuration Summary${NC}"
echo -e "${PURPLE}============================${NC}"
echo -e "${GREEN}📦 Products file: $PRODUCTS_FILE${NC}"
echo -e "${GREEN}📊 Total products available: $product_count${NC}"
echo -e "${GREEN}📁 Taxonomy file: $TAXONOMY_FILE${NC}"

# Interactive mode for number of products
if [ "$INTERACTIVE_MODE" = "true" ]; then
    echo ""
    echo -e "${PURPLE}${BOLD}Step 3: Select Test Mode${NC}"
    echo -e "${PURPLE}======================${NC}"
    echo ""
    echo "How would you like to test?"
    echo ""
    echo "1. Quick test (5 random products)"
    echo "2. Medium test (10 random products)"
    echo "3. Full test (all $product_count products)"
    echo "4. Custom number"
    echo ""
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            NUM_PRODUCTS="5"
            echo -e "${GREEN}→ Selected: Quick test with 5 products${NC}"
            ;;
        2)
            NUM_PRODUCTS="10"
            echo -e "${GREEN}→ Selected: Medium test with 10 products${NC}"
            ;;
        3)
            NUM_PRODUCTS="$product_count"
            echo -e "${GREEN}→ Selected: Full test with all products${NC}"
            ;;
        4)
            read -p "Enter number of products to test (1-$product_count): " NUM_PRODUCTS
            echo -e "${GREEN}→ Selected: Custom test with $NUM_PRODUCTS products${NC}"
            ;;
        *)
            NUM_PRODUCTS="5"
            echo -e "${YELLOW}→ Invalid choice. Using quick test with 5 products${NC}"
            ;;
    esac
    
    # Ask about detailed output
    if [ -z "$SHOW_STAGES" ]; then
        echo ""
        read -p "Show detailed classification stages? (y/n): " show_detail
        if [ "$show_detail" = "y" ] || [ "$show_detail" = "Y" ]; then
            SHOW_STAGES="--show-stage-paths"
            echo -e "${GREEN}→ Detailed stage output enabled${NC}"
        else
            echo -e "${GREEN}→ Using summary output only${NC}"
        fi
    fi
else
    echo -e "${GREEN}🎯 Testing mode: $NUM_PRODUCTS products${NC}"
fi

echo ""
echo -e "${PURPLE}${BOLD}Step 4: Starting Classification${NC}"
echo -e "${PURPLE}=============================${NC}"
echo ""
echo -e "${CYAN}${BOLD}What happens next:${NC}"
echo -e "${CYAN}=================${NC}"
echo "For each product, the AI will:"
echo "  1. Identify broad category types (Electronics, Apparel, etc.)"
echo "  2. Find specific subcategories within those types"
echo "  3. Select the single best matching category"
echo ""
if [ -n "$SHOW_STAGES" ]; then
    echo -e "${YELLOW}📝 Detailed mode: You'll see explanations at each stage${NC}"
else
    echo -e "${YELLOW}⚡ Summary mode: You'll see just the final results${NC}"
fi
echo ""
echo -e "${BLUE}${"="*80}${NC}"
echo ""

# Change to the script directory to ensure relative paths work correctly
cd "$(dirname "$0")" || {
    echo -e "${RED}❌ Error: Could not change to script directory${NC}"
    exit 1
}

# Prepare arguments for Python script
PYTHON_ARGS="--products-file $PRODUCTS_FILE --taxonomy-file $TAXONOMY_FILE"

if [ -n "$NUM_PRODUCTS" ]; then
    PYTHON_ARGS="$PYTHON_ARGS --num-products $NUM_PRODUCTS"
fi

if [ -n "$SHOW_STAGES" ]; then
    PYTHON_ARGS="$PYTHON_ARGS $SHOW_STAGES"
fi

# Execute the Python script
python3 ../tests/simple_batch_tester.py $PYTHON_ARGS

# Capture the exit code from the Python script
exit_code=$?

# Provide comprehensive feedback based on results
echo ""
echo -e "${BLUE}${"="*80}${NC}"
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✅ Classification Complete!${NC}"
    echo -e "${BLUE}${"="*80}${NC}"
    echo ""
    echo -e "${CYAN}${BOLD}What Just Happened:${NC}"
    echo -e "${CYAN}==================${NC}"
    echo "  • The AI analyzed each product description"
    echo "  • It narrowed down from thousands of categories to find the best match"
    echo "  • Each product was assigned its most appropriate category"
    echo ""
    echo -e "${GREEN}${BOLD}Next Steps:${NC}"
    echo -e "${GREEN}===========${NC}"
    echo "  • Review the classifications above for accuracy"
    echo "  • Try running with --show-stages to see the AI's reasoning"
    echo "  • Modify sample_products.txt to test your own products"
    echo "  • Use classify_single_product.sh for interactive testing"
else
    echo -e "${RED}${BOLD}❌ Classification Failed${NC}"
    echo -e "${BLUE}${"="*80}${NC}"
    echo -e "${RED}Error code: $exit_code${NC}"
    echo ""
    echo -e "${YELLOW}${BOLD}Troubleshooting:${NC}"
    echo -e "${YELLOW}===============${NC}"
    echo "  • Check that your API key is valid"
    echo "  • Ensure all files exist and are readable"
    echo "  • Try running with fewer products"
    echo "  • Check the error messages above for details"
fi

exit $exit_code 