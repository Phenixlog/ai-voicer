import { apiClient } from './client';
import type { Plan, CheckoutSession, PortalSession } from '../types';

export const billingApi = {
  async getPlans(): Promise<Plan[]> {
    const response = await apiClient.get<{ plans: Plan[] }>('/v1/plans');
    return response.plans;
  },

  async createCheckoutSession(planCode: string): Promise<CheckoutSession> {
    return apiClient.post<CheckoutSession>(`/v1/billing/checkout-session?plan_code=${planCode}`, {});
  },

  async createPortalSession(): Promise<PortalSession> {
    return apiClient.post<PortalSession>('/v1/billing/portal-session', {});
  },
};
