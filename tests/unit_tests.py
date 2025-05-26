#!/usr/bin/env python3
"""
Test script for the Taxonomy Navigator.

This script performs basic tests on the TaxonomyNavigator class to ensure
it works as expected.
"""

import os
import unittest
import tempfile
from unittest.mock import patch, MagicMock
from taxonomy_navigator_engine import TaxonomyNavigator

class TestTaxonomyNavigator(unittest.TestCase):
    """Test cases for the TaxonomyNavigator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary taxonomy file
        self.temp_taxonomy = tempfile.NamedTemporaryFile(delete=False, mode='w+')
        self.temp_taxonomy.write("# Test Taxonomy\n")
        self.temp_taxonomy.write("Category A\n")
        self.temp_taxonomy.write("Category A > Subcategory A1\n")
        self.temp_taxonomy.write("Category A > Subcategory A1 > Item A1a\n")
        self.temp_taxonomy.write("Category A > Subcategory A2\n")
        self.temp_taxonomy.write("Category B\n")
        self.temp_taxonomy.write("Category B > Subcategory B1\n")
        self.temp_taxonomy.close()
        
        # Mock OpenAI client
        self.mock_openai_client = MagicMock()
        self.mock_openai_response = MagicMock()
        self.mock_openai_response.choices = [MagicMock()]
        self.mock_openai_response.choices[0].message.content = "Category A"
        self.mock_openai_client.chat.completions.create.return_value = self.mock_openai_response

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
        self.assertIn("Category A", tree["children"])
        self.assertIn("Category B", tree["children"])
        self.assertIn("Subcategory A1", tree["children"]["Category A"]["children"])
        self.assertIn("Subcategory A2", tree["children"]["Category A"]["children"])
        self.assertIn("Item A1a", tree["children"]["Category A"]["children"]["Subcategory A1"]["children"])

    @patch('openai.OpenAI')
    def test_query_openai(self, mock_openai):
        """Test that OpenAI is queried correctly."""
        mock_openai.return_value = self.mock_openai_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        categories = ["Category A", "Category B"]
        result = navigator.query_openai("Test Product", categories)
        
        # Check that OpenAI was called
        self.mock_openai_client.chat.completions.create.assert_called_once()
        
        # Check the result
        self.assertEqual(result, "Category A")

    @patch('openai.OpenAI')
    def test_navigate_taxonomy(self, mock_openai):
        """Test the taxonomy navigation."""
        # Set up OpenAI responses for each level
        responses = [
            MagicMock(choices=[MagicMock(message=MagicMock(content="Category A"))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Subcategory A1"))]),
            MagicMock(choices=[MagicMock(message=MagicMock(content="Item A1a"))])
        ]
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = responses
        mock_openai.return_value = mock_client
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        path = navigator.navigate_taxonomy("Test Product")
        
        # Check the path
        self.assertEqual(path, ["Category A", "Subcategory A1", "Item A1a"])

    @patch('openai.OpenAI')
    def test_save_results(self, mock_openai):
        """Test saving results to a file."""
        mock_openai.return_value = self.mock_openai_client
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            temp_output_path = temp_output.name
        
        navigator = TaxonomyNavigator(self.temp_taxonomy.name, "dummy_api_key")
        path = ["Category A", "Subcategory A1", "Item A1a"]
        navigator.save_results("Test Product", path, temp_output_path)
        
        # Check that the file was created and contains valid JSON
        import json
        with open(temp_output_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_info"], "Test Product")
        self.assertEqual(data[0]["category_path"], path)
        
        os.unlink(temp_output_path)

if __name__ == '__main__':
    unittest.main() 