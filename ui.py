import streamlit as st
import pandas as pd
import requests

from io import BytesIO
from datetime import datetime

from competitor_fetcher import fetch_all_products
from matcher import find_matches


# ==========================================
# SHOPIFY API PRODUCTEN OPHALEN
# ==========================================

def fetch_shopify_products(
    shop_url,
    access_token
):

    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }

    url = (
        f"https://{shop_url}"
        f"/admin/api/2024-01/products.json?limit=250"
    )

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    data = response.json()["products"]

    products = []

    for product in data:

        product_title = product.get("title", "")

        for variant in product.get("variants", []):

            variant_title = variant.get("title", "")

            full_title = product_title

            if (
                variant_title
                and variant_title != "Default Title"
            ):
                full_title += (
                    f" - {variant_title}"
                )

            try:
                price = float(
                    variant.get("price", 0)
                )
            except:
                price = 0

            products.append({

                "shop": "My Shop",

                "title": full_title,

                "product_title":
                    product_title,

                "variant_title":
                    variant_title,

                "price":
                    price,

                "sku":
                    str(
                        variant.get("sku", "")
                    ).strip(),

                "handle":
                    str(
                        product.get("handle", "")
                    ).strip(),
            })

    return products


# ==========================================
# STREAMLIT UI
# ==========================================

st.set_page_config(
    page_title="Competitor Pricing Tool",
    layout="wide"
)

st.title(
    "Shopify Competitor Comparison Tool"
)

st.write(
    "Vergelijk jouw Shopify shop live "
    "met concurrenten"
)

# ==========================================
# SHOPIFY SETTINGS
# ==========================================

st.header("Shopify instellingen")

shop_url = st.text_input(
    "Shop URL",
    placeholder="voorbeeld.myshopify.com"
)

access_token = st.text_input(
    "Shopify Admin API Token",
    type="password"
)

# ==========================================
# START BUTTON
# ==========================================

if (
    shop_url
    and access_token
    and st.button("Start vergelijking")
):

    # ==========================================
    # EIGEN PRODUCTEN OPHALEN
    # ==========================================

    with st.spinner(
        "Eigen Shopify producten ophalen..."
    ):

        my_products = fetch_shopify_products(
            shop_url,
            access_token
        )

    # ==========================================
    # CONCURRENTEN OPHALEN
    # ==========================================

    with st.spinner(
        "Concurrent producten ophalen..."
    ):

        competitor_products = (
            fetch_all_products()
        )

    # ==========================================
    # MATCHING
    # ==========================================

    with st.spinner(
        "Producten vergelijken..."
    ):

        matches, unmatched, unmatched_competitors = (
            find_matches(
                my_products,
                competitor_products
            )
        )

    # ==========================================
    # MATCHED RESULTS
    # ==========================================

    st.header("Gematchte producten")

    matched_results = []

    for match in matches:

        price_difference = round(
            match["my_price"]
            - match["competitor_price"],
            2
        )

        matched_results.append({

            "Mijn Product":
                match["my_full_title"],

            "Mijn SKU":
                match["my_sku"],

            "Mijn Prijs":
                match["my_price"],

            "Concurrent Shop":
                match["competitor_shop"],

            "Concurrent Product":
                match[
                    "competitor_full_title"
                ],

            "Concurrent SKU":
                match["competitor_sku"],

            "Concurrent Prijs":
                match["competitor_price"],

            "Prijsverschil":
                price_difference,

            "Match Type":
                match["match_type"],

            "Match Score":
                match["score"],
        })

    matched_df = pd.DataFrame(
        matched_results
    )

    st.success(
        f"{len(matched_df)} matches gevonden"
    )

    st.dataframe(
        matched_df,
        use_container_width=True
    )

    # ==========================================
    # PRODUCTEN ZONDER MATCH
    # ==========================================

    st.header(
        "Eigen producten zonder match"
    )

    unmatched_df = pd.DataFrame(
        unmatched
    )

    st.dataframe(
        unmatched_df,
        use_container_width=True
    )

    # ==========================================
    # LOVELY DOTS
    # ==========================================

    st.header(
        "Lovely Dots producten"
    )

    lovelydots_df = pd.DataFrame([

        p for p in competitor_products
        if p["shop"] == "Lovely Dots"

    ])

    st.dataframe(
        lovelydots_df,
        use_container_width=True
    )

    # ==========================================
    # CREA WITH GABY
    # ==========================================

    st.header(
        "Crea with Gaby producten"
    )

    gaby_df = pd.DataFrame([

        p for p in competitor_products
        if p["shop"] == "Crea with Gaby"

    ])

    st.dataframe(
        gaby_df,
        use_container_width=True
    )

    # ==========================================
    # SAMES JOURNAL
    # ==========================================

    st.header(
        "Sames Journal producten"
    )

    sames_df = pd.DataFrame([

        p for p in competitor_products
        if p["shop"] == "Sames Journal"

    ])

    st.dataframe(
        sames_df,
        use_container_width=True
    )

    # ==========================================
    # EXCEL EXPORT
    # ==========================================

    st.header("Excel Export")

    excel_buffer = BytesIO()

    export_date = datetime.now().strftime(
        "%Y-%m-%d_%H-%M"
    )

    file_name = (
        f"pricing_export_"
        f"{export_date}.xlsx"
    )

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        matched_df.to_excel(
            writer,
            sheet_name="Matches",
            index=False
        )

        unmatched_df.to_excel(
            writer,
            sheet_name="Unmatched",
            index=False
        )

        lovelydots_df.to_excel(
            writer,
            sheet_name="Lovely Dots",
            index=False
        )

        gaby_df.to_excel(
            writer,
            sheet_name="Crea with Gaby",
            index=False
        )

        sames_df.to_excel(
            writer,
            sheet_name="Sames Journal",
            index=False
        )

    excel_buffer.seek(0)

    st.download_button(

        label="Download Excel Export",

        data=excel_buffer,

        file_name=file_name,

        mime=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )