#!/usr/bin/env python3
"""
Test script for the Taxonomy Navigator.

This script performs basic tests on the TaxonomyNavigator class to ensure
the 5-stage classification process works as expected.
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from taxonomy_navigator_engine import TaxonomyNavigator

class TestTaxonomyNavigator(unittest.TestCase):
    """Test cases for the TaxonomyNavigator class with 5-stage classification."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary taxonomy file
        self.temp_taxonomy = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.temp_taxonomy.write("# Test Taxonomy\n")
        self.temp_taxonomy.write("Electronics\n")
        self.temp_taxonomy.write("Electronics > Cell Phones\n")
        self.temp_taxonomy.write("Electronics > Cell Phones > Smartphones\n")
        self.temp_taxonomy.write("Electronics > Computers\n")
        self.temp_taxonomy.write("Electronics > Computers > Laptops\n")
        self.temp_taxonomy.write("Apparel\n")
        self.temp_taxonomy.write("Apparel > Shoes\n")
        self.temp_taxonomy.write("Apparel > Shoes > Athletic Shoes\n")
        self.temp_taxonomy.close()
        
        # Mock OpenAI client
        self.mock_openai_client = MagicMock()

    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.temp_taxonomy.name)

    @patch('openai.OpenAI')
    def test_build_taxonomy_tree(self, mock_openai):
        """Test that the taxonomy tree is built correctly."""
        mock_openai.return_value = self.mock_openai_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        tree = navigator.taxonomy_tree
        
        # Check tree structure
        self.assertIn("Electronics", tree["children"])
        self.assertIn("Apparel", tree["children"])
        self.assertIn("Cell Phones", tree["children"]["Electronics"]["children"])
        self.assertIn("Computers", tree["children"]["Electronics"]["children"])
        self.assertIn("Smartphones", tree["children"]["Electronics"]["children"]["Cell Phones"]["children"])

    @patch('openai.OpenAI')
    def test_stage1_leaf_matching(self, mock_openai):
        """Test Stage 1: Initial leaf node matching."""
        # Mock response for Stage 1 (top 20 leaf nodes)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Smartphones\nLaptops\nAthletic Shoes"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        result = navigator.stage1_leaf_matching("iPhone 14: Smartphone")
        
        # Check that OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check the result contains expected categories
        self.assertIn("Smartphones", result)
        self.assertIn("Laptops", result)
        self.assertIn("Athletic Shoes", result)

    @patch('openai.OpenAI')
    def test_stage2_layer_filtering(self, mock_openai):
        """Test Stage 2: Layer filtering."""
        mock_openai.return_value = self.mock_openai_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        
        # Test with mixed categories from different layers
        selected_leaves = ["Smartphones", "Laptops", "Athletic Shoes"]
        filtered = navigator.stage2_layer_filtering(selected_leaves)
        
        # Should filter to most popular layer (Electronics has 2, Apparel has 1)
        self.assertIn("Smartphones", filtered)
        self.assertIn("Laptops", filtered)
        self.assertNotIn("Athletic Shoes", filtered)

    @patch('openai.OpenAI')
    def test_stage3_refined_selection(self, mock_openai):
        """Test Stage 3: Refined selection."""
        # Mock response for Stage 3 (top 10 from filtered)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Smartphones\nLaptops"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        filtered_leaves = ["Smartphones", "Laptops"]
        result = navigator.stage3_refined_selection("iPhone 14: Smartphone", filtered_leaves)
        
        # Check that OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check the result
        self.assertIn("Smartphones", result)
        self.assertIn("Laptops", result)

    @patch('openai.OpenAI')
    def test_stage4_validation(self, mock_openai):
        """Test Stage 4: Validation."""
        mock_openai.return_value = self.mock_openai_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        
        # Test with mix of valid and invalid categories
        refined_leaves = ["Smartphones", "Laptops", "InvalidCategory"]
        validated = navigator.stage4_validation(refined_leaves)
        
        # Should only return valid categories
        self.assertIn("Smartphones", validated)
        self.assertIn("Laptops", validated)
        self.assertNotIn("InvalidCategory", validated)
        self.assertEqual(len(validated), 2)

    @patch('openai.OpenAI')
    def test_stage5_final_selection(self, mock_openai):
        """Test Stage 5: Final selection."""
        # Mock response for Stage 5 (final selection)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1"  # Select first option
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        validated_leaves = ["Smartphones", "Laptops"]
        result = navigator.stage5_final_selection("iPhone 14: Smartphone", validated_leaves)
        
        # Check that OpenAI was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Check the result (should be 0-based index)
        self.assertEqual(result, 0)

    @patch('openai.OpenAI')
    def test_navigate_taxonomy_full_process(self, mock_openai):
        """Test the complete 5-stage taxonomy navigation process."""
        # Set up OpenAI responses for each stage
        responses = [
            # Stage 1: Leaf matching
            MagicMock(choices=[MagicMock(message=MagicMock(content="Smartphones\nLaptops\nAthletic Shoes"))]),
            # Stage 3: Refined selection
            MagicMock(choices=[MagicMock(message=MagicMock(content="Smartphones\nLaptops"))]),
            # Stage 5: Final selection
            MagicMock(choices=[MagicMock(message=MagicMock(content="1"))])
        ]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses
        mock_openai.return_value = mock_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        paths, best_idx = navigator.navigate_taxonomy("iPhone 14: Smartphone")
        
        # Check that we got valid results
        self.assertIsInstance(paths, list)
        self.assertIsInstance(best_idx, int)
        self.assertGreaterEqual(best_idx, 0)
        
        # Check that the best path is valid
        if paths != [["False"]]:
            self.assertLess(best_idx, len(paths))
            best_path = paths[best_idx]
            self.assertIsInstance(best_path, list)
            self.assertGreater(len(best_path), 0)

    @patch('openai.OpenAI')
    def test_save_results(self, mock_openai):
        """Test saving results to a file."""
        mock_openai.return_value = self.mock_openai_client
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        paths = [["Electronics", "Cell Phones", "Smartphones"]]
        best_idx = 0
        navigator.save_results("iPhone 14: Smartphone", paths, best_idx, temp_output_path)
        
        # Check that the file was created and contains valid JSON
        import json
        with open(temp_output_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_info"], "iPhone 14: Smartphone")
        self.assertEqual(data[0]["best_match_index"], 0)
        self.assertEqual(len(data[0]["matches"]), 1)
        self.assertEqual(data[0]["matches"][0]["category_path"], ["Electronics", "Cell Phones", "Smartphones"])
        
        os.unlink(temp_output_path)

if __name__ == '__main__':
    unittest.main() 