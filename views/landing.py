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

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())


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
        st.markdown(f'<div style="text-align: center;"><span class="landing-badge"> {t("landing_badge")}</span></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # Hero Section
    st.markdown(f'<p class="landing-subtitle">{t("landing_subtitle")}</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="landing-title">PROINVESTI<span style="color: #8B5CF6;">X</span></h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="landing-desc">{t("landing_description")}</p>', unsafe_allow_html=True)
    
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
                <span style='color: #1F2937; font-size: 1.2rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;'>{t("landing_countdown_title")}</span>
            </div>
            <div style='display: flex; justify-content: center; gap: 3rem;'>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 3rem; font-weight: 700;'>{countdown['total_days']:,}</div>
                    <div style='color: #4B5563; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;'>{t("landing_days")}</div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 3rem; font-weight: 700;'>{countdown['years']}</div>
                    <div style='color: #4B5563; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;'>{t("landing_years")}</div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 3rem; font-weight: 700;'>{countdown['months']}</div>
                    <div style='color: #4B5563; font-size: 0.85rem; text-transform: uppercase; font-weight: 500;'>{t("landing_months")}</div>
                </div>
            </div>
            <div style='text-align: center; margin-top: 1rem;'>
                <span style='color: #4B5563; font-size: 0.9rem;'>{t("landing_until_ceremony")}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Platform Impact
    st.subheader(f" {t('landing_impact')}")
    st.caption(t("landing_impact_desc"))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label=f" {t('landing_talents')}", value="80,000+")
    with col2:
        st.metric(label=f" {t('landing_diaspora')}", value="5,5M+")
    with col3:
        st.metric(label=f" {t('landing_investment')}", value="€2B+")
    with col4:
        st.metric(label=f"📁 {t('landing_dossiers')}", value="33")
    
    st.divider()
    
    # Platform Capabilities
    st.subheader(f" {t('landing_capabilities')}")
    st.caption(t("landing_capabilities_desc"))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown(f"###  {t('landing_ntsp')}")
            st.write(t("landing_ntsp_desc"))
        
        with st.container(border=True):
            st.markdown(f"###  {t('landing_ticketchain')}")
            st.write(t("landing_ticketchain_desc"))
    
    with col2:
        with st.container(border=True):
            st.markdown(f"###  {t('landing_foundation')}")
            st.write(t("landing_foundation_desc"))
        
        with st.container(border=True):
            st.markdown(f"###  {t('landing_identity')}")
            st.write(t("landing_identity_desc"))
    
    with col3:
        with st.container(border=True):
            st.markdown(f"###  {t('landing_consulate')}")
            st.write(t("landing_consulate_desc"))
        
        with st.container(border=True):
            st.markdown(f"###  {t('landing_wallet')}")
            st.write(t("landing_wallet_desc"))
    
    st.divider()
    
    # CTA Section
    st.subheader(f" {t('landing_join')}")
    st.info(t("landing_join_desc"))
    
    # CTA Buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f" {t('landing_investor_portal')}", use_container_width=True, key="cta_investor"):
            navigate_to('investor_portal')
    
    with col2:
        if st.button(f" {t('landing_masterplan')}", use_container_width=True, key="cta_masterplan"):
            navigate_to('masterplan')
    
    with col3:
        if st.button(f" {t('login')}", use_container_width=True, key="cta_login"):
            navigate_to('login')
    
    with col4:
        if st.button(f" {t('register')}", use_container_width=True, key="cta_register"):
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
                    {t("landing_footer_platform")} 
                </div>
                <div style="color: #9CA3AF; font-size: 0.75rem; margin-top: 5px;">
                    v{VERSION} {t("landing_footer_version")}
                </div>
                <div style="margin-top: 10px; color: #7C3AED; font-size: 0.8rem;">
                    {t("landing_sadaka")}
                </div>
            </div>
        """, unsafe_allow_html=True)
