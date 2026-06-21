import logging
from sensors import BaseSensor
from typing import Any, Dict, Callable, Optional
from protocols import canbus_protocol

class CanBusSensor(BaseSensor):

    def __init__(self, name: str, sensor_id: int, crc: int, protocol, validator: Optional[Callable[[Any], bool]] = None):
        super().__init__(name, sensor_id, validator)
        self.validator = validator
        self.crc = crc
        self.protocol = protocol 
    
def read(self, raw_payload: Any) -> str:
        decoded_value = decode_payload(raw_payload) 
        value = decoded_value if self.validator(value) is true else "error"
        timestamp = time.time()
        return f"{timestamp}-{self.sensor_id}-{decoded_value}-unit_placeholder"

    # def write(self, data: Any) -> bool:
    #     """
    #     Optional: Sends data or configuration commands back to the sensor.
    #     """
    #     pass