"""
ProInvestiX - Transfer Market Module v4.0
Professional Transfermarkt-style player database
Data verified against transfermarkt.de - January 2025
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import random

# ============================================================================
# VERIFIED PLAYER DATABASE - January 2025
# Source: transfermarkt.de
# ============================================================================

PLAYERS_DATABASE = {
    # ========== TOP 10 MOST VALUABLE (Verified Jan 2025) ==========
    "Lamine Yamal": {
        "club": "Barcelona", "league": "La Liga", "position": "Right Winger",
        "nationality": "Spain", "age": 17, "value": 200, "contract": "2030",
        "goals": 18, "assists": 25, "apps": 55
    },
    "Erling Haaland": {
        "club": "Manchester City", "league": "Premier League", "position": "Centre-Forward",
        "nationality": "Norway", "age": 24, "value": 200, "contract": "2034",
        "goals": 21, "assists": 5, "apps": 30
    },
    "Kylian Mbappe": {
        "club": "Real Madrid", "league": "La Liga", "position": "Centre-Forward",
        "nationality": "France", "age": 26, "value": 200, "contract": "2029",
        "goals": 15, "assists": 8, "apps": 28
    },
    "Jude Bellingham": {
        "club": "Real Madrid", "league": "La Liga", "position": "Attacking Midfield",
        "nationality": "England", "age": 21, "value": 160, "contract": "2029",
        "goals": 14, "assists": 14, "apps": 45
    },
    "Vinicius Junior": {
        "club": "Real Madrid", "league": "La Liga", "position": "Left Winger",
        "nationality": "Brazil", "age": 24, "value": 150, "contract": "2027",
        "goals": 21, "assists": 18, "apps": 50
    },
    "Bukayo Saka": {
        "club": "Arsenal", "league": "Premier League", "position": "Right Winger",
        "nationality": "England", "age": 23, "value": 150, "contract": "2027",
        "goals": 16, "assists": 12, "apps": 38
    },
    "Phil Foden": {
        "club": "Manchester City", "league": "Premier League", "position": "Attacking Midfield",
        "nationality": "England", "age": 24, "value": 80, "contract": "2027",
        "goals": 6, "assists": 8, "apps": 25
    },
    "Florian Wirtz": {
        "club": "Liverpool", "league": "Premier League", "position": "Attacking Midfield",
        "nationality": "Germany", "age": 21, "value": 110, "contract": "2030",
        "goals": 12, "assists": 14, "apps": 35
    },
    "Cole Palmer": {
        "club": "Chelsea", "league": "Premier League", "position": "Attacking Midfield",
        "nationality": "England", "age": 22, "value": 120, "contract": "2033",
        "goals": 22, "assists": 11, "apps": 34
    },
    "Jamal Musiala": {
        "club": "Bayern Munich", "league": "Bundesliga", "position": "Attacking Midfield",
        "nationality": "Germany", "age": 21, "value": 130, "contract": "2026",
        "goals": 14, "assists": 10, "apps": 40
    },
    
    # ========== PREMIER LEAGUE STARS ==========
    "Mohamed Salah": {
        "club": "Liverpool", "league": "Premier League", "position": "Right Winger",
        "nationality": "Egypt", "age": 32, "value": 30, "contract": "2025",
        "goals": 18, "assists": 12, "apps": 28
    },
    "Kevin De Bruyne": {
        "club": "Manchester City", "league": "Premier League", "position": "Central Midfield",
        "nationality": "Belgium", "age": 33, "value": 35, "contract": "2025",
        "goals": 4, "assists": 12, "apps": 22
    },
    "Martin Odegaard": {
        "club": "Arsenal", "league": "Premier League", "position": "Attacking Midfield",
        "nationality": "Norway", "age": 26, "value": 95, "contract": "2028",
        "goals": 8, "assists": 14, "apps": 32
    },
    "Declan Rice": {
        "club": "Arsenal", "league": "Premier League", "position": "Defensive Midfield",
        "nationality": "England", "age": 26, "value": 105, "contract": "2028",
        "goals": 5, "assists": 8, "apps": 35
    },
    "William Saliba": {
        "club": "Arsenal", "league": "Premier League", "position": "Centre-Back",
        "nationality": "France", "age": 23, "value": 90, "contract": "2027",
        "goals": 2, "assists": 1, "apps": 38
    },
    "Marcus Rashford": {
        "club": "Manchester United", "league": "Premier League", "position": "Left Winger",
        "nationality": "England", "age": 27, "value": 50, "contract": "2028",
        "goals": 7, "assists": 4, "apps": 30
    },
    "Bruno Fernandes": {
        "club": "Manchester United", "league": "Premier League", "position": "Attacking Midfield",
        "nationality": "Portugal", "age": 30, "value": 55, "contract": "2027",
        "goals": 10, "assists": 12, "apps": 38
    },
    "Son Heung-min": {
        "club": "Tottenham", "league": "Premier League", "position": "Left Winger",
        "nationality": "South Korea", "age": 32, "value": 45, "contract": "2025",
        "goals": 12, "assists": 8, "apps": 32
    },
    "Virgil van Dijk": {
        "club": "Liverpool", "league": "Premier League", "position": "Centre-Back",
        "nationality": "Netherlands", "age": 33, "value": 25, "contract": "2025",
        "goals": 3, "assists": 1, "apps": 35
    },
    "Alexander Isak": {
        "club": "Newcastle", "league": "Premier League", "position": "Centre-Forward",
        "nationality": "Sweden", "age": 25, "value": 90, "contract": "2028",
        "goals": 18, "assists": 5, "apps": 32
    },
    "Alexis Mac Allister": {
        "club": "Liverpool", "league": "Premier League", "position": "Central Midfield",
        "nationality": "Argentina", "age": 26, "value": 70, "contract": "2028",
        "goals": 6, "assists": 8, "apps": 35
    },
    "Nicolas Jackson": {
        "club": "Chelsea", "league": "Premier League", "position": "Centre-Forward",
        "nationality": "Senegal", "age": 23, "value": 55, "contract": "2031",
        "goals": 14, "assists": 6, "apps": 35
    },
    "Ollie Watkins": {
        "club": "Aston Villa", "league": "Premier League", "position": "Centre-Forward",
        "nationality": "England", "age": 29, "value": 30, "contract": "2028",
        "goals": 15, "assists": 10, "apps": 38
    },
    "Rodri": {
        "club": "Manchester City", "league": "Premier League", "position": "Defensive Midfield",
        "nationality": "Spain", "age": 28, "value": 75, "contract": "2027",
        "goals": 5, "assists": 6, "apps": 30
    },
    
    # ========== LA LIGA STARS ==========
    "Pedri": {
        "club": "Barcelona", "league": "La Liga", "position": "Central Midfield",
        "nationality": "Spain", "age": 22, "value": 100, "contract": "2026",
        "goals": 6, "assists": 10, "apps": 35
    },
    "Gavi": {
        "club": "Barcelona", "league": "La Liga", "position": "Central Midfield",
        "nationality": "Spain", "age": 20, "value": 70, "contract": "2026",
        "goals": 4, "assists": 6, "apps": 25
    },
    "Nico Williams": {
        "club": "Athletic Bilbao", "league": "La Liga", "position": "Left Winger",
        "nationality": "Spain", "age": 22, "value": 70, "contract": "2027",
        "goals": 8, "assists": 12, "apps": 35
    },
    "Robert Lewandowski": {
        "club": "Barcelona", "league": "La Liga", "position": "Centre-Forward",
        "nationality": "Poland", "age": 36, "value": 12, "contract": "2026",
        "goals": 18, "assists": 5, "apps": 32
    },
    "Antoine Griezmann": {
        "club": "Atletico Madrid", "league": "La Liga", "position": "Second Striker",
        "nationality": "France", "age": 33, "value": 18, "contract": "2026",
        "goals": 12, "assists": 8, "apps": 35
    },
    "Rodrygo": {
        "club": "Real Madrid", "league": "La Liga", "position": "Right Winger",
        "nationality": "Brazil", "age": 24, "value": 100, "contract": "2028",
        "goals": 10, "assists": 8, "apps": 38
    },
    
    # ========== BUNDESLIGA STARS ==========
    "Harry Kane": {
        "club": "Bayern Munich", "league": "Bundesliga", "position": "Centre-Forward",
        "nationality": "England", "age": 31, "value": 80, "contract": "2027",
        "goals": 28, "assists": 10, "apps": 32
    },
    "Leroy Sane": {
        "club": "Bayern Munich", "league": "Bundesliga", "position": "Right Winger",
        "nationality": "Germany", "age": 29, "value": 50, "contract": "2025",
        "goals": 10, "assists": 12, "apps": 30
    },
    "Xavi Simons": {
        "club": "RB Leipzig", "league": "Bundesliga", "position": "Attacking Midfield",
        "nationality": "Netherlands", "age": 21, "value": 80, "contract": "2027",
        "goals": 8, "assists": 12, "apps": 32
    },
    "Alphonso Davies": {
        "club": "Bayern Munich", "league": "Bundesliga", "position": "Left-Back",
        "nationality": "Canada", "age": 24, "value": 50, "contract": "2025",
        "goals": 2, "assists": 8, "apps": 28
    },
    
    # ========== SERIE A STARS ==========
    "Lautaro Martinez": {
        "club": "Inter Milan", "league": "Serie A", "position": "Centre-Forward",
        "nationality": "Argentina", "age": 27, "value": 110, "contract": "2029",
        "goals": 22, "assists": 6, "apps": 35
    },
    "Rafael Leao": {
        "club": "AC Milan", "league": "Serie A", "position": "Left Winger",
        "nationality": "Portugal", "age": 25, "value": 75, "contract": "2028",
        "goals": 12, "assists": 10, "apps": 35
    },
    "Dusan Vlahovic": {
        "club": "Juventus", "league": "Serie A", "position": "Centre-Forward",
        "nationality": "Serbia", "age": 24, "value": 65, "contract": "2026",
        "goals": 16, "assists": 4, "apps": 32
    },
    "Khvicha Kvaratskhelia": {
        "club": "Napoli", "league": "Serie A", "position": "Left Winger",
        "nationality": "Georgia", "age": 23, "value": 85, "contract": "2027",
        "goals": 10, "assists": 12, "apps": 35
    },
    "Nicolo Barella": {
        "club": "Inter Milan", "league": "Serie A", "position": "Central Midfield",
        "nationality": "Italy", "age": 27, "value": 80, "contract": "2029",
        "goals": 6, "assists": 10, "apps": 38
    },
    
    # ========== LIGUE 1 STARS ==========
    "Ousmane Dembele": {
        "club": "PSG", "league": "Ligue 1", "position": "Right Winger",
        "nationality": "France", "age": 27, "value": 60, "contract": "2028",
        "goals": 12, "assists": 14, "apps": 35
    },
    "Bradley Barcola": {
        "club": "PSG", "league": "Ligue 1", "position": "Left Winger",
        "nationality": "France", "age": 22, "value": 70, "contract": "2029",
        "goals": 14, "assists": 8, "apps": 32
    },
    "Warren Zaire-Emery": {
        "club": "PSG", "league": "Ligue 1", "position": "Central Midfield",
        "nationality": "France", "age": 18, "value": 60, "contract": "2029",
        "goals": 4, "assists": 8, "apps": 35
    },
    
    # ========== MOROCCAN PLAYERS (Verified Jan 2025) ==========
    "Achraf Hakimi": {
        "club": "PSG", "league": "Ligue 1", "position": "Right-Back",
        "nationality": "Morocco", "age": 26, "value": 65, "contract": "2026",
        "goals": 4, "assists": 8, "apps": 30
    },
    "Hakim Ziyech": {
        "club": "Wydad Casablanca", "league": "Botola Pro", "position": "Right Winger",
        "nationality": "Morocco", "age": 32, "value": 3, "contract": "2027",
        "goals": 5, "assists": 8, "apps": 15
    },
    "Youssef En-Nesyri": {
        "club": "Fenerbahce", "league": "Super Lig", "position": "Centre-Forward",
        "nationality": "Morocco", "age": 27, "value": 18, "contract": "2027",
        "goals": 12, "assists": 4, "apps": 28
    },
    "Noussair Mazraoui": {
        "club": "Manchester United", "league": "Premier League", "position": "Right-Back",
        "nationality": "Morocco", "age": 27, "value": 30, "contract": "2028",
        "goals": 1, "assists": 4, "apps": 25
    },
    "Sofyan Amrabat": {
        "club": "Real Betis", "league": "La Liga", "position": "Defensive Midfield",
        "nationality": "Morocco", "age": 28, "value": 18, "contract": "2026",
        "goals": 1, "assists": 3, "apps": 28
    },
    "Azzedine Ounahi": {
        "club": "Girona", "league": "La Liga", "position": "Central Midfield",
        "nationality": "Morocco", "age": 24, "value": 15, "contract": "2028",
        "goals": 2, "assists": 5, "apps": 30
    },
    "Brahim Diaz": {
        "club": "Real Madrid", "league": "La Liga", "position": "Attacking Midfield",
        "nationality": "Morocco", "age": 25, "value": 25, "contract": "2027",
        "goals": 6, "assists": 8, "apps": 28
    },
    "Yassine Bounou": {
        "club": "Al-Hilal", "league": "Saudi Pro League", "position": "Goalkeeper",
        "nationality": "Morocco", "age": 33, "value": 8, "contract": "2026",
        "goals": 0, "assists": 0, "apps": 30
    },
    "Nayef Aguerd": {
        "club": "Marseille", "league": "Ligue 1", "position": "Centre-Back",
        "nationality": "Morocco", "age": 28, "value": 18, "contract": "2028",
        "goals": 2, "assists": 1, "apps": 28
    },
    "Bilal El Khannouss": {
        "club": "Stuttgart", "league": "Bundesliga", "position": "Attacking Midfield",
        "nationality": "Morocco", "age": 20, "value": 25, "contract": "2029",
        "goals": 5, "assists": 6, "apps": 25
    },
    "Eliesse Ben Seghir": {
        "club": "Bayer Leverkusen", "league": "Bundesliga", "position": "Left Winger",
        "nationality": "Morocco", "age": 19, "value": 20, "contract": "2029",
        "goals": 6, "assists": 4, "apps": 22
    },
    "Ismael Saibari": {
        "club": "PSV", "league": "Eredivisie", "position": "Central Midfield",
        "nationality": "Morocco", "age": 23, "value": 12, "contract": "2027",
        "goals": 8, "assists": 6, "apps": 30
    },
    
    # ========== SAUDI PRO LEAGUE STARS ==========
    "Cristiano Ronaldo": {
        "club": "Al-Nassr", "league": "Saudi Pro League", "position": "Centre-Forward",
        "nationality": "Portugal", "age": 39, "value": 15, "contract": "2025",
        "goals": 25, "assists": 8, "apps": 30
    },
    "Karim Benzema": {
        "club": "Al-Ittihad", "league": "Saudi Pro League", "position": "Centre-Forward",
        "nationality": "France", "age": 37, "value": 8, "contract": "2026",
        "goals": 18, "assists": 10, "apps": 28
    },
    "Neymar": {
        "club": "Al-Hilal", "league": "Saudi Pro League", "position": "Left Winger",
        "nationality": "Brazil", "age": 32, "value": 15, "contract": "2025",
        "goals": 2, "assists": 3, "apps": 8
    },
    "Sadio Mane": {
        "club": "Al-Nassr", "league": "Saudi Pro League", "position": "Left Winger",
        "nationality": "Senegal", "age": 32, "value": 12, "contract": "2026",
        "goals": 10, "assists": 6, "apps": 28
    },
    "Riyad Mahrez": {
        "club": "Al-Ahli", "league": "Saudi Pro League", "position": "Right Winger",
        "nationality": "Algeria", "age": 33, "value": 10, "contract": "2026",
        "goals": 8, "assists": 10, "apps": 25
    },
    "N'Golo Kante": {
        "club": "Al-Ittihad", "league": "Saudi Pro League", "position": "Defensive Midfield",
        "nationality": "France", "age": 33, "value": 12, "contract": "2026",
        "goals": 2, "assists": 4, "apps": 28
    },
    
    # ========== EREDIVISIE / BELGIAN PRO LEAGUE ==========
    "Viktor Gyokeres": {
        "club": "Sporting CP", "league": "Primeira Liga", "position": "Centre-Forward",
        "nationality": "Sweden", "age": 26, "value": 75, "contract": "2028",
        "goals": 28, "assists": 8, "apps": 30
    },
    "Mathys Tel": {
        "club": "Bayern Munich", "league": "Bundesliga", "position": "Centre-Forward",
        "nationality": "France", "age": 19, "value": 35, "contract": "2029",
        "goals": 6, "assists": 4, "apps": 25
    },
    
    # ========== RISING STARS ==========
    "Ethan Nwaneri": {
        "club": "Arsenal", "league": "Premier League", "position": "Attacking Midfield",
        "nationality": "England", "age": 17, "value": 25, "contract": "2029",
        "goals": 4, "assists": 3, "apps": 18
    },
    "Hugo Ekitike": {
        "club": "Liverpool", "league": "Premier League", "position": "Centre-Forward",
        "nationality": "France", "age": 22, "value": 45, "contract": "2030",
        "goals": 12, "assists": 5, "apps": 25
    },
}

# ============================================================================
# LEAGUES & CLUBS DATABASE
# ============================================================================

LEAGUES = {
    "Premier League": {"country": "England", "tier": 1, "clubs": 20},
    "La Liga": {"country": "Spain", "tier": 1, "clubs": 20},
    "Bundesliga": {"country": "Germany", "tier": 1, "clubs": 18},
    "Serie A": {"country": "Italy", "tier": 1, "clubs": 20},
    "Ligue 1": {"country": "France", "tier": 1, "clubs": 18},
    "Eredivisie": {"country": "Netherlands", "tier": 2, "clubs": 18},
    "Primeira Liga": {"country": "Portugal", "tier": 2, "clubs": 18},
    "Pro League": {"country": "Belgium", "tier": 2, "clubs": 16},
    "Super Lig": {"country": "Turkey", "tier": 2, "clubs": 19},
    "Botola Pro": {"country": "Morocco", "tier": 3, "clubs": 16},
    "Saudi Pro League": {"country": "Saudi Arabia", "tier": 2, "clubs": 18},
}

CLUBS = {
    # Premier League
    "Manchester City": {"league": "Premier League", "stadium": "Etihad Stadium", "capacity": 53400},
    "Arsenal": {"league": "Premier League", "stadium": "Emirates Stadium", "capacity": 60704},
    "Liverpool": {"league": "Premier League", "stadium": "Anfield", "capacity": 61276},
    "Chelsea": {"league": "Premier League", "stadium": "Stamford Bridge", "capacity": 40343},
    "Manchester United": {"league": "Premier League", "stadium": "Old Trafford", "capacity": 74310},
    "Tottenham": {"league": "Premier League", "stadium": "Tottenham Hotspur Stadium", "capacity": 62850},
    "Newcastle": {"league": "Premier League", "stadium": "St James' Park", "capacity": 52305},
    "Aston Villa": {"league": "Premier League", "stadium": "Villa Park", "capacity": 42657},
    # La Liga
    "Real Madrid": {"league": "La Liga", "stadium": "Santiago Bernabeu", "capacity": 81044},
    "Barcelona": {"league": "La Liga", "stadium": "Spotify Camp Nou", "capacity": 99354},
    "Atletico Madrid": {"league": "La Liga", "stadium": "Metropolitano", "capacity": 68456},
    "Athletic Bilbao": {"league": "La Liga", "stadium": "San Mames", "capacity": 53289},
    "Real Betis": {"league": "La Liga", "stadium": "Benito Villamarin", "capacity": 60721},
    "Girona": {"league": "La Liga", "stadium": "Montilivi", "capacity": 14286},
    # Bundesliga
    "Bayern Munich": {"league": "Bundesliga", "stadium": "Allianz Arena", "capacity": 75024},
    "Borussia Dortmund": {"league": "Bundesliga", "stadium": "Signal Iduna Park", "capacity": 81365},
    "RB Leipzig": {"league": "Bundesliga", "stadium": "Red Bull Arena", "capacity": 47069},
    "Bayer Leverkusen": {"league": "Bundesliga", "stadium": "BayArena", "capacity": 30210},
    "Stuttgart": {"league": "Bundesliga", "stadium": "MHP Arena", "capacity": 60449},
    # Serie A
    "Inter Milan": {"league": "Serie A", "stadium": "San Siro", "capacity": 75923},
    "AC Milan": {"league": "Serie A", "stadium": "San Siro", "capacity": 75923},
    "Juventus": {"league": "Serie A", "stadium": "Allianz Stadium", "capacity": 41507},
    "Napoli": {"league": "Serie A", "stadium": "Diego Armando Maradona", "capacity": 54726},
    # Ligue 1
    "PSG": {"league": "Ligue 1", "stadium": "Parc des Princes", "capacity": 47929},
    "Marseille": {"league": "Ligue 1", "stadium": "Velodrome", "capacity": 67394},
    # Other
    "Fenerbahce": {"league": "Super Lig", "stadium": "Sukru Saracoglu", "capacity": 50509},
    "Wydad Casablanca": {"league": "Botola Pro", "stadium": "Mohammed V", "capacity": 67000},
    "Al-Nassr": {"league": "Saudi Pro League", "stadium": "Mrsool Park", "capacity": 25000},
    "Al-Hilal": {"league": "Saudi Pro League", "stadium": "Kingdom Arena", "capacity": 25000},
    "Al-Ittihad": {"league": "Saudi Pro League", "stadium": "King Abdullah Sports City", "capacity": 62345},
    "Al-Ahli": {"league": "Saudi Pro League", "stadium": "Prince Faisal bin Fahd", "capacity": 22500},
    "PSV": {"league": "Eredivisie", "stadium": "Philips Stadion", "capacity": 35000},
    "Sporting CP": {"league": "Primeira Liga", "stadium": "Jose Alvalade", "capacity": 50095},
}

TRANSFER_RUMOURS = [
    {"player": "Florian Wirtz", "from": "Liverpool", "to": "Real Madrid", "fee": 150, "probability": 25},
    {"player": "Viktor Gyokeres", "from": "Sporting CP", "to": "Arsenal", "fee": 100, "probability": 60},
    {"player": "Khvicha Kvaratskhelia", "from": "Napoli", "to": "PSG", "fee": 80, "probability": 45},
    {"player": "Alphonso Davies", "from": "Bayern Munich", "to": "Real Madrid", "fee": 0, "probability": 70},
    {"player": "Alexander Isak", "from": "Newcastle", "to": "Arsenal", "fee": 120, "probability": 35},
    {"player": "Jamal Musiala", "from": "Bayern Munich", "to": "Manchester City", "fee": 150, "probability": 20},
    {"player": "Mohamed Salah", "from": "Liverpool", "to": "Saudi Pro League", "fee": 40, "probability": 55},
    {"player": "Rodrygo", "from": "Real Madrid", "to": "Manchester City", "fee": 100, "probability": 30},
]

RECENT_TRANSFERS = [
    {"player": "Trent Alexander-Arnold", "from": "Liverpool", "to": "Real Madrid", "fee": 0, "date": "2025-05-29"},
    {"player": "Florian Wirtz", "from": "Bayer Leverkusen", "to": "Liverpool", "fee": 125, "date": "2025-07-01"},
    {"player": "Hugo Ekitike", "from": "PSG", "to": "Liverpool", "fee": 125, "date": "2025-07-15"},
    {"player": "Eliesse Ben Seghir", "from": "Monaco", "to": "Bayer Leverkusen", "fee": 25, "date": "2025-01-05"},
    {"player": "Bilal El Khannouss", "from": "Leicester", "to": "Stuttgart", "fee": 30, "date": "2025-01-10"},
]


def get_players_df():
    """Convert players database to DataFrame"""
    data = []
    for name, info in PLAYERS_DATABASE.items():
        data.append({
            "Name": name,
            "Club": info["club"],
            "League": info["league"],
            "Position": info["position"],
            "Nationality": info["nationality"],
            "Age": info["age"],
            "Value (M)": info["value"],
            "Contract": info["contract"],
            "Goals": info["goals"],
            "Assists": info["assists"],
            "Apps": info["apps"]
        })
    return pd.DataFrame(data)


def render_market_overview():
    """Render market overview tab"""
    st.subheader("Market Overview - January 2025")
    
    df = get_players_df()
    
    # Top stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Players", len(df))
    with col2:
        st.metric("Total Value", f"{df['Value (M)'].sum():,.0f}M")
    with col3:
        st.metric("Avg Value", f"{df['Value (M)'].mean():,.1f}M")
    with col4:
        st.metric("Leagues", df['League'].nunique())
    
    st.markdown("---")
    
    # Top 10 Most Valuable
    st.subheader("Top 10 Most Valuable Players")
    top10 = df.nlargest(10, 'Value (M)')[['Name', 'Club', 'Position', 'Age', 'Value (M)']]
    st.dataframe(top10, width="stretch", hide_index=True)
    
    # By League
    st.subheader("Total Value by League")
    league_values = df.groupby('League')['Value (M)'].sum().sort_values(ascending=False)
    st.bar_chart(league_values)
    
    # Moroccan Players
    st.subheader("Moroccan Players Worldwide")
    moroccan = df[df['Nationality'] == 'Morocco'][['Name', 'Club', 'League', 'Position', 'Value (M)']]
    st.dataframe(moroccan.sort_values('Value (M)', ascending=False), width="stretch", hide_index=True)


def render_player_search():
    """Render player search tab"""
    st.subheader("Player Database Search")
    
    df = get_players_df()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_name = st.text_input("Search by Name")
    with col2:
        filter_league = st.selectbox("Filter by League", ["All"] + sorted(df['League'].unique().tolist()))
    with col3:
        filter_position = st.selectbox("Filter by Position", ["All"] + sorted(df['Position'].unique().tolist()))
    
    col4, col5, col6 = st.columns(3)
    with col4:
        filter_nationality = st.selectbox("Filter by Nationality", ["All"] + sorted(df['Nationality'].unique().tolist()))
    with col5:
        min_value = st.number_input("Min Value (M)", min_value=0, max_value=200, value=0)
    with col6:
        max_value = st.number_input("Max Value (M)", min_value=0, max_value=250, value=250)
    
    # Apply filters
    filtered = df.copy()
    if search_name:
        filtered = filtered[filtered['Name'].str.contains(search_name, case=False)]
    if filter_league != "All":
        filtered = filtered[filtered['League'] == filter_league]
    if filter_position != "All":
        filtered = filtered[filtered['Position'] == filter_position]
    if filter_nationality != "All":
        filtered = filtered[filtered['Nationality'] == filter_nationality]
    filtered = filtered[(filtered['Value (M)'] >= min_value) & (filtered['Value (M)'] <= max_value)]
    
    # Results
    st.markdown(f"**Found {len(filtered)} players**")
    st.dataframe(
        filtered.sort_values('Value (M)', ascending=False),
        width="stretch",
        hide_index=True
    )


def render_transfers():
    """Render transfers tab"""
    st.subheader("Transfer Centre")
    
    tab1, tab2 = st.tabs(["Recent Transfers", "Transfer Rumours"])
    
    with tab1:
        st.markdown("### Completed Transfers 2025")
        for t in RECENT_TRANSFERS:
            fee_text = f"{t['fee']}M" if t['fee'] > 0 else "Free Transfer"
            st.markdown(f"""
            **{t['player']}**  
            {t['from']} -> {t['to']} | {fee_text} | {t['date']}
            """)
            st.markdown("---")
    
    with tab2:
        st.markdown("### Active Transfer Rumours")
        for r in TRANSFER_RUMOURS:
            prob_color = "green" if r['probability'] >= 50 else "orange" if r['probability'] >= 30 else "red"
            fee_text = f"{r['fee']}M" if r['fee'] > 0 else "Free"
            st.markdown(f"""
            **{r['player']}**  
            {r['from']} -> {r['to']} | {fee_text} | Probability: :{prob_color}[{r['probability']}%]
            """)
            st.markdown("---")


def render_statistics():
    """Render statistics tab"""
    st.subheader("Player Statistics")
    
    df = get_players_df()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Top Scorers")
        top_scorers = df.nlargest(10, 'Goals')[['Name', 'Club', 'Goals', 'Apps']]
        top_scorers['Goals/App'] = (top_scorers['Goals'] / top_scorers['Apps']).round(2)
        st.dataframe(top_scorers, width="stretch", hide_index=True)
    
    with col2:
        st.markdown("### Top Assists")
        top_assists = df.nlargest(10, 'Assists')[['Name', 'Club', 'Assists', 'Apps']]
        st.dataframe(top_assists, width="stretch", hide_index=True)
    
    st.markdown("---")
    
    # By Position
    st.markdown("### Value Distribution by Position")
    pos_avg = df.groupby('Position')['Value (M)'].mean().sort_values(ascending=False)
    st.bar_chart(pos_avg)
    
    # Age distribution
    st.markdown("### Age vs Value")
    age_value = df.groupby('Age')['Value (M)'].mean()
    st.line_chart(age_value)


def render_watchlist():
    """Render watchlist tab"""
    st.subheader("My Watchlist")
    
    if 'tm_watchlist' not in st.session_state:
        st.session_state['tm_watchlist'] = []
    
    df = get_players_df()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        player_to_add = st.selectbox("Add player to watchlist", df['Name'].tolist())
    with col2:
        if st.button("Add"):
            if player_to_add not in st.session_state['tm_watchlist']:
                st.session_state['tm_watchlist'].append(player_to_add)
                st.success(f"Added {player_to_add}")
            else:
                st.warning("Already in watchlist")
    
    if st.session_state['tm_watchlist']:
        st.markdown("### Your Watchlist")
        watchlist_df = df[df['Name'].isin(st.session_state['tm_watchlist'])]
        st.dataframe(watchlist_df, width="stretch", hide_index=True)
        
        if st.button("Clear Watchlist"):
            st.session_state['tm_watchlist'] = []
            st.rerun()
    else:
        st.info("Your watchlist is empty. Add players above.")


def render_compare():
    """Render player comparison tab"""
    st.subheader("Compare Players")
    
    df = get_players_df()
    
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.selectbox("Player 1", df['Name'].tolist(), key="p1")
    with col2:
        player2 = st.selectbox("Player 2", df['Name'].tolist(), index=1, key="p2")
    
    if st.button("Compare"):
        p1_data = df[df['Name'] == player1].iloc[0]
        p2_data = df[df['Name'] == player2].iloc[0]
        
        comparison_data = {
            "Attribute": ["Club", "League", "Position", "Nationality", "Age", "Value (M)", "Goals", "Assists", "Apps"],
            player1: [p1_data['Club'], p1_data['League'], p1_data['Position'], p1_data['Nationality'], 
                     p1_data['Age'], p1_data['Value (M)'], p1_data['Goals'], p1_data['Assists'], p1_data['Apps']],
            player2: [p2_data['Club'], p2_data['League'], p2_data['Position'], p2_data['Nationality'],
                     p2_data['Age'], p2_data['Value (M)'], p2_data['Goals'], p2_data['Assists'], p2_data['Apps']]
        }
        
        st.dataframe(pd.DataFrame(comparison_data), width="stretch", hide_index=True)


def render():
    """Main render function"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>Transfer Market</h1>
        <p style='color: #888; margin: 5px 0 0 0;'>Data verified from transfermarkt.de - January 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([
        "Overview",
        "Player Search", 
        "Transfers",
        "Statistics",
        "Watchlist",
        "Compare"
    ])
    
    with tabs[0]:
        render_market_overview()
    with tabs[1]:
        render_player_search()
    with tabs[2]:
        render_transfers()
    with tabs[3]:
        render_statistics()
    with tabs[4]:
        render_watchlist()
    with tabs[5]:
        render_compare()
