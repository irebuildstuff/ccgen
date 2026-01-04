"""
Credit card generation module with Luhn algorithm validation.
Supports BIN (Bank Identification Number) of 3, 4, or 6 digits.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


def validate_bin(bin: str) -> bool:
    """Validates BIN format (3, 4, or 6 digits)."""
    if not bin.isdigit():
        return False
    return len(bin) in [3, 4, 6]


def detect_card_type(bin: str) -> Tuple[str, int]:
    """
    Detects card type and returns (card_type, card_length).
    card_type: 'visa', 'mastercard', 'amex', or 'unknown'
    card_length: 15 for Amex, 16 for others
    """
    bin_int = int(bin)
    bin_len = len(bin)
    
    # For short BINs, check first digit
    if bin_len < 6:
        first_digit = bin[0]
        if first_digit == '4':
            return ('visa', 16)
        elif first_digit == '3':
            return ('amex', 15)
        else:
            return ('unknown', 16)  # Default to 16 digits
    
    # For 6-digit BINs, check full ranges
    if bin.startswith('4'):
        return ('visa', 16)
    elif bin.startswith('34') or bin.startswith('37'):
        return ('amex', 15)
    elif bin.startswith('51') or bin.startswith('52') or bin.startswith('53') or \
         bin.startswith('54') or bin.startswith('55'):
        return ('mastercard', 16)
    elif 222100 <= bin_int <= 272099:
        return ('mastercard', 16)
    else:
        return ('unknown', 16)  # Default to 16 digits


def calculate_luhn_check_digit(partial_number: str) -> int:
    """
    Calculates the Luhn check digit for a partial card number.
    Returns the check digit (0-9).
    """
    def luhn_checksum(card_num: str) -> int:
        def digits_of(n: str):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        return checksum % 10
    
    # Calculate what check digit would make the number valid
    for check_digit in range(10):
        test_number = partial_number + str(check_digit)
        if luhn_checksum(test_number) == 0:
            return check_digit
    return 0


def luhn_check(card_number: str) -> bool:
    """
    Validates card number using Luhn algorithm.
    Returns True if valid, False otherwise.
    """
    def luhn_checksum(card_num: str) -> int:
        def digits_of(n: str):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0


def generate_card_number(bin: str, card_length: int = 16) -> str:
    """
    Generates a Luhn-valid card number from BIN.
    
    Args:
        bin: Bank Identification Number (3, 4, or 6 digits)
        card_length: Desired card length (15 for Amex, 16 for others)
    
    Returns:
        Complete card number with Luhn check digit
    """
    # Determine prefix length based on card type and BIN length
    if card_length == 15:  # Amex
        # Amex uses 15 digits total, 14 before check digit
        # Use first 4 digits from BIN (or pad if shorter)
        if len(bin) >= 4:
            prefix = bin[:4]
        else:
            prefix = bin.ljust(4, '0')  # Pad with zeros to 4 digits
        digits_before_check = 14
    else:  # 16 digits (Visa, Mastercard)
        # 16 digits total, 15 before check digit
        # Use up to 6 digits from BIN
        if len(bin) >= 6:
            prefix = bin[:6]
        elif len(bin) >= 4:
            prefix = bin[:4]
        else:
            prefix = bin[:3] if len(bin) == 3 else bin
        digits_before_check = 15
    
    # Generate remaining digits randomly
    remaining_digits = digits_before_check - len(prefix)
    if remaining_digits > 0:
        random_part = ''.join([str(random.randint(0, 9)) for _ in range(remaining_digits)])
        partial_number = prefix + random_part
    else:
        # If prefix is already too long, trim it
        partial_number = prefix[:digits_before_check]
    
    # Calculate and append Luhn check digit
    check_digit = calculate_luhn_check_digit(partial_number)
    card_number = partial_number + str(check_digit)
    
    # Verify the generated number
    if not luhn_check(card_number):
        # If somehow invalid, regenerate (shouldn't happen but safety check)
        return generate_card_number(bin, card_length)
    
    return card_number


def generate_expiry_date() -> Tuple[str, str]:
    """
    Generates a future expiry date.
    Returns (MM, YYYY) tuple as strings.
    """
    # Generate expiry between 6 months and 5 years from now
    months_ahead = random.randint(6, 60)
    expiry_date = datetime.now() + timedelta(days=months_ahead * 30)
    return (str(expiry_date.month).zfill(2), str(expiry_date.year))


def generate_cvv(card_number: str) -> str:
    """
    Generates CVV code (3 or 4 digits based on card type).
    Amex uses 4 digits, others use 3 digits.
    """
    if len(card_number) == 15:  # Amex
        return str(random.randint(1000, 9999))
    else:  # Visa, Mastercard
        return str(random.randint(100, 999))


def generate_card(bin: str) -> Dict[str, str]:
    """
    Generates a single credit card with all details.
    
    Args:
        bin: Bank Identification Number (3, 4, or 6 digits)
    
    Returns:
        Dictionary with keys: number, month, year, cvv
    """
    # Detect card type to determine length
    card_type, card_length = detect_card_type(bin)
    
    # Generate card number
    card_number = generate_card_number(bin, card_length)
    
    # Generate expiry date
    month, year = generate_expiry_date()
    
    # Generate CVV
    cvv = generate_cvv(card_number)
    
    return {
        'number': card_number,
        'month': month,
        'year': year,
        'cvv': cvv
    }


def generate_cards(bin: str, quantity: int) -> List[Dict[str, str]]:
    """
    Generates multiple credit cards.
    
    Args:
        bin: Bank Identification Number (3, 4, or 6 digits)
        quantity: Number of cards to generate
    
    Returns:
        List of card dictionaries
    """
    cards = []
    for _ in range(quantity):
        card = generate_card(bin)
        cards.append(card)
    return cards
