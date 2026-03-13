export const Footer = () => {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row items-start justify-between gap-8">
          {/* Brand */}
          <div>
            <span className="text-xl font-bold text-slate-900 tracking-tight">THEORIA</span>
            <p className="mt-2 text-sm text-slate-500 max-w-xs">
              Parlez naturellement, Theoria écrit proprement pour vous, partout.
            </p>
          </div>

          {/* Links */}
          <div className="flex gap-16">
            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-3">Produit</h4>
              <ul className="space-y-2">
                <li><a href="#features" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">Fonctionnalités</a></li>
                <li><a href="#pricing" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">Pricing</a></li>
                <li><a href="#faq" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-3">Légal</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">Confidentialité</a></li>
                <li><a href="#" className="text-sm text-slate-500 hover:text-slate-900 transition-colors">CGU</a></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-400">
            &copy; {new Date().getFullYear()} Theoria. Tous droits réservés.
          </p>
        </div>
      </div>
    </footer>
  );
};
