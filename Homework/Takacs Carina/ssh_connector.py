import paramiko


class SSHConnector:
    def __init__(self, device=None, **kwargs):
        self.device = device
        self.username = None
        self.password = None
        self.client = None

    def connect(self, **kwargs):
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        host = kwargs.get('host')
        port = kwargs.get('port', 22)
        if host is None:
            raise ValueError("A host parameter is required to establish an SSH connection.")

        self.client = paramiko.SSHClient()
        # Automatically add the host key for first-time connection.
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=host,
            port=port,
            username=self.username,
            password=self.password,
            look_for_keys=False,
            allow_agent=False
        )
        return self.client

    def get_device_details(self):
        if self.client is None:
            raise Exception("Not connected to any device. Call connect() first.")
        command = "show version"
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode("utf-8")
        return output

    def do_initial_configuration(self):

        if self.client is None:
            raise Exception("Not connected to any device. Call connect() first.")

        # Set up a series of configuration commands.
        # If the device object is provided, you can customize the configuration using its attributes.
        hostname = self.device.custom.hostname if self.device and hasattr(self.device, 'custom') else "Default-Hostname"
        commands = [
            "configure terminal",
            f"hostname {hostname}",
            "interface GigabitEthernet0/0",
            "ip address 10.0.0.1 255.255.255.0",
            "no shutdown",
            "exit",
            "end",
            "write memory"
        ]
        config_output = ""
        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)
            # Append each command's output; you might want to add logging or more detailed error handling.
            config_output += stdout.read().decode("utf-8")
        return config_output

    def custom_method(self):
        return "Custom SSH method executed!"

    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
