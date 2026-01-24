# ProInvestiX Enterprise - Module Inventarisatie
## Fase 0.1 - Complete Analyse

---

## OVERZICHT

| Metric | Waarde |
|--------|--------|
| Totaal modules | 24 |
| Totaal code regels | ~18,000+ |
| Database tabellen | 100 |
| Bestaande API endpoints | 20 |
| Talen ondersteund | 4 (NL/FR/EN/AR) |

---

## MODULES GERANGSCHIKT OP GROOTTE

| # | Module | Regels | Complexiteit |
|---|--------|--------|--------------|
| 1 | frmf | 2,926 | ⭐⭐⭐⭐⭐ |
| 2 | fandorpen | 1,513 | ⭐⭐⭐⭐⭐ |
| 3 | maroc_id_shield | 1,423 | ⭐⭐⭐⭐⭐ |
| 4 | ntsp | 1,343 | ⭐⭐⭐⭐⭐ |
| 5 | hayat | 986 | ⭐⭐⭐⭐ |
| 6 | antihate | 926 | ⭐⭐⭐⭐ |
| 7 | inclusion | 887 | ⭐⭐⭐⭐ |
| 8 | subscriptions | 864 | ⭐⭐⭐⭐ |
| 9 | transfer_market | 770 | ⭐⭐⭐⭐ |
| 10 | dashboard | 735 | ⭐⭐⭐ |
| 11 | pma_logistics | 707 | ⭐⭐⭐ |
| 12 | nil | 658 | ⭐⭐⭐ |
| 13 | ticketchain | 599 | ⭐⭐⭐ |
| 14 | foundation_bank | 547 | ⭐⭐⭐ |
| 15 | antilobby | 527 | ⭐⭐⭐ |
| 16 | diaspora_wallet | 495 | ⭐⭐⭐ |
| 17 | analytics | 478 | ⭐⭐⭐ |
| 18 | transfers | 374 | ⭐⭐ |
| 19 | consulate_hub | 360 | ⭐⭐ |
| 20 | security_admin | 355 | ⭐⭐ |
| 21 | identity_shield | 329 | ⭐⭐ |
| 22 | adapters | 293 | ⭐⭐ |
| 23 | academy | 200 | ⭐ |
| 24 | mobility | 61 | ⭐ |

---

## MODULE DETAILS

---

### 1. DASHBOARD (735 regels)
**Beschrijving:** Executive Dashboard met KPIs en overzichten

**Functies:**
- render() - Main render
- render_wk_countdown_mini() - WK 2030 countdown
- render_top_kpis() - Top KPI cards
- render_transfer_volume_chart() - Transfer grafiek
- render_revenue_distribution() - Revenue pie chart
- render_talent_by_position() - Talent per positie
- render_ticket_sales_chart() - Ticket verkoop
- render_diaspora_distribution() - Diaspora kaart
- render_foundation_growth() - Foundation groei
- render_recent_activity() - Recente activiteit
- render_quick_stats() - Snelle statistieken

**Database tabellen:** Leest van alle modules

**API endpoints nodig:**
- GET /api/v1/dashboard/stats
- GET /api/v1/dashboard/kpis
- GET /api/v1/dashboard/charts/{type}

---

### 2. NTSP - National Talent Scouting Platform (1,343 regels)
**Beschrijving:** Talent database en scouting systeem

**Functies:**
- render_talent_database() - Talent overzicht
- render_talent_detail() - Talent profiel
- render_new_talent() - Nieuw talent registreren
- render_evaluations() - Evaluaties
- render_new_evaluation() - Nieuwe evaluatie
- render_medical() - Medische records
- render_mental() - Mental health
- render_watchlist() - Watchlist
- render_scouts() - Scout management
- render_analytics() - Analytics

**Database tabellen:**
- ntsp_talent_profiles
- ntsp_evaluations
- ntsp_medical_records
- ntsp_mental_evaluations
- ntsp_career_history
- ntsp_watchlist
- ntsp_scouts

**API endpoints nodig:**
- GET /api/v1/talents
- GET /api/v1/talents/{id}
- POST /api/v1/talents
- PUT /api/v1/talents/{id}
- GET /api/v1/talents/{id}/evaluations
- POST /api/v1/talents/{id}/evaluations
- GET /api/v1/scouts
- POST /api/v1/scouts

---

### 3. TRANSFERS (374 regels)
**Beschrijving:** Transfer management en compensatie berekening

**Functies:**
- render_transfer_overview() - Transfer overzicht
- render_new_transfer() - Nieuwe transfer
- render_compensation_calculator() - Compensatie calculator
- render_contract_templates() - Contract templates
- render_transfer_analytics() - Analytics

**Database tabellen:**
- transfers
- transfer_compensations
- contract_templates

**API endpoints nodig:**
- GET /api/v1/transfers
- GET /api/v1/transfers/{id}
- POST /api/v1/transfers
- GET /api/v1/transfers/compensation/calculate
- GET /api/v1/contracts/templates

---

### 4. ACADEMY (200 regels)
**Beschrijving:** Academy management systeem

**Functies:**
- render_overview() - Academy overzicht
- render_new_academy() - Nieuwe academy
- render_teams() - Teams beheer
- render_enrollments() - Inschrijvingen
- render_staff() - Staff beheer

**Database tabellen:**
- academies
- academy_teams
- academy_enrollments
- academy_staff

**API endpoints nodig:**
- GET /api/v1/academies
- POST /api/v1/academies
- GET /api/v1/academies/{id}/teams
- POST /api/v1/academies/{id}/enrollments
- GET /api/v1/academies/{id}/staff

---

### 5. TRANSFER MARKET (770 regels)
**Beschrijving:** Transfermarkt-style speler database

**Functies:**
- render_overview() - Markt overzicht
- render_search() - Speler zoeken
- render_player_profile() - Speler profiel
- render_clubs() - Club profielen
- render_transfers() - Transfer historie
- render_top_lists() - Top lijsten
- render_stats() - Statistieken
- render_watchlist() - Watchlist
- render_compare() - Speler vergelijken

**Database tabellen:**
- tm_players
- tm_statistics
- tm_transfers
- tm_value_history
- tm_rumours
- tm_watchlist

**API endpoints nodig:**
- GET /api/v1/market/players
- GET /api/v1/market/players/{id}
- GET /api/v1/market/clubs
- GET /api/v1/market/transfers
- GET /api/v1/market/top/{category}
- POST /api/v1/market/watchlist

---

### 6. TICKETCHAIN (599 regels)
**Beschrijving:** Blockchain ticket systeem

**Functies:**
- render_events() - Evenementen
- render_minting() - Ticket minting
- render_validator() - Ticket validatie
- render_loyalty() - Loyalty programma

**Database tabellen:**
- ticketchain_events
- ticketchain_tickets
- loyalty_points
- fiscal_ledger

**API endpoints nodig:**
- GET /api/v1/events
- POST /api/v1/events
- POST /api/v1/tickets/mint
- GET /api/v1/tickets/verify/{hash}
- GET /api/v1/loyalty/{user_id}

---

### 7. FOUNDATION BANK (547 regels)
**Beschrijving:** Sadaka Jaaria foundation management

**Functies:**
- render_foundation_summary() - Samenvatting
- render_overview() - Overzicht
- render_transactions() - Transacties
- render_donations() - Donaties
- render_analytics() - Analytics

**Database tabellen:**
- foundation_donations
- foundation_contributions
- financial_records

**API endpoints nodig:**
- GET /api/v1/foundation/stats
- GET /api/v1/foundation/donations
- POST /api/v1/foundation/donate
- GET /api/v1/foundation/transactions

---

### 8. DIASPORA WALLET (495 regels)
**Beschrijving:** Digitale wallet voor diaspora

**Functies:**
- render_wallet_overview() - Wallet overzicht
- render_new_wallet() - Nieuwe wallet
- render_transactions() - Transacties
- render_investments() - Investeringen
- render_diaspora_card() - Diaspora kaart
- render_wallet_analytics() - Analytics

**Database tabellen:**
- diaspora_wallets
- wallet_transactions
- diaspora_investments
- diaspora_cards
- diaspora_travel_packages

**API endpoints nodig:**
- GET /api/v1/wallets
- POST /api/v1/wallets
- GET /api/v1/wallets/{id}/balance
- POST /api/v1/wallets/{id}/transfer
- GET /api/v1/wallets/{id}/transactions

---

### 9. SUBSCRIPTIONS (864 regels)
**Beschrijving:** Abonnement en membership systeem

**Functies:**
- render_plans() - Abonnement plannen
- render_my_subscriptions() - Mijn abonnementen
- render_new_subscription() - Nieuw abonnement
- render_gift_cards() - Gift cards
- render_subscription_analytics() - Analytics

**Database tabellen:**
- subscription_plans
- subscriptions
- user_subscriptions
- subscription_payments
- gift_subscriptions

**API endpoints nodig:**
- GET /api/v1/subscriptions/plans
- GET /api/v1/subscriptions/user/{id}
- POST /api/v1/subscriptions
- POST /api/v1/subscriptions/gift

---

### 10. FANDORPEN (1,513 regels)
**Beschrijving:** Fan village management voor WK 2030

**Functies:**
- render_fandorpen_management() - FanDorp beheer
- render_volunteers() - Vrijwilligers
- render_volunteer_registration() - Registratie
- render_shifts() - Diensten
- render_incidents() - Incidenten
- render_training_badges() - Training badges
- render_qr_checkin() - QR check-in
- render_chat() - Chat systeem
- render_dashboard() - Dashboard

**Database tabellen:**
- fandorpen
- fandorp_volunteers
- fandorp_shifts
- fandorp_incidents
- fandorp_training
- fandorp_messages
- fandorp_services

**API endpoints nodig:**
- GET /api/v1/fandorpen
- POST /api/v1/fandorpen
- GET /api/v1/fandorpen/{id}/volunteers
- POST /api/v1/fandorpen/{id}/shifts
- POST /api/v1/fandorpen/{id}/incidents
- GET /api/v1/fandorpen/{id}/chat

---

### 11. CONSULATE HUB (360 regels)
**Beschrijving:** Consulaire diensten portaal

**Functies:**
- render_document_vault() - Document kluis
- render_scholarships() - Beurzen
- render_investments() - Investeringen
- render_assistance() - Hulp aanvragen

**Database tabellen:**
- consular_documents
- consular_services
- consular_appointments
- consular_registry
- consular_assistance
- scholarship_applications

**API endpoints nodig:**
- GET /api/v1/consulate/documents
- POST /api/v1/consulate/documents
- GET /api/v1/consulate/scholarships
- POST /api/v1/consulate/appointments

---

### 12. IDENTITY SHIELD (329 regels)
**Beschrijving:** Identiteit verificatie en fraude detectie

**Functies:**
- render_identity_registry() - Identiteit register
- render_fraud_monitoring() - Fraude monitoring
- render_manual_alert_form() - Alert formulier
- render_analytics() - Analytics

**Database tabellen:**
- identity_shield
- fraud_alerts
- verification_requests

**API endpoints nodig:**
- GET /api/v1/identities
- POST /api/v1/identities/verify
- GET /api/v1/identities/{id}/verify
- POST /api/v1/fraud/alert

---

### 13. MAROC ID SHIELD (1,423 regels)
**Beschrijving:** Marokkaanse digitale identiteit systeem

**Functies:**
- render_verification() - Verificatie
- render_levels_overview() - Verificatie levels
- render_organizations() - Organisaties
- render_role_certificates() - Rol certificaten
- render_transaction_signing() - Transactie signing
- render_pma_dashboard() - PMA dashboard
- render_admin() - Admin panel

**Database tabellen:**
- maroc_identities
- maroc_organizations
- maroc_role_certificates
- maroc_transaction_signatures
- maroc_verification_requests
- maroc_consents
- maroc_pma_queue

**API endpoints nodig:**
- GET /api/v1/maroc/identities
- POST /api/v1/maroc/verify
- GET /api/v1/maroc/organizations
- POST /api/v1/maroc/certificates
- POST /api/v1/maroc/sign

---

### 14. FRMF (2,926 regels) ⭐ GROOTSTE MODULE
**Beschrijving:** Koninklijke Marokkaanse Voetbalbond systeem

**Functies:**
- render_referee_registry() - Scheidsrechter register
- render_refereechain() - Blockchain audit trail
- render_match_assignments() - Wedstrijd toewijzingen
- render_var_vault() - VAR beslissingen
- render_referee_performance() - Prestaties
- render_player_profiles() - Speler profielen
- render_contract_management() - Contract beheer
- render_medical_records() - Medische records
- render_performance_analytics() - Performance analytics
- render_match_incidents() - Wedstrijd incidenten

**Database tabellen:**
- frmf_players (nog niet in setup)
- frmf_refereechain (nog niet in setup)
- frmf_contracts (nog niet in setup)
- frmf_contract_clauses (nog niet in setup)
- frmf_player_medical (nog niet in setup)
- frmf_player_fitness (nog niet in setup)
- frmf_return_to_play (nog niet in setup)
- frmf_match_performance (nog niet in setup)
- frmf_season_stats (nog niet in setup)
- frmf_team_performance (nog niet in setup)

**API endpoints nodig:**
- GET /api/v1/frmf/referees
- POST /api/v1/frmf/referees
- GET /api/v1/frmf/refereechain
- GET /api/v1/frmf/var-decisions
- GET /api/v1/frmf/players
- POST /api/v1/frmf/contracts
- GET /api/v1/frmf/medical/{player_id}

---

### 15. HAYAT HEALTH (986 regels)
**Beschrijving:** Mental health en wellbeing platform

**Functies:**
- render_crisis_center() - Crisis centrum
- render_wellbeing_dashboard() - Wellbeing dashboard
- render_sessions() - Sessies
- render_rehabilitation() - Rehabilitatie
- render_hayat_analytics() - Analytics
- render_hayat_admin() - Admin panel

**Database tabellen:**
- hayat_sessions
- hayat_wellbeing_logs
- hayat_rehabilitation
- hayat_alerts
- hayat_crisis_alerts
- health_records

**API endpoints nodig:**
- GET /api/v1/hayat/sessions
- POST /api/v1/hayat/sessions
- GET /api/v1/hayat/wellbeing/{user_id}
- POST /api/v1/hayat/crisis/alert

---

### 16. INCLUSION (887 regels)
**Beschrijving:** Women & Paralympic sports platform

**Functies:**
- render_women_hubs() - Women hubs
- render_women_players() - Women spelers
- render_paralympics() - Paralympics
- render_programs() - Programma's
- render_events() - Evenementen
- render_inclusion_analytics() - Analytics

**Database tabellen:**
- women_hubs
- women_players
- inclusion_athletes
- inclusion_programs
- inclusion_events
- paralympic_athletes

**API endpoints nodig:**
- GET /api/v1/inclusion/women/hubs
- GET /api/v1/inclusion/women/players
- GET /api/v1/inclusion/paralympics
- GET /api/v1/inclusion/programs
- GET /api/v1/inclusion/events

---

### 17. ANTI-HATE SHIELD (926 regels)
**Beschrijving:** Anti-discriminatie en bescherming platform

**Functies:**
- render_dashboard() - Dashboard
- render_monitoring() - Monitoring
- render_incidents() - Incidenten
- render_legal() - Juridische zaken
- render_wellness() - Wellness checks
- render_antihate_analytics() - Analytics

**Database tabellen:**
- antihate_incidents
- antihate_cases
- antihate_monitored
- antihate_legal_cases
- antihate_wellness_checks

**API endpoints nodig:**
- GET /api/v1/antihate/incidents
- POST /api/v1/antihate/incidents
- GET /api/v1/antihate/cases
- POST /api/v1/antihate/monitor

---

### 18. ANTI-LOBBY (527 regels)
**Beschrijving:** Transparantie en anti-corruptie systeem

**Functies:**
- render_contract_registry() - Contract register
- render_ownership_control() - Eigendom controle
- render_payment_tracking() - Betaling tracking
- render_audit_dashboard() - Audit dashboard
- render_reports() - Rapporten

**Database tabellen:** (gebruikt demo data)

**API endpoints nodig:**
- GET /api/v1/antilobby/contracts
- GET /api/v1/antilobby/ownership
- GET /api/v1/antilobby/payments
- GET /api/v1/antilobby/audit

---

### 19. ANALYTICS (478 regels)
**Beschrijving:** Platform-brede analytics

**Functies:**
- render_ticketchain_analytics() - Ticket analytics
- render_financial_analytics() - Financial analytics
- render_talent_analytics() - Talent analytics
- render_security_analytics() - Security analytics

**Database tabellen:** Leest van alle modules

**API endpoints nodig:**
- GET /api/v1/analytics/tickets
- GET /api/v1/analytics/financial
- GET /api/v1/analytics/talents
- GET /api/v1/analytics/security

---

### 20. SECURITY ADMIN (355 regels)
**Beschrijving:** Beveiligings administratie

**Functies:**
- render_security_center() - Security center
- render_audit_logs() - Audit logs
- render_security_alerts() - Alerts
- render_compliance_reports() - Compliance
- render_admin_panel() - Admin panel
- render_user_management() - User management
- render_system_settings() - Systeem settings

**Database tabellen:**
- audit_logs
- users
- sessions

**API endpoints nodig:**
- GET /api/v1/admin/audit-logs
- GET /api/v1/admin/users
- PUT /api/v1/admin/users/{id}
- GET /api/v1/admin/settings

---

### 21. PMA LOGISTICS (707 regels)
**Beschrijving:** Logistics en supply chain

**Functies:**
- render_shipment_tracking() - Zending tracking
- render_warehouse_management() - Warehouse
- render_inventory() - Inventaris
- render_fleet() - Vloot beheer
- render_customs() - Douane

**Database tabellen:** (gebruikt demo data)

**API endpoints nodig:**
- GET /api/v1/logistics/shipments
- POST /api/v1/logistics/shipments
- GET /api/v1/logistics/inventory
- GET /api/v1/logistics/fleet

---

### 22. MOBILITY (61 regels)
**Beschrijving:** Mobiliteit placeholder

**Functies:**
- render() - Basic render

**Database tabellen:**
- mobility_records
- mobility_packages
- mobility_bookings

**API endpoints nodig:**
- GET /api/v1/mobility/packages
- POST /api/v1/mobility/bookings

---

### 23. NIL (658 regels)
**Beschrijving:** News Intelligence Lab - Fake news detectie

**Functies:**
- render_signal_monitor() - Signal monitoring
- render_content_forensics() - Content forensics
- render_source_registry() - Bron register
- render_evidence_vault() - Bewijs kluis
- render_fact_cards() - Fact cards
- render_crisis_playbook() - Crisis playbook
- render_kpi_dashboard() - KPI dashboard

**Database tabellen:**
- nil_signals
- nil_sources
- nil_evidence
- nil_fact_cards
- nil_forensics
- nil_crisis_incidents
- nil_playbook_templates
- nil_kpi_metrics

**API endpoints nodig:**
- GET /api/v1/nil/signals
- POST /api/v1/nil/signals
- GET /api/v1/nil/sources
- GET /api/v1/nil/evidence
- GET /api/v1/nil/fact-cards

---

### 24. ADAPTERS (293 regels)
**Beschrijving:** Adapter modules voor sport, mobility, health

**Functies:**
- render_sport() - Sport adapter
- render_mobility() - Mobility adapter
- render_fleet_management() - Fleet
- render_mobility_bookings() - Bookings
- render_health() - Health adapter

**Database tabellen:** Gebruikt bestaande tabellen

**API endpoints nodig:**
- Deelt endpoints met andere modules

---

## DATABASE TABELLEN (100 totaal)

### Gegroepeerd per domein:

**Auth & Users (4)**
- users
- sessions
- user_registry
- audit_logs

**NTSP & Talent (7)**
- ntsp_talent_profiles
- ntsp_evaluations
- ntsp_medical_records
- ntsp_mental_evaluations
- ntsp_career_history
- ntsp_watchlist
- ntsp_scouts

**Transfers (3)**
- transfers
- transfer_compensations
- contract_templates

**Academy (4)**
- academies
- academy_teams
- academy_enrollments
- academy_staff

**Transfer Market (6)**
- tm_players
- tm_statistics
- tm_transfers
- tm_value_history
- tm_rumours
- tm_watchlist

**TicketChain (4)**
- ticketchain_events
- ticketchain_tickets
- loyalty_points
- fiscal_ledger

**Foundation (3)**
- foundation_donations
- foundation_contributions
- financial_records

**Diaspora (5)**
- diaspora_wallets
- wallet_transactions
- diaspora_investments
- diaspora_cards
- diaspora_travel_packages

**Subscriptions (5)**
- subscription_plans
- subscriptions
- user_subscriptions
- subscription_payments
- gift_subscriptions

**FanDorpen (7)**
- fandorpen
- fandorp_volunteers
- fandorp_shifts
- fandorp_incidents
- fandorp_training
- fandorp_messages
- fandorp_services

**Consulate (6)**
- consular_documents
- consular_services
- consular_appointments
- consular_registry
- consular_assistance
- scholarship_applications

**Identity (3)**
- identity_shield
- fraud_alerts
- verification_requests

**Maroc ID (7)**
- maroc_identities
- maroc_organizations
- maroc_role_certificates
- maroc_transaction_signatures
- maroc_verification_requests
- maroc_consents
- maroc_pma_queue

**Hayat Health (6)**
- hayat_sessions
- hayat_wellbeing_logs
- hayat_rehabilitation
- hayat_alerts
- hayat_crisis_alerts
- health_records

**Inclusion (6)**
- women_hubs
- women_players
- inclusion_athletes
- inclusion_programs
- inclusion_events
- paralympic_athletes

**Anti-Hate (5)**
- antihate_incidents
- antihate_cases
- antihate_monitored
- antihate_legal_cases
- antihate_wellness_checks

**NIL (8)**
- nil_signals
- nil_sources
- nil_evidence
- nil_fact_cards
- nil_forensics
- nil_crisis_incidents
- nil_playbook_templates
- nil_kpi_metrics

**E-Sports (3)**
- esports_players
- esports_teams
- esports_tournaments

**Mobility (3)**
- mobility_records
- mobility_packages
- mobility_bookings

**API (1)**
- api_access_log

---

## BESTAANDE API ENDPOINTS (20)

```
GET  /                              - Health check
GET  /health                        - Health status
GET  /api/v1/stats                  - Platform stats

GET  /api/v1/talents                - Alle talents
GET  /api/v1/talents/{id}           - Talent by ID

GET  /api/v1/transfers              - Alle transfers
GET  /api/v1/transfers/{id}         - Transfer by ID

GET  /api/v1/events                 - Alle events
GET  /api/v1/events/{id}            - Event by ID
GET  /api/v1/tickets/verify/{hash}  - Verify ticket

GET  /api/v1/wallets                - Alle wallets
GET  /api/v1/wallets/{id}/balance   - Wallet balance

GET  /api/v1/foundation/stats       - Foundation stats

GET  /api/v1/referees               - Alle referees
GET  /api/v1/var-decisions          - VAR decisions
GET  /api/v1/var-decisions/{id}/verify - Verify VAR

GET  /api/v1/signals                - NIL signals
GET  /api/v1/signals/{id}           - Signal by ID

GET  /api/v1/identities             - Alle identities
GET  /api/v1/identities/{id}/verify - Verify identity
```

---

## API ENDPOINTS NODIG (Geschat: 150+)

Per module gemiddeld 6-8 endpoints nodig voor CRUD + specifieke functies.

---

## VOLGENDE STAP

**Fase 0.2:** Database schema documenteren
- SQLAlchemy models ontwerpen
- Relaties tussen tabellen
- Migratie strategie

---

*Document gegenereerd: Fase 0.1 Complete*
