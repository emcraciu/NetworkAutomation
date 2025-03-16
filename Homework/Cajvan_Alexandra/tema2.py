import random


class Port:
    """Represents a single switch port"""

    def __init__(self, port):
        self.name = port["name"]
        self.vlan = port["vlan"]
        self.duplex = port["duplex"]
        self.speed = port["speed"]
        self.state = port["state"]

        # Store any extra attributes
        self.extra_attributes = {k: v for k, v in port.items() if k not in {"name", "vlan", "duplex", "speed", "state"}}

    def __str__(self):
        """Returns a converted string"""
        return f'name {self.name}, vlan {self.vlan}, state {self.state}'


class Switch:
    """Represents a network switch"""

    def __init__(self, model, serial):
        self.model = model
        self.serial = serial
        self.ports = []

    def add_switch_port(self, name, vlan, duplex, speed, state, **kwargs):
        """
        Adds a port and stores the data inside object's ports list (self.ports).
        Minimum data: name, vlan, duplex, speed, state. Accepts more data using kwargs
        """
        new_port = {'name': name, 'vlan': vlan, 'duplex': duplex, 'speed': speed, 'state': state}

        for key, value in kwargs.items():
            new_port[key] = value

        self.ports.append(new_port)

    def remove_switch_port(self, name):
        """Removes port based on port name"""
        for port in self.ports:
            if port['name'] == name:
                self.ports.remove(port)

    def update_switch_port(self, name, **kwargs):
        """Updates port data based on port name"""
        for port in self.ports:
            if port['name'] == name:
                for key, value in kwargs.items():
                    port[key] = value

    def __str__(self):
        """Returns a converted string"""
        return f"{self.serial}:{len(self.ports)}"

    def __repr__(self):
        """Returns representation inside another object"""
        return f"{self.model}:{self.serial}"

    def __iter__(self):
        """Makes the switch iterable by returning an iterator over its ports"""
        # return iter(self.ports)  # Converts the list into an iterator, just self.ports is iterable but not an iterator.
        return (Port(port_dict) for port_dict in self.ports)


def generate_serial():
    """Generates a random serial number with 6 uppercase letters and 3 digits"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"

    serial = ""

    for count in range(6):
        random_index = random.choice(range(0, len(alphabet)-1))  # Pick a random index
        serial += alphabet[random_index]  # Get the letter

    for count in range(3):
        random_index = random.choice(range(0, len(digits)-1))  # Pick a random index
        serial += digits[random_index]  # Get the digit

    return serial


def generator_switches(x):
    """Generator that produces X switch objects with random data"""
    switches = []
    for count in range(x):
        random_model = "Cisco Catalyst " + random.choice(['9200', '9300', '9500', '2960X'])
        random_serial = generate_serial()
        switch = Switch(model=random_model, serial=random_serial)

        # Random number of ports (between 8-64, step of 4)
        ports_count = random.choice(range(8, 65, 4))

        for i in range(ports_count):
            switch.add_switch_port(
                name=f"Eth0/{i}",
                vlan=random.randint(1, 4094),
                duplex=random.choice(['full', 'half']),
                speed=random.choice([10, 100, 1000, 10000]),
                state=random.choice(['up', 'down'])
            )

        switches.append(switch)

    return switches

all_switches = generator_switches(100)
for switch in all_switches:
    if len(switch.ports) < 29:
        continue
    has_port_200 = False
    is_fast = False
    for port in switch:
        if port.vlan == 200:
            has_port_200 = True
        if port.speed >= 1000:
            is_fast = True
    if not has_port_200 and not is_fast:
        continue
    print(switch)

    #and thats that
