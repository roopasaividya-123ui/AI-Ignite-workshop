/**
 * TruthGuard AI — Single Page Application Client Controller
 */

// ── State Management ──────────────────────────────────────────────────────────
const state = {
  currentUser: null,
  token: localStorage.getItem("truthguard_token") || null,
  currentReport: null,
  activeTab: "text",
  historySavedOnly: false,
  allSources: [],
  currentModule: null,
  explanationMode: "standard",
};

// ── Application Initialization ───────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  checkAuth();
  loadLandingStats();
  
  // Handle share token in URL hash if present (e.g. #/report/share-token)
  handleHashRouting();
  window.addEventListener("hashchange", handleHashRouting);
});

function handleHashRouting() {
  const hash = window.location.hash;
  if (hash.startsWith("#/report/")) {
    const reportIdOrToken = hash.replace("#/report/", "");
    loadReportByIdOrToken(reportIdOrToken);
  } else if (hash.startsWith("#/")) {
    const route = hash.replace("#/", "");
    if (["landing", "analyzer", "dashboard", "sources", "awareness", "history", "admin"].includes(route)) {
      navigateTo(route);
    }
  }
}

// ── Theme Switcher (Dark / Light) ────────────────────────────────────────────
function initTheme() {
  const savedTheme = localStorage.getItem("truthguard_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const target = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", target);
  localStorage.setItem("truthguard_theme", target);
  updateThemeIcon(target);
}

function updateThemeIcon(theme) {
  const icon = document.getElementById("theme-icon");
  if (!icon) return;
  if (theme === "light") {
    icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>`;
  } else {
    icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>`;
  }
}

// ── Navigation Router ────────────────────────────────────────────────────────
function navigateTo(viewName) {
  const views = document.querySelectorAll(".view-panel");
  views.forEach((v) => v.classList.add("hidden"));

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) {
    targetView.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Update active sidebar nav styling
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.remove("text-blue-400", "bg-blue-600/20", "border", "border-blue-500/30", "font-semibold");
    btn.classList.add("text-slate-300");
  });
  const activeBtn = document.getElementById(`nav-${viewName}`);
  if (activeBtn) {
    activeBtn.classList.add("text-blue-400", "bg-blue-600/20", "border", "border-blue-500/30", "font-semibold");
    activeBtn.classList.remove("text-slate-300");
  }

  // View specific data fetchers
  if (viewName === "dashboard") loadDashboardData();
  if (viewName === "sources") loadSourcesData();
  if (viewName === "awareness") loadAwarenessModules();
  if (viewName === "history") loadHistory();
  if (viewName === "admin") loadAdminPanel();
  if (viewName === "landing") loadLandingStats();
}

function scrollToSection(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth" });
}

function toggleMobileMenu() {
  const menu = document.getElementById("mobile-menu");
  if (menu) menu.classList.toggle("hidden");
}

// ── Toast Notification Service ───────────────────────────────────────────────
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `p-3 rounded-xl shadow-xl text-xs font-semibold flex items-center space-x-2 border transition-all duration-300 transform translate-y-2 pointer-events-auto ${
    type === "success"
      ? "bg-slate-900 text-emerald-300 border-emerald-500/40"
      : type === "error"
      ? "bg-slate-900 text-red-300 border-red-500/40"
      : "bg-slate-900 text-blue-300 border-blue-500/40"
  }`;

  const iconSvg =
    type === "success"
      ? `<svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`
      : type === "error"
      ? `<svg class="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`
      : `<svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

  toast.innerHTML = `${iconSvg}<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove("translate-y-2");
    toast.classList.add("translate-y-0");
  }, 10);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ── User Authentication & Profile ────────────────────────────────────────────
async function checkAuth() {
  if (!state.token) {
    updateUserUI(null);
    return;
  }
  try {
    const res = await fetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (res.ok) {
      const user = await res.json();
      state.currentUser = user;
      updateUserUI(user);
    } else {
      logout();
    }
  } catch (e) {
    console.error("Auth check failed:", e);
  }
}

function updateUserUI(user) {
  const displayName = document.getElementById("user-display-name");
  const roleLabel = document.getElementById("user-role-label");
  const avatar = document.getElementById("user-avatar");
  const authBtn = document.getElementById("auth-action-btn");
  const adminNavItem = document.getElementById("admin-nav-item");
  const scoreBadge = document.getElementById("user-awareness-score-badge");

  if (user) {
    if (displayName) displayName.textContent = user.full_name;
    if (roleLabel) roleLabel.textContent = `${user.role.toUpperCase()} Account`;
    if (avatar) avatar.textContent = user.full_name.charAt(0).toUpperCase();
    if (authBtn) {
      authBtn.textContent = "Sign Out";
      authBtn.onclick = logout;
    }
    if (scoreBadge) scoreBadge.textContent = user.awareness_score || 0;
    if (adminNavItem) {
      if (user.role === "admin") adminNavItem.classList.remove("hidden");
      else adminNavItem.classList.add("hidden");
    }
  } else {
    if (displayName) displayName.textContent = "Public Guest";
    if (roleLabel) roleLabel.textContent = "Anonymous Mode";
    if (avatar) avatar.textContent = "G";
    if (authBtn) {
      authBtn.textContent = "Sign In";
      authBtn.onclick = openAuthModal;
    }
    if (scoreBadge) scoreBadge.textContent = "0";
    if (adminNavItem) adminNavItem.classList.add("hidden");
  }
}

function logout() {
  state.token = null;
  state.currentUser = null;
  localStorage.removeItem("truthguard_token");
  updateUserUI(null);
  showToast("Signed out successfully.", "info");
  navigateTo("landing");
}

let isRegisterMode = false;

function openAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeAuthModal() {
  const modal = document.getElementById("auth-modal");
  if (modal) modal.classList.add("hidden");
}

function toggleAuthMode() {
  isRegisterMode = !isRegisterMode;
  const title = document.getElementById("auth-modal-title");
  const nameBox = document.getElementById("auth-name-container");
  const adminBox = document.getElementById("auth-admin-secret-container");
  const submitBtn = document.getElementById("auth-submit-btn");
  const toggleBtn = document.getElementById("auth-toggle-mode-btn");

  if (isRegisterMode) {
    title.textContent = "Create TruthGuard Account";
    nameBox.classList.remove("hidden");
    adminBox.classList.remove("hidden");
    submitBtn.textContent = "Create Account";
    toggleBtn.textContent = "Already have an account? Sign In";
  } else {
    title.textContent = "Sign In to TruthGuard AI";
    nameBox.classList.add("hidden");
    adminBox.classList.add("hidden");
    submitBtn.textContent = "Sign In";
    toggleBtn.textContent = "Need an account? Register here";
  }
}

async function handleAuthSubmit(event) {
  event.preventDefault();
  const email = document.getElementById("auth-email").value;
  const password = document.getElementById("auth-password").value;
  const name = document.getElementById("auth-name").value;
  const adminSecret = document.getElementById("auth-admin-secret").value;

  try {
    let endpoint = isRegisterMode ? "/api/auth/register" : "/api/auth/login";
    let body = isRegisterMode
      ? {
          email,
          password,
          full_name: name,
          role: adminSecret ? "admin" : "user",
          admin_secret: adminSecret || null,
        }
      : { email, password };

    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Authentication error", "error");
      return;
    }

    state.token = data.access_token;
    state.currentUser = data.user;
    localStorage.setItem("truthguard_token", data.access_token);
    updateUserUI(data.user);
    closeAuthModal();
    showToast(`Welcome, ${data.user.full_name}!`, "success");
  } catch (e) {
    showToast("Network or connection error.", "error");
  }
}

async function demoSignIn(role) {
  try {
    const res = await fetch(`/api/auth/demo-login/${role}`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Demo sign-in failed", "error");
      return;
    }
    state.token = data.access_token;
    state.currentUser = data.user;
    localStorage.setItem("truthguard_token", data.access_token);
    updateUserUI(data.user);
    closeAuthModal();
    showToast(`Signed in as ${role.toUpperCase()} (${data.user.full_name})`, "success");
    if (role === "admin") navigateTo("admin");
  } catch (e) {
    showToast("Could not complete demo sign-in.", "error");
  }
}

// ── Landing Page Statistics ──────────────────────────────────────────────────
async function loadLandingStats() {
  try {
    const res = await fetch("/api/dashboard/stats");
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById("landing-stat-total").textContent = data.total_analyses;
    document.getElementById("landing-stat-verified").textContent = data.verified_claims;
    document.getElementById("landing-stat-debunked").textContent = data.contradicted_claims + data.misleading_claims;
    document.getElementById("landing-stat-sources").textContent = data.total_trusted_sources;
  } catch (e) {
    console.error("Landing stats fetch error:", e);
  }
}

// ── AI News Analyzer Controller ──────────────────────────────────────────────
function switchInputTab(tab) {
  state.activeTab = tab;
  ["text", "url", "document"].forEach((t) => {
    const btn = document.getElementById(`tab-btn-${t}`);
    const box = document.getElementById(`input-container-${t}`);
    if (t === tab) {
      btn.className = "tab-btn pb-3 text-sm font-semibold text-blue-400 border-b-2 border-blue-500 flex items-center space-x-2";
      box.classList.remove("hidden");
    } else {
      btn.className = "tab-btn pb-3 text-sm font-medium text-slate-400 hover:text-slate-200 flex items-center space-x-2";
      box.classList.add("hidden");
    }
  });
}

function clearAnalyzerForm() {
  document.getElementById("input-text-title").value = "";
  document.getElementById("input-text-content").value = "";
  document.getElementById("input-url").value = "";
  document.getElementById("input-document-content").value = "";
  const fileMeta = document.getElementById("uploaded-file-meta");
  if (fileMeta) fileMeta.classList.add("hidden");
}

async function loadDemoScenario(scenarioId) {
  try {
    const res = await fetch("/api/analyze/demo-examples");
    const examples = await res.json();
    const match = examples.find((e) => e.id === scenarioId);
    if (!match) return;

    switchInputTab("text");
    document.getElementById("input-text-title").value = match.title;
    document.getElementById("input-text-content").value = match.content;
    showToast(`Loaded preset: ${match.tag}`, "info");
  } catch (e) {
    showToast("Error loading demo scenario", "error");
  }
}

async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/analyze/upload-document", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || "Upload failed", "error");
      return;
    }

    document.getElementById("input-document-content").value = data.content;
    const fileMeta = document.getElementById("uploaded-file-meta");
    fileMeta.textContent = `File: ${data.filename} (${Math.round(data.size_bytes / 1024)} KB extracted)`;
    fileMeta.classList.remove("hidden");
    showToast(`Successfully extracted text from ${data.filename}`, "success");
  } catch (e) {
    showToast("Failed to process document file.", "error");
  }
}

async function executeAnalysis() {
  const tab = state.activeTab;
  let payload = { input_type: tab };

  if (tab === "text") {
    const title = document.getElementById("input-text-title").value;
    const content = document.getElementById("input-text-content").value;
    if (!content.trim()) {
      showToast("Please enter text or a claim to analyze.", "error");
      return;
    }
    payload.title = title;
    payload.content = content;
  } else if (tab === "url") {
    const url = document.getElementById("input-url").value;
    if (!url.trim()) {
      showToast("Please provide a valid news article URL.", "error");
      return;
    }
    payload.url = url;
  } else if (tab === "document") {
    const docText = document.getElementById("input-document-content").value;
    if (!docText.trim()) {
      showToast("Please upload or extract document content first.", "error");
      return;
    }
    payload.document_text = docText;
    payload.title = "Uploaded Document Fact-Check";
  }

  // Show Animated Pipeline Progress
  const pipelineBox = document.getElementById("pipeline-progress-container");
  const runBtn = document.getElementById("run-analyze-btn");
  pipelineBox.classList.remove("hidden");
  runBtn.disabled = true;
  runBtn.classList.add("opacity-50", "cursor-not-allowed");

  // Animate through pipeline steps smoothly
  animatePipelineSteps();

  try {
    const headers = { "Content-Type": "application/json" };
    if (state.token) headers["Authorization"] = `Bearer ${state.token}`;

    const res = await fetch("/api/analyze", {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });

    const report = await res.json();
    if (!res.ok) {
      showToast(report.detail || "Analysis error occurred.", "error");
      pipelineBox.classList.add("hidden");
      runBtn.disabled = false;
      runBtn.classList.remove("opacity-50", "cursor-not-allowed");
      return;
    }

    // Wait 1.2s to let user see pipeline reach 100% completion
    setTimeout(() => {
      pipelineBox.classList.add("hidden");
      runBtn.disabled = false;
      runBtn.classList.remove("opacity-50", "cursor-not-allowed");
      displayCredibilityReport(report);
      navigateTo("report");
    }, 1200);
  } catch (e) {
    pipelineBox.classList.add("hidden");
    runBtn.disabled = false;
    runBtn.classList.remove("opacity-50", "cursor-not-allowed");
    showToast("Network failure executing analysis.", "error");
  }
}

function animatePipelineSteps() {
  const steps = [
    "Step 1: Extracting content & publisher bylines",
    "Step 2: Isolating atomic factual claims",
    "Step 3: Query formulation for fact-check registries",
    "Step 4: Querying PIB, WHO & IFCN registries",
    "Step 5: Ranking supporting vs contradicting evidence",
    "Step 6: Calculating credibility score & abstention check",
    "Step 7: Synthesizing dual-mode explanations",
    "Step 8: Finalizing credibility report",
  ];

  let current = 1;
  const statusLabel = document.getElementById("pipeline-status-text");

  const interval = setInterval(() => {
    if (current > 8) {
      clearInterval(interval);
      return;
    }
    const stepEl = document.getElementById(`step-item-${current}`);
    if (stepEl) {
      stepEl.classList.remove("text-slate-400");
      stepEl.classList.add("text-blue-400", "font-semibold");
      const numSpan = stepEl.querySelector(".step-num");
      if (numSpan) numSpan.classList.add("bg-blue-600", "text-white");
    }
    if (statusLabel) statusLabel.textContent = steps[current - 1];
    current++;
  }, 160);
}

// ── News Credibility Report Rendering ────────────────────────────────────────
function displayCredibilityReport(report) {
  state.currentReport = report;

  document.getElementById("report-header-title").textContent = report.title;
  document.getElementById("report-share-tag").textContent = `ID: #${report.share_token || report.id.substring(0, 8)}`;

  // Score circular gauge
  const score = report.overall_credibility_score;
  const scoreNum = document.getElementById("report-score-number");
  scoreNum.textContent = Math.round(score);

  const circle = document.getElementById("report-gauge-circle");
  // Circumference = 2 * pi * 42 ~= 263.89
  const circumference = 264;
  const offset = circumference - (score / 100) * circumference;
  circle.style.strokeDasharray = `${circumference}`;
  circle.style.strokeDashoffset = `${offset}`;

  // Verdict colors & badge
  const verdictBadge = document.getElementById("report-verdict-badge");
  verdictBadge.textContent = report.verdict;

  let colorClass = "bg-slate-800 text-slate-300 border-slate-700";
  let circleStroke = "#64748b";

  if (report.verdict === "Supported by evidence") {
    colorClass = "bg-emerald-500/20 text-emerald-400 border-emerald-500/40 glow-green";
    circleStroke = "#10b981";
  } else if (report.verdict === "Likely accurate") {
    colorClass = "bg-blue-500/20 text-blue-400 border-blue-500/40 glow-blue";
    circleStroke = "#3b82f6";
  } else if (report.verdict === "Misleading") {
    colorClass = "bg-amber-500/20 text-amber-400 border-amber-500/40";
    circleStroke = "#f59e0b";
  } else if (report.verdict === "Contradicted by evidence") {
    colorClass = "bg-red-500/20 text-red-400 border-red-500/40 glow-red";
    circleStroke = "#ef4444";
  } else {
    colorClass = "bg-slate-800 text-slate-400 border-slate-700";
    circleStroke = "#64748b";
  }

  verdictBadge.className = `px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${colorClass}`;
  circle.style.stroke = circleStroke;

  document.getElementById("report-confidence-label").textContent = `Confidence: ${Math.round(report.confidence_score)}%`;

  // Verdict overview sentence
  const verdictDesc = document.getElementById("report-verdict-description");
  if (report.verdict === "Supported by evidence" || report.verdict === "Likely accurate") {
    verdictDesc.textContent = "This story aligns with verified public announcements and documentation from authoritative institutions.";
  } else if (report.verdict === "Contradicted by evidence") {
    verdictDesc.textContent = "Authoritative investigation confirms this story contains fabricated claims, hoax elements, or fraudulent instructions.";
  } else if (report.verdict === "Misleading") {
    verdictDesc.textContent = "The story contains a mix of factual and misleading context, missing vital caveats or distorting dates/locations.";
  } else {
    verdictDesc.textContent = "Insufficient independent corroborating evidence was found. In accordance with TruthGuard's verification doctrine, we abstain from drawing an ungrounded conclusion.";
  }

  // Metadata pills
  document.getElementById("meta-domain-pill").textContent = `Domain: ${report.extracted_domain || "Direct Input"}`;
  document.getElementById("meta-author-pill").textContent = `Author: ${report.author || "Uncredited"}`;
  document.getElementById("meta-date-pill").textContent = `Checked: ${new Date(report.created_at).toLocaleDateString()}`;

  // Warnings
  const warningsBox = document.getElementById("report-warnings-container");
  if (report.warnings && report.warnings.length > 0) {
    warningsBox.classList.remove("hidden");
    warningsBox.innerHTML = report.warnings
      .map(
        (w) => `
        <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-xs text-amber-300 flex items-start space-x-2">
          <svg class="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          <div><strong>${w.category.toUpperCase().replace("_", " ")}:</strong> ${w.message}</div>
        </div>
      `
      )
      .join("");
  } else {
    warningsBox.classList.add("hidden");
  }

  // Dual-mode Explanations
  formatExplanationMarkdown("explanation-text-standard", report.ai_explanation_standard);
  formatExplanationMarkdown("explanation-text-beginner", report.ai_explanation_beginner);

  // Claim-by-Claim Breakdown
  const claimsContainer = document.getElementById("claims-breakdown-list");
  if (report.claims && report.claims.length > 0) {
    claimsContainer.innerHTML = report.claims
      .map(
        (c) => `
      <div class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-200">Claim #${c.claim_id}</span>
          <span class="px-2 py-0.5 rounded font-mono text-[10px] font-semibold ${
            c.verdict.includes("Supported")
              ? "bg-emerald-500/20 text-emerald-400"
              : c.verdict.includes("Contradicted")
              ? "bg-red-500/20 text-red-400"
              : "bg-slate-800 text-slate-400"
          }">${c.verdict}</span>
        </div>
        <p class="text-slate-300 italic">"${c.claim_text}"</p>
        <p class="text-slate-400">${c.explanation}</p>
        ${
          c.citations && c.citations.length > 0
            ? `<div class="pt-1 flex flex-wrap gap-2">${c.citations
                .map(
                  (cit) =>
                    `<a href="${cit.url}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-blue-400 hover:underline flex items-center space-x-1 font-mono"><span>🔗 ${cit.source}</span></a>`
                )
                .join("")}</div>`
            : ""
        }
      </div>
    `
      )
      .join("");
  } else {
    claimsContainer.innerHTML = `<p class="text-xs text-slate-500">No individual claims decomposed.</p>`;
  }

  // Supporting Evidence Table
  const suppList = document.getElementById("supporting-evidence-list");
  const suppBadge = document.getElementById("supporting-count-badge");
  suppBadge.textContent = `${report.supporting_evidence.length} found`;
  if (report.supporting_evidence.length > 0) {
    suppList.innerHTML = report.supporting_evidence
      .map(
        (e) => `
      <div class="p-3 rounded-xl bg-slate-900/80 border border-emerald-500/20 text-xs space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="font-bold text-emerald-400">${e.source_name}</span>
          <span class="text-[10px] font-mono text-slate-400">Score: ${e.credibility_rating}/100</span>
        </div>
        <p class="text-slate-300 italic">"${e.quote_or_summary}"</p>
        <div class="flex items-center justify-between pt-1">
          <span class="text-[10px] text-slate-400">${e.publish_date || "Verified Record"}</span>
          <a href="${e.source_url}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-blue-400 hover:underline">View Source Link ↗</a>
        </div>
      </div>
    `
      )
      .join("");
  } else {
    suppList.innerHTML = `<p class="text-xs text-slate-500">No supporting evidence identified.</p>`;
  }

  // Contradicting Evidence Table
  const contraList = document.getElementById("contradicting-evidence-list");
  const contraBadge = document.getElementById("contradicting-count-badge");
  contraBadge.textContent = `${report.contradicting_evidence.length} found`;
  if (report.contradicting_evidence.length > 0) {
    contraList.innerHTML = report.contradicting_evidence
      .map(
        (e) => `
      <div class="p-3 rounded-xl bg-slate-900/80 border border-red-500/20 text-xs space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="font-bold text-red-400">${e.source_name}</span>
          <span class="text-[10px] font-mono text-slate-400">Score: ${e.credibility_rating}/100</span>
        </div>
        <p class="text-slate-300 italic">"${e.quote_or_summary}"</p>
        <div class="flex items-center justify-between pt-1">
          <span class="text-[10px] text-slate-400">${e.publish_date || "Fact-Check Debunk"}</span>
          <a href="${e.source_url}" target="_blank" rel="noopener noreferrer" class="text-[10px] text-blue-400 hover:underline">View Source Link ↗</a>
        </div>
      </div>
    `
      )
      .join("");
  } else {
    contraList.innerHTML = `<p class="text-xs text-slate-500">No contradictory records identified.</p>`;
  }

  // Source Credibility Panel
  const srcPanel = document.getElementById("source-credibility-panel");
  const sc = report.source_credibility || {};
  srcPanel.innerHTML = `
    <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
      <span class="text-[10px] font-mono text-slate-400 uppercase">Publisher Tier</span>
      <p class="font-bold text-slate-200 mt-1">${sc.publisher_tier || "Tier 3 - Unverified"}</p>
    </div>
    <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
      <span class="text-[10px] font-mono text-slate-400 uppercase">Domain Trust Rating</span>
      <p class="font-bold text-blue-400 mt-1">${sc.reputation_score || 50}/100</p>
    </div>
    <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
      <span class="text-[10px] font-mono text-slate-400 uppercase">Author Transparency</span>
      <p class="font-bold text-slate-200 mt-1">${sc.author_transparency || "Moderate"}</p>
    </div>
  `;

  // Update Save button state
  updateSaveButtonUI(report.is_saved);
}

function formatExplanationMarkdown(containerId, text) {
  const container = document.getElementById(containerId);
  if (!container) return;
  // Simple markdown renderer for headers, bold, bullets
  let html = text
    .replace(/^### (.*$)/gim, '<h4 class="text-sm font-bold text-white mt-2 mb-1">$1</h4>')
    .replace(/^#### (.*$)/gim, '<h5 class="text-xs font-bold text-blue-300 mt-2 mb-1 uppercase tracking-wider">$1</h5>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white">$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/^- (.*$)/gim, '<li class="ml-4 list-disc text-slate-300">$1</li>')
    .replace(/\n\n/g, '<p class="my-2"></p>');
  container.innerHTML = html;
}

function switchExplanationMode(mode) {
  state.explanationMode = mode;
  const stdBtn = document.getElementById("btn-mode-standard");
  const begBtn = document.getElementById("btn-mode-beginner");
  const stdText = document.getElementById("explanation-text-standard");
  const begText = document.getElementById("explanation-text-beginner");

  if (mode === "beginner") {
    stdBtn.className = "px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-all";
    begBtn.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-600 text-white transition-all";
    stdText.classList.add("hidden");
    begText.classList.remove("hidden");
  } else {
    stdBtn.className = "px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-600 text-white transition-all";
    begBtn.className = "px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition-all";
    stdText.classList.remove("hidden");
    begText.classList.add("hidden");
  }
}

async function toggleSaveCurrentReport() {
  if (!state.currentReport) return;
  if (!state.token) {
    showToast("Please sign in to save and bookmark reports.", "info");
    openAuthModal();
    return;
  }

  try {
    const res = await fetch(`/api/reports/${state.currentReport.id}/save`, {
      method: "POST",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    const data = await res.json();
    state.currentReport.is_saved = data.is_saved;
    updateSaveButtonUI(data.is_saved);
    showToast(data.is_saved ? "Report saved to bookmarks." : "Removed from bookmarks.", "success");
  } catch (e) {
    showToast("Failed to toggle save status.", "error");
  }
}

function updateSaveButtonUI(isSaved) {
  const icon = document.getElementById("save-star-icon");
  const label = document.getElementById("save-btn-label");
  if (!icon || !label) return;

  if (isSaved) {
    icon.className = "w-4 h-4 text-amber-400 fill-amber-400";
    label.textContent = "Saved";
  } else {
    icon.className = "w-4 h-4 text-slate-400";
    label.textContent = "Save Report";
  }
}

function openShareModal() {
  if (!state.currentReport) return;
  const link = `${window.location.origin}/#/report/${state.currentReport.share_token}`;
  document.getElementById("share-link-input").value = link;
  document.getElementById("share-modal").classList.remove("hidden");
}

function closeShareModal() {
  document.getElementById("share-modal").classList.add("hidden");
}

function copyShareLink() {
  const input = document.getElementById("share-link-input");
  input.select();
  navigator.clipboard.writeText(input.value);
  showToast("Public report link copied to clipboard!", "success");
  closeShareModal();
}

async function loadReportByIdOrToken(tokenOrId) {
  try {
    let res = await fetch(`/api/reports/share/${tokenOrId}`);
    if (!res.ok) {
      res = await fetch(`/api/reports/${tokenOrId}`);
    }
    if (!res.ok) {
      showToast("Report not found or private.", "error");
      return;
    }
    const report = await res.json();
    displayCredibilityReport(report);
    navigateTo("report");
  } catch (e) {
    showToast("Failed to load report.", "error");
  }
}

// ── Live Dashboard Data & SVG Charts ─────────────────────────────────────────
async function loadDashboardData() {
  try {
    // 1. Stats Counters
    const resStats = await fetch("/api/dashboard/stats");
    const stats = await resStats.json();
    document.getElementById("dash-total").textContent = stats.total_analyses;
    document.getElementById("dash-verified").textContent = stats.verified_claims;
    document.getElementById("dash-misleading").textContent = stats.misleading_claims;
    document.getElementById("dash-contradicted").textContent = stats.contradicted_claims;

    // 2. Credibility Distribution Donut Chart
    const resDist = await fetch("/api/dashboard/credibility-distribution");
    const distData = await resDist.json();
    renderCredibilityDonut(distData);

    // 3. Weekly Activity Area Chart
    const resWeekly = await fetch("/api/dashboard/weekly-activity");
    const weeklyData = await resWeekly.json();
    renderWeeklyActivityChart(weeklyData);

    // 4. Recent Analyses Table
    const resRecent = await fetch("/api/dashboard/recent-analyses");
    const recentData = await resRecent.json();
    renderRecentAnalysesTable(recentData);
  } catch (e) {
    console.error("Dashboard data load error:", e);
  }
}

function renderCredibilityDonut(data) {
  const wrapper = document.getElementById("svg-donut-wrapper");
  const legend = document.getElementById("distribution-legend");
  if (!wrapper || !legend) return;

  const total = data.reduce((acc, cur) => acc + cur.count, 0) || 1;
  const radius = 35;
  const circumference = 2 * Math.PI * radius; // ~220
  let cumulativePercent = 0;

  const circleSegments = data
    .map((item) => {
      const strokeDash = (item.count / total) * circumference;
      const strokeDashoffset = -cumulativePercent * circumference;
      cumulativePercent += item.count / total;
      return `<circle cx="50" cy="50" r="${radius}" fill="none" stroke="${item.color}" stroke-width="12" stroke-dasharray="${strokeDash} ${circumference}" stroke-dashoffset="${strokeDashoffset}" class="transition-all duration-700"/>`;
    })
    .join("");

  wrapper.innerHTML = `
    <svg viewBox="0 0 100 100" class="w-full h-full transform -rotate-90">
      ${circleSegments}
    </svg>
    <div class="absolute text-center">
      <span class="text-xl font-bold text-white">${total}</span>
      <span class="block text-[9px] font-mono text-slate-400 uppercase">Claims</span>
    </div>
  `;

  legend.innerHTML = data
    .map(
      (item) => `
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${item.color}"></span>
        <span class="text-slate-300">${item.name}</span>
      </div>
      <span class="font-mono text-slate-400 font-semibold">${item.count} (${item.percentage}%)</span>
    </div>
  `
    )
    .join("");
}

function renderWeeklyActivityChart(data) {
  const container = document.getElementById("weekly-chart-container");
  if (!container) return;

  const maxVal = Math.max(...data.map((d) => d.analyses_count), 4);

  container.innerHTML = data
    .map((d) => {
      const heightPct = Math.max(12, (d.analyses_count / maxVal) * 100);
      return `
      <div class="flex-1 flex flex-col items-center h-full justify-end group">
        <span class="text-[10px] font-mono text-blue-400 opacity-0 group-hover:opacity-100 mb-1 transition-opacity">${d.analyses_count}</span>
        <div class="w-full max-w-[28px] bg-gradient-to-t from-blue-600 to-indigo-500 rounded-t-lg transition-all duration-500 hover:from-blue-500 hover:to-indigo-400" style="height: ${heightPct}%;"></div>
        <span class="text-[10px] font-mono text-slate-400 mt-2">${d.day}</span>
      </div>
    `;
    })
    .join("");
}

function renderRecentAnalysesTable(records) {
  const tbody = document.getElementById("recent-analyses-tbody");
  if (!tbody) return;

  if (records.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500">No verification analyses on record yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = records
    .map((r) => {
      let badgeColor = "bg-slate-800 text-slate-400";
      if (r.verdict.includes("Supported")) badgeColor = "bg-emerald-500/20 text-emerald-400";
      if (r.verdict.includes("Misleading")) badgeColor = "bg-amber-500/20 text-amber-400";
      if (r.verdict.includes("Contradicted")) badgeColor = "bg-red-500/20 text-red-400";

      return `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="py-3 font-medium text-slate-200 max-w-xs truncate">${r.title}</td>
        <td class="py-3"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${badgeColor}">${r.verdict}</span></td>
        <td class="py-3 font-mono font-bold text-blue-400">${Math.round(r.overall_credibility_score)}/100</td>
        <td class="py-3 font-mono text-slate-400">${r.extracted_domain || "text"}</td>
        <td class="py-3 text-right">
          <button onclick="loadReportByIdOrToken('${r.id}')" class="text-blue-400 hover:text-blue-300 font-medium">Inspect →</button>
        </td>
      </tr>
    `;
    })
    .join("");
}

// ── Trusted Sources & Live Domain Inspector ──────────────────────────────────
async function loadSourcesData(category = "") {
  try {
    let url = "/api/sources";
    if (category) url += `?category=${category}`;
    const res = await fetch(url);
    state.allSources = await res.json();
    renderSourcesGrid(state.allSources);
  } catch (e) {
    console.error("Sources fetch error:", e);
  }
}

function renderSourcesGrid(sources) {
  const grid = document.getElementById("sources-cards-grid");
  if (!grid) return;

  if (sources.length === 0) {
    grid.innerHTML = `<div class="col-span-full py-8 text-center text-slate-500 text-xs">No matching authoritative sources found.</div>`;
    return;
  }

  grid.innerHTML = sources
    .map(
      (s) => `
    <div class="glass-panel p-5 rounded-xl border border-slate-800 space-y-2.5">
      <div class="flex items-start justify-between">
        <div>
          <h4 class="font-bold text-white text-sm">${s.name}</h4>
          <span class="text-xs font-mono text-blue-400">${s.domain}</span>
        </div>
        <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-500/20 text-blue-300">${s.credibility_rating}/100</span>
      </div>
      <p class="text-xs text-slate-400 leading-relaxed">${s.description}</p>
      <div class="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[10px]">
        <span class="text-slate-400 uppercase font-mono">${s.category.replace("_", " ")} • ${s.country}</span>
        ${s.is_ifcn_certified ? `<span class="text-emerald-400 font-semibold">✓ IFCN Signatory</span>` : `<span class="text-slate-400">Reputed Registry</span>`}
      </div>
    </div>
  `
    )
    .join("");
}

function filterSourcesCategory(cat) {
  document.querySelectorAll(".source-cat-btn").forEach((btn) => {
    btn.className = "source-cat-btn px-3 py-1.5 rounded-lg text-xs font-medium glass-panel text-slate-300 hover:text-white";
  });
  if (event && event.target) {
    event.target.className = "source-cat-btn px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 text-white";
  }
  loadSourcesData(cat);
}

function searchSourcesList(q) {
  const query = q.toLowerCase();
  const filtered = state.allSources.filter(
    (s) => s.name.toLowerCase().includes(query) || s.domain.toLowerCase().includes(query)
  );
  renderSourcesGrid(filtered);
}

async function scanDomainReputation() {
  const input = document.getElementById("domain-scan-input").value;
  if (!input.trim()) return;

  const resultBox = document.getElementById("domain-scan-result");
  resultBox.classList.remove("hidden");
  resultBox.innerHTML = `<p class="text-slate-400">Inspecting authoritative registry for '${input}'...</p>`;

  try {
    const res = await fetch(`/api/sources/verify-domain?domain=${encodeURIComponent(input.trim())}`);
    const data = await res.json();

    resultBox.innerHTML = `
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="font-bold text-white text-sm">${data.source_name || data.domain}</span>
          <span class="px-2 py-0.5 rounded font-mono font-bold ${
            data.reputation_score >= 80 ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
          }">${data.reputation_score}/100</span>
        </div>
        <p class="text-slate-300"><strong>Classification:</strong> ${data.publisher_tier}</p>
        <p class="text-slate-400"><strong>Author Transparency:</strong> ${data.author_transparency}</p>
        ${data.notes ? `<ul class="list-disc ml-4 text-[11px] text-slate-400">${data.notes.map((n) => `<li>${n}</li>`).join("")}</ul>` : ""}
      </div>
    `;
  } catch (e) {
    resultBox.innerHTML = `<p class="text-red-400">Failed to inspect domain.</p>`;
  }
}

// ── Misinformation Awareness Center & Quizzes ────────────────────────────────
async function loadAwarenessModules() {
  try {
    const res = await fetch("/api/awareness/modules");
    const modules = await res.json();
    const grid = document.getElementById("awareness-modules-grid");
    if (!grid) return;

    grid.innerHTML = modules
      .map(
        (m) => `
      <div class="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col justify-between space-y-3">
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="px-2 py-0.5 rounded text-[10px] font-mono uppercase font-semibold bg-purple-500/20 text-purple-300">${m.category}</span>
            <span class="text-[10px] font-mono text-slate-400">${m.difficulty}</span>
          </div>
          <h4 class="font-bold text-white text-base">${m.title}</h4>
          <p class="text-xs text-slate-300 mt-2 leading-relaxed">${m.summary}</p>
        </div>
        <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between">
          <span class="text-[10px] font-mono text-slate-400">${m.total_questions} Questions Test</span>
          <button onclick="startModuleQuiz('${m.id}')" class="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-lg shadow-purple-500/20">
            Start Lesson & Quiz →
          </button>
        </div>
      </div>
    `
      )
      .join("");
  } catch (e) {
    console.error("Awareness modules error:", e);
  }
}

async function startModuleQuiz(moduleId) {
  try {
    const res = await fetch(`/api/awareness/modules/${moduleId}`);
    const mod = await res.json();
    state.currentModule = mod;

    document.getElementById("quiz-title-header").textContent = mod.title;
    document.getElementById("quiz-module-content").innerHTML = formatModuleMarkdown(mod.content);

    const qList = document.getElementById("quiz-questions-list");
    qList.innerHTML = mod.questions
      .map(
        (q, qIdx) => `
      <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <p class="font-semibold text-white text-xs">Q${qIdx + 1}: ${q.question}</p>
        <div class="space-y-2">
          ${q.options
            .map(
              (opt, optIdx) => `
            <label class="flex items-center space-x-2.5 p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 cursor-pointer text-xs text-slate-300">
              <input type="radio" name="quiz_q_${q.question_id}" value="${optIdx}" class="text-purple-600 focus:ring-0">
              <span>${opt}</span>
            </label>
          `
            )
            .join("")}
        </div>
      </div>
    `
      )
      .join("");

    document.getElementById("awareness-modules-grid").classList.add("hidden");
    document.getElementById("awareness-quiz-panel").classList.remove("hidden");
    document.getElementById("quiz-result-feedback").classList.add("hidden");
    window.scrollTo({ top: 100, behavior: "smooth" });
  } catch (e) {
    showToast("Error opening module quiz.", "error");
  }
}

function formatModuleMarkdown(text) {
  return text
    .replace(/^# (.*$)/gim, '<h3 class="text-base font-bold text-white mb-2">$1</h3>')
    .replace(/^### (.*$)/gim, '<h4 class="text-sm font-bold text-purple-300 mt-3 mb-1">$1</h4>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong class="text-white">$1</strong>')
    .replace(/^- (.*$)/gim, '<li class="ml-4 list-disc text-slate-300 my-0.5">$1</li>')
    .replace(/\n\n/g, '<p class="my-2"></p>');
}

function closeQuizView() {
  document.getElementById("awareness-modules-grid").classList.remove("hidden");
  document.getElementById("awareness-quiz-panel").classList.add("hidden");
}

async function submitCurrentQuiz() {
  if (!state.currentModule) return;

  const answers = {};
  for (const q of state.currentModule.questions) {
    const selected = document.querySelector(`input[name="quiz_q_${q.question_id}"]:checked`);
    if (!selected) {
      showToast(`Please answer question #${q.question_id}`, "error");
      return;
    }
    answers[q.question_id] = parseInt(selected.value);
  }

  try {
    const headers = { "Content-Type": "application/json" };
    if (state.token) headers["Authorization"] = `Bearer ${state.token}`;

    const res = await fetch(`/api/awareness/modules/${state.currentModule.id}/submit`, {
      method: "POST",
      headers,
      body: JSON.stringify({ answers }),
    });

    const result = await res.json();
    const feedbackBox = document.getElementById("quiz-result-feedback");
    feedbackBox.classList.remove("hidden");

    feedbackBox.innerHTML = `
      <div class="p-3 rounded-lg ${result.passed ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"} font-bold mb-3">
        ${result.passed ? "🎉 Congratulations! You Passed this Awareness Module!" : "Keep practicing! Review the explanations below:"}
        Score: ${result.score}/${result.max_score} (${result.percentage}%)
      </div>
      <div class="space-y-2">
        ${result.feedback
          .map(
            (fb) => `
          <div class="p-2.5 rounded bg-slate-800/80 text-[11px] space-y-1">
            <div class="flex items-center space-x-1 font-bold ${fb.is_correct ? "text-emerald-400" : "text-red-400"}">
              <span>${fb.is_correct ? "✓ Correct" : "✗ Incorrect"}</span>
              <span class="text-slate-300 font-normal">— ${fb.question}</span>
            </div>
            <p class="text-slate-400"><em>${fb.explanation}</em></p>
          </div>
        `
          )
          .join("")}
      </div>
    `;

    // Update awareness score badge
    document.getElementById("user-awareness-score-badge").textContent = result.new_user_awareness_score;
    if (state.currentUser) state.currentUser.awareness_score = result.new_user_awareness_score;
    showToast(`Literacy Score updated to ${result.new_user_awareness_score}!`, "success");
  } catch (e) {
    showToast("Error evaluating quiz answers.", "error");
  }
}

// ── Analysis History & Saved Reports ─────────────────────────────────────────
async function loadHistory() {
  const search = document.getElementById("history-search-input").value;
  const verdict = document.getElementById("history-verdict-filter").value;
  const tbody = document.getElementById("history-table-tbody");
  if (!tbody) return;

  try {
    let url = `/api/reports?saved_only=${state.historySavedOnly}`;
    if (search) url += `&q=${encodeURIComponent(search)}`;
    if (verdict) url += `&verdict=${encodeURIComponent(verdict)}`;

    const headers = {};
    if (state.token) headers["Authorization"] = `Bearer ${state.token}`;

    const res = await fetch(url, { headers });
    const reports = await res.json();

    if (reports.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" class="p-6 text-center text-slate-500">No matching analysis reports found.</td></tr>`;
      return;
    }

    tbody.innerHTML = reports
      .map(
        (r) => `
      <tr class="hover:bg-slate-800/40 transition-colors">
        <td class="p-4 font-mono text-[10px] text-slate-400">${new Date(r.created_at).toLocaleDateString()}</td>
        <td class="p-4 font-medium text-slate-200 max-w-sm truncate">${r.title}</td>
        <td class="p-4"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${
          r.verdict.includes("Supported")
            ? "bg-emerald-500/20 text-emerald-400"
            : r.verdict.includes("Contradicted")
            ? "bg-red-500/20 text-red-400"
            : "bg-slate-800 text-slate-400"
        }">${r.verdict}</span></td>
        <td class="p-4 font-mono font-bold text-blue-400">${Math.round(r.overall_credibility_score)}/100</td>
        <td class="p-4 text-right space-x-2">
          <button onclick="loadReportByIdOrToken('${r.id}')" class="text-blue-400 hover:text-blue-300 font-medium">View</button>
          ${state.currentUser ? `<button onclick="deleteReportRecord('${r.id}')" class="text-red-400 hover:text-red-300">Delete</button>` : ""}
        </td>
      </tr>
    `
      )
      .join("");
  } catch (e) {
    console.error("History fetch error:", e);
  }
}

function toggleSavedFilter() {
  state.historySavedOnly = !state.historySavedOnly;
  const btn = document.getElementById("history-saved-toggle");
  if (state.historySavedOnly) {
    btn.textContent = "★ Saved Only: ON";
    btn.className = "px-4 py-2.5 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/30 text-xs font-semibold";
  } else {
    btn.textContent = "★ Saved Only: OFF";
    btn.className = "px-4 py-2.5 rounded-xl glass-panel text-xs text-slate-300 font-medium hover:text-white transition-colors";
  }
  loadHistory();
}

async function deleteReportRecord(reportId) {
  if (!confirm("Are you sure you want to delete this analysis report?")) return;
  try {
    const res = await fetch(`/api/reports/${reportId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (res.ok) {
      showToast("Report deleted successfully.", "success");
      loadHistory();
    } else {
      showToast("Could not delete report.", "error");
    }
  } catch (e) {
    showToast("Network error deleting report.", "error");
  }
}

// ── Admin Governance Panel (RBAC) ────────────────────────────────────────────
async function loadAdminPanel() {
  if (!state.currentUser || state.currentUser.role !== "admin") {
    showToast("Admin access required. Please sign in as Admin.", "error");
    demoSignIn("admin");
    return;
  }

  try {
    const headers = { Authorization: `Bearer ${state.token}` };

    // 1. Admin Metrics
    const resMetrics = await fetch("/api/admin/metrics", { headers });
    const metrics = await resMetrics.json();
    document.getElementById("admin-metric-users").textContent = metrics.total_users;
    document.getElementById("admin-metric-analyses").textContent = metrics.total_analyses;
    document.getElementById("admin-metric-misinfo").textContent = metrics.flagged_misinformation_count;
    document.getElementById("admin-metric-cache").textContent = `${metrics.cache_hit_rate}%`;

    // 2. Admin Sources List
    const resSources = await fetch("/api/admin/sources", { headers });
    const sources = await resSources.json();
    const sourcesTbody = document.getElementById("admin-sources-tbody");
    sourcesTbody.innerHTML = sources
      .map(
        (s) => `
      <tr class="hover:bg-slate-800/40">
        <td class="py-2.5 font-bold text-slate-200">${s.name}</td>
        <td class="py-2.5 font-mono text-blue-400">${s.domain}</td>
        <td class="py-2.5 uppercase font-mono text-[10px] text-slate-400">${s.category}</td>
        <td class="py-2.5 font-mono font-bold text-emerald-400">${s.credibility_rating}</td>
        <td class="py-2.5">${s.is_ifcn_certified ? "✓ Yes" : "No"}</td>
        <td class="py-2.5 text-right">
          <button onclick="deleteSourceRecord(${s.id})" class="text-red-400 hover:text-red-300">Remove</button>
        </td>
      </tr>
    `
      )
      .join("");

    // 3. Admin Users List
    const resUsers = await fetch("/api/admin/users", { headers });
    const users = await resUsers.json();
    const usersTbody = document.getElementById("admin-users-tbody");
    usersTbody.innerHTML = users
      .map(
        (u) => `
      <tr class="hover:bg-slate-800/40">
        <td class="py-2.5 font-bold text-slate-200">${u.full_name}</td>
        <td class="py-2.5 font-mono text-slate-400">${u.email}</td>
        <td class="py-2.5"><span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
          u.role === "admin" ? "bg-amber-500/20 text-amber-300" : "bg-slate-800 text-slate-300"
        }">${u.role}</span></td>
        <td class="py-2.5 font-mono text-purple-400">${u.awareness_score} pts</td>
        <td class="py-2.5">${u.is_active ? `<span class="text-emerald-400 font-semibold">Active</span>` : `<span class="text-red-400 font-semibold">Suspended</span>`}</td>
        <td class="py-2.5 text-right">
          <button onclick="toggleUserStatusRecord(${u.id})" class="text-xs text-blue-400 hover:text-blue-300 font-medium">Toggle Status</button>
        </td>
      </tr>
    `
      )
      .join("");
  } catch (e) {
    console.error("Admin load error:", e);
  }
}

function openAddSourceModal() {
  document.getElementById("add-source-modal").classList.remove("hidden");
}

function closeAddSourceModal() {
  document.getElementById("add-source-modal").classList.add("hidden");
}

async function handleCreateSourceSubmit(event) {
  event.preventDefault();
  const name = document.getElementById("new-source-name").value;
  const domain = document.getElementById("new-source-domain").value;
  const category = document.getElementById("new-source-category").value;
  const rating = parseFloat(document.getElementById("new-source-rating").value);
  const isIfcn = document.getElementById("new-source-ifcn").checked;
  const desc = document.getElementById("new-source-desc").value;

  try {
    const res = await fetch("/api/admin/sources", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${state.token}`,
      },
      body: JSON.stringify({
        name,
        domain,
        category,
        credibility_rating: rating,
        country: "India",
        is_ifcn_certified: isIfcn,
        description: desc,
      }),
    });

    if (res.ok) {
      showToast(`Source '${name}' added to registry!`, "success");
      closeAddSourceModal();
      loadAdminPanel();
    } else {
      const err = await res.json();
      showToast(err.detail || "Failed to add source", "error");
    }
  } catch (e) {
    showToast("Network error creating source.", "error");
  }
}

async function deleteSourceRecord(sourceId) {
  if (!confirm("Are you sure you want to remove this source from the trusted registry?")) return;
  try {
    const res = await fetch(`/api/admin/sources/${sourceId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (res.ok) {
      showToast("Source removed from registry.", "success");
      loadAdminPanel();
    }
  } catch (e) {
    showToast("Error deleting source.", "error");
  }
}

async function toggleUserStatusRecord(userId) {
  try {
    const res = await fetch(`/api/admin/users/${userId}/status`, {
      method: "PUT",
      headers: { Authorization: `Bearer ${state.token}` },
    });
    if (res.ok) {
      showToast("User account status updated.", "success");
      loadAdminPanel();
    }
  } catch (e) {
    showToast("Error updating user status.", "error");
  }
}
