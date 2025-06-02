from pyats import aetest
from pyats.topology import loader

from lib.telnet_connector import TelnetConnector


class TestClass(aetest.Testcase):

     ## for 1 device with telnet_connector
    @aetest.test
    def connect_to_devices(self):
        tb = loader.load('testbed_example.yaml')
        dev = tb.devices['FTD']  # Ensure that ' {name} ' exists in your YAML file
        # conn = dev.connections.telnet['class'](dev)  # Get the telnet connection object from the testbed
        telnet_connector = TelnetConnector(dev)  # Initialize your TelnetConnector2
        # telnet_connector.connect(connection=conn)  # Use the connection object
        telnet_connector.do_initial_configuration()  # Execute initial configuration commands
        telnet_connector.disconnect()  # Disconnect from the device