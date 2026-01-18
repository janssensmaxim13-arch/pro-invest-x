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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Platform Impact - Met CSS injection en Streamlit containers
    st.markdown("""
    <style>
    .impact-container {
        background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 30%, #C4B5FD 50%, #A78BFA 70%, #8B5CF6 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 10px 40px rgba(139, 92, 246, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .impact-title {
        text-align: center;
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .impact-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .impact-grid {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .impact-card {
        background: rgba(255,255,255,0.2);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        text-align: center;
        min-width: 150px;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .impact-icon {
        font-size: 2rem;
        margin-bottom: 0.3rem;
    }
    .impact-value {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .impact-label {
        color: rgba(255,255,255,0.9);
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .gold-container {
        background: linear-gradient(135deg, #D4AF37 0%, #F5D67B 25%, #D4AF37 50%, #F5D67B 75%, #D4AF37 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(212, 175, 55, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .gold-title {
        text-align: center;
        color: #1F2937;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .gold-subtitle {
        text-align: center;
        color: #374151;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .gold-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
    }
    @media (max-width: 768px) {
        .gold-grid {
            grid-template-columns: 1fr;
        }
    }
    .gold-card {
        background: rgba(255,255,255,0.25);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.4);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .gold-card-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .gold-card-title {
        color: #1F2937;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .gold-card-desc {
        color: #374151;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Nu de HTML met class names
    talents_label = t('landing_talents')
    diaspora_label = t('landing_diaspora')
    investment_label = t('landing_investment')
    dossiers_label = t('landing_dossiers')
    impact_title = t('landing_impact')
    impact_desc = t('landing_impact_desc')
    
    st.markdown(f'''<div class="impact-container">
<div class="impact-title">📊 {impact_title}</div>
<div class="impact-subtitle">{impact_desc}</div>
<div class="impact-grid">
<div class="impact-card"><div class="impact-icon">⚽</div><div class="impact-value">80,000+</div><div class="impact-label">{talents_label}</div></div>
<div class="impact-card"><div class="impact-icon">🌍</div><div class="impact-value">5.5M+</div><div class="impact-label">{diaspora_label}</div></div>
<div class="impact-card"><div class="impact-icon">💰</div><div class="impact-value">€2B+</div><div class="impact-label">{investment_label}</div></div>
<div class="impact-card"><div class="impact-icon">📁</div><div class="impact-value">33</div><div class="impact-label">{dossiers_label}</div></div>
</div>
</div>''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Platform Capabilities - Gouden Vakjes
    cap_title = t('landing_capabilities')
    cap_desc = t('landing_capabilities_desc')
    
    ntsp_title = t('landing_ntsp')
    ntsp_desc = t('landing_ntsp_desc')
    ticket_title = t('landing_ticketchain')
    ticket_desc = t('landing_ticketchain_desc')
    foundation_title = t('landing_foundation')
    foundation_desc = t('landing_foundation_desc')
    identity_title = t('landing_identity')
    identity_desc = t('landing_identity_desc')
    consulate_title = t('landing_consulate')
    consulate_desc = t('landing_consulate_desc')
    wallet_title = t('landing_wallet')
    wallet_desc = t('landing_wallet_desc')
    
    st.markdown(f'''<div class="gold-container">
<div class="gold-title">🏆 {cap_title}</div>
<div class="gold-subtitle">{cap_desc}</div>
<div class="gold-grid">
<div class="gold-card"><div class="gold-card-icon">🎯</div><div class="gold-card-title">{ntsp_title}</div><div class="gold-card-desc">{ntsp_desc}</div></div>
<div class="gold-card"><div class="gold-card-icon">🎫</div><div class="gold-card-title">{ticket_title}</div><div class="gold-card-desc">{ticket_desc}</div></div>
<div class="gold-card"><div class="gold-card-icon">🏦</div><div class="gold-card-title">{foundation_title}</div><div class="gold-card-desc">{foundation_desc}</div></div>
<div class="gold-card"><div class="gold-card-icon">🛡️</div><div class="gold-card-title">{identity_title}</div><div class="gold-card-desc">{identity_desc}</div></div>
<div class="gold-card"><div class="gold-card-icon">🏛️</div><div class="gold-card-title">{consulate_title}</div><div class="gold-card-desc">{consulate_desc}</div></div>
<div class="gold-card"><div class="gold-card-icon">💳</div><div class="gold-card-title">{wallet_title}</div><div class="gold-card-desc">{wallet_desc}</div></div>
</div>
</div>''', unsafe_allow_html=True)
    
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
