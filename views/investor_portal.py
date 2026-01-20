# ============================================================================
# INVESTOR PORTAL - PROINVESTIX
# ============================================================================
# Dedicated page for investors with:
# - Investment overview
# - ROI projections
# - Partnership tiers
# - Financial highlights
# - Contact form
# ============================================================================

import streamlit as st
from datetime import datetime
from typing import Callable

try:
    from config import VERSION, LOGO_SHIELD
    from ui.styles import COLORS
except ImportError:
    VERSION = "5.1.2"
    LOGO_SHIELD = "assets/logo_shield.jpg"
    COLORS = {
        'purple_primary': '#8B5CF6',
        'purple_light': '#A78BFA',
        'gold': '#D4AF37',
        'text_primary': '#1F2937',
        'text_muted': '#94A3B8',
    }


def render_investor_portal(navigate_to: Callable):
    """Render the investor portal page."""
    
    # Header
    st.markdown(f"""
        <style>
            .investor-header {{
                background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                border: 1px solid rgba(212, 175, 55, 0.3);
                border-radius: 20px;
                padding: 3rem;
                text-align: center;
                margin-bottom: 2rem;
            }}
            
            .investor-title {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 2.5rem;
                font-weight: 700;
                color: {COLORS['gold']};
                margin-bottom: 0.5rem;
            }}
            
            .investor-subtitle {{
                font-family: 'Inter', sans-serif;
                color: {COLORS['text_muted']};
                font-size: 1.1rem;
            }}
            
            .investment-card {{
                background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(167, 139, 250, 0.15) 100%);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 16px;
                padding: 2rem;
                height: 100%;
            }}
            
            .tier-card {{
                background: linear-gradient(135deg, rgba(237, 233, 254, 0.8) 0%, rgba(245, 243, 255, 0.9) 100%);
                border: 2px solid rgba(139, 92, 246, 0.3);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                transition: all 0.3s ease;
            }}
            
            .tier-card:hover {{
                border-color: {COLORS['gold']};
                transform: translateY(-5px);
            }}
            
            .tier-card.featured {{
                border-color: {COLORS['gold']};
                background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            }}
            
            .tier-name {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: {COLORS['purple_light']};
                margin-bottom: 0.5rem;
            }}
            
            .tier-price {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 2.5rem;
                font-weight: 700;
                color: {COLORS['gold']};
            }}
            
            .tier-feature {{
                font-family: 'Inter', sans-serif;
                color: {COLORS['text_muted']};
                font-size: 0.9rem;
                padding: 0.5rem 0;
                border-bottom: 1px solid rgba(139, 92, 246, 0.1);
            }}
            
            .metric-highlight {{
                background: rgba(212, 175, 55, 0.1);
                border: 1px solid rgba(212, 175, 55, 0.3);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
            }}
            
            .metric-value {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 2.5rem;
                font-weight: 700;
                color: {COLORS['gold']};
            }}
            
            .metric-label {{
                font-family: 'Inter', sans-serif;
                color: {COLORS['text_muted']};
                font-size: 0.85rem;
            }}
            
            .section-header {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 1.8rem;
                font-weight: 700;
                color: {COLORS['text_primary']};
                margin: 2rem 0 1rem 0;
            }}
            
            /* MOBILE RESPONSIVE */
            @media (max-width: 1024px) {{
                .investor-header {{
                    padding: 2rem;
                }}
                .investor-title {{
                    font-size: 2rem;
                }}
                .tier-price {{
                    font-size: 2rem;
                }}
                .metric-value {{
                    font-size: 2rem;
                }}
            }}
            
            @media (max-width: 768px) {{
                .investor-header {{
                    padding: 1.5rem;
                    border-radius: 12px;
                }}
                .investor-title {{
                    font-size: 1.5rem;
                }}
                .investor-subtitle {{
                    font-size: 0.95rem;
                }}
                .investment-card {{
                    padding: 1.25rem;
                }}
                .tier-card {{
                    padding: 1.25rem;
                    margin-bottom: 1rem;
                }}
                .tier-name {{
                    font-size: 1.25rem;
                }}
                .tier-price {{
                    font-size: 1.75rem;
                }}
                .tier-feature {{
                    font-size: 0.85rem;
                }}
                .metric-highlight {{
                    padding: 1rem;
                }}
                .metric-value {{
                    font-size: 1.5rem;
                }}
                .section-header {{
                    font-size: 1.4rem;
                }}
            }}
            
            @media (max-width: 480px) {{
                .investor-header {{
                    padding: 1rem;
                }}
                .investor-title {{
                    font-size: 1.25rem;
                }}
                .tier-price {{
                    font-size: 1.5rem;
                }}
                .metric-value {{
                    font-size: 1.25rem;
                }}
            }}
        </style>
    """, unsafe_allow_html=True)
    
    # Back button
    col_back, col_space = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Home", key="investor_back"):
            navigate_to('landing')
    
    # Header
    st.markdown(f"""
        <div class="investor-header">
            <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
            <div class="investor-title">Investor Relations</div>
            <div class="investor-subtitle">
                Join the ProInvestiX ecosystem and be part of Morocco's national transformation
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # =========================================================================
    # KEY METRICS
    # =========================================================================
    
    st.markdown('<div class="section-header"> Investment Highlights</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("€2-3B", "Total Investment Scope", "2026-2035"),
        ("33", "Strategic Dossiers", "Fully Integrated"),
        ("5,5M+", "Diaspora Market", "Global Reach"),
        ("2030", "WK Morocco", "Catalyst Event"),
    ]
    
    for col, (value, label, sublabel) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
                <div class="metric-highlight">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                    <div style="color: {COLORS['purple_light']}; font-size: 0.75rem; margin-top: 0.25rem;">{sublabel}</div>
                </div>
            """, unsafe_allow_html=True)
    
    # =========================================================================
    # INVESTMENT THESIS
    # =========================================================================
    
    st.markdown('<div class="section-header"> Investment Thesis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div class="investment-card">
                <h3 style="color: {COLORS['gold']}; font-family: 'Rajdhani', sans-serif;"> Market Opportunity</h3>
                <ul style="color: {COLORS['text_muted']}; line-height: 2;">
                    <li><strong>WK 2030:</strong> Morocco co-hosts FIFA World Cup - massive infrastructure investment</li>
                    <li><strong>Diaspora:</strong> 5,5 million Moroccans abroad with €7B+ annual remittances</li>
                    <li><strong>Youth:</strong> 65% population under 35, football-obsessed nation</li>
                    <li><strong>Digital:</strong> 70%+ internet penetration, mobile-first market</li>
                    <li><strong>Government:</strong> Strong support for sports and digital transformation</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="investment-card">
                <h3 style="color: {COLORS['gold']}; font-family: 'Rajdhani', sans-serif;"> Revenue Streams</h3>
                <ul style="color: {COLORS['text_muted']}; line-height: 2;">
                    <li><strong>TicketChain™:</strong> 15% fee on €500M+ annual ticket market</li>
                    <li><strong>Transfers:</strong> 0.5% Foundation contribution on €200M+ transfers</li>
                    <li><strong>Subscriptions:</strong> B2B and B2C platform access fees</li>
                    <li><strong>Diaspora Wallet:</strong> Transaction fees on €7B remittance flow</li>
                    <li><strong>Data & Analytics:</strong> Premium insights for federations, clubs</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # PARTNERSHIP TIERS
    # =========================================================================
    
    st.markdown('<div class="section-header"> Partnership Tiers</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="tier-card">
                <div class="tier-name">SILVER</div>
                <div class="tier-price">€100K+</div>
                <div style="color: {COLORS['text_muted']}; margin: 1rem 0;">Entry Level Partner</div>
                <div class="tier-feature"> Platform Access</div>
                <div class="tier-feature"> Quarterly Reports</div>
                <div class="tier-feature"> Logo on Website</div>
                <div class="tier-feature"> 5 Event Tickets/Year</div>
                <div class="tier-feature"> Board Observer</div>
                <div class="tier-feature"> Strategic Input</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="tier-card featured">
                <div style="background: {COLORS['gold']}; color: #1a0a2e; padding: 0.25rem 1rem; 
                            border-radius: 20px; font-size: 0.75rem; font-weight: 600; 
                            display: inline-block; margin-bottom: 1rem;">RECOMMENDED</div>
                <div class="tier-name" style="color: {COLORS['gold']};">GOLD</div>
                <div class="tier-price">€500K+</div>
                <div style="color: {COLORS['text_muted']}; margin: 1rem 0;">Strategic Partner</div>
                <div class="tier-feature"> Everything in Silver</div>
                <div class="tier-feature"> Monthly Reports</div>
                <div class="tier-feature"> Premium Branding</div>
                <div class="tier-feature"> 25 Event Tickets/Year</div>
                <div class="tier-feature"> Board Observer Seat</div>
                <div class="tier-feature"> Strategic Input</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="tier-card">
                <div class="tier-name">DIAMOND</div>
                <div class="tier-price">€2M+</div>
                <div style="color: {COLORS['text_muted']}; margin: 1rem 0;">Founding Partner</div>
                <div class="tier-feature"> Everything in Gold</div>
                <div class="tier-feature"> Weekly Updates</div>
                <div class="tier-feature"> Exclusive Branding</div>
                <div class="tier-feature"> VIP Event Access</div>
                <div class="tier-feature"> Board Seat</div>
                <div class="tier-feature"> Strategic Input</div>
            </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # PROJECTED RETURNS
    # =========================================================================
    
    st.markdown('<div class="section-header"> Projected Returns (5-Year)</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="investment-card">
                <h4 style="color: {COLORS['text_muted']};">Conservative</h4>
                <div style="font-size: 2rem; color: {COLORS['text_primary']}; font-weight: 700;">12-15%</div>
                <div style="color: {COLORS['text_muted']}; font-size: 0.85rem;">Annual ROI</div>
                <br>
                <div style="color: {COLORS['text_muted']}; font-size: 0.8rem;">
                    Based on ticket sales and basic subscription revenue only
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="investment-card" style="border-color: {COLORS['gold']};">
                <h4 style="color: {COLORS['gold']};">Realistic</h4>
                <div style="font-size: 2rem; color: {COLORS['gold']}; font-weight: 700;">20-25%</div>
                <div style="color: {COLORS['text_muted']}; font-size: 0.85rem;">Annual ROI</div>
                <br>
                <div style="color: {COLORS['text_muted']}; font-size: 0.8rem;">
                    Including diaspora wallet adoption and transfer fees
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="investment-card">
                <h4 style="color: {COLORS['text_muted']};">Optimistic</h4>
                <div style="font-size: 2rem; color: {COLORS['text_primary']}; font-weight: 700;">35-40%</div>
                <div style="color: {COLORS['text_muted']}; font-size: 0.85rem;">Annual ROI</div>
                <br>
                <div style="color: {COLORS['text_muted']}; font-size: 0.8rem;">
                    Full ecosystem adoption with WK 2030 catalyst effect
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # =========================================================================
    # CONTACT FORM
    # =========================================================================
    
    st.markdown('<div class="section-header"> Get in Touch</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("investor_contact"):
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Full Name *")
                email = st.text_input("Email *")
            with col_b:
                company = st.text_input("Company/Organization")
                investment_range = st.selectbox("Investment Interest", [
                    "Select range...",
                    "€100K - €500K (Silver)",
                    "€500K - €2M (Gold)",
                    "€2M+ (Diamond)",
                    "Strategic Partnership",
                    "Just Exploring"
                ])
            
            message = st.text_area("Message", placeholder="Tell us about your interest in ProInvestiX...")
            
            if st.form_submit_button(" Send Inquiry", width='stretch'):
                if name and email:
                    st.success(" Thank you! Our investor relations team will contact you within 48 hours.")
                    st.balloons()
                else:
                    st.error("Please fill in required fields.")
    
    with col2:
        st.markdown(f"""
            <div class="investment-card">
                <h4 style="color: {COLORS['gold']};"> Direct Contact</h4>
                <br>
                <div style="color: {COLORS['text_muted']}; margin-bottom: 1rem;">
                    <strong>Investor Relations</strong><br>
                    investors@proinvestix.ma
                </div>
                <div style="color: {COLORS['text_muted']}; margin-bottom: 1rem;">
                    <strong>General Inquiries</strong><br>
                    info@proinvestix.ma
                </div>
                <div style="color: {COLORS['text_muted']};">
                    <strong>Headquarters</strong><br>
                    Casablanca, Morocco 
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(139, 92, 246, 0.2);">
            <div style="color: {COLORS['text_muted']}; font-size: 0.8rem;">
                ProInvestiX v{VERSION} | Investor Portal | Confidential
            </div>
        </div>
    """, unsafe_allow_html=True)
