import random
import json
class SwitchIterator():
    def __init__(self, interfaces):
        self.interfaces = interfaces
    def __next__(self):
        if self.interfaces:
            return self.interfaces.pop(0)
        raise StopIteration

class Switch():
    def __init__(self, model, serial):
        self.ports = []
        self.model = model
        self.serial = serial
    def add_switch_port(self, name, vlan, duplex, speed, state):
        self.ports.append(
            {
                'name': name,
                'vlan': vlan,
                'duplex': duplex,
                'speed': speed,
                'state': state,
            }
        )
    def remove_switch_port(self, name):
        idx = 0
        for i, port in enumerate(self.ports):
            if port['name'] == name:
                idx = i
        self.ports.pop(idx)
    def update_switch_port(self,name,vlan=None,duplex=None,speed=None,state=None):
        port = None
        for p in self.ports:
            if p['name'] == name:
                port = p
                break
        if port == None:
            raise Exception('Port does not exist')
        if vlan:
            port['vlan'] = vlan
        if duplex:
            port['duplex'] = duplex
        if speed:
            port['speed'] = speed
        if state:
            port['state'] = state
    def __str__(self):
        return f'{self.serial}:{len(self.ports)}'
    def __repr__(self):
        return f'{self.model}:{self.serial}'
    def __iter__(self):
        return SwitchIterator(self.ports)

possible_models = ['Cisco Nexus 7000 Series','Cisco N9300 Series Smart Switches','Cisco Catalyst 9400 Series Switches',
                   'Cisco Catalyst 9300 Series Switches','Cisco Catalyst 9200 Series Switches']
possible_duplex = ['Full-Duplex','Half-Duplex']
possible_speed = ['1Gbps','5Gbps','1000Mbps', '100Mpbs']
possible_states = ['Up','Administratively Down','Down','Err-Disabled']
def random_switch_gen(amt):
    for _ in range(amt):
        model = random.choice(possible_models)
        serial = random.randint(0,10000)
        ports = random.randint(2,16) * 4
        switch = Switch(model, serial)
        for i in range(ports):
            switch.add_switch_port(f'Fast-Ethernet 0/{i}',random.randint(2,4095),random.choice(possible_duplex),random.choice(possible_speed),random.choice(possible_states))
        yield switch

for switch in random_switch_gen(1):
    # print(json.dumps(switch.__dict__, indent=4))
    if (len(switch.ports) > 28 and
            list(filter(lambda port: port['vlan'] == 200, switch.ports))
            and all(map(lambda port: port['speed'] not in ['1000Mbps', '100Mpbs'], switch.ports))):
        print(switch)

