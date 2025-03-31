from ipaddress import IPv4Interface

from Homework.tema3.tema3.devices import Interface
from Homework.tema3.tema3.requirements.base-test import TestInterface

class ConfigureInterface(TestInterface):
    ports: list[Interface] = None
    def __init__(self, executor, builder):
        self.executor = executor
        self.builder = builder
        # self.device, self.ports, self.ips...

    def configure_range(self):
        """Step: Assign IP addresses."""

        pass

    def enable_interfaces(self.ports):
        """Step: Bring up interfaces."""
        pass

    def run(self):
        self.configure_range()






