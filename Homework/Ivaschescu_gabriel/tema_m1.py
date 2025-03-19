'''# Reading user input for switch config


Create and call python function that will collect vlan information
for each port of a switch and return a dictionary as in the example below:
```python
{
    'SW1': {
        'Ethernet1/1': {'vlans': [100, 200, 300]},
        'Ethernet1/2': {'vlans': [100, 500, 20]},
    },
    'SW2': {
        'Ethernet1/1': {'vlans': [10, 20, 30]},
        'Ethernet1/4': {'vlans': [11, 12, 13]},
    }
}
```
## Steps:
 - ask user for switch name
 - ask user for switch port
 - ask user for vlans corresponding to above port
   - user will provide vlans as "100,200,300"
   - user will be asked to add more vlans or press q
 - if no more vlans are provided user will be asked to provide additional port or press 'q'
 - if no more ports are provided user will be asked ro provide additional switch or press 'q'

## Checks:
 - make sure that vlans do not repeat for port - hint: set()
 - check if user provides same port name a second time
 - check if user provides same switch name a second time  '''


def collect_switch_info():
    sw_config = {}
    while True:
        sw_name = input("Enter switch name (or q to quit) : ").strip()
        if sw_name == 'q':
            break

        if sw_name not in sw_config:
            sw_config[sw_name] = {}

        while True:
            sw_port = input(f"Enter port for {sw_name}(or q to quit) : ").strip()
            if sw_port == 'q':
                break

            if sw_port not in sw_config[sw_name]:
                sw_config[sw_name][sw_port] = {'vlans': []}
                print(f"Port {sw_port} added to switch {sw_name}")
            else:
                print(f"Port {sw_port} already exists in switch {sw_name}, but you can add more vlans or press 'q'")



            while True:
                vlan = input(f"Enter vlans for {sw_port}(or q to quit) : ").strip()
                if vlan == 'q':
                    break

                try:
                    new_vlan = set(map(int, vlan.split(',')))
                    existing_vlans = set(sw_config[sw_name][sw_port]['vlans'])

                    combined_vlans = existing_vlans.union(new_vlan)
                    sw_config[sw_name][sw_port]['vlans'] = sorted(list(combined_vlans))

                except ValueError:
                    print("Invalid format for vlans")

    print("Final config fro switches")
    print(sw_config)


collect_switch_info()






