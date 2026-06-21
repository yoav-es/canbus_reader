import socket
import logging
from protocols import BaseProtocol
from src.utils import calculate_can_crc

# Constants
DEFAULT_CAN_NAME = "CANbus"
UDP_PORT = 5005
HOST = "127.0.0.1"
CAN_BUFFER = 1024

# Protocol Frame Specs
CAN_A_HEADER_LEN = 18
CAN_B_HEADER_LEN = 39

# Parsing Logic
IDE_BIT_INDEX = 11
IDE_EXTENDED_VALUE = 1

logger = logging.getLogger(__name__)


class Canbus(BaseProtocol):
    """Handles CAN bus communication via UDP socket."""

    def __init__(self, name=DEFAULT_CAN_NAME, port=UDP_PORT, host=HOST):
        super().__init__(name, port)
        self.host = host
        self._socket = None
        self.is_connected = False

    def connect(self) -> None:
        """Initializes and binds the UDP socket."""
        logger.info("Connecting to CAN bus simulator at %s:%d...", self.host, self.port)
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self.host, self.port))
            logger.info("Socket bound to %s:%d.", self.host, self.port)
            self.is_connected = True
        except Exception as e:
            logger.error("Failed to bind UDP socket: %s", e)
            self._socket = None
            raise

    def disconnect(self) -> None:
        """Safely closes the UDP socket."""
        if self._socket:
            logger.info("Closing CAN bus UDP socket.")
            try:
                self._socket.close()
            except Exception as e:
                logger.warning("Error closing socket: %s", e)
            finally:
                self._socket = None
                self.is_connected = False
        else:
            logger.debug("Disconnect called, but no active socket found.")

    def read_raw_frame(self) -> bytes:
        """Reads a single datagram from the socket."""
        if not self._socket:
            logger.error("Attempted to read from an uninitialized socket.")
            raise IOError("Socket not initialized.")

        try:
            data, addr = self._socket.recvfrom(CAN_BUFFER)
            logger.debug("Received %d bytes from %s", len(data), addr)
            return data
        except Exception as e:
            logger.error("Read operation failed: %s", e)
            raise

    def decode_can_payload(self, data: bytes, crc: str):
        """
        Verifies CRC and splits header from payload using protocol constants.
        """
        # 1. Integrity Check
        if crc != calculate_can_crc(data):
            logger.error("CRC mismatch detected.")
            raise ValueError("CRC MISMATCH: CORRUPTED DATA")

        # 2. Identify header length based on IDE bit
        is_extended = data[IDE_BIT_INDEX] == IDE_EXTENDED_VALUE
        header_len = CAN_B_HEADER_LEN if is_extended else CAN_A_HEADER_LEN

        # 3. Defensive Length Check
        if len(data) < header_len:
            logger.error("Invalid frame length: received %d, expected at least %d", 
                         len(data), header_len)
            raise ValueError("FRAME TOO SHORT: INVALID LENGTH")

        # 4. Parsing
        header = data[:header_len]
        payload = data[header_len:]

        return header, payload

    def write_raw_frame(self, frame: str) -> None:
        """Placeholder for sending functionality."""
        pass