import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios'

const API_URL = 'https://pro-invest-x-production.up.railway.app/api/v1'

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors & token refresh
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
    
    // Handle 401 - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)
          
          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${access_token}`
          }
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/auth/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// =============================================================================
// AUTH API
// =============================================================================

export const authApi = {
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  
  register: (data: { username: string; email: string; password: string; first_name?: string; last_name?: string }) =>
    api.post('/auth/register', data),
  
  me: () => api.get('/auth/me'),
  
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
  
  logout: () => api.post('/auth/logout'),
}

// =============================================================================
// DASHBOARD API
// =============================================================================

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getKPIs: () => api.get('/dashboard/kpis'),
  getChart: (chartType: string) => api.get(`/dashboard/charts/${chartType}`),
  getActivity: (limit?: number) => api.get('/dashboard/activity', { params: { limit } }),
  getWKCountdown: () => api.get('/dashboard/wk-countdown'),
}

// =============================================================================
// TALENTS API
// =============================================================================

export const talentsApi = {
  list: (params?: Record<string, any>) => api.get('/talents', { params }),
  get: (id: number) => api.get(`/talents/${id}`),
  create: (data: any) => api.post('/talents', data),
  update: (id: number, data: any) => api.put(`/talents/${id}`, data),
  delete: (id: number) => api.delete(`/talents/${id}`),
  getStats: () => api.get('/talents/stats/overview'),
  getFilters: () => api.get('/talents/filters/options'),
}

// =============================================================================
// SCOUTS API
// =============================================================================

export const scoutsApi = {
  list: (params?: Record<string, any>) => api.get('/scouts', { params }),
  get: (id: number) => api.get(`/scouts/${id}`),
  create: (data: any) => api.post('/scouts', data),
  update: (id: number, data: any) => api.put(`/scouts/${id}`, data),
  delete: (id: number) => api.delete(`/scouts/${id}`),
  getReports: (scoutId: number) => api.get(`/scouts/${scoutId}/reports`),
}

// =============================================================================
// TRANSFERS API
// =============================================================================

export const transfersApi = {
  list: (params?: Record<string, any>) => api.get('/transfers', { params }),
  get: (id: number) => api.get(`/transfers/${id}`),
  create: (data: any) => api.post('/transfers', data),
  update: (id: number, data: any) => api.put(`/transfers/${id}`, data),
  calculate: (data: any) => api.post('/transfers/calculate', data),
  getStats: () => api.get('/transfers/stats/overview'),
}

// =============================================================================
// EVENTS API
// =============================================================================

export const eventsApi = {
  list: (params?: Record<string, any>) => api.get('/events', { params }),
  get: (id: number) => api.get(`/events/${id}`),
  create: (data: any) => api.post('/events', data),
  update: (id: number, data: any) => api.put(`/events/${id}`, data),
  delete: (id: number) => api.delete(`/events/${id}`),
  mintTicket: (eventId: number, data: any) => api.post(`/events/${eventId}/tickets/mint`, data),
  getStats: () => api.get('/events/stats/overview'),
}

// =============================================================================
// TICKETS API
// =============================================================================

export const ticketsApi = {
  list: (params?: Record<string, any>) => api.get('/tickets', { params }),
  get: (id: number) => api.get(`/tickets/${id}`),
  verify: (hash: string) => api.get(`/tickets/${hash}/verify`),
  transfer: (ticketId: number, data: any) => api.post(`/tickets/${ticketId}/transfer`, data),
  getMyTickets: () => api.get('/tickets/my/tickets'),
  getMyLoyalty: () => api.get('/tickets/loyalty/me'),
}

// =============================================================================
// WALLETS API
// =============================================================================

export const walletsApi = {
  getMyWallet: () => api.get('/wallets/me'),
  get: (id: number) => api.get(`/wallets/${id}`),
  deposit: (walletId: number, data: any) => api.post(`/wallets/${walletId}/deposit`, data),
  withdraw: (walletId: number, data: any) => api.post(`/wallets/${walletId}/withdraw`, data),
  transfer: (walletId: number, data: any) => api.post(`/wallets/${walletId}/transfer`, data),
  getTransactions: (walletId: number, params?: any) => api.get(`/wallets/${walletId}/transactions`, { params }),
  getCards: (walletId: number) => api.get(`/wallets/${walletId}/cards`),
  createCard: (walletId: number, data: any) => api.post(`/wallets/${walletId}/cards`, data),
  getStats: () => api.get('/wallets/stats/overview'),
}

// =============================================================================
// FOUNDATION API
// =============================================================================

export const foundationApi = {
  getStats: () => api.get('/foundation/stats'),
  getDonations: () => api.get('/foundation/donations'),
  createDonation: (data: any) => api.post('/foundation/donations', data),
  getMyDonations: () => api.get('/foundation/my-donations'),
  getContributions: () => api.get('/foundation/contributions'),
  getProjects: () => api.get('/foundation/projects'),
}

// =============================================================================
// ACADEMIES API
// =============================================================================

export const academiesApi = {
  list: (params?: Record<string, any>) => api.get('/academies', { params }),
  get: (id: number) => api.get(`/academies/${id}`),
  create: (data: any) => api.post('/academies', data),
  update: (id: number, data: any) => api.put(`/academies/${id}`, data),
  delete: (id: number) => api.delete(`/academies/${id}`),
  getTeams: (academyId: number) => api.get(`/academies/${academyId}/teams`),
  createTeam: (academyId: number, data: any) => api.post(`/academies/${academyId}/teams`, data),
  getStaff: (academyId: number) => api.get(`/academies/${academyId}/staff`),
  createStaff: (academyId: number, data: any) => api.post(`/academies/${academyId}/staff`, data),
  getStats: () => api.get('/academies/stats/overview'),
}

// =============================================================================
// SUBSCRIPTIONS API
// =============================================================================

export const subscriptionsApi = {
  getPlans: () => api.get('/subscriptions/plans'),
  getMySubscription: () => api.get('/subscriptions/me'),
  create: (data: any) => api.post('/subscriptions', data),
  cancel: (id: number) => api.delete(`/subscriptions/${id}`),
  giftSubscription: (data: any) => api.post('/subscriptions/gift', data),
}

// =============================================================================
// FANDORPEN API
// =============================================================================

export const fandorpenApi = {
  list: (params?: Record<string, any>) => api.get('/fandorpen', { params }),
  get: (id: number) => api.get(`/fandorpen/${id}`),
  create: (data: any) => api.post('/fandorpen', data),
  getVolunteers: (id: number) => api.get(`/fandorpen/${id}/volunteers`),
  registerVolunteer: (id: number, data: any) => api.post(`/fandorpen/${id}/volunteers`, data),
  getShifts: (id: number) => api.get(`/fandorpen/${id}/shifts`),
  checkinShift: (fandorpId: number, shiftId: number) => 
    api.post(`/fandorpen/${fandorpId}/shifts/${shiftId}/checkin`),
  getStats: () => api.get('/fandorpen/stats/overview'),
}

// =============================================================================
// FRMF API
// =============================================================================

export const frmfApi = {
  // Referees
  listReferees: (params?: any) => api.get('/frmf/referees', { params }),
  getReferee: (id: number) => api.get(`/frmf/referees/${id}`),
  createReferee: (data: any) => api.post('/frmf/referees', data),
  
  // VAR Decisions
  listVARDecisions: (params?: any) => api.get('/frmf/var-decisions', { params }),
  createVARDecision: (data: any) => api.post('/frmf/var-decisions', data),
  verifyVARDecision: (id: number) => api.get(`/frmf/var-decisions/${id}/verify`),
  
  // Players
  listPlayers: (params?: any) => api.get('/frmf/players', { params }),
  createPlayer: (data: any) => api.post('/frmf/players', data),
  
  // Blockchain
  getRefereeChain: () => api.get('/frmf/refereechain'),
  verifyChain: () => api.get('/frmf/refereechain/verify'),
  
  getStats: () => api.get('/frmf/stats/overview'),
}

// =============================================================================
// IDENTITY API
// =============================================================================

export const identitiesApi = {
  list: (params?: any) => api.get('/identities', { params }),
  getMyIdentity: () => api.get('/identities/me'),
  get: (id: number) => api.get(`/identities/${id}`),
  create: (data: any) => api.post('/identities', data),
  update: (id: number, data: any) => api.put(`/identities/${id}`, data),
  verify: (id: number, data: any) => api.post(`/identities/${id}/verify`, data),
  listFraudAlerts: (params?: any) => api.get('/identities/fraud/alerts', { params }),
  createFraudAlert: (data: any) => api.post('/identities/fraud/alerts', data),
  getStats: () => api.get('/identities/stats/overview'),
}

// =============================================================================
// MAROC ID API
// =============================================================================

export const marocIdApi = {
  list: (params?: any) => api.get('/maroc-id', { params }),
  getMyMarocId: () => api.get('/maroc-id/me'),
  get: (id: number) => api.get(`/maroc-id/${id}`),
  create: (data: any) => api.post('/maroc-id', data),
  verify: (id: number, data: any) => api.post(`/maroc-id/${id}/verify`, data),
  getLevel: (id: number) => api.get(`/maroc-id/${id}/level`),
  getCertificates: (marocIdId?: number) => api.get('/maroc-id/certificates', { params: { maroc_id_pk: marocIdId } }),
  issueCertificate: (data: any) => api.post('/maroc-id/certificates', data),
  sign: (data: any) => api.post('/maroc-id/sign', data),
  getStats: () => api.get('/maroc-id/stats/overview'),
}

// =============================================================================
// HAYAT API
// =============================================================================

export const hayatApi = {
  listSessions: (params?: any) => api.get('/hayat/sessions', { params }),
  getSession: (id: number) => api.get(`/hayat/sessions/${id}`),
  createSession: (data: any) => api.post('/hayat/sessions', data),
  updateSession: (id: number, params: any) => api.put(`/hayat/sessions/${id}`, null, { params }),
  getWellbeing: (userId: number) => api.get(`/hayat/wellbeing/${userId}`),
  logWellbeing: (params: any) => api.post('/hayat/wellbeing', null, { params }),
  listCrisisAlerts: (params?: any) => api.get('/hayat/crisis', { params }),
  createCrisisAlert: (data: any) => api.post('/hayat/crisis', data),
  getStats: () => api.get('/hayat/stats'),
}

// =============================================================================
// ANTI-HATE API
// =============================================================================

export const antihateApi = {
  listIncidents: (params?: any) => api.get('/antihate/incidents', { params }),
  getIncident: (id: number) => api.get(`/antihate/incidents/${id}`),
  reportIncident: (data: any) => api.post('/antihate/incidents', data),
  updateIncident: (id: number, params: any) => api.put(`/antihate/incidents/${id}`, null, { params }),
  listLegalCases: (params?: any) => api.get('/antihate/legal', { params }),
  createLegalCase: (data: any) => api.post('/antihate/legal', data),
  getStats: () => api.get('/antihate/stats'),
}

// =============================================================================
// NIL API
// =============================================================================

export const nilApi = {
  listSignals: (params?: any) => api.get('/nil/signals', { params }),
  getSignal: (id: number) => api.get(`/nil/signals/${id}`),
  createSignal: (data: any) => api.post('/nil/signals', data),
  updateSignal: (id: number, params: any) => api.put(`/nil/signals/${id}`, null, { params }),
  listFactCards: (params?: any) => api.get('/nil/factcards', { params }),
  getFactCard: (id: number) => api.get(`/nil/factcards/${id}`),
  createFactCard: (data: any) => api.post('/nil/factcards', data),
  shareFactCard: (id: number) => api.post(`/nil/factcards/${id}/share`),
  search: (query: string) => api.get('/nil/search', { params: { query } }),
  getStats: () => api.get('/nil/stats'),
}

// =============================================================================
// CONSULATE API
// =============================================================================

export const consulateApi = {
  listConsulates: (country?: string) => api.get('/consulate/list', { params: { country } }),
  listDocuments: (params?: any) => api.get('/consulate/documents', { params }),
  getDocument: (id: number) => api.get(`/consulate/documents/${id}`),
  requestDocument: (data: any) => api.post('/consulate/documents', data),
  trackDocument: (id: number) => api.get(`/consulate/documents/${id}/track`),
  listAppointments: (upcomingOnly?: boolean) => api.get('/consulate/appointments', { params: { upcoming_only: upcomingOnly } }),
  getAppointment: (id: number) => api.get(`/consulate/appointments/${id}`),
  createAppointment: (data: any) => api.post('/consulate/appointments', data),
  cancelAppointment: (id: number) => api.delete(`/consulate/appointments/${id}`),
  getStats: () => api.get('/consulate/stats'),
}

// =============================================================================
// ADMIN API
// =============================================================================

export const adminApi = {
  listUsers: (params?: any) => api.get('/admin/users', { params }),
  getUser: (id: number) => api.get(`/admin/users/${id}`),
  createUser: (data: any) => api.post('/admin/users', data),
  updateUser: (id: number, data: any) => api.put(`/admin/users/${id}`, data),
  deleteUser: (id: number) => api.delete(`/admin/users/${id}`),
  listSessions: (params?: any) => api.get('/admin/sessions', { params }),
  terminateSession: (id: number) => api.delete(`/admin/sessions/${id}`),
  getAuditLogs: (params?: any) => api.get('/admin/audit', { params }),
  getHealth: () => api.get('/admin/health'),
  getSettings: () => api.get('/admin/settings'),
  getStats: () => api.get('/admin/stats'),
}

export default api
