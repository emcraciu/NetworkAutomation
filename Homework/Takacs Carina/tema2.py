

cart = {'apple': 10, 'plums': 15, 'bananas': 5}
shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

result = {}

for product in cart:
    result[product] = {}
    result[product]['price'] = None
    result[product]['total'] = None
    for shop in shops:
        if result[product]['price'] is None:
            result[product]['price'] = shops[shop][product]
        elif result[product]['price'] > shops[shop][product]:
            result[product]['price'] = shops[shop][product]

print(result)






