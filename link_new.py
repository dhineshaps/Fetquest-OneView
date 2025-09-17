import streamlit as st
import requests

st.title("TalentScout")

# --- Access secrets ---
# api_keys = st.secrets["google"]["api_keys"]  # List of API keys
# cx = st.secrets["google"]["cx"]

api_keys = "AIzaSyByJUQSEB2ofihGylvJujbUg-pGS9ToGeE"
cx = "32207faa631794d44"

query = st.text_input(
    "Search Query",
    placeholder="Python Developer Bengaluru"
).strip()

queryx = query
@st.cache_data(ttl=3600)
def fetch_results(query, api_key, cx):
    all_results = []
    for start in range(1, 101, 10):  
        test_query = f'site:linkedin.com/in "site:linkedin.com/in {query}"'
        params = {"key": api_keys, "cx": cx, "q": test_query, "num": 10, "start": start}
        try:
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 429:
                st.warning("Daily quota exceeded for the current API key. Try again tomorrow or use another key.")
                break
            else:
                st.error(f"HTTP Error: {response.status_code} - {response.text}")
                break
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {e}")
            break
        
        items = response.json().get("items", [])
        if not items:
            break
        all_results.extend(items)
    return all_results

if st.button("Search"):
    if not query:
        st.error("Please enter a query")
    else:
        st.write("Searching for:", f'site:linkedin.com/in "site:linkedin.com/in {query}"')
        
        import random
        api_key = random.choice(api_keys)
        
        results = fetch_results(query, api_key, cx)
        
        if not results:
            st.warning("No results found or quota exceeded.")
        else:
            st.success(f"Found {len(results)} results")
            for i, item in enumerate(results, start=1):
                st.subheader(f"{i}. {item.get('title')}")
                st.write(item.get("link"))
                snippet = item.get("snippet", "")
                if snippet:
                    st.write(snippet)
