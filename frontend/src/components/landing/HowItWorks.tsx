import { Keyboard, Mic, Sparkles, ClipboardPaste } from 'lucide-react';

const steps = [
  {
    icon: <Keyboard className="w-8 h-8" />,
    title: 'Appuie sur F8',
    description: 'Active la capture vocale depuis n\'importe quelle app.',
    color: 'bg-primary-50 text-primary-600',
  },
  {
    icon: <Mic className="w-8 h-8" />,
    title: 'Parle naturellement',
    description: 'Pas besoin de dicter lentement. Parle comme tu penses.',
    color: 'bg-accent-green-50 text-accent-green-600',
  },
  {
    icon: <Sparkles className="w-8 h-8" />,
    title: 'L\'IA structure',
    description: 'Ponctuation, orthographe, clarté — tout est nettoyé automatiquement.',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    icon: <ClipboardPaste className="w-8 h-8" />,
    title: 'Texte collé',
    description: 'Le texte propre est injecté directement dans ton champ actif.',
    color: 'bg-purple-50 text-purple-600',
  },
];

export const HowItWorks = () => {
  return (
    <section className="max-w-7xl mx-auto px-6 py-24">
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h2 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Comment ça marche
        </h2>
        <p className="mt-4 text-lg text-slate-600">
          4 étapes. Quelques secondes. Zéro friction.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {steps.map((step, index) => (
          <div key={step.title} className="relative text-center">
            {/* Connector line */}
            {index < steps.length - 1 && (
              <div className="hidden md:block absolute top-10 left-[60%] w-[calc(100%-20%)] h-px bg-slate-200" />
            )}

            {/* Step number */}
            <div className="relative inline-flex flex-col items-center">
              <div className={`w-20 h-20 rounded-2xl ${step.color} flex items-center justify-center mb-4`}>
                {step.icon}
              </div>
              <span className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
                {index + 1}
              </span>
            </div>

            <h3 className="font-semibold text-slate-900 mb-2">{step.title}</h3>
            <p className="text-sm text-slate-600">{step.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};
