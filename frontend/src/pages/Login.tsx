import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, ArrowRight, Sparkles, Mail } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/Button';

import { Alert } from '../components/ui/Alert';

export const Login = () => {
  const [email, setEmail] = useState('');
  const navigate = useNavigate();
  const { login, isLoading, error, clearError, isAuthenticated } = useAuth();

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/', { replace: true });
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!email.trim()) return;
    
    try {
      await login(email.trim());
      navigate('/', { replace: true });
    } catch {
      // Error is handled by the store
    }
  };

  return (
    <div className="min-h-screen gradient-bg flex items-center justify-center p-4">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-600 to-emerald-500 mb-4 shadow-lg shadow-blue-600/25">
            <Mic className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Théoria</h1>
          <p className="text-slate-300">Votre pensée, directement en texte clair</p>
        </div>

        {/* Card */}
        <div className="glass-dark rounded-2xl p-8 border border-white/10 shadow-2xl">
          <div className="text-center mb-6">
            <h2 className="text-xl font-semibold text-white mb-1">Bienvenue</h2>
            <p className="text-slate-400 text-sm">Connectez-vous pour accéder à votre compte</p>
          </div>

          {error && (
            <div className="mb-4">
              <Alert variant="error">{error}</Alert>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                Adresse email
              </label>
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
                  <Mail className="w-5 h-5" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="vous@exemple.com"
                  className="w-full pl-10 pr-4 py-3 bg-slate-800/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                  required
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              className="w-full"
              rightIcon={<ArrowRight className="w-5 h-5" />}
            >
              Se connecter
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-400">
              Pas encore de compte ?{' '}
              <button className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
                Créer un compte
              </button>
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-4 mt-8">
          <div className="text-center">
            <div className="w-10 h-10 mx-auto rounded-lg bg-white/5 border border-white/10 flex items-center justify-center mb-2">
              <Sparkles className="w-5 h-5 text-emerald-400" />
            </div>
            <p className="text-xs text-slate-400">Transcription IA</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 mx-auto rounded-lg bg-white/5 border border-white/10 flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <p className="text-xs text-slate-400">Ultra rapide</p>
          </div>
          <div className="text-center">
            <div className="w-10 h-10 mx-auto rounded-lg bg-white/5 border border-white/10 flex items-center justify-center mb-2">
              <svg className="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <p className="text-xs text-slate-400">Privé & sécurisé</p>
          </div>
        </div>
      </div>
    </div>
  );
};
