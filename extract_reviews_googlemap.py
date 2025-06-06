import streamlit as st
from serpapi.google_search import GoogleSearch
import pandas as pd
import re
from dotenv import load_dotenv
import os

load_dotenv('.env')

api_key = os.getenv("SERP_API_KEY")

def extract_data_id(url):
    """Extract data_id from Google Maps URL"""
    # This pattern should work with your specific URL
    pattern = r"!1s(0x[\w\d]+:0x[\w\d]+)"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def fetch_reviews(api_key, data_id, max_reviews=75):
    reviews = []
    params = {
        "engine": "google_maps_reviews",
        "data_id": data_id,
        "api_key": api_key,
        "hl": "en",
        "sort_by": "newestFirst"
    }

    try:
        page_count = 0
        while len(reviews) < max_reviews:
            page_count += 1
            search = GoogleSearch(params)
            results = search.get_dict()
            new_reviews = results.get("reviews", [])
            
            if not new_reviews:
                st.write(f"No more reviews found after page {page_count}")
                break
            
            reviews.extend(new_reviews)
            st.write(f"Page {page_count}: Found {len(new_reviews)} reviews. Total so far: {len(reviews)}")
            
            # Look specifically for the serpapi_pagination section
            if "serpapi_pagination" in results and "next_page_token" in results["serpapi_pagination"]:
                params["next_page_token"] = results["serpapi_pagination"]["next_page_token"]
                st.write("Found next_page_token, continuing to next page...")
            else:
                st.write("No next_page_token found in serpapi_pagination, stopping pagination")
                break
                
        return reviews[:max_reviews]
    except Exception as e:
        st.error(f"Error fetching reviews: {str(e)}")
        return []

def analyze_keywords(reviews, keywords):
    keyword_counts = {kw: 0 for kw in keywords}
    for review in reviews:
        text = review.get("snippet", "").lower()
        for kw in keywords:
            if kw.lower() in text:
                keyword_counts[kw] += 1
    total = len(reviews)
    if total == 0:
        return {kw: 0 for kw in keywords}
    analysis = {kw: (count / total) * 100 for kw, count in keyword_counts.items()}
    st.write(f"Raw counts: {keyword_counts}, Total reviews: {total}")
    return analysis

st.title("Google Maps Reviews Keyword Analyzer")
maps_url = st.text_input("Enter Google Maps URL of the business")
keywords_input = st.text_input("Enter keywords to search (comma-separated)")

if st.button("Analyze"):
    if not api_key or not maps_url or not keywords_input:
        st.error("Please provide all inputs.")
    else:
        data_id = extract_data_id(maps_url)
        if not data_id:
            st.error("Could not extract data_id from the URL. Please check the URL format.")
        else:
            keywords = [kw.strip() for kw in keywords_input.split(",")]
            with st.spinner("Fetching reviews..."):
                reviews = fetch_reviews(api_key, data_id)
            
            if reviews:
                st.success(f"Fetched {len(reviews)} reviews.")
                analysis = analyze_keywords(reviews, keywords)
                df = pd.DataFrame(list(analysis.items()), columns=["Keyword", "Mention Percentage"])
                df["Mention Percentage"] = df["Mention Percentage"].round(2)
                
                # Display results
                st.subheader("Analysis Results")
                st.dataframe(df)
                
                # Create a bar chart
                st.bar_chart(df.set_index("Keyword"))
                st.write(f"Extracted data_id: {data_id}")
            else:
                st.warning("No reviews found or unable to fetch reviews.")
