#file that contains the main logic of the project


import random
from switch import Switch

def generate_switches(meaw):
    models = ["Catalyst 9300", "Ubiquiti UniFi", "Switchul meu de acasa","Alt ceva 1900 toamna"]
    states = ["up", "down"]
    duplexes = ["full", "half"]

    for _ in range(meaw):
        model = random.choice(models)
        serial = f"SN{random.randint(100000,999999)}"
        switch = Switch(model, serial)

        number_of_ports = random.choice(range(8, 64, 4))

        for _ in range(number_of_ports):
            name = f"G0/{_}"
            vlan = random.randint(1,4094)
            duplex = random.choice(duplexes)
            speed = random.choice([100, 1000, 10000])
            state = random.choice(states)
            switch.add_switch_port(name, vlan, duplex, speed, state)

        yield switch


def main():
    switches = generate_switches(1000)
    filtered_switches = []
    for switch in switches:
        if len(switch.ports) > 8:
            for port in switch:
                if port.vlan == 200 and port.speed >= 1000:
                    filtered_switches.append(switch)
                    break

    print(f"Filtered Switches {len(filtered_switches)}:")
    for switch in filtered_switches:
        print(switch)
        print(repr(switch))


if __name__ == "__main__":
    main()

