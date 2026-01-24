# ============================================================================
# ProInvestiX Enterprise - SQLAlchemy Database Models
# Fase 0.2 - Complete Database Schema
# ============================================================================

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, Date,
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base

# ============================================================================
# AUTH & USERS
# ============================================================================

class User(Base):
    """Gebruikers tabel - authenticatie en autorisatie"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="User")  # SuperAdmin, Admin, User, Scout, etc.
    
    # Profile
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    avatar_url = Column(String(255))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    """Gebruiker sessies"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")


class AuditLog(Base):
    """Audit logging voor alle acties"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    username = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    module = Column(String(50))
    entity_type = Column(String(50))
    entity_id = Column(String(50))
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    details = Column(Text)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="audit_logs")


# ============================================================================
# NTSP - NATIONAL TALENT SCOUTING PLATFORM
# ============================================================================

class Talent(Base):
    """NTSP Talent profielen"""
    __tablename__ = "talents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(String(20), unique=True, nullable=False, index=True)  # NTSP-XXXXX
    
    # Personal
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    place_of_birth = Column(String(100))
    nationality = Column(String(50), nullable=False)
    dual_nationality = Column(String(50))
    passport_number = Column(String(50))
    
    # Diaspora
    is_diaspora = Column(Boolean, default=False)
    diaspora_country = Column(String(50))
    diaspora_city = Column(String(100))
    years_abroad = Column(Integer)
    speaks_arabic = Column(Boolean, default=False)
    speaks_french = Column(Boolean, default=False)
    other_languages = Column(String(200))
    
    # Contact
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))
    city = Column(String(100))
    country = Column(String(50))
    
    # Family (for youth)
    parent_name = Column(String(100))
    parent_phone = Column(String(20))
    parent_email = Column(String(100))
    
    # Football
    primary_position = Column(String(10), nullable=False)  # GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
    secondary_position = Column(String(10))
    preferred_foot = Column(String(10), default="Right")
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    
    # Current club
    current_club = Column(String(100))
    current_club_country = Column(String(50))
    current_league = Column(String(100))
    contract_start = Column(Date)
    contract_end = Column(Date)
    jersey_number = Column(Integer)
    
    # Status & Scores
    status = Column(String(20), default="Prospect")  # Prospect, Monitored, Priority, Signed, Inactive
    overall_score = Column(Float, default=0)
    potential_score = Column(Float, default=0)
    market_value = Column(Float, default=0)
    
    # Scout info
    discovered_by = Column(String(100))
    discovery_date = Column(Date)
    last_evaluation = Column(DateTime)
    evaluation_count = Column(Integer, default=0)
    
    # Flags
    priority_level = Column(String(10), default="Normal")  # Low, Normal, High, Critical
    national_team_eligible = Column(Boolean, default=True)
    interest_in_morocco = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Media
    photo_url = Column(String(255))
    video_url = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String(50))
    
    # Relationships
    evaluations = relationship("TalentEvaluation", back_populates="talent")
    medical_records = relationship("TalentMedical", back_populates="talent")
    mental_evaluations = relationship("TalentMentalEval", back_populates="talent")
    career_history = relationship("TalentCareer", back_populates="talent")


class TalentEvaluation(Base):
    """Scout evaluaties"""
    __tablename__ = "talent_evaluations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String(20), unique=True, nullable=False)
    talent_id = Column(Integer, ForeignKey("talents.id"), nullable=False)
    
    # Scout
    scout_id = Column(Integer, ForeignKey("scouts.id"))
    scout_name = Column(String(100))
    evaluation_date = Column(Date, nullable=False)
    match_observed = Column(String(200))
    match_date = Column(Date)
    
    # Technical scores (1-100)
    score_ball_control = Column(Integer)
    score_passing = Column(Integer)
    score_dribbling = Column(Integer)
    score_shooting = Column(Integer)
    score_heading = Column(Integer)
    score_first_touch = Column(Integer)
    
    # Physical scores (1-100)
    score_speed = Column(Integer)
    score_acceleration = Column(Integer)
    score_stamina = Column(Integer)
    score_strength = Column(Integer)
    score_jumping = Column(Integer)
    score_agility = Column(Integer)
    
    # Mental scores (1-100)
    score_positioning = Column(Integer)
    score_vision = Column(Integer)
    score_composure = Column(Integer)
    score_leadership = Column(Integer)
    score_work_rate = Column(Integer)
    score_decision_making = Column(Integer)
    
    # Goalkeeper specific
    score_reflexes = Column(Integer)
    score_handling = Column(Integer)
    score_kicking = Column(Integer)
    score_positioning_gk = Column(Integer)
    
    # Totals
    overall_technical = Column(Float)
    overall_physical = Column(Float)
    overall_mental = Column(Float)
    overall_score = Column(Float)
    potential_score = Column(Float)
    
    # Recommendation
    recommendation = Column(String(50))  # Sign, Monitor, Pass, Follow-up
    follow_up_required = Column(Boolean, default=False)
    recommended_for_academy = Column(Boolean, default=False)
    recommended_for_national = Column(Boolean, default=False)
    
    # Notes
    strengths = Column(Text)
    weaknesses = Column(Text)
    development_areas = Column(Text)
    notes = Column(Text)
    video_clips = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    talent = relationship("Talent", back_populates="evaluations")
    scout = relationship("Scout", back_populates="evaluations")


class TalentMedical(Base):
    """Medische records"""
    __tablename__ = "talent_medical"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(Integer, ForeignKey("talents.id"), nullable=False)
    
    # Basic
    blood_type = Column(String(5))
    allergies = Column(Text)
    chronic_conditions = Column(Text)
    current_medications = Column(Text)
    
    # Physical
    height_cm = Column(Integer)
    weight_kg = Column(Integer)
    body_fat_pct = Column(Float)
    muscle_mass_kg = Column(Float)
    bmi = Column(Float)
    
    # Fitness tests
    vo2_max = Column(Float)
    sprint_10m = Column(Float)
    sprint_30m = Column(Float)
    vertical_jump = Column(Integer)
    agility_test = Column(Float)
    beep_test = Column(Float)
    
    # Injuries
    injury_history = Column(Text)
    surgery_history = Column(Text)
    current_injuries = Column(Text)
    injury_risk = Column(String(20))
    
    # Clearance
    last_checkup = Column(Date)
    clearance_status = Column(String(20), default="Pending")
    clearance_expiry = Column(Date)
    doctor_name = Column(String(100))
    doctor_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    talent = relationship("Talent", back_populates="medical_records")


class TalentMentalEval(Base):
    """Mentale evaluaties"""
    __tablename__ = "talent_mental_evaluations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(Integer, ForeignKey("talents.id"), nullable=False)
    
    psychologist_name = Column(String(100))
    evaluation_date = Column(Date, nullable=False)
    evaluation_type = Column(String(50))
    
    # Scores (1-10)
    score_stress_mgmt = Column(Integer)
    score_pressure = Column(Integer)
    score_confidence = Column(Integer)
    score_motivation = Column(Integer)
    score_focus = Column(Integer)
    score_resilience = Column(Integer)
    score_team_dynamics = Column(Integer)
    score_communication = Column(Integer)
    
    # Personality
    personality_type = Column(String(20))
    learning_style = Column(String(20))
    communication_style = Column(String(20))
    
    # Risk factors
    burnout_risk = Column(String(10), default="Low")
    homesickness_risk = Column(String(10), default="Low")
    adaptation_concerns = Column(Text)
    
    # Diaspora specific
    cultural_identity_score = Column(Integer)
    morocco_connection = Column(String(20))
    language_barrier = Column(String(20))
    integration_support = Column(Boolean, default=False)
    
    recommendations = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    talent = relationship("Talent", back_populates="mental_evaluations")


class TalentCareer(Base):
    """Carrière geschiedenis"""
    __tablename__ = "talent_career_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    talent_id = Column(Integer, ForeignKey("talents.id"), nullable=False)
    
    club_name = Column(String(100), nullable=False)
    club_country = Column(String(50))
    league = Column(String(100))
    team_level = Column(String(20))  # First Team, U23, U21, U19, etc.
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    
    transfer_type = Column(String(20))  # Permanent, Loan, Free, Youth
    is_loan = Column(Boolean, default=False)
    
    # Stats
    appearances = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    minutes = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    talent = relationship("Talent", back_populates="career_history")


class Scout(Base):
    """Scouts"""
    __tablename__ = "scouts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scout_id = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    
    region = Column(String(50))  # Europe, Africa, Americas, Asia, etc.
    countries = Column(String(200))  # Comma-separated
    specialization = Column(String(100))  # Youth, First Team, Goalkeeper, etc.
    
    license_level = Column(String(20))
    experience_years = Column(Integer)
    
    is_active = Column(Boolean, default=True)
    total_evaluations = Column(Integer, default=0)
    total_signings = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    evaluations = relationship("TalentEvaluation", back_populates="scout")


class TalentWatchlist(Base):
    """Watchlist"""
    __tablename__ = "talent_watchlist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    talent_id = Column(Integer, ForeignKey("talents.id"), nullable=False)
    priority = Column(String(10), default="Normal")
    notes = Column(Text)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('user_id', 'talent_id'),)


# ============================================================================
# TRANSFERS
# ============================================================================

class Transfer(Base):
    """Transfer records"""
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_id = Column(String(20), unique=True, nullable=False)
    
    talent_id = Column(Integer, ForeignKey("talents.id"))
    player_name = Column(String(100), nullable=False)
    
    from_club = Column(String(100), nullable=False)
    from_country = Column(String(50))
    to_club = Column(String(100), nullable=False)
    to_country = Column(String(50))
    
    transfer_type = Column(String(20), nullable=False)  # Permanent, Loan, Free, Youth
    transfer_date = Column(Date, nullable=False)
    
    # Financial
    transfer_fee = Column(Float, default=0)
    add_ons = Column(Float, default=0)
    sell_on_pct = Column(Float, default=0)
    agent_fee = Column(Float, default=0)
    
    # Solidarity & Training
    training_compensation = Column(Float, default=0)
    solidarity_contribution = Column(Float, default=0)
    foundation_contribution = Column(Float, default=0)  # 0.5% Masterplan
    
    # Contract
    contract_length_years = Column(Integer)
    salary_annual = Column(Float)
    release_clause = Column(Float)
    
    # Smart contract
    smart_contract_hash = Column(String(66))
    blockchain_verified = Column(Boolean, default=False)
    
    status = Column(String(20), default="Pending")  # Pending, Completed, Cancelled
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class TransferCompensation(Base):
    """Training compensation & solidarity"""
    __tablename__ = "transfer_compensations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transfer_id = Column(Integer, ForeignKey("transfers.id"), nullable=False)
    
    club_name = Column(String(100), nullable=False)
    club_country = Column(String(50))
    compensation_type = Column(String(20), nullable=False)  # Training, Solidarity
    
    training_years = Column(Integer)
    age_from = Column(Integer)
    age_to = Column(Integer)
    
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="Pending")
    paid_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# ACADEMY
# ============================================================================

class Academy(Base):
    """Academies"""
    __tablename__ = "academies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    academy_id = Column(String(20), unique=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(50), default="Morocco")
    
    academy_type = Column(String(50))  # Youth, Professional, Development, etc.
    certification_level = Column(String(20))  # Basic, Bronze, Silver, Gold, Elite
    parent_club = Column(String(100))
    
    # Capacity
    total_capacity = Column(Integer, default=0)
    current_enrollment = Column(Integer, default=0)
    num_pitches = Column(Integer, default=0)
    
    # Contact
    director_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(255))
    
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teams = relationship("AcademyTeam", back_populates="academy")
    staff = relationship("AcademyStaff", back_populates="academy")
    enrollments = relationship("AcademyEnrollment", back_populates="academy")


class AcademyTeam(Base):
    """Academy teams"""
    __tablename__ = "academy_teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(String(20), unique=True, nullable=False)
    academy_id = Column(Integer, ForeignKey("academies.id"), nullable=False)
    
    team_name = Column(String(100), nullable=False)
    age_group = Column(String(10), nullable=False)  # U13, U14, U15, etc.
    head_coach = Column(String(100))
    assistant_coach = Column(String(100))
    
    max_players = Column(Integer, default=25)
    current_players = Column(Integer, default=0)
    
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    academy = relationship("Academy", back_populates="teams")


class AcademyStaff(Base):
    """Academy staff"""
    __tablename__ = "academy_staff"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(String(20), unique=True, nullable=False)
    academy_id = Column(Integer, ForeignKey("academies.id"), nullable=False)
    
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)  # Head Coach, Assistant, Physio, etc.
    
    email = Column(String(100))
    phone = Column(String(20))
    
    coaching_license = Column(String(20))
    specialization = Column(String(100))
    
    start_date = Column(Date)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    academy = relationship("Academy", back_populates="staff")


class AcademyEnrollment(Base):
    """Academy enrollments"""
    __tablename__ = "academy_enrollments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    enrollment_id = Column(String(20), unique=True, nullable=False)
    academy_id = Column(Integer, ForeignKey("academies.id"), nullable=False)
    talent_id = Column(Integer, ForeignKey("talents.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("academy_teams.id"))
    
    enrollment_date = Column(Date, nullable=False)
    enrollment_type = Column(String(20), nullable=False)  # Full-time, Part-time, Trial
    is_residential = Column(Boolean, default=False)
    
    scholarship_pct = Column(Float, default=0)
    monthly_fee = Column(Float, default=0)
    
    status = Column(String(20), default="Active")
    end_date = Column(Date)
    end_reason = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    academy = relationship("Academy", back_populates="enrollments")


# ============================================================================
# TICKETCHAIN
# ============================================================================

class Event(Base):
    """TicketChain events"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(20), unique=True, nullable=False)
    
    name = Column(String(200), nullable=False)
    event_type = Column(String(50))  # Match, Concert, Festival, Conference
    
    venue = Column(String(200), nullable=False)
    city = Column(String(100))
    country = Column(String(50))
    
    date = Column(DateTime, nullable=False)
    doors_open = Column(DateTime)
    
    capacity = Column(Integer, nullable=False)
    tickets_sold = Column(Integer, default=0)
    tickets_available = Column(Integer)
    
    # Pricing
    price_min = Column(Float)
    price_max = Column(Float)
    
    # Integration
    mobility_enabled = Column(Boolean, default=False)
    diaspora_package = Column(Boolean, default=False)
    
    status = Column(String(20), default="Upcoming")  # Upcoming, OnSale, SoldOut, Past, Cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tickets = relationship("Ticket", back_populates="event")


class Ticket(Base):
    """TicketChain tickets"""
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_hash = Column(String(66), unique=True, nullable=False, index=True)
    
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner_name = Column(String(100))
    
    seat_section = Column(String(50))
    seat_row = Column(String(10))
    seat_number = Column(String(10))
    seat_info = Column(String(100))
    
    category = Column(String(50))  # VIP, Standard, Economy
    price = Column(Float, nullable=False)
    
    # Blockchain
    minted_at = Column(DateTime, default=datetime.utcnow)
    block_number = Column(Integer)
    transaction_hash = Column(String(66))
    
    # Status
    status = Column(String(20), default="Valid")  # Valid, Used, Expired, Cancelled, Resold
    used_at = Column(DateTime)
    
    # QR
    qr_code = Column(Text)
    
    # Linked bookings
    mobility_booking_id = Column(Integer)
    diaspora_package_id = Column(Integer)
    
    event = relationship("Event", back_populates="tickets")


class LoyaltyPoints(Base):
    """Loyalty program"""
    __tablename__ = "loyalty_points"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    points_balance = Column(Integer, default=0)
    total_earned = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    
    tier = Column(String(20), default="Bronze")  # Bronze, Silver, Gold, Platinum
    tickets_purchased = Column(Integer, default=0)
    
    last_activity = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# FOUNDATION BANK
# ============================================================================

class FoundationDonation(Base):
    """Foundation donations"""
    __tablename__ = "foundation_donations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    donation_id = Column(String(20), unique=True, nullable=False)
    
    donor_id = Column(Integer, ForeignKey("users.id"))
    donor_name = Column(String(100))
    donor_email = Column(String(100))
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    
    donation_type = Column(String(50))  # OneTime, Monthly, Annual, Sadaka
    project = Column(String(100))
    
    is_anonymous = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    
    payment_method = Column(String(20))
    payment_reference = Column(String(100))
    
    receipt_sent = Column(Boolean, default=False)
    receipt_number = Column(String(50))
    
    status = Column(String(20), default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)


class FoundationContribution(Base):
    """Auto 0.5% contributions from transfers/tickets"""
    __tablename__ = "foundation_contributions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contribution_id = Column(String(20), unique=True, nullable=False)
    
    source_type = Column(String(50), nullable=False)  # Transfer, Ticket, Subscription
    source_id = Column(String(50), nullable=False)
    
    amount = Column(Float, nullable=False)
    percentage = Column(Float, default=0.5)
    
    description = Column(String(200))
    auto_generated = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# DIASPORA WALLET
# ============================================================================

class Wallet(Base):
    """Diaspora wallets"""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_id = Column(String(20), unique=True, nullable=False)
    wallet_address = Column(String(66), unique=True, nullable=False, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Balance
    balance = Column(Float, default=0)
    currency = Column(String(3), default="EUR")
    
    # Diaspora info
    country_of_residence = Column(String(50))
    diaspora_region = Column(String(50))
    
    # KYC
    kyc_level = Column(Integer, default=0)  # 0, 1, 2, 3
    kyc_verified = Column(Boolean, default=False)
    
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    """Wallet transactions"""
    __tablename__ = "wallet_transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(20), unique=True, nullable=False)
    
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    
    type = Column(String(20), nullable=False)  # Deposit, Withdraw, Transfer, Payment
    direction = Column(String(10), nullable=False)  # In, Out
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    
    recipient_wallet = Column(String(66))
    recipient_name = Column(String(100))
    
    reference = Column(String(100))
    description = Column(String(200))
    
    # Blockchain
    blockchain_hash = Column(String(66))
    
    status = Column(String(20), default="Completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    wallet = relationship("Wallet", back_populates="transactions")


class DiasporaCard(Base):
    """Diaspora cards"""
    __tablename__ = "diaspora_cards"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String(20), unique=True, nullable=False)
    
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    card_type = Column(String(20), nullable=False)  # Standard, Gold, Platinum
    card_number_last4 = Column(String(4))
    
    expiry_date = Column(Date)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    
    daily_limit = Column(Float, default=1000)
    monthly_limit = Column(Float, default=10000)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# SUBSCRIPTIONS
# ============================================================================

class SubscriptionPlan(Base):
    """Subscription plans"""
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(String(20), unique=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    tier = Column(String(20), nullable=False)  # Basic, Standard, Premium, Enterprise
    billing_cycle = Column(String(20), nullable=False)  # Monthly, Annual
    
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    
    features = Column(Text)  # JSON array
    
    max_users = Column(Integer, default=1)
    api_calls_limit = Column(Integer)
    storage_gb = Column(Integer)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """User subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(String(20), unique=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    next_billing = Column(Date)
    
    status = Column(String(20), default="Active")  # Active, Paused, Cancelled, Expired
    auto_renew = Column(Boolean, default=True)
    
    payment_method = Column(String(20))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime)
    
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payments = relationship("SubscriptionPayment", back_populates="subscription")


class SubscriptionPayment(Base):
    """Subscription payments"""
    __tablename__ = "subscription_payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String(20), unique=True, nullable=False)
    
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR")
    
    billing_period_start = Column(Date)
    billing_period_end = Column(Date)
    
    payment_method = Column(String(20))
    payment_reference = Column(String(100))
    
    status = Column(String(20), default="Completed")
    paid_at = Column(DateTime)
    
    invoice_number = Column(String(50))
    invoice_url = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscription = relationship("Subscription", back_populates="payments")


# ============================================================================
# FANDORPEN
# ============================================================================

class FanDorp(Base):
    """Fan villages"""
    __tablename__ = "fandorpen"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fandorp_id = Column(String(20), unique=True, nullable=False)
    
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(50))
    
    location = Column(String(200))
    capacity = Column(Integer)
    
    # WK 2030
    host_nation = Column(String(50))  # Morocco, Spain, Portugal
    
    opening_date = Column(Date)
    closing_date = Column(Date)
    
    status = Column(String(20), default="Planning")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    volunteers = relationship("FanDorpVolunteer", back_populates="fandorp")
    shifts = relationship("FanDorpShift", back_populates="fandorp")
    incidents = relationship("FanDorpIncident", back_populates="fandorp")


class FanDorpVolunteer(Base):
    """Volunteers"""
    __tablename__ = "fandorp_volunteers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    volunteer_id = Column(String(20), unique=True, nullable=False)
    
    fandorp_id = Column(Integer, ForeignKey("fandorpen.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    
    nationality = Column(String(50))
    languages = Column(String(200))  # Comma-separated
    
    role = Column(String(50))  # Guide, Security, Medical, Transport, etc.
    skills = Column(Text)
    
    availability_start = Column(Date)
    availability_end = Column(Date)
    
    is_trained = Column(Boolean, default=False)
    training_completed = Column(DateTime)
    
    status = Column(String(20), default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    fandorp = relationship("FanDorp", back_populates="volunteers")
    shifts = relationship("FanDorpShift", back_populates="volunteer")


class FanDorpShift(Base):
    """Volunteer shifts"""
    __tablename__ = "fandorp_shifts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shift_id = Column(String(20), unique=True, nullable=False)
    
    fandorp_id = Column(Integer, ForeignKey("fandorpen.id"), nullable=False)
    volunteer_id = Column(Integer, ForeignKey("fandorp_volunteers.id"))
    
    shift_date = Column(Date, nullable=False)
    shift_type = Column(String(50))  # Morning, Afternoon, Evening, Night
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    
    role = Column(String(50))
    location = Column(String(100))
    
    status = Column(String(20), default="Scheduled")  # Scheduled, CheckedIn, Completed, NoShow
    check_in_time = Column(DateTime)
    check_out_time = Column(DateTime)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    fandorp = relationship("FanDorp", back_populates="shifts")
    volunteer = relationship("FanDorpVolunteer", back_populates="shifts")


class FanDorpIncident(Base):
    """Incidents"""
    __tablename__ = "fandorp_incidents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(20), unique=True, nullable=False)
    
    fandorp_id = Column(Integer, ForeignKey("fandorpen.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("fandorp_volunteers.id"))
    
    incident_type = Column(String(50), nullable=False)  # Medical, Security, Lost, Complaint
    severity = Column(String(20), default="Low")  # Low, Medium, High, Critical
    
    description = Column(Text, nullable=False)
    location = Column(String(100))
    
    involved_parties = Column(Text)
    nationality = Column(String(50))
    
    status = Column(String(20), default="Open")
    resolution = Column(Text)
    
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    
    fandorp = relationship("FanDorp", back_populates="incidents")


# ============================================================================
# IDENTITY & MAROC ID
# ============================================================================

class Identity(Base):
    """Identity Shield"""
    __tablename__ = "identities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    identity_id = Column(String(20), unique=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    
    full_name = Column(String(200), nullable=False)
    date_of_birth = Column(Date)
    nationality = Column(String(50))
    
    # Documents
    document_type = Column(String(20))  # Passport, ID, ResidencePermit
    document_number = Column(String(50))
    document_country = Column(String(50))
    document_expiry = Column(Date)
    
    # Verification
    verification_level = Column(Integer, default=0)  # 0-3
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(String(100))
    
    # Risk
    risk_level = Column(String(20), default="Low")
    fraud_score = Column(Integer, default=0)
    monitoring_enabled = Column(Boolean, default=False)
    
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)


class FraudAlert(Base):
    """Fraud alerts"""
    __tablename__ = "fraud_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(20), unique=True, nullable=False)
    
    identity_id = Column(Integer, ForeignKey("identities.id"))
    
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="Medium")
    
    description = Column(Text)
    evidence = Column(Text)
    
    auto_detected = Column(Boolean, default=True)
    detection_source = Column(String(100))
    
    status = Column(String(20), default="Active")
    resolution = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))


class MarocIdentity(Base):
    """Maroc ID Shield identities"""
    __tablename__ = "maroc_identities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    maroc_id = Column(String(20), unique=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    identity_id = Column(Integer, ForeignKey("identities.id"))
    
    # CIN (Carte d'Identité Nationale)
    cin_number = Column(String(20))
    cin_issued_at = Column(String(100))
    cin_expiry = Column(Date)
    
    # Digital ID
    digital_signature = Column(String(255))
    public_key = Column(Text)
    
    # Verification levels
    level_0_basic = Column(Boolean, default=False)
    level_1_documents = Column(Boolean, default=False)
    level_2_biometric = Column(Boolean, default=False)
    level_3_official = Column(Boolean, default=False)
    
    current_level = Column(Integer, default=0)
    
    # Diaspora
    is_diaspora = Column(Boolean, default=False)
    residence_country = Column(String(50))
    consulate = Column(String(100))
    
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# HAYAT HEALTH
# ============================================================================

class HayatSession(Base):
    """Mental health sessions"""
    __tablename__ = "hayat_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(20), unique=True, nullable=False)
    
    talent_id = Column(Integer, ForeignKey("talents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Anonymous code for privacy
    anonymous_code = Column(String(20))
    
    session_type = Column(String(50))  # Individual, Group, Crisis, Follow-up
    provider_name = Column(String(100))
    
    scheduled_at = Column(DateTime)
    duration_minutes = Column(Integer)
    
    # Encrypted notes
    notes_hash = Column(String(255))
    
    mood_before = Column(Integer)  # 1-10
    mood_after = Column(Integer)
    
    status = Column(String(20), default="Scheduled")
    completed_at = Column(DateTime)
    
    follow_up_needed = Column(Boolean, default=False)
    next_session = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class HayatCrisisAlert(Base):
    """Crisis alerts"""
    __tablename__ = "hayat_crisis_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(20), unique=True, nullable=False)
    
    talent_id = Column(Integer, ForeignKey("talents.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="Medium")
    
    trigger = Column(String(200))
    description = Column(Text)
    
    auto_detected = Column(Boolean, default=False)
    reporter = Column(String(100))
    
    status = Column(String(20), default="Active")
    response_actions = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)
    resolved_at = Column(DateTime)


# ============================================================================
# NIL - NEWS INTELLIGENCE LAB
# ============================================================================

class NILSignal(Base):
    """Misinformation signals"""
    __tablename__ = "nil_signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(20), unique=True, nullable=False)
    
    # Content
    title = Column(String(300), nullable=False)
    content = Column(Text)
    content_hash = Column(String(66))
    
    source_url = Column(String(500))
    source_platform = Column(String(50))
    
    # Classification
    signal_type = Column(String(50))  # Misinformation, Disinformation, Rumor, etc.
    category = Column(String(50))
    
    # Risk assessment
    risk_score = Column(Integer)  # 0-100
    reach_estimate = Column(Integer)
    virality_score = Column(Float)
    
    # Verification
    verification_status = Column(String(20), default="Pending")
    fact_check_result = Column(String(20))
    
    # Related
    related_entity = Column(String(100))
    related_entity_type = Column(String(50))
    
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    evidence = relationship("NILEvidence", back_populates="signal")


class NILEvidence(Base):
    """Evidence for signals"""
    __tablename__ = "nil_evidence"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String(20), unique=True, nullable=False)
    
    signal_id = Column(Integer, ForeignKey("nil_signals.id"), nullable=False)
    
    evidence_type = Column(String(50))  # Screenshot, Archive, Document, Testimony
    
    title = Column(String(200))
    description = Column(Text)
    
    file_url = Column(String(500))
    file_hash = Column(String(66))
    
    blockchain_hash = Column(String(66))
    
    collected_by = Column(String(100))
    collected_at = Column(DateTime, default=datetime.utcnow)
    
    signal = relationship("NILSignal", back_populates="evidence")


class NILFactCard(Base):
    """Fact cards"""
    __tablename__ = "nil_fact_cards"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String(20), unique=True, nullable=False)
    
    signal_id = Column(Integer, ForeignKey("nil_signals.id"))
    
    claim = Column(Text, nullable=False)
    verdict = Column(String(20), nullable=False)  # True, False, Misleading, Unverified
    
    explanation = Column(Text)
    sources = Column(Text)  # JSON array
    
    published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    
    views = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# ANTI-HATE SHIELD
# ============================================================================

class AntiHateIncident(Base):
    """Hate incidents"""
    __tablename__ = "antihate_incidents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(20), unique=True, nullable=False)
    
    # Target
    target_type = Column(String(50))  # Player, Coach, Fan, Official
    target_id = Column(Integer)
    target_name = Column(String(100))
    
    # Incident
    incident_type = Column(String(50), nullable=False)  # Racist, Sexist, Homophobic, etc.
    platform = Column(String(50))  # Twitter, Instagram, Stadium, etc.
    
    content = Column(Text)
    content_hash = Column(String(66))
    
    evidence_url = Column(String(500))
    screenshot_url = Column(String(500))
    
    # Assessment
    severity = Column(String(20), default="Medium")
    verified = Column(Boolean, default=False)
    
    # Response
    status = Column(String(20), default="Reported")
    action_taken = Column(Text)
    
    reported_by = Column(String(100))
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)


class AntiHateLegalCase(Base):
    """Legal cases"""
    __tablename__ = "antihate_legal_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(20), unique=True, nullable=False)
    
    incident_id = Column(Integer, ForeignKey("antihate_incidents.id"))
    
    case_type = Column(String(50))  # Criminal, Civil, Disciplinary
    jurisdiction = Column(String(50))
    
    defendant_info = Column(Text)
    
    status = Column(String(20), default="Open")
    filing_date = Column(Date)
    hearing_date = Column(Date)
    
    outcome = Column(String(100))
    penalty = Column(Text)
    
    lawyer_name = Column(String(100))
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# CONSULATE HUB
# ============================================================================

class ConsularDocument(Base):
    """Consular documents"""
    __tablename__ = "consular_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(20), unique=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    identity_id = Column(Integer, ForeignKey("identities.id"))
    
    document_type = Column(String(50), nullable=False)
    document_number = Column(String(50))
    
    file_url = Column(String(500))
    file_hash = Column(String(66))
    
    issued_at = Column(Date)
    expires_at = Column(Date)
    issued_by = Column(String(100))
    
    status = Column(String(20), default="Valid")
    created_at = Column(DateTime, default=datetime.utcnow)


class ConsularAppointment(Base):
    """Consular appointments"""
    __tablename__ = "consular_appointments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(String(20), unique=True, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    consulate = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=False)
    
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    status = Column(String(20), default="Scheduled")
    notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# INDEXES
# ============================================================================

# Add indexes for frequently queried columns
Index('idx_talents_nationality', Talent.nationality)
Index('idx_talents_status', Talent.status)
Index('idx_talents_position', Talent.primary_position)
Index('idx_transfers_date', Transfer.transfer_date)
Index('idx_events_date', Event.date)
Index('idx_tickets_status', Ticket.status)
Index('idx_nil_signals_status', NILSignal.status)
Index('idx_antihate_status', AntiHateIncident.status)
