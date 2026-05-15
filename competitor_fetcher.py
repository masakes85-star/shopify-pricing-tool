import requests
import time
import re

SHOPS = {
    "Lovely Dots": "https://lovelydots.nl",
    "Crea with Gaby": "https://creawithgaby.com",
    "Sames Journal": "https://samesjournal.com",
    "Cloth & Paper": "https://www.clothandpaper.com",
}


# ==========================================
# NEXT PAGE PARSER
# ==========================================

def get_next_link(response):

    link_header = response.headers.get("Link")

    if not link_header:
        return None

    links = link_header.split(",")

    for link in links:
        if 'rel="next"' in link:
            return link.split(";")[0].strip()[1:-1]

    return None


# ==========================================
# PAGINATION FETCH
# ==========================================

def fetch_products(shop_name, base_url):

    url = f"{base_url}/products.json?limit=250"

    products = []

    while url:

        response = requests.get(url)
        response.raise_for_status()

        data = response.json().get("products", [])

        for product in data:

            product_title = product.get("title", "")

            for variant in product.get("variants", []):

                variant_title = variant.get("title", "")

                full_title = product_title

                if (
                    variant_title
                    and variant_title != "Default Title"
                ):
                    full_title += f" - {variant_title}"

                try:
                    price = float(variant.get("price", 0))
                except:
                    price = 0

                products.append({

                    "shop": shop_name,
                    "title": full_title,
                    "product_title": product_title,
                    "variant_title": variant_title,
                    "price": price,
                    "sku": str(variant.get("sku", "")).strip(),
                    "handle": str(product.get("handle", "")).strip(),
                    "url": f"{base_url}/products/{product.get('handle')}"
                })

        url = get_next_link(response)

        time.sleep(0.2)

    return products


# ==========================================
# FALLBACK VIA HANDLE
# ==========================================

def fetch_product_by_handle(base_url, handle):

    try:
        url = f"{base_url}/products/{handle}.js"
        response = requests.get(url)

        if response.status_code != 200:
            return None

        product = response.json()
        product_title = product.get("title", "")

        results = []

        for variant in product.get("variants", []):

            variant_title = variant.get("title", "")

            full_title = product_title

            if variant_title and variant_title != "Default Title":
                full_title += f" - {variant_title}"

            results.append({

                "shop": base_url,
                "title": full_title,
                "product_title": product_title,
                "variant_title": variant_title,
                "price": float(variant.get("price", 0)) / 100,
                "sku": str(variant.get("sku", "")).strip(),
                "handle": handle,
                "url": f"{base_url}/products/{handle}"
            })

        return results

    except:
        return None


# ==========================================
# COLLECTION SCRAPER (KEY FIX)
# ==========================================

def fetch_handles_from_collection(base_url):

    url = f"{base_url}/collections/all"

    response = requests.get(url)
    html = response.text

    handles = set(
        re.findall(r'/products/([^"]+)', html)
    )

    return list(handles)


# ==========================================
# MAIN
# ==========================================

def fetch_all_products():

    all_products = []

    for shop_name, base_url in SHOPS.items():

        print(f"Ophalen: {shop_name}")

        try:

            products = fetch_products(
                shop_name,
                base_url
            )

            existing_handles = set(
                p["handle"] for p in products
            )

            # 🔥 EXTRA: haal alles uit collection
            handles = fetch_handles_from_collection(
                base_url
            )

            for handle in handles:

                if handle not in existing_handles:

                    extra = fetch_product_by_handle(
                        base_url,
                        handle
                    )

                    if extra:
                        products.extend(extra)

            print(f"{shop_name}: {len(products)} totaal")

            all_products.extend(products)

        except Exception as e:

            print(f"Fout bij {shop_name}: {e}")

    return all_products
