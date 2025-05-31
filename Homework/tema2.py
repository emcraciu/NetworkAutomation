import random

class Port:

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)

        assert self.name

        self.vlan = kwargs.get('vlan', [])
        self.duplex = kwargs.get('duplex', None)
        self.speed = kwargs.get('speed', None)
        self.state = kwargs.get('state', None)

    def __str__(self):
        return f'{self.vlan}, {self.duplex}, {self.speed}, {self.state}'

    def __repr__(self):
        return f'{self.name}'

    def set(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        return {
            'name': self.name,
            'vlans': self.vlan,
            'duplex': self.duplex,
            'speed': self.speed,
            'state': self.state
        }

class Switch:

    ports: list[Port] = []

    def __init__(self, serial, model="none"):
        self.serial = serial
        self.model = model

    def get_input(self):

        keys = {'vlan':"", 'duplex':"", 'speed':"", 'state':""}

        for key in keys:
            value = input(f'please input value for {key}: ')
            keys[key] = value

        return keys

    def add_switch_port(self, **info):

        # name = input('please enter port name')

        name = info.get("name")
        if name not in [port.name for port in self.ports]:
            print("----Creating port----")
            port = Port(**info)
            self.ports.append(port)

        else:
            port = next((p for p in self.ports if p.name == name), None)
            port.set(**info)

    def remove_switch_port(self, name):
        for port in self.ports:
            if port.name == name:
                self.ports.remove(port)
                return

        print("did not find element to remove :(")


    def update_switch_port(self, name):
        for port in self.ports:
            if port.name == name:
                info = self.get_input()
                port.set(**info)
        else:
            print("did not find element to update :(")

    def __str__(self):
        return f'{self.serial}: {len(self.ports)}'

    def __repr__(self):
        return f'{self.model}: {self.serial}'

    def __iter__(self):
        for port in self.ports:
            yield port #extra: return port obj
            #yield port.to_dict() - returns dict of port



def generator(nr_switches):
    for _ in range(nr_switches):
        serial = random.choice(['serial1', 'serial2', 'serial3'])
        model = random.choice(['ModelA', 'ModelB', 'ModelC'])
        switch = Switch(serial, model)

        num_ports = random.randrange(8, 65, 4)
        for i in range(num_ports):
            dict1 = {
                "name": f'port{i+1}',
                "vlan": random.choice([10,20,30,40]),
                "duplex": random.choice(['full', 'half']),
                "speed": random.choice([10, 100, 1000,1500,2000]),
                "state": random.choice(['active', 'standby'])
            }

            switch.add_switch_port(**dict1)
        yield switch


for switch in generator(100):
    if len(switch.ports) > 28:
        if 20 in [port.vlan for port in switch.ports]:
            if [port.speed for port in switch.ports if port.speed > 1000]:
                print(switch)




