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
        style: {},
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
        getBoundingClientRect() { return {width: 0, height: 0}; },
        getContext() { return null; },
        click() { this.clicked = true; },
      });
    return elements.get(id);
  }
  const navigation = ["home", "chats", "map", "context", "health", "setup", "settings"].map(
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
        (selector === "[data-view]" || selector === "nav [data-view]") ? navigation : [],
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
      else if (url.startsWith("/api/map?")) data = {documents: [], groups: {}};
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
      path.join(__dirname, "../frontend/public/app.js"),
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

  assert.equal(element("view-explore").hidden, true);
  await vm.runInNewContext('showView("chats")', sandbox);
  assert.equal(element("view-explore").hidden, false);
  assert.equal(element("view-chats").hidden, false);
  assert.equal(element("view-map").hidden, false);
  element("search").value = "keep this query";
  element("explore-toggle").onclick();
  assert.equal(element("view-explore").dataset.mode, "map");
  assert.equal(element("search").value, "keep this query");
  assert.equal(element("explore-toggle").attributes["aria-pressed"], "true");
  element("explore-toggle").onclick();
  assert.equal(element("view-explore").dataset.mode, "search");
  element("search").value = "";

  await element("nav-home").onclick();
  assert.equal(element("view-home").hidden, false);
  assert.equal(element("view-setup").hidden, true);
  assert.equal(element("page-title").hidden, true);
  assert.equal(element("home-chat-count").textContent, "1 captured conversation");
  assert.equal(element("nav-home").attributes["aria-label"], "Home");

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
  await vm.runInNewContext('notice("Local model could not initialize", true)', sandbox);
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
  assert.equal(element("sync-label").textContent, "Synced");
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

  // Derived subtopics retain exact source IDs and projected world coordinates.
  const mapped = Array.from({length: 12}, (_, i) => ({source: "codex", id: "map-" + i, title: "Garden planning " + i, x: i, y: i % 3, group: "garden", projects: [], date: "2026-10-25"}));
  sandbox.mappedFixture = mapped;
  await vm.runInNewContext('mapData = {documents: mappedFixture, groups: {garden: "Gardening"}}; buildMapSubtopics(); filterMap();', sandbox);
  assert.equal(vm.runInNewContext('mapSubtopics.size', sandbox), 3);
  assert.equal(vm.runInNewContext('[...mapSubtopics.values()].reduce((sum, group) => sum + group.keys.size, 0)', sandbox), 12);
  await vm.runInNewContext('enterMapLevel("garden", "")', sandbox);
  assert.equal(element("map-level").textContent, "Subtopics");
  await vm.runInNewContext('enterMapLevel("garden", "garden:0")', sandbox);
  assert.equal(element("map-level").textContent, "Conversations");
  assert.equal(vm.runInNewContext('visibleMapDocuments.length', sandbox), 4);
  assert.equal(mapped[0].x, 0);
  element("map-back").onclick();
  assert.equal(element("map-level").textContent, "Subtopics");
  element("map-back").onclick();
  assert.equal(element("map-level").textContent, "Topics");
  assert.equal(vm.runInNewContext('visibleMapDocuments.length', sandbox), 12);

});
