from pyats import aetest
from pyats.topology import loader

from Homework.TESTBED.ssh_connector import SSHConnector
from telnet_connector import TelnetConnector

tb = loader.load('testbed_example.yaml')


class Example(aetest.Testcase):

    # @aetest.test
    # def connect_to_devices(self):
    #     dev = tb.devices['IOU1']
    #     conn = dev.connections.telnet['class'](dev)  # type: TelnetConnector
    #     conn.connect(connection=dev.connections.telnet)
    #     conn.do_initial_configuration()
    #     conn.disconnect()
    #
    # @aetest.test
    # def connect_to_csr(self):
    #     dev = tb.devices['Router']
    #     conn = dev.connections.telnet['class'](dev) # type: TelnetConnector
    #     conn.connect(connection=dev.connections.telnet)
    #     conn.do_initial_configuration()
    #     conn.disconnect()
    pass

class SSHTest(aetest.Testcase):
    @aetest.test
    def check_ssh_connection(self):
        device = tb.devices['Router']
        conn = device.connections.ssh['class'](device)  # type: SSHConnector
        conn.connect(connection=device.connections.ssh)

        output = conn.do_custom_method()
        print("a")
        print(f"Comanda show ip interface brief =>\n{output}")

        conn.disconnect()


if __name__ == '__main__':
    aetest.main()