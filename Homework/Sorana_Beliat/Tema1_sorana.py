def functie_switch():
    vlan_data = {}
    while True:
        print('Give switch name or press q to exit: ')
        switch_name = input().strip()
        if switch_name == 'q':
            break
        if switch_name not in vlan_data:
            vlan_data[switch_name] = {}
        while True:
            print(f'Give switch port or press q to exit: ')
            switch_port = input().strip()
            if switch_port == 'q':
                break
            if switch_port not in vlan_data[switch_name]:
                vlan_data[switch_name][switch_port] = {'vlans':set()}
            while True:
                print(f'Give VLANs for port {switch_port} or press q to exit:')
                vlan_input = input().strip()
                if vlan_input == 'q':
                    break

                vlan_list = vlan_input.split(',')
                for vlan in vlan_list:
                    vlan=vlan.strip()
                    vlan_data[switch_name][switch_port]['vlans'].add(int (vlan))
                print('Give another VLAN? (y/n):')
                if input() =='n':
                    break
        print('Give another switch? (y/n):')
        if input() =='n':
           break
    for switch in vlan_data:
        for port in vlan_data[switch]:
            vlan_data[switch][port]['vlans'] = sorted(list(vlan_data[switch][port]['vlans']))
    return vlan_data
vlan_info = functie_switch()
print(vlan_info)
