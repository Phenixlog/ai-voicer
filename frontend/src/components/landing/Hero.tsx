import { Mic, ArrowRight } from 'lucide-react';

export const Hero = () => {
  return (
    <section className="relative overflow-hidden">
      {/* Background gradients */}
      <div aria-hidden="true" className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gradient-to-br from-primary-200/40 via-primary-100/20 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-gradient-to-tl from-accent-green-200/30 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-6 pt-32 pb-20 lg:pt-40 lg:pb-28">
        <div className="text-center max-w-4xl mx-auto">
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 border border-primary-200 mb-8">
            <Mic className="w-4 h-4 text-primary-600" />
            <span className="text-sm font-medium text-primary-700">Voice-to-text pour professionnels</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-slate-900 mb-6">
            Parle une fois.{' '}
            <span className="gradient-text">Ecris partout.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed">
            Theoria capture ta voix avec un raccourci clavier, structure le texte avec l'IA,
            puis l'injecte dans ton outil actif en quelques secondes.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <a
              href="#pricing"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all shadow-lg shadow-primary-600/25 hover:shadow-xl hover:shadow-primary-600/30"
            >
              Démarrer gratuitement
              <ArrowRight className="w-5 h-5" />
            </a>
            <a
              href="#features"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:border-slate-300 hover:shadow-md transition-all"
            >
              Voir les fonctionnalités
            </a>
          </div>

          {/* Social proof */}
          <p className="text-sm text-slate-500">
            Compatible avec Cursor, Notion, Gmail, Slack, et plus encore.
          </p>
        </div>

        {/* Demo visual */}
        <div className="mt-16 max-w-3xl mx-auto">
          <div className="relative rounded-2xl bg-slate-900 p-8 shadow-2xl border border-slate-800">
            {/* Window controls */}
            <div className="flex items-center gap-2 mb-6">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="ml-4 text-sm text-slate-500 font-mono">theoria</span>
            </div>

            {/* Simulated flow */}
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <kbd className="px-2 py-1 text-xs font-mono bg-slate-800 text-slate-300 rounded border border-slate-700">F8</kbd>
                </div>
                <span className="text-slate-500 text-sm">Appuie et parle...</span>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div
                      key={i}
                      className="w-1 bg-accent-green-400 rounded-full animate-wave wave-bar"
                      style={{ height: `${12 + Math.random() * 20}px` }}
                    />
                  ))}
                </div>
                <span className="text-accent-green-400 text-sm font-medium">Ecoute en cours...</span>
              </div>

              <div className="border-t border-slate-800 pt-4">
                <p className="text-slate-400 text-sm line-through mb-2">
                  "euh bonjour je voulais savoir si on pouvait se voir demain pour parler du projet"
                </p>
                <p className="text-white text-sm">
                  "Bonjour, je voulais savoir si nous pouvions nous voir demain pour discuter du projet."
                </p>
              </div>

              <div className="flex items-center gap-2 text-accent-green-400">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm">Texte collé dans Slack</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
