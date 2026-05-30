"use strict";

/* ---- theme toggle (ported verbatim from paper-base, key renamed) ---- */
const themeToggle = document.querySelector(".theme-toggle");
const themeButtons = themeToggle.querySelectorAll("button[data-mode]");
const prefersDarkMQ = window.matchMedia("(prefers-color-scheme: dark)");
let themeMode = localStorage.getItem("phyra-dualtrans-theme") || "system";

function resolveActual(mode) {
  if (mode === "system") return prefersDarkMQ.matches ? "dark" : "light";
  return mode;
}
function applyTheme(mode) {
  themeMode = mode;
  document.documentElement.setAttribute("data-theme", resolveActual(mode));
  themeButtons.forEach(b => b.setAttribute("aria-pressed", b.dataset.mode === mode));
  localStorage.setItem("phyra-dualtrans-theme", mode);
}
themeButtons.forEach(b => b.addEventListener("click", () => applyTheme(b.dataset.mode)));
prefersDarkMQ.addEventListener?.("change", () => { if (themeMode === "system") applyTheme("system"); });
applyTheme(themeMode);

/* ---- helpers ---- */
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
function fmtBytes(n) {
  if (!n) return "0 B";
  const u = ["B", "KB", "MB", "GB"]; let i = 0;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return n.toFixed(1) + " " + u[i];
}

/* ---- state ---- */
let pickedFile = null;
let compressMode = "lossy";
const sources = new Map();   // jobId -> EventSource
let archbase = { enabled: false, port: 8037 };   // phyra-archbase integration

/* ---- input zone ---- */
const dz = $("dropzone");
dz.addEventListener("click", () => $("file").click());
$("file").addEventListener("change", e => setFile(e.target.files[0]));
["dragover", "dragenter"].forEach(ev =>
  dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.add("drag"); }));
["dragleave", "drop"].forEach(ev =>
  dz.addEventListener(ev, e => { e.preventDefault(); dz.classList.remove("drag"); }));
dz.addEventListener("drop", e => {
  if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
});
function setFile(f) {
  if (!f) return;
  pickedFile = f;
  $("file-name").textContent = f.name + " (" + fmtBytes(f.size) + ")";
  $("arxiv").value = "";
}
$("arxiv").addEventListener("input", () => {
  if ($("arxiv").value.trim()) { pickedFile = null; $("file-name").textContent = ""; $("file").value = ""; }
});

/* ---- compression segmented ---- */
$("compress").querySelectorAll("button").forEach(b =>
  b.addEventListener("click", () => {
    compressMode = b.dataset.v;
    $("compress").querySelectorAll("button").forEach(x =>
      x.setAttribute("aria-pressed", x === b));
    $("wrap-dpi").style.display = compressMode === "lossy" ? "" : "none";
  }));

/* ---- backend select ---- */
async function loadBackends() {
  const list = await (await fetch("/api/backends")).json();
  const sel = $("backend");
  sel.innerHTML = "";
  for (const b of list) {
    const o = document.createElement("option");
    o.value = b.kind; o.textContent = b.label;
    o.dataset.needs = (b.needs || []).join(",");
    o.dataset.defaultModel = b.default_model || "";
    o.dataset.needsPassword = b.needs_password ? "1" : "";
    sel.appendChild(o);
  }
  sel.addEventListener("change", onBackendChange);
}
function onBackendChange() {
  const sel = $("backend");
  const kind = sel.value;
  const isOpenAI = kind === "openai";
  const isOllama = kind === "ollama";
  const opt = sel.selectedOptions[0];
  // any gated backend (ollama / claude_cli when a password is set);
  // openai is never gated so its needs_password is false
  const needsPw = !!opt && opt.dataset.needsPassword === "1";
  $("wrap-base-url").style.display = (isOpenAI || isOllama) ? "" : "none";
  $("wrap-api-key").style.display = isOpenAI ? "" : "none";
  $("list-models").style.display = isOllama ? "" : "none";
  $("wrap-admin-pw").style.display = needsPw ? "" : "none";
  $("wrap-think").style.display = isOllama ? "" : "none";
  if (kind === "claude_cli" && !$("model").value) $("model").value = "sonnet";
  if (typeof loadRuntime === "function") loadRuntime();
}

$("list-models").addEventListener("click", async () => {
  const host = $("base-url").value.trim() || undefined;
  const q = host ? "?host=" + encodeURIComponent(host) : "";
  const r = await (await fetch("/api/backends/ollama/models" + q)).json();
  const dl = $("model-list"); dl.innerHTML = "";
  if (!r.available) { alert(r.reason || "Ollama not reachable"); return; }
  for (const m of r.models) {
    const o = document.createElement("option"); o.value = m; dl.appendChild(o);
  }
  if (r.models.length && !$("model").value) $("model").value = r.models[0];
});

/* ---- settings (per-user, browser-local) ----
   Preferences live in THIS browser only. The server has no auth and may
   be LAN-exposed, so it keeps no shared settings file: nothing here is
   sent to or stored on the server, and the API key is never persisted
   anywhere — it is typed per session and sent only with that request. */
const PREFS_KEY = "phyra-dualtrans-prefs";

async function loadSettings() {
  // built-in defaults (read-only, non-secret) overlaid with this
  // browser's saved preferences
  let builtin = {};
  try { builtin = await (await fetch("/api/settings")).json(); } catch (_) {}
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(PREFS_KEY) || "{}"); } catch (_) {}
  const s = { ...builtin, ...saved };

  $("backend").value = s.backend || "ollama";
  $("model").value = s.model || "qwen3-32b-trans";
  $("base-url").value = s.base_url || "";
  $("api-key").value = "";
  $("api-key").placeholder = "API key — sent per request, never stored";
  $("lang-in").value = s.lang_in || "en";
  $("lang-out").value = s.lang_out || "zh-TW";
  $("qps").value = s.qps || 2;
  $("mono").checked = !!s.mono;
  $("compat").checked = !!s.compat;
  $("distill").checked = !!s.distill;
  $("think-mode").checked = !!s.think;
  $("dpi").value = s.dpi || 150;
  $("preset").value = s.preset || "ebook";
  compressMode = s.compress || "lossy";
  $("compress").querySelectorAll("button").forEach(x =>
    x.setAttribute("aria-pressed", x.dataset.v === compressMode));
  $("wrap-dpi").style.display = compressMode === "lossy" ? "" : "none";
  onBackendChange();
}
$("save-defaults").addEventListener("click", () => {
  const body = collect();
  delete body._file;
  delete body.api_key;          // never persist the key, even locally
  localStorage.setItem(PREFS_KEY, JSON.stringify(body));
  alert("Saved in this browser (not shared, not sent to the server).");
});

function collect() {
  return {
    backend: $("backend").value,
    model: $("model").value.trim(),
    base_url: $("base-url").value.trim(),
    api_key: $("api-key").value,            // "" = keep saved
    lang_in: $("lang-in").value.trim() || "en",
    lang_out: $("lang-out").value.trim() || "zh-TW",
    qps: parseInt($("qps").value, 10) || 2,
    compat: $("compat").checked,
    compress: compressMode,
    dpi: parseInt($("dpi").value, 10) || 150,
    preset: $("preset").value,
    mono: $("mono").checked,
    distill: $("distill").checked,
    think: $("think-mode").checked,
  };
}

/* ---- preflight ---- */
$("preflight").addEventListener("click", async () => {
  const c = collect();
  const q = new URLSearchParams({ backend: c.backend, lang_out: c.lang_out,
    compress: c.compress, base_url: c.base_url || "" });
  const r = await (await fetch("/api/preflight?" + q)).json();
  const ul = $("checks"); ul.innerHTML = "";
  for (const ck of r.checks) {
    const li = document.createElement("li");
    li.innerHTML = `<span class="${ck.ok ? "ok" : "bad"}">${ck.ok ? "✓" : "✗"}</span> `
      + `<b>${esc(ck.name)}</b> — ${esc(ck.detail || "")}`;
    ul.appendChild(li);
    if (!ck.ok && ck.hint) {
      const h = document.createElement("li");
      h.className = "hint"; h.textContent = "→ " + ck.hint;
      ul.appendChild(h);
    }
  }
  const head = document.createElement("li");
  head.className = r.ok ? "ok" : "bad";
  head.textContent = r.ok ? "preflight OK" : "preflight FAILED";
  ul.prepend(head);
});

/* ---- translate ---- */
$("translate").addEventListener("click", async () => {
  const c = collect();
  const fd = new FormData();
  if (pickedFile) fd.append("file", pickedFile);
  else if ($("arxiv").value.trim()) fd.append("arxiv", $("arxiv").value.trim());
  else { alert("Choose a PDF or enter an arXiv URL / id."); return; }

  fd.append("lang_in", c.lang_in);
  fd.append("lang_out", c.lang_out);
  fd.append("qps", c.qps);
  fd.append("compat", c.compat);
  fd.append("compress", c.compress);
  fd.append("dpi", c.dpi);
  fd.append("preset", c.preset);
  fd.append("mono", c.mono);
  fd.append("distill", c.distill);
  fd.append("backend", JSON.stringify({
    kind: c.backend, model: c.model,
    base_url: c.base_url || null, api_key: c.api_key || null,
    think: c.think,
  }));
  fd.append("admin_password", $("admin-pw").value);

  $("translate").disabled = true;
  try {
    const r = await fetch("/api/translate", { method: "POST", body: fd });
    if (r.status === 401) {
      alert("管理員密碼錯誤或未填 — 此後端(ollama / Claude CLI)需要密碼。");
      $("admin-pw").value = ""; $("admin-pw").focus();
      return;
    }
    if (!r.ok) { alert("Error: " + (await r.text())); return; }
    const { job_id } = await r.json();
    await refreshJobs();
    subscribe(job_id);
  } finally {
    $("translate").disabled = false;
  }
});

/* ---- tabs (Single / Batch) ---- */
document.querySelectorAll(".tabs .tab").forEach(t =>
  t.addEventListener("click", () => {
    document.querySelectorAll(".tabs .tab").forEach(x =>
      x.setAttribute("aria-selected", x === t));
    const batch = t.dataset.tab === "batch";
    $("card-single").style.display = batch ? "none" : "";
    $("card-batch").style.display = batch ? "" : "none";
  }));

/* ---- batch input ---- */
let batchFiles = [];
const dzb = $("dropzone-b");
dzb.addEventListener("click", () => $("file-b").click());
$("file-b").addEventListener("change", e => addBatchFiles(e.target.files));
["dragover", "dragenter"].forEach(ev =>
  dzb.addEventListener(ev, e => { e.preventDefault(); dzb.classList.add("drag"); }));
["dragleave", "drop"].forEach(ev =>
  dzb.addEventListener(ev, e => { e.preventDefault(); dzb.classList.remove("drag"); }));
dzb.addEventListener("drop", e => {
  if (e.dataTransfer.files.length) addBatchFiles(e.dataTransfer.files);
});
function addBatchFiles(list) {
  for (const f of list) batchFiles.push(f);          // keep add order
  $("batch-files").textContent = batchFiles.length
    ? batchFiles.map((f, i) => `${i + 1}. ${f.name}`).join("  ·  ")
    : "";
}

$("translate-batch").addEventListener("click", async () => {
  const c = collect();
  const arxiv = $("arxiv-b").value.trim();
  if (!batchFiles.length && !arxiv) {
    alert("Add PDFs or arXiv links for the batch."); return;
  }
  const fd = new FormData();
  fd.append("lang_in", c.lang_in);
  fd.append("lang_out", c.lang_out);
  fd.append("qps", c.qps);
  fd.append("compat", c.compat);
  fd.append("compress", c.compress);
  fd.append("dpi", c.dpi);
  fd.append("preset", c.preset);
  fd.append("mono", c.mono);
  fd.append("distill", c.distill);
  fd.append("backend", JSON.stringify({
    kind: c.backend, model: c.model,
    base_url: c.base_url || null, api_key: c.api_key || null,
    think: c.think,
  }));
  fd.append("admin_password", $("admin-pw").value);
  for (const f of batchFiles) fd.append("file", f);   // order preserved
  if (arxiv) fd.append("arxiv", arxiv);

  $("translate-batch").disabled = true;
  try {
    const r = await fetch("/api/translate/batch", { method: "POST", body: fd });
    if (r.status === 401) {
      alert("管理員密碼錯誤或未填 — 此後端(ollama / Claude CLI)需要密碼。");
      $("admin-pw").value = ""; $("admin-pw").focus(); return;
    }
    if (!r.ok) { alert("Error: " + (await r.text())); return; }
    const { jobs } = await r.json();
    batchFiles = []; $("batch-files").textContent = ""; $("arxiv-b").value = "";
    await refreshJobs();
    for (const j of jobs) subscribe(j.job_id);
  } finally {
    $("translate-batch").disabled = false;
  }
});

/* ---- jobs ---- */
function fmtDur(sec) {
  sec = Math.max(0, Math.round(sec));
  const h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60),
        s = sec % 60;
  return h ? `${h}h ${m}m ${s}s` : (m ? `${m}m ${s}s` : `${s}s`);
}
function fmtTime(epoch) {
  // absolute local timestamp; drop the date when it's today
  const d = new Date(epoch * 1000);
  const t = d.toLocaleTimeString();
  const today = new Date();
  const sameDay = d.toDateString() === today.toDateString();
  return sameDay ? t : `${d.toLocaleDateString()} ${t}`;
}

function jobCard(j) {
  const pct = (j.progress && j.progress.overall_pct) || 0;
  const out = j.outputs || {};
  const term = ["succeeded", "failed", "canceled"].includes(j.status);
  // start time + running/total elapsed
  let dur = "";
  if (j.started_at) {
    const end = (term && j.finished_at) ? j.finished_at : Date.now() / 1000;
    const verb = term ? "total" : "elapsed";
    dur = `<span class="job-start" title="processing start time">🕒 ${esc(fmtTime(j.started_at))}</span>`
        + `<span class="job-dur" data-elapsed data-started="${j.started_at}"`
        + ` data-fixed="${term && j.finished_at ? 1 : ''}"`
        + ` title="processing time (start → ${term ? j.status : 'now'})">`
        + `⏱ ${verb} ${fmtDur(end - j.started_at)}</span>`;
  } else if (j.status === "queued") {
    dur = `<span class="job-dur" title="waiting in queue">⏱ queued</span>`;
  }
  // outputs open INLINE in a new browser tab (view, not forced download).
  // order: 📑 原文 → 🌐 雙語 → 📄 Mono (then archive / delete in ctrl)
  const dl = [];
  if (out.original) dl.push(`<a href="/api/jobs/${j.id}/download?kind=original&inline=1" target="_blank" rel="noopener">📑 原文 PDF</a>`);
  if (out.dual) dl.push(`<a href="/api/jobs/${j.id}/download?kind=dual&inline=1" target="_blank" rel="noopener">🌐 雙語 PDF</a>`);
  if (out.mono) dl.push(`<a href="/api/jobs/${j.id}/download?kind=mono&inline=1" target="_blank" rel="noopener">📄 Mono PDF</a>`);
  const ctrl = [];
  if (j.status === "running" || j.status === "queued")
    ctrl.push(`<button data-cancel="${j.id}">Cancel</button>`);
  // save the original + dual into phyra-archbase (only when reachable and
  // both PDFs exist on this job). j.archived flags an already-saved job —
  // the button stays clickable (re-save overwrites) but shows it's done.
  if (j.status === "succeeded" && archbase.enabled && out.dual && out.original)
    ctrl.push(j.archived
      ? `<button data-archive="${j.id}" data-stem="${esc(j.stem || "")}" class="archived" title="已存入論文庫；可再次存入覆蓋">✓ 已入庫（可重存）</button>`
      : `<button data-archive="${j.id}" data-stem="${esc(j.stem || "")}">📥 存入 archbase</button>`);
  if (term)
    ctrl.push(`<button data-del="${j.id}">🗑 Delete</button>`);
  let note = "";
  if (j.error) note = `<div class="job-meta" style="color:var(--p-accent)">${esc(j.error)}</div>`;
  // progress bar + live stage line only while active; history items omit them
  const progress = term ? "" :
    `<div class="bar"><i style="width:${pct}%"></i></div>
    <div class="job-meta" data-stage>${esc((j.progress && j.progress.stage) || "")} ${pct ? pct + "%" : ""}</div>`;
  return `<div class="job" id="job-${j.id}">
    <div class="job-top">
      <span class="badge ${j.status}">${j.status}</span>
      <span class="job-stem">${esc(j.stem || j.id)}</span>
      ${dur}
    </div>
    ${progress}
    ${note}
    <div class="actions">${dl.join("")}${ctrl.join("")}</div>
  </div>`;
}

let jobDetails = [];     // detailed JobView objects (newest-first, as the API returns)
let jobLimit = 20;       // 20 | 50 | Infinity — how many cards to show
let jobQuery = "";       // filename (stem) filter

async function refreshJobs() {
  const list = await (await fetch("/api/jobs")).json();
  if (!list.length) {
    jobDetails = [];
    $("jobs").innerHTML = '<div class="empty">No jobs yet.</div>';
    return;
  }
  const full = [];
  for (const j of list) {
    full.push(await (await fetch("/api/jobs/" + j.id)).json());
  }
  jobDetails = full;
  renderJobsList();
  // resubscribe to anything still active
  for (const j of list) {
    if ((j.status === "running" || j.status === "queued") && !sources.has(j.id))
      subscribe(j.id);
  }
}

// render jobDetails through the filename search + show-count limit. Called by
// refreshJobs and directly by the search / limit controls (no refetch).
function renderJobsList() {
  const root = $("jobs");
  if (!jobDetails.length) {
    root.innerHTML = '<div class="empty">No jobs yet.</div>';
    return;
  }
  const q = jobQuery.trim().toLowerCase();
  const matched = q
    ? jobDetails.filter(j => (j.stem || j.id || "").toLowerCase().includes(q))
    : jobDetails;
  if (!matched.length) {
    root.innerHTML = `<div class="empty">沒有符合「${esc(jobQuery)}」的任務。</div>`;
    return;
  }
  const shown = jobLimit === Infinity ? matched : matched.slice(0, jobLimit);
  let html = shown.map(jobCard).join("");
  if (matched.length > shown.length)
    html += `<div class="empty">顯示前 ${shown.length} / ${matched.length} 筆 — 調整右上「顯示」或用搜尋縮小範圍。</div>`;
  root.innerHTML = html;
  bindJobButtons();
}

function renderCard(j) {
  // replace a single job card in place (used on SSE stage transitions so
  // new outputs — e.g. the original PDF — and status surface immediately)
  const el = $("job-" + j.id);
  if (!el) return;
  el.outerHTML = jobCard(j);
  bindJobButtons();
}

function bindJobButtons() {
  document.querySelectorAll("[data-cancel]").forEach(b =>
    b.onclick = async () => { await fetch(`/api/jobs/${b.dataset.cancel}/cancel`, { method: "POST" }); });
  document.querySelectorAll("[data-del]").forEach(b =>
    b.onclick = async () => {
      // guard against accidental clicks — deletion removes the workdir
      if (!confirm("確定刪除這個任務？此操作會移除伺服器上的譯文、原文 PDF 等所有檔案，且無法復原。"))
        return;
      sources.get(b.dataset.del)?.close(); sources.delete(b.dataset.del);
      await fetch("/api/jobs/" + b.dataset.del, { method: "DELETE" });
      refreshJobs();
    });
  document.querySelectorAll("[data-archive]").forEach(b =>
    b.onclick = () => openArchiveModal(b.dataset.archive, b));
}

/* ---- archive into phyra-archbase ---- */
function deTokenize(s) {  // mirror archbase filename_to_display
  return String(s || "").replace(/__/g, ": ").replace(/_/g, " ").trim();
}
function sanitizeTitleForStem(title) {  // mirror vendor.sanitize_title_for_stem
  return String(title || "").trim()
    .replace(/:\s+/g, "_")
    .replace(/[<>:"/\\|?*\x00-\x1f]/g, "_")
    .replace(/\s+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
}

async function openArchiveModal(jobId, btn) {
  // ask the server for a prefill (it splits the stem the same way the
  // archive itself will); fall back to a client-side guess on failure
  let s = {};
  try { s = await (await fetch(`/api/jobs/${jobId}/archive/suggest`)).json(); }
  catch (_) { s = { yymm: "", title: deTokenize(btn.dataset.stem) }; }
  if (!s.yymm) {
    const d = new Date();
    s.yymm = String(d.getFullYear()).slice(2) + String(d.getMonth() + 1).padStart(2, "0");
  }

  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal" role="dialog" aria-modal="true">
      <h3>存入 phyra-archbase</h3>
      <p class="modal-sub">確認檔名後存入論文庫（原文 PDF + 雙語 PDF）。</p>
      <div class="modal-row yymm">
        <label for="ar-yymm">YYMM（年月，4 碼）</label>
        <input id="ar-yymm" type="text" maxlength="4" inputmode="numeric" value="${esc(s.yymm)}">
      </div>
      <div class="modal-row">
        <label for="ar-title">標題</label>
        <input id="ar-title" type="text" value="${esc(s.title || "")}">
      </div>
      <div class="modal-preview" id="ar-preview"></div>
      <div class="modal-actions">
        <button type="button" class="btn ghost" id="ar-cancel">取消</button>
        <button type="button" class="btn" id="ar-ok">存入</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);

  const elY = overlay.querySelector("#ar-yymm");
  const elT = overlay.querySelector("#ar-title");
  const elP = overlay.querySelector("#ar-preview");
  const close = () => overlay.remove();
  const updatePreview = () => {
    const stem = `${elY.value.trim()}_${sanitizeTitleForStem(elT.value)}`;
    elP.innerHTML = `檔名：<code>${esc(stem)}.pdf</code> · <code>${esc(stem)}_bilingual.…dual.pdf</code>`;
  };
  elY.addEventListener("input", updatePreview);
  elT.addEventListener("input", updatePreview);
  updatePreview();
  elT.focus();

  overlay.addEventListener("click", e => { if (e.target === overlay) close(); });
  overlay.querySelector("#ar-cancel").onclick = close;
  overlay.querySelector("#ar-ok").onclick = async () => {
    const yymm = elY.value.trim(), title = elT.value.trim();
    if (!/^\d{4}$/.test(yymm)) { alert("YYMM 需為 4 位數字（例如 2402）。"); elY.focus(); return; }
    if (!title) { alert("請填標題。"); elT.focus(); return; }
    const okBtn = overlay.querySelector("#ar-ok");
    okBtn.disabled = true; okBtn.textContent = "存入中…";
    const fd = new FormData();
    fd.append("yymm", yymm); fd.append("title", title);
    try {
      const r = await fetch(`/api/jobs/${jobId}/archive`, { method: "POST", body: fd });
      if (!r.ok) { alert("存入失敗：" + (await r.text())); return; }
      const res = await r.json();
      close();
      if (btn) {
        // keep it clickable so the user can re-save after editing the paper;
        // the green "archived" look mirrors what a page refresh would show.
        btn.textContent = res.index_ok ? "✓ 已入庫（可重存）" : "✓ 已存（索引待重整）";
        btn.classList.add("archived");
      }
    } finally {
      okBtn.disabled = false; okBtn.textContent = "存入";
    }
  };
}

function subscribe(jobId) {
  if (sources.has(jobId)) return;
  const es = new EventSource(`/api/jobs/${jobId}/events`);
  sources.set(jobId, es);
  const onAny = async (ev) => {
    let d = {};
    try { d = JSON.parse(ev.data); } catch (_) { return; }
    const card = $("job-" + jobId);
    if (!card) {
      // card not in the DOM: refresh only for a job we don't know yet —
      // a known job hidden by the search/limit filter must NOT trigger a
      // refetch on every progress tick.
      if (!jobDetails.some(j => j.id === jobId)) await refreshJobs();
      return;
    }
    const t = d.type;
    if (t === "progress" || t === "snapshot") {
      const p = d.progress || d;
      const pct = p.overall_pct || 0;
      const barI = card.querySelector(".bar > i");
      if (barI) barI.style.width = pct + "%";
      const stg = card.querySelector("[data-stage]");
      if (stg) stg.textContent = (p.stage || "") + (pct ? " " + pct + "%" : "");
    } else if (t === "rate_limit") {
      const stg = card.querySelector("[data-stage]");
      if (stg) stg.textContent =
        `rate-limited — retry ${d.attempt}/${d.max_attempts}, waiting ${d.wait_sec}s`;
    } else if (t === "distill") {
      const m = { start: "distilling translation guide…",
        done: "translation guide ready", skipped: "distillation skipped" };
      const stg = card.querySelector("[data-stage]");
      if (stg) stg.textContent = m[d.stage] || "distilling…";
    } else if (t === "status" || t === "stage_end" || t === "chunk_fallback") {
      // re-render the card so new outputs (e.g. the original PDF, exposed
      // at the input stage) and the fresh status surface right away
      const j = await (await fetch("/api/jobs/" + jobId)).json();
      renderCard(j);
    } else if (t === "done" || t === "error" || t === "canceled") {
      es.close(); sources.delete(jobId);
      await refreshJobs();
    }
  };
  ["snapshot", "status", "progress", "rate_limit", "chunk_fallback",
   "distill", "stage_end", "done", "error", "canceled", "message"].forEach(
    name => es.addEventListener(name, onAny));
  es.onerror = () => { /* browser auto-reconnects; snapshot replays state */ };
}

/* live-tick the processing time of running jobs (terminal ones are
   fixed via data-fixed and left untouched) */
setInterval(() => {
  document.querySelectorAll(".job-dur[data-elapsed]").forEach(el => {
    if (el.dataset.fixed) return;
    const st = parseFloat(el.dataset.started);
    if (st) el.textContent = "⏱ elapsed " + fmtDur(Date.now() / 1000 - st);
  });
}, 1000);

/* ---- jobs list controls (filename search + show-count) ---- */
$("job-search").addEventListener("input", e => {
  jobQuery = e.target.value;
  renderJobsList();
});
$("job-limit").addEventListener("change", e => {
  jobLimit = e.target.value === "all" ? Infinity : (parseInt(e.target.value, 10) || 20);
  renderJobsList();
});

/* ---- runtime / GPU status (under Options) ----
   Surfaces the silent slow-down: a crashed GPU driver makes nvidia-smi
   fail and Ollama falls back to CPU (~10× slower, no error). When the
   ollama backend is selected we probe its Base URL; otherwise the server
   probes the managed Ollama. */
async function loadRuntime() {
  const el = $("runtime-status");
  if (!el) return;
  let host = "";
  if ($("backend").value === "ollama") host = $("base-url").value.trim();
  const q = host ? "?host=" + encodeURIComponent(host) : "";
  try {
    const r = await (await fetch("/api/runtime" + q)).json();
    el.textContent = r.summary || "未知";
    el.dataset.level = r.level || "";
    el.title = r.detail || "";
  } catch (_) {
    el.textContent = "狀態查詢失敗";
    el.dataset.level = "warn";
    el.title = "";
  }
}
$("runtime-refresh").addEventListener("click", loadRuntime);
// re-probe ~30s so a mid-session driver crash / CPU fallback gets noticed
setInterval(loadRuntime, 30000);

/* ---- phyra-archbase capability (gates the "存入 archbase" job button) ---- */
async function loadArchbase() {
  try { archbase = await (await fetch("/api/archbase")).json(); }
  catch (_) { archbase = { enabled: false, port: 8037 }; }
}

/* ---- "🜂 返回 Phyra Center" banner ----
 * Always visible (mirrors archbase's baked-in banner). The href is built
 * from THIS browser's hostname + the configured Center port (from our own
 * same-origin /api/center, so no CORS), so LAN access works. We don't
 * cross-origin probe Center's /healthz — that gets blocked by CORS on
 * Center's stdlib server, which was making the banner disappear. */
async function loadCenter() {
  const link = $("center-link");
  if (!link) return;
  let port = 8035;
  try { port = (await (await fetch("/api/center")).json()).port || 8035; }
  catch (_) { /* keep default */ }
  link.href = `${location.protocol}//${location.hostname}:${port}/`;
}

/* ---- boot ---- */
(async function () {
  await loadBackends();
  await loadSettings();
  await loadArchbase();
  loadCenter();              // banner is best-effort, doesn't block boot
  await refreshJobs();
  loadRuntime();
})();
