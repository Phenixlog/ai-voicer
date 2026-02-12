// User types
export interface User {
  id: string;
  email: string;
  name: string | null;
  locale: string;
  plan: string;
  created_at: string;
}

export interface UserSettings {
  hotkey: string;
  trigger_mode: 'hold' | 'toggle';
  language: string;
  style_mode: string;
  context_bias: string | null;
  hud_enabled: boolean;
}

// Auth types
export interface LoginRequest {
  email: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Plan types
export interface Plan {
  id: string;
  code: string;
  name: string;
  monthly_minutes: number;
  price_cents: number;
  currency: string;
}

// Usage types
export interface UsageStats {
  plan: {
    name: string;
    monthly_minutes: number;
  };
  usage: {
    used_minutes: number;
    remaining_minutes: number | 'unlimited';
    percentage: number;
  };
  success_rate_percent: number;
  total_transcriptions: number;
  average_latency_ms: number;
}

export interface UsageEvent {
  id: string;
  audio_seconds: number;
  success: boolean;
  created_at: string;
  context?: string;
}

// Billing types
export interface CheckoutSession {
  session_id: string;
  url: string;
}

export interface PortalSession {
  url: string;
}

// UI types
export interface NavItem {
  label: string;
  href: string;
  icon: string;
}
