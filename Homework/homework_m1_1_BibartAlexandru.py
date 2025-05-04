import json
from enum import Enum
from xml.etree.ElementTree import indent


class AppState(Enum):
    SWITCH = 0,
    INTERFACE = 1,
    VLAN = 2

config = {}
current_sw = {} # o sa aiba valorile din reset_current_sw initial
state = AppState.SWITCH
should_stop = False

def reset_current_sw():
    global current_sw
    current_sw = {
        'name': None,
        'interfaces': {
            # nume : [10,50,20] str -> List[int]
        },
    }

def save_current_sw():
    global current_sw
    global config
    config[current_sw['name']] = {}
    for interface in current_sw['interfaces']:
        vlans = current_sw['interfaces'][interface]
        config[current_sw['name']][interface] = {'vlans': vlans}

def ask_for_switch():
        global config
        global current_sw
        global state
        global should_stop
        print("# ADDING A SWITCH #")
        print("Press s to save the config.")
        while True:
            sw_name = input("Enter the name of the switch: ")
            if sw_name == 'q':
                should_stop = True
                return
            if sw_name == 's':
                should_stop = True
                return
            if sw_name in config:
                print(f"Switch '{sw_name}' already configured")
            else:
                current_sw['name'] = sw_name
                state = AppState.INTERFACE
                return

def ask_for_interface():
    global state
    global should_stop
    global current_sw
    print(f"# CONFIGURING INTERFACES FOR SWITCH: {current_sw['name']} #")
    print(f"Press s to save {current_sw['name']}'s config #")
    while True:
        int_name = input("Enter the name of the interface: ")
        if int_name == 'q':
            should_stop = True
            return
        if int_name =='s':
            save_current_sw()
            reset_current_sw()
            state = AppState.SWITCH
            return
        if len(current_sw['interfaces']) == 0 or int_name not in current_sw['interfaces']:
            current_sw['interfaces'][int_name] = []
            state = AppState.VLAN
            return
        print(f"Interface '{int_name}' already configured with configuration:{current_sw['interfaces'][int_name]}")


def ask_for_vlan():
    global state
    global should_stop
    global current_sw
    current_interf = None
    for interf, vlans in current_sw['interfaces'].items():
        if len(vlans) == 0:
            current_interf = interf
            break
    print(f"# CONFIGURING VLANS FOR INTERFACE: {current_interf} #")
    print("Press s when you're done with adding VLANs to go back to adding interfaces")
    while True:
        # print(current_sw)
        try:
            vlan_name = input("Enter the vlan id: ")
            if vlan_name == 'q':
                should_stop = True
                return
            if vlan_name == 's' and all([len(vlans) > 0 for i,vlans in current_sw['interfaces'].items()]):
                state = AppState.INTERFACE
                return
            elif vlan_name == 's':
                print("Interfaces must have at least 1 VLAN")
            else:
                vlan_name = int(vlan_name)
                current_sw['interfaces'][current_interf].append(vlan_name)
        except Exception as e:
            print("Vlan id must be an integer.")


def run():
    global should_stop
    global config
    global state
    reset_current_sw()
    while not should_stop:
        # print(current_sw)
        match state:
            case AppState.SWITCH:
                ask_for_switch()
            case AppState.INTERFACE:
                ask_for_interface()
            case AppState.VLAN:
                ask_for_vlan()

    print("The configuration is:")
    print(json.dumps(config, indent=4))

run()