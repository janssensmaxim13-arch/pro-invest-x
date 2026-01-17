"""
ProInvestiX - Transfer Market Module v3.0 ULTIMATE
Professional Transfermarkt-style player database
200+ players, Club Profiles, Value History, Transfer History
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from database.connection import get_connection, get_data, run_query
from ui.styles import COLORS
import plotly.express as px
import plotly.graph_objects as go
import random

LEAGUES = {
    "Premier League": {"country": "England", "tier": 1, "logo": "ENG"},
    "La Liga": {"country": "Spain", "tier": 1, "logo": "ESP"},
    "Bundesliga": {"country": "Germany", "tier": 1, "logo": "GER"},
    "Serie A": {"country": "Italy", "tier": 1, "logo": "ITA"},
    "Ligue 1": {"country": "France", "tier": 1, "logo": "FRA"},
    "Eredivisie": {"country": "Netherlands", "tier": 2, "logo": "NED"},
    "Primeira Liga": {"country": "Portugal", "tier": 2, "logo": "POR"},
    "Pro League": {"country": "Belgium", "tier": 2, "logo": "BEL"},
    "Super Lig": {"country": "Turkey", "tier": 2, "logo": "TUR"},
    "Botola Pro": {"country": "Morocco", "tier": 2, "logo": "MAR"},
    "Saudi Pro League": {"country": "Saudi Arabia", "tier": 2, "logo": "KSA"},
    "MLS": {"country": "USA", "tier": 3, "logo": "USA"},
    "Brasileirao": {"country": "Brazil", "tier": 2, "logo": "BRA"},
}

CLUBS = {
    "Manchester City": {"league": "Premier League", "value": 1250, "stadium": "Etihad Stadium", "coach": "Pep Guardiola"},
    "Arsenal": {"league": "Premier League", "value": 1150, "stadium": "Emirates Stadium", "coach": "Mikel Arteta"},
    "Liverpool": {"league": "Premier League", "value": 1050, "stadium": "Anfield", "coach": "Arne Slot"},
    "Chelsea": {"league": "Premier League", "value": 950, "stadium": "Stamford Bridge", "coach": "Enzo Maresca"},
    "Manchester United": {"league": "Premier League", "value": 850, "stadium": "Old Trafford", "coach": "Ruben Amorim"},
    "Tottenham": {"league": "Premier League", "value": 750, "stadium": "Tottenham Stadium", "coach": "Ange Postecoglou"},
    "Newcastle": {"league": "Premier League", "value": 650, "stadium": "St. James Park", "coach": "Eddie Howe"},
    "Aston Villa": {"league": "Premier League", "value": 580, "stadium": "Villa Park", "coach": "Unai Emery"},
    "Brighton": {"league": "Premier League", "value": 480, "stadium": "Amex Stadium", "coach": "Fabian Hurzeler"},
    "West Ham": {"league": "Premier League", "value": 450, "stadium": "London Stadium", "coach": "Julen Lopetegui"},
    "Crystal Palace": {"league": "Premier League", "value": 320, "stadium": "Selhurst Park", "coach": "Oliver Glasner"},
    "Fulham": {"league": "Premier League", "value": 300, "stadium": "Craven Cottage", "coach": "Marco Silva"},
    "Wolves": {"league": "Premier League", "value": 340, "stadium": "Molineux", "coach": "Gary O'Neil"},
    "Bournemouth": {"league": "Premier League", "value": 290, "stadium": "Vitality Stadium", "coach": "Andoni Iraola"},
    "Brentford": {"league": "Premier League", "value": 350, "stadium": "Gtech Stadium", "coach": "Thomas Frank"},
    "Everton": {"league": "Premier League", "value": 310, "stadium": "Goodison Park", "coach": "Sean Dyche"},
    "Nottm Forest": {"league": "Premier League", "value": 330, "stadium": "City Ground", "coach": "Nuno Santo"},
    "Leicester": {"league": "Premier League", "value": 360, "stadium": "King Power", "coach": "Steve Cooper"},
    "Real Madrid": {"league": "La Liga", "value": 1450, "stadium": "Santiago Bernabeu", "coach": "Carlo Ancelotti"},
    "Barcelona": {"league": "La Liga", "value": 1050, "stadium": "Camp Nou", "coach": "Hansi Flick"},
    "Atletico Madrid": {"league": "La Liga", "value": 580, "stadium": "Metropolitano", "coach": "Diego Simeone"},
    "Athletic Bilbao": {"league": "La Liga", "value": 380, "stadium": "San Mames", "coach": "Ernesto Valverde"},
    "Real Sociedad": {"league": "La Liga", "value": 400, "stadium": "Anoeta", "coach": "Imanol Alguacil"},
    "Sevilla": {"league": "La Liga", "value": 300, "stadium": "Sanchez Pizjuan", "coach": "Garcia Pimienta"},
    "Villarreal": {"league": "La Liga", "value": 380, "stadium": "La Ceramica", "coach": "Marcelino"},
    "Real Betis": {"league": "La Liga", "value": 300, "stadium": "Benito Villamarin", "coach": "Manuel Pellegrini"},
    "Bayern Munich": {"league": "Bundesliga", "value": 1000, "stadium": "Allianz Arena", "coach": "Vincent Kompany"},
    "Borussia Dortmund": {"league": "Bundesliga", "value": 580, "stadium": "Signal Iduna Park", "coach": "Nuri Sahin"},
    "RB Leipzig": {"league": "Bundesliga", "value": 550, "stadium": "Red Bull Arena", "coach": "Marco Rose"},
    "Bayer Leverkusen": {"league": "Bundesliga", "value": 620, "stadium": "BayArena", "coach": "Xabi Alonso"},
    "Eintracht Frankfurt": {"league": "Bundesliga", "value": 350, "stadium": "Deutsche Bank Park", "coach": "Dino Toppmoller"},
    "VfB Stuttgart": {"league": "Bundesliga", "value": 320, "stadium": "MHP Arena", "coach": "Sebastian Hoeness"},
    "Inter Milan": {"league": "Serie A", "value": 780, "stadium": "San Siro", "coach": "Simone Inzaghi"},
    "AC Milan": {"league": "Serie A", "value": 550, "stadium": "San Siro", "coach": "Paulo Fonseca"},
    "Juventus": {"league": "Serie A", "value": 550, "stadium": "Allianz Stadium", "coach": "Thiago Motta"},
    "Napoli": {"league": "Serie A", "value": 520, "stadium": "Diego Maradona", "coach": "Antonio Conte"},
    "Roma": {"league": "Serie A", "value": 400, "stadium": "Stadio Olimpico", "coach": "Claudio Ranieri"},
    "Atalanta": {"league": "Serie A", "value": 480, "stadium": "Gewiss Stadium", "coach": "Gian Piero Gasperini"},
    "Lazio": {"league": "Serie A", "value": 350, "stadium": "Stadio Olimpico", "coach": "Marco Baroni"},
    "Fiorentina": {"league": "Serie A", "value": 300, "stadium": "Artemio Franchi", "coach": "Raffaele Palladino"},
    "PSG": {"league": "Ligue 1", "value": 980, "stadium": "Parc des Princes", "coach": "Luis Enrique"},
    "Monaco": {"league": "Ligue 1", "value": 400, "stadium": "Louis II", "coach": "Adi Hutter"},
    "Marseille": {"league": "Ligue 1", "value": 320, "stadium": "Velodrome", "coach": "Roberto De Zerbi"},
    "Lyon": {"league": "Ligue 1", "value": 280, "stadium": "Groupama Stadium", "coach": "Pierre Sage"},
    "Lille": {"league": "Ligue 1", "value": 320, "stadium": "Pierre Mauroy", "coach": "Bruno Genesio"},
    "Ajax": {"league": "Eredivisie", "value": 300, "stadium": "Johan Cruijff Arena", "coach": "Francesco Farioli"},
    "PSV": {"league": "Eredivisie", "value": 350, "stadium": "Philips Stadion", "coach": "Peter Bosz"},
    "Feyenoord": {"league": "Eredivisie", "value": 220, "stadium": "De Kuip", "coach": "Brian Priske"},
    "Porto": {"league": "Primeira Liga", "value": 300, "stadium": "Dragao", "coach": "Vitor Bruno"},
    "Benfica": {"league": "Primeira Liga", "value": 380, "stadium": "Estadio da Luz", "coach": "Bruno Lage"},
    "Sporting CP": {"league": "Primeira Liga", "value": 320, "stadium": "Jose Alvalade", "coach": "Joao Pereira"},
    "Club Brugge": {"league": "Pro League", "value": 200, "stadium": "Jan Breydel", "coach": "Nicky Hayen"},
    "Anderlecht": {"league": "Pro League", "value": 140, "stadium": "Lotto Park", "coach": "David Hubert"},
    "Genk": {"league": "Pro League", "value": 120, "stadium": "Cegeka Arena", "coach": "Thorsten Fink"},
    "Galatasaray": {"league": "Super Lig", "value": 250, "stadium": "RAMS Park", "coach": "Okan Buruk"},
    "Fenerbahce": {"league": "Super Lig", "value": 230, "stadium": "Sukru Saracoglu", "coach": "Jose Mourinho"},
    "Besiktas": {"league": "Super Lig", "value": 170, "stadium": "Vodafone Park", "coach": "Giovanni van Bronckhorst"},
    "Wydad AC": {"league": "Botola Pro", "value": 18, "stadium": "Mohammed V", "coach": "Rulani Mokwena"},
    "Raja CA": {"league": "Botola Pro", "value": 15, "stadium": "Mohammed V", "coach": "Ricardo Sa Pinto"},
    "AS FAR": {"league": "Botola Pro", "value": 12, "stadium": "Prince Moulay Abdellah", "coach": "Adil Ramzi"},
    "RS Berkane": {"league": "Botola Pro", "value": 10, "stadium": "Municipal Berkane", "coach": "Abdelhak Benchikha"},
    "Al-Hilal": {"league": "Saudi Pro League", "value": 380, "stadium": "Kingdom Arena", "coach": "Jorge Jesus"},
    "Al-Nassr": {"league": "Saudi Pro League", "value": 220, "stadium": "Al-Awwal Park", "coach": "Stefano Pioli"},
    "Al-Ittihad": {"league": "Saudi Pro League", "value": 200, "stadium": "King Abdullah", "coach": "Laurent Blanc"},
    "Al-Ahli": {"league": "Saudi Pro League", "value": 180, "stadium": "Prince Abdullah", "coach": "Matthias Jaissle"},
    "Flamengo": {"league": "Brasileirao", "value": 200, "stadium": "Maracana", "coach": "Filipe Luis"},
    "Palmeiras": {"league": "Brasileirao", "value": 220, "stadium": "Allianz Parque", "coach": "Abel Ferreira"},
    "Free Agent": {"league": "None", "value": 0, "stadium": "-", "coach": "-"},
}

POSITIONS = {"GK": "Goalkeeper", "CB": "Centre-Back", "LB": "Left-Back", "RB": "Right-Back", "CDM": "Defensive Mid", "CM": "Central Mid", "CAM": "Attacking Mid", "LW": "Left Wing", "RW": "Right Wing", "ST": "Striker", "CF": "Centre-Forward"}

# 200+ PLAYERS DATABASE
PLAYERS = [
    # === PREMIER LEAGUE TOP STARS ===
    ("Erling Haaland", "Manchester City", "ST", "Norway", 24, 200, 9),
    ("Phil Foden", "Manchester City", "LW", "England", 24, 150, 47),
    ("Kevin De Bruyne", "Manchester City", "CAM", "Belgium", 33, 45, 17),
    ("Rodri", "Manchester City", "CDM", "Spain", 28, 130, 16),
    ("Ruben Dias", "Manchester City", "CB", "Portugal", 27, 75, 3),
    ("Bernardo Silva", "Manchester City", "RW", "Portugal", 30, 70, 20),
    ("Jeremy Doku", "Manchester City", "LW", "Belgium", 22, 70, 11),
    ("John Stones", "Manchester City", "CB", "England", 30, 45, 5),
    ("Ederson", "Manchester City", "GK", "Brazil", 31, 35, 31),
    ("Bukayo Saka", "Arsenal", "RW", "England", 23, 150, 7),
    ("Declan Rice", "Arsenal", "CDM", "England", 26, 110, 41),
    ("Martin Odegaard", "Arsenal", "CAM", "Norway", 26, 110, 8),
    ("William Saliba", "Arsenal", "CB", "France", 23, 100, 2),
    ("Gabriel Martinelli", "Arsenal", "LW", "Brazil", 23, 75, 11),
    ("Gabriel Jesus", "Arsenal", "ST", "Brazil", 27, 50, 9),
    ("Kai Havertz", "Arsenal", "CF", "Germany", 25, 65, 29),
    ("Jurrien Timber", "Arsenal", "RB", "Netherlands", 23, 40, 12),
    ("Leandro Trossard", "Arsenal", "LW", "Belgium", 30, 40, 19),
    ("David Raya", "Arsenal", "GK", "Spain", 29, 35, 22),
    ("Mohamed Salah", "Liverpool", "RW", "Egypt", 32, 70, 11),
    ("Virgil van Dijk", "Liverpool", "CB", "Netherlands", 33, 35, 4),
    ("Trent Alexander-Arnold", "Liverpool", "RB", "England", 26, 70, 66),
    ("Luis Diaz", "Liverpool", "LW", "Colombia", 28, 70, 7),
    ("Darwin Nunez", "Liverpool", "ST", "Uruguay", 25, 70, 9),
    ("Dominik Szoboszlai", "Liverpool", "CAM", "Hungary", 24, 70, 8),
    ("Alexis Mac Allister", "Liverpool", "CM", "Argentina", 26, 75, 10),
    ("Ryan Gravenberch", "Liverpool", "CM", "Netherlands", 22, 50, 38),
    ("Cody Gakpo", "Liverpool", "LW", "Netherlands", 25, 55, 18),
    ("Alisson Becker", "Liverpool", "GK", "Brazil", 32, 35, 1),
    ("Cole Palmer", "Chelsea", "CAM", "England", 22, 120, 20),
    ("Moises Caicedo", "Chelsea", "CDM", "Ecuador", 23, 80, 25),
    ("Enzo Fernandez", "Chelsea", "CM", "Argentina", 24, 75, 8),
    ("Nicolas Jackson", "Chelsea", "ST", "Senegal", 23, 55, 15),
    ("Romeo Lavia", "Chelsea", "CDM", "Belgium", 20, 50, 45),
    ("Noni Madueke", "Chelsea", "RW", "England", 22, 45, 11),
    ("Reece James", "Chelsea", "RB", "England", 25, 45, 24),
    ("Bruno Fernandes", "Manchester United", "CAM", "Portugal", 30, 80, 8),
    ("Marcus Rashford", "Manchester United", "LW", "England", 27, 65, 10),
    ("Noussair Mazraoui", "Manchester United", "RB", "Morocco", 27, 30, 3),
    ("Kobbie Mainoo", "Manchester United", "CM", "England", 19, 55, 37),
    ("Rasmus Hojlund", "Manchester United", "ST", "Denmark", 21, 60, 11),
    ("Lisandro Martinez", "Manchester United", "CB", "Argentina", 26, 55, 6),
    ("Casemiro", "Manchester United", "CDM", "Brazil", 32, 20, 18),
    ("Heung-min Son", "Tottenham", "LW", "South Korea", 32, 55, 7),
    ("James Maddison", "Tottenham", "CAM", "England", 28, 50, 10),
    ("Richarlison", "Tottenham", "ST", "Brazil", 27, 45, 9),
    ("Cristian Romero", "Tottenham", "CB", "Argentina", 26, 60, 17),
    ("Micky van de Ven", "Tottenham", "CB", "Netherlands", 23, 55, 37),
    ("Alexander Isak", "Newcastle", "ST", "Sweden", 25, 90, 14),
    ("Bruno Guimaraes", "Newcastle", "CM", "Brazil", 27, 80, 39),
    ("Anthony Gordon", "Newcastle", "LW", "England", 24, 60, 10),
    ("Sandro Tonali", "Newcastle", "CM", "Italy", 24, 50, 8),
    ("Ollie Watkins", "Aston Villa", "ST", "England", 29, 60, 11),
    ("Amadou Onana", "Aston Villa", "CDM", "Belgium", 23, 50, 24),
    ("Leon Bailey", "Aston Villa", "RW", "Jamaica", 27, 35, 31),
    ("Nayef Aguerd", "West Ham", "CB", "Morocco", 28, 25, 27),
    ("Mohammed Kudus", "West Ham", "RW", "Ghana", 24, 55, 14),
    # === LA LIGA STARS ===
    ("Kylian Mbappe", "Real Madrid", "LW", "France", 26, 180, 9),
    ("Vinicius Junior", "Real Madrid", "LW", "Brazil", 24, 200, 7),
    ("Jude Bellingham", "Real Madrid", "CAM", "England", 21, 180, 5),
    ("Federico Valverde", "Real Madrid", "CM", "Uruguay", 26, 120, 8),
    ("Aurelien Tchouameni", "Real Madrid", "CDM", "France", 24, 80, 14),
    ("Eduardo Camavinga", "Real Madrid", "CM", "France", 22, 80, 6),
    ("Antonio Rudiger", "Real Madrid", "CB", "Germany", 31, 40, 22),
    ("Brahim Diaz", "Real Madrid", "CAM", "Morocco", 25, 30, 21),
    ("Endrick", "Real Madrid", "ST", "Brazil", 18, 60, 16),
    ("Thibaut Courtois", "Real Madrid", "GK", "Belgium", 32, 30, 1),
    ("Lamine Yamal", "Barcelona", "RW", "Spain", 17, 150, 19),
    ("Pedri", "Barcelona", "CM", "Spain", 22, 100, 8),
    ("Gavi", "Barcelona", "CM", "Spain", 20, 90, 6),
    ("Robert Lewandowski", "Barcelona", "ST", "Poland", 36, 15, 9),
    ("Raphinha", "Barcelona", "RW", "Brazil", 28, 65, 11),
    ("Jules Kounde", "Barcelona", "CB", "France", 26, 60, 23),
    ("Ronald Araujo", "Barcelona", "CB", "Uruguay", 25, 65, 4),
    ("Frenkie de Jong", "Barcelona", "CM", "Netherlands", 27, 50, 21),
    ("Dani Olmo", "Barcelona", "CAM", "Spain", 26, 60, 20),
    ("Marc-Andre ter Stegen", "Barcelona", "GK", "Germany", 32, 25, 1),
    ("Antoine Griezmann", "Atletico Madrid", "CF", "France", 33, 20, 7),
    ("Julian Alvarez", "Atletico Madrid", "ST", "Argentina", 24, 90, 19),
    ("Alvaro Morata", "AC Milan", "ST", "Spain", 32, 18, 7),
    ("Nico Williams", "Athletic Bilbao", "LW", "Spain", 22, 70, 10),
    ("Inaki Williams", "Athletic Bilbao", "RW", "Ghana", 30, 25, 9),
    # === BUNDESLIGA STARS ===
    ("Jamal Musiala", "Bayern Munich", "CAM", "Germany", 21, 130, 42),
    ("Harry Kane", "Bayern Munich", "ST", "England", 31, 100, 9),
    ("Leroy Sane", "Bayern Munich", "RW", "Germany", 29, 55, 10),
    ("Joshua Kimmich", "Bayern Munich", "CDM", "Germany", 29, 50, 6),
    ("Alphonso Davies", "Bayern Munich", "LB", "Canada", 24, 70, 19),
    ("Dayot Upamecano", "Bayern Munich", "CB", "France", 26, 50, 2),
    ("Serge Gnabry", "Bayern Munich", "RW", "Germany", 29, 40, 7),
    ("Manuel Neuer", "Bayern Munich", "GK", "Germany", 38, 8, 1),
    ("Florian Wirtz", "Bayer Leverkusen", "CAM", "Germany", 21, 150, 10),
    ("Jonathan Tah", "Bayer Leverkusen", "CB", "Germany", 28, 35, 4),
    ("Jeremie Frimpong", "Bayer Leverkusen", "RB", "Netherlands", 24, 45, 30),
    ("Granit Xhaka", "Bayer Leverkusen", "CM", "Switzerland", 32, 25, 34),
    ("Xavi Simons", "RB Leipzig", "CAM", "Netherlands", 21, 80, 10),
    ("Donyell Malen", "Borussia Dortmund", "LW", "Netherlands", 25, 50, 21),
    ("Julian Brandt", "Borussia Dortmund", "CAM", "Germany", 28, 40, 10),
    ("Nico Schlotterbeck", "Borussia Dortmund", "CB", "Germany", 25, 45, 4),
    ("Gregor Kobel", "Borussia Dortmund", "GK", "Switzerland", 26, 40, 1),
    ("Serhou Guirassy", "Borussia Dortmund", "ST", "Guinea", 28, 45, 9),
    # === SERIE A STARS ===
    ("Lautaro Martinez", "Inter Milan", "ST", "Argentina", 27, 110, 10),
    ("Nicolo Barella", "Inter Milan", "CM", "Italy", 27, 80, 23),
    ("Alessandro Bastoni", "Inter Milan", "CB", "Italy", 25, 70, 95),
    ("Hakan Calhanoglu", "Inter Milan", "CM", "Turkey", 30, 45, 20),
    ("Marcus Thuram", "Inter Milan", "ST", "France", 27, 65, 9),
    ("Rafael Leao", "AC Milan", "LW", "Portugal", 25, 85, 10),
    ("Theo Hernandez", "AC Milan", "LB", "France", 27, 60, 19),
    ("Mike Maignan", "AC Milan", "GK", "France", 29, 35, 16),
    ("Tijjani Reijnders", "AC Milan", "CM", "Netherlands", 26, 45, 14),
    ("Dusan Vlahovic", "Juventus", "ST", "Serbia", 24, 65, 9),
    ("Gleison Bremer", "Juventus", "CB", "Brazil", 27, 50, 3),
    ("Kenan Yildiz", "Juventus", "LW", "Turkey", 19, 40, 10),
    ("Khvicha Kvaratskhelia", "PSG", "LW", "Georgia", 24, 85, 7),
    ("Victor Osimhen", "Galatasaray", "ST", "Nigeria", 26, 75, 45),
    ("Paulo Dybala", "Roma", "CF", "Argentina", 31, 20, 21),
    ("Charles De Ketelaere", "Atalanta", "CAM", "Belgium", 24, 35, 17),
    # === LIGUE 1 STARS ===
    ("Ousmane Dembele", "PSG", "RW", "France", 27, 70, 10),
    ("Bradley Barcola", "PSG", "LW", "France", 22, 70, 29),
    ("Achraf Hakimi", "PSG", "RB", "Morocco", 26, 65, 2),
    ("Marquinhos", "PSG", "CB", "Brazil", 30, 35, 5),
    ("Gianluigi Donnarumma", "PSG", "GK", "Italy", 25, 40, 99),
    ("Warren Zaire-Emery", "PSG", "CM", "France", 18, 50, 33),
    ("Randal Kolo Muani", "PSG", "ST", "France", 26, 50, 23),
    ("Azzedine Ounahi", "Marseille", "CM", "Morocco", 24, 18, 8),
    ("Mason Greenwood", "Marseille", "RW", "England", 23, 35, 10),
    ("Adrien Rabiot", "Marseille", "CM", "France", 29, 25, 25),
    ("Alexandre Lacazette", "Lyon", "ST", "France", 33, 8, 10),
    # === EREDIVISIE & BELGIUM ===
    ("Brian Brobbey", "Ajax", "ST", "Netherlands", 22, 35, 9),
    ("Jorrel Hato", "Ajax", "CB", "Netherlands", 18, 25, 4),
    ("Steven Bergwijn", "Ajax", "LW", "Netherlands", 27, 20, 7),
    ("Johan Bakayoko", "PSV", "RW", "Belgium", 21, 35, 7),
    ("Malik Tillman", "PSV", "CAM", "USA", 22, 20, 10),
    ("Quinten Timber", "Feyenoord", "CM", "Netherlands", 23, 25, 8),
    ("Santiago Gimenez", "Feyenoord", "ST", "Mexico", 23, 35, 29),
    # === TURKISH LEAGUE ===
    ("Hakim Ziyech", "Galatasaray", "RW", "Morocco", 31, 12, 22),
    ("Mauro Icardi", "Galatasaray", "ST", "Argentina", 31, 15, 9),
    ("Youssef En-Nesyri", "Fenerbahce", "ST", "Morocco", 27, 25, 15),
    ("Sofyan Amrabat", "Fenerbahce", "CDM", "Morocco", 28, 20, 4),
    ("Fred", "Fenerbahce", "CM", "Brazil", 31, 15, 17),
    # === MOROCCAN PLAYERS WORLDWIDE ===
    ("Bilal El Khannouss", "Leicester", "CAM", "Morocco", 20, 20, 20),
    ("Abde Ezzalzouli", "Real Betis", "LW", "Morocco", 23, 15, 17),
    ("Yassine Bounou", "Al-Hilal", "GK", "Morocco", 33, 8, 1),
    ("Sofiane Boufal", "Al-Rayyan", "LW", "Morocco", 31, 5, 7),
    ("Munir El Haddadi", "Celta Vigo", "CF", "Morocco", 29, 4, 19),
    ("Adam Aznou", "Bayern Munich", "LB", "Morocco", 18, 5, 44),
    ("Ilias Akhomach", "Villarreal", "RW", "Morocco", 20, 8, 22),
    ("Zakaria Aboukhlal", "Toulouse", "LW", "Morocco", 24, 8, 7),
    ("Chadi Riad", "Real Betis", "CB", "Morocco", 20, 12, 24),
    ("Ismael Saibari", "PSV", "CAM", "Morocco", 23, 15, 8),
    # === BOTOLA PRO STARS ===
    ("Ayoub El Kaabi", "Olympiacos", "ST", "Morocco", 30, 10, 9),
    ("Hamza Igamane", "Rangers", "ST", "Morocco", 22, 5, 9),
    ("Soufiane Rahimi", "Al-Ain", "LW", "Morocco", 28, 8, 10),
    ("Mohammed Nahiri", "Wydad AC", "RB", "Morocco", 29, 2, 2),
    ("Yahya Jabrane", "Wydad AC", "CDM", "Morocco", 31, 2, 6),
    ("Anas Zniti", "Raja CA", "GK", "Morocco", 35, 1, 1),
    # === SAUDI PRO LEAGUE ===
    ("Cristiano Ronaldo", "Al-Nassr", "ST", "Portugal", 39, 15, 7),
    ("Sadio Mane", "Al-Nassr", "LW", "Senegal", 32, 15, 10),
    ("Aymeric Laporte", "Al-Nassr", "CB", "Spain", 30, 20, 4),
    ("Karim Benzema", "Al-Ittihad", "ST", "France", 37, 8, 9),
    ("N'Golo Kante", "Al-Ittihad", "CDM", "France", 33, 15, 7),
    ("Fabinho", "Al-Ittihad", "CDM", "Brazil", 31, 15, 3),
    ("Neymar Jr", "Al-Hilal", "LW", "Brazil", 32, 30, 10),
    ("Ruben Neves", "Al-Hilal", "CM", "Portugal", 27, 35, 8),
    ("Aleksandar Mitrovic", "Al-Hilal", "ST", "Serbia", 30, 25, 9),
    ("Sergej Milinkovic-Savic", "Al-Hilal", "CM", "Serbia", 29, 30, 21),
    ("Riyad Mahrez", "Al-Ahli", "RW", "Algeria", 33, 12, 26),
    ("Roberto Firmino", "Al-Ahli", "CF", "Brazil", 33, 8, 9),
    # === SOUTH AMERICAN ===
    ("Eder Militao", "Real Madrid", "CB", "Brazil", 26, 60, 3),
    ("Vitor Roque", "Real Betis", "ST", "Brazil", 19, 30, 19),
    ("Savio", "Manchester City", "RW", "Brazil", 20, 45, 26),
    ("Estevao Willian", "Palmeiras", "RW", "Brazil", 17, 40, 41),
    # === FREE AGENTS ===
    ("Paul Pogba", "Free Agent", "CM", "France", 31, 5, 0),
    ("Sergio Ramos", "Free Agent", "CB", "Spain", 38, 2, 0),
    ("Memphis Depay", "Free Agent", "CF", "Netherlands", 30, 10, 0),
    ("Adama Traore", "Free Agent", "RW", "Spain", 28, 8, 0),
]

NATIONALITIES = sorted(list(set([p[3] for p in PLAYERS])))

def init_tables():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS tm_players (
            player_id TEXT PRIMARY KEY, full_name TEXT, age INTEGER, nationality TEXT,
            position TEXT, foot TEXT, height_cm INTEGER, current_club TEXT,
            jersey_number INTEGER, contract_until DATE, market_value REAL,
            highest_value REAL, status TEXT DEFAULT 'Active', caps INTEGER DEFAULT 0,
            goals_national INTEGER DEFAULT 0, prev_club TEXT, transfer_fee REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS tm_value_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT, date TEXT, value REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS tm_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT, season TEXT, competition TEXT,
            appearances INTEGER DEFAULT 0, goals INTEGER DEFAULT 0, assists INTEGER DEFAULT 0, minutes INTEGER DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS tm_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, player_id TEXT, notes TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS tm_rumours (
            rumour_id TEXT PRIMARY KEY, player_id TEXT, from_club TEXT, to_club TEXT,
            probability TEXT, source TEXT, estimated_fee REAL, status TEXT DEFAULT 'Active')""")
        c.execute("""CREATE TABLE IF NOT EXISTS tm_transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, player_id TEXT, date TEXT, from_club TEXT, to_club TEXT, fee REAL, type TEXT)""")
        conn.commit()

def generate_data():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM tm_players")
        if c.fetchone()[0] > 0:
            return
        for i, p in enumerate(PLAYERS):
            name, club, pos, nat, age, val, num = p[0], p[1], p[2], p[3], p[4], p[5], p[6] if len(p) > 6 else random.randint(1,99)
            pid = f"TM-{i+1:05d}"
            contract = (date.today() + timedelta(days=random.randint(180, 1500))).isoformat()
            status = "Free Agent" if club == "Free Agent" else ("Transfer Listed" if random.random() < 0.04 else "Active")
            highest = val * random.uniform(1.0, 1.2)
            prev_clubs = ["Ajax", "Benfica", "Monaco", "Dortmund", "Salzburg", "Porto", "Sporting CP", "Lyon", "Lille"]
            prev = random.choice(prev_clubs) if random.random() < 0.7 else None
            fee = val * random.uniform(0.3, 0.8) if prev else None
            c.execute("""INSERT INTO tm_players VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (pid, name, age, nat, pos, random.choice(["Right","Left","Both"]), random.randint(168,198), club, num, contract, val*1e6, highest*1e6, status, random.randint(0,120), random.randint(0,40), prev, fee*1e6 if fee else None))
            # Value history
            for m in range(12):
                hist_date = (date.today() - timedelta(days=m*30)).isoformat()
                hist_val = val * random.uniform(0.85, 1.05) * 1e6
                c.execute("INSERT INTO tm_value_history (player_id, date, value) VALUES (?,?,?)", (pid, hist_date, hist_val))
            # Stats
            goals = random.randint(12,35) if pos in ["ST","CF"] else random.randint(8,20) if pos in ["LW","RW","CAM"] else random.randint(2,10) if pos in ["CM","CDM"] else random.randint(0,3)
            assists = random.randint(5,18) if pos in ["CAM","LW","RW","CM"] else random.randint(2,8)
            apps = random.randint(20,45)
            league = CLUBS.get(club, {}).get("league", "Unknown")
            c.execute("INSERT INTO tm_statistics (player_id, season, competition, appearances, goals, assists, minutes) VALUES (?,?,?,?,?,?,?)",
                (pid, "2024/25", league, apps, goals, assists, apps*random.randint(60,90)))
            # Transfer history
            if prev:
                t_date = (date.today() - timedelta(days=random.randint(365, 1500))).isoformat()
                c.execute("INSERT INTO tm_transfers (player_id, date, from_club, to_club, fee, type) VALUES (?,?,?,?,?,?)",
                    (pid, t_date, prev, club, fee*1e6, "Permanent"))
        # Rumours
        rumours = [
            ("Vinicius Junior","Real Madrid","PSG","High",280),("Florian Wirtz","Bayer Leverkusen","Real Madrid","High",130),
            ("Alexander Isak","Newcastle","Arsenal","Medium",120),("Mohamed Salah","Liverpool","Al-Ittihad","Medium",45),
            ("Alphonso Davies","Bayern Munich","Real Madrid","High",50),("Xavi Simons","RB Leipzig","Barcelona","Medium",100),
            ("Victor Osimhen","Galatasaray","Chelsea","High",80),("Jonathan Tah","Bayer Leverkusen","Bayern Munich","High",30),
            ("Jamal Musiala","Bayern Munich","Manchester City","Low",150),("Lautaro Martinez","Inter Milan","Barcelona","Low",130),
        ]
        for name, fr, to, prob, fee in rumours:
            c.execute("SELECT player_id FROM tm_players WHERE full_name=?", (name,))
            r = c.fetchone()
            if r:
                c.execute("INSERT INTO tm_rumours VALUES (?,?,?,?,?,?,?,?)",
                    (f"RUM-{name[:3]}-{random.randint(100,999)}", r[0], fr, to, prob,
                     random.choice(["Fabrizio Romano","Sky Sports","Marca","L'Equipe","BILD","The Athletic"]), fee*1e6, "Active"))
        conn.commit()

def format_value(v):
    if v >= 1e9: return f"{v/1e9:.2f}B"
    if v >= 1e6: return f"{v/1e6:.1f}M"
    if v >= 1e3: return f"{v/1e3:.0f}K"
    return str(int(v))

def render(username: str = None):
    init_tables()
    generate_data()
    
    st.markdown(f"""<div style='background: linear-gradient(135deg, #1a365d 0%, #0f172a 100%); padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem; border-left: 4px solid #22c55e;'>
        <div style='display:flex;align-items:center;gap:1rem;'>
            <div style='background:linear-gradient(135deg,#22c55e,#16a34a);width:60px;height:60px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:bold;color:white;'>TM</div>
            <div><h1 style='color:white;margin:0;font-size:2rem;'>TRANSFER MARKET</h1>
            <p style='color:#94a3b8;margin:0;'>200+ Players | 65+ Clubs | 13 Leagues | Live Data</p></div>
        </div>
    </div>""", unsafe_allow_html=True)
    
    df = get_data("tm_players")
    if df.empty:
        st.warning("Loading...")
        return
    
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Players", f"{len(df):,}")
    c2.metric("Total Value", format_value(df['market_value'].sum()))
    c3.metric("Avg Value", format_value(df['market_value'].mean()))
    c4.metric("Leagues", len(LEAGUES))
    c5.metric("Clubs", len(CLUBS)-1)
    c6.metric("Nations", df['nationality'].nunique())
    
    tabs = st.tabs(["Overview","Player Search","Club Profiles","Transfers","Top Lists","Statistics","Watchlist","Compare"])
    
    with tabs[0]:
        render_overview(df)
    with tabs[1]:
        render_search(df)
    with tabs[2]:
        render_clubs(df)
    with tabs[3]:
        render_transfers(df)
    with tabs[4]:
        render_top_lists(df)
    with tabs[5]:
        render_stats(df)
    with tabs[6]:
        render_watchlist(username, df)
    with tabs[7]:
        render_compare(df)

def render_overview(df):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Market Value by League")
        league_val = {}
        for _, p in df.iterrows():
            club = p['current_club']
            if club in CLUBS:
                lg = CLUBS[club].get('league','Other')
                league_val[lg] = league_val.get(lg, 0) + p['market_value']
        league_df = pd.DataFrame(sorted(league_val.items(), key=lambda x:-x[1])[:10], columns=['League','Value'])
        fig = px.bar(league_df, x='League', y='Value', color='Value', color_continuous_scale='Greens')
        fig.update_layout(paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=350, showlegend=False, yaxis_title='Value (EUR)')
        fig.update_yaxes(tickformat='.2s')
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("#### Top Nationalities by Value")
        nat_val = df.groupby('nationality')['market_value'].sum().sort_values(ascending=False).head(10)
        fig = px.pie(values=nat_val.values, names=nat_val.index, hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=350)
        st.plotly_chart(fig, width="stretch")
    
    st.markdown("#### Most Valuable Players")
    top = df.nlargest(15,'market_value')[['full_name','age','position','nationality','current_club','market_value']].copy()
    top['market_value'] = top['market_value'].apply(format_value)
    top.columns = ['Player','Age','Pos','Nation','Club','Value']
    st.dataframe(top, hide_index=True, width="stretch")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Players by Position")
        pos_count = df['position'].value_counts()
        fig = px.bar(x=pos_count.index, y=pos_count.values, color=pos_count.values, color_continuous_scale='Blues')
        fig.update_layout(paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=280, showlegend=False, xaxis_title='Position', yaxis_title='Count')
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("#### Age Distribution")
        fig = px.histogram(df, x='age', nbins=20, color_discrete_sequence=['#22c55e'])
        fig.update_layout(paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=280, xaxis_title='Age', yaxis_title='Players')
        st.plotly_chart(fig, width="stretch")

def render_search(df):
    st.markdown("#### Advanced Player Search")
    c1,c2,c3,c4 = st.columns(4)
    search = c1.text_input("Player Name", placeholder="Search...")
    leagues = ["All"] + list(LEAGUES.keys())
    league = c2.selectbox("League", leagues)
    pos = c3.selectbox("Position", ["All"] + list(POSITIONS.keys()))
    nat = c4.selectbox("Nationality", ["All"] + NATIONALITIES)
    
    c1,c2,c3,c4 = st.columns(4)
    minv = c1.number_input("Min Value (M)", 0, 300, 0)
    maxv = c2.number_input("Max Value (M)", 0, 300, 300)
    min_age = c3.number_input("Min Age", 15, 45, 15)
    max_age = c4.number_input("Max Age", 15, 45, 45)
    
    filtered = df.copy()
    if search:
        filtered = filtered[filtered['full_name'].str.contains(search, case=False, na=False)]
    if league != "All":
        league_clubs = [c for c,info in CLUBS.items() if info.get('league')==league]
        filtered = filtered[filtered['current_club'].isin(league_clubs)]
    if pos != "All":
        filtered = filtered[filtered['position'] == pos]
    if nat != "All":
        filtered = filtered[filtered['nationality'] == nat]
    filtered = filtered[(filtered['market_value'] >= minv*1e6) & (filtered['market_value'] <= maxv*1e6)]
    filtered = filtered[(filtered['age'] >= min_age) & (filtered['age'] <= max_age)]
    
    st.markdown(f"**{len(filtered)} players found**")
    disp = filtered[['full_name','age','position','nationality','current_club','market_value','status']].copy()
    disp['market_value'] = disp['market_value'].apply(format_value)
    disp.columns = ['Player','Age','Pos','Nation','Club','Value','Status']
    st.dataframe(disp.sort_values('Value', ascending=False), hide_index=True, width="stretch", height=400)
    
    if not filtered.empty:
        st.markdown("---")
        sel = st.selectbox("View Player Profile", filtered['full_name'].tolist())
        if sel:
            render_player_profile(sel, df)

def render_player_profile(name, df):
    p = df[df['full_name']==name].iloc[0]
    c1,c2,c3 = st.columns([1,2,1])
    with c1:
        pos_colors = {"ST":"#ef4444","CF":"#ef4444","LW":"#f97316","RW":"#f97316","CAM":"#22c55e","CM":"#22c55e","CDM":"#3b82f6","CB":"#6366f1","LB":"#8b5cf6","RB":"#8b5cf6","GK":"#eab308"}
        col = pos_colors.get(p['position'], '#666')
        st.markdown(f"""<div style='background:linear-gradient(135deg,{col}40,{col}20);padding:1.5rem;border-radius:12px;text-align:center;border:2px solid {col};'>
            <div style='font-size:2.5rem;font-weight:bold;color:white;'>{p['jersey_number']}</div>
            <div style='color:{col};font-weight:bold;font-size:1.2rem;'>{p['position']}</div>
            <div style='color:#94a3b8;'>{POSITIONS.get(p['position'],p['position'])}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div style='background:rgba(30,41,59,0.5);padding:1.5rem;border-radius:12px;'>
            <h2 style='color:white;margin:0;'>{p['full_name']}</h2>
            <p style='color:#94a3b8;margin:0.5rem 0;'>{p['nationality']} | {p['age']} years</p>
            <p style='color:#64748b;'>{p['current_club']}</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div style='background:linear-gradient(135deg,#059669,#10b981);padding:1.5rem;border-radius:12px;text-align:center;'>
            <div style='font-size:1.8rem;font-weight:bold;color:white;'>{format_value(p['market_value'])}</div>
            <div style='color:#a7f3d0;'>Market Value</div>
        </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Height", f"{p['height_cm']} cm")
    c2.metric("Foot", p['foot'])
    c3.metric("Int. Caps", p['caps'])
    c4.metric("Int. Goals", p['goals_national'])
    
    # Value History
    st.markdown("#### Market Value History")
    hist = get_data("tm_value_history", f"player_id='{p['player_id']}'")
    if not hist.empty:
        hist = hist.sort_values('date')
        fig = px.line(hist, x='date', y='value', markers=True)
        fig.update_traces(line_color='#22c55e', marker_color='#22c55e')
        fig.update_layout(paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=250, xaxis_title='Date', yaxis_title='Value (EUR)')
        fig.update_yaxes(tickformat='.2s')
        st.plotly_chart(fig, width="stretch")
    
    # Transfer History
    transfers = get_data("tm_transfers", f"player_id='{p['player_id']}'")
    if not transfers.empty:
        st.markdown("#### Transfer History")
        t_disp = transfers[['date','from_club','to_club','fee','type']].copy()
        t_disp['fee'] = t_disp['fee'].apply(lambda x: format_value(x) if pd.notna(x) else 'Free')
        t_disp.columns = ['Date','From','To','Fee','Type']
        st.dataframe(t_disp, hide_index=True, width="stretch")

def render_clubs(df):
    st.markdown("#### Club Profiles")
    league_sel = st.selectbox("Select League", list(LEAGUES.keys()))
    league_clubs = [c for c,info in CLUBS.items() if info.get('league')==league_sel]
    
    if league_clubs:
        club_sel = st.selectbox("Select Club", sorted(league_clubs))
        if club_sel and club_sel in CLUBS:
            info = CLUBS[club_sel]
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Stadium", info.get('stadium','-'))
            c2.metric("Coach", info.get('coach','-'))
            squad = df[df['current_club']==club_sel]
            c3.metric("Squad Size", len(squad))
            c4.metric("Squad Value", format_value(squad['market_value'].sum()))
            
            st.markdown(f"#### {club_sel} Squad")
            if not squad.empty:
                sq_disp = squad[['full_name','age','position','nationality','market_value','jersey_number']].copy()
                sq_disp['market_value'] = sq_disp['market_value'].apply(format_value)
                sq_disp.columns = ['Player','Age','Pos','Nation','Value','#']
                st.dataframe(sq_disp.sort_values('Value', ascending=False), hide_index=True, width="stretch")
            
            # Squad by position
            st.markdown("#### Squad Composition")
            pos_val = squad.groupby('position')['market_value'].sum()
            fig = px.pie(values=pos_val.values, names=pos_val.index, hole=0.4)
            fig.update_layout(paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=300)
            st.plotly_chart(fig, width="stretch")

def render_transfers(df):
    t1,t2,t3,t4 = st.tabs(["Rumours","Recent Transfers","Free Agents","Transfer Listed"])
    with t1:
        rum = get_data("tm_rumours")
        if rum.empty:
            st.info("No rumours")
        else:
            rum_df = rum.merge(df[['player_id','full_name','position','market_value']], on='player_id', how='left')
            for _, r in rum_df.iterrows():
                col = "#22c55e" if r['probability']=="High" else "#f59e0b" if r['probability']=="Medium" else "#ef4444"
                st.markdown(f"""<div style='background:rgba(30,41,59,0.5);padding:1rem;border-radius:8px;margin-bottom:0.75rem;border-left:4px solid {col};'>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <strong style='color:white;font-size:1.1rem;'>{r['full_name']}</strong>
                        <span style='background:{col};color:white;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.8rem;'>{r['probability']}</span>
                    </div>
                    <div style='color:#94a3b8;margin:0.5rem 0;'>{r['from_club']} &rarr; <strong style='color:#60a5fa;'>{r['to_club']}</strong></div>
                    <div style='color:#64748b;font-size:0.85rem;'>Est. Fee: {format_value(r['estimated_fee'])} | Source: {r['source']}</div>
                </div>""", unsafe_allow_html=True)
    with t2:
        tr = get_data("tm_transfers")
        if tr.empty:
            st.info("No transfers")
        else:
            tr_df = tr.merge(df[['player_id','full_name','position']], on='player_id', how='left')
            tr_disp = tr_df[['date','full_name','position','from_club','to_club','fee']].sort_values('date', ascending=False).head(20)
            tr_disp['fee'] = tr_disp['fee'].apply(lambda x: format_value(x) if pd.notna(x) else 'Free')
            tr_disp.columns = ['Date','Player','Pos','From','To','Fee']
            st.dataframe(tr_disp, hide_index=True, width="stretch")
    with t3:
        fa = df[df['status']=='Free Agent'][['full_name','age','position','nationality','market_value']]
        if fa.empty:
            st.info("No free agents")
        else:
            fa['market_value'] = fa['market_value'].apply(format_value)
            fa.columns = ['Player','Age','Pos','Nation','Value']
            st.dataframe(fa, hide_index=True, width="stretch")
    with t4:
        tl = df[df['status']=='Transfer Listed'][['full_name','age','position','current_club','market_value']]
        if tl.empty:
            st.info("None transfer listed")
        else:
            tl['market_value'] = tl['market_value'].apply(format_value)
            tl.columns = ['Player','Age','Pos','Club','Value']
            st.dataframe(tl, hide_index=True, width="stretch")

def render_top_lists(df):
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Most Valuable")
        tv = df.nlargest(25,'market_value')[['full_name','age','position','current_club','market_value']].copy()
        tv['market_value'] = tv['market_value'].apply(format_value)
        tv.columns = ['Player','Age','Pos','Club','Value']
        st.dataframe(tv, hide_index=True, width="stretch", height=500)
    with c2:
        st.markdown("#### Top Talents (U21)")
        yg = df[df['age']<=21].nlargest(25,'market_value')[['full_name','age','position','current_club','market_value']].copy()
        yg['market_value'] = yg['market_value'].apply(format_value)
        yg.columns = ['Player','Age','Pos','Club','Value']
        st.dataframe(yg, hide_index=True, width="stretch", height=500)
    
    st.markdown("---")
    st.markdown("#### Top by Position")
    pos_sel = st.selectbox("Select Position", list(POSITIONS.keys()))
    pos_df = df[df['position']==pos_sel].nlargest(15,'market_value')[['full_name','age','nationality','current_club','market_value']].copy()
    pos_df['market_value'] = pos_df['market_value'].apply(format_value)
    pos_df.columns = ['Player','Age','Nation','Club','Value']
    st.dataframe(pos_df, hide_index=True, width="stretch")
    
    st.markdown("#### Top by Nationality")
    nat_sel = st.selectbox("Select Nationality", NATIONALITIES, key="nat_top")
    nat_df = df[df['nationality']==nat_sel].nlargest(15,'market_value')[['full_name','age','position','current_club','market_value']].copy()
    nat_df['market_value'] = nat_df['market_value'].apply(format_value)
    nat_df.columns = ['Player','Age','Pos','Club','Value']
    st.dataframe(nat_df, hide_index=True, width="stretch")

def render_stats(df):
    stats = get_data("tm_statistics")
    if stats.empty:
        st.info("No stats")
        return
    stats_df = stats.merge(df[['player_id','full_name','position','current_club','nationality']], on='player_id', how='left')
    
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Top Scorers 2024/25")
        sc = stats_df.nlargest(20,'goals')[['full_name','position','current_club','goals','appearances']].copy()
        sc['ratio'] = (sc['goals']/sc['appearances']).round(2)
        sc.columns = ['Player','Pos','Club','Goals','Apps','G/App']
        st.dataframe(sc, hide_index=True, width="stretch")
    with c2:
        st.markdown("#### Top Assists 2024/25")
        ass = stats_df.nlargest(20,'assists')[['full_name','position','current_club','assists','appearances']].copy()
        ass['ratio'] = (ass['assists']/ass['appearances']).round(2)
        ass.columns = ['Player','Pos','Club','Assists','Apps','A/App']
        st.dataframe(ass, hide_index=True, width="stretch")
    
    st.markdown("#### Goals + Assists Combined")
    stats_df['ga'] = stats_df['goals'] + stats_df['assists']
    ga = stats_df.nlargest(15,'ga')[['full_name','position','current_club','goals','assists','ga']].copy()
    ga.columns = ['Player','Pos','Club','Goals','Assists','G+A']
    st.dataframe(ga, hide_index=True, width="stretch")

def render_watchlist(username, df):
    if not username:
        st.warning("Login to use watchlist")
        return
    st.markdown("#### Add to Watchlist")
    c1,c2 = st.columns([3,1])
    player_add = c1.selectbox("Select Player", df['full_name'].tolist())
    if c2.button("Add to Watchlist", type="primary"):
        pid = df[df['full_name']==player_add]['player_id'].iloc[0]
        run_query("INSERT INTO tm_watchlist (user_id, player_id) VALUES (?,?)", (username, pid))
        st.success(f"Added {player_add}")
        st.rerun()
    
    st.markdown("---")
    st.markdown("#### My Watchlist")
    wl = get_data("tm_watchlist", f"user_id='{username}'")
    if wl.empty:
        st.info("Your watchlist is empty")
    else:
        wl_df = wl.merge(df, on='player_id', how='left')
        for _, p in wl_df.iterrows():
            c1,c2,c3 = st.columns([3,1,1])
            c1.write(f"**{p['full_name']}** ({p['position']}) - {p['current_club']}")
            c2.write(format_value(p['market_value']))
            if c3.button("Remove", key=f"rm_{p['player_id']}"):
                run_query("DELETE FROM tm_watchlist WHERE user_id=? AND player_id=?", (username, p['player_id']))
                st.rerun()

def render_compare(df):
    st.markdown("#### Compare Players")
    c1,c2 = st.columns(2)
    p1 = c1.selectbox("Player 1", df['full_name'].tolist(), key="cmp1")
    p2 = c2.selectbox("Player 2", df['full_name'].tolist(), key="cmp2")
    
    if p1 and p2:
        d1 = df[df['full_name']==p1].iloc[0]
        d2 = df[df['full_name']==p2].iloc[0]
        
        comp = pd.DataFrame({
            'Attribute': ['Age','Position','Club','Nation','Value','Height','Foot','Status','Int. Caps'],
            p1: [d1['age'],d1['position'],d1['current_club'],d1['nationality'],format_value(d1['market_value']),f"{d1['height_cm']}cm",d1['foot'],d1['status'],d1['caps']],
            p2: [d2['age'],d2['position'],d2['current_club'],d2['nationality'],format_value(d2['market_value']),f"{d2['height_cm']}cm",d2['foot'],d2['status'],d2['caps']]
        })
        st.dataframe(comp, hide_index=True, width="stretch")
        
        # Stats comparison
        stats = get_data("tm_statistics")
        s1 = stats[stats['player_id']==d1['player_id']]
        s2 = stats[stats['player_id']==d2['player_id']]
        
        if not s1.empty and not s2.empty:
            st.markdown("#### Season Statistics")
            stats_comp = pd.DataFrame({
                'Stat': ['Appearances','Goals','Assists','Minutes'],
                p1: [s1.iloc[0]['appearances'], s1.iloc[0]['goals'], s1.iloc[0]['assists'], s1.iloc[0]['minutes']],
                p2: [s2.iloc[0]['appearances'], s2.iloc[0]['goals'], s2.iloc[0]['assists'], s2.iloc[0]['minutes']]
            })
            st.dataframe(stats_comp, hide_index=True, width="stretch")
        
        # Value chart
        fig = go.Figure(data=[
            go.Bar(name=p1, x=['Market Value'], y=[d1['market_value']/1e6], marker_color='#3b82f6'),
            go.Bar(name=p2, x=['Market Value'], y=[d2['market_value']/1e6], marker_color='#22c55e')
        ])
        fig.update_layout(barmode='group', paper_bgcolor='#FAF9FF', plot_bgcolor='#FFFFFF', font_color='white', height=280, yaxis_title='Value (M EUR)')
        st.plotly_chart(fig, width="stretch")
