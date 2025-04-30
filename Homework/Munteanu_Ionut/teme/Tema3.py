import random

class Port_Iter:
    def __init__(self,switch_dict):
        self.switch_dict = switch_dict

    def __next__(self):
        if self.switch_dict == {}:
            raise StopIteration
        key, value = self.switch_dict.popitem()
        return {key: value}

class Switch:
    def __init__(self, model,serial):
        self.model = model
        self.serial = serial
        self.switch_dict={}

    def add_switch_port(self,name,vlan,duplex,speed,state):
        self.name=name
        self.switch_dict[name]={
            "Model":self.model,
            "Serial":self.serial,
            "Vlan":vlan,
            "Duplex":duplex,
            "Speed":speed,
            "State":state}

    def remove_switch_port(self,name):
        if name in self.switch_dict.keys():
            del self.switch_dict[name]

    def update_switch_dict(self,name,vlan,duplex,speed,state):
        if name in self.switch_dict.keys():
            self.switch_dict[name]["Vlan"] = vlan
            self.switch_dict[name]["Duplex"] = duplex
            self.switch_dict[name]["Speed"] = speed
            self.switch_dict[name]["State"] = state
            return True
        return False

    def show_data(self):
        print(self.switch_dict)

    def __iter__(self):
        return Port_Iter(self.switch_dict)

    def __str__(self):
        return f"{self.model}:{len(self.switch_dict)}"

    def __repr__(self):
        return f"{self.model}:{self.serial}"

switch1 = Switch("cisco", "123")
switch1.add_switch_port("GigabitEthernet0/1", "10", "full-duplex", "1000 Mbps", "on")
switch1.add_switch_port("GigabitEthernet0/2", "20", "full-duplex", "100 Mbps", "on")
switch1.add_switch_port("GigabitEthernet0/3", "40", "full-duplex", "500 Mbps", "off")

switch1.remove_switch_port("GigabitEthernet0/2")
switch1.update_switch_dict("GigabitEthernet0/1","15","half-duplex","100 Mbps","off")

print(str(switch1))
print(repr(switch1))

for switch in switch1:
    print(switch)

name=""
duplex=["full-duplex","half-duplex"]
state=["on","off"]
model=["cisco","cisco5678","cisco4564","cisco9999"]
serial=["1234","958485","3249595923","954992"]
list_of_switches=[]

def generate_switch_dict(number):
    for _ in range(number):
        switch2 = Switch(random.choice(model), random.choice(serial))
        ports_number=random.randrange(8,64,4)
        for __ in range(ports_number):
            switch2.add_switch_port("Gigabit0/"+str(__),random.randint(1,300),random.choice(duplex),str(random.randrange(100,10000,100))+" Mbps",random.choice(state))

        list_of_switches.append(switch2)
    for item in list_of_switches:
        for key,value in item.switch_dict.items():
            if int(item.switch_dict[key]["Speed"].split(" ")[0]) > 1000 and len(item.switch_dict)<28 and int(item.switch_dict[key]["Vlan"]) ==200:
                item.show_data()

generate_switch_dict(100)

