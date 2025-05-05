import random

class Switch:

    def __init__(self, model, serial):
        self.model = model
        self.serial = serial
        self.ports = {}
    def add_switch_port(self, name, vlan, duplex,speed,state):
        self.ports[name] = {}
        self.ports[name]['vlan'] = vlan
        self.ports[name]['duplex'] = duplex
        self.ports[name]['speed'] = speed
        self.ports[name]['state'] = state
    def remove_switch_port(self, name):
        del self.ports[name]
    def update_switch_port(self, name, vlan=None, duplex=None,speed=None,state=None):
        if vlan is not None:
            self.ports[name]['vlan'] = vlan
        if duplex is not None:
            self.ports[name]['duplex'] = duplex
        if speed is not None:
            self.ports[name]['speed'] = speed
        if state is not None:
            self.ports[name]['state'] = state

    def __str__(self):
        return f"{self.serial}:{len(self.ports)}"
    def __repr__(self):
        return f"{self.model}:{self.serial}"
    def __iter__(self):
        for port in self.ports:
            yield self.ports[port] #yield-to turn it into a generator


#
# sw1 = Switch("G7",123)
# sw2 = Switch("G8",456)
# sw3 = Switch("G9",789)



#
# sw1.add_switch_port('Fa0/1', [10,20,30],"Half duplex","100Mbps","Up")
# print(sw1.ports)
# sw1.update_switch_port("Fa0/1",[10,20, 99])
# print(sw1.ports)
#
# print(str(sw1))

#
#
# list_of_numbers = [1, 2, 3]
# for port in sw1:
#     print(port)

def random_serial():

    return str(random.randint(1000, 9999))

def generator_switches(count):
    models = ['Cisco', 'Juniper', 'HP', 'Arista', 'Dell']
    duplex_options = ['full', 'half']
    speed_options = [100, 1000, 10000]  # speeds in Mbps
    state_options = ['up', 'down']

    for _ in range(count):
        model = random.choice(models)
        serial = random_serial()
        switch = Switch(model, serial)

        # Random number of ports between 8 and 64 with a step of 4.
        num_ports = random.choice(range(8, 65, 4))

        for port_number in range(1, num_ports + 1):
            port_name = f"Fa0/{port_number}"
            # Assign random values for vlan, duplex, speed, and state.
            vlan = random.randint(1, 4094)
            duplex = random.choice(duplex_options)
            speed = random.choice(speed_options)
            state = random.choice(state_options)
            switch.add_switch_port(port_name, vlan, duplex, speed, state)

        yield switch

switch_generator = generator_switches(100)

for switch in switch_generator:
    if len(switch.ports) > 28:
        for port in switch.ports:
            port = switch.ports[port]
            if (port["vlan"] == 200) and (port["speed"] >= 1000):
                print(f"Switch model: {switch.model}",f"Switch serial: {switch.serial}",sep="\n")

# print(gen_switches)
# print(gen_switches[0].model,gen_switches[0].serial,len(gen_switches[0].ports))
# print(gen_switches[0])
