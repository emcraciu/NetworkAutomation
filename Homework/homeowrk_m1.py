main_dictionary={}
while True:
    switch_name=input("Enter your switch name: ")
    if main_dictionary.get(switch_name) is None:
        main_dictionary[switch_name]={}

        while True:
            port_name=input("Enter port name ('q' to quit): ")
            if port_name =='q':
                break
            if main_dictionary[switch_name].get(port_name) is None:
                main_dictionary[switch_name][port_name]={}
            else:
                print("Port name already exists")
            print(main_dictionary[switch_name])



    else:
        print("You have already entered the switch name")


    print(main_dictionary)