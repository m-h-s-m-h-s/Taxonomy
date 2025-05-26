#!/bin/bash
#
# Taxonomy Navigator - Batch Product Analysis Tool
#
# This script provides simple batch testing of multiple products using the
# Taxonomy Navigator's 5-stage AI classification system. It focuses on clean,
# minimal output perfect for demonstrations and quick validation.
#
# Features:
# - Batch processing from text files using 5-stage AI process
# - Clean, minimal output showing "Product: Category"
# - No timing overhead or complex metrics
# - Perfect for demonstrations and quick validation
# - Configurable AI models and taxonomy files
# - Progressive filtering: 4,722 → 20 → filtered L1 → 10 → validated → 1
# - Stage 4 validation prevents AI hallucinations
#
# 5-Stage Classification Process:
# 1. AI selects top 20 leaf nodes from all 4,722 categories (gpt-4.1-nano)
# 2. Algorithmic filtering to most popular L1 taxonomy layer
# 3. AI refines to top 10 categories from filtered L1 taxonomy candidates (gpt-4.1-nano)
# 4. Validation to ensure no AI hallucinations (algorithmic)
# 5. AI final selection using enhanced model (gpt-4.1-nano)
#
# Use Cases:
# - Quick validation of classification accuracy
# - Clean output for demonstrations and presentations
# - Manual review of specific product sets
# - Testing without performance overhead
#
# Usage Examples:
#   # Simple batch testing with default products
#   ./analyze_batch_products.sh
#
#   # Custom products file with verbose logging
#   ./analyze_batch_products.sh --products my_products.txt --verbose
#
# Author: AI Assistant
# Version: 5.0
# Last Updated: 2025-01-25
#

# Script configuration and default values
PRODUCTS_FILE="../tests/sample_products.txt"
TAXONOMY_FILE="../data/taxonomy.en-US.txt"
MODEL="gpt-4.1-nano"
VERBOSE=""
SHOW_STAGE1_PATHS=""

# Color codes for enhanced output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage information
usage() {
    echo -e "${BLUE}Taxonomy Navigator - Batch Product Analysis Tool (5-Stage AI Process)${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --products FILE            Products file to test"
    echo "                                 (default: ../tests/sample_products.txt)"
    echo "  -t, --taxonomy FILE            Taxonomy file path"
    echo "                                 (default: ../data/taxonomy.en-US.txt)"
    echo "  -m, --model MODEL              OpenAI model for Stages 1&3"
    echo "                                 (default: gpt-4.1-nano, Stage 4 uses gpt-4.1-nano)"
    echo "  -v, --verbose                  Enable verbose logging for debugging"
    echo "  -h, --help                     Show this help message"
    echo ""
    echo "5-Stage Classification Process:"
    echo "  Stage 1: AI selects top 20 categories from 4,722 options (gpt-4.1-nano)"
    echo "  Stage 2: Algorithmic filtering to most popular L1 taxonomy layer"
    echo "  Stage 3: AI refines to top 10 categories from filtered L1 taxonomy candidates (gpt-4.1-nano)"
    echo "  Stage 4: Validation to ensure no AI hallucinations (algorithmic)"
    echo "  Stage 5: AI final selection using enhanced model (gpt-4.1-nano)"
    echo ""
    echo "Examples:"
    echo "  # Simple batch testing with default products"
    echo "  $0"
    echo ""
    echo "  # Custom products file with verbose logging"
    echo "  $0 --products my_products.txt --verbose"
    echo ""
    echo "  # Custom model for Stages 1&3 (Stage 4 always uses gpt-4.1-nano)"
    echo "  $0 --products my_products.txt --model gpt-4o"
    echo ""
    echo "Output Format:"
    echo "  Each product shows: [Product Description] followed by Final Category"
    echo "  Clean, minimal output perfect for demonstrations and validation"
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
        echo -e "${YELLOW}⚠️  No API key found in file or environment variable${NC}"
        echo -e "${YELLOW}💡 You can provide your OpenAI API key using:${NC}"
        echo -e "${YELLOW}   1. Create file: data/api_key.txt with your key${NC}"
        echo -e "${YELLOW}   2. Set environment variable: export OPENAI_API_KEY=your-key${NC}"
        echo ""
    fi
}

# Function to count products in file for preview
count_products() {
    local file_path="$1"
    local count=$(grep -c "^[[:space:]]*[^[:space:]]" "$file_path" 2>/dev/null || echo "0")
    echo "$count"
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
        -m|--model)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --model requires a model name${NC}"
                exit 1
            fi
            MODEL="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --show-stage1-paths)
            SHOW_STAGE1_PATHS="--show-stage1-paths"
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

# Pre-flight checks and validation
echo -e "${BLUE}🔍 Taxonomy Navigator - Batch Product Analysis (5-Stage AI Process)${NC}"
echo -e "${BLUE}================================================================${NC}"
echo ""

# Validate input files exist
echo -e "${BLUE}📋 Validating configuration...${NC}"
validate_file "$PRODUCTS_FILE" "Products"
validate_file "$TAXONOMY_FILE" "Taxonomy"

# Check API key availability
check_api_key

# Count products for preview
product_count=$(count_products "$PRODUCTS_FILE")

# Display configuration summary
echo -e "${GREEN}📦 Products file: $PRODUCTS_FILE${NC}"
echo -e "${GREEN}📊 Products to test: $product_count${NC}"
echo -e "${GREEN}📁 Taxonomy file: $TAXONOMY_FILE${NC}"
echo -e "${GREEN}🤖 AI Models: Stages 1&3 use $MODEL, Stage 4 uses gpt-4.1-nano${NC}"

if [ -n "$VERBOSE" ]; then
    echo -e "${GREEN}🔍 Verbose logging enabled${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Starting simple batch testing...${NC}"
echo -e "${YELLOW}💡 Output format: \"[Product]: Category\"${NC}"
echo ""

# Change to the script directory to ensure relative paths work correctly
cd "$(dirname "$0")" || {
    echo -e "${RED}❌ Error: Could not change to script directory${NC}"
    exit 1
}

# Execute the appropriate tool based on mode
python3 ../tests/simple_batch_tester.py \
    --products-file "$PRODUCTS_FILE" \
    --taxonomy-file "$TAXONOMY_FILE" \
    --model "$MODEL" \
    $VERBOSE \
    $SHOW_STAGE1_PATHS

# Capture the exit code from the Python script
exit_code=$?

# Provide comprehensive feedback based on results
echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Simple batch testing completed successfully!${NC}"
    echo -e "${BLUE}💡 Results shown above in format: \"[Product]: Category\"${NC}"
    
    if [ "$product_count" -gt 0 ]; then
        echo -e "${GREEN}📊 Processed $product_count products${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}💡 Next Steps:${NC}"
    echo -e "${BLUE}  • Review the classifications above${NC}"
    echo -e "${BLUE}  • Use detailed mode (without --simple) for comprehensive analysis${NC}"
    echo -e "${BLUE}  • Use interactive mode for real-time testing${NC}"
else
    echo -e "${RED}❌ Simple batch testing failed with error code: $exit_code${NC}"
    echo -e "${YELLOW}💡 Check that all files exist and API key is configured${NC}"
    echo -e "${YELLOW}💡 Use detailed mode with --verbose for more error information${NC}"
fi

exit $exit_code 