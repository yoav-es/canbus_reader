# utils.py

CAN_CRC_POLYNOMIAL = 0x4599
CAN_CRC_MASK = 0x7FFF

def calculate_can_crc(bit_stream: str) -> str:
    """
    Calculates the 15-bit CAN CRC remainder for a given binary bit stream.
    Implements polynomial division using the standard CAN-15 polynomial (0x4599).
    """
    remainder = 0x0000
    
    for bit_char in bit_stream:
        input_bit = int(bit_char)
        remainder_msb = (remainder >> 14) & 1
        remainder = (remainder << 1) & CAN_CRC_MASK
        
        if remainder_msb ^ input_bit:
            remainder ^= CAN_CRC_POLYNOMIAL
            
    return bin(remainder)[2:].zfill(15)