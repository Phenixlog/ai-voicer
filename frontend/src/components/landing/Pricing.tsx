import { Check, Sparkles, Zap, Crown } from 'lucide-react';

const plans = [
  {
    name: 'Free',
    description: 'Pour tester et usages légers',
    price: '0€',
    period: '/mois',
    icon: <Sparkles className="w-5 h-5 text-amber-500" />,
    features: [
      '30 minutes/mois',
      'Transcription standard',
      'Support communautaire',
    ],
  },
  {
    name: 'Pro',
    description: 'Pour les créateurs réguliers',
    price: '12€',
    period: '/mois',
    icon: <Zap className="w-5 h-5 text-primary-500" />,
    popular: true,
    features: [
      '5 heures/mois',
      'Styles personnalisés',
      'Historique 7 jours',
      'Support prioritaire',
    ],
  },
  {
    name: 'Power',
    description: 'Pour les power users',
    price: '29€',
    period: '/mois',
    icon: <Crown className="w-5 h-5 text-purple-500" />,
    features: [
      'Illimité',
      'Latence prioritaire',
      'Historique 30 jours',
      'Support dédié',
    ],
  },
];

export const Pricing = () => {
  return (
    <section id="pricing" className="max-w-7xl mx-auto px-6 py-24">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h2 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Pricing simple et transparent
        </h2>
        <p className="mt-4 text-lg text-slate-600">
          Commence gratuitement. Passe à Pro quand tu es prêt.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={`relative rounded-2xl p-8 transition-all ${
              plan.popular
                ? 'bg-white border-2 border-primary-500 shadow-xl shadow-primary-500/10 scale-105'
                : 'bg-white border border-slate-200 hover:border-slate-300 hover:shadow-lg'
            }`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="px-4 py-1 text-xs font-semibold text-white bg-primary-600 rounded-full">
                  Le plus populaire
                </span>
              </div>
            )}

            <div className="mb-6">
              <div className="flex items-center gap-2 mb-2">
                {plan.icon}
                <h3 className="text-lg font-semibold text-slate-900">{plan.name}</h3>
              </div>
              <p className="text-slate-500 text-sm">{plan.description}</p>
            </div>

            <div className="mb-8">
              <span className="text-5xl font-bold text-slate-900">{plan.price}</span>
              <span className="text-slate-500">{plan.period}</span>
            </div>

            <ul className="space-y-3 mb-8">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-center gap-3 text-sm text-slate-600">
                  <div className="w-5 h-5 rounded-full bg-accent-green-100 flex items-center justify-center flex-shrink-0">
                    <Check className="w-3 h-3 text-accent-green-600" />
                  </div>
                  {feature}
                </li>
              ))}
            </ul>

            <a
              href="/login"
              className={`block w-full text-center py-3 px-6 rounded-xl font-semibold transition-all ${
                plan.popular
                  ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/25'
                  : 'bg-slate-100 text-slate-900 hover:bg-slate-200'
              }`}
            >
              {plan.price === '0€' ? 'Commencer gratuitement' : 'Choisir ce plan'}
            </a>
          </div>
        ))}
      </div>
    </section>
  );
};
