# ProInvestiX Enterprise - API Routes Planning
## Fase 0.3 - Complete API Specificatie

---

## BASE URL

```
Production:  https://api.proinvestix.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## AUTHENTICATION

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login, returns JWT |
| POST | `/auth/register` | Register new user |
| POST | `/auth/refresh` | Refresh token |
| POST | `/auth/logout` | Logout (invalidate token) |
| POST | `/auth/forgot-password` | Request password reset |
| POST | `/auth/reset-password` | Reset password |
| GET | `/auth/me` | Get current user |

### Request/Response Examples

```json
// POST /auth/login
Request:
{
  "email": "admin@proinvestix.ma",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@proinvestix.ma",
    "role": "SuperAdmin"
  }
}
```

---

## DASHBOARD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/stats` | Platform statistics |
| GET | `/dashboard/kpis` | Key performance indicators |
| GET | `/dashboard/charts/{type}` | Chart data |
| GET | `/dashboard/activity` | Recent activity |
| GET | `/dashboard/wk-countdown` | WK 2030 countdown |

---

## NTSP - TALENTS (26 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/talents` | List all talents |
| GET | `/talents/{id}` | Get talent by ID |
| POST | `/talents` | Create new talent |
| PUT | `/talents/{id}` | Update talent |
| DELETE | `/talents/{id}` | Delete talent |
| GET | `/talents/{id}/evaluations` | Get talent evaluations |
| POST | `/talents/{id}/evaluations` | Add evaluation |
| GET | `/talents/{id}/medical` | Get medical records |
| POST | `/talents/{id}/medical` | Add medical record |
| GET | `/talents/{id}/mental` | Get mental evaluations |
| POST | `/talents/{id}/mental` | Add mental evaluation |
| GET | `/talents/{id}/career` | Get career history |
| POST | `/talents/{id}/career` | Add career entry |
| GET | `/talents/search` | Search talents |
| GET | `/talents/filters` | Get filter options |
| GET | `/talents/stats` | Talent statistics |
| GET | `/talents/export` | Export to CSV/Excel |

### Scouts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/scouts` | List all scouts |
| GET | `/scouts/{id}` | Get scout by ID |
| POST | `/scouts` | Create scout |
| PUT | `/scouts/{id}` | Update scout |
| DELETE | `/scouts/{id}` | Delete scout |
| GET | `/scouts/{id}/evaluations` | Scout's evaluations |

### Watchlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/watchlist` | Get user's watchlist |
| POST | `/watchlist` | Add to watchlist |
| DELETE | `/watchlist/{talent_id}` | Remove from watchlist |

---

## TRANSFERS (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transfers` | List all transfers |
| GET | `/transfers/{id}` | Get transfer by ID |
| POST | `/transfers` | Create transfer |
| PUT | `/transfers/{id}` | Update transfer |
| DELETE | `/transfers/{id}` | Cancel transfer |
| GET | `/transfers/{id}/compensations` | Get compensations |
| POST | `/transfers/calculate` | Calculate fees |
| GET | `/transfers/templates` | Contract templates |
| POST | `/transfers/templates` | Create template |
| GET | `/transfers/stats` | Transfer statistics |
| GET | `/transfers/export` | Export data |

---

## ACADEMY (15 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/academies` | List academies |
| GET | `/academies/{id}` | Get academy |
| POST | `/academies` | Create academy |
| PUT | `/academies/{id}` | Update academy |
| DELETE | `/academies/{id}` | Delete academy |
| GET | `/academies/{id}/teams` | Get teams |
| POST | `/academies/{id}/teams` | Create team |
| GET | `/academies/{id}/staff` | Get staff |
| POST | `/academies/{id}/staff` | Add staff |
| GET | `/academies/{id}/enrollments` | Get enrollments |
| POST | `/academies/{id}/enrollments` | Enroll talent |
| DELETE | `/academies/{id}/enrollments/{eid}` | Remove enrollment |
| GET | `/academies/stats` | Academy statistics |

---

## TRANSFER MARKET (18 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/market/players` | List players |
| GET | `/market/players/{id}` | Get player |
| GET | `/market/players/{id}/history` | Value history |
| GET | `/market/players/{id}/stats` | Player stats |
| GET | `/market/players/{id}/transfers` | Transfer history |
| GET | `/market/players/search` | Search players |
| GET | `/market/players/top/{category}` | Top lists |
| GET | `/market/clubs` | List clubs |
| GET | `/market/clubs/{id}` | Get club |
| GET | `/market/clubs/{id}/squad` | Club squad |
| GET | `/market/transfers` | Recent transfers |
| GET | `/market/rumours` | Transfer rumours |
| GET | `/market/watchlist` | User's watchlist |
| POST | `/market/watchlist` | Add to watchlist |
| DELETE | `/market/watchlist/{id}` | Remove from watchlist |
| GET | `/market/compare` | Compare players |

---

## TICKETCHAIN (16 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/events` | List events |
| GET | `/events/{id}` | Get event |
| POST | `/events` | Create event |
| PUT | `/events/{id}` | Update event |
| DELETE | `/events/{id}` | Cancel event |
| GET | `/events/{id}/tickets` | Get tickets |
| POST | `/events/{id}/tickets/mint` | Mint ticket |
| GET | `/tickets/{hash}` | Get ticket by hash |
| GET | `/tickets/{hash}/verify` | Verify ticket |
| POST | `/tickets/{hash}/use` | Mark as used |
| POST | `/tickets/{hash}/transfer` | Transfer ticket |
| GET | `/loyalty` | Get loyalty points |
| GET | `/loyalty/history` | Points history |
| POST | `/loyalty/redeem` | Redeem points |

---

## FOUNDATION BANK (10 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/foundation/stats` | Foundation statistics |
| GET | `/foundation/donations` | List donations |
| POST | `/foundation/donations` | Make donation |
| GET | `/foundation/donations/{id}` | Get donation |
| GET | `/foundation/contributions` | Auto contributions |
| GET | `/foundation/projects` | Foundation projects |
| GET | `/foundation/reports` | Financial reports |
| GET | `/foundation/export` | Export data |

---

## DIASPORA WALLET (14 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wallets` | List wallets |
| GET | `/wallets/{id}` | Get wallet |
| POST | `/wallets` | Create wallet |
| GET | `/wallets/{id}/balance` | Get balance |
| GET | `/wallets/{id}/transactions` | Get transactions |
| POST | `/wallets/{id}/deposit` | Deposit |
| POST | `/wallets/{id}/withdraw` | Withdraw |
| POST | `/wallets/{id}/transfer` | Transfer |
| GET | `/wallets/{id}/cards` | Get cards |
| POST | `/wallets/{id}/cards` | Request card |
| PUT | `/wallets/{id}/cards/{cid}` | Update card |
| GET | `/wallets/investments` | Get investments |
| POST | `/wallets/investments` | Make investment |

---

## SUBSCRIPTIONS (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/subscriptions/plans` | List plans |
| GET | `/subscriptions/plans/{id}` | Get plan |
| GET | `/subscriptions` | User subscriptions |
| GET | `/subscriptions/{id}` | Get subscription |
| POST | `/subscriptions` | Subscribe |
| PUT | `/subscriptions/{id}` | Update subscription |
| DELETE | `/subscriptions/{id}` | Cancel subscription |
| GET | `/subscriptions/{id}/payments` | Payment history |
| POST | `/subscriptions/gift` | Gift subscription |
| GET | `/subscriptions/gift/{code}` | Redeem gift |

---

## FANDORPEN - WK 2030 (20 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/fandorpen` | List FanDorpen |
| GET | `/fandorpen/{id}` | Get FanDorp |
| POST | `/fandorpen` | Create FanDorp |
| PUT | `/fandorpen/{id}` | Update FanDorp |
| GET | `/fandorpen/{id}/volunteers` | Get volunteers |
| POST | `/fandorpen/{id}/volunteers` | Register volunteer |
| GET | `/fandorpen/{id}/shifts` | Get shifts |
| POST | `/fandorpen/{id}/shifts` | Create shift |
| PUT | `/fandorpen/{id}/shifts/{sid}` | Update shift |
| POST | `/fandorpen/{id}/shifts/{sid}/checkin` | Check in |
| POST | `/fandorpen/{id}/shifts/{sid}/checkout` | Check out |
| GET | `/fandorpen/{id}/incidents` | Get incidents |
| POST | `/fandorpen/{id}/incidents` | Report incident |
| PUT | `/fandorpen/{id}/incidents/{iid}` | Update incident |
| GET | `/fandorpen/{id}/training` | Training modules |
| POST | `/fandorpen/{id}/training/{tid}/complete` | Complete training |
| GET | `/fandorpen/{id}/chat` | Get chat messages |
| POST | `/fandorpen/{id}/chat` | Send message |
| GET | `/fandorpen/stats` | Statistics |

---

## CONSULATE HUB (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/consulate/documents` | Get documents |
| POST | `/consulate/documents` | Upload document |
| GET | `/consulate/documents/{id}` | Get document |
| DELETE | `/consulate/documents/{id}` | Delete document |
| GET | `/consulate/appointments` | Get appointments |
| POST | `/consulate/appointments` | Create appointment |
| PUT | `/consulate/appointments/{id}` | Update appointment |
| DELETE | `/consulate/appointments/{id}` | Cancel appointment |
| GET | `/consulate/services` | Available services |
| GET | `/consulate/scholarships` | Scholarships |
| POST | `/consulate/scholarships` | Apply for scholarship |
| GET | `/consulate/assistance` | Assistance requests |

---

## IDENTITY SHIELD (10 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/identities` | List identities |
| GET | `/identities/{id}` | Get identity |
| POST | `/identities` | Create identity |
| PUT | `/identities/{id}` | Update identity |
| GET | `/identities/{id}/verify` | Verify identity |
| POST | `/identities/{id}/verify` | Submit verification |
| GET | `/fraud/alerts` | Get fraud alerts |
| POST | `/fraud/alerts` | Create alert |
| PUT | `/fraud/alerts/{id}` | Update alert |
| GET | `/fraud/stats` | Fraud statistics |

---

## MAROC ID SHIELD (14 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/maroc-id` | List Maroc IDs |
| GET | `/maroc-id/{id}` | Get Maroc ID |
| POST | `/maroc-id` | Create Maroc ID |
| PUT | `/maroc-id/{id}` | Update Maroc ID |
| POST | `/maroc-id/{id}/verify` | Request verification |
| GET | `/maroc-id/{id}/level` | Get verification level |
| POST | `/maroc-id/{id}/upgrade` | Upgrade level |
| GET | `/maroc-id/organizations` | List organizations |
| POST | `/maroc-id/organizations` | Create organization |
| GET | `/maroc-id/certificates` | List certificates |
| POST | `/maroc-id/certificates` | Issue certificate |
| PUT | `/maroc-id/certificates/{id}` | Update certificate |
| POST | `/maroc-id/sign` | Sign transaction |
| GET | `/maroc-id/pma` | PMA queue |

---

## FRMF (22 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/frmf/referees` | List referees |
| GET | `/frmf/referees/{id}` | Get referee |
| POST | `/frmf/referees` | Create referee |
| PUT | `/frmf/referees/{id}` | Update referee |
| GET | `/frmf/refereechain` | Get blockchain |
| GET | `/frmf/refereechain/verify` | Verify chain |
| GET | `/frmf/var-decisions` | VAR decisions |
| GET | `/frmf/var-decisions/{id}` | Get VAR decision |
| POST | `/frmf/var-decisions` | Add VAR decision |
| GET | `/frmf/var-decisions/{id}/verify` | Verify VAR |
| GET | `/frmf/players` | List players |
| GET | `/frmf/players/{id}` | Get player |
| POST | `/frmf/players` | Create player |
| GET | `/frmf/contracts` | List contracts |
| POST | `/frmf/contracts` | Create contract |
| GET | `/frmf/contracts/{id}` | Get contract |
| GET | `/frmf/medical` | Medical records |
| POST | `/frmf/medical` | Add medical record |
| GET | `/frmf/performance` | Performance stats |
| GET | `/frmf/matches` | Match assignments |
| POST | `/frmf/matches` | Create assignment |

---

## HAYAT HEALTH (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hayat/sessions` | List sessions |
| GET | `/hayat/sessions/{id}` | Get session |
| POST | `/hayat/sessions` | Create session |
| PUT | `/hayat/sessions/{id}` | Update session |
| GET | `/hayat/wellbeing/{user_id}` | Wellbeing logs |
| POST | `/hayat/wellbeing` | Add wellbeing log |
| GET | `/hayat/crisis` | Crisis alerts |
| POST | `/hayat/crisis` | Create crisis alert |
| PUT | `/hayat/crisis/{id}` | Update crisis |
| GET | `/hayat/rehabilitation` | Rehabilitation |
| GET | `/hayat/stats` | Statistics |

---

## INCLUSION (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inclusion/women/hubs` | Women hubs |
| GET | `/inclusion/women/players` | Women players |
| POST | `/inclusion/women/players` | Add player |
| GET | `/inclusion/paralympics` | Paralympic athletes |
| POST | `/inclusion/paralympics` | Add athlete |
| GET | `/inclusion/programs` | Programs |
| POST | `/inclusion/programs` | Create program |
| GET | `/inclusion/events` | Events |
| POST | `/inclusion/events` | Create event |
| GET | `/inclusion/stats` | Statistics |

---

## ANTI-HATE SHIELD (14 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/antihate/incidents` | List incidents |
| GET | `/antihate/incidents/{id}` | Get incident |
| POST | `/antihate/incidents` | Report incident |
| PUT | `/antihate/incidents/{id}` | Update incident |
| GET | `/antihate/monitoring` | Monitored accounts |
| POST | `/antihate/monitoring` | Add to monitoring |
| GET | `/antihate/legal` | Legal cases |
| GET | `/antihate/legal/{id}` | Get legal case |
| POST | `/antihate/legal` | Create legal case |
| PUT | `/antihate/legal/{id}` | Update legal case |
| GET | `/antihate/wellness` | Wellness checks |
| POST | `/antihate/wellness` | Add wellness check |
| GET | `/antihate/stats` | Statistics |

---

## NIL - NEWS INTELLIGENCE (16 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/nil/signals` | List signals |
| GET | `/nil/signals/{id}` | Get signal |
| POST | `/nil/signals` | Create signal |
| PUT | `/nil/signals/{id}` | Update signal |
| GET | `/nil/signals/{id}/evidence` | Get evidence |
| POST | `/nil/signals/{id}/evidence` | Add evidence |
| GET | `/nil/sources` | List sources |
| POST | `/nil/sources` | Add source |
| GET | `/nil/fact-cards` | Fact cards |
| GET | `/nil/fact-cards/{id}` | Get fact card |
| POST | `/nil/fact-cards` | Create fact card |
| PUT | `/nil/fact-cards/{id}` | Update fact card |
| GET | `/nil/forensics` | Forensics |
| GET | `/nil/crisis` | Crisis playbook |
| GET | `/nil/stats` | Statistics |

---

## ANALYTICS (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/overview` | Overview stats |
| GET | `/analytics/talents` | Talent analytics |
| GET | `/analytics/transfers` | Transfer analytics |
| GET | `/analytics/tickets` | Ticket analytics |
| GET | `/analytics/financial` | Financial analytics |
| GET | `/analytics/security` | Security analytics |
| GET | `/analytics/export` | Export report |

---

## ADMIN (12 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List users |
| GET | `/admin/users/{id}` | Get user |
| POST | `/admin/users` | Create user |
| PUT | `/admin/users/{id}` | Update user |
| DELETE | `/admin/users/{id}` | Delete user |
| GET | `/admin/audit` | Audit logs |
| GET | `/admin/sessions` | Active sessions |
| DELETE | `/admin/sessions/{id}` | Terminate session |
| GET | `/admin/settings` | System settings |
| PUT | `/admin/settings` | Update settings |
| GET | `/admin/health` | System health |
| POST | `/admin/backup` | Create backup |

---

## TOTAAL ENDPOINTS

| Module | Endpoints |
|--------|-----------|
| Auth | 7 |
| Dashboard | 5 |
| NTSP (Talents) | 26 |
| Transfers | 12 |
| Academy | 15 |
| Transfer Market | 18 |
| TicketChain | 16 |
| Foundation | 10 |
| Wallet | 14 |
| Subscriptions | 12 |
| FanDorpen | 20 |
| Consulate | 12 |
| Identity | 10 |
| Maroc ID | 14 |
| FRMF | 22 |
| Hayat | 12 |
| Inclusion | 12 |
| Anti-Hate | 14 |
| NIL | 16 |
| Analytics | 8 |
| Admin | 12 |
| **TOTAAL** | **~287** |

---

## HTTP STATUS CODES

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created |
| 204 | No Content (delete) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

---

## RESPONSE FORMAT

```json
// Success
{
  "success": true,
  "data": { ... },
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [...]
  }
}
```

---

## VOLGENDE STAP

**Fase 1.1:** Backend project setup
- FastAPI initialisatie
- Database configuratie
- Auth implementatie

---

*Document gegenereerd: Fase 0.3 Complete*
