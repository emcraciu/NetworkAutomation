import time

dict_items={}
dict_shops= {"Kaufland":
                    {"apple":1.2,"plums":4,"cherry":5.5,"bananas":3,"oranges":6},
            "Lidl":
                    {'apple': 1.3, 'pears': 3, 'bananas': 2},
            "Carrefour":
                    {'apple': 1.4, 'oranges': 2, 'bananas': 10}}

def best_shop(smallest_price_and_shop):
    smallest_price = 100000000000.0
    smallest_price_shop_name = ""
    for key, value in smallest_price_and_shop.items():
        if float(smallest_price_and_shop[key]) < smallest_price:
            smallest_price = smallest_price_and_shop[key]
            smallest_price_shop_name = key

    return {"The shop with the smallest price":smallest_price_shop_name,"Price:": smallest_price}

def main_function(dict_items,dict_shops):
        list_of_shop_names=dict_shops.keys()
        list_of_wanted_items=dict_items.keys()
        smallest_price_and_shop={}

        for shop_name in list_of_shop_names:

            shop_current_price = 0
            trigger = 0

            for item_name in list_of_wanted_items:

                for shop_items in dict_shops[shop_name]:
                    if item_name == shop_items:

                        shop_current_price += dict_items[item_name] * dict_shops[shop_name][shop_items]
                        trigger+=1

                if trigger == len(list_of_wanted_items):
                    smallest_price_and_shop[shop_name]=shop_current_price

        return best_shop(smallest_price_and_shop)

def processing_function():
    for i in range(10):
        time.sleep(0.15)
        print(i*"*",end="")
    print("\n")
    print("Done processing!")

while True:
    print("Find the best price for you!!")
    items=input("Enter the items you want: ")
    amount=input("Enter the amount you want: ")
    while not amount.isdigit():
        amount = input("Enter the amount you want as integer(1-100)!: ")

    amount=int(amount)
    dict_items[items] = amount

    response=input("\nDo you want to continue? (y/n): ")
    if response == "y":
        continue
    processing_function()
    break

best_shop=main_function(dict_items,dict_shops)
print(best_shop)
