const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const source = fs.readFileSync(path.join(__dirname, "../frontend/public/theme.js"), "utf8");

function fixture(saved, blocked = false) {
  const callbacks = {};
  const button = {
    attributes: {},
    setAttribute(key, value) { this.attributes[key] = value; },
    addEventListener(type, callback) { callbacks[type] = callback; },
  };
  const root = { dataset: {}, style: {} };
  const stored = [];
  vm.runInNewContext(source, {
    document: { documentElement: root, readyState: "complete", getElementById: () => button },
    window: { dispatchEvent() {} },
    Event: class { constructor(type) { this.type = type; } },
    matchMedia: () => ({ matches: false }),
    localStorage: {
      getItem() { if (blocked) throw new Error("Storage disabled"); return saved; },
      setItem(key, value) { if (blocked) throw new Error("Storage disabled"); stored.push([key, value]); },
    },
  });
  return { root, button, callbacks, stored };
}

test("theme loads a saved preference and toggles with accessible state", () => {
  const {root, button, callbacks, stored} = fixture("light");
  assert.equal(root.dataset.theme, "light");
  assert.equal(button.textContent, "Dark mode");
  assert.equal(button.attributes["aria-pressed"], "true");
  callbacks.click();
  assert.equal(root.dataset.theme, "dark");
  assert.equal(button.attributes["aria-label"], "Switch to light mode");
  assert.deepEqual(stored, [["smriti-theme", "dark"]]);
});

test("theme remains usable when preference storage is blocked", () => {
  const {root, callbacks} = fixture(null, true);
  assert.equal(root.dataset.theme, "dark");
  assert.doesNotThrow(() => callbacks.click());
  assert.equal(root.dataset.theme, "light");
});
