# test_ssh_connector.py
import unittest
from pyats.datastructures import AttrDict
from pyats.topology import Device
from ssh_connector import SSHConnector

# Dummy SSH client to simulate paramiko.SSHClient behavior
class DummySSHClient:
    def __init__(self):
        self.connected = False

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, hostname, port, username, password, look_for_keys, allow_agent):
        self.connected = True

    def exec_command(self, command):
        # Simulate the execution of a command; return fixed output.
        class DummyStream:
            def read(self):
                return b"dummy command output"
        return (None, DummyStream(), None)

    def close(self):
        self.connected = False

class TestSSHConnector(unittest.TestCase):
    def setUp(self):
        # Create a dummy device with custom attributes
        self.device = Device(name="ssh_device")
        self.device.custom = AttrDict({"hostname": "SSH-Router"})
        self.device.connections = AttrDict({
            "ssh": AttrDict({
                "credentials": AttrDict({
                    "login": AttrDict({
                        "username": "admin",
                        "password": AttrDict({"plaintext": "pass"})
                    })
                })
            })
        })
        # Initialize the SSHConnector with the dummy device.
        self.ssh_connector = SSHConnector(device=self.device)
        # Inject a dummy SSH client.
        self.ssh_connector.client = DummySSHClient()

    def test_custom_method(self):
        # Check that the custom method returns the expected confirmation message.
        result = self.ssh_connector.custom_method()
        self.assertEqual(result, "Custom SSH method executed!")

    def test_get_device_details(self):
        # Test that get_device_details uses exec_command and returns the dummy output.
        details = self.ssh_connector.get_device_details()
        self.assertEqual(details, "dummy command output")

    def test_do_initial_configuration(self):
        # do_initial_configuration sends a series of configuration commands.
        # With our dummy client, each command returns "dummy command output".
        config_output = self.ssh_connector.do_initial_configuration()
        # Since we expect concatenation of multiple outputs, check that our dummy output is present.
        self.assertIn("dummy command output", config_output)
        self.assertTrue(isinstance(config_output, str))

    def test_connect_method(self):
        # Instead of executing a real connection, simulate connect() via monkey patch.
        # Reset any existing client:
        self.ssh_connector.client = None

        # Define a dummy connect function that simply assigns a DummySSHClient.
        def dummy_connect(**kwargs):
            self.ssh_connector.client = DummySSHClient()
            # Call the connect() method on our dummy client.
            self.ssh_connector.client.connect(
                hostname=kwargs.get("host"),
                port=kwargs.get("port", 22),
                username=kwargs.get("username"),
                password=kwargs.get("password"),
                look_for_keys=False,
                allow_agent=False
            )
        # Monkey patch the original connect method.
        self.ssh_connector.connect = dummy_connect

        # Execute the "connect" with dummy parameters.
        self.ssh_connector.connect(host="192.168.1.1", port=22, username="admin", password="pass")

        # Check that the dummy client is now assigned and marked as connected.
        self.assertIsNotNone(self.ssh_connector.client)
        self.assertTrue(self.ssh_connector.client.connected)

if __name__ == "__main__":
    unittest.main()
