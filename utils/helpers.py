"""
Helper Utilities for Email Webhook

Common utility functions used across the webhook system.
"""

import base64
import hashlib
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import re

def generate_email_id() -> str:
    """
    Generate a unique email ID
    
    Returns:
        str: Unique email identifier
    """
    return str(uuid.uuid4())

def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def encode_attachment_data(data: bytes) -> str:
    """
    Encode binary data to base64 string
    
    Args:
        data: Binary data to encode
        
    Returns:
        str: Base64 encoded string
    """
    return base64.b64encode(data).decode('utf-8')

def decode_attachment_data(encoded_data: str) -> bytes:
    """
    Decode base64 string to binary data
    
    Args:
        encoded_data: Base64 encoded string
        
    Returns:
        bytes: Decoded binary data
    """
    return base64.b64decode(encoded_data)

def calculate_file_hash(data: bytes) -> str:
    """
    Calculate SHA-256 hash of file data
    
    Args:
        data: File data to hash
        
    Returns:
        str: SHA-256 hash in hexadecimal format
    """
    return hashlib.sha256(data).hexdigest()

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing dangerous characters
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove or replace dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:255-len(ext)-1] + ('.' + ext if ext else '')
    
    return sanitized

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def extract_domain_from_email(email: str) -> Optional[str]:
    """
    Extract domain from email address
    
    Args:
        email: Email address
        
    Returns:
        str: Domain name or None if invalid
    """
    if '@' not in email:
        return None
    
    return email.split('@')[1].lower()

def is_pdf_file(filename: str) -> bool:
    """
    Check if file is a PDF based on extension
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if PDF file
    """
    return filename.lower().endswith('.pdf')

def is_image_file(filename: str) -> bool:
    """
    Check if file is an image based on extension
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if image file
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        str: File extension (including dot) or empty string
    """
    if '.' not in filename:
        return ''
    
    return '.' + filename.split('.')[-1].lower()

def create_timestamp() -> datetime:
    """
    Create current UTC timestamp
    
    Returns:
        datetime: Current UTC timestamp
    """
    return datetime.now(timezone.utc)

def format_timestamp(timestamp: datetime) -> str:
    """
    Format timestamp as ISO string
    
    Args:
        timestamp: Datetime object
        
    Returns:
        str: ISO formatted timestamp
    """
    return timestamp.isoformat()

def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse ISO timestamp string to datetime object
    
    Args:
        timestamp_str: ISO formatted timestamp string
        
    Returns:
        datetime: Parsed datetime object or None if invalid
    """
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        str: Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'

def clean_html_tags(html_text: str) -> str:
    """
    Remove HTML tags from text
    
    Args:
        html_text: HTML text
        
    Returns:
        str: Plain text without HTML tags
    """
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html_text)

def extract_text_from_html(html_text: str) -> str:
    """
    Extract plain text from HTML content
    
    Args:
        html_text: HTML content
        
    Returns:
        str: Extracted plain text
    """
    # Remove HTML tags
    text = clean_html_tags(html_text)
    
    # Decode HTML entities
    import html
    text = html.unescape(text)
    
    # Clean up whitespace
    text = ' '.join(text.split())
    
    return text

def validate_attachment_data(attachment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean attachment data
    
    Args:
        attachment_data: Raw attachment data
        
    Returns:
        Dict: Validated and cleaned attachment data
    """
    validated = {}
    
    # Validate filename
    if 'filename' in attachment_data:
        validated['filename'] = sanitize_filename(attachment_data['filename'])
    else:
        raise ValueError("Filename is required")
    
    # Validate content type
    if 'content_type' in attachment_data:
        validated['content_type'] = attachment_data['content_type']
    else:
        # Try to guess from filename
        ext = get_file_extension(validated['filename'])
        if ext == '.pdf':
            validated['content_type'] = 'application/pdf'
        elif ext in ['.jpg', '.jpeg']:
            validated['content_type'] = 'image/jpeg'
        elif ext == '.png':
            validated['content_type'] = 'image/png'
        else:
            validated['content_type'] = 'application/octet-stream'
    
    # Validate size
    if 'size' in attachment_data:
        validated['size'] = int(attachment_data['size'])
        if validated['size'] < 0:
            raise ValueError("File size cannot be negative")
    else:
        raise ValueError("File size is required")
    
    # Validate data
    if 'data' in attachment_data and attachment_data['data']:
        try:
            # Try to decode to validate base64
            decode_attachment_data(attachment_data['data'])
            validated['data'] = attachment_data['data']
        except Exception:
            raise ValueError("Invalid base64 data")
    
    return validated
