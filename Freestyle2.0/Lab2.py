def network_add():
    switch_dict={}

    while True:
        switch=input('Enter your switch name or press q to quit: ')
        if switch.lower()=='q':
            break

        if switch in switch_dict:
            print(f'Switch{switch} already exists. Adding ports to it.')
        else:
            switch_dict[switch]={}

        while True:
            port=input("Enter your port name or press q to quit: ")
            if port.lower()=='q':
                break

            if port in switch_dict[switch]:
                print(f'Port {port} already exists. Adding vlans to it.')
            else:
                switch_dict[switch][port]={}

            while True:
                vlans=input("Enter your vlan name or press q to quit: ")
                if vlans.lower()=='q':
                    break

                vlan=set(map(int,vlans.split(",")))
                switch_dict[switch][port]['vlans'].update(vlans)

                print(f"Updated ports for {switch}: {switch_dict[switch]}")

    for switch, ports in switch_dict.items():
        for port, data in ports.items():
            data['vlans'] = sorted(data['vlans'])

    return switch_dict


network_data = network_add()

print('\nNetwork configuration: ')
print(network_data)
