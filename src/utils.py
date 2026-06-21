# utils.py

CAN_CRC_POLYNOMIAL = 0x4599
CAN_CRC_MASK = 0x7FFF

def calculate_can_crc(data: bytes) -> str:
    """
    Calculates the 15-bit CAN CRC remainder for a given bytes object.
    Operates on bits directly without string conversion.
    """
    remainder = 0x0000
    
    for byte in data:
        for i in range(7, -1, -1):
            input_bit = (byte >> i) & 1
            remainder_msb = (remainder >> 14) & 1
            
            remainder = (remainder << 1) & CAN_CRC_MASK
            
            if remainder_msb ^ input_bit:
                remainder ^= CAN_CRC_POLYNOMIAL
                
    return bin(remainder)[2:].zfill(15)