import streamlit as st
from app import scrape_flipkart_reviews, clean_review, summarize_reviews
import pandas as pd
import os

# -------------------- Streamlit Page Config --------------------
st.set_page_config(
    page_title="🛒 Flipkart Review Analyzer",
    page_icon="🧠",
    layout="wide"
)

# -------------------- Theme Toggle --------------------
theme = st.radio("🎨 Choose Theme", ["Light", "Dark"], horizontal=True)

def set_custom_style(theme):
    if theme == "Light":
        bg_color = "#f8f9fa"
        font_color = "#003366"
        button_color = "#ff4b4b"
        text_color = "#111111"
    else:
        bg_color = "#121212"
        font_color = "#90caf9"
        button_color = "#bb86fc"
        text_color = "#ffffff"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        h1, h2, h3 {{
            color: {font_color};
        }}
        .stButton > button {{
            background-color: {button_color};
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.5em 1.2em;
        }}
        .stDownloadButton > button {{
            background-color: #3a7ca5;
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }}
        .stTextInput > div > input {{
            border: 2px solid #4CAF50;
            border-radius: 6px;
            padding: 5px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_custom_style(theme)

# -------------------- Logo Section --------------------
# Use a hosted logo URL or local file (if available)
st.markdown("<h1 style='text-align: center;'>🧠 Flipkart Review Summarizer</h1>", unsafe_allow_html=True)
st.image("https://1000logos.net/wp-content/uploads/2021/06/Flipkart-logo.png", width=180, use_column_width=False)

st.markdown("Analyze product reviews, extract features, sentiment, FAQs, and download everything to Excel.")

# -------------------- URL Input --------------------
product_url = st.text_input("🔗 Enter Flipkart product URL:")

# -------------------- Start Button --------------------
if st.button("🚀 Start Analysis") and product_url:
    with st.spinner("Scraping reviews and generating summary..."):
        raw_reviews = scrape_flipkart_reviews(product_url, pages=5)

        if not raw_reviews:
            st.error("❌ No reviews found or scraping failed.")
        else:
            cleaned_reviews = [clean_review(r[2]) for r in raw_reviews]
            cleaned_text_block = "\n".join(cleaned_reviews[:30])
            summary = summarize_reviews(cleaned_text_block)

            df = pd.DataFrame(raw_reviews, columns=["Rating", "Title", "Review"])
            df["Cleaned Review"] = cleaned_reviews

            # Save to Excel
            os.makedirs("output", exist_ok=True)
            excel_path = "output/cleaned_reviews.xlsx"
            df.to_excel(excel_path, index=False)

            # Display summary
            st.markdown("### 🧠 Gemini Summary (6 Sections)")
            st.markdown(summary, unsafe_allow_html=True)

            # Table view
            with st.expander("📄 View Scraped Reviews Table"):
                st.dataframe(df, use_container_width=True)

            # Download button
            with open(excel_path, "rb") as f:
                st.download_button(
                    label="📥 Download Cleaned Reviews (Excel)",
                    data=f.read(),
                    file_name="cleaned_reviews.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            st.success("✅ Analysis complete!")

# -------------------- Footer --------------------
st.markdown("---")
st.markdown("🔧 Built using Streamlit, Gemini API, Selenium and BeautifulSoup.")
