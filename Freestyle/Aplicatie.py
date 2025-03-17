# Produsele disponibile și prețurile:
# 1️⃣ Sandwich ..................... 8 lei
# 2️⃣ Cafea .......................... 4 lei
# 3️⃣ Cola ............................ 5 lei
# 4️⃣ Apă ............................. 3 lei
# 5️⃣ Snack .......................... 5 lei
# 6️⃣ Combo Sandwich + Cola ... 11 lei

while True:
    print("──────────────────────────────")
    print("1 Sandwich ............... 8 lei")
    print("2 Cafea .................. 4 lei")
    print("3 Cola ................... 5 lei")
    print("4 Apă .................... 3 lei")
    print("5 Snack .................. 5 lei")
    print("6 Meniu Sandwich + Cola .. 11 lei")
    print("──────────────────────────────")

    choice = input("Alegeți o opțiune: ").strip().lower()

    if choice == 'x':
        print("O zi buna! ")
        break
    elif choice in {'1', '2', '3', '4', '5', '6'}:
        print(f"Ați selectat produsul {choice}. Vă rugăm să introduceți o bancnotă validă (1, 5, 10, 50, 100 lei).")
    else:
        print("Optiunea nu este valida ")