"use strict";

const form = document.getElementById("compare-form");
const username = document.getElementById("username");
const secret = document.getElementById("demo-secret");
const runButton = document.getElementById("run-button");

const presets = {
  valid: { username: "alice", demo_secret: "DemoPass123!" },
  invalid: { username: "alice", demo_secret: "wrong-secret" },
  injection: { username: "' OR '1'='1' --", demo_secret: "anything" },
};

for (const button of document.querySelectorAll("[data-preset]")) {
  button.addEventListener("click", () => {
    const preset = presets[button.dataset.preset];
    if (!preset) return;
    username.value = preset.username;
    secret.value = preset.demo_secret;
    for (const other of document.querySelectorAll("[data-preset]")) {
      other.classList.toggle("selected", other === button);
    }
  });
}

function renderMode(mode, result) {
  const card = document.getElementById(`${mode}-card`);
  const pill = document.getElementById(`${mode}-status`);
  const title = document.getElementById(`${mode}-title`);
  const detail = document.getElementById(`${mode}-detail`);
  card.classList.remove("is-success", "is-rejected", "is-error");
  if (result.status === "authenticated") {
    card.classList.add("is-success");
    pill.textContent = "MATCHED";
    title.textContent = "Authentication succeeded";
    detail.textContent = `Matched fictional account: ${result.account} (${result.role}).`;
  } else if (result.status === "query_error") {
    card.classList.add("is-error");
    pill.textContent = "QUERY ERROR";
    title.textContent = "SQL statement failed";
    detail.textContent = result.message;
  } else {
    card.classList.add("is-rejected");
    pill.textContent = "REJECTED";
    title.textContent = "Authentication rejected";
    detail.textContent = result.message;
  }
}

function renderFinding(data) {
  const panel = document.getElementById("finding-panel");
  const title = document.getElementById("finding-title");
  const detail = document.getElementById("finding-detail");
  panel.classList.toggle("observed", data.finding === "injection_effect_observed");
  const headings = {
    injection_effect_observed: "SQL injection effect demonstrated",
    both_authenticated: "Valid demonstration credentials",
    vulnerable_query_error: "Unsafe query syntax error",
    no_bypass_observed: "No bypass observed",
  };
  title.textContent = headings[data.finding] || "Comparison completed";
  detail.textContent = data.explanation;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!username.value || !secret.value) {
    document.getElementById("finding-title").textContent = "Both fields are required";
    document.getElementById("finding-detail").textContent = "Choose a preset or enter fictional lab inputs.";
    return;
  }
  runButton.disabled = true;
  runButton.textContent = "Running...";
  try {
    const response = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.value, demo_secret: secret.value }),
      cache: "no-store",
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The local lab could not run the comparison.");
    renderMode("vulnerable", data.vulnerable);
    renderMode("protected", data.protected);
    renderFinding(data);
    // The server records only sanitized outcome labels, never submitted inputs.
    if (data.event_id) {
      document.getElementById("finding-detail").textContent += ` Recorded as lab event #${data.event_id}.`;
    }
  } catch (error) {
    document.getElementById("finding-title").textContent = "Comparison could not complete";
    document.getElementById("finding-detail").textContent = error.message;
  } finally {
    runButton.disabled = false;
    runButton.textContent = "Run comparison →";
  }
});
