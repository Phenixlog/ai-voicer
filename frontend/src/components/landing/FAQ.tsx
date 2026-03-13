import { useState } from 'react';
import { ChevronDown } from 'lucide-react';

const faqs = [
  {
    question: 'Le texte est-il automatiquement collé ?',
    answer: 'Oui, après traitement par l\'IA, Theoria colle le texte directement dans le champ actif via les APIs d\'accessibilité macOS. Aucune action manuelle requise.',
  },
  {
    question: 'Puis-je changer mon raccourci clavier ?',
    answer: 'Oui, depuis les paramètres de l\'application. Tu peux choisir entre F8, F9, ou d\'autres touches, et basculer entre le mode "hold" (maintenir) et "toggle" (appuyer).',
  },
  {
    question: 'Est-ce que ça fonctionne dans toutes les apps ?',
    answer: 'Theoria fonctionne dans n\'importe quel champ de texte sur macOS : Slack, Notion, Gmail, Cursor, VS Code, Pages, et plus. Si tu peux y taper du texte, Theoria peut y coller.',
  },
  {
    question: 'Mes données audio sont-elles stockées ?',
    answer: 'Non. L\'audio est envoyé pour transcription puis immédiatement supprimé. Aucun fichier audio n\'est conservé sur nos serveurs. Tu gardes le contrôle total.',
  },
  {
    question: 'Que se passe-t-il si je dépasse mon quota ?',
    answer: 'Tu reçois une alerte à 80% de ton quota. Une fois atteint, tu peux attendre le renouvellement mensuel ou passer au plan supérieur instantanément.',
  },
  {
    question: 'Quelles langues sont supportées ?',
    answer: 'Français et anglais au lancement. D\'autres langues seront ajoutées dans les prochaines mises à jour.',
  },
];

export const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section id="faq" className="max-w-3xl mx-auto px-6 py-24">
      <div className="text-center mb-16">
        <h2 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Questions fréquentes
        </h2>
      </div>

      <div className="space-y-3">
        {faqs.map((faq, index) => (
          <div
            key={index}
            className="rounded-xl border border-slate-200 bg-white overflow-hidden transition-all hover:border-slate-300"
          >
            <button
              onClick={() => setOpenIndex(openIndex === index ? null : index)}
              className="w-full flex items-center justify-between px-6 py-4 text-left"
            >
              <span className="font-medium text-slate-900">{faq.question}</span>
              <ChevronDown
                className={`w-5 h-5 text-slate-400 transition-transform flex-shrink-0 ${
                  openIndex === index ? 'rotate-180' : ''
                }`}
              />
            </button>
            {openIndex === index && (
              <div className="px-6 pb-4">
                <p className="text-slate-600 text-sm leading-relaxed">{faq.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};
