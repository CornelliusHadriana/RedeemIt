#!/usr/bin/env python3
"""Debug script to extract card number from Starbucks card."""

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

image = Image.open('imageparsing/starbucks_giftcard.png')

# Crop the region where card number should be (between 'is' at y=92 and 'Treat' at y=201)
card_region = image.crop((0, 110, 800, 200))

print('=== Cropped region - Original ===')
text = pytesseract.image_to_string(card_region, config='--psm 7')
print(repr(text))

print('\n=== Cropped - Grayscale + High Contrast ===')
gray = card_region.convert('L')
enhanced = ImageEnhance.Contrast(gray).enhance(3.0)
text = pytesseract.image_to_string(enhanced, config='--psm 7 -c tessedit_char_whitelist=0123456789')
print(repr(text))

print('\n=== Cropped - Inverted ===')
inverted = ImageOps.invert(gray)
text = pytesseract.image_to_string(inverted, config='--psm 7')
print(repr(text))

print('\n=== Cropped - Threshold ===')
threshold = gray.point(lambda x: 0 if x < 100 else 255, '1')
text = pytesseract.image_to_string(threshold, config='--psm 7')
print(repr(text))

print('\n=== Full image with digits whitelist ===')
gray_full = image.convert('L')
text = pytesseract.image_to_string(gray_full, config='-c tessedit_char_whitelist=0123456789')
print(text[:300])
