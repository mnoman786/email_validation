export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  company: string
  is_verified: boolean
  date_joined: string
  timezone: string
  avatar?: string
}

export interface Subscription {
  id: string
  plan: string
  status: string
  available_credits: number
  total_credits_purchased: number
  total_credits_used: number
  trial_ends_at?: string
  current_period_start?: string
  current_period_end?: string
  plan_details: {
    name: string
    price: number
    credits: number
    features: string[]
  }
}

export type ValidationStatus =
  | 'valid'
  | 'invalid'
  | 'risky'
  | 'disposable'
  | 'spam_trap'
  | 'catch_all'
  | 'unknown'

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical'
export type DomainReputation = 'excellent' | 'good' | 'fair' | 'poor' | 'unknown'
export type SuggestedAction = 'safe_to_send' | 'send_with_caution' | 'do_not_send' | 'unknown'

export interface ValidationResult {
  id: string
  email: string
  status: ValidationStatus
  score: number
  is_valid: boolean
  local_part: string
  domain: string
  syntax_valid: boolean
  mx_found: boolean
  mx_records: string[]
  dns_valid: boolean
  smtp_check: boolean
  smtp_connectable: boolean
  smtp_response_code?: number
  is_disposable: boolean
  is_catch_all: boolean
  is_role_account: boolean
  is_free_provider: boolean
  is_spam_trap: boolean
  is_greylisted: boolean
  is_blacklisted: boolean
  domain_reputation: DomainReputation
  risk_level: RiskLevel
  suggested_action: SuggestedAction
  score_breakdown: Record<string, { points: number; max: number; label: string }>
  processing_time_ms: number
  validated_at: string
}

export interface BulkJob {
  id: string
  name: string
  original_filename: string
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
  total_emails: number
  processed_emails: number
  progress_percentage: number
  valid_count: number
  invalid_count: number
  risky_count: number
  disposable_count: number
  catch_all_count: number
  spam_trap_count: number
  unknown_count: number
  credits_used: number
  created_at: string
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  error_message?: string
}

export interface APIKey {
  id: string
  name: string
  key_prefix: string
  permissions: string
  is_active: boolean
  created_at: string
  last_used_at?: string
  expires_at?: string
  rate_limit_per_hour: number
  total_requests: number
  allowed_ips: string[]
}

export interface Webhook {
  id: string
  name: string
  url: string
  events: string[]
  is_active: boolean
  created_at: string
  last_triggered_at?: string
  total_deliveries: number
  failed_deliveries: number
}

export interface CreditPack {
  id: string
  name: string
  credits: number
  price_usd: number
  is_popular: boolean
}

export interface Plan {
  id: string
  name: string
  price: number
  credits: number
  features: string[]
}

export interface Payment {
  id: string
  payment_type: string
  status: string
  amount_usd: number
  credits_added: number
  description: string
  created_at: string
}

export interface ValidationStats {
  overview: {
    total_validations: number
    valid_count: number
    invalid_count: number
    risky_count: number
    disposable_count: number
    catch_all_count: number
    spam_trap_count: number
    unknown_count: number
    average_score: number
    valid_percentage: number
    total_bulk_jobs: number
  }
  daily_breakdown: Array<{
    date: string
    count: number
    avg_score: number
  }>
}

export interface PaginatedResponse<T> {
  pagination: {
    count: number
    total_pages: number
    current_page: number
    page_size: number
    next: string | null
    previous: string | null
  }
  results: T[]
}

export interface AuthTokens {
  access: string
  refresh: string
}
