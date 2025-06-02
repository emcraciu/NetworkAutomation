def collect_switch_config():
    switch_config = {}

    while True:
        switch_name = input("Enter switch name (or 'q' to quit): ")
        if switch_name == 'q':
            break

        if switch_name not in switch_config:
            switch_config[switch_name] = {}

        while True:
            port = input(f"Enter port for {switch_name} (or 'q' to stop adding ports): ")
            if port == 'q':
                break

            if port not in switch_config[switch_name]:
                switch_config[switch_name][port] = {'vlans': []}

            while True:
                vlan_input = input(f"Enter VLANs for {port} (comma-separated, or 'q' to stop adding VLANs): ")
                if vlan_input == 'q':
                    break

                vlans = vlan_input.split(',')
                for vlan in vlans:
                    vlan = int(vlan)
                    vlan_set = set(switch_config[switch_name][port]['vlans'])
                    vlan_set.add(vlan)
                    switch_config[switch_name][port]['vlans'] = list(vlan_set)

            switch_config[switch_name][port]['vlans'].sort()

    return switch_config


switches = collect_switch_config()
print(switches)