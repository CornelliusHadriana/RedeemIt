#!/usr/bin/env python3
"""Test script for gift card image parsing."""

import sys
from pathlib import Path

# Add parent directory to path so we can import imageparsing
sys.path.insert(0, str(Path(__file__).parent.parent))

from imageparsing import GiftCardReader

# Get path to test image (relative to this script)
script_dir = Path(__file__).parent
image_path = script_dir / "amazon_giftcard.png"

reader = GiftCardReader()
result = reader.read_image(image_path)

print(f"Brand: {result.brand}")
print(f"Card Number: {result.card_number}")
print(f"PIN: {result.pin}")
print(f"Balance: {result.balance}")
print(f"Confidence: {result.confidence}")
print(f"\nRaw OCR Text:\n{result.raw_text[:500]}...")