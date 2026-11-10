export {};

/** Live workspace dashboard. Every state below comes from a server operation. */
type Directive = { id: string; name: string; label: string; source: string; category: string };
type Source = { id: string; kind: string; path: string; name: string };
type Dashboard = { directives: Directive[]; sources: Source[]; conversations: number; workspace: string; gmail: { email: string; verified_at: string } | null };
const element = <T extends HTMLElement = HTMLElement>(id: string): T => document.getElementById(id) as T;
const home = element("view-home");
const dialog = element<HTMLDialogElement>("hub-dialog");
let dashboard: Dashboard | undefined;
let refreshVersion = 0;

async function request<T>(path: string, method = "GET", body?: object): Promise<T> {
  const key = "chatos-token:" + location.origin;
  const token = localStorage.getItem(key) || sessionStorage.getItem(key) || "";
  const response = await fetch("/api/" + path, { method, headers: { "X-ChatOS-Token": token, "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Workspace request failed");
  return data as T;
}
function node<K extends keyof HTMLElementTagNameMap>(tag: K, text = "", className = ""): HTMLElementTagNameMap[K] {
  const result = document.createElement(tag);
  result.textContent = text;
  if (className) result.className = className;
  return result;
}
function button(text: string, action: () => Promise<void> | void, className = ""): HTMLButtonElement {
  const result = node("button", text, className);
  result.type = "button";
  result.addEventListener("click", () => void perform(action));
  return result;
}
async function perform(action: () => Promise<void> | void): Promise<void> {
  element("hub-error").hidden = true;
  try { await action(); } catch (error) {
    const message = error instanceof Error ? error.message : "Workspace operation failed";
    element("hub-error").textContent = message;
    element("hub-error").hidden = false;
    if (dialog.open) element("hub-dialog-message").textContent = message;
  }
}
function openDialog(title: string, kicker = "WORKSPACE"): HTMLElement {
  element("hub-dialog-heading").textContent = title;
  element("hub-dialog-kicker").textContent = kicker;
  element("hub-dialog-message").textContent = "";
  const body = element("hub-dialog-body");
  body.replaceChildren();
  if (!dialog.open) dialog.showModal();
  return body;
}
function pre(text: string): HTMLPreElement { return node("pre", text, "hub-source-text"); }

function renderDirectives(): void {
  if (!dashboard) return;
  const filter = element<HTMLInputElement>("hub-file-filter").value.toLowerCase();
  const groups = element("hub-file-groups");
  const expanded = new Set([...groups.querySelectorAll<HTMLDetailsElement>("details[open]")].map(item => item.dataset.category));
  const firstRender = !groups.querySelector("details");
  groups.replaceChildren();
  const categories = [["instructions", "Instruction files"], ["memory", "Memory files"], ["skills", "Skills & scripts"]];
  for (const [category, label] of categories) {
    const items = dashboard.directives.filter(item => item.category === category && `${item.label} ${item.source}`.toLowerCase().includes(filter));
    const details = node("details");
    details.dataset.category = category;
    details.open = Boolean(filter) || expanded.has(category) || firstRender;
    const summary = node("summary");
    summary.append(node("span", label), node("small", String(items.length)));
    details.append(summary);
    const list = node("div", "", "hub-file-list");
    for (const item of items) {
      const file = button("", async () => {
        const body = openDialog(item.label, "LIVE DIRECTIVE");
        element("hub-dialog-message").textContent = "Reading " + item.source;
        const result = await request<{ text: string; source: string; sha256: string; read_at: string }>("home/directive?" + new URLSearchParams({ id: item.id }));
        element("hub-dialog-message").textContent = result.source + " · Read " + new Date(result.read_at).toLocaleTimeString();
        body.append(pre(result.text), node("p", "SHA-256 · " + result.sha256, "hub-file-hash"));
      }, "hub-file");
      file.title = item.source;
      file.append(node("span", category === "skills" ? "‹/›" : "▤", "hub-file-symbol"), node("span", item.label));
      if (item.label !== item.name) file.append(node("small", item.name));
      list.append(file);
    }
    if (!items.length) list.append(node("p", filter ? "No matching files." : "No registered files in this category.", "hub-empty"));
    details.append(list);
    groups.append(details);
  }
  element("hub-file-count").textContent = `${dashboard.directives.length} available directive files`;
}
async function refresh(): Promise<void> {
  const version = ++refreshVersion;
  const data = await request<Dashboard>("home");
  if (version !== refreshVersion) return;
  dashboard = data;
  element("hub-system-status").replaceChildren(node("i"), document.createTextNode("Workspace online"));
  element("hub-workspace-label").textContent = data.workspace.split("/").slice(-2).join(" / ");
  element("hub-workspace-label").title = data.workspace;
  const git = data.sources.filter(item => item.kind === "git");
  const vaults = data.sources.filter(item => item.kind === "vault");
  element("hub-git-detail").textContent = git.length ? git.map(item => item.name).slice(0, 2).join(" · ") : "Mount a local repository";
  element("hub-git-count").textContent = String(git.length) + " LOCAL";
  element("hub-vault-detail").textContent = vaults.length ? vaults.map(item => item.name).slice(0, 2).join(" · ") : "Mount an Obsidian directory";
  element("hub-vault-count").textContent = String(vaults.length) + " VAULT";
  element("home-chat-count").textContent = `${data.conversations.toLocaleString()} captured conversations`;
  element("hub-gmail-detail").textContent = data.gmail ? data.gmail.email : "Connect an account to read your inbox";
  element("hub-gmail-state").textContent = data.gmail ? "OPEN ↗" : "CONNECT ↗";
  element("hub-gmail-dot").classList.toggle("connected", Boolean(data.gmail));
  renderDirectives();
}

async function browse(source: Source, path = ""): Promise<void> {
  const body = openDialog(source.name, source.kind === "git" ? "GIT REPOSITORY" : "OBSIDIAN VAULT");
  element("hub-dialog-message").textContent = source.path + (path ? "/" + path : "");
  const data = await request<{ kind: string; path: string; text?: string; items?: { name: string; path: string; directory: boolean }[]; total?: number }>("home/source?" + new URLSearchParams({ id: source.id, path }));
  if (path) body.append(button("← Parent directory", () => browse(source, path.split("/").slice(0, -1).join("/")), "hub-back"));
  if (data.kind === "file") body.append(pre(data.text || ""));
  else {
    const list = node("div", "", "hub-browser-list");
    for (const item of data.items || []) list.append(button(`${item.directory ? "▱" : "▤"}  ${item.name}${item.directory ? " /" : ""}`, () => browse(source, item.path)));
    if (!data.items?.length) list.append(node("p", "No visible text files in this directory.", "hub-empty"));
    body.append(list);
    if ((data.total || 0) > 300) body.append(node("p", "Showing the first 300 entries. Browse a subdirectory to narrow the list."));
  }
}
function showSources(kind: string): void {
  const body = openDialog(kind === "git" ? "Git repositories" : "Obsidian vaults", "GROUNDED SOURCES");
  const sources = dashboard?.sources.filter(item => item.kind === kind) || [];
  for (const source of sources) {
    const row = button("", () => browse(source), "hub-source-root");
    row.append(node("strong", source.name), node("small", source.path));
    body.append(row);
  }
  if (!sources.length) body.append(node("p", "No source directories are registered yet.", "hub-empty"));
  body.append(button("＋ Mount a directory", () => showMount(kind), "hub-primary"));
}
function showMount(initial = "git"): void {
  const body = openDialog("Mount a source or tool", "ADD CONNECTION");
  const form = node("form", "", "hub-mount-form");
  const label = node("label", "Connection type");
  const type = node("select");
  type.dataset.native = "true";
  for (const [value, text] of [["git", "Git repository"], ["vault", "Obsidian vault"], ["gmail", "Gmail API"]]) {
    const option = node("option", text); option.value = value; type.append(option);
  }
  type.value = initial;
  label.append(type);
  const pathLabel = node("label", "Absolute directory path");
  const path = node("input"); path.placeholder = "/absolute/path/to/source"; path.required = true; pathLabel.append(path);
  const copy = node("p", "Mounting makes this directory available in the source browser. Files stay in place.", "hub-empty");
  const submit = node("button", "Mount directory", "hub-primary"); submit.type = "submit";
  type.addEventListener("change", () => {
    const gmail = type.value === "gmail";
    pathLabel.hidden = gmail; path.required = !gmail;
    submit.textContent = gmail ? "Connect Gmail" : "Mount directory";
    copy.textContent = gmail ? "Connect an authorized Gmail account to read inbox metadata." : "Mounting makes this directory available in the source browser. Files stay in place.";
  });
  form.append(label, pathLabel, copy, submit);
  form.addEventListener("submit", event => {
    event.preventDefault();
    void perform(async () => {
      if (type.value === "gmail") { showGmailConnect(); return; }
      submit.disabled = true;
      try {
        const source = await request<Source>("home/source", "POST", { kind: type.value, path: path.value });
        await refresh(); await browse(source);
      } finally { submit.disabled = false; }
    });
  });
  body.append(form);
}
function showGmailConnect(): void {
  const body = openDialog("Connect Gmail", "GMAIL API · READ ACCESS");
  body.append(node("p", "Provide a Google OAuth access token authorized for gmail.readonly. It is sent only to Google's Gmail API and kept in server memory until you disconnect or restart the server."));
  const link = node("a", "Get an OAuth token from Google ↗");
  link.href = "https://developers.google.com/oauthplayground/#step1&scopes=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly"; link.target = "_blank"; link.rel = "noopener noreferrer";
  body.append(link);
  const form = node("form", "", "hub-mount-form");
  const label = node("label", "OAuth access token");
  const token = node("input"); token.type = "password"; token.required = true; token.autocomplete = "off"; label.append(token);
  const submit = node("button", "Verify & connect", "hub-primary"); submit.type = "submit";
  form.append(label, submit);
  form.addEventListener("submit", event => {
    event.preventDefault();
    void perform(async () => {
      submit.disabled = true;
      try { await request("home/gmail", "POST", { token: token.value.trim() }); token.value = ""; await refresh(); await showInbox(); }
      finally { submit.disabled = false; }
    });
  });
  body.append(form);
}
async function showInbox(query = ""): Promise<void> {
  if (!dashboard?.gmail) { showGmailConnect(); return; }
  const body = openDialog("Gmail inbox", "CONNECTED ACCOUNT");
  element("hub-dialog-message").textContent = dashboard.gmail.email;
  const form = node("form", "", "hub-mail-search");
  const search = node("input"); search.type = "search"; search.placeholder = "Search Gmail…"; search.setAttribute("aria-label", "Search Gmail"); search.value = query;
  const submit = node("button", "Search"); submit.type = "submit"; form.append(search, submit);
  form.addEventListener("submit", event => { event.preventDefault(); void perform(() => showInbox(search.value)); });
  body.append(form, node("p", "Loading mailbox…", "hub-mail-loading"));
  const data = await request<{ items: { subject: string; from: string; date: string; snippet: string }[] }>("home/gmail?" + new URLSearchParams({ q: query }));
  body.querySelector(".hub-mail-loading")?.remove();
  for (const mail of data.items) {
    const article = node("article", "", "hub-mail-item");
    article.append(node("strong", mail.subject), node("small", `${mail.from} · ${mail.date}`), node("p", mail.snippet)); body.append(article);
  }
  if (!data.items.length) body.append(node("p", "No matching messages."));
  body.append(button("Disconnect account", async () => { await request("home/gmail/disconnect", "POST", {}); await refresh(); dialog.close(); }, "hub-disconnect"));
}

element("hub-registry-toggle").addEventListener("click", () => {
  const toggle = element<HTMLButtonElement>("hub-registry-toggle");
  const content = element("hub-registry-content");
  content.hidden = !content.hidden;
  toggle.setAttribute("aria-expanded", String(!content.hidden));
});
element("hub-file-filter").addEventListener("input", renderDirectives);
element("hub-refresh").addEventListener("click", () => void perform(refresh));
element("hub-git").addEventListener("click", () => showSources("git"));
element("hub-vault").addEventListener("click", () => showSources("vault"));
element("hub-mount").addEventListener("click", () => showMount());
element("hub-gmail").addEventListener("click", () => void perform(() => showInbox()));
element("hub-health").addEventListener("click", () => void perform(async () => {
  const body = openDialog("Workspace health", "DIAGNOSTICS");
  element("hub-dialog-message").textContent = "Checking database and captured sources…";
  const result = await request<Record<string, unknown>>("health");
  element("hub-dialog-message").textContent = result.ok ? "Checks passed" : "Checks need attention";
  body.append(pre(JSON.stringify(result, null, 2)));
}));
if (home) new MutationObserver(() => {
  if (!home.hidden) void perform(refresh);
}).observe(home, { attributes: true, attributeFilter: ["hidden"] });
document.addEventListener("visibilitychange", () => { if (!document.hidden && !home.hidden) void perform(refresh); });
void perform(refresh);
