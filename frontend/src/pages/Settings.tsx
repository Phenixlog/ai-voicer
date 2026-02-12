import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  User, 
  Mic, 
  Keyboard, 
  Bell, 
  Shield,
  Save,
  CheckCircle
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Alert } from '../components/ui/Alert';
import { useAuth } from '../hooks/useAuth';

// Settings Navigation
const settingsNav = [
  { id: 'account', label: 'Compte', icon: User, path: '/settings/account' },
  { id: 'voice', label: 'Préférences voix', icon: Mic, path: '/settings/voice' },
  { id: 'shortcuts', label: 'Raccourcis', icon: Keyboard, path: '/settings/shortcuts' },
  { id: 'notifications', label: 'Notifications', icon: Bell, path: '/settings/notifications' },
  { id: 'privacy', label: 'Confidentialité', icon: Shield, path: '/settings/privacy' },
];

// Account Settings
const AccountSettings = () => {
  const { user, isLoading } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Informations du compte</h2>
        <p className="text-slate-600">Gérez vos informations personnelles</p>
      </div>

      {saved && (
        <Alert variant="success" title="Sauvegardé">
          Vos modifications ont été enregistrées avec succès.
        </Alert>
      )}

      <Card>
        <div className="space-y-4">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
              {user?.name?.charAt(0).toUpperCase() || user?.email.charAt(0).toUpperCase()}
            </div>
            <div>
              <Button variant="secondary" size="sm">Changer l'avatar</Button>
              <p className="text-sm text-slate-500 mt-1">JPG, PNG ou GIF. 1MB max.</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <Input
              label="Nom complet"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Votre nom"
            />
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="vous@exemple.com"
            />
          </div>

          <Input
            label="Langue"
            value="Français"
            disabled
            helper="La langue de l'interface. La langue de dictée se configure dans 'Préférences voix'."
          />

          <div className="pt-4 flex justify-end">
            <Button 
              onClick={handleSave}
              isLoading={isLoading}
              leftIcon={<Save className="w-4 h-4" />}
            >
              Sauvegarder
            </Button>
          </div>
        </div>
      </Card>

      <Card className="border-red-200">
        <h3 className="text-lg font-semibold text-red-600 mb-2">Zone dangereuse</h3>
        <p className="text-slate-600 mb-4">Ces actions sont irréversibles.</p>
        <div className="flex gap-3">
          <Button variant="ghost" className="text-red-600 hover:bg-red-50">
            Exporter mes données
          </Button>
          <Button variant="ghost" className="text-red-600 hover:bg-red-50">
            Supprimer mon compte
          </Button>
        </div>
      </Card>
    </div>
  );
};

// Voice Settings
const VoiceSettings = () => {
  const { settings, updateSettings, isLoading } = useAuth();
  const [localSettings, setLocalSettings] = useState({
    language: settings?.language || 'fr',
    style_mode: settings?.style_mode || 'message',
    trigger_mode: settings?.trigger_mode || 'hold',
  });
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    await updateSettings(localSettings);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const languages = [
    { value: 'fr', label: 'Français' },
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Español' },
    { value: 'de', label: 'Deutsch' },
  ];

  const styleModes = [
    { value: 'message', label: 'Message informel' },
    { value: 'email', label: 'Email professionnel' },
    { value: 'note', label: 'Note structurée' },
    { value: 'prompt', label: 'Prompt IA' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Préférences voix</h2>
        <p className="text-slate-600">Personnalisez comment Théoria transcrit votre voix</p>
      </div>

      {saved && (
        <Alert variant="success" title="Sauvegardé">
          Vos préférences ont été mises à jour.
        </Alert>
      )}

      <Card>
        <div className="space-y-6">
          <Select
            label="Langue de dictée"
            options={languages}
            value={localSettings.language}
            onChange={(e) => setLocalSettings({ ...localSettings, language: e.target.value })}
            helper="Langue principale pour la transcription. Théoria détecte automatiquement le français et l'anglais."
          />

          <Select
            label="Style de sortie par défaut"
            options={styleModes}
            value={localSettings.style_mode}
            onChange={(e) => setLocalSettings({ ...localSettings, style_mode: e.target.value })}
            helper="Comment votre texte sera formaté par défaut."
          />

          <div className="pt-4 flex justify-end">
            <Button 
              onClick={handleSave}
              isLoading={isLoading}
              leftIcon={<Save className="w-4 h-4" />}
            >
              Sauvegarder
            </Button>
          </div>
        </div>
      </Card>

      <Card>
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Prévisualisation du style</h3>
        <div className="space-y-4">
          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-sm font-medium text-slate-500 mb-2">Entrée vocale :</p>
            <p className="text-slate-700 italic">"Euh... salut tout le monde, alors euh... je voulais vous dire que... euh... la réunion est décalée à 14h, ok ?"</p>
          </div>
          <div className="flex justify-center">
            <div className="text-slate-400">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </div>
          </div>
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
            <p className="text-sm font-medium text-emerald-600 mb-2">Sortie {styleModes.find(s => s.value === localSettings.style_mode)?.label} :</p>
            {localSettings.style_mode === 'message' && (
              <p className="text-slate-700">Salut tout le monde ! La réunion est décalée à 14h. À plus !</p>
            )}
            {localSettings.style_mode === 'email' && (
              <p className="text-slate-700">Bonjour à tous,<br/><br/>Je vous informe que la réunion est décalée à 14h.<br/><br/>Cordialement,</p>
            )}
            {localSettings.style_mode === 'note' && (
              <p className="text-slate-700">• Réunion décalée à 14h</p>
            )}
            {localSettings.style_mode === 'prompt' && (
              <p className="text-slate-700">Réunion décalée à 14h. Contexte : informer l'équipe du changement d'horaire.</p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

// Shortcuts Settings
const ShortcutsSettings = () => {
  const { settings, updateSettings, isLoading } = useAuth();
  const [hotkey, setHotkey] = useState(settings?.hotkey || 'f8');
  const [triggerMode, setTriggerMode] = useState(settings?.trigger_mode || 'hold');
  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    await updateSettings({ hotkey, trigger_mode: triggerMode as 'hold' | 'toggle' });
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Raccourcis clavier</h2>
        <p className="text-slate-600">Configurez comment vous activez Théoria</p>
      </div>

      {saved && (
        <Alert variant="success" title="Sauvegardé">
          Vos raccourcis ont été mis à jour.
        </Alert>
      )}

      <Card>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Mode de déclenchement
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setTriggerMode('hold')}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  triggerMode === 'hold'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="font-medium text-slate-900 mb-1">Maintenir</div>
                <div className="text-sm text-slate-500">Maintenez la touche pendant la dictée</div>
              </button>
              <button
                onClick={() => setTriggerMode('toggle')}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  triggerMode === 'toggle'
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div className="font-medium text-slate-900 mb-1">Toggle</div>
                <div className="text-sm text-slate-500">Appuyez une fois pour démarrer/arrêter</div>
              </button>
            </div>
          </div>

          <Input
            label="Raccourci clavier"
            value={hotkey}
            onChange={(e) => setHotkey(e.target.value.toLowerCase())}
            placeholder="f8"
            helper="Touche ou combinaison pour activer Théoria (ex: cmd+shift+t)"
          />

          <div className="p-4 bg-slate-50 rounded-lg">
            <p className="text-sm font-medium text-slate-700 mb-2">Testez votre configuration :</p>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <kbd className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-lg font-mono shadow-sm">
                  {hotkey.toUpperCase()}
                </kbd>
              </div>
              <span className="text-slate-500">→</span>
              <div className="flex items-center gap-2 text-slate-600">
                <CheckCircle className="w-5 h-5 text-emerald-500" />
                <span>Écoute...</span>
              </div>
            </div>
          </div>

          <div className="pt-4 flex justify-end">
            <Button 
              onClick={handleSave}
              isLoading={isLoading}
              leftIcon={<Save className="w-4 h-4" />}
            >
              Sauvegarder
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Notification Settings
const NotificationsSettings = () => {
  const [settings, setSettings] = useState({
    email_usage: true,
    email_newsletter: false,
    push_quota: true,
    push_updates: true,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Notifications</h2>
        <p className="text-slate-600">Gérez vos préférences de notification</p>
      </div>

      <Card>
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-slate-900 mb-4">Email</h3>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.email_usage}
                  onChange={(e) => setSettings({ ...settings, email_usage: e.target.checked })}
                  className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-slate-700">Rapport d'usage hebdomadaire</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.email_newsletter}
                  onChange={(e) => setSettings({ ...settings, email_newsletter: e.target.checked })}
                  className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-slate-700">Newsletter et nouveautés</span>
              </label>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100">
            <h3 className="font-medium text-slate-900 mb-4">Notifications push</h3>
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.push_quota}
                  onChange={(e) => setSettings({ ...settings, push_quota: e.target.checked })}
                  className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-slate-700">Alerte quota (80% utilisé)</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.push_updates}
                  onChange={(e) => setSettings({ ...settings, push_updates: e.target.checked })}
                  className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-slate-700">Mises à jour de l'application</span>
              </label>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Privacy Settings
const PrivacySettings = () => {
  const [settings, setSettings] = useState({
    store_audio: false,
    analytics: true,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Confidentialité</h2>
        <p className="text-slate-600">Contrôlez vos données et votre vie privée</p>
      </div>

      <Card>
        <div className="space-y-6">
          <div>
            <h3 className="font-medium text-slate-900 mb-2">Stockage des données</h3>
            <label className="flex items-start gap-3 cursor-pointer mt-4">
              <input
                type="checkbox"
                checked={settings.store_audio}
                onChange={(e) => setSettings({ ...settings, store_audio: e.target.checked })}
                className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500 mt-0.5"
              />
              <div>
                <span className="text-slate-700 font-medium">Conserver l'historique des transcriptions</span>
                <p className="text-sm text-slate-500 mt-1">
                  Théoria conserve vos transcriptions pendant 30 jours pour vous permettre de les consulter dans l'historique.
                </p>
              </div>
            </label>
          </div>

          <div className="pt-4 border-t border-slate-100">
            <h3 className="font-medium text-slate-900 mb-2">Anonymisation</h3>
            <label className="flex items-start gap-3 cursor-pointer mt-4">
              <input
                type="checkbox"
                checked={settings.analytics}
                onChange={(e) => setSettings({ ...settings, analytics: e.target.checked })}
                className="w-5 h-5 rounded border-slate-300 text-primary-600 focus:ring-primary-500 mt-0.5"
              />
              <div>
                <span className="text-slate-700 font-medium">Participer à l'amélioration de Théoria</span>
                <p className="text-sm text-slate-500 mt-1">
                  Envoyez des statistiques d'utilisation anonymisées pour nous aider à améliorer le service.
                </p>
              </div>
            </label>
          </div>
        </div>
      </Card>

      <Alert variant="info" title="Vos données vous appartiennent">
        Théoria ne vend jamais vos données. Vos enregistrements audio sont supprimés immédiatement après la transcription sauf si vous activez l'historique.
      </Alert>
    </div>
  );
};

// Main Settings Component
export const Settings = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get current section from URL
  const currentSection = location.pathname.split('/').pop() || 'account';

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Paramètres</h1>
        <p className="text-slate-600">Personnalisez votre expérience Théoria</p>
      </div>

      <div className="grid lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {settingsNav.map((item) => {
              const Icon = item.icon;
              const isActive = currentSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {currentSection === 'account' && <AccountSettings />}
          {currentSection === 'voice' && <VoiceSettings />}
          {currentSection === 'shortcuts' && <ShortcutsSettings />}
          {currentSection === 'notifications' && <NotificationsSettings />}
          {currentSection === 'privacy' && <PrivacySettings />}
        </div>
      </div>
    </div>
  );
};
