cart = {'apple': 10, 'plums': 15, 'bananas': 5}
shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

def finder (items, shop_list):
    result = {}
    for item in items:
        result[item] = {}
        result[item]['price'] = None

        for shop in shop_list:
            if result[item]['price'] is None:
                result[item]['price'] = shop_list[shop][item]
            elif result[item]['price'] > shop_list[shop][item]:
                result[item]['price'] = shop_list[shop][item]
        result[item]['total'] = result[item]['price'] * items[item]
    return result


print(finder(cart,shops))






