"""
ProInvestiX - Travel & Mobility Module v2.0
FIXED VERSION - No database errors
"""

import streamlit as st
from datetime import datetime, date
import random

MOROCCAN_CITIES = ["Casablanca", "Rabat", "Marrakech", "Tangier", "Fes", "Agadir"]

TRANSPORT_TYPES = [
    {"type": "Economy Shuttle", "price_km": 2, "capacity": 20},
    {"type": "Premium Shuttle", "price_km": 4, "capacity": 12},
    {"type": "VIP Transfer", "price_km": 15, "capacity": 4},
]

WK2030_PACKAGES = [
    {"name": "WK2030 Basic", "price": 2500, "duration": "7 days"},
    {"name": "WK2030 Premium", "price": 7500, "duration": "10 days"},
    {"name": "WK2030 VIP", "price": 25000, "duration": "14 days"},
]

def render(username=None):
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FFFFFF 0%, #16213e 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>🚗 Travel & Mobility</h1>
        <p style='color: #888;'>WK2030 Travel Services</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["📦 Packages", "🚌 Shuttle", "🚘 VIP Transfer"])
    
    with tabs[0]:
        st.subheader("WK 2030 Travel Packages")
        wk_start = datetime(2030, 6, 13)
        days_until = (wk_start - datetime.now()).days
        st.metric("Days to WK2030", days_until)
        
        for pkg in WK2030_PACKAGES:
            st.markdown(f"### {pkg['name']}")
            st.markdown(f"**{pkg['duration']}** - **{pkg['price']:,} MAD**")
            if st.button("Book", key=f"book_{pkg['name']}"):
                st.success("Booked!")
            st.markdown("---")
    
    with tabs[1]:
        st.subheader("Shuttle Services")
        pickup = st.selectbox("From", MOROCCAN_CITIES)
        dropoff = st.selectbox("To", MOROCCAN_CITIES, key="to")
        shuttle_type = st.selectbox("Type", [t['type'] for t in TRANSPORT_TYPES])
        if st.button("Book Shuttle"):
            st.success(f"Shuttle booked! Ref: SHT-{random.randint(10000,99999)}")
    
    with tabs[2]:
        st.subheader("VIP Transfer")
        vehicle = st.selectbox("Vehicle", ["Mercedes S-Class", "BMW 7 Series", "Range Rover"])
        pickup_loc = st.text_input("Pickup Location")
        if st.button("Book VIP"):
            st.success(f"VIP Transfer booked! Ref: VIP-{random.randint(1000,9999)}")
