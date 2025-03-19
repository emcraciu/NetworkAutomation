
#file for switches and ports


from device import Device

class Port:
    def __init__(self, name, vlan, duplex, speed, state):
        self.name = name
        self.vlan = vlan
        self.duplex = duplex
        self.speed = speed
        self.state = state

    def __str__(self):
        return f"Port: {self.name}, Vlan: {self.vlan}, Duplex: {self.duplex}, Speed: {self.speed} Mbs, State: {self.state}"

    def __repr__(self):
        return f"{Port(name=self.name, vlan=self.vlan, duplex=self.duplex, speed=self.speed, state=self.state)}"



class Switch(Device):
    def __init__(self, model, serial):
        super().__init__(serial)
        self.model = model
        self.ports = {}

    def add_switch_port(self, name, vlan, duplex, speed, state):
        self.ports[name] = Port(name, vlan, duplex, speed, state)

    def remove_switch_port(self, name):
        if name in self.ports:
            del self.ports[name]

    def update_switch_port(self, name, vlan = None, duplex = None, speed = None, state = None):
        if name in self.ports:
            port = self.ports[name]
            if vlan is not None:
                port.vlan = vlan
            if duplex is not None:
                port.duplex = duplex
            if speed is not None:
                port.speed = speed
            if state is not None:
                port.state = state

    def __str__(self):
        return f"{self.name} : {len(self.ports)}"

    def __repr__(self):
        return f"Switch: (model={self.model!r}, serial={self.name!r}, ports={len(self.ports)})"

    def __iter__(self):
        for port in self.ports.values():
            yield port

