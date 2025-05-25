from pyats import aetest
from pyats.topology import loader
tb = loader.load("Bibart/Incercare_pyATS/config.yaml")

class ConfigureFTDTests(aetest.Testcase):
    @aetest.test
    def configure(self):
        try:
            device = tb.devices['FTD']
            conn_class = device.connections.telnet['class']
            telnet_connector = conn_class(device)
            telnet_connector.connect(connection=device.connections.telnet)
            telnet_connector.do_initial_config()
        except KeyError:
            print('Invalid testbed. FTD is missing')

if __name__ == '__main__':
    aetest.main()