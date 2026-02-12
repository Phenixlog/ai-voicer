import { 
  Mic, 
  FileText, 
  Zap, 
  Crown, 
  TrendingUp, 
  CheckCircle,
  MessageSquare,
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { ProgressRing } from '../components/ui/ProgressRing';
import { useUsage } from '../hooks/useUsage';
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';

// Stat Card Component
interface StatCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  iconBg: string;
  trend?: string;
  trendUp?: boolean;
}

const StatCard = ({ title, value, subtitle, icon, iconBg, trend, trendUp }: StatCardProps) => (
  <Card>
    <div className="flex items-start justify-between">
      <div>
        <p className="text-sm text-slate-500 mb-1">{title}</p>
        <p className="text-2xl font-bold text-slate-900">{value}</p>
        <div className="flex items-center gap-2 mt-2">
          {trend && (
            <span className={`text-sm font-medium flex items-center gap-1 ${trendUp ? 'text-emerald-600' : 'text-slate-600'}`}>
              {trendUp && <TrendingUp className="w-4 h-4" />}
              {trend}
            </span>
          )}
          <span className="text-sm text-slate-400">{subtitle}</span>
        </div>
      </div>
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${iconBg}`}>
        {icon}
      </div>
    </div>
  </Card>
);

// Activity Item Component
interface ActivityItemProps {
  title: string;
  context: string;
  duration: string;
  time: string;
  icon: React.ReactNode;
}

const ActivityItem = ({ title, context, duration, time, icon }: ActivityItemProps) => (
  <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
    <div className="flex items-center gap-4">
      <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
        {icon}
      </div>
      <div>
        <p className="font-medium text-slate-900">{title}</p>
        <p className="text-sm text-slate-500">{duration} • {context}</p>
      </div>
    </div>
    <span className="text-sm text-slate-400">{time}</span>
  </div>
);

// Usage Chart Component
const UsageChart = () => {
  const data = [40, 60, 45, 80, 55, 70, 90, 100, 30, 20, 35, 25, 40, 50];
  const max = Math.max(...data);

  return (
    <div className="h-64 flex items-end gap-2">
      {data.map((value, index) => (
        <div 
          key={index}
          className={`flex-1 rounded-t transition-all duration-300 hover:opacity-80 ${
            index === data.length - 8 ? 'bg-primary-600' : 'bg-primary-100'
          }`}
          style={{ height: `${(value / max) * 100}%` }}
        />
      ))}
    </div>
  );
};

export const Dashboard = () => {
  const { stats, history, isLoading, refetch } = useUsage();
  const { user } = useAuth();

  // Calculate quota percentage
  const quotaPercent = stats?.usage?.percentage || 0;
  const usedMinutes = stats?.usage?.used_minutes || 0;
  const remainingMinutes = stats?.usage?.remaining_minutes || 0;
  const totalMinutes = stats?.plan?.monthly_minutes || 300;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Tableau de bord</h1>
          <p className="text-slate-600">Bienvenue{user?.name ? `, ${user.name}` : ''} ! Voici votre résumé d'activité.</p>
        </div>
        <Button variant="secondary" onClick={() => refetch()}>
          Actualiser
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Usage ce mois"
          value={`${Math.floor(usedMinutes / 60)}h ${usedMinutes % 60}m`}
          subtitle="vs mois dernier"
          icon={<Mic className="w-6 h-6 text-blue-600" />}
          iconBg="bg-blue-100"
          trend="+12%"
          trendUp={true}
        />
        <StatCard
          title="Transcriptions"
          value={isLoading ? '-' : String(stats?.total_transcriptions || 0)}
          subtitle="taux de succès"
          icon={<FileText className="w-6 h-6 text-emerald-600" />}
          iconBg="bg-emerald-100"
          trend={`${stats?.success_rate_percent || 99}%`}
          trendUp={true}
        />
        <StatCard
          title="Temps moyen"
          value={`${(stats?.average_latency_ms || 3200) / 1000}s`}
          subtitle="De la voix au texte"
          icon={<Zap className="w-6 h-6 text-amber-600" />}
          iconBg="bg-amber-100"
        />
        <StatCard
          title="Plan actuel"
          value={user?.plan ? user.plan.charAt(0).toUpperCase() + user.plan.slice(1) : 'Free'}
          subtitle="Renouvellement mensuel"
          icon={<Crown className="w-6 h-6 text-purple-600" />}
          iconBg="bg-purple-100"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Usage Chart */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-semibold text-slate-900">Usage des 30 derniers jours</h2>
              <select className="text-sm border border-slate-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                <option>30 derniers jours</option>
                <option>7 derniers jours</option>
                <option>Cette année</option>
              </select>
            </div>
            <UsageChart />
            <div className="flex justify-between mt-4 text-xs text-slate-400">
              <span>1 fév</span>
              <span>15 fév</span>
              <span>Aujourd'hui</span>
            </div>
          </Card>
        </div>

        {/* Quota Card */}
        <Card>
          <h2 className="font-semibold text-slate-900 mb-6">Quota mensuel</h2>
          
          <div className="flex justify-center mb-6">
            <ProgressRing 
              progress={quotaPercent}
              size={160}
              color="#1a73e8"
              strokeWidth={10}
            >
              <div className="text-center">
                <span className="text-3xl font-bold text-slate-900">{Math.round(quotaPercent)}%</span>
                <p className="text-sm text-slate-500">utilisé</p>
              </div>
            </ProgressRing>
          </div>
          
          <div className="space-y-3 mb-6">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Utilisé</span>
              <span className="font-medium text-slate-900">{Math.floor(usedMinutes / 60)}h {usedMinutes % 60}m</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Restant</span>
              <span className="font-medium text-slate-900">
                {remainingMinutes === 'unlimited' ? 'Illimité' : `${Math.floor((remainingMinutes as number) / 60)}h ${(remainingMinutes as number) % 60}m`}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Total</span>
              <span className="font-medium text-slate-900">
                {totalMinutes === 0 ? 'Illimité' : `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m`}
              </span>
            </div>
          </div>
          
          <Link to="/billing">
            <Button variant="ghost" className="w-full">
              {user?.plan === 'free' ? 'Passer à Pro' : 'Gérer mon abonnement'}
            </Button>
          </Link>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <div className="flex items-center justify-between mb-6">
          <h2 className="font-semibold text-slate-900">Activité récente</h2>
          <Link to="/history" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            Voir tout
          </Link>
        </div>
        
        <div className="space-y-3">
          {history.length > 0 ? (
            history.map((event, index) => (
              <ActivityItem
                key={event.id || index}
                title={event.context || 'Transcription'}
                context={event.context || 'Général'}
                duration={`${Math.ceil(event.audio_seconds / 60)} min`}
                time={new Date(event.created_at).toLocaleDateString('fr-FR', { 
                  day: 'numeric', 
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
                icon={<CheckCircle className="w-5 h-5 text-emerald-600" />}
              />
            ))
          ) : (
            <>
              <ActivityItem
                title="Note de réunion"
                context="Slack"
                duration="12 min"
                time="Il y a 2h"
                icon={<CheckCircle className="w-5 h-5 text-emerald-600" />}
              />
              <ActivityItem
                title="Email client"
                context="Gmail"
                duration="5 min"
                time="Il y a 4h"
                icon={<CheckCircle className="w-5 h-5 text-emerald-600" />}
              />
              <ActivityItem
                title="Idée produit"
                context="Notion"
                duration="3 min"
                time="Hier"
                icon={<CheckCircle className="w-5 h-5 text-emerald-600" />}
              />
            </>
          )}
        </div>
      </Card>

      {/* Quick Settings */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <h2 className="font-semibold text-slate-900 mb-4">Raccourci clavier</h2>
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-2">
              <kbd className="px-2 py-1 bg-white border border-slate-200 rounded text-sm font-mono shadow-sm">⌘</kbd>
              <kbd className="px-2 py-1 bg-white border border-slate-200 rounded text-sm font-mono shadow-sm">⇧</kbd>
              <kbd className="px-2 py-1 bg-white border border-slate-200 rounded text-sm font-mono shadow-sm">T</kbd>
            </div>
            <Link to="/settings/shortcuts">
              <Button variant="ghost" size="sm">Modifier</Button>
            </Link>
          </div>
        </Card>
        
        <Card>
          <h2 className="font-semibold text-slate-900 mb-4">Style par défaut</h2>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="font-medium text-slate-900">Message informel</p>
                <p className="text-sm text-slate-500">Ton naturel, concis</p>
              </div>
            </div>
            <Link to="/settings/voice">
              <Button variant="ghost" size="sm">Changer</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};
