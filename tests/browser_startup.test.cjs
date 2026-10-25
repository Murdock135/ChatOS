// Exercise the real app script against a delayed overview and a minimal DOM.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("startup navigation survives and failed smart searches recover without stale results", async () => {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id))
      elements.set(id, {
        value: "",
        textContent: "",
        checked: false,
        hidden: false,
        dataset: {},
        classList: {
          values: new Set(),
          toggle(name, enabled) {
            if (enabled) this.values.add(name); else this.values.delete(name);
          },
        },
        children: [],
        append(...children) { this.children.push(...children); },
        replaceChildren(...children) { this.children = children; },
        attributes: {},
        setAttribute(name, value) { this.attributes[name] = value; },
        addEventListener() {},
        click() { this.clicked = true; },
      });
    return elements.get(id);
  }
  const navigation = ["chats", "map", "context", "health", "setup", "settings"].map(
    (view) => {
      const button = element("nav-" + view);
      button.dataset.view = view;
      return button;
    },
  );
  let releaseOverview;
  const overview = new Promise((resolve) => {
    releaseOverview = resolve;
  });
  const sandbox = {
    document: {
      getElementById: element,
      createElement: () => element(Symbol()),
      createTextNode: (text) => ({ textContent: text }),
      querySelectorAll: (selector) =>
        selector === "[data-view]" ? navigation : [],
    },
    window: { addEventListener() {} },
    location: { origin: "http://localhost", hash: "", pathname: "/" },
    sessionStorage: {
      getItem() {
        return "fixture-token";
      },
      setItem() {},
    },
    history: { replaceState() {} },
    URLSearchParams,
    Blob,
    setTimeout,
    clearTimeout,
    fetch: async (url) => {
      let data;
      if (url === "/api/overview") data = await overview;
      else if (url.startsWith("/api/chats?")) data = { items: [], total: 0 };
      else if (url === "/api/search-models") data = {settings: {embedding: {model_id: "fixture/embed"}, reranker: {model_id: "fixture/rank"}}, downloaded: {}, runtime_ready: false};
      else if (url === "/api/setup")
        data = { supported: false, detail: "Fixture setup" };
      else throw new Error("Unexpected fixture request: " + url);
      return { ok: true, json: async () => data };
    },
  };
  vm.runInNewContext(
    fs.readFileSync(
      path.join(__dirname, "../src/chatos/static/app.js"),
      "utf8",
    ),
    sandbox,
  );
  const navigationFinished = element("nav-setup").onclick();
  releaseOverview({
    workspace: "/fictional",
    projects: [],
    chats: 1,
    archived: 0,
    status: {},
  });
  await navigationFinished;
  assert.equal(element("page-title").textContent, "Setup & handoff");
  assert.equal(element("view-setup").hidden, false);
  assert.equal(element("view-chats").hidden, true);
  assert.equal(element("notice").textContent, "");

  assert.equal(element("nav-settings").attributes["aria-label"], "Settings");
  await element("nav-settings").onclick();
  assert.equal(element("page-title").textContent, "Settings");
  assert.equal(element("view-settings").hidden, false);
  assert.equal(element("view-setup").hidden, true);
  assert.equal(element("workspace-path").textContent, "/fictional");
  assert.equal(element("settings-last-sync").textContent, "No completed sync recorded yet.");
  element("import").onclick();
  assert.equal(element("import-file").clicked, true);
  await element("nav-setup").onclick();

  element("search").value = "langchain";
  element("search-mode").value = "hybrid";
  sandbox.fetch = async () => ({
    ok: false,
    status: 400,
    json: async () => ({ error: "Local model could not initialize" }),
  });
  await vm.runInNewContext("safely(() => loadChats())()", sandbox);
  assert.equal(element("result-count").textContent, "");
  assert.equal(element("search-error").hidden, false);
  assert.equal(element("search-error-title").textContent, "Smart search error");
  assert.equal(element("next-page").disabled, true);
  assert.equal(element("search-error-message").textContent, "Local model could not initialize");
  assert.equal(element("notice").textContent, "");

  element("search-error-dismiss").onclick();
  assert.equal(element("search-error").hidden, true);
  sandbox.fetch = async () => ({
    ok: true,
    json: async () => ({ items: [], total: 0 }),
  });
  await element("search-error-retry").onclick();
  assert.equal(element("search-error").hidden, true);
  assert.equal(element("result-count").textContent, "0 conversations matching your search");
  assert.equal(element("notice").textContent, "");

  let rejectOlder;
  sandbox.fetch = () => new Promise((resolve, reject) => { rejectOlder = reject; });
  const olderSearch = vm.runInNewContext("safely(() => loadChats())()", sandbox);
  sandbox.fetch = async () => ({
    ok: true,
    json: async () => ({ items: [], total: 0 }),
  });
  await vm.runInNewContext("loadChats()", sandbox);
  rejectOlder(new Error("Older search failed"));
  await olderSearch;
  assert.equal(element("notice").textContent, "");
  assert.equal(element("search-error").hidden, true);
  assert.equal(element("result-count").textContent, "0 conversations matching your search");

  // A sync reports running, completion, partial failures and request failures in place.
  let releaseSync;
  let syncEntered;
  const entered = new Promise((resolve) => { syncEntered = resolve; });
  const syncResult = new Promise((resolve) => { releaseSync = resolve; });
  let outcome = { status: "partial", changes: { chats: { new: 1, updated: 2 } }, errors: [{ error: "Source unavailable" }] };
  sandbox.fetch = async (url) => {
    let data;
    if (url === "/api/sync") { syncEntered(); data = await syncResult; }
    else if (url === "/api/overview") data = { workspace: "/fictional", projects: [], chats: 1, archived: 0, status: {} };
    else if (url === "/api/setup") data = { supported: false, detail: "Fixture setup" };
    else if (url === "/api/search-models") data = { settings: { embedding: {model_id: "fixture/embed"}, reranker: {model_id: "fixture/rank"} }, downloaded: {}, runtime_ready: false };
    else data = { items: [], total: 0 };
    return { ok: true, json: async () => data };
  };
  const syncFinished = element("settings-sync").onclick();
  await entered;
  assert.equal(element("sync-label").textContent, "Syncing…");
  assert.equal(element("sync").disabled, true);
  assert.equal(element("settings-sync").disabled, true);
  releaseSync(outcome);
  await syncFinished;
  assert.match(element("sync-message").textContent, /Source unavailable/);
  assert.equal(element("sync-status").classList.values.has("has-error"), true);
  assert.equal(element("sync").disabled, false);
  assert.equal(element("sync-label").textContent, "Sync");
  assert.equal(element("settings-sync-label").textContent, "Sync now");

  const normalFetch = sandbox.fetch;
  sandbox.fetch = async (url) => url === "/api/sync"
    ? { ok: true, json: async () => ({status: "ok", changes: { chats: { new: 3, updated: 4 } }, errors: []}) }
    : normalFetch(url);
  await element("sync").onclick();
  assert.equal(element("sync-message").textContent, "Sync complete · 3 new chats, 4 updated chats");
  assert.equal(element("sync-status").classList.values.has("has-error"), false);

  sandbox.fetch = async () => { throw new Error("Connection lost"); };
  await element("sync").onclick();
  assert.equal(element("sync-message").textContent, "Sync error · Connection lost");
  assert.equal(element("sync-status").classList.values.has("has-error"), true);
  assert.equal(element("sync").disabled, false);

  sandbox.fetch = async () => ({ ok: true, json: async () => ({
    items: [{source: "chatgpt", id: "fictional", title: "Plan a garden", messages: 3, updated_at: "2026-10-25T12:00:00Z", models: ["captured-model-a", "captured-model-b"]}], total: 1
  }) });
  await vm.runInNewContext("loadChats()", sandbox);
  await vm.runInNewContext('showView("chats")', sandbox);
  assert.equal(element("subtitle").hidden, true);
  const row = element("chat-list").children[0];
  assert.equal(row.children.length, 4);
  assert.equal(row.children[0].children[0].children[0].textContent, "Plan a garden");
  assert.equal(row.children[2].children[0].textContent, "captured-model-a");
  assert.equal(row.children[2].children[1].textContent, "+1 more");

  // Pagination replaces rows, carries scope, resets on size/filter changes and clamps stale pages.
  const pageRequests = [];
  let available = 23;
  sandbox.fetch = async (url) => {
    const query = new URLSearchParams(url.split("?")[1]);
    pageRequests.push(query);
    const offset = Number(query.get("offset"));
    const limit = Number(query.get("limit"));
    const items = Array.from({length: Math.max(0, Math.min(limit, available - offset))}, (_, i) => ({source: "codex", id: String(offset+i), title: "Page item " + (offset+i), messages: 1, models: []}));
    return {ok: true, json: async () => ({items, total: available})};
  };
  element("page-size").value = "10";
  element("search").value = "garden";
  element("source").value = "codex";
  await element("page-size").onchange();
  assert.equal(element("chat-list").children.length, 10);
  assert.equal(element("page-label").textContent, "Page 1 of 3");
  assert.equal(element("page-range").textContent, "1–10 of 23");
  assert.equal(element("previous-page").disabled, true);
  await element("next-page").onclick();
  assert.equal(element("chat-list").children.length, 10);
  assert.equal(pageRequests.at(-1).get("offset"), "10");
  assert.equal(pageRequests.at(-1).get("q"), "garden");
  assert.equal(pageRequests.at(-1).get("source"), "codex");
  await element("next-page").onclick();
  assert.equal(element("chat-list").children.length, 3);
  assert.equal(element("page-range").textContent, "21–23 of 23");
  assert.equal(element("next-page").disabled, true);
  await element("previous-page").onclick();
  assert.equal(element("page-label").textContent, "Page 2 of 3");
  element("page-size").value = "50";
  await element("page-size").onchange();
  assert.equal(pageRequests.at(-1).get("limit"), "50");
  assert.equal(pageRequests.at(-1).get("offset"), "0");
  element("page-size").value = "100";
  await element("page-size").onchange();
  assert.equal(pageRequests.at(-1).get("limit"), "100");
  element("page-size").value = "10";
  await element("page-size").onchange();
  await element("next-page").onclick();
  await element("source").onchange();
  assert.equal(element("page-label").textContent, "Page 1 of 3");
  available = 1;
  await vm.runInNewContext("loadChats(3)", sandbox);
  assert.equal(element("page-label").textContent, "Page 1 of 1");
  assert.equal(element("page-range").textContent, "1–1 of 1");
  available = 0;
  await vm.runInNewContext("loadChats()", sandbox);
  assert.equal(element("page-range").textContent, "0 conversations");
  assert.equal(element("previous-page").disabled, true);
  assert.equal(element("next-page").disabled, true);

});
