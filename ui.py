import streamlit as st
import pandas as pd

from io import BytesIO
from datetime import datetime

from competitor_fetcher import fetch_all_products
from matcher import find_matches


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Competitor Pricing Tool",
    layout="wide"
)

st.title("Shopify Competitor Comparison Tool")

st.write(
    "Vergelijk jouw Shopify CSV export "
    "of bekijk alleen concurrenten"
)

# ==========================================
# MODE SELECTIE
# ==========================================

mode = st.radio(

    "Kies modus",

    [
        "Vergelijk met eigen CSV",
        "Alleen concurrenten bekijken"
    ]
)

# ==========================================
# CSV IMPORT
# ==========================================

uploaded_file = None

if mode == "Vergelijk met eigen CSV":

    uploaded_file = st.file_uploader(
        "Upload Shopify Product CSV",
        type=["csv"]
    )

# ==========================================
# START BUTTON
# ==========================================

start_clicked = st.button(
    "Start"
)

if (
    (
        mode == "Vergelijk met eigen CSV"
        and uploaded_file
        and start_clicked
    )
    or
    (
        mode == "Alleen concurrenten bekijken"
        and start_clicked
    )
):

    # ==========================================
    # EIGEN PRODUCTEN INLADEN
    # ==========================================

    my_products = []
    my_df = pd.DataFrame()

    if mode == "Vergelijk met eigen CSV":

        my_df = pd.read_csv(
            uploaded_file
        )

        my_df = my_df[
            my_df["Variant Price"].notna()
        ]

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
                full_title += (
                    f" - {variant_title}"
                )

            try:

                price = float(
                    row.get(
                        "Variant Price",
                        0
                    )
                )

            except:

                price = 0

            my_products.append({

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
                        row.get(
                            "Variant SKU",
                            ""
                        )
                    ).strip(),

                "handle":
                    str(
                        row.get(
                            "Handle",
                            ""
                        )
                    ).strip(),
            })

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

    matches = []
    unmatched = []

    if mode == "Vergelijk met eigen CSV":

        with st.spinner(
            "Producten vergelijken..."
        ):

            (
                matches,
                unmatched,
                unmatched_competitors

            ) = find_matches(

                my_products,
                competitor_products
            )

    else:

        unmatched_competitors = (
            competitor_products
        )

    # ==========================================
    # MATCHES
    # ==========================================

    if mode == "Vergelijk met eigen CSV":

        st.header(
            "Gematchte producten"
        )

        matched_results = []

        for match in matches:

            price_difference = round(

                match["my_price"]
                - match["competitor_price"],

                2
            )

            matched_results.append({

                "Mijn Full Titel":
                    match[
                        "my_full_title"
                    ],

                "Mijn SKU":
                    match["my_sku"],

                "Mijn Handle":
                    match[
                        "my_handle"
                    ],

                "Mijn Prijs":
                    match["my_price"],

                "Concurrent Shop":
                    match[
                        "competitor_shop"
                    ],

                "Concurrent Full Titel":
                    match[
                        "competitor_full_title"
                    ],

                "Concurrent SKU":
                    match[
                        "competitor_sku"
                    ],

                "Concurrent Handle":
                    match[
                        "competitor_handle"
                    ],

                "Concurrent Prijs":
                    match[
                        "competitor_price"
                    ],

                "Prijsverschil":
                    price_difference,

                "Match Type":
                    match[
                        "match_type"
                    ],

                "Match Score":
                    match["score"],
            })

        matched_df = pd.DataFrame(
            matched_results
        )

        st.success(
            f"{len(matched_df)} "
            f"matches gevonden"
        )

        st.dataframe(
            matched_df,
            use_container_width=True
        )

    else:

        matched_df = pd.DataFrame()

    # ==========================================
    # EIGEN PRODUCTEN ZONDER MATCH
    # ==========================================

    if mode == "Vergelijk met eigen CSV":

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

    else:

        unmatched_df = pd.DataFrame()

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

    st.header(
        "Excel Export"
    )

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

        if mode == (
            "Vergelijk met eigen CSV"
        ):

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