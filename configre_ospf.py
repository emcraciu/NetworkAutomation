from pyats import aetest
from pyats.aetest.steps import Steps, Step
from pyats.topology import loader, Device
from genie.libs.conf.ospf.ospf import Ospf
from genie.libs.conf.interface.iosxe import Interface
tb = loader.load('testbeds/OSPF.yaml')

class Example(aetest.Testcase):
    def configure_ospf(self, steps: Steps, device_name: str, device: Device):
        with steps.start('Connect to device'):
            device.connect(log_stdout=True)

        for interface_name, pyats_interface in device.interfaces.items():
            with steps.start(f'Creating Interface Object on {device_name}'):
                interface = Interface(name='GigabitEthernet1')
                interface.device = device
                interface.ipv4 = pyats_interface.ipv4
                config = interface.build_config(apply=False)
                device.configure(config.cli_config.data)

        with steps.start(f'Configuring OSPF on {device_name}'):
            ospf = Ospf()
            ospf.device_attr[device].vrf_attr['default'].instance = '1'
            # ospf.device_attr[device].vrf_attr['default'].router_id = '192.168.101.2'
            area = ospf.device_attr[device].vrf_attr['default'].area_attr[0]
            area.area = 0
            # for interface in ospf.device_attr[device].interfaces:
            #     print(interface)
            # area.areanetwork_keys.append('0.0.0.0 255.255.255.255')
            # area.areanetwork_keys.data.add('0.0.0.0 255.255.255.255')

            config = ospf.build_config(devices=[device], apply=False)
            device.configure(config[device_name].cli_config.data)
            print(config[device_name].cli_config.data)

    @aetest.test
    def configure_ospf_devices(self, steps: Steps):
        for device_name, device in tb.devices.items():
            self.configure_ospf(steps, device_name, device)


if __name__ == '__main__':
    aetest.main()