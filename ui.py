import streamlit as st
import pandas as pd

from io import BytesIO
from datetime import datetime

from competitor_fetcher import fetch_all_products
from matcher import find_matches


st.set_page_config(
    page_title="Competitor Pricing Tool",
    layout="wide"
)

st.title("Shopify Competitor Comparison Tool")

st.write(
    "Upload jouw Shopify CSV export en vergelijk met concurrenten"
)

# ==========================================
# CSV IMPORT
# ==========================================

uploaded_file = st.file_uploader(
    "Upload Shopify Product CSV",
    type=["csv"]
)

# ==========================================
# START BUTTON
# ==========================================

if uploaded_file and st.button("Start vergelijking"):

    # ==========================================
    # CSV LADEN
    # ==========================================

    my_df = pd.read_csv(uploaded_file)

    # Alleen rijen met variant prijs
    my_df = my_df[
        my_df["Variant Price"].notna()
    ]

    my_products = []

    for _, row in my_df.iterrows():

        product_title = str(
            row.get("Title", "")
        ).strip()

        variant_title = str(
            row.get("Option1 Value", "")
        ).strip()

        full_title = product_title

        if (
            variant_title
            and variant_title != "nan"
            and variant_title != "Default Title"
        ):
            full_title += f" - {variant_title}"

        try:
            price = float(
                row.get("Variant Price", 0)
            )
        except:
            price = 0

        my_products.append({

            "shop": "My Shop",

            "title": full_title,

            "product_title": product_title,

            "variant_title": variant_title,

            "price": price,

            "sku": str(
                row.get("Variant SKU", "")
            ).strip(),

            "handle": str(
                row.get("Handle", "")
            ).strip(),
        })

    # ==========================================
    # CONCURRENTEN OPHALEN
    # ==========================================

    with st.spinner(
        "Concurrent producten ophalen..."
    ):

        all_products = fetch_all_products()

    competitor_products = all_products

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
    # MATCHED
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

            "Mijn Full Titel":
                match["my_full_title"],

            "Mijn SKU":
                match["my_sku"],

            "Mijn Handle":
                match["my_handle"],

            "Mijn Prijs":
                match["my_price"],

            "Concurrent Shop":
                match["competitor_shop"],

            "Concurrent Full Titel":
                match["competitor_full_title"],

            "Concurrent SKU":
                match["competitor_sku"],

            "Concurrent Handle":
                match["competitor_handle"],

            "Concurrent Prijs":
                match["competitor_price"],

            "Concurrent Compare At Price":
                match["competitor_compare_at_price"],

            "Concurrent Vendor":
                match["competitor_vendor"],

            "Concurrent Product Type":
                match["competitor_product_type"],

            "Concurrent Tags":
                match["competitor_tags"],

            "Concurrent Variant ID":
                match["competitor_variant_id"],

            "Concurrent Product ID":
                match["competitor_product_id"],

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
    # EIGEN PRODUCTEN ZONDER MATCH
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
    # LOVELY DOTS ZONDER MATCH
    # ==========================================

    lovelydots_unmatched = [
        p for p in unmatched_competitors
        if p["shop"] == "Lovely Dots"
    ]

    st.header(
        "Lovely Dots zonder match"
    )

    lovelydots_df = pd.DataFrame(
        lovelydots_unmatched
    )

    st.dataframe(
        lovelydots_df,
        use_container_width=True
    )

    # ==========================================
    # CREA WITH GABY ZONDER MATCH
    # ==========================================

    gaby_unmatched = [
        p for p in unmatched_competitors
        if p["shop"] == "Crea with Gaby"
    ]

    st.header(
        "Crea with Gaby zonder match"
    )

    gaby_df = pd.DataFrame(
        gaby_unmatched
    )

    st.dataframe(
        gaby_df,
        use_container_width=True
    )

    # ==========================================
    # SAMES JOURNAL ZONDER MATCH
    # ==========================================

    sames_unmatched = [
        p for p in unmatched_competitors
        if p["shop"] == "Sames Journal"
    ]

    st.header(
        "Sames Journal zonder match"
    )

    sames_df = pd.DataFrame(
        sames_unmatched
    )

    st.dataframe(
        sames_df,
        use_container_width=True
    )

    # ==========================================
    # ALLE PRODUCTEN MIJN SHOP
    # ==========================================

    st.header("Alle producten - Mijn Shop")

    my_all_results = []

    for _, row in my_df.iterrows():

        product_title = str(
            row.get("Title", "")
        ).strip()

        variant_title = str(
            row.get("Option1 Value", "")
        ).strip()

        full_title = product_title

        if (
            variant_title
            and variant_title != "nan"
            and variant_title != "Default Title"
        ):
            full_title += f" - {variant_title}"

        my_all_results.append({

            "Full Titel":
                full_title,

            "Product":
                product_title,

            "Variant":
                variant_title,

            "SKU":
                str(
                    row.get("Variant SKU", "")
                ).strip(),

            "Prijs":
                row.get(
                    "Variant Price",
                    ""
                ),

            "Compare At Price":
                row.get(
                    "Variant Compare At Price",
                    ""
                ),

            "Handle":
                str(
                    row.get("Handle", "")
                ).strip(),

            "Vendor":
                row.get(
                    "Vendor",
                    ""
                ),

            "Product Type":
                row.get(
                    "Type",
                    ""
                ),

            "Tags":
                row.get(
                    "Tags",
                    ""
                ),

            "Status":
                row.get(
                    "Status",
                    ""
                ),
        })

    my_all_df = pd.DataFrame(
        my_all_results
    )

    st.dataframe(
        my_all_df,
        use_container_width=True
    )

    # ==========================================
    # ALLE PRODUCTEN LOVELY DOTS
    # ==========================================

    st.header(
        "Alle producten - Lovely Dots"
    )

    lovelydots_all = [
        p for p in competitor_products
        if p["shop"] == "Lovely Dots"
    ]

    lovelydots_all_df = pd.DataFrame(
        lovelydots_all
    )

    st.dataframe(
        lovelydots_all_df,
        use_container_width=True
    )

    # ==========================================
    # ALLE PRODUCTEN CREA WITH GABY
    # ==========================================

    st.header(
        "Alle producten - Crea with Gaby"
    )

    gaby_all = [
        p for p in competitor_products
        if p["shop"] == "Crea with Gaby"
    ]

    gaby_all_df = pd.DataFrame(
        gaby_all
    )

    st.dataframe(
        gaby_all_df,
        use_container_width=True
    )

    # ==========================================
    # ALLE PRODUCTEN SAMES JOURNAL
    # ==========================================

    st.header(
        "Alle producten - Sames Journal"
    )

    sames_all = [
        p for p in competitor_products
        if p["shop"] == "Sames Journal"
    ]

    sames_all_df = pd.DataFrame(
        sames_all
    )

    st.dataframe(
        sames_all_df,
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
        f"export_producten_"
        f"{export_date}_"
        f"shopifyshops.xlsx"
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

        my_all_df.to_excel(
            writer,
            sheet_name="Eigen Producten",
            index=False
        )

        lovelydots_all_df.to_excel(
            writer,
            sheet_name="Lovely Dots",
            index=False
        )

        gaby_all_df.to_excel(
            writer,
            sheet_name="Crea with Gaby",
            index=False
        )

        sames_all_df.to_excel(
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