"""
Data models for gift card information extraction.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class GiftCardInfo:
    """Represents extracted information from a gift card image."""
    
    brand: Optional[str] = None
    card_number: Optional[str] = None
    pin: Optional[str] = None
    balance: Optional[float] = None
    expiration_date: Optional[date] = None
    barcode: Optional[str] = None
    raw_text: Optional[str] = None
    confidence: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "brand": self.brand,
            "card_number": self.card_number,
            "pin": self.pin,
            "balance": self.balance,
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "barcode": self.barcode,
            "raw_text": self.raw_text,
            "confidence": self.confidence,
        }
    
    def is_valid(self) -> bool:
        """Check if the extracted info contains minimum required fields."""
        return bool(self.card_number or self.barcode)
