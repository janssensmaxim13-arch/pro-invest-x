# ============================================================================
# PROINVESTIX LANDING PAGE - STREAMLIT NATIVE VERSION
# ============================================================================
# Gebruikt Streamlit componenten in plaats van ruwe HTML om rendering
# problemen te voorkomen
# ============================================================================

import streamlit as st
from datetime import datetime
from typing import Callable

try:
    from config import VERSION
except ImportError:
    VERSION = "5.4.1"


def get_wk2030_countdown():
    """Calculate days until WK 2030 opening match."""
    wk_date = datetime(2030, 6, 13)
    today = datetime.now()
    delta = wk_date - today
    
    years = delta.days // 365
    remaining_days = delta.days % 365
    months = remaining_days // 30
    
    return {
        'total_days': delta.days,
        'years': years,
        'months': months,
    }


def render_landing_page(navigate_to: Callable):
    """Render the public landing page using Streamlit native components."""
    
    countdown = get_wk2030_countdown()
    
    # Custom CSS voor de pagina
    st.markdown("""
        <style>
        .landing-badge {
            background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
            color: #1F2937;
            padding: 10px 25px;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.9rem;
            display: inline-block;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
        }
        .landing-title {
            color: #4C1D95;
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            margin: 0;
        }
        .landing-subtitle {
            color: #7C3AED;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 4px;
            text-align: center;
        }
        .landing-desc {
            color: #6B7280;
            font-size: 1.1rem;
            text-align: center;
        }
        .countdown-number {
            color: #D4AF37;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .countdown-label {
            color: #6B7280;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .feature-title {
            color: #4C1D95;
            font-weight: 600;
        }
        .feature-desc {
            color: #6B7280;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # WK 2030 Badge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><span class="landing-badge"> OFFICIAL WK 2030 PARTNER</span></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # Hero Section
    st.markdown('<p class="landing-subtitle">National Investment Platform</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="landing-title">PROINVESTI<span style="color: #8B5CF6;">X</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="landing-desc">Building Morocco\'s Future Through Sport, Technology & Diaspora Connection</p>', unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Countdown met gouden achtergrond
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #D4AF37 0%, #F4E5B2 50%, #D4AF37 100%);
            border: 2px solid #B8860B;
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin: 1rem 0;
            box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
        '>
            <div style='text-align: center; margin-bottom: 1rem;'>
                <span style='color: #1F2937; font-size: 1.2rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;'>WK 2030 Countdown</span>
            </div>
            <div style='display: flex; justify-content: center; gap: 3rem;'>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 3rem; font-weight: 700;'>{countdown['total_days']:,}</div>
                    <div style='color: #4B5563; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;'>Days</div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 3rem; font-weight: 700;'>{countdown['years']}</div>
                    <div style='color: #4B5563; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;'>Years</div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 3rem; font-weight: 700;'>{countdown['months']}</div>
                    <div style='color: #4B5563; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;'>Months</div>
                </div>
            </div>
            <div style='text-align: center; margin-top: 1rem;'>
                <span style='color: #4B5563; font-size: 0.9rem;'>Until WK 2030 Opening Ceremony</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Platform Impact
    st.subheader(" Platform Impact")
    st.caption("Real-time statistics from the ProInvestiX ecosystem")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label=" Talents Tracked", value="80,000+")
    with col2:
        st.metric(label=" Diaspora Connected", value="5,5M+")
    with col3:
        st.metric(label=" Investment Potential", value="€2B+")
    with col4:
        st.metric(label="📁 Integrated Dossiers", value="33")
    
    st.divider()
    
    # Platform Capabilities
    st.subheader(" Platform Capabilities")
    st.caption("Comprehensive national infrastructure for sport, economy & identity")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("###  NTSP™ Talent Scouting")
            st.write("AI-powered national talent identification system tracking 80,000+ players.")
        
        with st.container(border=True):
            st.markdown("###  TicketChain™ Blockchain")
            st.write("Fraud-proof ticketing system with blockchain verification.")
    
    with col2:
        with st.container(border=True):
            st.markdown("###  Foundation Bank")
            st.write("Automated 0.5% contribution. Sadaka Jaaria - continuous charity.")
        
        with st.container(border=True):
            st.markdown("###  Identity Shield™")
            st.write("24/7 AI-powered identity protection and fraud detection.")
    
    with col3:
        with st.container(border=True):
            st.markdown("###  Digital Consulate Hub™")
            st.write("Complete diaspora services: documents, scholarships, assistance.")
        
        with st.container(border=True):
            st.markdown("###  Diaspora Wallet™")
            st.write("Digital financial identity for the global Moroccan community.")
    
    st.divider()
    
    # CTA Section
    st.subheader(" Join the Movement")
    st.info("**\"We work FOR Morocco, WITH Morocco\"** - Building a lasting legacy through sport, technology, and the power of 5,5 million diaspora members worldwide.")
    
    # CTA Buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(" Investor Portal", width="stretch", key="cta_investor"):
            navigate_to('investor_portal')
    
    with col2:
        if st.button(" Full Masterplan", width="stretch", key="cta_masterplan"):
            navigate_to('masterplan')
    
    with col3:
        if st.button(" Login", width="stretch", key="cta_login"):
            navigate_to('login')
    
    with col4:
        if st.button(" Register", width="stretch", key="cta_register"):
            navigate_to('register')
    
    # Footer
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 1.5rem; margin-bottom: 10px;">
                    <span style="color: #4C1D95;">PROINVESTI</span><span style="color: #8B5CF6;">X</span>
                </div>
                <div style="color: #6B7280; font-size: 0.85rem;">
                    National Investment Platform | Morocco 
                </div>
                <div style="color: #9CA3AF; font-size: 0.75rem; margin-top: 5px;">
                    v{VERSION} ULTIMATE | Enterprise Ready | WK 2030 Partner
                </div>
                <div style="margin-top: 10px; color: #7C3AED; font-size: 0.8rem;">
                    صدقة جارية - Sadaka Jaaria - Continuous Charity
                </div>
            </div>
        """, unsafe_allow_html=True)
