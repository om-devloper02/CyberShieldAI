/* CyberShield AI - Production UI JavaScript */

const CyberShieldUI = (() => {
  const html = document.documentElement;

  // ===== Theme =====
  function initTheme() {
    const saved = localStorage.getItem('cs_theme') || 'dark';
    html.setAttribute('data-theme', saved);
    updateThemeBtn(saved);
  }

  function updateThemeBtn(theme) {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    const icon = btn.querySelector('i');
    const label = btn.querySelector('span');
    if (theme === 'dark') {
      icon.className = 'fas fa-moon me-1';
      if (label) label.textContent = 'Dark Mode';
    } else {
      icon.className = 'fas fa-sun me-1';
      if (label) label.textContent = 'Light Mode';
    }
  }

  function toggleTheme() {
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('cs_theme', next);
    updateThemeBtn(next);
    showToast('Theme changed to ' + next + ' mode', 'success', 2500);
  }

  // ===== Sidebar =====
  function initSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const backdrop = document.getElementById('sidebarBackdrop');
    const toggle = document.getElementById('sidebarToggle');
    const mobileToggle = document.getElementById('mobileSidebarToggle');

    if (toggle) {
      toggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        mainContent?.classList.toggle('expanded');
        localStorage.setItem('cs_sidebar', sidebar.classList.contains('collapsed') ? 'collapsed' : 'open');
      });
    }

    function openMobile() {
      sidebar?.classList.add('mobile-open');
      backdrop?.classList.add('show');
    }
    function closeMobile() {
      sidebar?.classList.remove('mobile-open');
      backdrop?.classList.remove('show');
    }

    mobileToggle?.addEventListener('click', openMobile);
    backdrop?.addEventListener('click', closeMobile);

    const saved = localStorage.getItem('cs_sidebar');
    if (saved === 'collapsed' && sidebar && window.innerWidth > 992) {
      sidebar.classList.add('collapsed');
      mainContent?.classList.add('expanded');
    }
  }

  // ===== Global Loader =====
  function showLoader(text = 'Loading...') {
    const el = document.getElementById('globalLoader');
    if (!el) return;
    el.querySelector('.loader-text').textContent = text;
    el.classList.add('active');
    el.setAttribute('aria-hidden', 'false');
  }

  function hideLoader() {
    const el = document.getElementById('globalLoader');
    if (!el) return;
    el.classList.remove('active');
    el.setAttribute('aria-hidden', 'true');
  }

  // ===== Toast Notifications =====
  function showToast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const icons = { success: 'fa-check-circle', danger: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    const colors = { success: '#2ed573', danger: '#ff4757', warning: '#ffa502', info: '#4f8ef7' };

    const toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
      <i class="fas ${icons[type] || icons.info}" style="color:${colors[type] || colors.info};font-size:1.2rem;"></i>
      <span style="font-size:0.875rem;flex:1">${message}</span>
      <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-muted);cursor:pointer;padding:4px">
        <i class="fas fa-times"></i>
      </button>`;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateX(100px)'; setTimeout(() => toast.remove(), 300); }, duration);
  }

  // ===== Confirm Modal =====
  function confirmAction(title, body, onConfirm, btnClass = 'btn-danger', btnLabel = 'Confirm') {
    const modal = document.getElementById('globalConfirmModal');
    if (!modal) { if (confirm(body)) onConfirm(); return; }
    document.getElementById('confirmModalTitle').textContent = title;
    document.getElementById('confirmModalBody').textContent = body;
    const btn = document.getElementById('confirmModalBtn');
    btn.className = 'btn ' + btnClass;
    btn.textContent = btnLabel;
    const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
    const newBtn = btn.cloneNode(true);
    btn.parentNode.replaceChild(newBtn, btn);
    newBtn.addEventListener('click', () => { bsModal.hide(); onConfirm(); });
    bsModal.show();
  }

  // ===== Tooltips =====
  function initTooltips() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
      new bootstrap.Tooltip(el, { trigger: 'hover' });
    });
  }

  // ===== Global Search =====
  const SEARCH_ITEMS = [
    { label: 'Dashboard', url: '/dashboard/', icon: 'fa-gauge-high' },
    { label: 'Website Scanner', url: '/website/', icon: 'fa-globe' },
    { label: 'Email Scanner', url: '/email/', icon: 'fa-envelope' },
    { label: 'Password Analyzer', url: '/password/', icon: 'fa-key' },
    { label: 'Malware Scanner', url: '/malware/', icon: 'fa-bug' },
    { label: 'Network Scanner', url: '/network/', icon: 'fa-network-wired' },
    { label: 'Attack Simulator', url: '/simulation/', icon: 'fa-flask' },
    { label: 'Phone Hacking Guide', url: '/simulation/phone-hacking', icon: 'fa-mobile-screen-button' },
    { label: 'Training', url: '/training/', icon: 'fa-graduation-cap' },
    { label: 'Cyber Crime Portal', url: '/training/cybercrime', icon: 'fa-gavel' },
    { label: 'Threat Intel', url: '/threat/', icon: 'fa-radiation' },
    { label: 'AI Assistant', url: '#', icon: 'fa-robot', action: 'openAIChat' },
    { label: 'Reports', url: '/reports/', icon: 'fa-chart-bar' },
    { label: 'My Profile', url: '/auth/profile', icon: 'fa-user' },
    { label: 'Settings', url: '/auth/settings', icon: 'fa-gear' },
  ];

  function initSearch() {
    const input = document.getElementById('globalSearch');
    const dropdown = document.getElementById('searchDropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      if (!q) { dropdown.classList.remove('show'); return; }
      const matches = SEARCH_ITEMS.filter(i => i.label.toLowerCase().includes(q));
      if (!matches.length) {
        dropdown.innerHTML = '<div class="p-3 text-muted small text-center">No results found</div>';
      } else {
        dropdown.innerHTML = matches.map(m =>
          m.action === 'openAIChat'
            ? `<a href="#" class="search-item" onclick="CyberShield.openAIChat();return false;"><i class="fas ${m.icon} text-primary"></i>${m.label}</a>`
            : `<a href="${m.url}" class="search-item"><i class="fas ${m.icon} text-primary"></i>${m.label}</a>`
        ).join('');
      }
      dropdown.classList.add('show');
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const first = dropdown.querySelector('.search-item');
        if (first) window.location = first.href;
      }
      if (e.key === 'Escape') dropdown.classList.remove('show');
    });

    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) dropdown.classList.remove('show');
    });
  }

  // ===== Notifications =====
  async function loadNotifications() {
    const list = document.getElementById('notifList');
    const badge = document.getElementById('notifCount');
    if (!list) return;

    try {
      const resp = await fetch('/dashboard/notifications');
      const data = await resp.json();
      const unread = data.notifications.filter(n => !n.read).length;

      if (badge) {
        badge.textContent = unread;
        badge.style.display = unread > 0 ? 'flex' : 'none';
      }

      if (!data.notifications.length) {
        list.innerHTML = '<div class="notif-empty text-muted small p-4 text-center"><i class="fas fa-bell-slash d-block mb-2 fa-lg opacity-50"></i>No notifications yet</div>';
        return;
      }

      list.innerHTML = data.notifications.map(n => `
        <div class="notif-item ${n.read ? '' : 'unread'}" data-id="${n.id}">
          <div class="notif-item-icon ${n.type}">
            <i class="fas fa-${n.icon}"></i>
          </div>
          <div class="flex-grow-1 min-width-0">
            <div class="small fw-semibold">${n.title}</div>
            <div class="text-muted" style="font-size:0.75rem">${n.message}</div>
            <div class="text-muted" style="font-size:0.68rem;margin-top:2px">${n.time}</div>
          </div>
        </div>`).join('');
    } catch {
      list.innerHTML = '<div class="notif-empty text-muted small p-3 text-center">Could not load notifications</div>';
    }
  }

  function initNotifications() {
    loadNotifications();
    document.getElementById('markAllRead')?.addEventListener('click', () => {
      document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
      const badge = document.getElementById('notifCount');
      if (badge) badge.style.display = 'none';
      showToast('All notifications marked as read', 'success', 2500);
    });
    setInterval(loadNotifications, 60000);
  }

  // ===== File Dropzones =====
  function initDropzones() {
    document.querySelectorAll('.file-dropzone').forEach(zone => {
      const input = zone.querySelector('input[type="file"]');
      if (!input) return;

      zone.addEventListener('click', () => input.click());
      zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
      zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
          input.files = e.dataTransfer.files;
          input.dispatchEvent(new Event('change', { bubbles: true }));
          const label = zone.querySelector('.dropzone-filename');
          if (label) label.textContent = e.dataTransfer.files[0].name;
        }
      });
      input.addEventListener('change', () => {
        const label = zone.querySelector('.dropzone-filename');
        if (label && input.files[0]) label.textContent = input.files[0].name;
      });
    });
  }

  // ===== Form Submit Loading =====
  function initFormLoading() {
    document.querySelectorAll('form[data-loading]').forEach(form => {
      form.addEventListener('submit', function() {
        const btn = form.querySelector('[type="submit"]');
        if (btn) {
          btn.disabled = true;
          btn.dataset.originalHtml = btn.innerHTML;
          btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        }
      });
    });
  }

  // ===== Auto-dismiss alerts =====
  function initAlerts() {
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(a => {
      setTimeout(() => {
        a.classList.remove('show');
        setTimeout(() => a.remove(), 300);
      }, 5000);
    });
  }

  // ===== Password Toggle (global) =====
  function initPasswordToggles() {
    document.querySelectorAll('[data-toggle-password]').forEach(btn => {
      btn.addEventListener('click', () => {
        const target = document.getElementById(btn.dataset.togglePassword);
        if (!target) return;
        const icon = btn.querySelector('i');
        const isPassword = target.type === 'password';
        target.type = isPassword ? 'text' : 'password';
        if (icon) icon.className = `fas fa-${isPassword ? 'eye-slash' : 'eye'}`;
      });
    });
  }

  // ===== Init =====
  function init() {
    initTheme();
    initSidebar();
    initTooltips();
    initSearch();
    initNotifications();
    initDropzones();
    initFormLoading();
    initAlerts();
    initPasswordToggles();
    initAIChatWidget();

    document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
  }

  return { init, showLoader, hideLoader, showToast, confirmAction, loadNotifications };
})();

// ===== AI Chat Widget =====
const AIChat = { open: () => {}, close: () => {} };

function initChatBot(formId, messagesId, inputId) {
  const chatForm = document.getElementById(formId);
  const chatMessages = document.getElementById(messagesId);
  const chatInput = document.getElementById(inputId);
  if (!chatForm || !chatMessages || !chatInput) return;

  function appendMessage(role, text, extra = null) {
    const div = document.createElement('div');
    div.className = `chat-message ${role} fade-in-up`;
    div.innerHTML = `
      <div class="chat-bubble">
        ${role === 'ai' ? '<i class="fas fa-robot me-2 text-primary"></i>' : ''}
        <span>${text}</span>
        ${extra?.mitigations ? `<div class="mt-2">${extra.mitigations.map(m => `<span class="badge bg-secondary me-1 mb-1">${m}</span>`).join('')}</div>` : ''}
        ${extra?.suggestions ? `<div class="mt-2 small text-muted">Try: ${extra.suggestions.join(', ')}</div>` : ''}
      </div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    chatInput.value = '';
    appendMessage('user', msg);
    const typing = document.createElement('div');
    typing.className = 'chat-message ai';
    typing.innerHTML = '<div class="chat-bubble"><div class="chat-typing"><span></span><span></span><span></span></div></div>';
    chatMessages.appendChild(typing);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    try {
      const data = await apiPost('/assistant/chat', { message: msg });
      typing.remove();
      appendMessage('ai', data.response, data);
    } catch {
      typing.remove();
      appendMessage('ai', 'Sorry, I encountered an error. Please try again.');
    }
  });

  return { appendMessage, chatInput, chatForm };
}

function initAIChatWidget() {
  const fab = document.getElementById('aiChatFab');
  const panel = document.getElementById('aiChatPanel');
  const closeBtn = document.getElementById('aiChatClose');
  if (!fab || !panel) return;

  const chat = initChatBot('widgetChatForm', 'widgetChatMessages', 'widgetChatInput');

  function openChat() {
    panel.classList.add('open');
    panel.setAttribute('aria-hidden', 'false');
    fab.classList.add('active');
    const icon = fab.querySelector('i');
    if (icon) icon.className = 'fas fa-times';
    setTimeout(() => document.getElementById('widgetChatInput')?.focus(), 300);
  }

  function closeChat() {
    panel.classList.remove('open');
    panel.setAttribute('aria-hidden', 'true');
    fab.classList.remove('active');
    const icon = fab.querySelector('i');
    if (icon) icon.className = 'fas fa-robot';
  }

  function toggleChat() {
    if (panel.classList.contains('open')) closeChat();
    else openChat();
  }

  fab.addEventListener('click', toggleChat);
  closeBtn?.addEventListener('click', closeChat);

  document.querySelectorAll('.ai-topic-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const input = document.getElementById('widgetChatInput');
      if (input) {
        input.value = `Explain ${chip.dataset.topic}`;
        document.getElementById('widgetChatForm')?.requestSubmit();
      }
    });
  });

  const params = new URLSearchParams(window.location.search);
  if (params.get('chat') === 'open') {
    openChat();
    window.history.replaceState({}, '', window.location.pathname);
  }

  AIChat.open = openChat;
  AIChat.close = closeChat;
}

// ===== Scan Result Popup =====
function showScanPopup(level, scoreLabel, subtitle, viewUrl) {
  const configs = {
    safe:       { cls: 'secure',   modalCls: 'secure-modal',   icon: 'fa-shield-halved', title: '✅ SECURE' },
    suspicious: { cls: 'warning',  modalCls: 'warning-modal',  icon: 'fa-exclamation-triangle', title: '⚠️ SUSPICIOUS' },
    dangerous:  { cls: 'insecure', modalCls: 'insecure-modal', icon: 'fa-times-circle', title: '❌ NOT SECURE' },
    // password strength aliases
    very_strong: { cls: 'secure',   modalCls: 'secure-modal',   icon: 'fa-lock', title: '✅ VERY STRONG' },
    strong:      { cls: 'secure',   modalCls: 'secure-modal',   icon: 'fa-lock', title: '✅ STRONG' },
    moderate:    { cls: 'warning',  modalCls: 'warning-modal',  icon: 'fa-unlock', title: '⚠️ MODERATE' },
    weak:        { cls: 'insecure', modalCls: 'insecure-modal', icon: 'fa-unlock-keyhole', title: '❌ WEAK' },
    very_weak:   { cls: 'insecure', modalCls: 'insecure-modal', icon: 'fa-unlock-keyhole', title: '❌ VERY WEAK' },
  };
  const cfg = configs[level] || configs['suspicious'];
  const body = document.getElementById('scanResultModalBody');
  const content = document.getElementById('scanResultModalContent');
  const viewBtn = document.getElementById('scanResultModalViewBtn');

  content.className = 'modal-content cs-modal ' + cfg.modalCls;
  body.innerHTML = `
    <div class="scan-popup-icon ${cfg.cls}">
      <i class="fas ${cfg.icon}"></i>
    </div>
    <div class="scan-popup-title ${cfg.cls}">${cfg.title}</div>
    <div class="scan-popup-subtitle">${subtitle}</div>
    ${scoreLabel ? `<div class="scan-popup-score"><i class="fas fa-chart-bar text-muted"></i>${scoreLabel}</div>` : ''}
  `;

  if (viewUrl) {
    viewBtn.href = viewUrl;
    viewBtn.style.display = 'inline-flex';
    viewBtn.className = `btn px-4 btn-outline-${ cfg.cls === 'secure' ? 'success' : cfg.cls === 'warning' ? 'warning' : 'danger' }`;
    viewBtn.textContent = 'View Full Details';
  } else {
    viewBtn.style.display = 'none';
  }

  bootstrap.Modal.getOrCreateInstance(document.getElementById('scanResultModal')).show();
}

// ===== Risk Score Gauge =====
function drawGauge(canvasId, score, riskLevel) {
  const el = document.getElementById(canvasId);
  if (!el) return;
  const colors = { safe: '#2ed573', suspicious: '#ffa502', dangerous: '#ff4757' };
  const color = colors[riskLevel] || '#4f8ef7';
  const pct = score / 100;
  const size = 140, r = 56, cx = size / 2, cy = size / 2;
  const circ = 2 * Math.PI * r;
  el.innerHTML = `
    <svg width="${size}" height="${size}" style="transform:rotate(-90deg)">
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="var(--border-color)" stroke-width="10"/>
      <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${color}" stroke-width="10"
        stroke-dasharray="${pct * circ} ${circ}" stroke-linecap="round" style="transition:stroke-dasharray 1s ease"/>
    </svg>
    <div class="gauge-value" style="color:${color}">
      <span>${score}</span><small style="font-size:0.7rem;color:var(--text-muted)">/ 100</small>
    </div>`;
}

// ===== AJAX Helper =====
async function apiPost(url, data, isFormData = false) {
  const opts = {
    method: 'POST',
    headers: isFormData ? {} : { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
    body: isFormData ? data : JSON.stringify(data)
  };
  const resp = await fetch(url, opts);
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ message: 'Request failed' }));
    throw new Error(err.message || 'Request failed');
  }
  return resp.json();
}

// ===== Utilities =====
function showLoading(id) { const el = document.getElementById(id); if (el) el.style.display = 'block'; }
function hideLoading(id) { const el = document.getElementById(id); if (el) el.style.display = 'none'; }
function hideEl(id) { const el = document.getElementById(id); if (el) el.style.display = 'none'; }

function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}

// ===== Website Scanner =====
const websiteForm = document.getElementById('websiteScanForm');
if (websiteForm) {
  websiteForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = document.getElementById('urlInput').value.trim();
    if (!url) return CyberShieldUI.showToast('Please enter a URL', 'warning');
    showLoading('scanLoading');
    hideEl('scanResult');
    try {
      const data = await apiPost('/website/scan', { url });
      if (data.success) {
        renderWebsiteResult(data.result);
        const r = data.result;
        showScanPopup(
          r.risk_level,
          `Risk Score: ${r.risk_score}/100`,
          r.risk_level === 'safe' ? 'This website appears safe to visit.' :
          r.risk_level === 'suspicious' ? 'This website has some suspicious indicators.' :
          'This website is dangerous! Do not enter any personal information.',
          data.scan_id ? `/website/result/${data.scan_id}` : null
        );
      }
    } catch (err) {
      CyberShieldUI.showToast(err.message, 'danger');
    } finally {
      hideLoading('scanLoading');
    }
  });
}

function renderWebsiteResult(r) {
  const el = document.getElementById('scanResult');
  if (!el) return;
  el.style.display = 'block';
  el.classList.add('fade-in-up');
  el.innerHTML = `
    <div class="scan-result-panel">
      <div class="result-header ${r.risk_level}">
        <div class="risk-gauge" id="gaugeContainer"></div>
        <div>
          <div class="risk-badge risk-${r.risk_level} mb-2">
            <i class="fas ${r.risk_level === 'safe' ? 'fa-check-circle' : r.risk_level === 'suspicious' ? 'fa-exclamation-triangle' : 'fa-times-circle'}"></i>
            ${r.risk_level.toUpperCase()}
          </div>
          <h5 class="mb-1">${r.url}</h5>
          <small class="text-muted">Risk Score: ${r.risk_score}/100</small>
          ${r.ai_prediction ? `<br><small class="text-muted">AI: ${r.ai_prediction.label} (${r.ai_prediction.confidence}%)</small>` : ''}
        </div>
      </div>
      <div class="card-body">
        <div class="row g-4">
          <div class="col-md-6">
            <h6 class="mb-3"><i class="fas fa-list-check me-2 text-primary"></i>Security Checks</h6>
            ${renderChecks(r.checks)}
          </div>
          <div class="col-md-6">
            <h6 class="mb-3"><i class="fas fa-triangle-exclamation me-2 text-warning"></i>Findings</h6>
            ${r.findings.length ? r.findings.map(f => `<div class="check-item"><i class="fas fa-exclamation-circle check-fail"></i><span>${f}</span></div>`).join('') : '<div class="check-item"><i class="fas fa-check-circle check-pass"></i><span>No issues found</span></div>'}
            <h6 class="mt-4 mb-3"><i class="fas fa-lightbulb me-2 text-success"></i>Recommendations</h6>
            ${r.recommendations.map(rec => `<div class="check-item"><i class="fas fa-arrow-right check-pass"></i><span>${rec}</span></div>`).join('')}
          </div>
        </div>
      </div>
    </div>`;
  drawGauge('gaugeContainer', r.risk_score, r.risk_level);
}

function renderChecks(checks) {
  const labels = {
    https: 'HTTPS Enabled', ssl: 'SSL Certificate Valid', short_url: 'No Short URL',
    ip_url: 'Not IP-Based URL', typosquatting: 'No Typosquatting', homograph: 'No Homograph Attack',
    domain_age: 'Domain Age', suspicious_keywords: 'No Suspicious Keywords'
  };
  return Object.entries(labels).map(([key, label]) => {
    const val = checks[key];
    let pass, text;
    if (key === 'https' || key === 'ssl') pass = val === true || val?.valid === true;
    else if (key === 'short_url' || key === 'ip_url' || key === 'homograph') pass = !val;
    else if (key === 'typosquatting') pass = !val?.detected;
    else if (key === 'domain_age') { pass = (val?.days_old || 0) >= 180; text = val?.days_old ? `${val.days_old} days old` : ''; }
    else if (key === 'suspicious_keywords') { pass = !val || val.length === 0; text = val?.length ? `${val.length} found` : ''; }
    else pass = true;
    return `<div class="check-item"><i class="fas ${pass ? 'fa-check-circle check-pass' : 'fa-times-circle check-fail'}"></i><span>${label}${text ? ` <span class="text-muted">(${text})</span>` : ''}</span></div>`;
  }).join('');
}

// ===== Password Analyzer =====
const passwordInput = document.getElementById('passwordInput');
if (passwordInput) {
  passwordInput.addEventListener('input', debounce(async () => {
    const pw = passwordInput.value;
    if (!pw) { hideEl('passwordResult'); return; }
    try {
      const data = await apiPost('/password/analyze', { password: pw });
      if (data.success) {
        renderPasswordResult(data.result);
        const r = data.result;
        showScanPopup(
          r.strength,
          `Score: ${r.strength_score}/100 | Entropy: ${r.entropy} bits`,
          r.leaked ? `⚠️ Found in ${r.leaked_count.toLocaleString()} data breaches!` :
          r.strength_score >= 60 ? 'Your password is strong and not found in any breach.' :
          'Your password is weak. Please use a stronger password.',
          null
        );
      }
    } catch {}
  }, 500));
}

function renderPasswordResult(r) {
  const el = document.getElementById('passwordResult');
  if (!el) return;
  el.style.display = 'block';
  const strengthColors = { very_weak: 'danger', weak: 'danger', moderate: 'warning', strong: 'success', very_strong: 'success' };
  const color = strengthColors[r.strength] || 'info';
  el.innerHTML = `
    <div class="card fade-in-up">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <strong>Strength: <span class="text-${color} text-capitalize">${r.strength.replace('_', ' ')}</span></strong>
          <span class="badge bg-${color}">${r.strength_score}/100</span>
        </div>
        <div class="progress mb-3"><div class="progress-bar bg-${color}" style="width:${r.strength_score}%"></div></div>
        <div class="row g-3 mb-3">
          <div class="col-6"><small class="text-muted">Entropy</small><div class="fw-bold">${r.entropy} bits</div></div>
          <div class="col-6"><small class="text-muted">Length</small><div class="fw-bold">${r.length} chars</div></div>
        </div>
        ${r.leaked ? `<div class="alert alert-danger py-2 mb-3"><i class="fas fa-exclamation-triangle me-2"></i>Found in <strong>${r.leaked_count.toLocaleString()}</strong> data breaches!</div>` : ''}
        <h6>Crack Time Estimates</h6>
        <div class="table-responsive mb-3">
          <table class="table table-sm" style="font-size:0.8rem">
            ${Object.entries(r.crack_time).map(([k, v]) => `<tr><td class="text-muted">${k.replace(/_/g,' ')}</td><td class="fw-semibold">${v}</td></tr>`).join('')}
          </table>
        </div>
        ${r.issues.length ? r.issues.map(i => `<div class="check-item"><i class="fas fa-times-circle check-fail"></i><span>${i}</span></div>`).join('') : ''}
        ${r.suggestions.map(s => `<div class="check-item"><i class="fas fa-lightbulb" style="color:var(--accent-warning)"></i><span>${s}</span></div>`).join('')}
      </div>
    </div>`;
}

// ===== Full-page Chat (legacy assistant page) =====
initChatBot('chatForm', 'chatMessages', 'chatInput');

// ===== Dashboard Charts =====
function initDashboardCharts(chartData) {
  const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#e8e8f0';
  const gridColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#2a2a4a';

  const typeCtx = document.getElementById('scanTypeChart');
  if (typeCtx && chartData.by_type) {
    new Chart(typeCtx, {
      type: 'doughnut',
      data: { labels: Object.keys(chartData.by_type), datasets: [{ data: Object.values(chartData.by_type), backgroundColor: ['#4f8ef7','#2ed573','#ffa502','#ff4757','#a55eea'], borderWidth: 0 }] },
      options: { responsive: true, plugins: { legend: { labels: { color: textColor } } }, cutout: '65%' }
    });
  }

  const riskCtx = document.getElementById('riskChart');
  if (riskCtx && chartData.by_risk) {
    new Chart(riskCtx, {
      type: 'bar',
      data: { labels: ['Safe', 'Suspicious', 'Dangerous'], datasets: [{ data: [chartData.by_risk.safe||0, chartData.by_risk.suspicious||0, chartData.by_risk.dangerous||0], backgroundColor: ['#2ed573','#ffa502','#ff4757'], borderRadius: 6 }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#888' }, grid: { display: false } }, y: { ticks: { color: '#888' }, grid: { color: gridColor } } } }
    });
  }

  const dayCtx = document.getElementById('dailyChart');
  if (dayCtx && chartData.by_day) {
    const days = Object.keys(chartData.by_day).sort();
    new Chart(dayCtx, {
      type: 'line',
      data: { labels: days.map(d => d.slice(5)), datasets: [{ label: 'Scans', data: days.map(d => chartData.by_day[d]), borderColor: '#4f8ef7', backgroundColor: 'rgba(79,142,247,0.1)', fill: true, tension: 0.4, pointRadius: 4 }] },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#888' }, grid: { display: false } }, y: { ticks: { color: '#888' }, grid: { color: gridColor } } } }
    });
  }
}

// ===== Boot =====
document.addEventListener('DOMContentLoaded', () => CyberShieldUI.init());

window.CyberShield = {
  showToast: (...a) => CyberShieldUI.showToast(...a),
  showLoader: (...a) => CyberShieldUI.showLoader(...a),
  hideLoader: (...a) => CyberShieldUI.hideLoader(...a),
  confirmAction: (...a) => CyberShieldUI.confirmAction(...a),
  openAIChat: () => AIChat.open(),
  closeAIChat: () => AIChat.close(),
  drawGauge, initDashboardCharts, apiPost, showScanPopup
};
