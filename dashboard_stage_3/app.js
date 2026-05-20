// Stage 3 dashboard client logic (Batch 257)
// Reads window.STAGE3_DATA from data.js; renders status bar + tabs.

function fmtMoney(x) {
  if (x === null || x === undefined) return "-";
  const sign = x < 0 ? "-" : "";
  return sign + "$" + Math.abs(x).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtPct(x, withSign) {
  if (x === null || x === undefined) return "-";
  const sign = withSign && x >= 0 ? "+" : "";
  return sign + x.toFixed(2) + "%";
}

function cssClass(x) {
  if (x === null || x === undefined || x === 0) return "";
  return x > 0 ? "positive" : "negative";
}

function renderStatusBar() {
  const d = window.STAGE3_DATA || {};
  const portfolio = d.portfolio || {};
  document.getElementById("last-update").textContent =
    "Last updated: " + (d.last_update || "(no data)");
  document.getElementById("portfolio-value").textContent = fmtMoney(portfolio.current_value);
  const pnlEl = document.getElementById("daily-pnl");
  pnlEl.textContent = fmtMoney(portfolio.daily_pnl_dollar);
  pnlEl.className = "stat-value " + cssClass(portfolio.daily_pnl_dollar);
  const ret = portfolio.current_value && portfolio.starting_value
    ? (portfolio.current_value - portfolio.starting_value) / portfolio.starting_value * 100
    : 0;
  const retEl = document.getElementById("total-return");
  retEl.textContent = fmtPct(ret, true);
  retEl.className = "stat-value " + cssClass(ret);
  const ddEl = document.getElementById("drawdown");
  ddEl.textContent = fmtPct(portfolio.current_dd_pct);
  ddEl.className = "stat-value " + (portfolio.current_dd_pct > 5 ? "negative" : "");
  document.getElementById("open-positions").textContent = portfolio.n_open || 0;
  document.getElementById("closed-trades").textContent = (d.closed_trades || []).length;
}

function renderOpen() {
  const d = window.STAGE3_DATA || {};
  const positions = (d.portfolio || {}).open_positions || [];
  if (!positions.length) return '<div class="empty">No open positions</div>';
  let html = '<table><thead><tr><th>Ticker</th><th>Combo</th><th>Entry Date</th><th>Entry</th><th>Stop</th><th>Tier</th><th>Days</th></tr></thead><tbody>';
  positions.forEach(p => {
    html += `<tr><td>${p.ticker}</td><td>${p.combo_id || ''}</td><td>${p.entry_date}</td><td>${fmtMoney(p.entry_price)}</td><td>${fmtMoney(p.current_stop)}</td><td>${p.confidence_tier}</td><td>${p.days_held}</td></tr>`;
  });
  return html + '</tbody></table>';
}

function renderClosed() {
  const d = window.STAGE3_DATA || {};
  const trades = d.closed_trades || [];
  if (!trades.length) return '<div class="empty">No closed trades yet</div>';
  let html = '<table><thead><tr><th>Ticker</th><th>Combo</th><th>Exit Date</th><th>Entry</th><th>Exit</th><th>PnL %</th><th>PnL $</th><th>Hold</th></tr></thead><tbody>';
  trades.slice().reverse().forEach(t => {
    const cls = t.pnl_pct > 0 ? "positive" : "negative";
    html += `<tr><td>${t.ticker}</td><td>${t.combo_id || ''}</td><td>${t.exit_date}</td><td>${fmtMoney(t.entry_price)}</td><td>${fmtMoney(t.exit_price)}</td><td class="${cls}">${fmtPct(t.pnl_pct, true)}</td><td class="${cls}">${fmtMoney(t.pnl_dollar)}</td><td>${t.hold_days}d</td></tr>`;
  });
  return html + '</tbody></table>';
}

function renderPicks() {
  const d = window.STAGE3_DATA || {};
  const picks = d.todays_picks || [];
  if (!picks.length) return '<div class="empty">No picks today</div>';
  let html = '<table><thead><tr><th>#</th><th>Ticker</th><th>Strategy</th><th>Exit</th><th>Tier</th><th>Size %</th><th>Entry</th><th>Stop</th></tr></thead><tbody>';
  picks.forEach((p, i) => {
    html += `<tr><td>${i + 1}</td><td>${p.ticker}</td><td>${p.strategy}</td><td>${p.exit_method}</td><td>${p.confidence_tier}</td><td>${p.position_size_pct}%</td><td>${fmtMoney(p.entry_price)}</td><td>${fmtMoney(p.initial_stop)}</td></tr>`;
  });
  return html + '</tbody></table>';
}

function renderJournal() {
  const d = window.STAGE3_DATA || {};
  const journal = d.journal_entries || [];
  if (!journal.length) return '<div class="empty">No journal entries yet</div>';
  let html = '<div style="font-size:13px;line-height:1.6">';
  journal.slice().reverse().forEach(j => {
    html += `<div style="margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #e8e8ed"><div style="font-weight:600">${j.date}</div><pre style="white-space:pre-wrap;font-family:inherit;margin:8px 0 0">${j.markdown || ''}</pre></div>`;
  });
  return html + '</div>';
}

function showTab(tabName) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
  const content = document.getElementById('tab-content');
  switch (tabName) {
    case 'open':    content.innerHTML = renderOpen(); break;
    case 'closed':  content.innerHTML = renderClosed(); break;
    case 'picks':   content.innerHTML = renderPicks(); break;
    case 'journal': content.innerHTML = renderJournal(); break;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  renderStatusBar();
  document.querySelectorAll('.tab').forEach(t => t.addEventListener('click', () => showTab(t.dataset.tab)));
  showTab('open');
});
