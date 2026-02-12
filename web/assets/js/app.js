import { apiFetch, toBearerHeaders } from "/assets/js/api.js";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "/assets/js/auth.js";

const state = {
  me: null,
  usage: null,
  plans: [],
};

const ui = {
  authCard: document.querySelector("#authCard"),
  emailInput: document.querySelector("#emailInput"),
  authError: document.querySelector("#authError"),
  loginBtn: document.querySelector("#loginBtn"),
  logoutBtn: document.querySelector("#logoutBtn"),
  sessionState: document.querySelector("#sessionState"),
  welcomeText: document.querySelector("#welcomeText"),
  syncStatus: document.querySelector("#syncStatus"),
  openBillingTabBtn: document.querySelector("#openBillingTabBtn"),
  refreshOverviewBtn: document.querySelector("#refreshOverviewBtn"),
  refreshUsageBtn: document.querySelector("#refreshUsageBtn"),
  saveSettingsBtn: document.querySelector("#saveSettingsBtn"),
  settingsState: document.querySelector("#settingsState"),
  billingState: document.querySelector("#billingState"),
  openPortalBtn: document.querySelector("#openPortalBtn"),
  usageDetails: document.querySelector("#usageDetails"),
  plansGrid: document.querySelector("#plansGrid"),
  kpiPlan: document.querySelector("#kpiPlan"),
  kpiUsed: document.querySelector("#kpiUsed"),
  kpiRemaining: document.querySelector("#kpiRemaining"),
  kpiSuccess: document.querySelector("#kpiSuccess"),
  quickPlan: document.querySelector("#quickPlan"),
  minutesTrend: document.querySelector("#minutesTrend"),
  qualityHint: document.querySelector("#qualityHint"),
  usageMeterLabel: document.querySelector("#usageMeterLabel"),
  usageMeterText: document.querySelector("#usageMeterText"),
  usageMeterFill: document.querySelector("#usageMeterFill"),
  setHotkey: document.querySelector("#setHotkey"),
  setTriggerMode: document.querySelector("#setTriggerMode"),
  setLanguage: document.querySelector("#setLanguage"),
  setOutputStyle: document.querySelector("#setOutputStyle"),
  menuItems: Array.from(document.querySelectorAll(".menu-item")),
  tabPanels: Array.from(document.querySelectorAll(".tab-panel")),
};

function authHeaders(extra = {}) {
  return toBearerHeaders(getAccessToken(), extra);
}

function setError(message) {
  ui.authError.textContent = message || "";
}

function setSyncStatus(text, isError = false) {
  if (!ui.syncStatus) return;
  ui.syncStatus.textContent = text;
  ui.syncStatus.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function setSubtleText(element, text, isError = false) {
  element.textContent = text;
  element.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function setActiveTab(tabName) {
  ui.menuItems.forEach((item) => {
    item.classList.toggle("active", item.dataset.tab === tabName);
  });
  ui.tabPanels.forEach((panel) => {
    panel.classList.toggle("hidden", panel.id !== `tab-${tabName}`);
  });
}

function renderUsage() {
  const usage = state.usage?.usage || {};
  const plan = state.usage?.plan || {};
  const successRate = state.usage?.success_rate_percent ?? 0;
  const usedMinutes = usage.used_minutes ?? 0;
  const quotaMinutes = plan.monthly_minutes ?? 0;
  const remainingMinutes =
    usage.remaining_minutes === null || usage.remaining_minutes === undefined
      ? "illimite"
      : String(usage.remaining_minutes);
  const usagePercent =
    quotaMinutes > 0 ? Math.max(0, Math.min(100, Math.round((usedMinutes / quotaMinutes) * 100))) : 12;

  ui.kpiPlan.textContent = plan.name || state.me?.plan || "-";
  ui.kpiUsed.textContent = String(usedMinutes);
  ui.kpiRemaining.textContent = remainingMinutes;
  ui.kpiSuccess.textContent = `${successRate}%`;
  ui.quickPlan.textContent = quotaMinutes > 0 ? `${quotaMinutes} min / mois` : "Quota illimite";
  ui.minutesTrend.textContent = `${usedMinutes} min utilisees ce cycle`;
  ui.qualityHint.textContent =
    successRate >= 95 ? "Qualite excellente" : successRate >= 85 ? "Qualite correcte" : "A ameliorer";
  ui.usageMeterLabel.textContent =
    quotaMinutes > 0 ? `${usagePercent}% du quota` : "Plan illimite";
  ui.usageMeterText.textContent = `${usedMinutes} min utilises`;
  ui.usageMeterFill.style.width = `${usagePercent}%`;

  const rows = [
    ["Plan", plan.name || "-"],
    ["Minutes utilisees", usedMinutes],
    ["Minutes restantes", remainingMinutes],
    ["Quota mensuel", quotaMinutes || "illimite"],
    ["Success rate", `${successRate}%`],
  ];

  ui.usageDetails.innerHTML = rows
    .map(
      ([label, value]) =>
        `<div class="detail-item"><span>${label}</span><strong>${value}</strong></div>`
    )
    .join("");
}

function renderPlans() {
  if (!state.plans.length) {
    ui.plansGrid.innerHTML = `<p class="subtle">Aucun plan disponible.</p>`;
    return;
  }

  ui.plansGrid.innerHTML = state.plans
    .map(
      (plan) => `
      <article class="plan-card">
        <h3>${plan.name}</h3>
        <p>${plan.description || "Plan Theoria"}</p>
        <p><strong>${(plan.price_cents || 0) / 100} ${String(plan.currency || "EUR").toUpperCase()}/mois</strong></p>
        <p>Quota: ${plan.monthly_minutes || "illimite"} min</p>
        <button class="btn btn-primary" data-checkout="${plan.code}">
          Choisir ${plan.name}
        </button>
      </article>
    `
    )
    .join("");

  Array.from(document.querySelectorAll("[data-checkout]")).forEach((button) => {
    button.addEventListener("click", async () => {
      const planCode = button.dataset.checkout;
      if (!planCode) return;
      try {
        setSubtleText(ui.billingState, "Ouverture du checkout...");
        const result = await apiFetch(
          `/v1/billing/checkout-session?plan_code=${encodeURIComponent(planCode)}`,
          {
            method: "POST",
            headers: authHeaders(),
          }
        );
        if (result?.url) {
          window.location.href = result.url;
        } else {
          setSubtleText(ui.billingState, "Checkout indisponible pour ce plan.", true);
        }
      } catch (error) {
        setSubtleText(ui.billingState, error.message, true);
      }
    });
  });
}

function renderSession() {
  if (!state.me) {
    ui.sessionState.textContent = "Session: non connecte";
    ui.welcomeText.textContent = "Connecte-toi pour acceder a ton espace Theoria.";
    ui.authCard.classList.remove("hidden");
    ui.logoutBtn.disabled = true;
    setSyncStatus("Etat: session requise");
    return;
  }

  ui.sessionState.textContent = `Session: ${state.me.email}`;
  ui.welcomeText.textContent = `Bienvenue ${state.me.name || state.me.email} - plan ${state.me.plan || "-"}`;
  ui.authCard.classList.add("hidden");
  ui.logoutBtn.disabled = false;
  setSyncStatus("Etat: synchronise");
}

async function loadMe() {
  state.me = await apiFetch("/v1/me", { headers: authHeaders() });
}

async function loadUsage() {
  state.usage = await apiFetch("/v1/usage/current-period", { headers: authHeaders() });
}

async function loadSettings() {
  const settings = await apiFetch("/v1/me/settings", { headers: authHeaders() });
  ui.setHotkey.value = settings.hotkey || "f8";
  ui.setTriggerMode.value = settings.trigger_mode || "hold";
  ui.setLanguage.value = settings.language || "fr";
  ui.setOutputStyle.value = settings.style_mode || "default";
}

async function loadPlans() {
  const payload = await apiFetch("/v1/plans");
  state.plans = payload?.plans || [];
}

async function bootstrapAuthenticatedView() {
  try {
    setSyncStatus("Etat: synchronisation...");
    await Promise.all([loadMe(), loadUsage(), loadSettings(), loadPlans()]);
    renderSession();
    renderUsage();
    renderPlans();
    setError("");
    setSyncStatus("Etat: synchronise");
  } catch (error) {
    clearTokens();
    state.me = null;
    state.usage = null;
    renderSession();
    setError(`Session invalide: ${error.message}`);
    setSyncStatus("Etat: erreur session", true);
  }
}

async function onLogin() {
  const email = ui.emailInput.value.trim();
  if (!email) {
    setError("Email requis.");
    return;
  }

  try {
    setError("");
    setSyncStatus("Etat: connexion...");
    const session = await apiFetch("/v1/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email }),
    });
    setTokens(session.access_token, session.refresh_token);
    await bootstrapAuthenticatedView();
  } catch (error) {
    setError(error.message);
    setSyncStatus("Etat: erreur connexion", true);
  }
}

async function onLogout() {
  const refreshToken = getRefreshToken();
  try {
    await apiFetch("/v1/auth/logout", {
      method: "POST",
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  } catch (_error) {
    // Local logout remains valid even if API logout fails.
  } finally {
    clearTokens();
    state.me = null;
    state.usage = null;
    renderSession();
    setError("");
    ui.usageDetails.innerHTML = "";
    ui.plansGrid.innerHTML = "";
    ui.kpiPlan.textContent = "-";
    ui.kpiUsed.textContent = "0";
    ui.kpiRemaining.textContent = "0";
    ui.kpiSuccess.textContent = "0%";
    ui.usageMeterFill.style.width = "0%";
    ui.usageMeterLabel.textContent = "0%";
    ui.usageMeterText.textContent = "0 min utilises";
    setSyncStatus("Etat: deconnecte");
  }
}

async function onRefreshUsage() {
  if (!getAccessToken()) return;
  try {
    setSyncStatus("Etat: rafraichissement...");
    await loadUsage();
    renderUsage();
    setSyncStatus("Etat: synchronise");
  } catch (error) {
    setSubtleText(ui.settingsState, error.message, true);
    setSyncStatus("Etat: erreur usage", true);
  }
}

async function onSaveSettings() {
  if (!getAccessToken()) return;

  try {
    setSubtleText(ui.settingsState, "Sauvegarde en cours...");
    setSyncStatus("Etat: sauvegarde settings...");
    await apiFetch("/v1/me/settings", {
      method: "PATCH",
      headers: authHeaders({
        "Content-Type": "application/json",
      }),
      body: JSON.stringify({
        hotkey: ui.setHotkey.value.trim(),
        trigger_mode: ui.setTriggerMode.value.trim(),
        language: ui.setLanguage.value.trim(),
        style_mode: ui.setOutputStyle.value.trim(),
      }),
    });
    setSubtleText(ui.settingsState, "Settings sauvegardes.");
    setSyncStatus("Etat: settings synchronises");
  } catch (error) {
    setSubtleText(ui.settingsState, error.message, true);
    setSyncStatus("Etat: erreur settings", true);
  }
}

async function onOpenPortal() {
  if (!getAccessToken()) return;
  try {
    setSubtleText(ui.billingState, "Ouverture du portail...");
    setSyncStatus("Etat: redirection billing...");
    const result = await apiFetch("/v1/billing/portal-session", {
      method: "POST",
      headers: authHeaders(),
    });
    if (result?.url) {
      window.location.href = result.url;
      return;
    }
    setSubtleText(ui.billingState, "Portail indisponible.", true);
    setSyncStatus("Etat: portail indisponible", true);
  } catch (error) {
    setSubtleText(ui.billingState, error.message, true);
    setSyncStatus("Etat: erreur billing", true);
  }
}

function bindEvents() {
  ui.menuItems.forEach((item) => {
    item.addEventListener("click", () => setActiveTab(item.dataset.tab));
  });
  ui.loginBtn.addEventListener("click", onLogin);
  ui.emailInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      void onLogin();
    }
  });
  ui.logoutBtn.addEventListener("click", onLogout);
  ui.refreshOverviewBtn.addEventListener("click", onRefreshUsage);
  ui.refreshUsageBtn.addEventListener("click", onRefreshUsage);
  ui.saveSettingsBtn.addEventListener("click", onSaveSettings);
  ui.openPortalBtn.addEventListener("click", onOpenPortal);
  ui.openBillingTabBtn.addEventListener("click", () => setActiveTab("billing"));
}

async function init() {
  bindEvents();
  setActiveTab("overview");
  setSyncStatus("Etat: pret");

  if (!getAccessToken()) {
    renderSession();
    await loadPlans().then(renderPlans).catch(() => {
      ui.plansGrid.innerHTML = `<p class="subtle">Billing indisponible.</p>`;
    });
    return;
  }

  await bootstrapAuthenticatedView();
}

void init();
