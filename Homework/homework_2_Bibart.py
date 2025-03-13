cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

def best_buy(cart, shops):
    shop_prices = {}
    for shop_name, shop_dict in shops.items():
        if all([item in shop_dict for item in cart]):
            shop_prices[shop_name] = sum([
                cart[item] * shop_dict[item] for item in cart
            ])
    shop_prices = list(shop_prices.items())
    shop_prices.sort(key=lambda x: x[1])
    print(shop_prices)
    return {
        "shop_name":shop_prices[0][0]
    }
print(best_buy(cart, shops))