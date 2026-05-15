import streamlit as st
import pandas as pd

from competitor_fetcher import (
    fetch_all_products,
    fetch_product_from_url
)

st.set_page_config(layout="wide")

st.title("Shopify Competitor Comparison Tool")

mode = st.radio(
    "Kies modus",
    ["Alleen concurrenten bekijken"]
)

if st.button("Start"):

    with st.spinner("Producten ophalen..."):
        competitor_products = fetch_all_products()

    st.write("TOTAL PRODUCTS:", len(competitor_products))

    # DEBUG
    test = [
        p for p in competitor_products
        if "floral-washi" in p["title"].lower()
    ]

    st.write("TEST RESULT:", test)

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
# 🔥 HANDMATIGE URL TOOL
# ==========================================

st.divider()
st.subheader("Handmatig product ophalen")

manual_url = st.text_input(
    "Plak Shopify product URL"
)

if st.button("Haal product op"):

    if manual_url:

        with st.spinner("Ophalen..."):
            result = fetch_product_from_url(manual_url)

        if result:
            st.success("Product gevonden")
            st.dataframe(pd.DataFrame(result))
        else:
            st.error("Niet gevonden")
