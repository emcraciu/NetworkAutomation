def add_switch():
    network={}

    while True:
        switch_name=input('Please enter your switch name or press q to quit: ')
        if switch_name.lower() == 'q':
            break
        if switch_name in network:
            print(f"Switch '{switch_name}' already exists. Adding ports to it.")
        else:
            network[switch_name]={}

        while True:
            port=input(f'Please enter your port for {switch_name} or press q to quit: ')
            if port.lower()== 'q':
                break
            if port in network[switch_name]:
                print(f"Port '{port}' already exists under switch '{switch_name}'. Adding VLANs to it.")
            else:
                network[switch_name][port]={'vlans': set()}

            while True:
                vlan=input('Please enter your vlan or press q to quit: ')
                if vlan.lower() == 'q':
                    break
                vlans=set(map(int, vlan.split(',')))
                network[switch_name][port]['vlans'].update(vlans)

            print(f'Updated ports for {switch_name}: {network[switch_name]}')

    for switch, ports in network.items():
        for port, data in ports.items():
            data['vlans'] = sorted(data['vlans'])

    return network


network_data = add_switch()

print('\nNetwork configuration: ')
print(network_data)
