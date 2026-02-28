"""
Utility functions for gift card image processing and text extraction.
"""

import re
from datetime import date
from typing import Optional, Dict, Any

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError as e:
    raise ImportError(
        "Pillow not installed. Run: pip install pillow"
    ) from e


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Preprocess an image to improve OCR accuracy.
    
    Args:
        image: PIL Image object.
        
    Returns:
        Preprocessed PIL Image.
    """
    # Convert to RGB if necessary
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Convert to grayscale
    grayscale = image.convert("L")
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(grayscale)
    enhanced = enhancer.enhance(2.0)
    
    # Apply sharpening filter
    sharpened = enhanced.filter(ImageFilter.SHARPEN)
    
    # Resize if too small (improves OCR for small images)
    min_dimension = 1000
    width, height = sharpened.size
    if width < min_dimension or height < min_dimension:
        scale = max(min_dimension / width, min_dimension / height)
        new_size = (int(width * scale), int(height * scale))
        sharpened = sharpened.resize(new_size, Image.Resampling.LANCZOS)
    
    return sharpened


def extract_patterns(text: str) -> Dict[str, Any]:
    """
    Extract common gift card patterns from OCR text.
    
    Args:
        text: Raw OCR text.
        
    Returns:
        Dictionary containing extracted patterns.
    """
    patterns = {
        "card_number": _extract_card_number(text),
        "pin": _extract_pin(text),
        "balance": _extract_balance(text),
        "expiration_date": _extract_expiration_date(text),
        "barcode": _extract_barcode(text),
    }
    
    return patterns


def _extract_card_number(text: str) -> Optional[str]:
    """
    Extract card number from text.
    
    Looks for patterns like:
    - 16-digit numbers (with or without spaces/dashes)
    - Numbers labeled as "Card Number", "Card #", etc.
    - Alphanumeric card numbers (like Starbucks, Amazon)
    """
    # PRIORITY 1: Look for standalone 16-digit numbers (most common card format)
    # This catches numbers like "6191 9695 1171 0892"
    standalone_pattern = r"\b([0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4})\b"
    match = re.search(standalone_pattern, text)
    if match:
        return _clean_number(match.group(1))
    
    # PRIORITY 2: Amazon claim codes (XXXX-XXXXXX-XXXXX format, alphanumeric)
    # Matches patterns like "ASOY-DSLW4H-3DMB3" or "ASOY - DSLW4H - 3DMB3"
    amazon_pattern = r"\b([A-Z0-9]{4}[\s\-]+[A-Z0-9]{5,7}[\s\-]+[A-Z0-9]{4,6})\b"
    match = re.search(amazon_pattern, text, re.IGNORECASE)
    if match:
        # Clean up the code (remove extra spaces, keep dashes)
        code = re.sub(r'\s+', '', match.group(1))
        return code
    
    # PRIORITY 3: Look for labeled card numbers (must have "number", "#", or "no" after "card")
    labeled_patterns = [
        r"card\s+number\s*(?:is|:)?\s*([A-Z0-9\s\-]{8,25})",
        r"card\s*#\s*(?:is|:)?\s*([A-Z0-9\s\-]{8,25})",
        r"card\s+no\.?\s*(?:is|:)?\s*([A-Z0-9\s\-]{8,25})",
        r"gift\s*card\s*(?:is|:)?\s*([A-Z0-9\s\-]{8,25})",
        r"claim\s+code\s*(?:is|:)?\s*([A-Z0-9\s\-]{10,25})",
    ]
    
    for pattern in labeled_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Make sure we didn't capture regular words
            captured = match.group(1).strip()
            if not re.match(r'^[A-Za-z\s]+$', captured):  # Not just letters
                return _clean_number(captured)
    
    # PRIORITY 4: Look for other long number sequences (12-19 digits)
    long_number_pattern = r"\b([0-9]{12,19})\b"
    match = re.search(long_number_pattern, text)
    if match:
        return match.group(1)
    
    # PRIORITY 5: Fallback - SKU-style codes (e.g., $8X21-495817)
    sku_pattern = r"\$([A-Z0-9]{3,}[\-][0-9]{4,})"
    match = re.search(sku_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # PRIORITY 6: Fallback - Starbucks-style alphanumeric codes (e.g., X21-495817)
    starbucks_pattern = r"\b([A-Z][0-9]{2}[\-][0-9]{6})\b"
    match = re.search(starbucks_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None


def _extract_pin(text: str) -> Optional[str]:
    """
    Extract PIN from text.
    
    Looks for patterns like:
    - "PIN: 1234"
    - "Access Code: 123456"
    - "Security Code: 1234"
    """
    pin_patterns = [
        r"pin\s*:?\s*([0-9]{4,8})",
        r"access\s*code\s*:?\s*([0-9]{4,8})",
        r"security\s*code\s*:?\s*([0-9]{4,8})",
        r"scratch\s*(?:to\s*)?reveal\s*:?\s*([0-9]{4,8})",
    ]
    
    for pattern in pin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def _extract_balance(text: str) -> Optional[float]:
    """
    Extract balance/value from text.
    
    Looks for patterns like:
    - "$25.00"
    - "Value: $50"
    - "Balance: $100.00"
    """
    balance_patterns = [
        r"(?:balance|value|amount)\s*:?\s*\$?\s*([0-9]+\.?[0-9]*)",
        r"\$\s*([0-9]+\.?[0-9]*)",
    ]
    
    for pattern in balance_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    return None


def _extract_expiration_date(text: str) -> Optional[date]:
    """
    Extract expiration date from text.
    
    Looks for patterns like:
    - "Exp: 12/25"
    - "Expires: 12/2025"
    - "Valid Until: 2025-12-31"
    """
    date_patterns = [
        (r"(?:exp(?:ires?)?|valid\s*(?:until|thru|through)?)\s*:?\s*(\d{1,2})[/\-](\d{2,4})", "md"),
        (r"(?:exp(?:ires?)?|valid\s*(?:until|thru|through)?)\s*:?\s*(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})", "ymd"),
    ]
    
    for pattern, format_type in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                if format_type == "md":
                    month = int(match.group(1))
                    year = int(match.group(2))
                    if year < 100:
                        year += 2000
                    return date(year, month, 1)
                elif format_type == "ymd":
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    return date(year, month, day)
            except ValueError:
                continue
    
    return None


def _extract_barcode(text: str) -> Optional[str]:
    """
    Extract barcode number from text.
    
    Looks for barcode-related labels and long number sequences.
    """
    barcode_patterns = [
        r"barcode\s*:?\s*([0-9]{8,20})",
        r"upc\s*:?\s*([0-9]{8,14})",
    ]
    
    for pattern in barcode_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None


def _clean_number(number_str: str) -> str:
    """Remove spaces, dashes, and other separators from a number string."""
    return re.sub(r"[\s\-]", "", number_str)
