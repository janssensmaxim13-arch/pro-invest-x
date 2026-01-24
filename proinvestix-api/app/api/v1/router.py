# ============================================================================
# ProInvestiX Enterprise API - Main Router
# ============================================================================

from fastapi import APIRouter

from app.api.v1.endpoints import auth
from app.api.v1.endpoints import dashboard
from app.api.v1.endpoints import talents
from app.api.v1.endpoints import scouts
from app.api.v1.endpoints import transfers
from app.api.v1.endpoints import events
from app.api.v1.endpoints import tickets
from app.api.v1.endpoints import wallets
from app.api.v1.endpoints import foundation
from app.api.v1.endpoints import academies
from app.api.v1.endpoints import subscriptions
from app.api.v1.endpoints import fandorpen
from app.api.v1.endpoints import admin
from app.api.v1.endpoints import frmf
from app.api.v1.endpoints import identities
from app.api.v1.endpoints import maroc_id
from app.api.v1.endpoints import hayat
from app.api.v1.endpoints import antihate
from app.api.v1.endpoints import nil
from app.api.v1.endpoints import consulate

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router)

# Dashboard
api_router.include_router(dashboard.router)

# NTSP - Talent Scouting
api_router.include_router(talents.router)
api_router.include_router(scouts.router)

# Transfers
api_router.include_router(transfers.router)

# TicketChain
api_router.include_router(events.router)
api_router.include_router(tickets.router)

# Diaspora Wallet
api_router.include_router(wallets.router)

# Foundation Bank
api_router.include_router(foundation.router)

# Academy
api_router.include_router(academies.router)

# Subscriptions
api_router.include_router(subscriptions.router)

# FanDorpen - WK 2030
api_router.include_router(fandorpen.router)

# FRMF
api_router.include_router(frmf.router)

# Identity Shield
api_router.include_router(identities.router)

# Maroc ID
api_router.include_router(maroc_id.router)

# Hayat Health
api_router.include_router(hayat.router)

# Anti-Hate Shield
api_router.include_router(antihate.router)

# NIL - News Intelligence
api_router.include_router(nil.router)

# Consulate Hub
api_router.include_router(consulate.router)

# Admin
api_router.include_router(admin.router)
