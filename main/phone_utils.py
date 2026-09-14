"""Telefon raqamini bir xil formatga keltirish."""
import re


def phone_digits(value: str) -> str:
    digits = re.sub(r'\D', '', str(value or ''))
    if digits.startswith('998') and len(digits) >= 12:
        return digits[3:12]
    if len(digits) >= 9:
        return digits[-9:]
    return digits


def normalize_phone(value: str) -> str:
    """Saqlash formati: +998XXXXXXXXX"""
    digits = phone_digits(value)
    if len(digits) == 9:
        return f'+998{digits}'
    raw = (value or '').strip()
    return raw


def format_phone_display(value: str) -> str:
    compact = normalize_phone(value)
    digits = phone_digits(compact)
    if len(digits) == 9:
        return f'+998 {digits[0:2]} {digits[2:5]} {digits[5:7]} {digits[7:9]}'
    return compact or ''
