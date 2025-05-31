import unittest
from unittest.mock import MagicMock

from connectors.telnet_connector import TelnetConnector
from scripts.device_config import set_device_hostname, get_device_prompt


class TestDeviceConfig(unittest.TestCase):
    """Unit tests for device configuration helper functions.
        Contributors: Furmanek Carina, Jude Victor
    """

    def setUp(self) -> None:
        """Setup a mock device object before each test."""
        self.mock_device = MagicMock()
        self.mock_device.name = "Router"

    def test_set_hostname_with_mock(self) -> None:
        """Test setting the hostname on a mocked device."""
        target_hostname = "Router1"
        result = set_device_hostname(self.mock_device)
        self.assertTrue(result)
        self.mock_device.configure.assert_called_once_with(f"hostname {target_hostname}")


if __name__ == '__main__':
    # This allows running the tests in this file directly
    unittest.main()
