import subprocess
import time
import telnetlib
class TelnetContext:
    def __init__(self, address: str, port: int, hostname: bytes):
        self.address = address
        self.port = port
        self.connection = None
        self.hostname = hostname

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

def configure_router() -> None:
    """
    Configures the router using Telnet based on your provided code.
    It logs in, enters configuration mode, sets interface IPs, configures DHCP,
    a static route, and SSH.
    """
    HOST = "192.168.11.1"      # Router IP address
    PORT = 23                  # Telnet port (default is 23)
    HOSTNAME_PROMPT = b"IOU1"  # Router hostname prompt

    def send_command(telnet, command: bytes, delay: float = 1.0):
        """Send a command via Telnet and wait for a short delay."""
        telnet.write(command)
        time.sleep(delay)
        output = telnet.connection.read_very_eager()
        print(output.decode(errors="ignore"))

    with TelnetContext(HOST, PORT, HOSTNAME_PROMPT) as telnet:
        # Go to privileged EXEC mode
        send_command(telnet, b"enable", 1)
        send_command(telnet, b"password", 1)  # Adjust this if needed

        # Enter global configuration mode
        send_command(telnet, b"configure terminal", 1)

        # Configure interfaces (skip Ethernet0/4 if unsupported)
        interfaces = [
            ("Ethernet0/1", "192.168.101.1", "255.255.255.0"),
            ("Ethernet0/2", "192.168.102.1", "255.255.255.0"),
            ("Ethernet0/3", "192.168.103.1", "255.255.255.0"),
            # ("Ethernet0/4", "192.168.104.1", "255.255.255.0"),  # Uncomment if supported
        ]
        for iface, ip, mask in interfaces:
            send_command(telnet, f"interface {iface}".encode(), 0.5)
            send_command(telnet, f"ip address {ip} {mask}".encode(), 0.5)
            send_command(telnet, b"no shutdown", 0.5)
            send_command(telnet, b"exit", 0.5)

        # Re-enter global configuration mode if needed
        send_command(telnet, b"configure terminal", 1)

        # Configure DHCP on Ethernet0/1 (if supported)
        send_command(telnet, b"ip dhcp excluded-address 192.168.101.1 192.168.101.99", 0.5)
        send_command(telnet, b"ip dhcp excluded-address 192.168.101.201 192.168.101.254", 0.5)
        send_command(telnet, b"ip dhcp pool VLAN101", 0.5)
        send_command(telnet, b"network 192.168.101.0 255.255.255.0", 0.5)
        send_command(telnet, b"default-router 192.168.101.1", 0.5)
        send_command(telnet, b"dns-server 192.168.102.2", 0.5)
        send_command(telnet, b"exit", 0.5)

        # Configure a static route
        send_command(telnet, b"ip route 192.168.105.0 255.255.255.0 192.168.102.2", 0.5)

        # ----- SSH configuration as the very last step -----
        send_command(telnet, b"ip domain name example.com", 0.5)
        send_command(telnet, b"crypto key generate rsa modulus 2048", 2)
        send_command(telnet, b"ip ssh version 2", 0.5)
        send_command(telnet, b"username admin privilege 15 secret cisco", 0.5)
        send_command(telnet, b"line vty 0 4", 0.5)
        send_command(telnet, b"transport input ssh", 0.5)
        send_command(telnet, b"login local", 0.5)
        send_command(telnet, b"exit", 0.5)

        # Exit configuration mode and save the configuration
        send_command(telnet, b"end", 0.5)
        send_command(telnet, b"write memory", 1)

def configure_interface(interface: str, ip_with_prefix: str) -> None:
    """
    Configures the given network interface with the specified IP address.

    Parameters:
      interface (str): The network interface to configure (e.g., 'ens4').
      ip_with_prefix (str): The IP address with prefix length (e.g., '192.168.101.100/24').

    This function calls the 'ip' command to add the IP address.
    """
    try:
        # Run the ip command to add the address
        subprocess.run(
            ['ip', 'addr', 'add', ip_with_prefix, 'dev', interface],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Successfully configured {interface} with IP {ip_with_prefix}")
    except subprocess.CalledProcessError as e:
        print(f"Error configuring {interface} with IP {ip_with_prefix}:")
        print(e.stderr)

    try:
        # Turn on the interface (bring it up)
        subprocess.run(
            ['ip', 'link', 'set', interface, 'up'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Successfully turned on the interface {interface}")
    except subprocess.CalledProcessError as e:
        print(f"Error turning on the interface {interface}:")
        print(e.stderr)


def set_route(route: str, interface: str) -> None:
    """
    Sets a static route on the Ubuntu VM using the specified network interface.

    Parameters:
      route (str): The destination network with prefix (e.g., '192.168.96.0/20').
      interface (str): The network interface to use (e.g., 'ens4').

    This function calls the 'ip route add' command to add the route.
    """
    try:
        # Run the ip command to add the route
        subprocess.run(
            ['ip', 'route', 'add', route, 'dev', interface],
            check=True,
            capture_output=True,
            text=True
        )

        print(f"Successfully set route {route} on interface {interface}")
    except subprocess.CalledProcessError as e:
        print(f"Error setting route {route} on interface {interface}:")
        print(e.stderr)


def configure_csr_router(user: str, password: str, hostname: str) -> None:
    """
    Configures the CSR router's initial configuration using a Telnet connection.
    This routine mimics the wizard prompts:
      - It waits for the initial configuration dialog prompt.
      - Answers the wizard prompts with the provided parameters.
    """
    HOST = "192.168.102.2"  # CSR Router IP address
    PORT = 23  # Telnet port for CSR
    HOSTNAME_PROMPT = hostname.encode()  # Expected prompt (e.g., "Router")

    def send_command(telnet, command: bytes, delay: float = 1.0):
        telnet.write(command)
        time.sleep(delay)
        output = telnet.connection.read_very_eager()
        print(output.decode(errors="ignore"))

    with TelnetContext(HOST, PORT, HOSTNAME_PROMPT) as telnet:
        # Kick off the session by sending a newline.
        telnet.write(b"\n")
        time.sleep(1)
        output = telnet.connection.read_very_eager()
        print("Initial output from CSR router:")
        print(output.decode(errors="ignore"))

        # Check if we see the initial configuration dialog.
        if b"initial configuration dialog? [yes/no]" in output:
            # Respond to the wizard prompts.
            send_command(telnet, b"yes", 2)  # Accept initial configuration dialog
            send_command(telnet, b"yes", 2)  # management setup? [yes/no]
            send_command(telnet, hostname.encode(), 1)  # host name prompt: send hostname
            send_command(telnet, password.encode(), 1)  # Enter enable secret:
            send_command(telnet, password.encode(), 1)  # Enter enable password:
            send_command(telnet, password.encode(), 1)  # Enter virtual terminal password:
            send_command(telnet, b"no", 1)  # SNMP Network Management? [yes]:
            send_command(telnet, b"GigabitEthernet1", 1)  # interface summary:
            send_command(telnet, b"yes", 1)  # IP on this interface? [yes]:
            send_command(telnet, b"192.168.102.2", 1)  # IP address for this interface:
            send_command(telnet, b"255.255.255.0", 1)  # mask for this interface [255.255.255.0] :
            send_command(telnet, b"2", 1)  # Enter your selection [2]:

            # Optionally, poll until configuration finishes.
            for _ in range(10):
                time.sleep(60)
                telnet.write(b"\n")
                poll_output = telnet.connection.read_very_eager()
                print(poll_output.decode(errors="ignore"))
                if hostname.encode() in poll_output:
                    break
        elif b"Router>" in output or b"Router#" in output:
            print("CSR Router is already configured")
        elif b"User Access Verification" in output:
            print("CSR Router is asking for a password, maybe it's already configured")
        elif b'Password required, but none set' in output:
            print("CSR Router needs a password to initiate a telnet connection, configure it manually, then re execute the script")
def ping_device(ip_address: str, count: int = 4) -> None:
    """
    Sends a ping command to the specified IP address.

    Parameters:
      ip_address (str): The target IP address to ping.
      count (int): Number of ping packets to send (default is 4).

    This function uses the 'ping' command to send ICMP echo requests.
    """
    import subprocess

    try:
        # Execute the ping command with the specified count.
        result = subprocess.run(
            ['ping', '-c', str(count), ip_address],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Ping result for {ip_address}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error pinging {ip_address}:\n{e.stderr}")



def main():
    configure_csr_router('Admin', 'admin', 'Router')

if __name__ == '__main__':
    main()
