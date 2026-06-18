const SENTIMENT_COLORS = {
  positivo: "#0b7a46",
  neutro: "#6b7280",
  negativo: "#b42318"
};

async function loadStatus() {
  const response = await fetch("docs/status.json", { cache: "no-store" });
  if (!response.ok) return null;
  return response.json();
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node && value !== undefined && value !== null) node.textContent = value;
}

function setHref(id, value) {
  const node = document.getElementById(id);
  if (node && value) node.href = value;
}

function formatPercent(value, total) {
  if (!total) return "0%";
  return `${Math.round((value / total) * 100)}%`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function shortHash(value) {
  if (!value) return "";
  return `${value.slice(0, 8)}...`;
}

function renderSentiment(sentiment) {
  const total = sentiment.total || 0;
  const positive = sentiment.positivo || 0;
  const neutral = sentiment.neutro || 0;
  const negative = sentiment.negativo || 0;
  setText("positive-total", positive);
  setText("neutral-total", neutral);
  setText("negative-total", negative);
  setText("positive-percent", formatPercent(positive, total));
  setText("neutral-percent", formatPercent(neutral, total));
  setText("negative-percent", formatPercent(negative, total));

  const donut = document.getElementById("sentiment-donut");
  if (donut) {
    if (!total) {
      donut.style.background = "conic-gradient(#d9e2df 0 100%)";
      donut.dataset.label = "0";
    } else {
      const positiveEnd = (positive / total) * 100;
      const neutralEnd = positiveEnd + (neutral / total) * 100;
      donut.style.background = `conic-gradient(${SENTIMENT_COLORS.positivo} 0 ${positiveEnd}%, ${SENTIMENT_COLORS.neutro} ${positiveEnd}% ${neutralEnd}%, ${SENTIMENT_COLORS.negativo} ${neutralEnd}% 100%)`;
      donut.dataset.label = String(total);
    }
  }

  const legend = document.getElementById("sentiment-legend");
  if (legend) {
    legend.innerHTML = [
      ["positivo", positive],
      ["neutro", neutral],
      ["negativo", negative]
    ].map(([name, count]) => `
      <div class="legend-row">
        <span class="swatch" style="background:${SENTIMENT_COLORS[name]}"></span>
        <span>${name}</span>
        <strong>${count}</strong>
      </div>
    `).join("");
  }
}

function renderBars(id, items, emptyText) {
  const node = document.getElementById(id);
  if (!node) return;
  if (!items || !items.length) {
    node.innerHTML = `<p class="empty">${emptyText}</p>`;
    return;
  }
  const max = Math.max(...items.map((item) => item.count), 1);
  node.innerHTML = items.map((item) => `
    <div class="bar-row">
      <div class="bar-label">
        <span>${escapeHtml(item.name)}</span>
        <strong>${item.count}</strong>
      </div>
      <div class="bar-track"><span style="width:${Math.max(4, (item.count / max) * 100)}%"></span></div>
    </div>
  `).join("");
}

function renderTrend(items) {
  const node = document.getElementById("trend-chart");
  if (!node) return;
  if (!items || !items.length) {
    node.innerHTML = '<p class="empty">Sin serie temporal todavia.</p>';
    return;
  }
  const max = Math.max(...items.map((item) => item.comments_total), 1);
  node.innerHTML = items.map((item) => `
    <div class="trend-col">
      <div class="trend-bar" style="height:${Math.max(8, (item.comments_total / max) * 100)}%"></div>
      <span>${escapeHtml(item.date.slice(5))}</span>
      <strong>${item.comments_total}</strong>
    </div>
  `).join("");
}

function renderComments(items) {
  const body = document.getElementById("comments-body");
  if (!body) return;
  if (!items || !items.length) {
    body.innerHTML = '<tr><td colspan="7">Sin comentarios reales en la ultima corrida.</td></tr>';
    return;
  }
  body.innerHTML = items.map((item) => `
    <tr>
      <td>${escapeHtml(item.comment_created_at)}</td>
      <td>${escapeHtml(item.network)}</td>
      <td>${escapeHtml(item.category)}</td>
      <td><span class="pill ${escapeHtml(item.sentiment)}">${escapeHtml(item.sentiment)}</span></td>
      <td>${escapeHtml(item.sentiment_score)}</td>
      <td>${escapeHtml(item.message)}</td>
      <td>${item.post_url ? `<a href="${escapeHtml(item.post_url)}">Abrir</a>` : ""}</td>
    </tr>
  `).join("");
}

function renderAlerts(items) {
  const body = document.getElementById("alerts-body");
  if (!body) return;
  if (!items || !items.length) {
    body.innerHTML = '<tr><td colspan="6">Sin alertas reales en la ultima corrida.</td></tr>';
    return;
  }
  body.innerHTML = items.map((item) => `
    <tr>
      <td>${escapeHtml(item.comment_created_at)}</td>
      <td>${escapeHtml(item.category)}</td>
      <td>${escapeHtml(item.urgency)}</td>
      <td><span class="pill ${escapeHtml(item.sentiment)}">${escapeHtml(item.sentiment)}</span></td>
      <td>${escapeHtml(item.message)}</td>
      <td>${item.post_url ? `<a href="${escapeHtml(item.post_url)}">Abrir</a>` : ""}</td>
    </tr>
  `).join("");
}

function renderEvidence(items) {
  const body = document.getElementById("evidence-body");
  if (!body) return;
  if (!items || !items.length) {
    body.innerHTML = '<tr><td colspan="4">Sin evidencias cargadas.</td></tr>';
    return;
  }
  body.innerHTML = items.map((item) => `
    <tr>
      <td>${escapeHtml(item.type)}</td>
      <td>${escapeHtml(item.file_name)}</td>
      <td>${escapeHtml(shortHash(item.sha256))}</td>
      <td>${item.url ? `<a href="${escapeHtml(item.url)}">Drive</a>` : "Local"}</td>
    </tr>
  `).join("");
}

loadStatus().then((status) => {
  if (!status) return;
  const latest = status.latest_run || {};
  const sentiment = status.sentiment || {};
  setText("latest-run-id", latest.run_id);
  setText("latest-run-time", latest.timestamp_utc);
  setText("scope-note", status.scope_note);
  setText("page-name", status.meta_page?.name);
  setText("page-status", status.meta_page?.api_status);
  setText("comments-total", latest.comments_total);
  setText("alerts-total", latest.alerts_total);
  setText("posts-visible", latest.posts_visible);
  setText("website-status", status.website?.status || "Pendiente");
  setText("diagnostic-title", status.diagnostic?.title);
  setText("diagnostic-detail", status.diagnostic?.detail);
  setText("next-step-title", status.next_step?.title);
  setText("next-step-detail", status.next_step?.detail);
  setHref("update-dashboard-link", status.automation?.workflow_url);
  renderSentiment(sentiment);
  renderBars("category-bars", status.categories, "Sin categorias todavia.");
  renderTrend(status.trend);
  renderAlerts(status.alerts);
  renderComments(status.comments);
  renderEvidence(status.evidence);
}).catch(() => {});
