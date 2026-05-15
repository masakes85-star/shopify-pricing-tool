import requests
import time
import re
import random

SHOPS = {
    "Lovely Dots": "https://lovelydots.nl",
    "Crea with Gaby": "https://creawithgaby.com",
    "Sames Journal": "https://samesjournal.com",
    "Cloth & Paper": "https://www.clothandpaper.com",
}


# ==========================================
# PAGINATION
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
# API FETCH
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
                if variant_title and variant_title != "Default Title":
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
        time.sleep(0.1)

    return products


# ==========================================
# COLLECTION SCRAPER
# ==========================================

def fetch_handles_from_collection(base_url):

    try:
        html = requests.get(f"{base_url}/collections/all").text
        return list(set(re.findall(r'/products/([^"]+)', html)))
    except:
        return []


# ==========================================
# SITEMAP SCRAPER
# ==========================================

def fetch_handles_from_sitemap(base_url):

    handles = set()

    try:
        index = requests.get(f"{base_url}/sitemap.xml").text

        sitemap_links = re.findall(r'<loc>(.*?)</loc>', index)

        product_sitemaps = [
            url for url in sitemap_links
            if "sitemap_products" in url
        ]

        for sitemap_url in product_sitemaps:
            xml = requests.get(sitemap_url).text

            found = re.findall(r'/products/([^<]+)', xml)
            handles.update(found)

    except:
        pass

    return list(handles)


# ==========================================
# FALLBACK (.JS)
# ==========================================

def fetch_product_by_handle(shop_name, base_url, handle):

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
                "shop": shop_name,  # 🔥 FIX
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
# HANDMATIGE URL FETCH (NIEUW 🔥)
# ==========================================

def fetch_product_from_url(product_url):

    try:
        base = product_url.split("/products/")[0]
        handle = product_url.split("/products/")[1].split("?")[0]

        return fetch_product_by_handle("Manual", base, handle)

    except:
        return None


# ==========================================
# MAIN
# ==========================================

def fetch_all_products():

    all_products = []

    for shop_name, base_url in SHOPS.items():

        try:

            products = fetch_products(shop_name, base_url)

            existing_handles = set(p["handle"] for p in products)

            collection_handles = fetch_handles_from_collection(base_url)
            sitemap_handles = fetch_handles_from_sitemap(base_url)

            all_handles = set(collection_handles) | set(sitemap_handles)

            missing_handles = [
                h for h in all_handles
                if h not in existing_handles
            ]

            # 🔥 PERFORMANCE FIX
            LIMIT = 80

            if len(missing_handles) > LIMIT:
                missing_handles = random.sample(missing_handles, LIMIT)

            for handle in missing_handles:

                extra = fetch_product_by_handle(
                    shop_name,
                    base_url,
                    handle
                )

                if extra:
                    products.extend(extra)

            all_products.extend(products)

        except Exception as e:
            print(f"Error {shop_name}: {e}")

    return all_products
