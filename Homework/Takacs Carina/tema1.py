import pprint
main_dictionary={}
while True: #endless loop for creating endless switches

    switch_name=input("Enter your switch name: ")
    if switch_name=='q':
        break
    if main_dictionary.get(switch_name) is None: #I try to see if the switch_name exists in the dictionary
        main_dictionary[switch_name]={}

        while True:
            port_name=input("Enter port name ('q' to quit): ")
            if port_name =='q':
                break  #if the user enters 'q' it won't ask for more port names
            if main_dictionary[switch_name].get(port_name) is None:
                main_dictionary[switch_name][port_name]={}
                main_dictionary[switch_name][port_name]['vlans']=[]
                while True:
                    vlan_nr=(input("Enter vlan number: "))
                    if vlan_nr=='q':
                        break
                    else:
                        main_dictionary[switch_name][port_name]['vlans'].append(int(vlan_nr))
                main_dictionary[switch_name][port_name]['vlans'] = list(set(main_dictionary[switch_name][port_name]['vlans']))
            else:
                print("Port name already exists")
            #print(main_dictionary[switch_name]) # print what's inside the switch,after creation




    else:
        print("You have already entered the switch name")


    print(main_dictionary) #standard print
    pprint.pprint(main_dictionary) #pprint