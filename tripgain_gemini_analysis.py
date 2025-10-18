import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ============== CONFIGURATION ==============
URL = "https://en.wikipedia.org/wiki/Artificial_intelligence"   # can change to BBC or CNN
OUTPUT_FILE = "summary_output.txt"

# ============== STEP 1: Gemini Setup ==============
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found. Please set it as an environment variable.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# ============== STEP 2: Fetch and Clean Webpage ==============
def fetch_and_clean(url):
    print(f"📡 Fetching webpage: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    # Remove scripts, styles, nav, footer
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)
    return clean_text

# ============== STEP 3: Build Prompt ==============
def build_prompt(content):
    prompt = f"""
You are an AI research assistant. Analyze the following webpage content related to technology, business, or society.

TASK:
1. Read and understand the key points from the content.
2. Summarize the core ideas in **3 to 5 clear bullet points**.
3. After the summary, provide exactly **one line of analytical insight** that interprets the overall trend, theme, or implication.
4. Keep the summary neutral, factual, and concise.
5. Use this exact structure in your answer:

Summary:
• <point 1>
• <point 2>
• <point 3>
• <point 4>
• <point 5>
Insight:
<one-line insight>

CONTENT STARTS BELOW:
---------------------
{content}
---------------------
"""
    return prompt

# ============== STEP 4: Send to Gemini ==============
def analyze_with_gemini(text):
    prompt = build_prompt(text)
    response = model.generate_content(prompt)
    return response.text.strip()

# ============== STEP 5: Save Output ==============
def save_output(result):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"\n✅ Summary and Insight saved to {OUTPUT_FILE}")

# ============== MAIN SCRIPT ==============
if __name__ == "__main__":
    try:
        cleaned_text = fetch_and_clean(URL)
        gemini_result = analyze_with_gemini(cleaned_text)
        print("\n" + gemini_result)  # Print in exact format
        save_output(gemini_result)
    except Exception as e:
        print(f"❌ Error: {e}")
