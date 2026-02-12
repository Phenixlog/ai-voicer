import { Check, Sparkles, Zap, Crown, ExternalLink } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

import { useBilling } from '../hooks/useBilling';
import { useAuth } from '../hooks/useAuth';
import { useState } from 'react';

// Plan Feature Component
const PlanFeature = ({ text, included = true }: { text: string; included?: boolean }) => (
  <li className={`flex items-center gap-3 text-sm ${included ? 'text-slate-600' : 'text-slate-400'}`}>
    <div className={`w-5 h-5 rounded-full flex items-center justify-center ${included ? 'bg-emerald-100' : 'bg-slate-100'}`}>
      <Check className={`w-3 h-3 ${included ? 'text-emerald-600' : 'text-slate-400'}`} />
    </div>
    <span className={included ? '' : 'line-through'}>{text}</span>
  </li>
);

// Plan Card Component
interface PlanCardProps {
  name: string;
  description: string;
  price: string;
  period: string;
  features: { text: string; included?: boolean }[];
  icon: React.ReactNode;
  popular?: boolean;
  current?: boolean;
  onSelect?: () => void;
  isLoading?: boolean;
}

const PlanCard = ({ 
  name, 
  description, 
  price, 
  period, 
  features, 
  icon, 
  popular = false,
  current = false,
  onSelect,
  isLoading = false
}: PlanCardProps) => (
  <div className={`relative rounded-2xl p-6 ${
    popular 
      ? 'bg-white border-2 border-primary-500 shadow-xl shadow-primary-500/10' 
      : 'bg-white border border-slate-200 hover:border-slate-300 hover:shadow-lg transition-all'
  }`}>
    {popular && (
      <div className="absolute -top-3 left-1/2 -translate-x-1/2">
        <span className="px-3 py-1 text-xs font-semibold text-white bg-primary-600 rounded-full">
          Populaire
        </span>
      </div>
    )}
    
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <h3 className="text-lg font-semibold text-slate-900">{name}</h3>
      </div>
      <p className="text-slate-500 text-sm">{description}</p>
    </div>
    
    <div className="mb-6">
      <span className="text-4xl font-bold text-slate-900">{price}</span>
      <span className="text-slate-500">{period}</span>
    </div>
    
    <ul className="space-y-3 mb-6">
      {features.map((feature, index) => (
        <PlanFeature key={index} text={feature.text} included={feature.included !== false} />
      ))}
    </ul>
    
    {current ? (
      <Button variant="secondary" className="w-full" disabled>
        Plan actuel
      </Button>
    ) : (
      <Button 
        variant={popular ? 'primary' : 'secondary'} 
        className="w-full"
        onClick={onSelect}
        isLoading={isLoading}
      >
        {price === '0€' ? 'Commencer gratuitement' : 'Choisir ce plan'}
      </Button>
    )}
  </div>
);

// Pricing Plans Component
const PricingPlans = () => {
  const { checkout, isCheckoutLoading } = useBilling();
  const { user } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const handleSelectPlan = (planCode: string) => {
    setSelectedPlan(planCode);
    checkout(planCode);
  };

  const plansData = [
    {
      code: 'free',
      name: 'Free',
      description: 'Pour tester et usages légers',
      price: '0€',
      period: '/mois',
      icon: <Sparkles className="w-5 h-5 text-amber-500" />,
      features: [
        { text: '30 minutes/mois' },
        { text: 'Transcription standard' },
        { text: 'Support communautaire' },
        { text: 'Historique 24h', included: false },
      ],
    },
    {
      code: 'pro',
      name: 'Pro',
      description: 'Pour les créateurs réguliers',
      price: '12€',
      period: '/mois',
      icon: <Zap className="w-5 h-5 text-primary-500" />,
      popular: true,
      features: [
        { text: '5 heures/mois' },
        { text: 'Styles personnalisés' },
        { text: 'Historique 7 jours' },
        { text: 'Support prioritaire' },
      ],
    },
    {
      code: 'power',
      name: 'Power',
      description: 'Pour les power users',
      price: '29€',
      period: '/mois',
      icon: <Crown className="w-5 h-5 text-purple-500" />,
      features: [
        { text: 'Illimité' },
        { text: 'Latence prioritaire' },
        { text: 'Historique 30 jours' },
        { text: 'Support dédié' },
      ],
    },
  ];

  return (
    <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
      {plansData.map((plan) => (
        <PlanCard
          key={plan.code}
          {...plan}
          current={user?.plan === plan.code}
          onSelect={() => handleSelectPlan(plan.code)}
          isLoading={isCheckoutLoading && selectedPlan === plan.code}
        />
      ))}
    </div>
  );
};

// Current Subscription Component
const CurrentSubscription = () => {
  const { user } = useAuth();
  const { openPortal, isPortalLoading } = useBilling();

  if (!user || user.plan === 'free') {
    return (
      <Card className="bg-gradient-to-br from-primary-50 to-emerald-50 border-primary-200">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-primary-600" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-900">Vous utilisez le plan Free</h3>
            <p className="text-sm text-slate-600">Passez à Pro pour débloquer plus de fonctionnalités</p>
          </div>
          <Button variant="primary">
            Passer à Pro
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
            <Crown className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">Plan {user.plan.charAt(0).toUpperCase() + user.plan.slice(1)}</h3>
            <p className="text-sm text-slate-600">Renouvellement automatique le 15 de chaque mois</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Button 
            variant="secondary" 
            onClick={() => openPortal()}
            isLoading={isPortalLoading}
            rightIcon={<ExternalLink className="w-4 h-4" />}
          >
            Gérer l'abonnement
          </Button>
        </div>
      </div>
    </Card>
  );
};

// Billing History Component
const BillingHistory = () => {
  const history = [
    { date: '15 Jan 2025', description: 'Théoria Pro - Janvier 2025', amount: '12,00€', status: 'Payé' },
    { date: '15 Déc 2024', description: 'Théoria Pro - Décembre 2024', amount: '12,00€', status: 'Payé' },
    { date: '15 Nov 2024', description: 'Théoria Pro - Novembre 2024', amount: '12,00€', status: 'Payé' },
  ];

  return (
    <Card>
      <h3 className="font-semibold text-slate-900 mb-4">Historique de facturation</h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Date</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Description</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Montant</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Statut</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item, index) => (
              <tr key={index} className="border-b border-slate-100 last:border-0">
                <td className="py-3 px-4 text-sm text-slate-600">{item.date}</td>
                <td className="py-3 px-4 text-sm text-slate-900">{item.description}</td>
                <td className="py-3 px-4 text-sm text-slate-900 font-medium">{item.amount}</td>
                <td className="py-3 px-4">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-700">
                    {item.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

// Main Billing Component
export const Billing = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Facturation</h1>
        <p className="text-slate-600">Gérez votre abonnement et vos paiements</p>
      </div>

      {/* Current Subscription */}
      <CurrentSubscription />

      {/* Pricing Plans */}
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-6 text-center">Choisissez votre formule</h2>
        <PricingPlans />
      </div>

      {/* Billing History (only for paid plans) */}
      {user?.plan !== 'free' && <BillingHistory />}

      {/* FAQ */}
      <Card>
        <h3 className="font-semibold text-slate-900 mb-4">Questions fréquentes</h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-slate-900 mb-1">Puis-je changer de plan à tout moment ?</h4>
            <p className="text-sm text-slate-600">Oui, vous pouvez upgrader ou downgrader votre plan à tout moment. Les changements prennent effet immédiatement.</p>
          </div>
          <div>
            <h4 className="font-medium text-slate-900 mb-1">Que se passe-t-il si je dépasse mon quota ?</h4>
            <p className="text-sm text-slate-600">Vous recevrez une alerte à 80% de votre quota. Une fois atteint, vous devrez attendre le renouvellement ou upgrader votre plan.</p>
          </div>
          <div>
            <h4 className="font-medium text-slate-900 mb-1">Comment annuler mon abonnement ?</h4>
            <p className="text-sm text-slate-600">Vous pouvez annuler à tout moment depuis le portail client Stripe. Votre accès reste actif jusqu'à la fin de la période payée.</p>
          </div>
        </div>
      </Card>
    </div>
  );
};
