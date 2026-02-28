"""
Gift Card Ingestion Module

This module provides functionality to read gift card images and extract
relevant information using OCR (pytesseract).
"""

from .card_reader import GiftCardReader
from .models import GiftCardInfo

__all__ = ["GiftCardReader", "GiftCardInfo"]
