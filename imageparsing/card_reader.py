"""
Gift Card Reader Module

Uses pytesseract OCR to extract information from gift card images.
Optionally uses Google Gemini (free tier) for intelligent extraction.
"""

import os
import re
from pathlib import Path
from typing import Union, Optional

try:
    import pytesseract
    from PIL import Image
except ImportError as e:
    raise ImportError(
        "Required dependencies not installed. "
        "Run: pip install pytesseract pillow"
    ) from e

from .models import GiftCardInfo
from .utils import preprocess_image, extract_patterns


class GiftCardReader:
    """
    Reads gift card images and extracts relevant information using OCR.
    Optionally uses LLM (Google Gemini) for more accurate extraction.
    """
    
    # Common gift card brand patterns
    KNOWN_BRANDS = [
        "amazon", "visa", "mastercard", "target", "walmart", "starbucks",
        "apple", "google play", "netflix", "spotify", "steam", "xbox",
        "playstation", "nintendo", "best buy", "home depot", "lowes",
        "costco", "sephora", "ulta", "nike", "adidas", "uber", "lyft",
        "doordash", "grubhub", "chipotle", "panera", "dunkin", "mcdonald"
    ]
    
    def __init__(self, tesseract_cmd: Optional[str] = None, use_llm: bool = True):
        """
        Initialize the GiftCardReader.
        
        Args:
            tesseract_cmd: Optional path to tesseract executable.
            use_llm: Whether to use LLM for extraction (requires GOOGLE_API_KEY).
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.use_llm = use_llm and bool(os.getenv("GOOGLE_API_KEY"))
    
    def read_image(self, image_path: Union[str, Path]) -> GiftCardInfo:
        """
        Read a gift card image and extract information.
        
        Args:
            image_path: Path to the gift card image.
            
        Returns:
            GiftCardInfo object containing extracted data.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        image = Image.open(image_path)
        
        # Run multi-pass OCR to handle different text styles
        raw_text = self._multi_pass_ocr(image)
        
        # Extract structured information
        return self._parse_text(raw_text)
    
    def _multi_pass_ocr(self, image: Image.Image) -> str:
        """
        Run OCR with multiple preprocessing methods and combine results.
        
        This handles gift cards where text may be on different backgrounds
        (colored, gradient, etc.) that require different preprocessing.
        """
        from PIL import ImageOps
        
        texts = []
        
        # Pass 1: Standard preprocessing (contrast enhancement)
        processed = preprocess_image(image)
        texts.append(pytesseract.image_to_string(processed))
        
        # Pass 2: Threshold preprocessing (for text on colored backgrounds)
        grayscale = image.convert("L")
        threshold = grayscale.point(lambda x: 0 if x < 100 else 255, "1")
        texts.append(pytesseract.image_to_string(threshold))
        
        # Pass 3: Different threshold level
        threshold2 = grayscale.point(lambda x: 0 if x < 128 else 255, "1")
        texts.append(pytesseract.image_to_string(threshold2))
        
        # Combine all text, removing duplicates while preserving order
        combined = "\n".join(texts)
        return combined
    
    def read_image_bytes(self, image_bytes: bytes) -> GiftCardInfo:
        """
        Read gift card information from image bytes.
        
        Args:
            image_bytes: Raw image data as bytes.
            
        Returns:
            GiftCardInfo object containing extracted data.
        """
        from io import BytesIO
        
        image = Image.open(BytesIO(image_bytes))
        
        # Run multi-pass OCR to handle different text styles
        raw_text = self._multi_pass_ocr(image)
        
        # Extract structured information
        return self._parse_text(raw_text)
    
    def _parse_text(self, raw_text: str) -> GiftCardInfo:
        """
        Parse raw OCR text and extract gift card information.
        
        Args:
            raw_text: Raw text extracted from OCR.
            
        Returns:
            GiftCardInfo object with parsed data.
        """
        # Try LLM extraction first if available
        if self.use_llm:
            try:
                from .llm_extractor import extract_with_gemini
                extracted = extract_with_gemini(raw_text)
                
                if extracted.get("card_number"):
                    return GiftCardInfo(
                        brand=extracted.get("brand"),
                        card_number=extracted.get("card_number"),
                        pin=extracted.get("pin"),
                        balance=extracted.get("balance"),
                        raw_text=raw_text,
                        confidence=0.9,  # High confidence with LLM
                    )
            except Exception as e:
                print(f"LLM extraction failed, falling back to regex: {e}")
        
        # Fallback to regex-based extraction
        patterns = extract_patterns(raw_text)
        
        return GiftCardInfo(
            brand=self._detect_brand(raw_text),
            card_number=patterns.get("card_number"),
            pin=patterns.get("pin"),
            balance=patterns.get("balance"),
            expiration_date=patterns.get("expiration_date"),
            barcode=patterns.get("barcode"),
            raw_text=raw_text,
            confidence=self._calculate_confidence(patterns),
        )
    
    def _detect_brand(self, text: str) -> Optional[str]:
        """
        Detect the gift card brand from OCR text.
        
        Args:
            text: Raw OCR text.
            
        Returns:
            Detected brand name or None.
        """
        text_lower = text.lower()
        for brand in self.KNOWN_BRANDS:
            if brand in text_lower:
                return brand.title()
        return None
    
    def _calculate_confidence(self, patterns: dict) -> float:
        """
        Calculate confidence score based on extracted patterns.
        
        Args:
            patterns: Dictionary of extracted patterns.
            
        Returns:
            Confidence score between 0.0 and 1.0.
        """
        score = 0.0
        weights = {
            "card_number": 0.4,
            "pin": 0.2,
            "balance": 0.2,
            "barcode": 0.2,
        }
        
        for key, weight in weights.items():
            if patterns.get(key):
                score += weight
        
        return min(score, 1.0)
