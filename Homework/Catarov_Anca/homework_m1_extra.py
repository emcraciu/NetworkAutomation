
def bestBuy(cart, shops): ##functie cu 2 arg: cosul si magazinele
    shop_product = {} ##am initializat un dict gol
    for product in cart: ##am parcus fiecare produs din cos
        price = 0 ##am initializat o variabila price cu valoarea 0,pt. a stoca cel mai mic pret al produsului
        shop_name = "" ##am initializat numele magazinului pt a stoca numele magazinului cu cel mai mic pret
        for shop in shops: ##am parcurs fiecare magazin din magazine
            for prod in shops[shop]: ## am parcurs fiecare produs din magazin
                if product == prod: ## am verificat daca produsul pe care il cautam exista in magazin
                    if price == 0: ## am verificat daca nu avem pret cu ce sa il comparam
                        price = shops[shop][prod] ## am salvat primul pret gasit
                        shop_name = shop ## am salvat magazinul unde am gasit pretul
                    elif price > shops[shop][prod]: ## am verificat pretul salvat cu cu pretul gasit in alt magazin
                        price = shops[shop][prod]## am salvat pretul gasit
                        shop_name = shop ## am salvat magazinul unde am gasit pretul
        if price > 0: ## am verificat daca avem pret,adica produsul se afla intr-un magazin
            if shop_name not in shop_product: ## am verificat daca magazinul nu se afla in dict nostru
                shop_product[shop_name] = {"total_price": 0} ## am initializat magazinul in dict cu total_price pe 0
            total_price = shop_product[shop_name]["total_price"] ## am luat total_price
            total_price += price * cart[product] ## am inmultit cantitatea cu pretul si l-am adunat cu costul total
            shop_product[shop_name]["total_price"] = total_price ##am salvat total_price in dict
            shop_product[shop_name][product] = {"Cantitate": cart[product], "Price": price } ##am adaugat produsul in dict
    return shop_product

cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

print(bestBuy(cart, shops)) ## am apelat functia si am afisat rezultatul