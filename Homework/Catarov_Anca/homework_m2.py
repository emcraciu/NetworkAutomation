from http.server import nobody


class Switch(object):
    def __init__(self, switch_model, switch_serial):
        self.switch_model = switch_model
        self.switch_serial = switch_serial
        self.ports = {}

    def add_switch_port(self, nume, vlan, duplex, viteza, stare):
        self.ports[nume] = {'vlan': vlan, 'duplex': duplex,'viteza': viteza, 'stare': stare}

    def remove_switch_port(self, nume):
        del self.ports[nume]

    def update_switch_port(self, nume, vlan = None, duplex = None, viteza = None, stare = None):
        if vlan != None:
            self.ports[nume]['vlan'] = vlan
        if duplex != None:
            self.ports[nume]['duplex'] = duplex
        if viteza != None:
            self.ports[nume]['viteza'] = viteza
        if stare != None:
            self.ports[nume]['stare'] = stare


    def print_serial_and_port_numbers(self):
        return f'{self.switch_serial}:{len(self.ports)}'

    def print_model_and_serial(self):
        return f'{self.switch_model}:{self.switch_serial}'

    def __iter__(self):
        for port in self.ports:
            yield self.ports[port]




sw1  = Switch('Cisco',12)
sw1.add_switch_port('eth1/1',10,'full',1000,'on')
sw1.add_switch_port('eth1/2',10,'full',1000,'on')
print(sw1.ports)
sw1.remove_switch_port('eth1/1')
print(sw1.ports)
sw1.update_switch_port('eth1/2',23,None,100)
print(sw1.ports)
print(sw1.print_serial_and_port_numbers())
print(sw1.print_model_and_serial())
for port in sw1:
    print(port)


# TODO - punctul 4
# TODO - punctul 5