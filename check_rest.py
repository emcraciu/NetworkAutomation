"""
Contains test classes that test the REST connection
"""
from pyats import aetest
from pyats.topology import loader

from connectors_lib.rest_connector import RESTConnector

tb = loader.load('testbeds/config.yaml')

class Example(aetest.Testcase):
    """
    Connects to CSR via REST
    """
    @aetest.test
    def connect_to_devices(self):
        """
        Connects to CSR via REST
        """
        dev = tb.devices['CSR']
        conn = dev.connections.rest
        username = conn.credentials.login.username
        password = conn.credentials.login.password.plaintext
        conn_class: RESTConnector = conn['class'](dev)
        conn_class.connect(connection=conn, username=username, password=password)
        # out = conn_class.get_interface('GigabitEthernet1')
        conn_class.get_restconf_capabilities()
        conn_class.get_restconf_capabilities()
        for api in conn_class.api_endpoints.copy():
            conn_class.get_api_endpoint(api)


if __name__ == '__main__':
    aetest.main()
