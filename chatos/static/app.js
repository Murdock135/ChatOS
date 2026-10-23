"use strict";
const $ = (id) => document.getElementById(id);
const node = (tag, text = "", className = "") => {
  const result = document.createElement(tag);
  result.textContent = text;
  if (className) result.className = className;
  return result;
};
const storageKey = "chatos-token:" + location.origin;
let token = sessionStorage.getItem(storageKey) || "";
function acceptLaunchToken() {
  const fragment = new URLSearchParams(location.hash.slice(1));
  if (!fragment.has("token")) return false;
  token = fragment.get("token") || "";
  sessionStorage.setItem(storageKey, token);
  history.replaceState(null, "", location.pathname);
  return true;
}
acceptLaunchToken();
let overview,
  current,
  currentView = "chats",
  loaded = 0,
  requestId = 0,
  contextItems = [],
  dirty = false;
window.addEventListener("beforeunload", (event) => {
  if (dirty) {
    event.preventDefault();
    event.returnValue = "";
  }
});
const notice = (message, error = false) => {
  $("notice").textContent = message;
  $("notice").className = error ? "error" : "";
};
async function api(path, method = "GET", body) {
  const response = await fetch("/api/" + path, {
    method,
    headers: {
      "X-ChatOS-Token": token,
      "Content-Type":
        body instanceof Blob ? "application/octet-stream" : "application/json",
    },
    body:
      body === undefined
        ? undefined
        : body instanceof Blob
          ? body
          : JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}
function safely(action) {
  return async (...args) => {
    try {
      await action(...args);
    } catch (error) {
      notice(error.message, true);
    }
  };
}
function option(value, label) {
  const result = node("option", label);
  result.value = value;
  return result;
}
function date(value) {
  return value ? new Date(value).toLocaleString() : "Date unknown";
}
function captureLabel(value) {
  const labels = {
    exported_visible_branches:
      "Export snapshot · includes conversation branches",
    partial_desktop_tool_capture: "Partial desktop capture",
    partial_history_projection: "Partial history recovery",
    available_visible_messages: "Available captured messages",
    local_library_annotation: "Your local annotation",
    current_workspace_file: "Current workspace note",
  };
  return labels[value] || value || "Capture unknown";
}
function fillProjects() {
  const selected = $("project").value;
  $("project").replaceChildren(option("", "All projects"));
  for (const project of overview.projects)
    $("project").append(option(project.id, project.name));
  $("project").value = selected;
}
async function refreshOverview() {
  overview = await api("overview");
  $("workspace-path").textContent = overview.workspace;
  fillProjects();
}
async function showView(view) {
  if (
    dirty &&
    view !== currentView &&
    !confirm("Discard unsaved annotation changes?")
  )
    return;
  if (view !== currentView) dirty = false;
  currentView = view;
  for (const section of ["chats", "map", "context", "health"])
    $("view-" + section).hidden = section !== view;
  for (const button of document.querySelectorAll("[data-view]")) {
    const selected = button.dataset.view === view;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  }
  const titles = {
    chats: ["Conversations", "Find a conversation. Pick up a thread."],
    map: [
      "Conversation map",
      "Explore related chats. Similarity is a suggestion, not a decision.",
    ],
    context: ["Skills & memory", "Inspect the context behind your assistant."],
    health: [
      "Health & sync",
      "Know what is captured, current, and still missing.",
    ],
  };
  $("page-title").textContent = titles[view][0];
  $("subtitle").textContent = titles[view][1];
  if (view === "chats") await loadChats();
  if (view === "context") await loadContext();
  if (view === "health") renderHealth();
  if (view === "map") await loadMap();
}
async function loadChats(append = false) {
  const id = ++requestId;
  const query = new URLSearchParams({
    q: $("search").value,
    source: $("source").value,
    project: $("project").value,
    archived: $("archived").checked,
    offset: append ? loaded : 0,
  });
  const data = await api("chats?" + query);
  if (id !== requestId) return;
  if (!append) {
    $("chat-list").replaceChildren();
    loaded = 0;
  }
  for (const chat of data.items) {
    const card = node("button", "", "chat-card");
    card.dataset.source = chat.source;
    card.dataset.id = chat.id;
    card.classList.toggle(
      "selected",
      !!current &&
        chat.source === current.record.source &&
        chat.id === current.record.id,
    );
    card.append(node("strong", chat.title));
    const meta = node("small");
    meta.append(
      node("span", chat.source, "pill"),
      document.createTextNode(
        chat.messages + " messages" + (chat.has_note ? " · Note" : ""),
      ),
    );
    card.append(meta, node("small", date(chat.updated_at)));
    card.onclick = safely(() => openChat(chat.source, chat.id));
    $("chat-list").append(card);
  }
  loaded += data.items.length;
  $("result-count").textContent =
    data.total +
    " " +
    ($("archived").checked ? "archived " : "") +
    (data.total === 1 ? "conversation" : "conversations") +
    ($("search").value ? " matching your search" : " in your library");
  $("more").hidden = loaded >= data.total;
  if (!loaded)
    $("chat-list").append(
      node(
        "p",
        "No conversations match. Try another search or check source coverage.",
        "muted",
      ),
    );
}
async function openChat(source, id, messageId) {
  if (dirty && !confirm("Discard unsaved annotation changes?")) return;
  dirty = false;
  current = await api("chat?" + new URLSearchParams({ source, id }));
  if (currentView !== "chats") {
    $("archived").checked = current.annotation.archived;
    await showView("chats");
  }
  for (const card of document.querySelectorAll("#chat-list .chat-card"))
    card.classList.toggle(
      "selected",
      card.dataset.source === source && card.dataset.id === id,
    );
  const { record, annotation } = current,
    reader = $("reader");
  reader.replaceChildren();
  const head = node("div", "", "reader-head");
  head.append(node("h2", annotation.title || record.title));
  head.append(
    node(
      "p",
      record.source +
        " · " +
        record.messages.length +
        " messages · " +
        captureLabel(record.capture),
      "muted",
    ),
  );
  head.append(node("p", "Source ID: " + record.id, "source-details"));
  if (annotation.title)
    head.append(node("p", "Original title: " + record.title, "source-details"));
  if (record.limits?.length) {
    const capture = node("details", "", "capture-details");
    capture.append(node("summary", "About this capture"));
    for (const limit of record.limits) capture.append(node("p", limit));
    head.append(capture);
  }
  const details = node("details", "", "annotations");
  details.append(node("summary", "Local title, notes & project"));
  const form = node("form", "", "form-grid");
  const titleLabel = node("label", "Local title (original stays unchanged)"),
    title = node("input");
  title.value = annotation.title;
  title.maxLength = 300;
  title.placeholder = record.title;
  title.id = "local-title";
  titleLabel.append(title);
  const noteLabel = node("label", "Your note"),
    note = node("textarea");
  note.value = annotation.note;
  note.maxLength = 100000;
  note.id = "local-note";
  note.placeholder = "What should you remember about this conversation?";
  noteLabel.append(note);
  title.oninput = note.oninput = () => {
    dirty = true;
  };
  const actions = node("div", "", "form-actions"),
    save = node("button", "Save annotations", "primary");
  save.type = "submit";
  const archive = node(
    "button",
    annotation.archived ? "Restore to library" : "Archive locally",
  );
  archive.type = "button";
  actions.append(
    save,
    archive,
    node("small", "Stored locally; no source-app changes."),
  );
  form.append(titleLabel, noteLabel, actions);
  form.onsubmit = safely(async (event) => {
    event.preventDefault();
    save.disabled = true;
    try {
      await api("annotation", "PUT", {
        source,
        id,
        changes: { title: title.value, note: note.value },
      });
      dirty = false;
      await openChat(source, id);
      await loadChats();
      notice("Local annotations saved. Captured messages are unchanged.");
    } finally {
      save.disabled = false;
    }
  });
  archive.onclick = safely(async () => {
    if (dirty && !confirm("Discard unsaved annotation changes?")) return;
    dirty = false;
    await api("annotation", "PUT", {
      source,
      id,
      changes: { archived: !annotation.archived },
    });
    reader.replaceChildren(
      node(
        "div",
        "Conversation " +
          (annotation.archived
            ? "restored."
            : "archived locally. Use Archived to restore it."),
        "empty",
      ),
    );
    current = null;
    await refreshOverview();
    await loadChats();
    notice("Library updated. The captured source record is retained.");
  });
  const projectArea = node("div", "", "project-edit"),
    projectLabel = node(
      "label",
      "Project associations (select any that apply)",
    ),
    projectSelect = node("select");
  projectSelect.multiple = true;
  projectSelect.id = "chat-projects";
  for (const project of overview.projects) {
    const item = option(project.id, project.name);
    item.selected = record.projects.includes(project.id);
    projectSelect.append(item);
  }
  projectLabel.append(projectSelect);
  const assign = node("button", "Apply project assignment");
  assign.type = "button";
  assign.onclick = safely(async () => {
    if (dirty && !confirm("Discard unsaved annotation changes?")) return;
    dirty = false;
    const projects = [...projectSelect.selectedOptions].map(
      (item) => item.value,
    );
    await api("assign", "POST", { source, id, projects });
    await openChat(source, id);
    await loadChats();
    notice(
      "Project assignment saved. External project notes were not changed.",
    );
  });
  projectArea.append(projectLabel, assign);
  details.append(form, projectArea);
  const transcript = node("div", "", "transcript");
  for (const message of record.messages) {
    const section = node("section", "", "message");
    section.dataset.messageId = message.id;
    section.append(
      node("span", message.role, "role " + message.role),
      node(
        "p",
        date(message.timestamp) +
          " · " +
          (message.model || "Model unknown") +
          " · " +
          message.id,
        "message-meta",
      ),
      node("div", message.text, "message-body"),
    );
    if (message.parent_id || message.export_node_id) {
      const branch = node("details", "", "branch-details");
      branch.append(node("summary", "Branch relationship"));
      if (message.export_node_id)
        branch.append(node("p", "Branch node: " + message.export_node_id));
      branch.append(node("p", "Parent node: " + (message.parent_id || "Root")));
      section.append(branch);
    }
    transcript.append(section);
  }
  reader.append(head, details, transcript);
  if (messageId) {
    const message = [...transcript.children].find(
      (item) => item.dataset.messageId === messageId,
    );
    if (message) message.scrollIntoView({ block: "center" });
  }
}
$("evidence").onclick = safely(async () => {
  if (!$("search").value.trim()) {
    notice("Enter a subject or question first.");
    return;
  }
  if (dirty && !confirm("Discard unsaved annotation changes?")) return;
  dirty = false;
  const packet = await api(
    "retrieve?" +
      new URLSearchParams({
        q: $("search").value,
        project: $("project").value,
      }),
  );
  const reader = $("reader");
  reader.replaceChildren();
  const head = node("div", "", "reader-head");
  head.append(
    node("h2", "Source evidence"),
    node(
      "p",
      "Candidate passages, not an automatically generated answer. Check speaker, context, and later changes.",
      "muted",
    ),
  );
  reader.append(head);
  const body = node("div", "", "transcript");
  for (const item of packet.passages) {
    const section = node("section", "", "message");
    section.append(
      node(
        "span",
        { local_annotation: "Local note", workspace_note: "Workspace note" }[
          item.role
        ] || item.role,
        "role",
      ),
      node("h3", item.title),
      node(
        "p",
        captureLabel(item.capture) +
          " · " +
          item.path +
          (item.line ? ":" + item.line : ""),
        "message-meta",
      ),
      node("div", item.excerpt, "message-body"),
    );
    if (item.source !== "workspace") {
      const open = node("button", "Open captured chat");
      open.onclick = safely(() =>
        openChat(item.source, item.id, item.message_id),
      );
      section.append(open);
    }
    body.append(section);
  }
  if (!packet.passages.length)
    body.append(
      node(
        "p",
        "No matching passages found. Try different wording; missing results do not prove a discussion never happened.",
        "callout",
      ),
    );
  reader.append(body);
});
async function loadContext() {
  const data = await api("context");
  contextItems = data.items;
  $("context-summary").textContent =
    contextItems.length +
    " captured files · Snapshot " +
    (data.captured_at || "unavailable; run sync");
  filterContext();
}
function filterContext() {
  $("context-list").replaceChildren();
  const query = $("context-query").value.toLowerCase(),
    type = $("context-type").value;
  for (const item of contextItems.filter(
    (item) =>
      (!type || item.category === type) &&
      item.source.toLowerCase().includes(query),
  )) {
    const button = node("button", "", "chat-card");
    button.append(
      node("strong", item.source.split("/").slice(-2).join("/")),
      node("small", item.category),
    );
    button.onclick = safely(async () => {
      const data = await api(
        "context/read?" + new URLSearchParams({ path: item.snapshot }),
      );
      const head = node("div", "", "reader-head");
      head.append(
        node("h2", item.source.split("/").slice(-2).join("/")),
        node("p", "Captured copy · " + data.captured_at, "muted"),
        node("p", "Live source: " + data.source, "source-details"),
      );
      $("context-reader").replaceChildren(
        head,
        node("pre", data.text, "context-body"),
      );
    });
    $("context-list").append(button);
  }
}
function table(headers, rows) {
  const result = node("table"),
    head = node("tr");
  for (const label of headers) head.append(node("th", label));
  result.append(head);
  for (const values of rows) {
    const row = node("tr");
    for (const value of values) row.append(node("td", String(value)));
    result.append(row);
  }
  return result;
}
function renderHealth(health) {
  const out = $("health-output");
  out.replaceChildren();
  const status = overview.status;
  const stats = node("div", "", "stats");
  for (const [value, label] of [
    [status.run_id || "—", "Last run ID"],
    [status.status, "Run status"],
    [(status.errors || []).length, "Run errors"],
    [overview.chats, "Active conversations"],
    [overview.archived, "Archived locally"],
  ]) {
    const item = node("div", "", "stat");
    item.append(node("strong", String(value)), node("span", label));
    stats.append(item);
  }
  out.append(stats);
  out.append(node("p", "Last sync: " + date(status.finished_at), "muted"));
  if (status.changes) {
    out.append(node("h3", "Changes captured in the last run"));
    out.append(
      table(
        ["Item", "New", "Updated", "Removed", "Total"],
        Object.entries(status.changes)
          .filter(([, value]) => value && typeof value === "object")
          .map(([key, value]) => [
            key,
            value.new,
            value.updated,
            value.removed,
            value.total,
          ]),
      ),
    );
  }
  out.append(node("h3", "Source coverage"));
  out.append(
    table(
      ["Source", "State", "Details"],
      Object.entries(status.sources || {}).map(([key, value]) => [
        key,
        value.status,
        value.detail,
      ]),
    ),
  );
  if (health) {
    const section = node("section", "", "report-section");
    section.append(
      node("h3", health.ok ? "Health checks passed" : "Health needs attention"),
    );
    for (const message of [...health.errors, ...health.warnings])
      section.append(node("p", message, "callout"));
    out.append(section);
  }
  if ((status.errors || []).length)
    out.append(
      node("pre", JSON.stringify(status.errors, null, 2), "context-body"),
    );
}
let mapData,
  visibleMapDocuments = [],
  mapZoom = 1,
  panX = 0,
  panY = 0,
  dragging,
  moved = false,
  mapPositions = [];
async function loadMap() {
  mapData = await api("map");
  const selected = $("map-project").value;
  $("map-project").replaceChildren(option("", "All projects"));
  for (const project of overview.projects)
    $("map-project").append(option(project.id, project.name));
  $("map-project").value = selected;
  filterMap();
}
function filterMap() {
  if (!mapData) return;
  const query = $("map-query").value.toLowerCase(),
    project = $("map-project").value,
    source = $("map-source").value;
  visibleMapDocuments = (mapData.documents || []).filter(
    (item) =>
      item.title.toLowerCase().includes(query) &&
      (!project || item.projects.includes(project)) &&
      (!source || item.source === source),
  );
  $("map-summary").textContent =
    visibleMapDocuments.length +
    " of " +
    (mapData.documents || []).length +
    " mapped conversations · Built " +
    date(mapData.checked_at) +
    " · " +
    (mapData.freshness_note || "Run sync to generate the map.");
  $("map-method").textContent =
    (mapData.method || "Experimental representation") +
    " " +
    (mapData.limits || "");
  $("map-list").replaceChildren();
  for (const item of visibleMapDocuments) {
    const button = node("button", item.title);
    button.onclick = safely(() => openChat(item.source, item.id));
    $("map-list").append(button);
  }
  drawMap();
}
function drawMap() {
  if (!mapData || currentView !== "map") return;
  const canvas = $("map-canvas"),
    context = canvas.getContext("2d"),
    docs = visibleMapDocuments,
    width = canvas.clientWidth,
    height = canvas.clientHeight,
    ratio = devicePixelRatio || 1;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);
  mapPositions = [];
  if (!docs.length) return;
  const xs = docs.map((item) => item.x),
    ys = docs.map((item) => item.y),
    minX = Math.min(...xs),
    maxX = Math.max(...xs),
    minY = Math.min(...ys),
    maxY = Math.max(...ys),
    scale =
      Math.min(
        (width - 60) / (maxX - minX || 1),
        (height - 60) / (maxY - minY || 1),
      ) * mapZoom;
  const colors = ["#286548", "#597cac", "#b37b46", "#8967a0", "#a46b7a"];
  for (const item of docs) {
    const x = width / 2 + (item.x - (minX + maxX) / 2) * scale + panX,
      y = height / 2 - (item.y - (minY + maxY) / 2) * scale + panY;
    let hash = 0;
    for (const c of item.group || "")
      hash = (hash * 31 + c.charCodeAt(0)) >>> 0;
    context.beginPath();
    context.arc(x, y, 6, 0, Math.PI * 2);
    context.fillStyle =
      item.group === "unclustered" ? "#95a295" : colors[hash % colors.length];
    context.fill();
    mapPositions.push({ x, y, item });
  }
}
function zoom(factor) {
  mapZoom = Math.max(0.25, Math.min(20, mapZoom * factor));
  drawMap();
}
const canvas = $("map-canvas");
canvas.onpointerdown = (event) => {
  dragging = { x: event.clientX, y: event.clientY, panX, panY };
  moved = false;
  canvas.setPointerCapture(event.pointerId);
};
canvas.onpointermove = (event) => {
  if (!dragging) {
    const box = canvas.getBoundingClientRect(),
      x = event.clientX - box.left,
      y = event.clientY - box.top;
    const point = mapPositions.find(
      (point) => (point.x - x) ** 2 + (point.y - y) ** 2 < 144,
    );
    $("map-hover").textContent = point
      ? point.item.title
      : "Select a point or conversation title to read its messages.";
    return;
  }
  const dx = event.clientX - dragging.x,
    dy = event.clientY - dragging.y;
  moved ||= Math.abs(dx) + Math.abs(dy) > 4;
  panX = dragging.panX + dx;
  panY = dragging.panY + dy;
  drawMap();
};
canvas.onpointerup = safely(async (event) => {
  if (!moved) {
    const box = canvas.getBoundingClientRect(),
      x = event.clientX - box.left,
      y = event.clientY - box.top;
    const point = mapPositions.find(
      (point) => (point.x - x) ** 2 + (point.y - y) ** 2 < 144,
    );
    if (point) await openChat(point.item.source, point.item.id);
  }
  dragging = null;
});
canvas.onpointercancel = () => {
  dragging = null;
};
canvas.addEventListener(
  "wheel",
  (event) => {
    event.preventDefault();
    zoom(event.deltaY < 0 ? 1.12 : 1 / 1.12);
  },
  { passive: false },
);
$("map-in").onclick = () => zoom(1.25);
$("map-out").onclick = () => zoom(0.8);
$("map-reset").onclick = () => {
  mapZoom = 1;
  panX = panY = 0;
  drawMap();
};
window.addEventListener("resize", drawMap);
for (const button of document.querySelectorAll("[data-view]"))
  button.onclick = safely(() => showView(button.dataset.view));
let timer;
$("search").oninput = () => {
  clearTimeout(timer);
  timer = setTimeout(
    safely(() => loadChats()),
    220,
  );
};
for (const id of ["source", "project", "archived"])
  $(id).onchange = safely(() => loadChats());
$("more").onclick = safely(() => loadChats(true));
$("context-query").oninput = filterContext;
$("context-type").onchange = filterContext;
$("check-health").onclick = safely(async () => {
  $("check-health").disabled = true;
  try {
    renderHealth(await api("health"));
  } finally {
    $("check-health").disabled = false;
  }
});
$("sync").onclick = safely(async () => {
  $("sync").disabled = true;
  $("sync").textContent = "Syncing…";
  notice("Sync is running. You can keep reading captured records.");
  try {
    const result = await api("sync", "POST", {});
    await refreshOverview();
    await showView(currentView);
    notice(
      "Run " +
        result.run_id +
        " · " +
        result.status +
        " · " +
        result.changes.chats.new +
        " new chats, " +
        result.changes.chats.updated +
        " updated chats.",
      result.status !== "ok",
    );
  } finally {
    $("sync").disabled = false;
    $("sync").textContent = "Sync workspace";
  }
});
safely(async () => {
  await refreshOverview();
  await showView("chats");
})();

$("import").onclick = () => $("import-file").click();
$("import-file").onchange = safely(async () => {
  const file = $("import-file").files[0];
  if (!file) return;
  $("import").disabled = true;
  try {
    const extension = file.name.split(".").pop().toLowerCase();
    notice("Validating the selected export…");
    const result = await api(
      "import?" + new URLSearchParams({ format: extension }),
      "POST",
      file,
    );
    notice(
      result.conversations +
        (result.conversations === 1
          ? " conversation received."
          : " conversations received.") +
        " Select Sync workspace to import them. The export stays in your local inbox.",
    );
  } finally {
    $("import").disabled = false;
    $("import-file").value = "";
  }
});
$("backup").onclick = safely(async () => {
  $("backup").disabled = true;
  try {
    const result = await api("backup", "POST", {});
    notice(
      "Fresh database backup verified: " +
        result.path +
        ". Includes local annotations; stored on this device.",
    );
  } finally {
    $("backup").disabled = false;
  }
});

$("map-query").oninput = filterMap;
for (const id of ["map-project", "map-source"]) $(id).onchange = filterMap;

window.addEventListener(
  "hashchange",
  safely(async () => {
    if (!acceptLaunchToken()) return;
    await refreshOverview();
    await showView(currentView);
    notice("Reconnected to the local workspace.");
  }),
);
