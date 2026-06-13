import struct

# --- CAN Protocol Constants ---
CAN_A_MAX_ID = 0x7FF
CAN_B_MAX_ID = 0x1FFFFFFF

CAN_CRC_POLYNOMIAL = 0x4599
CAN_CRC_MASK = 0x7FFF

CAN_CRC_DELIMITER = "1"
CAN_PAYLOAD_SIZE_BITS = 64


def encode_can_frame(sensor_id: int, sensor_value: float) -> bytes:
    """
    Generates a complete, standard-compliant CAN Frame binary string.
    Automatically switches between CAN A (Standard) and CAN B (Extended) 
    formats based on the provided sensor_id.
    """
    # 1. Dynamically select and generate the correct header type
    if sensor_id <= CAN_A_MAX_ID:
        header = create_can_a_header(sensor_id)
    elif sensor_id <= CAN_B_MAX_ID:
        header = create_can_b_header(sensor_id)
    else:
        raise ValueError(f"Sensor ID exceeds the maximum 29-bit limit ({hex(CAN_B_MAX_ID)}).")

    # 2. Generate the 64-bit Payload from the sensor float value
    payload = create_payload(sensor_value)

    # 3. Create the unified bit stream for the CRC calculation
    bit_stream_for_crc = header + payload

    # 4. Calculate the mathematical 15-bit CRC remainder
    crc = calculate_can_crc(bit_stream_for_crc)

    # 5. Assemble the final digital frame with the required protocol delimiter
    complete_frame = header + payload + crc + CAN_CRC_DELIMITER
    
    return complete_frame.encode()


def create_can_a_header(sensor_id: int) -> str:
    """
    Generates an 18-bit CAN A (Standard) Header binary string.
    Contains: 11-bit ID, RTR (0), IDE (0), r0 (0), and 4-bit DLC (8).
    """
    # Format ID to exactly 11 bits
    binary_id = bin(sensor_id)[2:].zfill(11)
    
    # Structure fields: Identifier + Control Bits (RTR=0, IDE=0, r0=0) + DLC (8)
    header_parts = [
        binary_id,   
        "000",       
        "1000"       
    ]
    
    return "".join(header_parts)


def create_can_b_header(sensor_id: int) -> str:
    """
    Generates a 39-bit CAN B (Extended) Header binary string.
    Contains: 11-bit Base ID, SRR (1), IDE (1), 18-bit Extension ID, 
    RTR (0), r1 (0), r0 (0), and 4-bit DLC (8).
    """
    # Format ID to exactly 29 bits
    binary_id = bin(sensor_id)[2:].zfill(29)
    
    # Slicing and assembling the extended frame bit architecture (Total: 39 bits)
    header_parts = [
        binary_id[0:11],   # Base ID (11 bits)
        "1",               # SRR bit (1 bit)
        "1",               # IDE bit (1 bit)
        binary_id[11:29],  # Extension ID (18 bits)
        "0",               # RTR bit (1 bit)
        "0",               # r1 - Reserved bit 1 (1 bit)
        "00",              # r0 and additional control padding to align fields (2 bits)
        "1000"             # DLC (4 bits)
    ]
    
    return "".join(header_parts)


def create_payload(value: float) -> str:
    """
    Converts a 32-bit float value into a 64-bit CAN data payload.
    Pads the remaining 4 bytes with zeros to satisfy the DLC=8 requirement.
    """
    # Convert float to 4-byte (32-bit) binary using system native endianness
    raw_bytes = struct.pack('f', value)
    
    # Pad with 4 empty bytes to complete the 8-byte (64-bit) requirement
    empty_padding = b'\x00\x00\x00\x00'
    raw_bytes += empty_padding
    
    # Convert each byte to an 8-bit binary string representation
    payload_bits = [bin(byte)[2:].zfill(8) for byte in raw_bytes]
    
    return "".join(payload_bits)


def calculate_can_crc(bit_stream: str) -> str:
    """
    Calculates the 15-bit CAN CRC remainder for a given binary bit stream.
    Implements polynomial division using the standard CAN-15 polynomial (0x4599).
    """
    remainder = 0x0000
    
    for bit_char in bit_stream:
        input_bit = int(bit_char)
        
        # Isolate the Most Significant Bit (MSB) of the current 15-bit register
        remainder_msb = (remainder >> 14) & 1
        
        # Shift the register left and apply mask to constrain it to 15 bits
        remainder = (remainder << 1) & CAN_CRC_MASK
        
        # Execute conditional feedback division loop
        if remainder_msb ^ input_bit:
            remainder ^= CAN_CRC_POLYNOMIAL
            
    # Return the final calculated remainder padded to 15 bits
    return bin(remainder)[2:].zfill(15)




if __name__ == "__main__":
    print("Running encoder sanity checks with asserts...")

    # --- Test Case 1: CAN A (Standard 11-bit) ---
    test_id_a = 0x123
    test_val_a = 25.5
    frame_a = encode_can_frame(test_id_a, test_val_a)
    
    # Assertions for CAN A: 11 (ID) + 3 (Ctrl) + 4 (DLC) + 64 (Payload) + 15 (CRC) + 1 (Delim) = 98 bits
    assert len(frame_a) == 98, f"Expected CAN A frame length to be 98, got {len(frame_a)}"
    assert frame_a[-1] == CAN_CRC_DELIMITER, "CAN A frame missing CRC Delimiter at the end"
    assert frame_a[11:14] == "000", "CAN A control bits (RTR, IDE, r0) should be '000'"

    # --- Test Case 2: CAN B (Extended 29-bit) ---
    test_id_b = 0x1F2A3B4
    test_val_b = -12.34
    frame_b = encode_can_frame(test_id_b, test_val_b)
    
    # Assertions for CAN B: 11 (Base) + 1 (SRR) + 1 (IDE) + 18 (Ext) + 1 (RTR) + 2 (r) + 4 (DLC) + 64 (Payload) + 15 (CRC) + 1 (Delim) = 119 bits
    assert len(frame_b) == 119, f"Expected CAN B frame length to be 119, got {len(frame_b)}"
    assert frame_b[-1] == CAN_CRC_DELIMITER, "CAN B frame missing CRC Delimiter at the end"
    assert frame_b[11:13] == "11", "CAN B bits SRR and IDE must be '11'"

    print(" All sanity checks passed successfully!")