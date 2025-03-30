import time
from telnet_context import TelnetContext

HOST = "192.168.11.1"  # Router IP address
PORT = 23  # Telnet port (default is 23)
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

    # Configure interfaces (if your router doesn’t support Ethernet0/4, skip it)
    interfaces = [
        ("Ethernet0/1", "192.168.101.1", "255.255.255.0"),
        ("Ethernet0/2", "192.168.102.1", "255.255.255.0"),
        ("Ethernet0/3", "192.168.103.1", "255.255.255.0"),
        # ("Ethernet0/4", "192.168.104.1", "255.255.255.0"),  # Commented out if not supported
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
    # The "lease" command may not be supported on all devices; remove if causing issues:
    # send_command(telnet, b"lease 7", 0.5)
    send_command(telnet, b"exit", 0.5)

    # Configure a static route (ensure you’re in configuration mode)
    send_command(telnet, b"ip route 192.168.105.0 255.255.255.0 192.168.102.2", 0.5)

    # ----- SSH configuration as the very last step -----
    # Still in global configuration mode
    send_command(telnet, b"ip domain name example.com", 0.5)
    # Generate RSA keys for SSH; if prompted (e.g. for modulus size), you may need to send additional input.
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
