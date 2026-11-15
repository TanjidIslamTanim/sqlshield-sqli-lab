"use strict";
const findingKeys = [
  "injection_effect_observed", "both_authenticated",
  "no_bypass_observed", "vulnerable_query_error",
];
const findingLabels = {
  injection_effect_observed: "Injection effect observed",
  both_authenticated: "Both authenticated",
  no_bypass_observed: "No bypass observed",
  vulnerable_query_error: "Unsafe query error",
};
const findingColors = {
  injection_effect_observed: "#ef9a7e",
  both_authenticated: "#46cce0",
  no_bypass_observed: "#35deb1",
  vulnerable_query_error: "#edc178",
};
const statusLabels = { authenticated: "MATCHED", rejected: "REJECTED", query_error: "QUERY ERROR" };

function setText(id, value) {
  document.getElementById(id).textContent = String(value);
}
function setBar(id, value, denominator) {
  const percent = denominator > 0 ? (value / denominator) * 100 : 0;
  document.getElementById(id).style.width = `${Math.min(100, Math.max(0, percent))}%`;
}
function renderStats(stats) {
  setText("metric-total", stats.total);
  setText("metric-bypass", stats.bypass_observed);
  setText("metric-vulnerable", stats.vulnerable_matched);
  setText("metric-protected", stats.protected_rejected);
  for (const key of findingKeys) {
    // The API calls this finding bypass_observed; the UI uses its full label.
    const count = key === "injection_effect_observed"
      ? stats.bypass_observed
      : stats[key];
    setText(`count-${key}`, count);
    setBar(`bar-${key}`, count, stats.total);
  }
  setText("compare-vulnerable", stats.vulnerable_matched);
  setText("compare-protected", stats.protected_matched);
  setBar("bar-compare-vulnerable", stats.vulnerable_matched, stats.total);
  setBar("bar-compare-protected", stats.protected_matched, stats.total);
  setText("last-updated", stats.last_event_at ? "DATA AVAILABLE" : "AWAITING FIRST TEST");
}
function addCell(row, text, cssClass = "") {
  const cell = document.createElement("td");
  cell.textContent = text;
  if (cssClass) cell.className = cssClass;
  row.appendChild(cell);
  return cell;
}
function renderEvents(events) {
  const tbody = document.getElementById("events-body");
  tbody.replaceChildren();
  if (!events.length) {
    const row = document.createElement("tr");
    const cell = addCell(row, "No recorded comparisons yet. Run a test in the comparison lab.", "empty-events");
    cell.colSpan = 5;
    tbody.appendChild(row);
    return;
  }
  for (const event of events) {
    const row = document.createElement("tr");
    addCell(row, `#${event.id}`, "event-id");
    const time = new Date(event.created_at);
    addCell(row, Number.isNaN(time.getTime()) ? event.created_at : time.toLocaleString());
    addCell(row, findingLabels[event.finding] || "Other", `finding-${event.finding}`);
    addCell(row, statusLabels[event.vulnerable_status] || "OTHER", `status-${event.vulnerable_status}`);
    addCell(row, statusLabels[event.protected_status] || "OTHER", `status-${event.protected_status}`);
    tbody.appendChild(row);
  }
}
function renderTimeline(events) {
  const svg = document.getElementById("timeline-chart");
  svg.replaceChildren();
  const ns = "http://www.w3.org/2000/svg";
  const recent = events.slice(0, 24).reverse();
  if (!recent.length) {
    const empty = document.createElementNS(ns, "text");
    empty.setAttribute("x", "15"); empty.setAttribute("y", "43");
    empty.setAttribute("fill", "#8eacbd"); empty.setAttribute("font-size", "13");
    empty.textContent = "Run comparisons to populate the timeline.";
    svg.appendChild(empty);
    return;
  }
  const count = recent.length;
  const gap = 7;
  const barWidth = Math.min(20, (690 - (count - 1) * gap) / count);
  const totalWidth = count * barWidth + (count - 1) * gap;
  const offset = (720 - totalWidth) / 2;
  for (let index = 0; index < count; index += 1) {
    const event = recent[index];
    const bar = document.createElementNS(ns, "rect");
    bar.setAttribute("x", String(offset + index * (barWidth + gap)));
    bar.setAttribute("y", "16"); bar.setAttribute("width", String(barWidth));
    bar.setAttribute("height", "44"); bar.setAttribute("rx", "4");
    bar.setAttribute("fill", findingColors[event.finding] || "#8da6b4");
    bar.setAttribute("opacity", "0.95");
    const label = document.createElementNS(ns, "title");
    label.textContent = `Event #${event.id}: ${findingLabels[event.finding] || "Other"}`;
    bar.appendChild(label);
    svg.appendChild(bar);
  }
}
async function loadDashboard() {
  const refresh = document.getElementById("refresh-btn");
  const message = document.getElementById("load-message");
  refresh.disabled = true;
  message.textContent = "Loading local event history…";
  message.classList.remove("error");
  try {
    const [statsResponse, eventsResponse] = await Promise.all([
      fetch("/api/stats", { cache: "no-store" }),
      fetch("/api/events?limit=50", { cache: "no-store" }),
    ]);
    if (!statsResponse.ok || !eventsResponse.ok) throw new Error("Could not load local event data.");
    const stats = await statsResponse.json();
    const data = await eventsResponse.json();
    renderStats(stats);
    renderEvents(data.events);
    renderTimeline(data.events);
    message.textContent = `Loaded ${stats.total} recorded comparison${stats.total === 1 ? "" : "s"}.`;
  } catch (error) {
    message.classList.add("error");
    message.textContent = `${error.message} Check that the Flask server is running and refresh.`;
  } finally {
    refresh.disabled = false;
  }
}
document.getElementById("refresh-btn").addEventListener("click", loadDashboard);
loadDashboard();
