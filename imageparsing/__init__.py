"""
Gift Card Ingestion Module

This module provides functionality to read gift card images and extract
relevant information using Groq vision LLM.
"""

from .groq_parser import parse_gift_card_image
__all__ = ["parse_gift_card_image"]