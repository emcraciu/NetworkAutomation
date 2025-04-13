from pyats import aetest
from pyats.topology import loader

from ssh_connector import SSHConnector
from telnet_connector import TelnetConnector

tb = loader.load('testbed_homework_m5.yaml')


class Example(aetest.Testcase):

    @aetest.test
    def connect_to_devices(self):
        dev = tb.devices['IOU1']
        conn = dev.connections.telnet['class'](dev)  # type: TelnetConnector
        conn.connect(connection=dev.connections.telnet)
        conn.do_initial_configuration()
        conn.disconnect()

    @aetest.test
    def connect_to_devices_ssh(self):
        dev = tb.devices['IOU1']
        conn = dev.connections.ssh['class']()  # type: SSHConnector
        creds = dev.connections.ssh.credentials['login']  # {'username': ..., 'password': ...}

        # Aici "spargem" dicționarul direct în keyword arguments
        conn.connect(**creds)
        conn.do_initial_configuration()

    @aetest.test
    def connect_to_devices_CSR_ssh(self):
        dev = tb.devices['Router']
        conn = dev.connections.ssh['class']()  # type: SSHConnector
        creds = dev.connections.ssh.credentials['login']  # {'username': ..., 'password': ...}

        # Aici "spargem" dicționarul direct în keyword arguments
        conn.connect(**creds)
        conn.do_initial_configuration()

    @aetest.test
    def connect_to_devices_CSR(self):
        dev = tb.devices['Router']
        conn = dev.connections.telnet['class'](dev)  # type: TelnetConnector
        conn.connect(connection=dev.connections.telnet)
        conn.do_initial_configuration()
        conn.disconnect()

if __name__ == '__main__':
    aetest.main()
