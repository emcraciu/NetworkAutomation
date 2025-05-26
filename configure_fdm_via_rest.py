"""Added docstrings for module"""

import ssl
import time

from pyats import aetest
from pyats.aetest.steps import Steps
from pyats.topology import loader

ssl._create_default_https_context = ssl._create_unverified_context
from connectors_lib.swagger_connector import SwaggerConnector

tb = loader.load('testbeds/config.yaml')
device = tb.devices['FTD']


class Example3(aetest.Testcase):
    @aetest.test
    def configure_fdm_interface(self, steps: Steps):
        with steps.start('Connecting to FDM'):
            swagger: SwaggerConnector = device.connections.rest['class'](device)
            swagger.connect(connection=device.connections.rest)

        with steps.start('Changing DHCP server'):
            dhcp_servers = swagger.client.DHCPServerContainer.getDHCPServerContainerList().result()
            for dhcp_server in dhcp_servers['items']:
                dhcp_server.servers = []
                result = swagger.client.DHCPServerContainer.editDHCPServerContainer(
                    objId=dhcp_server.id,
                    body=dhcp_server
                ).result()
                print(result)

        # with steps.start('Creating Security Zone'):
        #     ref = swagger.client.get_model('ReferenceModel')
        #     phy = swagger.client.Interface.getPhysicalInterfaceList().result()['items'][2]
        #     security_zone = swagger.client.get_model('SecurityZone')
        #     sz = security_zone(
        #         name='AutoCreated1',
        #         mode='ROUTED',
        #         interfaces=[ref(id=phy.id, name=phy.name, hardwareName=phy.hardwareName, type=phy.type)]
        #     )
        #     result = swagger.client.SecurityZone.addSecurityZone(body=sz).result()
        #     print(result)

        with steps.start("Configuring Interface"):
            existing_object = swagger.client.Interface.getPhysicalInterfaceList().result()['items']
            for obj in existing_object:
                if obj.hardwareName == 'GigabitEthernet0/0':
                    obj.ipv4.ipAddress.ipAddress = device.interfaces['GigabitEthernet0/0'].ipv4.ip.compressed
                    obj.ipv4.ipAddress.netmask = device.interfaces['GigabitEthernet0/0'].ipv4.netmask.compressed
                    obj.enabled = True
                    obj.ipv4.dhcp = False
                    obj.ipv4.ipType = 'STATIC'
                elif obj.hardwareName == 'GigabitEthernet0/1':
                    obj.ipv4.ipAddress.ipAddress = device.interfaces['GigabitEthernet0/1'].ipv4.ip.compressed
                    obj.ipv4.ipAddress.netmask = device.interfaces['GigabitEthernet0/1'].ipv4.netmask.compressed
                    obj.enabled = True
                    obj.ipv4.dhcp = False
                    obj.ipv4.ipType = 'STATIC'
                else:
                    continue
                result = swagger.client.Interface.editPhysicalInterface(objId=obj.id, body=obj).result()
                print(result)

        with steps.start('Creating Access Rule'):
            out = swagger.client.AccessPolicy.getAccessPolicyList()
            model = swagger.client.get_model('AccessRule')
            res = swagger.client.AccessPolicy.addAccessRule(
                parentId=out.result().items[0].id,
                body= model(
                    name='AccessRule10',
                    ruleAction='PERMIT',
                )
            )
            print(res.result())

        with steps.start('Create network object'):
            network_object = swagger.client.get_model('NetworkObject')

        with steps.start('Deploying configuration'):
            response = swagger.client.Deployment.addDeployment().result()
            for _ in range(10):
                time.sleep(3)
                tasks = swagger.client.Deployment.getDeployment(objId=response.id).result()
                if len(tasks['deploymentStatusMessages']) == 0:
                    continue
                status = tasks['deploymentStatusMessages'][-1]
                if status['taskState'] == "FINISHED":
                    break
            else:
                print("Deployment failed or is taking too much time.")


if __name__ == '__main__':
    aetest.main()
