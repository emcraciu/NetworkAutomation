"""
Manages a Telnet connection
"""
import logging
# pylint: disable=deprecated-module
import re
import telnetlib
from typing import Optional

from pyats.datastructures import AttrDict
from pyats.topology import Device

logger = logging.getLogger(__name__)


class TelnetConnector:
    """
    Manages a Telnet connection to a device.
    Handles basic read/write operations.
    """

    def __init__(self, device: Device):
        self.device = device
        self._conn: Optional[telnetlib.Telnet] = None
        self.connection_details: Optional[AttrDict] = None  # Renamed for clarity

    def connect(self, **kwargs):
        """
        Connects to the device using Telnet.
        Expects 'connection' in kwargs containing connection parameters.
        """
        self.connection_details = kwargs['connection']
        if not self.connection_details or not hasattr(self.connection_details, 'ip'):
            raise ValueError("Connection details with IP address are required.")

        logger.info(
            f"Attempting Telnet connection to {self.connection_details.ip.compressed}:{self.connection_details.port}")
        self._conn = telnetlib.Telnet(
            host=self.connection_details.ip.compressed,
            port=self.connection_details.port,
            timeout=kwargs.get('timeout', 10)  # Added default timeout
        )
        logger.info(f"Successfully connected to {self.device.name} via Telnet.")

    def read(self, encoding: str = 'utf-8', errors: str = 'ignore') -> str:
        """
        Reads any immediate output from the device.
        """
        if not self._conn:
            raise ConnectionError("Telnet connection is not established.")
        return self._conn.read_very_eager().decode(encoding, errors=errors)

    def write(self, command: str, add_newline: bool = True, encoding: str = 'utf-8') -> None:
        """
        Sends a command to the device.
        Appends a newline character by default.
        """
        if not self._conn:
            raise ConnectionError("Telnet connection is not established.")
        logger.debug(f"Writing to {self.device.name}: {command.strip()}")
        payload = command.encode(encoding)
        if add_newline:
            payload += b'\n'
        self._conn.write(payload)

    def write_raw(self, command: str, encoding: str = 'utf-8') -> str:
        """
        Writes a command without newline and returns immediate output.
        """
        if not self._conn:
            raise ConnectionError("Telnet connection is not established.")
        logger.debug(f"Writing raw to {self.device.name}: {command.strip()}")
        self._conn.write(command.encode(encoding))
        return self.read(encoding)

    def expect(self, patterns: list[str], timeout: Optional[float] = None, encoding: str = 'utf-8',
               errors: str = 'ignore') -> tuple[int, Optional[re.Match], str]:
        """
        Reads until one of a list of regular expressions is found or timeout.
        Returns a tuple: (index of pattern, match object, text read).
        """
        if not self._conn:
            raise ConnectionError("Telnet connection is not established.")

        encoded_patterns = [p.encode(encoding) for p in patterns]
        try:
            index, match_obj, text_bytes = self._conn.expect(encoded_patterns, timeout=timeout)
            text_read = text_bytes.decode(encoding, errors=errors)
            if index == -1:  # No match
                logger.warning(
                    f"Expected patterns {patterns} not found in output on {self.device.name}. Output: {text_read[:200]}...")  # Log snippet
            return index, match_obj, text_read
        except EOFError:
            logger.error(f"EOFError while expecting patterns on {self.device.name}. Connection may have closed.")
            raise ConnectionAbortedError(f"Connection closed by remote host {self.device.name}")

    def is_connected(self) -> bool:
        """
        Returns the current status of the Telnet connection.
        Checks if the socket is still open by trying a NOP.
        """
        if not self._conn:
            return False
        try:
            self._conn.sock.sendall(telnetlib.IAC + telnetlib.NOP)
            return True
        except (OSError, EOFError, AttributeError):  # AttributeError if _conn.sock is None
            return False

    def disconnect(self):
        """
        Closes the Telnet connection.
        """
        if self._conn:
            logger.info(f"Disconnecting Telnet from {self.device.name}")
            self._conn.close()
            self._conn = None
        self.connection_details = None