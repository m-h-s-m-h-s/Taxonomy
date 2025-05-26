#!/usr/bin/env python3
"""
Taxonomy Navigator Interactive Interface

This module provides an interactive command-line interface for the Taxonomy Navigator
system. It allows users to test product classifications in real-time without needing
to use command-line arguments for each query.

Features:
- Interactive product entry with prompts
- Real-time classification results using 5-stage AI process
- Option to save results to file
- Continuous operation until user exits
- Verbose logging option for debugging
- Support for both simple and detailed output formats

This interface is ideal for:
- Testing the classification system with various products
- Demonstrating the system capabilities
- Development and debugging
- Quick ad-hoc classifications

The system uses a sophisticated five-stage approach:
1. Initial Leaf Node Matching: AI selects top 20 relevant categories from all 4,722 options
2. Layer Filtering: Algorithmic filtering to most popular L1 taxonomy layer
3. Refined Selection: AI refines to top 10 categories from filtered L1 taxonomy candidates
4. Validation: Ensures AI didn't hallucinate any category names that don't exist
5. Final Selection: AI selects best match using enhanced model (gpt-4.1-mini)

Author: AI Assistant
Version: 5.0
Last Updated: 2025-01-25
"""

import os
import sys
import argparse
import logging
import json
from datetime import datetime

# Add the src directory to the Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy_navigator_engine import TaxonomyNavigator
from config import get_api_key

# Configure logging for the interface
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("taxonomy_interface")

class TaxonomyInterface:
    """
    Interactive interface for the Taxonomy Navigator system.
    
    This class provides a user-friendly command-line interface that allows
    users to interactively classify products without needing to restart
    the program for each classification.
    
    Attributes:
        navigator (TaxonomyNavigator): The taxonomy navigation engine
        save_results (bool): Whether to save results to file
        output_file (str): Path to output file if saving results
        session_results (list): List of all results from current session
    """
    
    def __init__(self, taxonomy_file=None, api_key=None, 
                 model="gpt-4.1-nano", save_results=False, output_file=None):
        """
        Initialize the interactive interface.
        
        Args:
            taxonomy_file (str): Path to taxonomy file
            api_key (str, optional): OpenAI API key
            model (str): OpenAI model for initial classification stage
            save_results (bool): Whether to save results to file
            output_file (str, optional): Output file path
            
        Raises:
            ValueError: If API key cannot be obtained
            FileNotFoundError: If taxonomy file doesn't exist
        """
        logger.info("Initializing Taxonomy Navigator Interactive Interface")
        
        # Set default taxonomy file path if not provided
        if taxonomy_file is None:
            taxonomy_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'taxonomy.en-US.txt')
        
        # Initialize the navigator
        self.navigator = TaxonomyNavigator(taxonomy_file, api_key, model)
        
        # Configure result saving
        self.save_results = save_results
        self.output_file = output_file or f"interactive_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.session_results = []
        
        logger.info("Interface initialized successfully")
        
    def display_welcome(self):
        """Display welcome message and usage instructions."""
        print("\n" + "="*70)
        print("🔍 TAXONOMY NAVIGATOR - INTERACTIVE INTERFACE")
        print("="*70)
        print("\nWelcome to the AI-powered product classification system!")
        print("\nThis interface uses a sophisticated 5-stage AI process to classify")
        print("products into appropriate taxonomy categories using OpenAI's models.")
        print("\n📋 How to use:")
        print("  • Enter product information when prompted")
        print("  • Use format: 'Product Name: Description' or just 'Product Name'")
        print("  • Type 'quit', 'exit', or 'q' to end the session")
        print("  • Type 'help' for additional commands")
        print("  • Type 'stats' to see session statistics")
        print("\n💡 Examples:")
        print("  • iPhone 14 Pro: Smartphone with advanced camera system")
        print("  • Xbox Wireless Controller: Gaming controller with Bluetooth")
        print("  • Nike Air Max: Running shoes with air cushioning")
        print("\n🤖 5-Stage Classification Process:")
        print("  1. AI selects top 20 categories from 4,722 options")
        print("  2. Algorithmic filtering to most popular L1 taxonomy layer")
        print("  3. AI refines to top 10 categories from filtered L1 taxonomy candidates")
        print("  4. Validation: Ensures AI didn't hallucinate any category names that don't exist")
        print("  5. AI final selection using enhanced model (gpt-4.1-mini)")
        print("\n" + "="*70 + "\n")
        
    def display_help(self):
        """Display help information and available commands."""
        print("\n📖 HELP - Available Commands:")
        print("-" * 40)
        print("🔍 Classification Commands:")
        print("  • Enter any product info to classify it")
        print("  • Format: 'Product Name: Description'")
        print("  • Or just: 'Product Name'")
        print("\n⚙️  System Commands:")
        print("  • help, h          - Show this help message")
        print("  • stats, statistics - Show session statistics")
        print("  • clear, cls       - Clear the screen")
        print("  • quit, exit, q    - Exit the interface")
        print("\n💾 Results:")
        if self.save_results:
            print(f"  • Results are being saved to: {self.output_file}")
        else:
            print("  • Results are not being saved (use --save-results to enable)")
        print("-" * 40 + "\n")
        
    def display_stats(self):
        """Display session statistics."""
        total_classifications = len(self.session_results)
        successful_classifications = len([r for r in self.session_results if r['best_match'] != 'False'])
        failed_classifications = total_classifications - successful_classifications
        
        print("\n📊 SESSION STATISTICS:")
        print("-" * 30)
        print(f"Total Classifications: {total_classifications}")
        print(f"Successful: {successful_classifications}")
        print(f"Failed: {failed_classifications}")
        
        if total_classifications > 0:
            success_rate = (successful_classifications / total_classifications) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            # Show recent classifications
            print("\n🕒 Recent Classifications:")
            recent = self.session_results[-5:]  # Last 5
            for i, result in enumerate(recent, 1):
                product = result['product_info'][:40] + "..." if len(result['product_info']) > 40 else result['product_info']
                match = result['best_match']
                print(f"  {i}. {product} → {match}")
        
        print("-" * 30 + "\n")
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def classify_product(self, product_info):
        """
        Classify a single product and display results.
        
        Args:
            product_info (str): Product information to classify
            
        Returns:
            dict: Classification result with metadata
        """
        print(f"\n🔍 Classifying: {product_info}")
        print("⏳ Processing... (this may take a few seconds)")
        
        try:
            # Perform classification
            start_time = datetime.now()
            paths, best_match_idx = self.navigator.navigate_taxonomy(product_info)
            end_time = datetime.now()
            
            # Determine best match
            if paths == [["False"]]:
                best_match = "False"
                best_path = []
            else:
                best_path = paths[best_match_idx]
                best_match = " > ".join(best_path)
            
            # Create result record
            result = {
                'timestamp': start_time.isoformat(),
                'product_info': product_info,
                'best_match': best_match,
                'best_path': best_path,
                'all_candidates': [" > ".join(path) for path in paths] if paths != [["False"]] else [],
                'processing_time_seconds': (end_time - start_time).total_seconds(),
                'success': best_match != "False"
            }
            
            # Display result in clean format
            print(f"\n[{product_info}]")
            if best_match == "False":
                print("False")
            else:
                print(best_path[-1] if best_path else "False")
            print("-" * 50)
            
            # Save to session results
            self.session_results.append(result)
            
            # Save to file if enabled
            if self.save_results:
                self._save_result_to_file(result)
                
            return result
            
        except Exception as e:
            error_msg = f"Error during classification: {e}"
            logger.error(error_msg)
            print(f"\n❌ {error_msg}")
            
            # Create error result
            result = {
                'timestamp': datetime.now().isoformat(),
                'product_info': product_info,
                'best_match': 'Error',
                'error': str(e),
                'success': False
            }
            self.session_results.append(result)
            return result
    
    def _save_result_to_file(self, result):
        """
        Save a single result to the output file.
        
        Args:
            result (dict): Classification result to save
        """
        try:
            # Append to existing file or create new one
            if os.path.exists(self.output_file):
                # Read existing data
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Add new result
            data.append(result)
            
            # Write back to file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.debug(f"Result saved to {self.output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save result to file: {e}")
    
    def run(self):
        """
        Run the interactive interface main loop.
        
        This method handles the main interaction loop, processing user input
        and dispatching to appropriate handlers.
        """
        self.display_welcome()
        
        try:
            while True:
                # Get user input
                try:
                    user_input = input("🔍 Enter product info (or 'help' for commands): ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n\n👋 Goodbye!")
                    break
                
                # Handle empty input
                if not user_input:
                    print("⚠️  Please enter some product information or type 'help' for commands.")
                    continue
                
                # Process commands
                command = user_input.lower()
                
                if command in ['quit', 'exit', 'q']:
                    print("\n👋 Thank you for using Taxonomy Navigator!")
                    if self.session_results:
                        print(f"📊 Session Summary: {len(self.session_results)} classifications completed")
                        if self.save_results:
                            print(f"💾 Results saved to: {self.output_file}")
                    break
                    
                elif command in ['help', 'h']:
                    self.display_help()
                    continue
                    
                elif command in ['stats', 'statistics']:
                    self.display_stats()
                    continue
                    
                elif command in ['clear', 'cls']:
                    self.clear_screen()
                    self.display_welcome()
                    continue
                
                # Classify the product
                self.classify_product(user_input)
                
        except Exception as e:
            logger.error(f"Unexpected error in interface: {e}")
            print(f"\n❌ An unexpected error occurred: {e}")
            print("Please restart the interface.")

def main():
    """
    Command-line interface for the interactive taxonomy navigator.
    
    Provides options for configuring the interface and underlying classification system.
    """
    parser = argparse.ArgumentParser(
        description='Interactive interface for AI-powered product taxonomy classification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Basic interactive mode
  %(prog)s --save-results                     # Save results to file
  %(prog)s --verbose --model gpt-4.1-nano    # Verbose mode with different model
  %(prog)s --taxonomy-file custom.txt         # Use custom taxonomy file
        """
    )
    
    # Configuration arguments
    default_taxonomy = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'taxonomy.en-US.txt')
    parser.add_argument('--taxonomy-file', default=default_taxonomy,
                       help='Path to taxonomy file (default: data/taxonomy.en-US.txt)')
    parser.add_argument('--api-key',
                       help='OpenAI API key (optional if set in api_key.txt or environment)')
    parser.add_argument('--model', default='gpt-4.1-nano',
                       help='OpenAI model for Stage 1 classification (default: gpt-4.1-nano)')
    
    # Output options
    parser.add_argument('--save-results', action='store_true',
                       help='Save classification results to JSON file')
    parser.add_argument('--output-file',
                       help='Output file path (default: auto-generated with timestamp)')
    
    # Debugging options
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging for debugging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        # Suppress all logging for clean output
        logging.getLogger().setLevel(logging.CRITICAL)
        logging.getLogger("taxonomy_navigator").setLevel(logging.CRITICAL)
        logging.getLogger("httpx").setLevel(logging.CRITICAL)
    
    try:
        # Validate API key availability
        api_key = get_api_key(args.api_key)
        if not api_key:
            print("❌ Error: OpenAI API key not found.")
            print("\n💡 Please provide your API key using one of these methods:")
            print("   1. Set environment variable: export OPENAI_API_KEY=your-key")
            print("   2. Create file: data/api_key.txt with your key")
            print("   3. Use command line: --api-key your-key")
            sys.exit(1)
        
        # Initialize and run the interface
        interface = TaxonomyInterface(
            taxonomy_file=args.taxonomy_file,
            api_key=api_key,
            model=args.model,
            save_results=args.save_results,
            output_file=args.output_file
        )
        
        interface.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Interface interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start interface: {e}")
        print(f"❌ Error starting interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 