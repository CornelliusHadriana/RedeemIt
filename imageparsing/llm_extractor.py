"""
LLM-based gift card information extractor using Google Gemini (free tier).
"""

import os
import json
import re
from typing import Optional, Dict, Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


EXTRACTION_PROMPT = """You are a gift card information extractor. Given the OCR text from a gift card image, extract the following information:

- brand: The gift card brand (e.g., Amazon, Starbucks, Target)
- card_number: The gift card number/code (may have dashes, spaces, or be alphanumeric). Look for claim codes, card numbers, or redemption codes.
- pin: The PIN or security code if present
- balance: The card balance/value if shown (as a number only, no currency symbol)

Return ONLY valid JSON in this exact format:
{"brand": "...", "card_number": "...", "pin": "...", "balance": ...}

Use null for any field you cannot find. Do not include any explanation, just the JSON.

OCR Text:
"""


def extract_with_gemini(raw_text: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Use Google Gemini to intelligently extract gift card info from OCR text.
    
    Args:
        raw_text: The raw OCR text from the gift card image.
        api_key: Optional API key. If not provided, uses GOOGLE_API_KEY env var.
        
    Returns:
        Dictionary with extracted fields: brand, card_number, pin, balance
    """
    if genai is None:
        raise ImportError(
            "google-genai not installed. Run: pip install google-genai"
        )
    
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "No API key provided. Set GOOGLE_API_KEY environment variable or pass api_key parameter."
        )
    
    client = genai.Client(api_key=api_key)
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=EXTRACTION_PROMPT + raw_text,
            config=types.GenerateContentConfig(
                temperature=0,
                max_output_tokens=200,
            )
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Try to find JSON in the response
        json_match = re.search(r'\{[^}]+\}', response_text)
        if json_match:
            return json.loads(json_match.group())
        
        return json.loads(response_text)
        
    except json.JSONDecodeError:
        return {"brand": None, "card_number": None, "pin": None, "balance": None}
    except Exception as e:
        print(f"Gemini extraction error: {e}")
        return {"brand": None, "card_number": None, "pin": None, "balance": None}
