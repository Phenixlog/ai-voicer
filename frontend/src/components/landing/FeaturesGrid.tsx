import { Mic, Sparkles, Globe, Keyboard, Zap, Shield, Monitor, Languages, Settings } from 'lucide-react';

const features = [
  {
    icon: <Mic className="w-6 h-6" />,
    name: 'Push-to-talk fluide',
    description: 'Appuie, parle, relâche. L\'écriture suit ton rythme sans changer d\'app.',
    size: 'large' as const,
  },
  {
    icon: <Sparkles className="w-6 h-6" />,
    name: 'Texte propre automatiquement',
    description: 'Orthographe, ponctuation et structure nettoyées par l\'IA.',
    size: 'medium' as const,
  },
  {
    icon: <Zap className="w-6 h-6" />,
    name: 'Ultra rapide',
    description: 'De la voix au texte en quelques secondes grâce au pipeline Mistral.',
    size: 'medium' as const,
  },
  {
    icon: <Globe className="w-6 h-6" />,
    name: 'Partout',
    description: 'Fonctionne dans n\'importe quel champ texte : Slack, Gmail, Notion, Cursor...',
    size: 'medium' as const,
  },
  {
    icon: <Monitor className="w-6 h-6" />,
    name: 'HUD flottant',
    description: 'Indicateur visuel discret : écoute, traitement, terminé.',
    size: 'small' as const,
  },
  {
    icon: <Keyboard className="w-6 h-6" />,
    name: 'Raccourci configurable',
    description: 'F8, F9, Ctrl, Cmd... choisis ta touche et ton mode (hold ou toggle).',
    size: 'small' as const,
  },
  {
    icon: <Languages className="w-6 h-6" />,
    name: 'Multilingue',
    description: 'Français et anglais au lancement, plus de langues à venir.',
    size: 'small' as const,
  },
  {
    icon: <Shield className="w-6 h-6" />,
    name: 'Privé par design',
    description: 'Tes données audio ne sont jamais stockées. Contrôle total.',
    size: 'medium' as const,
  },
  {
    icon: <Settings className="w-6 h-6" />,
    name: 'Daemon macOS natif',
    description: 'Tourne en arrière-plan, se lance au démarrage, zéro friction.',
    size: 'large' as const,
  },
];

const sizeClasses = {
  small: 'md:col-span-1 md:row-span-1',
  medium: 'md:col-span-2 md:row-span-1',
  large: 'md:col-span-3 md:row-span-1',
};

export const FeaturesGrid = () => {
  return (
    <section id="features" className="max-w-7xl mx-auto px-6 py-24">
      {/* Section title */}
      <div className="text-center max-w-2xl mx-auto mb-16">
        <h2 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Tout ce qu'il faut pour{' '}
          <span className="gradient-text">dicter efficacement</span>
        </h2>
        <p className="mt-4 text-lg text-slate-600">
          Un outil conçu pour les professionnels qui écrivent beaucoup et veulent gagner du temps.
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 auto-rows-[minmax(140px,auto)]">
        {features.map((feature) => (
          <div
            key={feature.name}
            className={`group rounded-2xl border border-slate-200 bg-white p-6 hover:shadow-lg hover:border-primary-200 transition-all ${sizeClasses[feature.size]}`}
          >
            <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center text-primary-600 mb-4 group-hover:bg-primary-100 transition-colors">
              {feature.icon}
            </div>
            <h3 className="font-semibold text-slate-900 mb-1">{feature.name}</h3>
            <p className="text-sm text-slate-600">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};
