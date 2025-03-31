from abc import ABC, abstractmethod
import ipaddress

class CommandBuilder(ABC):
    @abstractmethod
    def enter_interface(self, interface_name: str) -> str:
        """Return the command to enter configuration mode for a specific interface."""
        pass

    @abstractmethod
    def set_interface_ip(self, ip: ipaddress.IPv4Interface) -> str:
        """Return the command to set an IP address on the interface."""
        pass

    @abstractmethod
    def enable_interface(self) -> str:
        """Return the command to enable (bring up) the interface."""
        pass

    @abstractmethod
    def exit_interface(self) -> str:
        """Return the command to exit interface configuration mode."""
        pass

