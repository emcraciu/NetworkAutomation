from multiprocessing.util import log_to_stderr

from pyats import aetest
from pyats.aetest.steps import Steps, Step
from pyats.topology import loader
from genie.libs.conf.ospf.ospf import Ospf
tb = loader.load('OSPF.yaml')
device = tb.devices['CSR']


class Example(aetest.Testcase):
    @aetest.test
    def configure_ospf_scr(self, steps: Steps):
        with steps.start('Connect to device'):
            device.connect(log_stdout=True)

        with steps.start('Configure OSPF'):
            ospf = Ospf()
            ospf.device_attr[device].vrf_attr['default'].instance = '1'
            ospf.device_attr[device].vrf_attr['default'].router_id = '192.168.101.2'
            ospf.device_attr[device].vrf_attr['default'].area_attr[0].area = 0
            # ospf.device_attr[device].vrf_attr['default'].interface_attr['GigabitEthernet1'].area = 0

            config = ospf.build_config(devices=[device], apply=False)
            print(config)

if __name__ == '__main__':
    aetest.main()
