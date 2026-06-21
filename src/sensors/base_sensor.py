from abc import ABC, abstractmethod
from typing import Any, Dict, Callable, Optional


class BaseSensor(ABC):
    """Abstract Base Class (Interface) defining the core architecture for all sensors.
    
    This class enforces a clean I/O interface. Validation logic is injected 
    via a callable (like a lambda) at initialization, keeping the class 
    stateless and focused solely on processing.
    """

    def __init__(self, name: str, sensor_id: int, validator: Optional[Callable[[Any], bool]] = None):
        """
        Args:
            name (str): Name of the sensor.
            sensor_id (int): ID of the sensor.
            validator (Callable): A lambda or function to validate decoded values.
        """
        self.name = name
        self.id = sensor_id
        self.validator = validator

    @abstractmethod
    def read(self, raw_payload: Any) -> Dict[str, Any]:
        """
        Processes raw data, performs decoding, validates using the injected 
        validator, and returns the result.
        """
        pass

    # def write(self, data: Any) -> bool:
    #     """
    #     Optional: Sends data or configuration commands back to the sensor.
    #     """
    #     pass