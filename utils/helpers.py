import re
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Check if a given string is a valid URL.
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if the URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_url(url):
    """
    Format a URL by adding the https:// prefix if it's missing.
    
    Args:
        url (str): The URL to format
        
    Returns:
        str: The formatted URL
    """
    if not url:
        return ""
        
    if not re.match(r'^https?://', url):
        return f"https://{url}"
    return url

def extract_domain(url):
    """
    Extract the domain name from a URL.
    
    Args:
        url (str): The URL to extract the domain from
        
    Returns:
        str: The domain name
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain
    except:
        return url

def truncate_text(text, max_length=50):
    """
    Truncate text to a maximum length and add ellipsis if needed.
    
    Args:
        text (str): The text to truncate
        max_length (int): The maximum length of the text
        
    Returns:
        str: The truncated text
    """
    if not text:
        return ""
        
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
