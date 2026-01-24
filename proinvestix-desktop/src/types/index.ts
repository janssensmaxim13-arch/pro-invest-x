// ============================================================================
// ProInvestiX Enterprise - TypeScript Types
// ============================================================================

// =============================================================================
// COMMON
// =============================================================================

export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    total: number
    page: number
    per_page: number
    total_pages: number
  }
}

export interface ApiError {
  detail: string
  status_code?: number
}

// =============================================================================
// AUTH
// =============================================================================

export interface User {
  id: number
  username: string
  email: string
  role: 'User' | 'Admin' | 'SuperAdmin' | 'Scout' | 'Academy'
  is_active: boolean
  is_verified: boolean
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// =============================================================================
// TALENTS
// =============================================================================

export interface Talent {
  id: number
  talent_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  nationality: string
  position: string
  current_club?: string
  height_cm?: number
  weight_kg?: number
  preferred_foot?: string
  is_diaspora: boolean
  diaspora_country?: string
  scout_rating?: number
  potential_rating?: number
  status: string
  created_at: string
}

export interface TalentCreate {
  first_name: string
  last_name: string
  date_of_birth: string
  nationality: string
  position: string
  current_club?: string
  is_diaspora?: boolean
  diaspora_country?: string
}

// =============================================================================
// TRANSFERS
// =============================================================================

export interface Transfer {
  id: number
  transfer_id: string
  talent_id: number
  from_club: string
  to_club: string
  transfer_type: 'Permanent' | 'Loan' | 'Free'
  transfer_fee?: number
  currency: string
  status: string
  training_compensation?: number
  solidarity_contribution?: number
  foundation_contribution?: number
  created_at: string
}

export interface CompensationCalculation {
  training_compensation: number
  solidarity_contribution: number
  foundation_contribution: number
  total: number
  breakdown: Record<string, number>
}

// =============================================================================
// EVENTS & TICKETS
// =============================================================================

export interface Event {
  id: number
  event_id: string
  name: string
  event_type: string
  venue: string
  city: string
  country: string
  event_date: string
  total_tickets: number
  tickets_sold: number
  ticket_price: number
  status: string
  created_at: string
}

export interface Ticket {
  id: number
  ticket_id: string
  event_id: number
  owner_id: number
  ticket_type: string
  blockchain_hash: string
  status: string
  purchased_at: string
  used_at?: string
}

export interface LoyaltyInfo {
  user_id: number
  points: number
  tier: string
  next_tier?: string
  points_to_next_tier?: number
}

// =============================================================================
// WALLET
// =============================================================================

export interface Wallet {
  id: number
  wallet_address: string
  user_id: number
  balance: number
  currency: string
  is_active: boolean
  created_at: string
}

export interface Transaction {
  id: number
  transaction_id: string
  wallet_id: number
  transaction_type: string
  amount: number
  currency: string
  status: string
  created_at: string
}

export interface DiasporaCard {
  id: number
  card_number: string
  card_type: string
  status: string
  expires_at: string
}

// =============================================================================
// FOUNDATION
// =============================================================================

export interface Donation {
  id: number
  donation_id: string
  user_id?: number
  amount: number
  currency: string
  donation_type: string
  is_anonymous: boolean
  receipt_number: string
  created_at: string
}

export interface Project {
  id: number
  project_id: string
  name: string
  description: string
  target_amount: number
  current_amount: number
  status: string
}

// =============================================================================
// ACADEMY
// =============================================================================

export interface Academy {
  id: number
  academy_id: string
  name: string
  city: string
  region: string
  country: string
  license_level: string
  capacity: number
  current_enrollment: number
  is_active: boolean
  created_at: string
}

export interface AcademyTeam {
  id: number
  team_id: string
  academy_id: number
  name: string
  age_group: string
  capacity: number
}

// =============================================================================
// FANDORPEN
// =============================================================================

export interface FanDorp {
  id: number
  fandorp_id: string
  name: string
  city: string
  country: string
  capacity: number
  status: string
  start_date: string
  end_date: string
}

export interface Volunteer {
  id: number
  volunteer_id: string
  fandorp_id: number
  user_id: number
  role: string
  status: string
  hours_worked: number
}

// =============================================================================
// FRMF
// =============================================================================

export interface Referee {
  id: number
  referee_id: string
  first_name: string
  last_name: string
  license_grade: string
  region: string
  total_matches: number
  avg_rating?: number
  is_active: boolean
}

export interface VARDecision {
  id: number
  decision_id: string
  match_id: string
  minute: number
  decision_type: string
  original_decision: string
  final_decision: string
  decision_changed: boolean
  blockchain_hash: string
  verified: boolean
}

// =============================================================================
// IDENTITY
// =============================================================================

export interface Identity {
  id: number
  identity_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  nationality: string
  verification_level: number
  is_verified: boolean
  status: string
}

export interface MarocID {
  id: number
  maroc_id: string
  first_name_fr: string
  last_name_fr: string
  cin_number?: string
  verification_level: number
  kyc_status: string
  wallet_address?: string
}

export interface Certificate {
  id: number
  certificate_id: string
  maroc_id: number
  certificate_type: string
  status: string
  issued_at: string
  expires_at: string
  qr_code?: string
}

// =============================================================================
// HAYAT
// =============================================================================

export interface HayatSession {
  id: number
  session_id: string
  user_id?: number
  session_type: string
  status: string
  scheduled_at?: string
  duration_minutes?: number
  wellbeing_score_after?: number
}

export interface CrisisAlert {
  id: number
  alert_id: string
  severity: string
  description: string
  status: string
  response_time_minutes?: number
  created_at: string
}

// =============================================================================
// ANTI-HATE
// =============================================================================

export interface AntiHateIncident {
  id: number
  incident_id: string
  incident_type: string
  platform?: string
  severity: string
  description: string
  status: string
  legal_action_taken: boolean
  reported_at: string
}

export interface LegalCase {
  id: number
  case_id: string
  incident_id: number
  case_type: string
  status: string
  verdict?: string
  filed_at: string
}

// =============================================================================
// NIL
// =============================================================================

export interface NILSignal {
  id: number
  signal_id: string
  signal_type: string
  headline: string
  content_summary: string
  severity: string
  status: string
  fact_check_result?: string
}

export interface FactCard {
  id: number
  card_id: string
  title: string
  claim: string
  verdict: string
  explanation: string
  views: number
  shares: number
}

// =============================================================================
// CONSULATE
// =============================================================================

export interface Consulate {
  id: string
  name: string
  city: string
  country: string
}

export interface ConsularDocument {
  id: number
  document_id: string
  document_type: string
  status: string
  tracking_number: string
  submitted_at: string
  pickup_location?: string
}

export interface Appointment {
  id: number
  appointment_id: string
  service_type: string
  consulate_name?: string
  scheduled_date: string
  scheduled_time?: string
  status: string
  confirmation_code?: string
}

// =============================================================================
// DASHBOARD
// =============================================================================

export interface DashboardStats {
  total_talents: number
  total_transfers: number
  total_events: number
  total_users: number
  transfer_volume: number
  tickets_sold: number
}

export interface KPI {
  label: string
  value: number | string
  change?: number
  trend?: 'up' | 'down' | 'neutral'
}

export interface ChartData {
  data: Array<{
    label: string
    value: number
    [key: string]: any
  }>
}
