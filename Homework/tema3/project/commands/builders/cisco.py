from Homework.tema3.tema3.commands.builders.base import CommandBuilder


class CiscoCommandBuilder(CommandBuilder):

    def interface_mode(self, interface):
        return b'interface ' + interface + b'\n'

    def set_interface_ip(self, ip: ipaddress.IPv4Interface, iface: Interface) -> str:
        return f"ip address {iface.name} ip {ip.ip} {ip.network.netmask}"

    def enable_interface(self) -> str:
        return b'no sh\n'

    def exit_interface(self) -> str:
        return b'exit\n'

    # Optional: include batch method
    def configure_interface(self, interface_name: str, ip: ipaddress.IPv4Interface) -> list[str]:
        """Return a full list of commands to configure and enable an interface."""
        return [
            self.enter_interface(interface_name),
            self.set_interface_ip(ip),
            self.enable_interface(),
            self.exit_interface(),
        ]

