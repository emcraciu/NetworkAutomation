cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

def create_dictionary(cart, **shops):

    shop_values = {}

    for shop_name, shop in shops.items():
        count = 0
        for item in cart:
            price = cart[item] * shop.get(item,0)
            count = count + price
        shop_values[shop_name] = count

    max_val = 0
    max_key = None
    for key, value in shop_values.items():
        if value > max_val:
            max_val = value
            max_key = key

    return {max_key: max_val}


print(create_dictionary(cart, **shops))






