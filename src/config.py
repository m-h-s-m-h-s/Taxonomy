#!/usr/bin/env python3
"""
Configuration Management for Taxonomy Navigator

This module provides configuration functions for the Taxonomy Navigator system.
Currently includes API key management with multiple fallback options.

Author: AI Assistant
Version: 2.0
Last Updated: 2025-01-25
"""

import os
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

def get_api_key(api_key_arg=None):
    """
    Retrieve OpenAI API key from multiple sources with fallback hierarchy.
    
    This function implements a secure and flexible approach to API key management
    by checking multiple sources in order of precedence. This allows users to
    provide the API key in the most convenient way for their setup.
    
    The search order is designed for security and convenience:
    1. Direct argument (highest precedence) - for programmatic use
    2. Environment variable - for secure server deployments
    3. Local file - for development convenience
    
    Args:
        api_key_arg (str, optional): API key provided directly as a function argument.
                                   This takes highest precedence if provided.
        
    Returns:
        str or None: The OpenAI API key if found, None if no key is available
                    from any source.
                    
    Example:
        # Try to get API key with fallback
        api_key = get_api_key()
        if not api_key:
            raise ValueError("No API key found")
            
        # Or provide directly
        api_key = get_api_key("sk-...")
        
    Security Notes:
        - Environment variables are preferred for production deployments
        - Local files should only be used in development environments
        - Never commit API keys to version control
        - The api_key.txt file is in .gitignore to prevent accidental commits
    """
    logger.debug("Attempting to retrieve OpenAI API key from available sources")
    
    # Priority 1: Direct argument (highest precedence)
    # This allows programmatic override and is useful for testing
    if api_key_arg:
        logger.debug("API key provided as direct argument")
        return api_key_arg
    
    # Priority 2: Environment variable
    # This is the recommended approach for production deployments
    # as it keeps secrets out of code and configuration files
    env_key = os.environ.get('OPENAI_API_KEY')
    if env_key:
        logger.debug("API key found in environment variable OPENAI_API_KEY")
        return env_key
    
    # Priority 3: Local file (lowest precedence)
    # This is convenient for development but should not be used in production
    # The file should be in the same directory as this utils.py file
    try:
        # Construct path to api_key.txt relative to this file's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        api_key_file = os.path.join(current_dir, '..', 'data', 'api_key.txt')
        
        # Normalize the path to handle the .. properly
        api_key_file = os.path.normpath(api_key_file)
        
        if os.path.exists(api_key_file):
            logger.debug(f"Found API key file at: {api_key_file}")
            with open(api_key_file, 'r', encoding='utf-8') as f:
                key = f.read().strip()
                if key:
                    logger.debug("API key successfully read from file")
                    return key
                else:
                    logger.warning("API key file exists but is empty")
        else:
            logger.debug(f"API key file not found at: {api_key_file}")
            
    except Exception as e:
        logger.warning(f"Error reading API key file: {e}")
    
    # No API key found from any source
    logger.warning("No OpenAI API key found from any source")
    logger.info("API key sources checked:")
    logger.info("1. Direct argument: Not provided")
    logger.info("2. Environment variable OPENAI_API_KEY: Not set")
    logger.info("3. File data/api_key.txt: Not found or empty")
    
    return None

def validate_api_key_format(api_key):
    """
    Validate that an API key has the expected OpenAI format.
    
    OpenAI API keys typically start with 'sk-' followed by a long string
    of characters. This function performs basic format validation.
    
    Args:
        api_key (str): The API key to validate
        
    Returns:
        bool: True if the key appears to have valid format, False otherwise
        
    Note:
        This only validates format, not whether the key is actually valid
        with OpenAI's servers. A properly formatted key may still be expired
        or invalid.
    """
    if not api_key or not isinstance(api_key, str):
        return False
        
    # OpenAI API keys start with 'sk-' and are typically 51+ characters
    if not api_key.startswith('sk-'):
        return False
        
    if len(api_key) < 20:  # Minimum reasonable length
        return False
        
    return True

def setup_api_key_file(api_key, overwrite=False):
    """
    Create or update the API key file for development use.
    
    This utility function helps set up the local API key file for development.
    It includes safety checks to prevent accidental overwrites.
    
    Args:
        api_key (str): The API key to write to the file
        overwrite (bool): Whether to overwrite existing file. Defaults to False.
        
    Returns:
        bool: True if file was created/updated successfully, False otherwise
        
    Raises:
        ValueError: If API key format is invalid
        FileExistsError: If file exists and overwrite=False
        
    Example:
        # Set up API key file for development
        setup_api_key_file("sk-your-key-here", overwrite=True)
    """
    if not validate_api_key_format(api_key):
        raise ValueError("Invalid API key format. OpenAI keys should start with 'sk-'")
    
    # Determine file path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.normpath(os.path.join(current_dir, '..', 'data'))
    api_key_file = os.path.join(data_dir, 'api_key.txt')
    
    # Check if file exists and handle overwrite logic
    if os.path.exists(api_key_file) and not overwrite:
        raise FileExistsError(f"API key file already exists at {api_key_file}. Use overwrite=True to replace it.")
    
    try:
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Write the API key
        with open(api_key_file, 'w', encoding='utf-8') as f:
            f.write(api_key)
            
        logger.info(f"API key file created at: {api_key_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create API key file: {e}")
        return False 