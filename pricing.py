def calculate_suggested_price(my_price, competitor_price):

    if competitor_price < my_price:
        return round(competitor_price - 0.05, 2)

    return my_price