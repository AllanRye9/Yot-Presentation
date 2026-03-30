/**
 * AI Forex Signal Hub – Frontend Logic
 * Handles: pair selection, signal display, accuracy chart, news feed,
 * alert subscription form and auto-refresh.
 */

'use strict';

// ─── State ───────────────────────────────────────────────────────────────────
let currentPair = 'EUR/USD';
let signalData = null;
let refreshTimer = null;
const REFRESH_INTERVAL_MS = 60_000; // 1 minute

// ─── DOM refs ─────────────────────────────────────────────────────────────────
const pairSelect      = document.getElementById('pair-select');
const lastUpdatedEl   = document.getElementById('last-updated');
const refreshBtn      = document.getElementById('btn-refresh');
const directionBadge  = document.getElementById('signal-direction');
const directionArrow  = document.getElementById('direction-arrow');
const confidenceFill  = document.getElementById('confidence-fill');
const confidencePct   = document.getElementById('confidence-pct');
const accuracy30d     = document.getElementById('accuracy-30d');
const entryPrice      = document.getElementById('entry-price');
const takeProfitEl    = document.getElementById('take-profit');
const stopLossEl      = document.getElementById('stop-loss');
const featuresEl      = document.getElementById('features-list');
const modelVersionEl  = document.getElementById('model-version');
const newsListEl      = document.getElementById('news-list');
const newsLoadingEl   = document.getElementById('news-loading');
const subscribeForm   = document.getElementById('subscribe-form');
const emailInput      = document.getElementById('email-input');
const subscribeStatus = document.getElementById('subscribe-status');
const chartCanvas     = document.getElementById('accuracy-chart');

// ─── Utility ──────────────────────────────────────────────────────────────────
function formatDate(isoStr) {
  try {
    return new Date(isoStr).toLocaleString(undefined, {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return isoStr;
  }
}

function sentimentIcon(s) {
  return s === 'positive' ? '📈' : s === 'negative' ? '📉' : '➡️';
}

// ─── Signal display ───────────────────────────────────────────────────────────
async function loadSignal(pair) {
  refreshBtn.classList.add('spinning');
  try {
    const res = await fetch(`/api/forex/signals?pair=${encodeURIComponent(pair)}`);
    if (!res.ok) throw new Error(await res.text());
    signalData = await res.json();
    renderSignal(signalData);
    drawChart(signalData.history);
  } catch (err) {
    console.error('Failed to load signal:', err);
  } finally {
    refreshBtn.classList.remove('spinning');
  }
}

function renderSignal(data) {
  const dir = data.direction;

  // Direction badge
  directionBadge.textContent = dir;
  directionBadge.className = `signal-direction-badge ${dir}`;
  directionArrow.textContent = dir === 'BUY' ? '▲' : dir === 'SELL' ? '▼' : '→';

  // Confidence bar
  confidenceFill.style.width = `${data.confidence}%`;
  confidenceFill.className = `confidence-fill ${dir}`;
  confidencePct.textContent = `${data.confidence}%`;

  // 30-day accuracy
  accuracy30d.innerHTML = `30-day model accuracy: <strong>${data.accuracy_30d}%</strong>`;

  // Price levels
  entryPrice.textContent   = formatPrice(data.entry_price, data.pair);
  takeProfitEl.textContent = formatPrice(data.take_profit, data.pair);
  stopLossEl.textContent   = formatPrice(data.stop_loss, data.pair);

  // Model info
  if (modelVersionEl) modelVersionEl.textContent = data.model_version || '';
  if (featuresEl) {
    featuresEl.innerHTML = (data.features_used || [])
      .map(f => `<span class="feature-tag">${f}</span>`)
      .join('');
  }

  // Last updated
  lastUpdatedEl.textContent = `Updated: ${formatDate(data.generated_at)}`;
}

function formatPrice(price, pair) {
  // JPY pairs use 2 decimal places; others use 4
  const decimals = pair && pair.includes('JPY') ? 2 : 4;
  return Number(price).toFixed(decimals);
}

// ─── Accuracy Chart ───────────────────────────────────────────────────────────
function drawChart(history) {
  if (!chartCanvas || !history || history.length === 0) return;

  const dpr    = window.devicePixelRatio || 1;
  const W      = chartCanvas.offsetWidth  || 860;
  const H      = 220;
  chartCanvas.width  = W * dpr;
  chartCanvas.height = H * dpr;
  chartCanvas.style.height = H + 'px';

  const ctx = chartCanvas.getContext('2d');
  ctx.scale(dpr, dpr);

  const PAD = { top: 18, right: 18, bottom: 46, left: 58 };
  const cw  = W - PAD.left - PAD.right;
  const ch  = H - PAD.top  - PAD.bottom;

  // Collect all prices
  const prices = history.flatMap(h => [h.entry, h.exit]);
  const minP   = Math.min(...prices);
  const maxP   = Math.max(...prices);
  const range  = maxP - minP || 1;

  const xOf = i => PAD.left + (i / (history.length - 1)) * cw;
  const yOf = p => PAD.top + ch - ((p - minP) / range) * ch;

  // ── Background grid ──
  ctx.strokeStyle = 'rgba(48,54,61,0.7)';
  ctx.lineWidth   = 1;
  const gridLines = 4;
  for (let g = 0; g <= gridLines; g++) {
    const y = PAD.top + (g / gridLines) * ch;
    ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + cw, y); ctx.stroke();
    const price = maxP - (g / gridLines) * range;
    const decimals = history[0] && history[0].entry > 10 ? 2 : 4;
    ctx.fillStyle   = 'rgba(139,148,158,0.85)';
    ctx.font        = `11px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
    ctx.textAlign   = 'right';
    ctx.fillText(price.toFixed(decimals), PAD.left - 6, y + 4);
  }

  // ── Price line (exit prices) ──
  ctx.beginPath();
  ctx.strokeStyle = '#58a6ff';
  ctx.lineWidth   = 2;
  ctx.lineJoin    = 'round';
  history.forEach((h, i) => {
    const x = xOf(i);
    const y = yOf(h.exit);
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();

  // ── Prediction dots ──
  history.forEach((h, i) => {
    const x = xOf(i);
    const y = yOf(h.exit);
    ctx.beginPath();
    ctx.arc(x, y, 4.5, 0, Math.PI * 2);
    ctx.fillStyle   = h.correct ? '#3fb950' : '#f85149';
    ctx.strokeStyle = 'var(--bg, #0d1117)';
    ctx.lineWidth   = 1.5;
    ctx.fill();
    ctx.stroke();
  });

  // ── X-axis date labels (every ~5 entries) ──
  ctx.fillStyle = 'rgba(139,148,158,0.85)';
  ctx.font      = `10px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
  ctx.textAlign = 'center';
  const step    = Math.ceil(history.length / 6);
  history.forEach((h, i) => {
    if (i % step !== 0 && i !== history.length - 1) return;
    const x    = xOf(i);
    const day  = h.day.slice(5);   // MM-DD
    ctx.fillText(day, x, H - PAD.bottom + 16);
  });

  // ── Axis lines ──
  ctx.strokeStyle = 'rgba(48,54,61,0.9)';
  ctx.lineWidth   = 1;
  ctx.beginPath();
  ctx.moveTo(PAD.left, PAD.top); ctx.lineTo(PAD.left, PAD.top + ch + 6); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(PAD.left - 4, PAD.top + ch); ctx.lineTo(PAD.left + cw, PAD.top + ch); ctx.stroke();
}

// ─── News Feed ────────────────────────────────────────────────────────────────
async function loadNews() {
  try {
    const res = await fetch('/api/forex/news');
    if (!res.ok) throw new Error(await res.text());
    const { news } = await res.json();
    renderNews(news);
  } catch (err) {
    newsLoadingEl.textContent = 'Could not load news at this time.';
    console.error('Failed to load news:', err);
  }
}

function renderNews(items) {
  newsLoadingEl.style.display = 'none';
  newsListEl.innerHTML = items.map(item => `
    <div class="news-card">
      <span class="sentiment-icon">${sentimentIcon(item.sentiment)}</span>
      <div class="news-content">
        <div class="news-headline">${escapeHtml(item.headline)}</div>
        <div class="news-meta">
          <span class="source">${escapeHtml(item.source)}</span>
          <span>${formatDate(item.published_at)}</span>
          <span class="sentiment-badge ${item.sentiment}">${item.sentiment}</span>
        </div>
      </div>
    </div>`).join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── Alert Subscription ───────────────────────────────────────────────────────
subscribeForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = emailInput.value.trim();
  const pairs = [...subscribeForm.querySelectorAll('input[type="checkbox"]:checked')]
    .map(cb => cb.value);

  subscribeStatus.className = 'subscribe-status';
  subscribeStatus.textContent = '';

  if (!email) {
    showSubscribeStatus('error', 'Please enter your email address.');
    return;
  }
  if (pairs.length === 0) {
    showSubscribeStatus('error', 'Please select at least one currency pair.');
    return;
  }

  const submitBtn = subscribeForm.querySelector('.btn-subscribe');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Subscribing…';

  try {
    const res = await fetch('/api/forex/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, pairs }),
    });
    const data = await res.json();
    if (data.success) {
      showSubscribeStatus('success', data.message);
      emailInput.value = '';
    } else {
      showSubscribeStatus('error', data.error || 'Subscription failed. Please try again.');
    }
  } catch (err) {
    showSubscribeStatus('error', 'Network error. Please try again.');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Subscribe';
  }
});

function showSubscribeStatus(type, msg) {
  subscribeStatus.className = `subscribe-status ${type}`;
  subscribeStatus.textContent = msg;
}

// ─── Event wiring ─────────────────────────────────────────────────────────────
pairSelect.addEventListener('change', () => {
  currentPair = pairSelect.value;
  loadSignal(currentPair);
  resetAutoRefresh();
});

refreshBtn.addEventListener('click', () => {
  loadSignal(currentPair);
  resetAutoRefresh();
});

function resetAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer);
  refreshTimer = setInterval(() => loadSignal(currentPair), REFRESH_INTERVAL_MS);
}

// ─── Resize chart on window resize ───────────────────────────────────────────
let resizeDebounce = null;
window.addEventListener('resize', () => {
  clearTimeout(resizeDebounce);
  resizeDebounce = setTimeout(() => {
    if (signalData) drawChart(signalData.history);
  }, 200);
});

// ─── Init ─────────────────────────────────────────────────────────────────────
loadSignal(currentPair);
loadNews();
resetAutoRefresh();
