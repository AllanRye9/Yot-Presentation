/**
 * AI Forex Signal Hub – Frontend Logic
 * Handles: pair selection, signal display, accuracy chart, news feed,
 * risk management calculator, technical analysis, alert subscription,
 * and auto-refresh.
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
const dataSourceBadge = document.getElementById('data-source-badge');
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

// Risk calculator DOM refs
const calcBalance   = document.getElementById('calc-balance');
const calcRiskPct   = document.getElementById('calc-risk-pct');
const calcEntry     = document.getElementById('calc-entry');
const calcSl        = document.getElementById('calc-sl');
const calcTp        = document.getElementById('calc-tp');
const calcLeverage  = document.getElementById('calc-leverage');
const calcLotType   = document.getElementById('calc-lot-type');

// Risk result DOM refs
const resRiskAmount   = document.getElementById('res-risk-amount');
const resPositionSize = document.getElementById('res-position-size');
const resPipValue     = document.getElementById('res-pip-value');
const resPipsSl       = document.getElementById('res-pips-sl');
const resPipsTp       = document.getElementById('res-pips-tp');
const resRr           = document.getElementById('res-rr');
const resProfit       = document.getElementById('res-profit');
const resMargin       = document.getElementById('res-margin');

// Technical analysis DOM refs
const taLoading       = document.getElementById('ta-loading');
const taContent       = document.getElementById('ta-content');
const taSrContent     = document.getElementById('ta-sr-content');
const taFvgContent    = document.getElementById('ta-fvg-content');
const taBosContent    = document.getElementById('ta-bos-content');
const taChochContent  = document.getElementById('ta-choch-content');
const taVolumeContent = document.getElementById('ta-volume-content');

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

function isJpy(pair) {
  return pair && pair.includes('JPY');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
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
    // Auto-fill calculator with signal levels
    autoFillCalculator(signalData);
    runCalculator();
    // Load technical analysis for this pair
    loadTechnicalAnalysis(pair);
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

  // Last updated + data source badge
  lastUpdatedEl.textContent = `Updated: ${formatDate(data.generated_at)}`;
  if (dataSourceBadge) {
    const isLive = data.is_live === true;
    dataSourceBadge.textContent = isLive ? '🟢 Live' : '🟡 Cached';
    dataSourceBadge.className = `fx-data-source ${isLive ? 'live' : 'static'}`;
    dataSourceBadge.title = data.data_source || '';
  }
}

function formatPrice(price, pair) {
  const decimals = isJpy(pair) ? 2 : 4;
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

// ─── Risk Management Calculator ───────────────────────────────────────────────

/** Approximate pip value in USD per standard lot for a given pair/price.
 *
 * Pip sizes:  non-JPY = 0.0001 (1/10,000), JPY = 0.01 (1/100)
 * Standard lot = 100,000 units
 *
 * Formula by quote currency:
 *   - Quote is USD (e.g. EUR/USD):  pipValue = pipSize × lotSize  → always $10
 *   - Base  is USD (e.g. USD/JPY):  pipValue = (pipSize × lotSize) / entryPrice
 *   - JPY cross (e.g. EUR/JPY):     pipValue ≈ (pipSize × lotSize) / entryPrice × 100
 *       The ×100 converts the yen-denominated pip to USD via the implicit $/¥ rate
 *       (approximated as entryPrice / 100 because JPY crosses trade near ¥100–200).
 *   - Other crosses:                approximated as $10 (same as quote-USD pairs)
 */
function pipValuePerStdLot(pair, entryPriceVal) {
  const LOT = 100_000;
  const jpy = isJpy(pair);
  const pipSize = jpy ? 0.01 : 0.0001;
  const parts = pair.split('/');
  const quoteCcy = parts[1];
  const baseCcy  = parts[0];

  // If quote currency is USD → pip value = pipSize * LOT (always $10 for std lot)
  if (quoteCcy === 'USD') return pipSize * LOT;
  // If base currency is USD → pip value = pipSize * LOT / entryPrice
  if (baseCcy === 'USD') return (pipSize * LOT) / entryPriceVal;
  // Cross pairs: approximate using mid-market (simplified)
  if (jpy) return (pipSize * LOT) / entryPriceVal * 100; // rough approx for JPY crosses
  return pipSize * LOT; // fallback approximation
}

function autoFillCalculator(data) {
  if (data.entry_price) calcEntry.value = data.entry_price;
  if (data.stop_loss)   calcSl.value    = data.stop_loss;
  if (data.take_profit) calcTp.value    = data.take_profit;
}

function runCalculator() {
  const balance   = parseFloat(calcBalance.value)  || 0;
  const riskPct   = parseFloat(calcRiskPct.value)  || 0;
  const entry     = parseFloat(calcEntry.value)    || 0;
  const sl        = parseFloat(calcSl.value)       || 0;
  const tp        = parseFloat(calcTp.value)       || 0;
  const leverage  = parseFloat(calcLeverage.value) || 100;
  const lotType   = calcLotType.value;

  const lotMultiplier = lotType === 'standard' ? 1 : lotType === 'mini' ? 0.1 : 0.01;

  if (!balance || !riskPct || !entry || !sl) {
    [resRiskAmount, resPositionSize, resPipValue, resPipsSl, resPipsTp, resRr, resProfit, resMargin]
      .forEach(el => { if (el) el.textContent = '–'; });
    return;
  }

  const pair = currentPair;
  const jpy  = isJpy(pair);
  const pipSize = jpy ? 0.01 : 0.0001;

  const riskAmount = balance * (riskPct / 100);
  const pipsSl     = Math.abs(entry - sl) / pipSize;
  const pipsTp     = tp ? Math.abs(tp - entry) / pipSize : 0;

  const pvPerStdLot = pipValuePerStdLot(pair, entry);
  // pip value adjusted for lot type
  const pvPerLot    = pvPerStdLot * lotMultiplier;

  // Position size in lots
  const positionLots = pipsSl > 0 ? riskAmount / (pipsSl * pvPerLot) : 0;
  const positionUnits = positionLots * 100_000 * lotMultiplier;

  // RR ratio
  const rr = pipsSl > 0 && pipsTp > 0 ? pipsTp / pipsSl : 0;

  // Potential profit
  const potentialProfit = positionLots * pipsTp * pvPerLot;

  // Required margin = (positionUnits * entry) / leverage
  const margin = (positionUnits * entry) / leverage;

  // Update UI
  resRiskAmount.textContent   = `$${riskAmount.toFixed(2)}`;
  resPositionSize.textContent = `${positionLots.toFixed(2)} lots`;
  resPipValue.textContent     = `$${pvPerLot.toFixed(2)}`;
  resPipsSl.textContent       = `${pipsSl.toFixed(1)} pips`;
  resPipsTp.textContent       = tp ? `${pipsTp.toFixed(1)} pips` : '–';
  resRr.textContent           = rr > 0 ? `1 : ${rr.toFixed(2)}` : '–';
  resProfit.textContent       = potentialProfit > 0 ? `$${potentialProfit.toFixed(2)}` : '–';
  resMargin.textContent       = `$${margin.toFixed(2)}`;

  // Color RR ratio
  resRr.className = 'risk-result-value rr-value';
  if (rr >= 2) resRr.classList.add('buy');
  else if (rr > 0 && rr < 1) resRr.classList.add('sell');
}

// Attach calculator listeners
[calcBalance, calcRiskPct, calcEntry, calcSl, calcTp, calcLeverage, calcLotType]
  .forEach(el => { if (el) el.addEventListener('input', runCalculator); });

// ─── Technical Analysis ───────────────────────────────────────────────────────
async function loadTechnicalAnalysis(pair) {
  taLoading.style.display = 'block';
  taContent.style.display = 'none';
  try {
    const res = await fetch(`/api/forex/technical?pair=${encodeURIComponent(pair)}`);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    renderTechnicalAnalysis(data);
  } catch (err) {
    taLoading.textContent = 'Could not load technical analysis.';
    console.error('Failed to load technical analysis:', err);
  }
}

function renderTechnicalAnalysis(data) {
  const dec = isJpy(data.pair) ? 2 : 4;
  const fmt = v => Number(v).toFixed(dec);

  // Support & Resistance
  const sr = data.support_resistance;
  taSrContent.innerHTML = `
    <div class="sr-group">
      <div class="sr-group-title resistance-title">Resistance</div>
      ${sr.resistance.slice().reverse().map(r => `
        <div class="sr-level resistance">
          <span class="sr-badge">R</span>
          <span class="sr-price">${fmt(r)}</span>
        </div>`).join('')}
      <div class="sr-current">
        <span class="sr-badge current-badge">●</span>
        <span class="sr-price current-price">Current: ${fmt(data.current_price)}</span>
      </div>
      ${sr.support.map(s => `
        <div class="sr-level support">
          <span class="sr-badge">S</span>
          <span class="sr-price">${fmt(s)}</span>
        </div>`).join('')}
    </div>`;

  // Fair Value Gaps
  taFvgContent.innerHTML = data.fvg.map(g => `
    <div class="ta-item ${g.type} ${g.filled ? 'filled' : 'unfilled'}">
      <div class="ta-item-header">
        <span class="ta-badge ${g.type}">${g.type.toUpperCase()} FVG</span>
        <span class="ta-badge ${g.filled ? 'neutral' : 'active'}">${g.filled ? 'Filled' : 'Unfilled'}</span>
        <span class="ta-date">${g.created}</span>
      </div>
      <div class="ta-price-range">${fmt(g.bottom)} – ${fmt(g.top)}</div>
      <div class="ta-desc">${escapeHtml(g.description)}</div>
    </div>`).join('');

  // Break of Structure
  taBosContent.innerHTML = data.bos.map(b => `
    <div class="ta-item ${b.type}">
      <div class="ta-item-header">
        <span class="ta-badge ${b.type}">${b.type.toUpperCase()} BOS</span>
        <span class="ta-date">${b.date}</span>
      </div>
      <div class="ta-price-single">${fmt(b.level)}</div>
      <div class="ta-desc">${escapeHtml(b.description)}</div>
    </div>`).join('');

  // CHoCH
  taChochContent.innerHTML = data.choch.map(c => `
    <div class="ta-item ${c.type}">
      <div class="ta-item-header">
        <span class="ta-badge ${c.type}">CHoCH</span>
        <span class="ta-date">${c.date}</span>
      </div>
      <div class="ta-price-single">${fmt(c.level)}</div>
      <div class="ta-desc">${escapeHtml(c.description)}</div>
    </div>`).join('');

  // High Volume Zones
  taVolumeContent.innerHTML = data.high_volume_zones.map(z => `
    <div class="ta-item volume-zone ${z.strength}">
      <div class="ta-item-header">
        <span class="ta-badge volume-${z.strength}">${z.strength.toUpperCase()} VOLUME</span>
        <span class="ta-price-range">${fmt(z.bottom)} – ${fmt(z.top)}</span>
      </div>
      <div class="ta-desc">${escapeHtml(z.description)}</div>
    </div>`).join('');

  taLoading.style.display = 'none';
  taContent.style.display = 'grid';
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
