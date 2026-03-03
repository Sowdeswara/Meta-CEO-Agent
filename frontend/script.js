/**
 * HELM v3 Frontend - Dark Professional Theme with Mode Toggle
 */

let currentMode = 'simple';
let charts = {};
let lastDecision = null;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
  console.log('[HELM] DOMContentLoaded event fired');
  
  // Check Chart.js
  if (typeof Chart === 'undefined') {
    console.error('[HELM] CRITICAL: Chart.js not loaded. Is CDN accessible?');
  } else {
    console.log('[HELM] Chart.js loaded successfully. Version:', Chart.version || 'unknown');
  }
  
  initThemeToggle();
  initModeToggle();
  initFormHandler();
  initRawToggle();
  console.log('[HELM] Frontend initialized');
});

// ===== THEME MANAGEMENT =====
function initThemeToggle() {
  const toggle = document.getElementById('theme-toggle');
  const savedTheme = localStorage.getItem('helm-theme') || 'dark';
  
  // Apply saved theme
  if (savedTheme === 'light') {
    document.documentElement.classList.add('light-theme');
    toggle.textContent = '🌙';
  } else {
    document.documentElement.classList.remove('light-theme');
    toggle.textContent = '☀️';
  }
  
  toggle.addEventListener('click', function() {
    document.documentElement.classList.toggle('light-theme');
    const isLight = document.documentElement.classList.contains('light-theme');
    localStorage.setItem('helm-theme', isLight ? 'light' : 'dark');
    toggle.textContent = isLight ? '🌙' : '☀️';
  });
}

// ===== MODE MANAGEMENT =====
function initModeToggle() {
  const modeBtns = document.querySelectorAll('.mode-btn');
  modeBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const mode = this.dataset.mode;
      switchMode(mode);
    });
  });
}

function switchMode(mode) {
  currentMode = mode;
  
  // Update button states
  document.querySelectorAll('.mode-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
  
  // Update content visibility
  document.getElementById('simple-mode').classList.add('hidden');
  document.getElementById('expert-mode').classList.add('hidden');
  
  if (mode === 'simple') {
    document.getElementById('simple-mode').classList.remove('hidden');
  } else {
    document.getElementById('expert-mode').classList.remove('hidden');
    // Re-render charts in expert mode to ensure proper display
    if (lastDecision) {
      setTimeout(renderExpertCharts, 100);
    }
  }
}

// ===== FORM HANDLER =====
function initFormHandler() {
  const form = document.getElementById('decision-form');
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    await submitDecision();
  });
}

async function submitDecision() {
  console.log('[HELM] submitDecision started');
  
  const prompt = document.getElementById('prompt').value;
  console.log('[HELM] Prompt:', prompt);
  
  const required = document.getElementById('required').value
    .split(',')
    .map(s => s.trim())
    .filter(Boolean);
  console.log('[HELM] Required fields:', required);
  
  // gather financial context from HTML form (ACTUAL FIELD IDS)
  const numericFields = [
    { id: 'revenue', key: 'revenue', label: 'Revenue' },
    { id: 'costs', key: 'costs', label: 'Costs' },
    { id: 'investment', key: 'investment', label: 'Investment' },
    { id: 'expected_returns', key: 'expected_returns', label: 'Expected Returns' },
    { id: 'timeframe_years', key: 'timeframe_years', label: 'Timeframe (years)' }
  ];
  
  const textFields = [
    { id: 'objectives', key: 'objectives', label: 'Objectives' },
    { id: 'constraints', key: 'constraints', label: 'Constraints' }
  ];

  const context = {};
  
  // Validate numeric fields
  for (const field of numericFields) {
    const element = document.getElementById(field.id);
    if (!element) {
      console.error(`[HELM] ERROR: Element #${field.id} not found in DOM`);
      showError(`Form field ${field.label} missing from page`);
      return;
    }
    
    const raw = element.value.trim();
    if (raw === '') {
      showError(`${field.label} is required`);
      element.focus();
      return;
    }
    
    const num = parseFloat(raw);
    if (isNaN(num)) {
      showError(`${field.label} must be a number`);
      element.focus();
      return;
    }
    
    context[field.key] = num;
    console.log(`[HELM] ${field.label}: ${num}`);
  }
  
  // Process text fields (split by comma)
  for (const field of textFields) {
    const element = document.getElementById(field.id);
    if (element) {
      const text = element.value.trim();
      if (text) {
        context[field.key] = text.split(',').map(s => s.trim()).filter(Boolean);
      }
      console.log(`[HELM] ${field.label}:`, context[field.key] || '[]');
    }
  }

  const payload = { prompt, context, required_fields: required };
  console.log('[HELM] Sending payload:', JSON.stringify(payload, null, 2));
  
  try {
    console.log('[HELM] Fetching /decision...');
    const r = await fetch('/decision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    console.log('[HELM] Response status:', r.status, r.statusText);
    
    let data;
    try {
      data = await r.json();
    } catch (jsonErr) {
      console.error('[HELM] Failed to parse JSON response:', jsonErr);
      const textResponse = await r.text();
      console.error('[HELM] Response text:', textResponse);
      throw new Error('Server returned invalid JSON: ' + textResponse);
    }
    
    console.log('[HELM] API Response:', data);
    
    if (!r.ok) {
      const errorMsg = data.detail || `Server error ${r.status}`;
      console.error('[HELM] API Error:', errorMsg);
      showError(errorMsg);
      return;
    }
    
    if (!data.decision) {
      console.error('[HELM] Response missing decision field');
      showError('Invalid response: missing decision data');
      return;
    }
    
    lastDecision = data.decision;
    console.log('[HELM] Decision received. Rendering...');
    renderResult(lastDecision);
    
  } catch (err) {
    console.error('[HELM] Network/Parse Error:', err);
    showError(`Request failed: ${err.message}`);
  }
}

// ===== RESULT RENDERING =====
function renderResult(decision) {
  console.log('[HELM] renderResult: Displaying decision');
  
  if (!decision) {
    console.error('[HELM] renderResult: decision is null');
    showError('Decision is null');
    return;
  }
  
  try {
    document.getElementById('result-section').classList.remove('hidden');
    document.getElementById('error-section').classList.add('hidden');
    console.log('[HELM] Result section shown');
    
    renderSimpleMode(decision);
    console.log('[HELM] Simple mode rendered');
    
    if (currentMode === 'expert') {
      renderExpertCharts(decision);
      console.log('[HELM] Expert mode rendered');
    }
    
    const rawJsonEl = document.getElementById('raw-json');
    if (rawJsonEl) {
      rawJsonEl.textContent = JSON.stringify(decision, null, 2);
    }
  } catch (renderErr) {
    console.error('[HELM] renderResult error:', renderErr);
    showError('Failed to render result: ' + renderErr.message);
  }
}

function renderSimpleMode(decision) {
  console.log('[HELM] renderSimpleMode: Starting with decision:', decision);
  
  // Decision text
  const textEl = document.getElementById('decision-text');
  if (!textEl) {
    console.error('[HELM] ERROR: #decision-text not found');
    return;
  }
  textEl.textContent = decision.decision_text || 'N/A';
  console.log('[HELM] Decision text set:', textEl.textContent);
  
  // Status badge
  const badge = document.getElementById('status-badge');
  if (!badge) {
    console.error('[HELM] ERROR: #status-badge not found');
    return;
  }
  const status = decision.status || 'unknown';
  badge.textContent = status.toUpperCase();
  badge.classList.remove('accept', 'reject', 'escalate');
  
  if (status === 'accepted') {
    badge.classList.add('accept');
  } else if (status === 'rejected') {
    badge.classList.add('reject');
  } else {
    badge.classList.add('escalate');
  }
  console.log('[HELM] Status badge set to:', status);
  
  // Metrics
  try {
    document.getElementById('metric-val-score').textContent = 
      (decision.validation_score * 100).toFixed(0) + '%';
    document.getElementById('metric-confidence').textContent = 
      (decision.confidence * 100).toFixed(0) + '%';
    document.getElementById('metric-roi').textContent = 
      (decision.roi_estimate * 100).toFixed(1) + '%';
    document.getElementById('metric-risk').textContent = decision.risk_level || 'N/A';
    console.log('[HELM] Metrics rendered');
  } catch (metricErr) {
    console.error('[HELM] Error rendering metrics:', metricErr);
  }
  
  // Arbitration chart
  renderArbChart(decision);
}

function renderArbChart(decision) {
  console.log('[HELM] renderArbChart: Starting');
  const arb = decision.reasoning?.arbitration || {};
  console.log('[HELM] Arbitration data:', arb);
  
  // Destroy existing chart
  if (charts.arb) {
    console.log('[HELM] Destroying previous arbChart');
    charts.arb.destroy();
  }
  
  const chartElement = document.getElementById('arbChart');
  if (!chartElement) {
    console.error('[HELM] ERROR: Canvas #arbChart not found in DOM');
    return;
  }
  
  if (typeof Chart === 'undefined') {
    console.error('[HELM] ERROR: Chart.js not loaded! typeof Chart =', typeof Chart);
    return;
  }
  
  console.log('[HELM] Creating arbChart with Chart.js');
  const ctx = chartElement.getContext('2d');
  charts.arb = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Strategy', 'Finance', 'Risk Adj.'],
      datasets: [{
        label: 'Score Component',
        data: [
          arb.strategy_component || 0,
          arb.finance_component || 0,
          arb.risk_adjustment || 0
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)'
        ],
        borderColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)'
        ],
        borderWidth: 2,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(context) {
              return (context.parsed.y * 100).toFixed(2) + '%';
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 1.0,
          ticks: { callback: function(v) { return (v * 100) + '%'; } },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderExpertCharts(decision) {
  const arb = decision.reasoning?.arbitration || {};
  const val = decision.reasoning?.validation?.score || {};
  
  renderAgentChart(decision);
  renderValidationChart(decision);
  renderRiskRoiChart(decision);
  renderArbDetails(arb);
}

function renderAgentChart(decision) {
  if (charts.agent) charts.agent.destroy();
  
  const arb = decision.reasoning?.arbitration || {};
  const ctx = document.getElementById('agentChart').getContext('2d');
  
  charts.agent = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Strategy', 'Finance'],
      datasets: [{
        data: [
          arb.strategy_component || 0,
          arb.finance_component || 0
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)'
        ],
        borderColor: ['rgb(59, 130, 246)', 'rgb(16, 185, 129)'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: function(context) {
              return (context.parsed * 100).toFixed(1) + '%';
            }
          }
        }
      }
    }
  });
}

function renderValidationChart(decision) {
  if (charts.validation) charts.validation.destroy();
  
  const val = decision.reasoning?.validation?.score || {};
  const ctx = document.getElementById('validationChart').getContext('2d');
  
  charts.validation = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['Schema', 'Required Fields', 'Numeric', 'ROI Viable', 'Overall'],
      datasets: [{
        label: 'Validation Metrics',
        data: [
          val.schema_complete || 0,
          val.required_fields_present || 0,
          val.numeric_valid || 0,
          val.roi_viable || 0,
          val.weighted_score || 0
        ],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          beginAtZero: true,
          max: 1.0,
          ticks: { callback: function(v) { return (v * 100) + '%'; } }
        }
      }
    }
  });
}

function renderRiskRoiChart(decision) {
  if (charts.riskRoi) charts.riskRoi.destroy();
  
  const ctx = document.getElementById('riskRoiChart').getContext('2d');
  
  const risk = 1 - (decision.validation_score || 0);
  const roi = decision.roi_estimate || 0;
  
  charts.riskRoi = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Decision Risk vs ROI',
        data: [{ x: risk, y: roi }],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
        radius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { position: 'bottom' }
      },
      scales: {
        x: {
          type: 'linear',
          min: 0,
          max: 1,
          title: { display: true, text: 'Risk Level' },
          ticks: { callback: function(v) { return (v * 100).toFixed(0) + '%'; } }
        },
        y: {
          type: 'linear',
          min: 0,
          max: 3,
          title: { display: true, text: 'ROI Estimate' },
          ticks: { callback: function(v) { return (v * 100).toFixed(0) + '%'; } }
        }
      }
    }
  });
}

function renderArbDetails(arb) {
  const container = document.getElementById('arb-details');
  
  const html = `
    <div class="arb-detail-row">
      <label>Composite Score:</label>
      <value>${(arb.composite_score || 0).toFixed(4)}</value>
    </div>
    <div class="arb-detail-row">
      <label>Strategy Component:</label>
      <value>${((arb.strategy_component || 0) * 100).toFixed(1)}%</value>
    </div>
    <div class="arb-detail-row">
      <label>Finance Component:</label>
      <value>${((arb.finance_component || 0) * 100).toFixed(1)}%</value>
    </div>
    <div class="arb-detail-row">
      <label>Risk Adjustment:</label>
      <value>${((arb.risk_adjustment || 0) * 100).toFixed(1)}%</value>
    </div>
    <div class="arb-detail-row">
      <label>Dominant Factor:</label>
      <value>${arb.dominant_factor || 'N/A'}</value>
    </div>
    <div class="arb-detail-row">
      <label>Arbitration Confidence:</label>
      <value>${((arb.confidence || 0) * 100).toFixed(1)}%</value>
    </div>
  `;
  
  container.innerHTML = html;
}

// ===== RAW JSON TOGGLE =====
function initRawToggle() {
  const toggle = document.getElementById('toggle-raw');
  const raw = document.getElementById('raw-json');
  
  toggle.addEventListener('click', function() {
    const isHidden = raw.classList.contains('hidden');
    if (isHidden) {
      raw.classList.remove('hidden');
      toggle.textContent = 'Hide JSON';
    } else {
      raw.classList.add('hidden');
      toggle.textContent = 'Show JSON';
    }
  });
}


