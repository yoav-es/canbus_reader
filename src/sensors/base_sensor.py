from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseSensor(ABC):
    """Abstract Base Class (Interface) defining the core architecture for all sensors.

    Handles basic sensor metadata, the processed data store, and enforces
    the decoupling of decoding and validation logic for distributed services.
    """

    def __init__(self, name: str, sensor_id: int):
        """Initialize core sensor attributes.

        Args:
            name (str): Name of the sensor (e.g., 'engine_rpm').
            sensor_id (int): Hexadecimal or integer ID of the sensor.
        """
        self.name = name
        self.id = sensor_id
        self.data: Dict[str, Any] = {}  # Stores the latest processed/decoded values

    def get_data(self) -> Dict[str, Any]:
        """Retrieve the latest processed data from the sensor.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed sensor fields.
        """
        return self.data

    @abstractmethod
    def decode(self, raw_frame: str) -> Dict[str, Any]:
        """Decode raw protocol data into meaningful physical values.

        Must be implemented by subclasses to handle specific bit-masking or slicing.

        Args:
            raw_frame (str): The raw frame/payload received from the protocol layer.

        Returns:
            Dict[str, Any]: The newly decoded telemetry data.
        """
        pass

    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Validate if a decoded value matches its configuration-driven rules.

        Must be implemented by subclasses to handle type-specific validation
        (e.g., range checks for float, allowed states for int, or flag checks for bool).

        Args:
            value (Any): The decoded physical value to check.

        Returns:
            bool: True if valid according to the configuration, False if not.
        """
        pass

    def set_parameters(self, **kwargs) -> None:
        """Optional method to update internal sensor configurations or thresholds.

        Args:
            **kwargs: Arbitrary keyword arguments representing configuration parameters.
        """
        pass