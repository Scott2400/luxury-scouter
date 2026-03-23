import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Luxury Rate Scouter", layout="wide")

st.title("🏨 The 'Cheap Bastard' Luxury Monitor")
st.subheader("Targeting: Four Seasons, Ritz, St. Regis, Peninsula, Aman, and Dorchester")

# 2. Sidebar Settings (Hard-coded API Key)
with st.sidebar:
    st.write("### Search Settings")
    # Scott's Secret Key
    api_key = "4257d491048147452900c81ab345347673c7489131fc239bc138b30bb90a7d56"
    check_in = st.date_input("Check-in Date")
    check_out = st.date_input("Check-out Date")
    search_button = st.button("Scour the US")

# 3. The Search Engine
if search_button:
    # Major US hubs for luxury value
    hubs = ["St. Louis", "Los Angeles", "Washington DC", "Houston", "Chicago", "Miami", "Seattle", "Atlanta"]
    all_results = []
    
    # Brand IDs for Scott's favorites
    TARGET_BRANDS = "33,67,101,114,168,215" 
    
    with st.spinner("Scouring for deals... this takes a moment..."):
        for city in hubs:
            url = "https://serpapi.com/search"
            params = {
                "engine": "google_hotels",
                "q": f"luxury hotels in {city}",
                "check_in_date": str(check_in),
                "check_out_date": str(check_out),
                "brands": TARGET_BRANDS,
                "currency": "USD",
                "gl": "us",
                "api_key": api_key
            }
            try:
                res = requests.get(url, params=params).json()
                for h in res.get('properties', []):
                    # We only want to keep the brands Scott actually likes
                    all_results.append({
                        "Hotel": h.get('name'),
                        "Nightly Rate": h.get('rate_per_night', {}).get('lowest'),
                        "Total Stay": h.get('total_rate', {}).get('lowest'),
                        "City": city
                    })
            except:
                continue

    if all_results:
        df = pd.DataFrame(all_results)
        
        # Clean pricing for sorting (Handle N/A as $9999)
        df['Nightly Rate'] = df['Nightly Rate'].fillna('$9999').astype(str)
        # Convert string price to a number we can actually sort and compare
        df['Price_Num'] = df['Nightly Rate'].str.replace('$', '').str.replace(',', '').replace('None', '9999').astype(float)
        df = df.sort_values(by='Price_Num')
        
        # The "Cheap Bastard" Highlight (Green if under $550)
        def highlight_deals(val):
            return 'background-color: #90ee90; color: black;' if 0 < val < 550.0 else ''
        
        st.success("Search Complete!")
        # Display the table with the highlight applied to the price column
        st.dataframe(df.style.applymap(highlight_deals, subset=['Price_Num']), use_container_width=True)
        
        # Download button for Scott's records
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Deals to CSV", data=csv, file_name="luxury_deals.csv")
    else:
        st.warning("No hotels found. Try different dates.")