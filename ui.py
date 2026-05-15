import streamlit as st
import pandas as pd

from competitor_fetcher import (
    fetch_all_products,
    fetch_product_from_url
)

from matcher import find_matches

from io import BytesIO
from datetime import datetime


# ==========================================
# CONFIG
# ==========================================

st.set_page_config(layout="wide")

st.title("Shopify Competitor Comparison Tool")

st.write("Vergelijk jouw Shopify CSV export of bekijk alleen concurrenten")


# ==========================================
# MODE
# ==========================================

mode = st.radio(
    "Kies modus",
    [
        "Vergelijk met eigen CSV",
        "Alleen concurrenten bekijken"
    ]
)


# ==========================================
# CSV UPLOAD
# ==========================================

uploaded_file = None

if mode == "Vergelijk met eigen CSV":
    uploaded_file = st.file_uploader(
        "Upload Shopify Product CSV",
        type=["csv"]
    )


# ==========================================
# START
# ==========================================

if st.button("Start"):

    # ==========================================
    # EIGEN PRODUCTEN
    # ==========================================

    my_products = []
    results = []

    if mode == "Vergelijk met eigen CSV" and uploaded_file:

        df = pd.read_csv(uploaded_file)
        df = df[df["Variant Price"].notna()]

        for _, row in df.iterrows():

            product_title = str(row.get("Title", "")).strip()
            variant_title = str(row.get("Option1 Value", "")).strip()

            full_title = product_title

            if (
                variant_title
                and variant_title != "nan"
                and variant_title != "Default Title"
            ):
                full_title += f" - {variant_title}"

            try:
                price = float(row.get("Variant Price", 0))
            except:
                price = 0

            my_products.append({
                "shop": "My Shop",
                "title": full_title,
                "product_title": product_title,
                "variant_title": variant_title,
                "price": price,
                "sku": str(row.get("Variant SKU", "")).strip(),
                "handle": str(row.get("Handle", "")).strip(),
            })


    # ==========================================
    # CONCURRENTEN
    # ==========================================

    with st.spinner("Concurrent producten ophalen..."):
        competitor_products = fetch_all_products()

    st.write("TOTAL PRODUCTS:", len(competitor_products))

    # DEBUG
    test = [
        p for p in competitor_products
        if "floral-washi" in p["title"].lower()
    ]
    st.write("TEST RESULT:", test)


    # ==========================================
    # MATCHING
    # ==========================================

    if mode == "Vergelijk met eigen CSV" and uploaded_file:

        with st.spinner("Vergelijken..."):

            matches, unmatched, _ = find_matches(
                my_products,
                competitor_products
            )

        st.subheader("Matches")

        for m in matches:

            diff = round(
                m["my_price"] - m["competitor_price"], 2
            )

            results.append({
                "Mijn Product": m["my_full_title"],
                "Mijn SKU": m["my_sku"],
                "Mijn Prijs": m["my_price"],
                "Concurrent": m["competitor_shop"],
                "Product": m["competitor_full_title"],
                "Prijs": m["competitor_price"],
                "Verschil": diff,
                "Score": m["score"]
            })

        st.dataframe(pd.DataFrame(results), use_container_width=True)


    # ==========================================
    # PER SHOP
    # ==========================================

    def show_shop(name):

        df = pd.DataFrame([
            p for p in competitor_products
            if p["shop"] == name
        ])

        st.subheader(f"{name} producten")
        st.dataframe(df, use_container_width=True)

    show_shop("Lovely Dots")
    show_shop("Crea with Gaby")
    show_shop("Sames Journal")
    show_shop("Cloth & Paper")


    # ==========================================
    # 📥 EXCEL EXPORT
    # ==========================================

    st.subheader("Excel Export")

    excel_buffer = BytesIO()

    export_date = datetime.now().strftime("%Y-%m-%d_%H-%M")
    file_name = f"pricing_export_{export_date}.xlsx"

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:

        # MATCHES
        if mode == "Vergelijk met eigen CSV" and uploaded_file:
            pd.DataFrame(results).to_excel(
                writer,
                sheet_name="Matches",
                index=False
            )

        # SHOPS
        for shop in [
            "Lovely Dots",
            "Crea with Gaby",
            "Sames Journal",
            "Cloth & Paper"
        ]:

            df = pd.DataFrame([
                p for p in competitor_products
                if p["shop"] == shop
            ])

            df.to_excel(
                writer,
                sheet_name=shop[:31],
                index=False
            )

    excel_buffer.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=excel_buffer,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==========================================
# 🔥 HANDMATIGE URL TOOL
# ==========================================

st.divider()
st.subheader("Handmatig product ophalen")

manual_url = st.text_input(
    "Plak Shopify product URL",
    placeholder="https://creawithgaby.com/products/..."
)

if st.button("Haal product op"):

    if manual_url:

        with st.spinner("Product ophalen..."):
            result = fetch_product_from_url(manual_url)

        if result:
            st.success("Product gevonden")
            st.dataframe(pd.DataFrame(result), use_container_width=True)
        else:
            st.error("Kon product niet ophalen")
