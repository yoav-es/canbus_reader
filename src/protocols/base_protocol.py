from abc import ABC, abstractmethod


class BaseProtocol(ABC):
    """Abstract Base Class (Interface) defining the contract for all communication protocols.

    Every new protocol (e.g., CAN Bus, Modbus) must inherit from this class
    and implement its mandatory abstract methods.
    """

    def __init__(self, name: str, port: int):
        """Initialize the core attributes of the communication protocol.

        Args:
            name (str): The name of the protocol (e.g., 'CANBus').
            port (int): The network port or channel identifier.
        """
        self.name = name
        self.port = port
        self.parameters = {}  # Dynamic dictionary for additional config settings

    @abstractmethod
    def connect(self) -> None:
        """Open the socket connection or communication channel with the hardware/simulator.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the communication channel and release resources gracefully.

        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def read_raw_frame(self) -> str:
        """Listen to the channel and read a single raw message frame (payload).

        Must be implemented by subclasses.

        Returns:
            str: The raw bitstring or bytes received from the network.
        """
        pass

    def write_raw_frame(self, frame: str) -> None:
        """Transmit a raw message frame back to the network (e.g., for calibration or requests).

        This method is optional. If a specific protocol does not support writing,
        calling this method will raise an error at runtime.

        Args:
            frame (str): The raw frame message to transmit.

        Raises:
            NotImplementedError: If the subclass has not implemented this method.
        """
        raise NotImplementedError(
            f"Protocol '{self.name}' does not support write operations."
        )