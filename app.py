import os
import re
import time
import nltk
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai

# ---------------- Setup ----------------
nltk.download('stopwords')
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# ---------------- Web Scraper ----------------
def scrape_flipkart_reviews(product_url, pages=5):
    options = Options()
    options.add_argument('--headless')  # comment this if you want to see the browser
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    driver.get(product_url)

    reviews = []

    # ❌ Try to close login pop-up
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'✕')]"))
        )
        close_btn.click()
        print("🔒 Closed pop-up.")
    except:
        pass

    # ✅ Click on 'View All Reviews' button
    try:
        review_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, '_23J90q')]"))
        )
        review_btn.click()
        print("Clicked on 'View All Reviews' on product page.")
        time.sleep(3)
    except:
        print("⚠️ Could not click 'All reviews' button.")

    for page in range(10):
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "ZmyHeo"))
            )
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_blocks = soup.find_all("div", class_="ZmyHeo")
            rating_blocks = soup.find_all("div", class_="XQDdHH")
            title_blocks = soup.find_all("p", class_="z9E0IG")

            for i, block in enumerate(review_blocks):
                try:
                    review_text = block.find("div").get_text(strip=True)
                    rating = rating_blocks[i].get_text(strip=True) if i < len(rating_blocks) else "N/A"
                    title = title_blocks[i].get_text(strip=True) if i < len(title_blocks) else "N/A"
                    reviews.append([rating, title, review_text])
                except:
                    continue

            print(f"✅ Scraped page {page + 1}")

            # 🔁 Try clicking the "Next" button using JavaScript
            try:
                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(3)
            except Exception as e:
                print(f"🔴 Couldn't click Next: {e}")
                break

        except Exception as e:
            print(f"🔴 Stopped at page {page + 1}: {e}")
            break

    driver.quit()
    return reviews

# ---------------- Preprocessing ----------------
def clean_review(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = text.lower()
    text = " ".join(word for word in text.split() if word not in stopwords.words('english'))
    return text

# ---------------- Gemini Summarization ----------------
def summarize_reviews(cleaned_text_block):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")  # ✅ Correct model usage

        prompt = f"""
        You are a professional AI assistant that analyzes customer reviews and returns a structured summary for e-commerce decision-making.

        Your task is to read the customer reviews provided below and generate a complete report in **exactly 6 numbered sections** as shown. 
        You **must return all 6 sections**. Do not skip or omit any section. If the data is missing, infer or explain based on the available content.

        ---

        💡 **Follow this exact format:**

        1. **Overall Sentiment Summary**  
        - Describe the general customer sentiment (positive, negative, or mixed) and why.

        2. **Key Features Frequently Mentioned**  
        - List the most mentioned features. Use bullet points.

        3. **Top 3 Recurring Pain Points**  
        - List exactly 3 specific complaints or issues from users.

        4. **Aggregate Rating (Out of 5)**  
        - Give a realistic score like 4.1 / 5 based on all reviews.

        5. **Pros and Cons**  
        - Two sections:
            - Pros: ✅ Bulleted list of advantages  
            - Cons: ❌ Bulleted list of disadvantages

        6. **Frequently Asked Questions (FAQs)**  
        - Generate 3–5 buyer questions based on the reviews.

        ---

        🔒 **Important Rules:**
        - Format exactly in 6 sections using the numbers above.
        - Use bold section titles.
        - If any section is missing from your answer, your response is invalid.
        - You must complete all 6 sections before ending your response.

        ---

        ### Customer Reviews:
        \"\"\"
        {cleaned_text_block}
        \"\"\"
        """


        print("📋 Generating summary with Gemini...")
        response = model.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"⚠️ Error generating summary: {e}"

# ---------------- Main ----------------
if __name__ == "__main__":
    url = input("🔗 Enter Flipkart product URL: ")
    raw_reviews = scrape_flipkart_reviews(url, pages=5)

    if raw_reviews:
        cleaned_reviews = [clean_review(r[2]) for r in raw_reviews]
        cleaned_text_block = "\n".join(cleaned_reviews[:30])  # Max 30 reviews for prompt

        print("\n📋 Generating summary with Gemini...")
        summary = summarize_reviews(cleaned_text_block)
        print("\n🧠 Summary:\n")
        print(summary)

        df = pd.DataFrame(raw_reviews, columns=["Rating", "Title", "Review"])
        df["Cleaned Review"] = cleaned_reviews
        os.makedirs("output", exist_ok=True)
        df.to_excel("output/cleaned_reviews.xlsx", index=False)
        print("\n✅ Reviews saved to 'output/cleaned_reviews.xlsx'")
    else:
        print("❌ No reviews scraped.")