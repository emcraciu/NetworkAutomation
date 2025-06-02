

class CreateDictionary:
    def __init__(self):
        self.dict1 = {}

    def get_switch(self):
        switch = input("🙏please enter switch name 🙏: ")
        if switch not in self.dict1:
            self.dict1[switch] = {}
            return switch
        elif switch in self.dict1:
            print("🚫switch already exists🚫")
            self.get_switch()
        else:
            return False

    def get_interface(self, switch):
        interface = input("please enter interface name 😉:")

        if interface not in self.dict1[switch]:
            self.dict1[switch][interface] = []
            return interface
        elif interface in self.dict1[switch]:
            print("🚫interface already exists🚫")
            self.get_interface(switch)
        else:
            return False

    def get_vlans(self, switch, interface):
        vlans = input("please enter vlans 😉:")
        vlans = list(set(vlans.split(',')))
        for vlan in vlans:
            if vlan not in self.dict1[switch][interface]:
                self.dict1[switch][interface].append(vlan)

    def menu(self):
        while True:
            switch = self.get_switch()
            if not switch:
                break
            while True:
                interface = self.get_interface(switch)
                if not interface:
                    break
                while True:
                    self.get_vlans(switch, interface)
                    more_vlans = input("add more VLANs to this interface? (y/q) 😳:")
                    if more_vlans.lower() == 'q':
                        break
                more_interfaces = input("add another interface to this switch? (y/q) 🤩:")
                if more_interfaces.lower() == 'q':
                    break
            more_switches = input("add another switch? (y/q)🫡:")
            if more_switches.lower() == 'q':
                break

        print(self.dict1)

dict = CreateDictionary()
dict.menu()
