const assert = require("node:assert/strict");
const fs = require("node:fs");
const test = require("node:test");
const vm = require("node:vm");

function fixture() {
  const elements = new Map();
  function element() {
    return {
      children: [],
      attributes: {},
      listeners: {},
      dataset: {},
      style: {},
      value: "",
      textContent: "",
      append(...children) {
        this.children.push(...children);
      },
      replaceChildren(...children) {
        this.children = children;
      },
      setAttribute(key, value) {
        this.attributes[key] = value;
      },
      addEventListener(key, callback) {
        this.listeners[key] = callback;
      },
    };
  }
  function get(id) {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  }
  const base = {
    source: "fictional",
    conversation_id: "fictional-id",
    title: "Home projects",
    description: "</script><script>untrusted()</script>",
    start_exchange: 1,
    end_exchange: 1,
    evidence_exchanges: [1],
    x: 0,
    y: 0,
    neighbors: [],
  };
  const points = [
    {
      ...base,
      id: "a",
      pilot_id: "P001",
      kind: "main",
      parent_id: null,
      label: "Household",
    },
    {
      ...base,
      id: "b",
      pilot_id: "P001",
      kind: "subtopic",
      parent_id: "a",
      label: "Solar batteries",
      x: 2,
      neighbors: [{ id: "c", cosine_distance: 0.2 }],
    },
    {
      ...base,
      id: "c",
      pilot_id: "P002",
      kind: "main",
      parent_id: null,
      label: "Energy research",
      x: 3,
    },
  ];
  const data = {
    metadata: { limits: [], excluded: [] },
    datasets: {
      first: { points, conversations: 2, subtopics: 1 },
      second: { points: points.slice(0, 2), conversations: 1, subtopics: 1 },
    },
  };
  get("topic-data").textContent = JSON.stringify(data);
  get("model").value = "first";
  get("kind").value = "all";
  const context = vm.createContext({
    document: {
      getElementById: get,
      createElement: element,
      createElementNS: element,
    },
  });
  const html = fs.readFileSync("src/chatos/templates/topic-map.html", "utf8");
  const script = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)][0][1];
  vm.runInContext(script, context);
  return { get, run: (code) => vm.runInContext(code, context) };
}

test("topic filters retain coordinates and parent selection draws its source family", () => {
  const { get, run } = fixture();
  assert.equal(get("nodes").children.length, 3);
  const before = run("JSON.stringify(points.map(p=>[p.screenX,p.screenY]))");
  run("select('b')");
  assert.equal(get("edges").children.length, 1);
  assert.ok(
    get("detail").children.some((e) => e.textContent.includes("untrusted()")),
  );
  get("query").value = "batteries";
  get("query").listeners.input();
  assert.equal(get("nodes").children.length, 1);
  assert.equal(get("edges").children.length, 0);
  assert.equal(
    run("JSON.stringify(points.map(p=>[p.screenX,p.screenY]))"),
    before,
  );
});

test("related selection clears filters, model changes reset selection, and empty search works", () => {
  const { get, run } = fixture();
  run("select('b')");
  get("query").value = "no matches";
  get("query").listeners.input();
  assert.equal(get("nodes").children.length, 0);
  const related = get("detail").children.find((e) =>
    e.textContent.includes("cosine distance"),
  );
  related.listeners.click();
  assert.equal(run("selected"), "c");
  assert.equal(get("query").value, "");
  get("model").value = "second";
  get("model").listeners.change();
  assert.equal(run("selected"), null);
  assert.equal(get("nodes").children.length, 2);
  get("zoom-in").listeners.click();
  assert.ok(run("pan.scale") > 1);
  get("reset").listeners.click();
  assert.equal(run("pan.scale"), 1);
});
