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
# PAGINATION HELPER
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
        response = requests.get(f"{base_url}/collections/all")
        html = response.text

        return list(set(
            re.findall(r'/products/([^"]+)', html)
        ))

    except:
        return []


# ==========================================
# SITEMAP SCRAPER (CORRECT)
# ==========================================

def fetch_handles_from_sitemap(base_url):

    handles = set()

    try:
        index = requests.get(f"{base_url}/sitemap.xml").text

        sitemap_links = re.findall(
            r'<loc>(.*?)</loc>',
            index
        )

        product_sitemaps = [
            url for url in sitemap_links
            if "sitemap_products" in url
        ]

        for sitemap_url in product_sitemaps:

            res = requests.get(sitemap_url)
            xml = res.text

            found = re.findall(
                r'/products/([^<]+)',
                xml
            )

            handles.update(found)

    except Exception as e:
        print("Sitemap error:", e)

    return list(handles)


# ==========================================
# FALLBACK PER PRODUCT
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
# MAIN FUNCTION (OPTIMIZED + FIX)
# ==========================================

def fetch_all_products():

    all_products = []

    for shop_name, base_url in SHOPS.items():

        print(f"\n=== {shop_name} ===")

        try:

            # 1. API
            products = fetch_products(shop_name, base_url)

            existing_handles = set(
                p["handle"] for p in products
            )

            # 2. EXTRA SOURCES
            collection_handles = fetch_handles_from_collection(base_url)
            sitemap_handles = fetch_handles_from_sitemap(base_url)

            all_handles = set(collection_handles) | set(sitemap_handles)

            missing_handles = [
                h for h in all_handles
                if h not in existing_handles
            ]

            print(f"Missende handles: {len(missing_handles)}")

            # 🔥 PERFORMANCE FIX
            LIMIT = 100

            if len(missing_handles) > LIMIT:
                missing_handles = random.sample(missing_handles, LIMIT)

            for handle in missing_handles:

                extra = fetch_product_by_handle(base_url, handle)

                if extra:
                    products.extend(extra)

            print(f"TOTAAL {shop_name}: {len(products)}")

            all_products.extend(products)

        except Exception as e:
            print(f"Fout bij {shop_name}: {e}")


    # ==========================================
    # 🔥 MANUAL OVERRIDE (JOUW FIX)
    # ==========================================

    known_missing = [
        ("Crea with Gaby", "https://creawithgaby.com", "floral-washi-tape-homebody-collection-30mm")
    ]

    for shop_name, base_url, handle in known_missing:

        extra = fetch_product_by_handle(base_url, handle)

        if extra:
            print(f"Handmatig toegevoegd: {handle}")
            all_products.extend(extra)

    return all_products
