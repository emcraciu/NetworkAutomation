from netmiko import ConnectHandler
from pyats.topology import Device

class SSHConnector:

    def __init__(self, device: Device):
        self.device = device
        self.username = None
        self.password = None
        self.connection = None
        self.ip = None
        self.port = None

    def connect(self, *args, **kwargs):
        c = kwargs['connection']
        self.username = c.credentials.login.username
        self.password = c.credentials.login.password.plaintext
        self.ip = c.ip.compressed
        self.port = c.port

        self.connection = ConnectHandler(
            device_type='cisco_ios',
            ip=self.ip,
            username=self.username,
            password=self.password,
            port=self.port,
        )

    def do_custom_method(self):
        return self.connection.send_command("show ip interface brief")

    def disconnect(self):
        if self.connection:
            self.connection.disconnect()
