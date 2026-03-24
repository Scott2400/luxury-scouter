import streamlit as st
import requests
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Cheap Bastard Luxury Monitor", layout="centered")

# Custom CSS for mobile-friendliness and visual polish
st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding: 1.5rem 1rem 2rem 1rem;
        max-width: 900px;
    }

    /* Title styling */
    h1 {
        font-size: clamp(1.4rem, 5vw, 2.2rem) !important;
        line-height: 1.2 !important;
    }
    h3 {
        font-size: clamp(0.9rem, 3vw, 1.1rem) !important;
    }

    /* Date inputs and button - stack nicely on mobile */
    .search-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        align-items: flex-end;
        margin-bottom: 1.25rem;
    }

    /* Make dataframe links clickable */
    a {
        color: #1a6b3c;
        text-decoration: none;
        font-weight: 500;
    }
    a:hover { text-decoration: underline; }

    /* Download button */
    .stDownloadButton button {
        background-color: #1a1a1a;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.25rem;
        font-size: 0.9rem;
    }

    /* Search button */
    .stButton button {
        background-color: #c8a96e;
        color: #1a1a1a;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        padding: 0.55rem 1.5rem;
        font-size: 1rem;
        width: 100%;
    }

    /* Progress text */
    .stProgress > div > div {
        background-color: #c8a96e;
    }
</style>
""", unsafe_allow_html=True)

# 2. Header
st.title("🏨 The 'Cheap Bastard' Luxury Monitor")
st.markdown("**Targeting:** Four Seasons · Ritz-Carlton · St. Regis · Peninsula · Aman · Dorchester")
st.markdown("---")

# 3. Search Controls (inline, no sidebar — mobile friendly)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    check_in = st.date_input("Check-in Date")
with col2:
    check_out = st.date_input("Check-out Date")
with col3:
    st.write("")
    st.write("")
    search_button = st.button("Scour the US")

# 4. City List — 75 cities
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

# 5. Brand IDs
TARGET_BRANDS = "33,67,101,114,168,215"
API_KEY = "4257d491048147452900c81ab345347673c7489131fc239bc138b30bb90a7d56"

# 6. Search Logic
if search_button:
    all_results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, city in enumerate(HUBS):
        status_text.markdown(f"🔍 Searching **{city}**... ({i+1}/{len(HUBS)})")
        progress_bar.progress((i + 1) / len(HUBS))

        url = "https://serpapi.com/search"
        params = {
            "engine": "google_hotels",
            "q": f"luxury hotels in {city}",
            "check_in_date": str(check_in),
            "check_out_date": str(check_out),
            "brands": TARGET_BRANDS,
            "currency": "USD",
            "gl": "us",
            "api_key": API_KEY
        }
        try:
            res = requests.get(url, params=params).json()
            for h in res.get('properties', []):
                link = h.get('link') or h.get('serpapi_property_url') or ""
                name = h.get('name', '')
                all_results.append({
                    "Hotel": f'<a href="{link}" target="_blank">{name}</a>' if link else name,
                    "Hotel_Name": name,  # plain text for sorting/CSV
                    "Nightly Rate": h.get('rate_per_night', {}).get('lowest'),
                    "Total Stay": h.get('total_rate', {}).get('lowest'),
                    "City": city,
                    "Link": link,
                })
        except:
            continue

    status_text.empty()
    progress_bar.empty()

    if all_results:
        df = pd.DataFrame(all_results)

        # Clean pricing
        df['Nightly Rate'] = df['Nightly Rate'].fillna('$9999').astype(str)
        df['Price_Num'] = (
            df['Nightly Rate']
            .str.replace('$', '', regex=False)
            .str.replace(',', '', regex=False)
            .replace('None', '9999')
            .astype(float)
        )
        df = df.sort_values(by='Price_Num').reset_index(drop=True)

        # Display table — show Hotel as HTML link, hide Price_Num and helper cols
        display_df = df[['Hotel', 'Nightly Rate', 'Total Stay', 'City']].copy()

        def highlight_deals(val):
            try:
                num = float(
                    str(val).replace('$', '').replace(',', '')
                )
                return 'background-color: #d4edda; color: #1a3a1a;' if 0 < num < 550 else ''
            except:
                return ''

        st.success(f"✅ Search complete — {len(df)} hotels found across {len(HUBS)} cities")

        st.write(
            display_df.style
            .applymap(highlight_deals, subset=['Nightly Rate'])
            .to_html(escape=False),
            unsafe_allow_html=True
        )

        # CSV uses plain text hotel names
        csv_df = df[['Hotel_Name', 'Nightly Rate', 'Total Stay', 'City', 'Link']].copy()
        csv_df.columns = ['Hotel', 'Nightly Rate', 'Total Stay', 'City', 'Link']
        csv = csv_df.to_csv(index=False).encode('utf-8')
        st.markdown("---")
        st.download_button("⬇️ Download Deals to CSV", data=csv, file_name="luxury_deals.csv")

    else:
        st.warning("No hotels found for those dates. Try different dates or check your API quota.")