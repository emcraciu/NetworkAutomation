# tests/configure_interfaces/test_configure_interfaces.py
import argparse
import sys

from pyats import aetest
from genie.testbed import load
from pyats.aetest.main import main

from core.device import NetworkDevice
from core.renderables import InterfaceConfig

parser = argparse.ArgumentParser()
parser.add_argument('--testbed', required=True)
args, remaining = parser.parse_known_args()
sys.argv = [sys.argv[0]] + remaining
testbed = load(args.testbed)

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_testbed(self):

        device = testbed.devices["IOU1"]
        print(device.custom)
        device.connect(via='cli_ssh')

        # Share with other testcases
        self.parent.parameters["testbed"] = testbed
        self.parent.parameters["device"] = device


class TestConfigureInterface(aetest.Testcase):
    @aetest.setup
    def setup(self):
        device = self.parent.parameters['device']
        self.device = NetworkDevice(device)
        self.intf = self.device.device.interfaces["GigabitEthernet2"]

    @aetest.test
    def configure_interface(self):
        intf_cfg = InterfaceConfig(self.intf, shutdown=False)
        commands = intf_cfg.render()
        self.device.device.configure(commands)

    @aetest.test
    def verify_interface_up(self):
        output = self.device.device.parse("show ip interface brief")
        intf_status = output["interface"][self.intf.name]
        assert intf_status["protocol"] == "up", "Interface protocol is not up"
        assert intf_status["ip_address"] != "unassigned", "IP was not set"

class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect(self):
        device = self.parent.parameters["device"]
        device.disconnect()

if __name__ == "__main__":

    sys.exit(main())
