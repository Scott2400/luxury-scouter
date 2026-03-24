import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Cheap Bastard Luxury Monitor", layout="centered")

st.markdown("""
<style>
    .main .block-container { padding: 1.5rem 1rem 2rem 1rem; max-width: 900px; }
    h1 { font-size: clamp(1.4rem, 5vw, 2.2rem) !important; line-height: 1.2 !important; }
    .stButton button { background-color: #c8a96e; color: #1a1a1a; font-weight: 700; border-radius: 6px; width: 100%; }
    .stProgress > div > div { background-color: #c8a96e; }
</style>
""", unsafe_allow_html=True)

st.title("🏨 The Cheap Bastard Luxury Monitor")
st.markdown("**Targeting:** Four Seasons · Ritz-Carlton · St. Regis · Peninsula · Aman · Dorchester")
st.markdown("---")

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    check_in = st.date_input("Check-in Date")
with col2:
    check_out = st.date_input("Check-out Date")
with col3:
    st.write(""); st.write("")
    search_button = st.button("Scour the US")

HUBS = [
    "New York", "Los Angeles", "Chicago", "Miami", "Washington DC",
    "San Francisco", "Boston", "Dallas", "Houston", "Las Vegas",
    "Atlanta", "Seattle", "Denver", "Phoenix", "New Orleans",
    "Philadelphia", "Austin", "Nashville", "Orlando", "San Diego",
    "St. Louis", "Charleston", "Scottsdale", "Aspen", "Vail",
    "Honolulu", "Maui", "Palm Beach", "Beverly Hills", "Santa Barbara",
    "Napa", "Sonoma", "Monterey", "Portland", "Salt Lake City",
    "Minneapolis", "Detroit", "Cleveland", "Pittsburgh", "Baltimore",
    "Tampa", "Fort Lauderdale", "Sarasota", "Key West", "Savannah",
    "Charlotte", "Raleigh", "Richmond", "Memphis", "Louisville",
    "Indianapolis", "Kansas City", "Omaha", "Oklahoma City", "Tulsa",
    "Albuquerque", "Santa Fe", "Tucson", "El Paso", "San Antonio",
    "Baton Rouge", "Jackson Hole", "Telluride", "Park City", "Big Sur",
    "Laguna Beach", "Palm Springs", "Sedona", "Hilton Head", "Kiawah Island",
    "Nantucket", "Martha's Vineyard", "Newport", "Greenwich", "Kennebunkport",
]

TARGET_BRANDS = "33,67,101,114,168,215"
API_KEY = "4257d491048147452900c81ab345347673c7489131fc239bc138b30bb90a7d56"

if search_button:
    all_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, city in enumerate(HUBS):
        status_text.markdown(f"🔍 Searching **{city}**... ({i+1}/{len(HUBS)})")
        progress_bar.progress((i + 1) / len(HUBS))
        try:
            params = {
                "engine": "google_hotels", "q": f"luxury hotels in {city}",
                "check_in_date": str(check_in), "check_out_date": str(check_out),
                "brands": TARGET_BRANDS, "currency": "USD", "gl": "us", "api_key": API_KEY
            }
            res = requests.get("https://serpapi.com/search", params=params).json()
            for h in res.get('properties', []):
                all_results.append({
                    "Hotel": h.get('name'),
                    "Nightly Rate": h.get('rate_per_night', {}).get('lowest'),
                    "Total Stay": h.get('total_rate', {}).get('lowest'),
                    "City": city,
                    "Link": h.get('link') or h.get('serpapi_property_url') or ""
                })
        except: continue

    status_text.empty()
    progress_bar.empty()

    if all_results:
        df = pd.DataFrame(all_results)
        st.success(f"✅ {len(df)} hotels found across {len(HUBS)} cities")

        # This table allows you to click the column headers to sort!
        st.dataframe(
            df[['Hotel', 'Nightly Rate', 'Total Stay', 'City']],
            column_config={
                "Hotel": st.column_config.LinkColumn("Hotel", display_text=df['Hotel'], help="Click to view hotel"),
            },
            hide_index=True,
            use_container_width=True
        )

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Deals to CSV", data=csv, file_name="luxury_deals.csv")
    else:
        st.warning("No hotels found.")