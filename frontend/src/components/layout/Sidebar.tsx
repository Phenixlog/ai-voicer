import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  History, 
  BarChart3, 
  User, 
  Mic, 
  Keyboard, 
  CreditCard, 
  HelpCircle, 
  LogOut,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  collapsed?: boolean;
}

const NavItem = ({ to, icon, label, collapsed = false }: NavItemProps) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => `
        flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
        transition-all duration-200
        ${isActive 
          ? 'bg-blue-50 text-blue-600' 
          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }
        ${collapsed ? 'justify-center' : ''}
      `}
      title={collapsed ? label : undefined}
    >
      {icon}
      {!collapsed && <span>{label}</span>}
    </NavLink>
  );
};

export const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { logout, user } = useAuth();
  const location = useLocation();

  const mainNavItems = [
    { to: '/', icon: <LayoutDashboard className="w-5 h-5" />, label: 'Tableau de bord' },
    { to: '/history', icon: <History className="w-5 h-5" />, label: 'Historique' },
    { to: '/stats', icon: <BarChart3 className="w-5 h-5" />, label: 'Statistiques' },
  ];

  const settingsNavItems = [
    { to: '/settings/account', icon: <User className="w-5 h-5" />, label: 'Compte' },
    { to: '/settings/voice', icon: <Mic className="w-5 h-5" />, label: 'Préférences voix' },
    { to: '/settings/shortcuts', icon: <Keyboard className="w-5 h-5" />, label: 'Raccourcis' },
    { to: '/billing', icon: <CreditCard className="w-5 h-5" />, label: 'Facturation' },
  ];

  const isSettingsActive = location.pathname.startsWith('/settings') || location.pathname === '/billing';

  return (
    <aside 
      className={`
        fixed left-0 top-16 bottom-0 
        bg-white border-r border-slate-200
        transition-all duration-300 z-40
        ${collapsed ? 'w-16' : 'w-64'}
      `}
    >
      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-4 w-6 h-6 bg-white border border-slate-200 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-600 shadow-sm"
      >
        {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
      </button>

      <div className="h-full overflow-y-auto py-4 px-3">
        {/* Main Nav */}
        <nav className="space-y-1 mb-6">
          {mainNavItems.map((item) => (
            <NavItem key={item.to} {...item} collapsed={collapsed} />
          ))}
        </nav>

        {/* Settings Nav */}
        <div className={`pt-4 border-t border-slate-200 ${isSettingsActive ? '' : 'opacity-75'}`}>
          {!collapsed && (
            <div className="px-3 mb-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Paramètres
            </div>
          )}
          <nav className="space-y-1">
            {settingsNavItems.map((item) => (
              <NavItem key={item.to} {...item} collapsed={collapsed} />
            ))}
          </nav>
        </div>

        {/* Help & Logout */}
        <div className="pt-4 border-t border-slate-200 mt-4">
          <nav className="space-y-1">
            <NavLink
              to="/help"
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all"
              title={collapsed ? 'Aide & Support' : undefined}
            >
              <HelpCircle className="w-5 h-5" />
              {!collapsed && <span>Aide & Support</span>}
            </NavLink>
            <button
              onClick={logout}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-all ${collapsed ? 'justify-center' : ''}`}
              title={collapsed ? 'Déconnexion' : undefined}
            >
              <LogOut className="w-5 h-5" />
              {!collapsed && <span>Déconnexion</span>}
            </button>
          </nav>
        </div>

        {/* User mini profile */}
        {!collapsed && user && (
          <div className="mt-auto pt-4 border-t border-slate-200">
            <div className="px-3 py-2">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-medium text-sm">
                  {user.name?.charAt(0).toUpperCase() || user.email.charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 truncate">{user.name || user.email}</p>
                  <p className="text-xs text-slate-500 capitalize">{user.plan}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
