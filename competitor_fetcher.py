import requests
import time

SHOPS = {
    "Lovely Dots": "https://lovelydots.nl",
    "Crea with Gaby": "https://creawithgaby.com",
    "Sames Journal": "https://samesjournal.com",
    "Cloth & Paper": "https://www.clothandpaper.com",
}


def get_next_link(response):

    link_header = response.headers.get("Link")

    if not link_header:
        return None

    links = link_header.split(",")

    for link in links:

        if 'rel="next"' in link:

            return (
                link
                .split(";")[0]
                .strip()[1:-1]
            )

    return None


def fetch_products(
    shop_name,
    base_url
):

    url = f"{base_url}/products.json?limit=250"

    products = []

    while url:

        print(
            f"Ophalen: {shop_name}"
        )

        response = requests.get(
            url,
            timeout=30
        )

        response.raise_for_status()

        data = response.json().get(
            "products",
            []
        )

        for product in data:

            product_title = product.get(
                "title",
                ""
            )

            for variant in product.get(
                "variants",
                []
            ):

                variant_title = variant.get(
                    "title",
                    ""
                )

                full_title = product_title

                if (
                    variant_title
                    and
                    variant_title
                    != "Default Title"
                ):

                    full_title += (
                        f" - {variant_title}"
                    )

                try:

                    price = float(
                        variant.get(
                            "price",
                            0
                        )
                    )

                except:

                    price = 0

                image_src = ""

                if product.get("image"):

                    image_src = (
                        product["image"]
                        .get("src", "")
                    )

                products.append({

                    "shop":
                        shop_name,

                    "title":
                        full_title,

                    "product_title":
                        product_title,

                    "body_html":
                        product.get(
                            "body_html",
                            ""
                        ),

                    "variant_title":
                        variant_title,

                    "price":
                        price,

                    "compare_at_price":
                        variant.get(
                            "compare_at_price"
                        ),

                    "sku":
                        str(
                            variant.get(
                                "sku",
                                ""
                            )
                        ).strip(),

                    "barcode":
                        str(
                            variant.get(
                                "barcode",
                                ""
                            )
                        ).strip(),

                    "inventory_qty":
                        variant.get(
                            "inventory_quantity",
                            ""
                        ),

                    "requires_shipping":
                        variant.get(
                            "requires_shipping",
                            True
                        ),

                    "taxable":
                        variant.get(
                            "taxable",
                            True
                        ),

                    "variant_id":
                        variant.get("id"),

                    "product_id":
                        product.get("id"),

                    "handle":
                        str(
                            product.get(
                                "handle",
                                ""
                            )
                        ).strip(),

                    "vendor":
                        product.get(
                            "vendor",
                            ""
                        ),

                    "product_type":
                        product.get(
                            "product_type",
                            ""
                        ),

                    "tags":
                        product.get(
                            "tags",
                            ""
                        ),

                    "published":
                        bool(
                            product.get(
                                "published_at"
                            )
                        ),

                    "status":
                        product.get(
                            "status",
                            "active"
                        ),

                    "image_src":
                        image_src,

                    "url":
                        f"{base_url}/products/{product.get('handle')}"
                })

        url = get_next_link(
            response
        )

        time.sleep(0.1)

    print(
        f"{shop_name}: "
        f"{len(products)} producten"
    )

    return products


def fetch_product_by_handle(
    base_url,
    handle
):

    try:

        url = (
            f"{base_url}"
            f"/products/{handle}.js"
        )

        response = requests.get(
            url,
            timeout=30
        )

        if response.status_code != 200:
            return None

        product = response.json()

        product_title = product.get(
            "title",
            ""
        )

        results = []

        for variant in product.get(
            "variants",
            []
        ):

            variant_title = variant.get(
                "title",
                ""
            )

            full_title = product_title

            if (
                variant_title
                and
                variant_title
                != "Default Title"
            ):
                full_title += (
                    f" - {variant_title}"
                )

            results.append({

                "shop": "Manual",

                "title":
                    full_title,

                "product_title":
                    product_title,

                "variant_title":
                    variant_title,

                "price":
                    float(
                        variant.get(
                            "price",
                            0
                        )
                    ) / 100,

                "sku":
                    str(
                        variant.get(
                            "sku",
                            ""
                        )
                    ).strip(),

                "handle":
                    handle,

                "url":
                    f"{base_url}/products/{handle}"
            })

        return results

    except Exception as e:

        print(e)

        return None


def ensure_missing_products(
    products,
    base_url
):

    existing_handles = set(
        p["handle"]
        for p in products
    )

    known_problem_handles = [
        "floral-washi-tape-homebody-collection-30mm"
    ]

    for handle in known_problem_handles:

        if handle not in existing_handles:

            extra = (
                fetch_product_by_handle(
                    base_url,
                    handle
                )
            )

            if extra:
                products.extend(extra)

    return products


def fetch_all_products():

    all_products = []

    for shop_name, base_url in SHOPS.items():

        try:

            shop_products = (
                fetch_products(
                    shop_name,
                    base_url
                )
            )

            shop_products = (
                ensure_missing_products(
                    shop_products,
                    base_url
                )
            )

            all_products.extend(
                shop_products
            )

        except Exception as e:

            print(
                f"Fout bij "
                f"{shop_name}: "
                f"{e}"
            )

    return all_products
