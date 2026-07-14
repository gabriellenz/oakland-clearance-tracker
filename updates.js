const DATA_URL = "data/oakland-2026.json";

function fmtDate(value) {
  if (!value) return "Unknown";
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:" ? url.href : "";
  } catch {
    return "";
  }
}

function sourceLink(source) {
  const url = safeUrl(source?.url);
  if (!url) return escapeHtml(source?.publisher || source?.title || "Source");
  const label = source.publisher || source.title || "Source";
  return `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`;
}

function renderLog(data) {
  document.getElementById("lastChecked").textContent = data.metadata.lastChecked || "unknown";
  document.getElementById("logIntro").textContent =
    `This log starts with updates found on or after ${fmtDate(data.metadata.updateLogStartDate)}. Earlier backfill work is not reconstructed here.`;

  const rows = data.updateLog || [];
  const log = document.getElementById("updateLog");
  if (!rows.length) {
    log.innerHTML = `<div class="empty-state">No forward-looking update-log entries yet.</div>`;
    return;
  }

  log.innerHTML = rows
    .map((row) => {
      const victim = row.victimName && row.victimName !== "unknown" ? row.victimName : "Name not released";
      return `<article class="log-item">
        <div>
          <span class="log-type">${escapeHtml(row.label)}</span>
          <h2>${escapeHtml(victim)}</h2>
          <p>${fmtDate(row.incidentDate)} · ${escapeHtml(row.location || "Location pending")}</p>
        </div>
        <div class="log-meta">
          <strong>Found ${fmtDate(row.dateFound)}</strong>
          <span>${sourceLink(row.source)}</span>
        </div>
      </article>`;
    })
    .join("");
}

async function init() {
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error(`Failed to load ${DATA_URL}`);
  renderLog(await response.json());
}

init().catch((error) => {
  document.body.innerHTML = `<main class="error"><h1>Data failed to load</h1><p>${escapeHtml(error.message)}</p></main>`;
});
