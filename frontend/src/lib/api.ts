import axios, { AxiosInstance } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: `${API_URL}/api/v1`,
    headers: { 'Content-Type': 'application/json' },
    timeout: 60000,
  })

  // Attach access token to every request
  client.interceptors.request.use((config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  })

  // Handle 401 — try to refresh token, then retry the original request once
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      // Only attempt refresh on 401 and only once per request
      if (
        error.response?.status === 401 &&
        !originalRequest._retry &&
        !originalRequest.url?.includes('/auth/token/refresh/') &&
        !originalRequest.url?.includes('/auth/login/')
      ) {
        originalRequest._retry = true

        try {
          const refreshToken = localStorage.getItem('refresh_token')
          if (!refreshToken) throw new Error('No refresh token stored')

          const res = await axios.post(`${API_URL}/api/v1/auth/token/refresh/`, {
            refresh: refreshToken,
          })

          const { access, refresh } = res.data
          localStorage.setItem('access_token', access)
          // Save rotated refresh token if returned
          if (refresh) {
            localStorage.setItem('refresh_token', refresh)
          }

          // Sync to zustand store
          try {
            const { useAuthStore } = await import('@/store/auth')
            const state = useAuthStore.getState()
            if (state.tokens) {
              useAuthStore.setState({
                tokens: { access, refresh: refresh || refreshToken },
              })
            }
          } catch { /* ignore store sync errors */ }

          originalRequest.headers.Authorization = `Bearer ${access}`
          return client(originalRequest)
        } catch (refreshError) {
          // Refresh failed — clear tokens and redirect to login
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          try {
            const { useAuthStore } = await import('@/store/auth')
            useAuthStore.getState().logout()
          } catch { /* ignore */ }
          if (typeof window !== 'undefined') {
            window.location.href = '/login'
          }
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )

  return client
}

export const api = createApiClient()

// Auth
export const authApi = {
  register: (data: {
    email: string
    password: string
    password_confirm: string
    first_name?: string
    last_name?: string
    company?: string
  }) => api.post('/auth/register/', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login/', data),

  logout: (refreshToken: string) =>
    api.post('/auth/logout/', { refresh: refreshToken }),

  me: () => api.get('/auth/me/'),

  updateMe: (data: Partial<{
    first_name: string
    last_name: string
    company: string
    timezone: string
  }>) => api.patch('/auth/me/', data),

  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post('/auth/change-password/', data),

  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password/', { email }),

  resetPassword: (data: { token: string; new_password: string }) =>
    api.post('/auth/reset-password/', data),

  verifyEmail: (token: string) =>
    api.get(`/auth/verify-email/${token}/`),
}

// Validation
export const validationApi = {
  validateSingle: (email: string, checkSmtp = true) =>
    api.post('/validation/validate/', { email, check_smtp: checkSmtp }),

  getHistory: (params?: Record<string, string | number>) =>
    api.get('/validation/history/', { params }),

  getStats: (days = 30) =>
    api.get('/validation/stats/', { params: { days } }),
}

// Bulk Jobs
export const bulkApi = {
  uploadFile: (formData: FormData) =>
    api.post('/validation/bulk/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  getJobs: (params?: Record<string, string>) =>
    api.get('/validation/bulk/', { params }),

  getJob: (jobId: string) =>
    api.get(`/validation/bulk/${jobId}/`),

  getJobResults: (jobId: string, params?: Record<string, string | number>) =>
    api.get(`/validation/bulk/${jobId}/results/`, { params }),

  downloadResults: (jobId: string, statusFilter?: string) => {
    const params = statusFilter && statusFilter !== 'all' ? `?status=${statusFilter}` : ''
    return `${API_URL}/api/v1/validation/bulk/${jobId}/download/${params}`
  },

  cancelJob: (jobId: string) =>
    api.post(`/validation/bulk/${jobId}/cancel/`),
}

// API Keys
export const apiKeysApi = {
  list: () => api.get('/api-keys/'),
  create: (data: {
    name: string
    permissions: string
    rate_limit_per_hour?: number
    allowed_ips?: string[]
  }) => api.post('/api-keys/', data),
  update: (id: string, data: Partial<{ name: string; is_active: boolean }>) =>
    api.patch(`/api-keys/${id}/`, data),
  delete: (id: string) => api.delete(`/api-keys/${id}/`),
}

// Billing
export const billingApi = {
  getSubscription: () => api.get('/billing/subscription/'),
  getPlans: () => api.get('/billing/plans/'),
  getCreditPacks: () => api.get('/billing/credit-packs/'),
  getPayments: () => api.get('/billing/payments/'),
  createCheckout: (creditPackId: string) =>
    api.post('/billing/checkout/', {
      credit_pack_id: creditPackId,
      success_url: `${typeof window !== 'undefined' ? window.location.origin : ''}/billing?success=true`,
      cancel_url: `${typeof window !== 'undefined' ? window.location.origin : ''}/billing?cancelled=true`,
    }),
}

// Webhooks
export const webhooksApi = {
  list: () => api.get('/webhooks/'),
  create: (data: { name: string; url: string; events: string[] }) =>
    api.post('/webhooks/', data),
  update: (id: string, data: Partial<{ name: string; is_active: boolean; events: string[] }>) =>
    api.patch(`/webhooks/${id}/`, data),
  delete: (id: string) => api.delete(`/webhooks/${id}/`),
  test: (id: string) => api.post(`/webhooks/${id}/test/`),
  getDeliveries: (id: string) => api.get(`/webhooks/${id}/deliveries/`),
}
