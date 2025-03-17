import random
import string

class Switch:
    def __init__(self, model, serial):
        self.model = model
        self.serial = serial
        self.ports = {}  #
        self._iter_index = 0

    def add_switch_port(self, name, vlan, duplex, speed, state):
        if name in self.ports:
            print(f"Port '{name}' already exists.")
            return
        self.ports[name] = {
            "name": name,
            "vlan": vlan,
            "duplex": duplex,
            "speed": speed,
            "state": state
        }
        print(f"Added port {name}")

    def remove_switch_port(self, name):
        if name in self.ports:
            del self.ports[name]
            print(f"Removed port {name}")
        else:
            print(f"Port '{name}' not found.")

    def update_switch_port(self, name, **kwargs):
        if name not in self.ports:
            print(f"Port '{name}' does not exist.")
            return
        for key, value in kwargs.items():
            if key in self.ports[name]:
                self.ports[name][key] = value
            else:
                print(f"'{key}' is not a valid attribute for port '{name}'.")

    def __str__(self):
        return f"{self.serial}:{len(self.ports)}"

    def __repr__(self):
        return f"{self.model}:{self.serial}"

    def __iter__(self):
        self._port_list = list(self.ports.values())
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < len(self._port_list):
            port_info = self._port_list[self._iter_index]
            self._iter_index += 1
            return port_info
        else:
            raise StopIteration



switch1=Switch("Cisco 2960", "ABCDE")
switch1.add_switch_port("Gigabit Ethernet 1/0/1", 10, "full", "100", "up")
switch1.add_switch_port("Gigabit Ethernet 1/0/2", 20, "half", "500", "down")
switch1.add_switch_port("Gigabit Ethernet 1/0/3", 30, "half", "1000", "down")
switch1.update_switch_port("Gigabit Ethernet 1/0/2", speed="1000" ,state="up")
switch1.remove_switch_port("Gigabit Ethernet 1/0/1")
print(switch1.ports)

print(str(switch1))
print(repr(switch1))

for port in switch1:
    print(port)

