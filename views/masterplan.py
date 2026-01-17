# ============================================================================
# MASTERPLAN SHOWCASE - PROINVESTIX
# ============================================================================
# Complete overview of all 33 Masterplan dossiers
# ============================================================================

import streamlit as st
from typing import Callable

try:
    from config import VERSION
    from ui.styles import COLORS
except ImportError:
    VERSION = "5.1.2"
    COLORS = {
        'purple_primary': '#8B5CF6',
        'purple_light': '#A78BFA',
        'gold': '#D4AF37',
        'text_primary': '#1F2937',
        'text_muted': '#94A3B8',
    }


# ============================================================================
# MASTERPLAN DATA
# ============================================================================

MASTERPLAN_DOSSIERS = {
    "Sport & Talent": [
        {"id": 1, "name": "Sport Division & NTSP™", "icon": "", "budget": "€50M", 
         "desc": "National Talent Scouting Platform met 80.000+ spelers tracking, AI-evaluatie, en career management."},
        {"id": 2, "name": "Transfer Management", "icon": "", "budget": "€10M",
         "desc": "Smart Contract transfers met FIFA compliance, solidariteitsbijdragen, en 0.5% Foundation."},
        {"id": 3, "name": "Academy Network", "icon": "", "budget": "€100M",
         "desc": "250 gecertificeerde academies in 12 regio's met jeugdopleiding en doorstroming."},
        {"id": 4, "name": "Women's Football", "icon": "", "budget": "€25M",
         "desc": "Dedicated programma voor vrouwenvoetbal met eigen competitie en nationale team support."},
        {"id": 5, "name": "Paralympics Division", "icon": "", "budget": "€15M",
         "desc": "Inclusief sportprogramma voor para-atleten met aangepaste faciliteiten."},
    ],
    "Financial Ecosystem": [
        {"id": 6, "name": "TicketChain™ Blockchain", "icon": "", "budget": "€30M",
         "desc": "Fraudebestendige ticketing met blockchain verificatie en QR-authenticatie."},
        {"id": 7, "name": "Foundation Bank", "icon": "️", "budget": "€20M",
         "desc": "0.5% automatische bijdrage op alle transacties - Sadaka Jaaria principe."},
        {"id": 8, "name": "Fiscal Framework", "icon": "", "budget": "€5M",
         "desc": "Belastingcompliance en transparante financiële rapportage aan overheid."},
        {"id": 9, "name": "Diaspora Wallet™", "icon": "", "budget": "€40M",
         "desc": "Digitale wallet voor 5,5M diaspora met investeringsmogelijkheden en loyalty."},
        {"id": 10, "name": "Subscription Platform", "icon": "", "budget": "€10M",
         "desc": "B2B en B2C abonnementen voor platform toegang en premium features."},
    ],
    "Diaspora Services": [
        {"id": 11, "name": "Digital Consulate Hub™", "icon": "️", "budget": "€35M",
         "desc": "Complete consulaire diensten: documenten, beurzen, en emergency support."},
        {"id": 12, "name": "Global Return Program", "icon": "", "budget": "€20M",
         "desc": "Reïntegratie programma voor terugkerende diaspora met job matching."},
        {"id": 13, "name": "Talent Reclamation", "icon": "", "budget": "€15M",
         "desc": "Identificatie en recruitment van diaspora talent voor nationale teams."},
        {"id": 14, "name": "Fandorp Network", "icon": "", "budget": "€10M",
         "desc": "Wereldwijd netwerk van supporter hubs voor Marokkaanse communities."},
    ],
    "Identity & Security": [
        {"id": 15, "name": "Identity Shield™", "icon": "️", "budget": "€25M",
         "desc": "24/7 AI-powered identiteitsbescherming en fraud detectie."},
        {"id": 16, "name": "Anti-Hate Shield", "icon": "", "budget": "€10M",
         "desc": "Content filtering en bescherming tegen online haat en discriminatie."},
        {"id": 17, "name": "Fraud Detection AI", "icon": "", "budget": "€15M",
         "desc": "Machine learning systeem voor real-time fraude preventie."},
        {"id": 18, "name": "GDPR Compliance", "icon": "", "budget": "€5M",
         "desc": "Volledige privacy compliance met Europese en Marokkaanse wetgeving."},
    ],
    "Health & Social": [
        {"id": 19, "name": "Hayat Health Initiative", "icon": "", "budget": "€50M",
         "desc": "Nationaal gezondheidsprogramma met medische screening en mentale support."},
        {"id": 20, "name": "Mental Health Support", "icon": "", "budget": "€15M",
         "desc": "Psychologische begeleiding voor atleten en families."},
        {"id": 21, "name": "Education Foundation", "icon": "", "budget": "€30M",
         "desc": "Beurzen en opleidingen voor talent zonder sportcarrière."},
    ],
    "Mobility & Events": [
        {"id": 22, "name": "WK 2030 Travel Hub", "icon": "️", "budget": "€100M",
         "desc": "Complete reisoplossingen voor WK bezoekers met transport en accommodatie."},
        {"id": 23, "name": "VIP Transport Services", "icon": "", "budget": "€25M",
         "desc": "Premium transport voor officials, investeerders, en VIP gasten."},
        {"id": 24, "name": "ProInvestiX Air", "icon": "️", "budget": "€200M",
         "desc": "Charter vluchten en partnerships met airlines voor events."},
        {"id": 25, "name": "Aïd Al Wahda Festival", "icon": "", "budget": "€20M",
         "desc": "Jaarlijks nationaal eenheidsfestival met sport en cultuur."},
    ],
    "Industry & Infrastructure": [
        {"id": 26, "name": "Phosphate Partnership", "icon": "️", "budget": "€500M",
         "desc": "OCP samenwerking voor industriële ontwikkeling en export."},
        {"id": 27, "name": "Sahara Development", "icon": "️", "budget": "€300M",
         "desc": "Infrastructuur en toerisme ontwikkeling in zuidelijke provincies."},
        {"id": 28, "name": "Energy & Sustainability", "icon": "", "budget": "€250M",
         "desc": "Groene energie projecten en duurzame stadions."},
        {"id": 29, "name": "Tech Hub Morocco", "icon": "", "budget": "€100M",
         "desc": "IT innovatie centrum en startup incubator."},
    ],
    "Media & Communication": [
        {"id": 30, "name": "Global Media Powerhouse", "icon": "", "budget": "€75M",
         "desc": "Eigen mediakanalen en content productie voor wereldwijd bereik."},
        {"id": 31, "name": "Digital Marketing Hub", "icon": "", "budget": "€20M",
         "desc": "Social media en digitale campagnes voor brand awareness."},
        {"id": 32, "name": "E-Sports Division", "icon": "", "budget": "€30M",
         "desc": "Competitive gaming met nationale teams en tournaments."},
    ],
    "Governance": [
        {"id": 33, "name": "Legal Framework", "icon": "️", "budget": "€10M",
         "desc": "Juridische structuur en compliance met internationale standaarden."},
    ],
}


def render_masterplan_page(navigate_to: Callable):
    """Render the masterplan showcase page."""
    
    st.markdown(f"""
        <style>
            .masterplan-header {{
                background: linear-gradient(135deg, rgba(237, 233, 254, 0.6) 0%, rgba(245, 243, 255, 0.8) 100%);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 20px;
                padding: 3rem;
                text-align: center;
                margin-bottom: 2rem;
            }}
            
            .dossier-card {{
                background: linear-gradient(135deg, #EDE9FE 0%, #F5F3FF 100%);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            }}
            
            .dossier-card:hover {{
                border-color: {COLORS['gold']};
                transform: translateX(5px);
            }}
            
            .dossier-id {{
                background: rgba(139, 92, 246, 0.2);
                color: {COLORS['purple_light']};
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.75rem;
                font-weight: 600;
            }}
            
            .dossier-name {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 1.2rem;
                font-weight: 600;
                color: {COLORS['text_primary']};
                margin: 0.5rem 0;
            }}
            
            .dossier-budget {{
                color: {COLORS['gold']};
                font-weight: 600;
                font-size: 1rem;
            }}
            
            .dossier-desc {{
                color: {COLORS['text_muted']};
                font-size: 0.9rem;
                line-height: 1.5;
            }}
            
            .category-header {{
                font-family: 'Rajdhani', sans-serif;
                font-size: 1.5rem;
                font-weight: 700;
                color: {COLORS['gold']};
                margin: 2rem 0 1rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid rgba(212, 175, 55, 0.3);
            }}
            
            .total-budget {{
                background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                border: 1px solid rgba(212, 175, 55, 0.3);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                margin: 2rem 0;
            }}
            
            /* MOBILE RESPONSIVE */
            @media (max-width: 768px) {{
                .masterplan-header {{
                    padding: 1.5rem;
                    border-radius: 12px;
                }}
                .dossier-card {{
                    padding: 1rem;
                }}
                .dossier-name {{
                    font-size: 1rem;
                }}
                .dossier-desc {{
                    font-size: 0.85rem;
                }}
                .category-header {{
                    font-size: 1.25rem;
                }}
                .total-budget {{
                    padding: 1.5rem;
                }}
            }}
            
            @media (max-width: 480px) {{
                .masterplan-header {{
                    padding: 1rem;
                }}
                .dossier-card {{
                    padding: 0.75rem;
                }}
                .dossier-name {{
                    font-size: 0.95rem;
                }}
                .dossier-budget {{
                    font-size: 0.9rem;
                }}
            }}
        </style>
    """, unsafe_allow_html=True)
    
    # Back button
    col_back, col_space = st.columns([1, 5])
    with col_back:
        if st.button("← Back to Home", key="masterplan_back"):
            navigate_to('landing')
    
    # Header
    st.markdown(f"""
        <div class="masterplan-header">
            <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
            <div style="font-family: 'Rajdhani', sans-serif; font-size: 2.5rem; font-weight: 700; color: {COLORS['text_primary']};">
                Masterplan 2026-2050
            </div>
            <div style="color: {COLORS['text_muted']}; font-size: 1.1rem; margin-top: 0.5rem;">
                33 Strategic Dossiers for Morocco's National Transformation
            </div>
            <div style="color: {COLORS['purple_light']}; font-size: 0.9rem; margin-top: 1rem;">
                "We work FOR Morocco, WITH Morocco" - Building a lasting legacy
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Total Budget
    total_budget = 0
    for category, dossiers in MASTERPLAN_DOSSIERS.items():
        for d in dossiers:
            budget_str = d['budget'].replace('€', '').replace('M', '')
            try:
                total_budget += float(budget_str)
            except:
                pass
    
    st.markdown(f"""
        <div class="total-budget">
            <div style="color: {COLORS['text_muted']}; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 2px;">
                Total Investment Scope
            </div>
            <div style="font-family: 'Rajdhani', sans-serif; font-size: 3rem; font-weight: 700; color: {COLORS['gold']};">
                €{total_budget/1000:.1f}B+
            </div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.85rem;">
                Across 33 integrated dossiers | 2026-2050 timeline
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Filter
    categories = ["All Categories"] + list(MASTERPLAN_DOSSIERS.keys())
    selected_category = st.selectbox("Filter by Category", categories)
    
    # Dossiers display
    if selected_category == "All Categories":
        display_categories = MASTERPLAN_DOSSIERS
    else:
        display_categories = {selected_category: MASTERPLAN_DOSSIERS[selected_category]}
    
    for category, dossiers in display_categories.items():
        st.markdown(f'<div class="category-header">{category}</div>', unsafe_allow_html=True)
        
        # Two columns for dossiers
        col1, col2 = st.columns(2)
        
        for i, dossier in enumerate(dossiers):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                st.markdown(f"""
                    <div class="dossier-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="dossier-id">Dossier {dossier['id']}</span>
                            <span class="dossier-budget">{dossier['budget']}</span>
                        </div>
                        <div class="dossier-name">
                            {dossier['icon']} {dossier['name']}
                        </div>
                        <div class="dossier-desc">
                            {dossier['desc']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    # Timeline
    st.markdown(f"""
        <div class="category-header"> Implementation Timeline</div>
    """, unsafe_allow_html=True)
    
    timeline_data = [
        ("2026", "Foundation", "Core platform launch, NTSP™ activation, TicketChain™ deployment"),
        ("2027-2028", "Expansion", "Academy network rollout, Diaspora Wallet™ launch, regional hubs"),
        ("2029", "WK Preparation", "Full infrastructure ready, travel hub activation, security systems"),
        ("2030", "WK 2030", "World Cup Morocco - Platform at full capacity, global showcase"),
        ("2031-2035", "Growth", "International expansion, new revenue streams, foundation maturity"),
        ("2036-2050", "Legacy", "Self-sustaining ecosystem, continuous impact, next generation"),
    ]
    
    for year, phase, desc in timeline_data:
        st.markdown(f"""
            <div style="display: flex; margin-bottom: 1rem; padding: 1rem; 
                        background: #EDE9FE; border-radius: 8px;
                        border-left: 3px solid {COLORS['gold']};">
                <div style="min-width: 100px; font-weight: 700; color: {COLORS['gold']};">{year}</div>
                <div style="min-width: 120px; color: {COLORS['purple_light']}; font-weight: 600;">{phase}</div>
                <div style="color: {COLORS['text_muted']};">{desc}</div>
            </div>
        """, unsafe_allow_html=True)
    
    # CTA
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(" Investor Portal", width="stretch", key="mp_investor"):
            navigate_to('investor_portal')
    
    with col2:
        if st.button(" Login to Platform", width="stretch", key="mp_login"):
            navigate_to('login')
    
    with col3:
        if st.button(" Back to Home", width="stretch", key="mp_home"):
            navigate_to('landing')
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(139, 92, 246, 0.2);">
            <div style="color: {COLORS['text_muted']}; font-size: 0.8rem;">
                ProInvestiX v{VERSION} | Masterplan Documentation | Morocco 
            </div>
        </div>
    """, unsafe_allow_html=True)
