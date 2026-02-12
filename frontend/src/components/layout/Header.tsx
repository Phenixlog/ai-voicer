import { Bell, Menu, Search } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface HeaderProps {
  onMenuClick?: () => void;
}

export const Header = ({ onMenuClick }: HeaderProps) => {
  const { user } = useAuth();
  const [notificationsOpen, setNotificationsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200 h-16">
      <div className="flex items-center justify-between h-full px-4 lg:px-6">
        {/* Left - Logo & Menu */}
        <div className="flex items-center gap-4">
          <button 
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <Menu className="w-5 h-5 text-slate-600" />
          </button>
          
          <a href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-emerald-500 flex items-center justify-center transition-transform group-hover:scale-105">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <span className="font-bold text-lg text-slate-900 hidden sm:block">Théoria</span>
          </a>
        </div>

        {/* Center - Search (hidden on mobile) */}
        <div className="hidden md:flex flex-1 max-w-md mx-8">
          <div className="relative w-full">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              placeholder="Rechercher..."
              className="w-full pl-10 pr-4 py-2 bg-slate-100 border-0 rounded-lg text-sm text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            />
          </div>
        </div>

        {/* Right - Notifications & User */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <div className="relative">
            <button 
              onClick={() => setNotificationsOpen(!notificationsOpen)}
              className="p-2 rounded-lg hover:bg-slate-100 text-slate-600 relative transition-colors"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Notifications dropdown */}
            {notificationsOpen && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setNotificationsOpen(false)}
                />
                <div className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl border border-slate-200 shadow-lg z-50 py-2">
                  <div className="px-4 py-2 border-b border-slate-100">
                    <h3 className="font-semibold text-slate-900">Notifications</h3>
                  </div>
                  <div className="px-4 py-3 text-sm text-slate-500">
                    Vous avez utilisé 70% de votre quota ce mois-ci.
                  </div>
                  <div className="px-4 py-2 border-t border-slate-100">
                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                      Voir tout
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

          {/* User avatar */}
          {user && (
            <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-medium text-slate-900">{user.name || user.email}</div>
                <div className="text-xs text-slate-500 capitalize">Plan {user.plan}</div>
              </div>
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium text-sm cursor-pointer hover:ring-2 hover:ring-primary-500/30 transition-all">
                {user.name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
