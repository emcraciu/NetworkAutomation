Full_Dict={}

def dict_function(swich_name:str, switch_ports:list, switch_vlan:list):
    global Full_Dict

    if swich_name not in Full_Dict:
        Full_Dict[swich_name] = {}

    for counter in range(0, len(switch_vlan)):
        Full_Dict[swich_name][switch_ports[counter]]={"vlans":switch_vlan[counter]}

def verify_input(value):
    if value == "q":
        return False
    return True

def verify_if_empty(value):
    while value == "":
        value=input("You did not provide any value!\nPlease try again: ")
    return value

def port_transformation():
    vlan_list = []
    vlan_set = set()
    vlan_name= input("Please enter all vlans or press q: ").split(",")

    if "q" in vlan_name:
        return False

    for vlan in vlan_name:
        vlan_set.add(int(vlan))

    for vlan in vlan_set:
        vlan_list.append(vlan)

    return vlan_list

def data_function():

    last_switch_name=""
    last_ports_name=""
    condition1=True

    while condition1:
        list_ports=[]
        list_vlans=[]

        switch_name=input("Please input the switch name or press q:")

        while switch_name == last_switch_name:
            switch_name=input("You have already entered this name\nPlease enter another switch name or press q:")

        switch_name=verify_if_empty(switch_name)
        condition1=verify_input(switch_name)

        if condition1 is False:
            break

        condition2=condition1

        while condition2:

            switch_ports=input("Please input the switch ports name or press q:")
            switch_ports = verify_if_empty(switch_ports)
            while switch_ports == last_ports_name:
                switch_ports=input("You have already entered this name\nPlease enter another port name or press q:")

            switch_vlan=port_transformation()

            condition2=verify_input(switch_ports) and verify_input(switch_vlan)

            if condition2:
                list_ports.append(switch_ports)
                list_vlans.append(switch_vlan)
                last_ports_name = switch_ports

        last_switch_name=switch_name

        dict_function(switch_name,list_ports,list_vlans)

data_function()
print(Full_Dict)