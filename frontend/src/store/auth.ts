import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { User, Subscription, AuthTokens } from '@/types'

interface AuthState {
  user: User | null
  subscription: Subscription | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  _hasHydrated: boolean

  setAuth: (user: User, subscription: Subscription | null, tokens: AuthTokens) => void
  setUser: (user: User) => void
  setSubscription: (subscription: Subscription) => void
  refreshSubscription: () => Promise<void>
  logout: () => void
  setHasHydrated: (state: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      subscription: null,
      tokens: null,
      isAuthenticated: false,
      _hasHydrated: false,

      setAuth: (user, subscription, tokens) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('access_token', tokens.access)
          localStorage.setItem('refresh_token', tokens.refresh)
        }
        set({ user, subscription, tokens, isAuthenticated: true })
      },

      setUser: (user) => set({ user }),

      setSubscription: (subscription) => set({ subscription }),

      refreshSubscription: async () => {
        try {
          const { billingApi } = await import('@/lib/api')
          const res = await billingApi.getSubscription()
          set({ subscription: res.data })
        } catch {
          // silently ignore — stale data is better than a crash
        }
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
        set({ user: null, subscription: null, tokens: null, isAuthenticated: false })
      },

      setHasHydrated: (state) => set({ _hasHydrated: state }),
    }),
    {
      name: 'emailguard-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        subscription: state.subscription,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        // Re-sync tokens to localStorage after rehydration
        if (state?.tokens && typeof window !== 'undefined') {
          localStorage.setItem('access_token', state.tokens.access)
          localStorage.setItem('refresh_token', state.tokens.refresh)
        }
        state?.setHasHydrated(true)
      },
    }
  )
)
