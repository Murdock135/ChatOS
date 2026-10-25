// Exercise the real app script against a delayed overview and a minimal DOM.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("navigation requested during startup survives the initial default view", async () => {
  const elements = new Map();
  function element(id) {
    if (!elements.has(id))
      elements.set(id, {
        value: "",
        textContent: "",
        checked: false,
        hidden: false,
        dataset: {},
        classList: { toggle() {} },
        append() {},
        replaceChildren() {},
        setAttribute() {},
        addEventListener() {},
      });
    return elements.get(id);
  }
  const navigation = ["chats", "map", "context", "health", "setup"].map(
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
});
