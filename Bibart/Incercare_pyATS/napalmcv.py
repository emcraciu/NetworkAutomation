from napalm import *
from pyats import aetest
from pyats.topology import loader
from modul6.part1.telnet_connector import TelnetConnector
tb = loader.load('config.yaml')
class Example(aetest.Testcase):
    @aetest.test
    def connect_to_devices(self):
        dev = tb.devices['V15']
        conn: TelnetConnector = dev.connections.telnet['class'](dev)
        conn.connect(connection=dev.connections.telnet)
        conn.do_initial_configuration()

if __name__ == '__main__':
    aetest.main()