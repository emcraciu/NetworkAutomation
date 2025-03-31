#context for handling ssh connection
#decorate a genertor function - would that be cool? - maybe with contexts
import telnetlib

def with_ssh(func):
    def wrapper(*args, **kwargs):
        with Telnet_Connection() as telnet:
            return func(ssh, *args, **kwargs)
    return wrapper

#context + connection
class Telnet_Connection:
    def __init__(self, device):
        self.device = device #leave as is rn

    def __enter__(self):
        self.connection = telnetlib.Telnet(self.address, self.port)
        self.connection.write(b"\n")
        out = self.connection.read_very_eager()
        # print(out.decode())
        if b'(config)' in out or b'(config-' in out:
            self.connection.write(b"end\n")
        return self

    def write(self, command: bytes):
        self.connection.write(command + b"\n")

    def expect(self, regex: list[bytes]):
        self.connection.expect([self.hostname + regex[0]])

    def __exit__(self, type, value, traceback):
        self.connection.close()

class Interface:
    pass

class Router:

    def __init__(self, **kwargs):
        self.ipaddress = kwargs.get("ipv4")
        self.ssh_port = kwargs.get("ssh_port")
        self.hostname = kwargs.get("hostname")
        self.password = kwargs.get("password")
