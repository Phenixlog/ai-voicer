import { useQuery, useMutation } from '@tanstack/react-query';
import { billingApi } from '../api/billing';

export const useBilling = () => {
  const plansQuery = useQuery({
    queryKey: ['billing', 'plans'],
    queryFn: () => billingApi.getPlans(),
    staleTime: 1000 * 60 * 60, // 1 hour
  });

  const checkoutMutation = useMutation({
    mutationFn: (planCode: string) => billingApi.createCheckoutSession(planCode),
    onSuccess: (data) => {
      // Redirect to Stripe checkout
      window.location.href = data.url;
    },
  });

  const portalMutation = useMutation({
    mutationFn: () => billingApi.createPortalSession(),
    onSuccess: (data) => {
      // Redirect to Stripe portal
      window.location.href = data.url;
    },
  });

  return {
    plans: plansQuery.data || [],
    isLoadingPlans: plansQuery.isLoading,
    checkout: checkoutMutation.mutate,
    isCheckoutLoading: checkoutMutation.isPending,
    openPortal: portalMutation.mutate,
    isPortalLoading: portalMutation.isPending,
  };
};
