#!/bin/bash
#
# Taxonomy Navigator - Single Product Classification Tool
#
# This script provides both command-line and interactive interfaces for classifying
# individual products using the Taxonomy Navigator system's 5-stage AI process.
# Choose between one-off classifications with immediate results or interactive mode 
# for testing multiple products in a session.
#
# Features:
# - Single product classification with immediate results using 5-stage AI process
# - Interactive mode for testing multiple products in one session
# - Configurable taxonomy files and AI models
# - JSON output for detailed result storage
# - Verbose logging option for debugging
# - Automatic results directory creation
# - Clear success/failure feedback
# - Uses gpt-4.1-nano for initial stages, gpt-4.1-mini for final precision
# - Stage 4 validation prevents AI hallucinations
#
# 5-Stage Classification Process:
# 1. AI selects top 20 leaf nodes from all 4,722 categories (gpt-4.1-nano)
# 2. Algorithmic filtering to most popular L1 taxonomy layer
# 3. AI refines to top 10 categories from filtered L1 taxonomy candidates (gpt-4.1-nano)
# 4. Validation to ensure no AI hallucinations (algorithmic)
# 5. AI final selection using enhanced model (gpt-4.1-nano)
#
# Usage Examples:
#   # Command-line mode (single product)
#   ./classify_single_product.sh -n "iPhone 14" -d "Smartphone with camera"
#   ./classify_single_product.sh -n "Xbox Controller" -d "Gaming controller" --verbose
#
#   # Interactive mode (multiple products in session)
#   ./classify_single_product.sh --interactive
#   ./classify_single_product.sh -i --verbose --save-results
#
# Author: AI Assistant
# Version: 5.0
# Last Updated: 2025-01-25
#

# Script configuration and default values
TAXONOMY_FILE="../data/taxonomy.en-US.txt"
OUTPUT_FILE="../results/taxonomy_results.json"
MODEL="gpt-4.1-nano"
VERBOSE=""
INTERACTIVE_MODE=false
SAVE_RESULTS=""

# Color codes for enhanced output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display comprehensive usage information
usage() {
    echo -e "${BLUE}Taxonomy Navigator - Single Product Classification Tool (5-Stage AI Process)${NC}"
    echo ""
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "MODES:"
    echo "  Command-line mode (default):"
    echo "    $0 --product-name \"Product Name\" --product-description \"Description\" [options]"
    echo ""
    echo "  Interactive mode:"
    echo "    $0 --interactive [options]"
    echo "    $0 -i [options]"
    echo ""
    echo "Required Arguments (Command-line mode only):"
    echo "  -n, --product-name NAME        Product name to classify"
    echo "  -d, --product-description DESC Detailed product description"
    echo ""
    echo "Interactive Mode Options:"
    echo "  -i, --interactive              Launch interactive classification interface"
    echo "  -s, --save-results             Save session results to JSON file"
    echo ""
    echo "Common Options:"
    echo "  -t, --taxonomy FILE            Path to taxonomy file"
    echo "                                 (default: ../data/taxonomy.en-US.txt)"
    echo "  -o, --output FILE              Output JSON file for results"
    echo "                                 (default: ../results/taxonomy_results.json)"
    echo "  -m, --model MODEL              OpenAI model for Stages 1&3"
    echo "                                 (default: gpt-4.1-nano, Stage 5 uses gpt-4.1-mini)"
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
    echo "  # Single product classification"
    echo "  $0 -n \"iPhone 14 Pro\" -d \"Smartphone with advanced camera system\""
    echo ""
    echo "  # Interactive mode for testing multiple products"
    echo "  $0 --interactive"
    echo ""
    echo "  # Interactive mode with result saving"
    echo "  $0 -i --save-results --verbose"
    echo ""
    echo "  # Custom model for Stages 1&3 (Stage 4 always uses gpt-4.1-nano)"
    echo "  $0 -n \"Nike Air Max\" -d \"Running shoes\" -m gpt-4o -o my_results.json"
    echo ""
    echo "Interactive Mode Features:"
    echo "  • Test multiple products in one session using 5-stage AI process"
    echo "  • Real-time classification results"
    echo "  • Session statistics and success rates"
    echo "  • Commands: help, stats, clear, quit"
    echo "  • Optional result saving to JSON file"
    echo ""
    exit 1
}

# Function to validate required arguments for command-line mode
validate_required_args() {
    if [ "$INTERACTIVE_MODE" = true ]; then
        # Interactive mode doesn't need product name/description
        return 0
    fi
    
    local missing_args=()
    
    if [ -z "$PRODUCT_NAME" ]; then
        missing_args+=("product name")
    fi
    
    if [ -z "$PRODUCT_DESCRIPTION" ]; then
        missing_args+=("product description")
    fi
    
    if [ ${#missing_args[@]} -gt 0 ]; then
        echo -e "${RED}❌ Error: Missing required arguments for command-line mode: ${missing_args[*]}${NC}"
        echo -e "${YELLOW}💡 Use --interactive mode to classify products interactively${NC}"
        echo ""
        usage
    fi
}

# Function to validate file existence
validate_file() {
    local file_path="$1"
    local file_type="$2"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${RED}❌ Error: $file_type file '$file_path' not found.${NC}"
        
        if [ "$file_type" = "Taxonomy" ]; then
            echo -e "${YELLOW}💡 Make sure you have the taxonomy file in the data/ directory.${NC}"
            echo -e "${YELLOW}   You can download it from Google Product Taxonomy.${NC}"
        fi
        
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

# Initialize variables for required arguments
PRODUCT_NAME=""
PRODUCT_DESCRIPTION=""

# Parse command line arguments with comprehensive validation
while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--product-name)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --product-name requires a value${NC}"
                exit 1
            fi
            PRODUCT_NAME="$2"
            shift 2
            ;;
        -d|--product-description)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --product-description requires a value${NC}"
                exit 1
            fi
            PRODUCT_DESCRIPTION="$2"
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
        -o|--output)
            if [ -z "$2" ]; then
                echo -e "${RED}Error: --output requires a file path${NC}"
                exit 1
            fi
            OUTPUT_FILE="$2"
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
        -i|--interactive)
            INTERACTIVE_MODE=true
            shift
            ;;
        -s|--save-results)
            SAVE_RESULTS="--save-results"
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
if [ "$INTERACTIVE_MODE" = true ]; then
    echo -e "${BLUE}🔍 Taxonomy Navigator - Interactive Classification Interface (5-Stage AI)${NC}"
    echo -e "${BLUE}=================================================================${NC}"
else
    echo -e "${BLUE}🔍 Taxonomy Navigator - Single Product Classification (5-Stage AI)${NC}"
    echo -e "${BLUE}=============================================================${NC}"
fi
echo ""

# Validate required arguments based on mode
validate_required_args

# Validate taxonomy file exists
echo -e "${BLUE}📋 Validating configuration...${NC}"
validate_file "$TAXONOMY_FILE" "Taxonomy"

# Check API key availability
check_api_key

# Create results directory if it doesn't exist (for command-line mode)
if [ "$INTERACTIVE_MODE" = false ]; then
    results_dir="$(dirname "$OUTPUT_FILE")"
    if [ ! -d "$results_dir" ]; then
        echo -e "${BLUE}📁 Creating results directory: $results_dir${NC}"
        mkdir -p "$results_dir" || {
            echo -e "${RED}❌ Error: Could not create results directory${NC}"
            exit 1
        }
    fi
fi

# Display configuration summary
if [ "$INTERACTIVE_MODE" = true ]; then
    echo -e "${GREEN}🎮 Mode: Interactive Classification Interface${NC}"
    if [ -n "$SAVE_RESULTS" ]; then
        echo -e "${GREEN}💾 Results will be saved to file${NC}"
    fi
else
    echo -e "${GREEN}📦 Product: $PRODUCT_NAME${NC}"
    echo -e "${GREEN}📝 Description: $PRODUCT_DESCRIPTION${NC}"
    echo -e "${GREEN}💾 Output file: $OUTPUT_FILE${NC}"
fi

echo -e "${GREEN}📁 Taxonomy file: $TAXONOMY_FILE${NC}"
echo -e "${GREEN}🤖 AI Models: Stages 1&3 use $MODEL, Stage 5 uses gpt-4.1-mini${NC}"

if [ -n "$VERBOSE" ]; then
    echo -e "${GREEN}🔍 Verbose logging enabled${NC}"
fi

echo ""
if [ "$INTERACTIVE_MODE" = true ]; then
    echo -e "${BLUE}🚀 Starting interactive interface...${NC}"
    echo -e "${YELLOW}💡 Type 'help' in the interface for available commands${NC}"
else
    echo -e "${BLUE}🚀 Starting classification...${NC}"
fi
echo ""

# Change to the script directory to ensure relative paths work correctly
cd "$(dirname "$0")" || {
    echo -e "${RED}❌ Error: Could not change to script directory${NC}"
    exit 1
}

# Execute the appropriate tool based on mode
if [ "$INTERACTIVE_MODE" = true ]; then
    # Launch interactive interface
    python3 ../src/interactive_interface.py \
        --taxonomy-file "$TAXONOMY_FILE" \
        --model "$MODEL" \
        $SAVE_RESULTS \
        $VERBOSE
else
    # Execute single product classification
    python3 ../src/taxonomy_navigator_engine.py \
        --product-name "$PRODUCT_NAME" \
        --product-description "$PRODUCT_DESCRIPTION" \
        --taxonomy-file "$TAXONOMY_FILE" \
        --model "$MODEL" \
        --output-file "$OUTPUT_FILE" \
        $VERBOSE
fi

# Capture the exit code from the Python script
exit_code=$?

# Provide comprehensive feedback based on results
echo ""
if [ $exit_code -eq 0 ]; then
    if [ "$INTERACTIVE_MODE" = true ]; then
        echo -e "${GREEN}✅ Interactive session completed successfully!${NC}"
    else
        echo -e "${GREEN}✅ Classification completed successfully!${NC}"
        echo -e "${GREEN}📄 Detailed results saved to: $OUTPUT_FILE${NC}"
        
        # Show a preview of the results if the file exists and is readable
        if [ -f "$OUTPUT_FILE" ] && command -v jq >/dev/null 2>&1; then
            echo ""
            echo -e "${BLUE}📊 Result Preview:${NC}"
            echo -e "${BLUE}=================${NC}"
            # Use jq to extract and display the best match if available
            best_match=$(jq -r '.[-1].matches[] | select(.is_best_match == true) | .full_path' "$OUTPUT_FILE" 2>/dev/null)
            if [ -n "$best_match" ] && [ "$best_match" != "null" ]; then
                echo -e "${GREEN}🎯 Best Match: $best_match${NC}"
            fi
        fi
    fi
else
    if [ "$INTERACTIVE_MODE" = true ]; then
        echo -e "${RED}❌ Interactive session failed with error code: $exit_code${NC}"
    else
        echo -e "${RED}❌ Classification failed with error code: $exit_code${NC}"
    fi
    echo -e "${YELLOW}💡 Try running with --verbose for more detailed error information${NC}"
fi

exit $exit_code 