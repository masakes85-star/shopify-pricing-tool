import requests

SHOPS = {
    "Lovely Dots": "https://lovelydots.nl/products.json?limit=250",
    "Crea with Gaby": "https://creawithgaby.com/products.json?limit=250",
    "Sames Journal": "https://samesjournal.com/products.json?limit=250",
}


def fetch_products(shop_name, url):

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()["products"]

    products = []

    for product in data:

        product_title = product.get("title", "")

        for variant in product.get("variants", []):

            variant_title = variant.get("title", "")

            # Full title maken
            full_title = product_title

            if (
                variant_title
                and variant_title != "Default Title"
            ):
                full_title += f" - {variant_title}"

            products.append({

                "shop": shop_name,

                "title": full_title,

                "product_title": product_title,

                "variant_title": variant_title,

                "price": float(
                    variant.get("price", 0)
                ),

                "compare_at_price":
                    variant.get("compare_at_price"),

                "sku":
                    str(
                        variant.get("sku", "")
                    ).strip(),

                "variant_id":
                    variant.get("id"),

                "product_id":
                    product.get("id"),

                "handle":
                    str(
                        product.get("handle", "")
                    ).strip(),

                "vendor":
                    product.get("vendor"),

                "product_type":
                    product.get("product_type"),

                "tags":
                    product.get("tags"),

                "created_at":
                    product.get("created_at"),

                "updated_at":
                    product.get("updated_at"),

                "url":
                    f"https://{url.split('/')[2]}/products/{product.get('handle')}"
            })

    return products


def fetch_all_products():

    all_products = []

    for shop_name, url in SHOPS.items():

        print(f"Ophalen: {shop_name}")

        products = fetch_products(
            shop_name,
            url
        )

        print(
            f"{len(products)} producten gevonden"
        )

        all_products.extend(products)

    return all_products