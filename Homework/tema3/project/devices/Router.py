
class Router:

    def __init__(self, **kwargs):
        self.ipaddress = kwargs.get("ipv4")
        self.ssh_port = kwargs.get("ssh_port")
        self.hostname = kwargs.get("hostname")
        self.password = kwargs.get("password")
