import netmiko
from netmiko import ConnectHandler
from time import sleep
from typing import Optional

from pyats.datastructures import AttrDict
from pyats.topology import Device

class SSHConnector:

    def __init__(self, device: Device, **kwargs):
        self._conn: Optional[netmiko.ConnectHandler] = None
        self.device = device
        # self.connection: Optional[AttrDict] = None

    def connect(self, **kwargs):
        connection_data = {
            'device_type': self.device.type,
            'host': self.device.interface.ipv4.ip.compressed,
            'username': self.device.connections.ssh.credentials.login.username,
            'password': self.device.connections.ssh.credentials.login.password.plaintext,
        }
        self._conn = ConnectHandler(**connection_data)


    # def _initial_conf_iou1(self):
    #     self.execute('conf t', prompt=[r'\(config\)#'])

        # configure interface
        # interface = self.device.interfaces['initial']
        # self.execute(f"interface {interface.name}", prompt=[r'\(config-if\)#'])
        # ip = interface.ipv4.ip.compressed
        # mask = interface.ipv4.network.netmask.exploded
        # self.execute(f"ip address {ip} {mask}", prompt=[r'\(config-if\)#'])
        # self.execute('no shutdown', prompt=[r'\(config-if\)#'])
        # self.execute('exit', prompt=[r'\(config\)#'])


    def execute(self, command, **kwargs):
        if isinstance(command, str):
            command = [command]
        output = self._conn.send_config_set(command)
        return output

    def get_device_details(self, *args, **kwargs):
        pass

    def do_initial_configuration(self):
        pass



if __name__ == "__main__":
    pass