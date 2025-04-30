def collect_switch_config():
    switch_config = {}

    while True:
        switch_name = input("Introduceți numele switch-ului (sau 'q' pentru a termina): ").strip()
        if switch_name.lower() == 'q':
            break

        if switch_name not in switch_config:
            switch_config[switch_name] = {}

        else:
            print(f"Switch-ul {switch_name} exista deja! Alegeti altul!")
            continue

        while True:
            port_name = input(f"Introduceți portul pentru {switch_name} (sau 'q' pentru a termina): ").strip()
            if port_name.lower() == 'q':
                break

            if port_name in switch_config[switch_name]:
                print(f"Portul {port_name} există deja pe {switch_name}. Alegeți altul!")
                continue

            vlan_list = set()
            while True:
                vlans = input(f"Introduceți VLAN-urile pentru {port_name} separate prin virgulă (sau 'q' pentru a termina): ").strip()
                if vlans.lower() == 'q':
                    break

                try:
                    vlan_numbers = {int(vlan) for vlan in vlans.split(',')}
                    vlan_list.update(vlan_numbers)
                    print(f"VLAN-urile curente pentru {port_name}: {sorted(vlan_list)}")
                except ValueError:
                    print("Introduceți doar numere separate prin virgulă!")
                    continue

            if vlan_list:
                switch_config[switch_name][port_name] = {"vlans": sorted(vlan_list)}

    return switch_config

config = collect_switch_config()
print("\nConfigurația finală a switch-urilor:")
print(config)