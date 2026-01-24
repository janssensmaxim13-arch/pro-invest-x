# ProInvestiX Enterprise - Database Schema
## Fase 0.2 - Complete Database Documentatie

---

## OVERZICHT

| Metric | Waarde |
|--------|--------|
| SQLAlchemy Models | 45 |
| Hoofd Entiteiten | 24 |
| Relatie Tabellen | 21 |
| Indexes | 10 |

---

## DATABASE ARCHITECTUUR

```
┌─────────────────────────────────────────────────────────────────┐
│                         CORE LAYER                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │  Users  │  │Sessions │  │AuditLog │  │Identity │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       │            │            │            │                  │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
┌───────┼────────────┼────────────┼────────────┼──────────────────┐
│       ▼            ▼            ▼            ▼                  │
│                      BUSINESS LAYER                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                         NTSP                             │   │
│  │  Talents ─── Evaluations ─── Medical ─── Career         │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      TRANSFERS                           │   │
│  │  Transfers ─── Compensations ─── Contracts              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      TICKETCHAIN                         │   │
│  │  Events ─── Tickets ─── Loyalty                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      FINANCIAL                           │   │
│  │  Wallets ─── Transactions ─── Foundation ─── Subs       │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      WK 2030                             │   │
│  │  FanDorpen ─── Volunteers ─── Shifts ─── Incidents      │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      PROTECTION                          │   │
│  │  AntiHate ─── NIL ─── Hayat ─── MarocID                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ENTITY RELATIONSHIP DIAGRAM (Simplified)

```
                                    ┌──────────┐
                                    │  Users   │
                                    └────┬─────┘
                                         │
           ┌─────────────────────────────┼─────────────────────────────┐
           │                             │                             │
           ▼                             ▼                             ▼
    ┌──────────┐                  ┌──────────┐                  ┌──────────┐
    │ Talents  │                  │ Wallets  │                  │ Identity │
    └────┬─────┘                  └────┬─────┘                  └────┬─────┘
         │                             │                             │
    ┌────┴────┐                   ┌────┴────┐                   ┌────┴────┐
    │         │                   │         │                   │         │
    ▼         ▼                   ▼         ▼                   ▼         ▼
┌────────┐ ┌────────┐      ┌────────┐ ┌────────┐        ┌────────┐ ┌────────┐
│Evals   │ │Medical │      │Trans   │ │Cards   │        │Fraud   │ │MarocID │
└────────┘ └────────┘      └────────┘ └────────┘        └────────┘ └────────┘
```

---

## MODELS DETAIL

### 1. AUTH & USERS

#### User
```python
class User:
    id: int (PK)
    username: str (unique, indexed)
    email: str (unique, indexed)
    password_hash: str
    role: str  # SuperAdmin, Admin, User, Scout
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: datetime
```

#### Session
```python
class Session:
    id: int (PK)
    user_id: int (FK → User)
    token: str (unique, indexed)
    ip_address: str
    expires_at: datetime
```

#### AuditLog
```python
class AuditLog:
    id: int (PK)
    user_id: int (FK → User)
    action: str
    module: str
    entity_type: str
    entity_id: str
    ip_address: str
    success: bool
    created_at: datetime (indexed)
```

---

### 2. NTSP - TALENT SCOUTING

#### Talent
```python
class Talent:
    id: int (PK)
    talent_id: str (unique, indexed)  # NTSP-XXXXX
    
    # Personal
    first_name, last_name: str
    date_of_birth: date
    nationality: str (indexed)
    dual_nationality: str
    
    # Diaspora
    is_diaspora: bool
    diaspora_country: str
    speaks_arabic, speaks_french: bool
    
    # Football
    primary_position: str (indexed)  # GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST
    secondary_position: str
    preferred_foot: str
    height_cm, weight_kg: int
    
    # Club
    current_club: str
    contract_end: date
    
    # Scores
    status: str (indexed)  # Prospect, Monitored, Priority, Signed
    overall_score: float
    potential_score: float
    market_value: float
    
    # Relationships
    evaluations: List[TalentEvaluation]
    medical_records: List[TalentMedical]
    mental_evaluations: List[TalentMentalEval]
    career_history: List[TalentCareer]
```

#### TalentEvaluation
```python
class TalentEvaluation:
    id: int (PK)
    talent_id: int (FK → Talent)
    scout_id: int (FK → Scout)
    
    # Technical scores (1-100)
    score_ball_control, score_passing, score_dribbling: int
    score_shooting, score_heading, score_first_touch: int
    
    # Physical scores (1-100)
    score_speed, score_acceleration, score_stamina: int
    score_strength, score_jumping, score_agility: int
    
    # Mental scores (1-100)
    score_positioning, score_vision, score_composure: int
    score_leadership, score_work_rate, score_decision_making: int
    
    # Totals
    overall_score, potential_score: float
    
    # Recommendation
    recommendation: str  # Sign, Monitor, Pass, Follow-up
```

#### Scout
```python
class Scout:
    id: int (PK)
    scout_id: str (unique)
    user_id: int (FK → User)
    
    first_name, last_name: str
    region: str  # Europe, Africa, Americas, Asia
    countries: str  # Comma-separated
    specialization: str
    
    total_evaluations: int
    total_signings: int
```

---

### 3. TRANSFERS

#### Transfer
```python
class Transfer:
    id: int (PK)
    transfer_id: str (unique)
    talent_id: int (FK → Talent)
    
    from_club, to_club: str
    transfer_type: str  # Permanent, Loan, Free, Youth
    transfer_date: date (indexed)
    
    # Financial
    transfer_fee: float
    add_ons: float
    sell_on_pct: float
    agent_fee: float
    
    # Solidarity
    training_compensation: float
    solidarity_contribution: float
    foundation_contribution: float  # 0.5%
    
    # Blockchain
    smart_contract_hash: str
    blockchain_verified: bool
    
    status: str  # Pending, Completed, Cancelled
```

---

### 4. ACADEMY

#### Academy
```python
class Academy:
    id: int (PK)
    academy_id: str (unique)
    
    name: str
    region, city, country: str
    academy_type: str
    certification_level: str  # Basic, Bronze, Silver, Gold, Elite
    
    total_capacity: int
    current_enrollment: int
    
    # Relationships
    teams: List[AcademyTeam]
    staff: List[AcademyStaff]
    enrollments: List[AcademyEnrollment]
```

---

### 5. TICKETCHAIN

#### Event
```python
class Event:
    id: int (PK)
    event_id: str (unique)
    
    name: str
    event_type: str  # Match, Concert, Festival
    venue, city, country: str
    date: datetime (indexed)
    
    capacity: int
    tickets_sold: int
    
    price_min, price_max: float
    
    mobility_enabled: bool
    diaspora_package: bool
    
    status: str (indexed)  # Upcoming, OnSale, SoldOut, Past
    
    # Relationships
    tickets: List[Ticket]
```

#### Ticket
```python
class Ticket:
    id: int (PK)
    ticket_hash: str (unique, indexed)  # Blockchain hash
    event_id: int (FK → Event)
    owner_id: int (FK → User)
    
    seat_section, seat_row, seat_number: str
    category: str  # VIP, Standard, Economy
    price: float
    
    # Blockchain
    minted_at: datetime
    block_number: int
    transaction_hash: str
    
    status: str (indexed)  # Valid, Used, Expired, Cancelled, Resold
    used_at: datetime
    
    qr_code: text
```

---

### 6. FINANCIAL

#### Wallet
```python
class Wallet:
    id: int (PK)
    wallet_id: str (unique)
    wallet_address: str (unique, indexed)  # Blockchain address
    user_id: int (FK → User)
    
    balance: float
    currency: str
    
    country_of_residence: str
    kyc_level: int  # 0, 1, 2, 3
    kyc_verified: bool
    
    # Relationships
    transactions: List[WalletTransaction]
```

#### FoundationDonation
```python
class FoundationDonation:
    id: int (PK)
    donation_id: str (unique)
    
    donor_id: int (FK → User)
    amount: float
    currency: str
    
    donation_type: str  # OneTime, Monthly, Sadaka
    project: str
    is_anonymous: bool
    is_recurring: bool
```

---

### 7. FANDORPEN (WK 2030)

#### FanDorp
```python
class FanDorp:
    id: int (PK)
    fandorp_id: str (unique)
    
    name: str
    city, country: str
    capacity: int
    
    host_nation: str  # Morocco, Spain, Portugal
    opening_date, closing_date: date
    
    status: str  # Planning, Active, Closed
    
    # Relationships
    volunteers: List[FanDorpVolunteer]
    shifts: List[FanDorpShift]
    incidents: List[FanDorpIncident]
```

#### FanDorpVolunteer
```python
class FanDorpVolunteer:
    id: int (PK)
    volunteer_id: str (unique)
    fandorp_id: int (FK → FanDorp)
    user_id: int (FK → User)
    
    first_name, last_name: str
    nationality: str
    languages: str  # Comma-separated
    
    role: str  # Guide, Security, Medical, Transport
    is_trained: bool
    
    status: str  # Pending, Approved, Active
```

---

### 8. PROTECTION

#### NILSignal
```python
class NILSignal:
    id: int (PK)
    signal_id: str (unique)
    
    title: str
    content: text
    content_hash: str  # For verification
    
    source_url: str
    source_platform: str
    
    signal_type: str  # Misinformation, Disinformation, Rumor
    
    risk_score: int  # 0-100
    verification_status: str
    fact_check_result: str
    
    status: str (indexed)
    
    # Relationships
    evidence: List[NILEvidence]
```

#### AntiHateIncident
```python
class AntiHateIncident:
    id: int (PK)
    incident_id: str (unique)
    
    target_type: str  # Player, Coach, Fan
    target_name: str
    
    incident_type: str  # Racist, Sexist, Homophobic
    platform: str
    
    content: text
    evidence_url: str
    
    severity: str
    verified: bool
    
    status: str (indexed)
    action_taken: text
```

#### HayatSession
```python
class HayatSession:
    id: int (PK)
    session_id: str (unique)
    
    talent_id: int (FK → Talent)
    anonymous_code: str  # Privacy protection
    
    session_type: str  # Individual, Group, Crisis
    provider_name: str
    
    scheduled_at: datetime
    duration_minutes: int
    
    mood_before, mood_after: int  # 1-10
    
    status: str
    follow_up_needed: bool
```

---

## RELATIES OVERZICHT

| Parent | Child | Type | FK |
|--------|-------|------|-----|
| User | Session | 1:N | user_id |
| User | AuditLog | 1:N | user_id |
| User | Wallet | 1:N | user_id |
| User | Subscription | 1:N | user_id |
| Talent | TalentEvaluation | 1:N | talent_id |
| Talent | TalentMedical | 1:N | talent_id |
| Talent | TalentMentalEval | 1:N | talent_id |
| Talent | TalentCareer | 1:N | talent_id |
| Talent | Transfer | 1:N | talent_id |
| Scout | TalentEvaluation | 1:N | scout_id |
| Academy | AcademyTeam | 1:N | academy_id |
| Academy | AcademyStaff | 1:N | academy_id |
| Academy | AcademyEnrollment | 1:N | academy_id |
| Event | Ticket | 1:N | event_id |
| Wallet | WalletTransaction | 1:N | wallet_id |
| FanDorp | FanDorpVolunteer | 1:N | fandorp_id |
| FanDorp | FanDorpShift | 1:N | fandorp_id |
| FanDorp | FanDorpIncident | 1:N | fandorp_id |
| NILSignal | NILEvidence | 1:N | signal_id |
| Subscription | SubscriptionPayment | 1:N | subscription_id |
| Identity | FraudAlert | 1:N | identity_id |

---

## INDEXES

| Table | Column(s) | Reason |
|-------|-----------|--------|
| users | username | Login lookup |
| users | email | Login lookup |
| sessions | token | Auth verification |
| talents | nationality | Filter by country |
| talents | status | Filter by status |
| talents | primary_position | Filter by position |
| transfers | transfer_date | Date range queries |
| events | date | Event listing |
| tickets | ticket_hash | Verification |
| tickets | status | Status filtering |
| nil_signals | status | Active signals |
| antihate_incidents | status | Open cases |
| audit_logs | created_at | Log queries |

---

## MIGRATIE STRATEGIE

### Van SQLite naar PostgreSQL

1. **Export bestaande data**
   ```bash
   sqlite3 proinvestix.db .dump > backup.sql
   ```

2. **Schema conversie**
   - TEXT → VARCHAR / TEXT
   - INTEGER → INTEGER / BIGINT
   - REAL → DECIMAL / FLOAT

3. **Alembic migrations**
   ```bash
   alembic init migrations
   alembic revision --autogenerate -m "Initial"
   alembic upgrade head
   ```

4. **Data import**
   ```python
   # Python script to migrate data
   ```

---

## VOLGENDE STAP

**Fase 0.3:** Project structuur bepalen
- Backend folder structuur (FastAPI)
- Frontend folder structuur (Next.js)
- Shared types/interfaces

---

*Document gegenereerd: Fase 0.2 Complete*
