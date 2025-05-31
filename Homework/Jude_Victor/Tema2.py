import random


class Switch:
    def __init__(self, model, serial):
        self.model = model
        self.serial = serial
        self.ports = {}

    def add_switch_port(self, name, vlan, duplex, speed, state):
        if name in self.ports:
            raise NameError(f"Port {name} already exists")
        self.ports[name] = {
            "vlan": vlan,
            "duplex": duplex,
            "speed": speed,
            "state": state,
        }

    def remove_switch_port(self, name):
        if name not in self.ports:
            raise ValueError("Port not found")
        del self.ports[name]

    def update_switch_port(self, name, **kwargs):
        if name not in self.ports:
            raise ValueError("Port not found")

        for key, value in kwargs.items():
            if key in self.ports[name]:
                self.ports[name][key] = value
            else:
                raise ValueError(f"'{key}' nu este un atribut valid pentru un port!")

    def __repr__(self):
        return f"{self.model}:{self.serial}"

    def __str__(self):
        return f"{self.serial}:{len(self.ports)}"

    def __iter__(self):
        return iter(self.ports.values())


def switch_generator(num_switches):
    models = ["Cisco", "Juniper", "Aruba"]

    for _ in range(num_switches):
        selected_model = random.choice(models)
        serial = f"SN{random.randint(1, 1000)}"
        switch = Switch(selected_model, serial)

        num_ports = random.choice(range(8, 65, 4))

        for port_num in range(1, num_ports + 1):
            port_name = f"Gig1/0/{port_num}"
            vlan = random.randint(1, 4094)
            duplex = random.choice(["full", "half"])
            speed = random.choice([100, 1000, 10000])
            state = random.choice(["up", "down"])
            switch.add_switch_port(port_name, vlan, duplex, speed, state)

        yield switch


matching_switches = []

for switch in switch_generator(100):
    if len(switch.ports) > 28:
        for port in switch:
            if port["vlan"] == 200 and port["speed"] >= 1000:
                matching_switches.append(switch)
                break

print(f"Total switches matching criteria: {len(matching_switches)}")
for sw in matching_switches:
    print(f"Switch: {sw} (Ports: {len(sw.ports)})")
