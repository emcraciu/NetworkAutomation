from pyats import aetest
from pyats.topology import loader

from config.config_ospf import OSPFInterfaceExtractor
from connectors.telnet_connector import TelnetConnector

tb = loader.load('testbed_config.yaml')


# class Example(aetest.Testcase):
#
#     @aetest.test
#     def connect_to_devices(self):
#         for device in tb.devices.values():
#             if device.type == 'router':
#                 conn_class = device.connections.telnet['class']
#                 if isinstance(conn_class, str):
#                     module_path, class_name = conn_class.rsplit('.', 1)
#                     module = __import__(module_path, fromlist=[class_name])
#                     conn_class = getattr(module, class_name)
#
#                 conn = conn_class(device)  # type: TelnetConnector
#                 conn.connect(connection=device.connections.telnet)
#                 conn.do_initial_configuration()
#                 conn.disconnect()

class OspfConfig(OSPFInterfaceExtractor):
    pass


if __name__ == '__main__':
    aetest.main()