const DATA_URL = "data/oakland-2026.json";

const COLORS = {
  yes: "#0d746b",
  no: "#b63434",
  unknown: "#b77a1b",
  victims: "#171716",
  muted: "#64605a",
  line: "#ded8cc",
  paper: "#fffdfa",
};

const STATUS_LABELS = {
  yes: "Arrest reported",
  no: "No public arrest",
  unknown: "Unknown",
};

let currentData = null;

function fmtDate(value) {
  if (!value) return "Unknown";
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function fmtTableDate(value) {
  if (!value) return "Unknown";
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function fmtMonth(value) {
  const [year, month] = value.split("-").map(Number);
  return new Date(year, month - 1, 1).toLocaleDateString("en-US", {
    month: "short",
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

function statusClass(status) {
  return status === "yes" || status === "no" ? status : "unknown";
}

function statusLabel(status) {
  return STATUS_LABELS[status] || STATUS_LABELS.unknown;
}

function arrestDetail(victim) {
  const dateLine =
    victim.arrestMade === "yes"
      ? victim.arrestDate
        ? `Arrest date: ${fmtDate(victim.arrestDate)}`
        : "Arrest date not yet pinned down"
      : victim.arrestMade === "no"
        ? "No public arrest found"
        : "Public arrest status unknown";
  const sourceLabel = victim.arrestSourcePublisher
    ? `Source: ${victim.arrestSourcePublisher}`
    : victim.arrestSourceTitle
      ? "Source"
      : "";
  const sourceLine = victim.arrestSourceUrl
    ? `<a href="${escapeHtml(victim.arrestSourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(sourceLabel || "Source")}</a>`
    : sourceLabel
      ? escapeHtml(sourceLabel)
      : "";
  return [escapeHtml(dateLine), sourceLine].filter(Boolean).join(" · ");
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function renderSummary(data) {
  const s = data.summary;
  setText("heroRate", `${s.publicArrestRateVictimLevel}%`);
  setText("heroBasis", `${s.arrestReportedVictims} of ${s.victims} victim rows have a public arrest reported`);
  setText("metricVictims", s.victims);
  setText("metricIncidents", s.incidents);
  setText("metricArrests", s.arrestReportedVictims);
  setText("metricUnresolved", s.noPublicArrestVictims + s.unknownArrestStatusVictims);
  setText(
    "scopeNote",
    "This tracker focuses on homicides where the ordinary public question is whether police made an arrest. Fatal police shootings are handled through a different public accountability process, so they are left out of this arrest-rate count.",
  );
  setText("lastChecked", data.metadata.lastChecked || "unknown");
}

function svg(width, height, inner) {
  return `<svg viewBox="0 0 ${width} ${height}" role="img" aria-hidden="false">${inner}</svg>`;
}

function linePath(points) {
  return points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
}

function renderCumulativeChart(data) {
  const rows = data.cumulative;
  const width = 780;
  const height = 385;
  const pad = { top: 54, right: 28, bottom: 48, left: 44 };
  const dates = rows.map((r) => new Date(`${r.date}T00:00:00`));
  const minDate = dates[0];
  const maxDate = dates[dates.length - 1];
  const maxY = Math.max(...rows.map((r) => r.victims), 1);
  const span = Math.max(maxDate - minDate, 1);
  const x = (date) => pad.left + ((date - minDate) / span) * (width - pad.left - pad.right);
  const y = (value) => height - pad.bottom - (value / maxY) * (height - pad.top - pad.bottom);
  const victimPoints = rows.map((r) => ({ x: x(new Date(`${r.date}T00:00:00`)), y: y(r.victims) }));
  const arrestPoints = rows.map((r) => ({
    x: x(new Date(`${r.date}T00:00:00`)),
    y: y(r.arrestReportedVictims),
  }));
  const ticks = [0, Math.ceil(maxY / 2), maxY];
  const monthLabels = [...new Set(rows.map((r) => r.date.slice(0, 7)))];

  const grid = ticks
    .map(
      (tick) =>
        `<line x1="${pad.left}" x2="${width - pad.right}" y1="${y(tick)}" y2="${y(tick)}" stroke="${COLORS.line}" />
         <text x="${pad.left - 10}" y="${y(tick) + 4}" text-anchor="end" class="axis">${tick}</text>`,
    )
    .join("");

  const labels = monthLabels
    .map((m) => {
      const lx = x(new Date(`${m}-01T00:00:00`));
      return `<text x="${lx}" y="${height - 18}" text-anchor="middle" class="axis">${fmtMonth(m)}</text>`;
    })
    .join("");

  const points = rows
    .map((r) => {
      const cx = x(new Date(`${r.date}T00:00:00`));
      return `<circle cx="${cx}" cy="${y(r.victims)}" r="3.2" fill="${COLORS.victims}" />`;
    })
    .join("");

  document.getElementById("cumulativeChart").innerHTML = svg(
    width,
    height,
    `<g aria-label="Legend">
       <line x1="${pad.left}" x2="${pad.left + 34}" y1="20" y2="20" stroke="${COLORS.victims}" stroke-width="4" />
       <text x="${pad.left + 44}" y="24" class="chart-label">Total homicide victims tracked</text>
       <line x1="${pad.left + 260}" x2="${pad.left + 294}" y1="20" y2="20" stroke="${COLORS.yes}" stroke-width="4" />
       <text x="${pad.left + 304}" y="24" class="chart-label">Victims with public arrest reported</text>
     </g>
     ${grid}
     <path d="${linePath(victimPoints)}" fill="none" stroke="${COLORS.victims}" stroke-width="4" />
     <path d="${linePath(arrestPoints)}" fill="none" stroke="${COLORS.yes}" stroke-width="4" />
     ${points}
     ${labels}`,
  );
}

function renderStatusChart(data) {
  const values = [
    { key: "yes", value: data.statusCounts.yes || 0 },
    { key: "no", value: data.statusCounts.no || 0 },
    { key: "unknown", value: data.statusCounts.unknown || 0 },
  ];
  const total = values.reduce((sum, d) => sum + d.value, 0);
  const width = 360;
  const height = 245;
  let x = 20;
  const barY = 74;
  const barH = 38;
  const barW = width - 40;
  const segments = values
    .map((d) => {
      const w = total ? (d.value / total) * barW : 0;
      const out = `<rect x="${x}" y="${barY}" width="${w}" height="${barH}" fill="${COLORS[d.key]}" />`;
      x += w;
      return out;
    })
    .join("");
  const legend = values
    .map((d, i) => {
      const y = 145 + i * 28;
      return `<rect x="22" y="${y - 12}" width="14" height="14" fill="${COLORS[d.key]}" />
              <text x="44" y="${y}" class="chart-label">${statusLabel(d.key)}: ${d.value}</text>`;
    })
    .join("");

  document.getElementById("statusChart").innerHTML = svg(
    width,
    height,
    `<text x="20" y="34" font-size="32" font-weight="800" fill="${COLORS.victims}">${data.summary.publicArrestRateVictimLevel}%</text>
     <text x="20" y="56" class="chart-label">victim-level public arrest proxy</text>
     ${segments}
     ${legend}`,
  );
}

function renderMonthlyChart(data) {
  const rows = data.byMonth;
  const width = 360;
  const height = 245;
  const pad = { top: 18, right: 16, bottom: 34, left: 34 };
  const max = Math.max(...rows.map((r) => r.total), 1);
  const gap = 14;
  const barW = (width - pad.left - pad.right - gap * (rows.length - 1)) / rows.length;
  const y = (value) => height - pad.bottom - (value / max) * (height - pad.top - pad.bottom);
  const bars = rows
    .map((row, i) => {
      const bx = pad.left + i * (barW + gap);
      let currentY = height - pad.bottom;
      const pieces = ["yes", "no", "unknown"]
        .map((key) => {
          const h = ((row[key] || 0) / max) * (height - pad.top - pad.bottom);
          currentY -= h;
          return `<rect x="${bx}" y="${currentY}" width="${barW}" height="${h}" fill="${COLORS[key]}" />`;
        })
        .join("");
      return `${pieces}
        <text x="${bx + barW / 2}" y="${height - 12}" text-anchor="middle" class="axis">${fmtMonth(row.month)}</text>
        <text x="${bx + barW / 2}" y="${y(row.total) - 6}" text-anchor="middle" class="axis">${row.total}</text>`;
    })
    .join("");

  document.getElementById("monthlyChart").innerHTML = svg(
    width,
    height,
    `<line x1="${pad.left}" x2="${width - pad.right}" y1="${height - pad.bottom}" y2="${height - pad.bottom}" stroke="${COLORS.line}" />
     ${bars}`,
  );
}

function renderVictims(data, filter = "") {
  const needle = filter.trim().toLowerCase();
  const searchableFields = (victim) =>
    [
      victim.name,
      victim.location,
      victim.neighborhood,
      victim.method,
      victim.caseNumber,
      victim.arrestMade,
      victim.clearanceStatus,
      victim.publicChargeSummary,
      victim.circumstancesSummary,
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
  const rows = data.victims.filter((victim) => searchableFields(victim).includes(needle));
  document.getElementById("victimRows").innerHTML = rows
    .map((victim) => {
      const race = victim.raceEthnicity ? `<div class="subtext">${escapeHtml(victim.raceEthnicity)}</div>` : "";
      return `<tr>
        <td>${fmtTableDate(victim.incidentDate)}<div class="subtext">${escapeHtml(victim.incidentTime || "")}</div></td>
        <td><div class="name">${escapeHtml(victim.name)}</div><div class="subtext">${escapeHtml([victim.age, victim.gender].filter(Boolean).join(", "))}</div>${race}</td>
        <td class="location-cell">${escapeHtml(victim.location)}<div class="subtext">${escapeHtml(victim.neighborhood || victim.method || "")}</div></td>
        <td>${escapeHtml(victim.caseNumber || "unknown")}</td>
        <td><span class="pill ${statusClass(victim.arrestMade)}">${statusLabel(victim.arrestMade)}</span><div class="microtext">${arrestDetail(victim)} · ${escapeHtml(victim.confidence)} confidence</div></td>
        <td>${escapeHtml(victim.publicChargeSummary || "Status pending")}<div class="subtext">${escapeHtml(victim.caseStatus || "")}</div></td>
        <td>${escapeHtml(victim.circumstancesSummary || "Summary pending.")}</td>
      </tr>`;
    })
    .join("");
}

function renderCountReports(data) {
  const reports = data.countReports.slice(-4).reverse();
  document.getElementById("countReports").innerHTML = reports
    .map(
      (report) => {
        const publisher = escapeHtml(report.publisher);
        const publisherLink = report.url
          ? `<a href="${escapeHtml(report.url)}" target="_blank" rel="noopener noreferrer">${publisher}</a>`
          : publisher;
        return `<div class="count-item">
          <strong>${report.reportedTotal} reported through ${fmtDate(report.periodEnd)}</strong>
          <span>${publisherLink} · comparable tracker count: ${report.trackerVictimCount}</span>
          <div class="subtext">${escapeHtml(report.discrepancy)}</div>
        </div>`;
      },
    )
    .join("");
}

function render(data) {
  currentData = data;
  renderSummary(data);
  renderCumulativeChart(data);
  renderStatusChart(data);
  renderMonthlyChart(data);
  renderVictims(data);
  renderCountReports(data);
}

async function init() {
  const response = await fetch(DATA_URL);
  if (!response.ok) throw new Error(`Failed to load ${DATA_URL}`);
  const data = await response.json();
  render(data);
  document.getElementById("caseFilter").addEventListener("input", (event) => {
    renderVictims(currentData, event.target.value);
  });
}

init().catch((error) => {
  document.body.innerHTML = `<main class="error"><h1>Data failed to load</h1><p>${escapeHtml(error.message)}</p></main>`;
});
