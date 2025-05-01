# code for exercise from markdown file

def vlan_information():
    switch_information = {} #stocam informatiile despre fiecare switch,port si vlan-uri
    switch_name = input("Enter switch name: ")
    while switch_name != 'q':  #bucla care continua pana cand user-ul introduce 'q' pentru a iesii din bucla
        print("Switch name is: ",switch_name)
        switch_port = input("Enter switch port: ")
        while switch_port != 'q':  #incep o alta bucla care continua pana cand user-ul introduce 'q'
            vlans_set = set() #set gol pentru VLAN-uri (folosim un set pentru a evita duplicarea VLAN-urilor)
            vlan = input("Enter vlan number: ")
            if vlan.isdigit(): #verific daca numărul introdus este un numar intreg
                vlans_set.add(int(vlan)) #adaug vlan-ul in set
            print(vlans_set)
            while vlan != 'q': #continui să cer VLAN-uri pentru portul respectiv până când user-ul introduce 'q'
                vlan = input("Add more vlan or press q to quit: ")
                if vlan.isdigit():
                    vlans_set.add(int(vlan))
                print(vlan)
                print(vlans_set)
            print(vlans_set)
            #verific daca switch-ul exista deja in dictionar, daca nu exista il adaug ca dict gol
            if switch_name not in switch_information:
                switch_information[switch_name] = {}
            #pentru acest switch adaugam un nou port daca nu exista, si valorile lui
            switch_information[switch_name][switch_port] = {'vlans': vlans_set}
            print(switch_information)
            switch_port = input("Add more ports or press q to quit: ")
        #intrebam user-ul daca mai adauga alt switch sau 'q' pentru a iesii din program
        switch_name = input("Add more switch names or press q to quit: ")
    return switch_information #returnam dictionarul cu toate informatiile



result = vlan_information() #apelez functia si stochez rezultatul in variabila 'result'
print(result)