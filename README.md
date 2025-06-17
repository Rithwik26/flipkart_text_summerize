# flipkart_text_summerize
An intelligent review summarization tool that scrapes customer reviews from Flipkart product pages and uses Gemini AI to generate structured, insightful summaries — including pros, cons, sentiment, and FAQs.

# 📌 Features
✅ Web scraping with Selenium & BeautifulSoup

🧠 AI summarization using Google Gemini API

📊 Review metadata extraction (rating, title, review)

📥 Excel download of raw + cleaned reviews

🎨 Branded Streamlit dashboard with Flipkart theme

🌗 Theme toggle: light/dark

🧼 Text preprocessing and noise removal


# 🧠 Gemini Summary Format
Gemini AI generates a 6-part structured summary:

Overall Sentiment Summary

Key Features Frequently Mentioned

Top 3 Recurring Pain Points

Aggregate Rating (Out of 5)

Pros and Cons

Frequently Asked Questions (FAQs)

# 🛠️ How It Works
User inputs a Flipkart product URL

Selenium scrapes reviews across pages

Reviews are cleaned and deduplicated

Gemini AI generates a summary from top reviews

Users can view, copy, or download results in Excel
