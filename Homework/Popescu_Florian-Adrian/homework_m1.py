import json

def collect_vlan_info():
    vlan_data = {} #initializam dictionarul gol

    while True:
        switch_name = input("Please enter the switch name (or q to quit): ").strip()
        if switch_name.lower() == "q":
            break

        if switch_name not in vlan_data:
            vlan_data[switch_name] = {}
        elif switch_name is vlan_data[switch_name]:
            print("Switch name already exists")

        while True:
            port_name = input(f"Please enter the port for {switch_name} (or q to quit): ").strip()
            if port_name.lower() == "q":
                break

            if port_name in vlan_data[switch_name]:
                print("Port already exists")

            while True:
                vlan_input = input(f"Please enter the vlan for {port_name} (comma-separeted or q to quit): ").strip()
                if vlan_input.strip() == "q":
                    break

                try:
                    vlan_list = list(sorted(set(map(int, vlan_input.split(',')))))
                    vlan_data[switch_name][port_name] = {'vlans': vlan_list}
                    break
                except:
                    print("Invalid input, please enter VLANs as comma-separated NUMBERS")

    return vlan_data

vlan_info = collect_vlan_info()
print("Vlan info: \n")
#functie pentru a afisa mai frumos output-ul
print(json.dumps(vlan_info, indent=4))