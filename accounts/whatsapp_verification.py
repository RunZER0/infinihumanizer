"""
WhatsApp Verification System with Morse Code Encoding
======================================================
Uses QR codes to initiate WhatsApp messages for manual approval.

Morse Code System:
A = 1, B = 2, C = 3, D = 4, E = 5, F = 6, G = 7, H = 8, I = 9, J = 0
"""

import random
import qrcode
from io import BytesIO
import base64
from urllib.parse import quote


# Morse code mapping
MORSE_ENCODE = {
    '1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E',
    '6': 'F', '7': 'G', '8': 'H', '9': 'I', '0': 'J'
}

MORSE_DECODE = {v: k for k, v in MORSE_ENCODE.items()}


def generate_verification_code():
    """Generate a random 6-digit numeric code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def encode_to_morse(numeric_code):
    """
    Convert numeric code to morse code (A-J).
    Example: "123456" -> "ABCDEF"
    """
    return ''.join([MORSE_ENCODE[digit] for digit in numeric_code])


def decode_from_morse(morse_code):
    """
    Convert morse code (A-J) back to numeric.
    Example: "ABCDEF" -> "123456"
    """
    return ''.join([MORSE_DECODE[char.upper()] for char in morse_code])


def generate_whatsapp_qr(email, encoded_code, phone_number="+254795191421"):
    """
    Generate a QR code that opens WhatsApp with a pre-filled message.
    
    Args:
        email: User's email address
        encoded_code: The morse-encoded verification code
        phone_number: Your WhatsApp number
        
    Returns:
        Base64-encoded QR code image
    """
    # Create WhatsApp message
    message = f"Kindly approve my signup via email: {email}\n\nVerification Code: {encoded_code}"
    
    # URL encode the message
    encoded_message = quote(message)
    
    # Create WhatsApp URL (works on mobile devices)
    # Format: https://wa.me/PHONE?text=MESSAGE
    whatsapp_url = f"https://wa.me/{phone_number.replace('+', '')}?text={encoded_message}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(whatsapp_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64


def verify_code(stored_numeric_code, submitted_code):
    """
    Verify if the submitted numeric code matches the stored one.
    
    Args:
        stored_numeric_code: The original 6-digit code
        submitted_code: The code submitted by user
        
    Returns:
        Boolean indicating if codes match
    """
    return stored_numeric_code == submitted_code
