from rapidfuzz import fuzz

MATCH_THRESHOLD = 75


def calculate_match_score(
    my_product,
    competitor_product
):

    # ==========================================
    # SKU EXACT MATCH
    # ==========================================

    my_sku = (
        my_product.get("sku", "")
        .lower()
        .strip()
    )

    competitor_sku = (
        competitor_product.get("sku", "")
        .lower()
        .strip()
    )

    if (
        my_sku
        and competitor_sku
        and my_sku == competitor_sku
    ):
        return 100, "SKU Match"

    # ==========================================
    # HANDLE MATCH
    # ==========================================

    my_handle = (
        my_product.get("handle", "")
        .lower()
        .strip()
    )

    competitor_handle = (
        competitor_product.get("handle", "")
        .lower()
        .strip()
    )

    if my_handle and competitor_handle:

        handle_score = fuzz.ratio(
            my_handle,
            competitor_handle
        )

        if handle_score >= 90:
            return handle_score, "Handle Match"

    # ==========================================
    # TITLE MATCH
    # ==========================================

    title_score = fuzz.ratio(
        my_product["title"].lower(),
        competitor_product["title"].lower()
    )

    return title_score, "Title Match"


def find_matches(
    my_products,
    competitor_products
):

    matches = []
    unmatched = []

    # ==========================================
    # PRODUCTEN GROEPEREN PER SHOP
    # ==========================================

    shops = {}

    for product in competitor_products:

        shop_name = product["shop"]

        if shop_name not in shops:
            shops[shop_name] = []

        shops[shop_name].append(product)

    # ==========================================
    # MATCH PER SHOP
    # ==========================================

    for my_product in my_products:

        found_match = False

        for shop_name, shop_products in shops.items():

            best_match = None
            best_score = 0
            best_match_type = ""

            for competitor_product in shop_products:

                score, match_type = (
                    calculate_match_score(
                        my_product,
                        competitor_product
                    )
                )

                if score > best_score:

                    best_score = score

                    best_match = competitor_product

                    best_match_type = match_type

            if (
                best_match
                and best_score >= MATCH_THRESHOLD
            ):

                found_match = True

                matches.append({

                    "my_product_title":
                        my_product["product_title"],

                    "my_variant_title":
                        my_product["variant_title"],

                    "my_full_title":
                        my_product["title"],

                    "my_price":
                        my_product["price"],

                    "my_sku":
                        my_product.get("sku", ""),

                    "my_handle":
                        my_product.get("handle", ""),

                    "competitor_shop":
                        best_match["shop"],

                    "competitor_product_title":
                        best_match["product_title"],

                    "competitor_variant_title":
                        best_match["variant_title"],

                    "competitor_full_title":
                        best_match["title"],

                    "competitor_price":
                        best_match["price"],

                    "competitor_sku":
                        best_match.get("sku", ""),

                    "competitor_handle":
                        best_match.get("handle", ""),

                    "competitor_compare_at_price":
                        best_match.get(
                            "compare_at_price",
                            ""
                        ),

                    "competitor_vendor":
                        best_match.get(
                            "vendor",
                            ""
                        ),

                    "competitor_product_type":
                        best_match.get(
                            "product_type",
                            ""
                        ),

                    "competitor_tags":
                        best_match.get(
                            "tags",
                            ""
                        ),

                    "competitor_variant_id":
                        best_match.get(
                            "variant_id",
                            ""
                        ),

                    "competitor_product_id":
                        best_match.get(
                            "product_id",
                            ""
                        ),

                    "score":
                        best_score,

                    "match_type":
                        best_match_type,
                })

        # ==========================================
        # GEEN MATCH
        # ==========================================

        if not found_match:

            unmatched.append({

                "shop":
                    my_product["shop"],

                "product_title":
                    my_product["product_title"],

                "variant_title":
                    my_product["variant_title"],

                "full_title":
                    my_product["title"],

                "price":
                    my_product["price"],

                "sku":
                    my_product.get("sku", ""),

                "handle":
                    my_product.get("handle", ""),
            })

    # ==========================================
    # CONCURRENTEN ZONDER MATCH
    # ==========================================

    unmatched_competitors = []

    for competitor_product in competitor_products:

        found = False

        for match in matches:

            if (
                match["competitor_full_title"]
                == competitor_product["title"]
                and
                match["competitor_shop"]
                == competitor_product["shop"]
            ):
                found = True
                break

        if not found:

            unmatched_competitors.append({

                "shop":
                    competitor_product["shop"],

                "product_title":
                    competitor_product["product_title"],

                "variant_title":
                    competitor_product["variant_title"],

                "full_title":
                    competitor_product["title"],

                "price":
                    competitor_product["price"],

                "sku":
                    competitor_product.get("sku", ""),

                "handle":
                    competitor_product.get("handle", ""),

                "compare_at_price":
                    competitor_product.get(
                        "compare_at_price",
                        ""
                    ),

                "vendor":
                    competitor_product.get(
                        "vendor",
                        ""
                    ),

                "product_type":
                    competitor_product.get(
                        "product_type",
                        ""
                    ),

                "tags":
                    competitor_product.get(
                        "tags",
                        ""
                    ),

                "variant_id":
                    competitor_product.get(
                        "variant_id",
                        ""
                    ),

                "product_id":
                    competitor_product.get(
                        "product_id",
                        ""
                    ),
            })

    return (
        matches,
        unmatched,
        unmatched_competitors
    )