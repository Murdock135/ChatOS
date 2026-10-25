"use strict";
// Keep native select values as the form contract while presenting visible choices.
function enhanceChoices(select) {
  if (select.dataset.enhanced) return;
  select.dataset.enhanced = "true";
  const wrapper = document.createElement("div");
  wrapper.className = "choice-control";
  wrapper.classList.toggle("menu-choices", select.dataset.presentation === "menu");
  const label = select.closest("label");
  const name = label?.firstChild?.textContent?.trim() || "Choose an option";
  wrapper.setAttribute("role", "group");
  wrapper.setAttribute("aria-label", name);
  select.after(wrapper);
  select.hidden = true;
  let filter = "";
  let updateSelection = () => {};
  select.addEventListener("change", () => updateSelection());
  select.addEventListener("choices-refresh", () => updateSelection());
  function build() {
    wrapper.replaceChildren();
    const options = [...select.options];
    const long = options.length > 5 || select.dataset.searchable === "true";
    wrapper.classList.toggle("choice-panel", long);
    if (long) {
      const search = document.createElement("input");
      search.type = "search";
      search.placeholder = "Find " + name.toLowerCase() + "…";
      search.setAttribute("aria-label", "Filter " + name.toLowerCase() + " options");
      search.value = filter;
      search.oninput = () => {
        filter = search.value;
        for (const button of wrapper.querySelectorAll("button"))
          button.hidden = !button.textContent.toLowerCase().includes(filter.toLowerCase());
      };
      wrapper.append(search);
    }
    const items = document.createElement("div");
    items.className = "choice-items";
    const buttons = [];
    function update() {
      buttons.forEach(([button, option]) => {
        button.setAttribute("aria-pressed", String(option.selected));
        button.disabled = select.disabled || option.disabled;
      });
    }
    for (const option of options) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = option.textContent;
      button.hidden = !option.textContent.toLowerCase().includes(filter.toLowerCase());
      button.onclick = () => {
        if (select.multiple) option.selected = !option.selected;
        else select.value = option.value;
        update();
        select.dispatchEvent(new Event("change", {bubbles: true}));
      };
      buttons.push([button, option]);
      items.append(button);
    }
    wrapper.append(items);
    updateSelection = update;
    update();
  }
  new MutationObserver(build).observe(select, {childList: true, subtree: true});
  build();
}
if (typeof MutationObserver !== "undefined") {
  for (const select of document.querySelectorAll("select")) enhanceChoices(select);
  new MutationObserver((changes) => {
    for (const change of changes) for (const added of change.addedNodes) {
      if (added.nodeType !== 1) continue;
      if (added.matches("select")) enhanceChoices(added);
      for (const select of added.querySelectorAll("select")) enhanceChoices(select);
    }
  }).observe(document.body, {childList: true, subtree: true});
}
const $ = (id) => document.getElementById(id);
const node = (tag, text = "", className = "") => {
  const result = document.createElement(tag);
  result.textContent = text;
  if (className) result.className = className;
  return result;
};
// Build formatted message content with DOM text nodes; source HTML stays inert.
function messageContent(text) {
  const body = node("div", "", "message-body formatted");
  function inline(parent, value) {
    const tokens = /(`[^`\n]+`|\*\*[^*\n]+\*\*|\[[^\]\n]+\]\(https?:\/\/[^\s)]+\))/g;
    let start = 0;
    for (const match of value.matchAll(tokens)) {
      parent.append(document.createTextNode(value.slice(start, match.index)));
      const token = match[0];
      if (token.startsWith("`")) parent.append(node("code", token.slice(1, -1)));
      else if (token.startsWith("**")) parent.append(node("strong", token.slice(2, -2)));
      else {
        const split = token.indexOf("](");
        const link = node("a", token.slice(1, split));
        link.href = token.slice(split + 2, -1);
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        parent.append(link);
      }
      start = match.index + token.length;
    }
    parent.append(document.createTextNode(value.slice(start)));
  }
  const blocks = text.split(/(```[^\n]*\n[\s\S]*?(?:```|$))/g);
  for (const block of blocks) {
    if (block.startsWith("```")) {
      const firstLine = block.indexOf("\n");
      const pre = node("pre");
      pre.append(node("code", block.slice(firstLine + 1).replace(/```$/, "")));
      body.append(pre);
      continue;
    }
    for (const paragraph of block.split(/\n\s*\n/)) {
      if (!paragraph.trim()) continue;
      const heading = paragraph.match(/^(#{1,4}) (.*)$/);
      const element = node(heading ? "h" + Math.min(heading[1].length + 2, 6) : "p");
      inline(element, heading ? heading[2] : paragraph);
      body.append(element);
    }
  }
  return body;
}
const storageKey = "chatos-token:" + location.origin;
const connectionStorage = typeof localStorage === "undefined" ? sessionStorage : localStorage;
let token = connectionStorage.getItem(storageKey) || sessionStorage.getItem(storageKey) || "";
function acceptLaunchToken() {
  const fragment = new URLSearchParams(location.hash.slice(1));
  if (!fragment.has("token")) return false;
  token = fragment.get("token") || "";
  sessionStorage.setItem(storageKey, token);
  connectionStorage.setItem(storageKey, token);
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
  if (!response.ok) {
    if (response.status === 401) {
      $("result-count").textContent = "Workspace disconnected";
      throw new Error("This browser is disconnected from your workspace. Open ChatOS using its launch link to reconnect; your conversations are still stored locally.");
    }
    throw new Error(data.error || "Request failed");
  }
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
function quantity(count, label) {
  return `${count} ${label}${count === 1 ? "" : "s"}`;
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
  for (const section of ["chats", "map", "context", "health", "setup"])
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
    setup: [
      "Setup & handoff",
      "Choose sources, review context, and carry it with you.",
    ],
    health: [
      "Health & sync",
      "Know what is captured, current, and still missing.",
    ],
  };
  $("page-title").textContent = titles[view][0];
  $("page-title").hidden = view === "chats";
  $("subtitle").textContent = titles[view][1];
  if (view === "chats") await loadChats();
  if (view === "context") await loadContext();
  if (view === "health") renderHealth();
  if (view === "map") await loadMap();
  if (view === "setup") await loadSetup();
}
async function loadChats(append = false) {
  const id = ++requestId;
  const activeFilters = [$("source").value, $("project").value, $("archived").checked].filter(Boolean).length;
  $("filter-summary").textContent = activeFilters ? `Filters · ${activeFilters}` : "Filters";
  const searchState = [activeFilters ? `${activeFilters} filters active` : "", $("search-mode").value === "hybrid" ? "Smart search" : ""].filter(Boolean);
  $("search-tools-summary").title = "Search options" + (searchState.length ? " · " + searchState.join(" · ") : "");
  $("search-tools-summary").classList.toggle("has-filters", activeFilters > 0);
  $("result-count").textContent = $("search").value.trim() ? "Searching your library…" : "Loading conversations…";
  const query = new URLSearchParams({
    q: $("search").value,
    mode: $("search-mode").value || "keyword",
    source: $("source").value,
    project: $("project").value,
    archived: $("archived").checked,
    offset: append ? loaded : 0,
  });
  if (reviewId && useReview) query.set("review", reviewId);
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
    const meta = node("small", "", "result-meta");
    meta.append(
      node("span", chat.source, "pill"),
      document.createTextNode(
        chat.messages + " messages" + (chat.has_note ? " · Note" : ""),
      ),
    );
    card.append(meta, node("small", date(chat.updated_at), "result-date"));
    if (chat.match) {
      const label = chat.match.role === "local_annotation" ? "Local note: " : "";
      card.append(node("p", label + chat.match.excerpt, "search-excerpt"));
    }
    card.onclick = safely(() =>
      openChat(chat.source, chat.id, chat.match?.message_id),
    );
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
  const back = node("button", "Close conversation · Esc", "reader-close");
  back.onclick = () => {
    if (dirty && !confirm("Discard unsaved annotation changes?")) return;
    dirty = false;
    reader.close();
  };
  reader.oncancel = (event) => {
    if (dirty && !confirm("Discard unsaved annotation changes?")) event.preventDefault();
    else dirty = false;
  };
  head.append(back);
  head.append(node("h2", annotation.title || record.title));
  const captureMeta = node(
    "p",
    record.source +
      " · " +
      record.messages.length +
      " messages · " +
      captureLabel(record.capture),
    "muted",
  );
  const incompleteCapture =
    record.capture?.startsWith("partial_") ||
    record.evidence?.warnings?.length ||
    record.evidence?.tool_has_more ||
    record.evidence?.unavailable_message_text?.length;
  if (incompleteCapture) {
    const note = node("span", "", "capture-note");
    const icon = node("button", "!", "capture-note-icon");
    icon.type = "button";
    icon.setAttribute("aria-label", "About this incomplete capture");
    icon.setAttribute("aria-describedby", "capture-note-text");
    const tooltip = node("span", "", "capture-note-tooltip");
    tooltip.id = "capture-note-text";
    tooltip.setAttribute("role", "tooltip");
    tooltip.append(node("strong", "About this capture"));
    const limits = record.limits?.length
      ? record.limits
      : ["Some conversation content could not be captured."];
    for (const limit of limits) tooltip.append(node("span", limit));
    note.append(icon, tooltip);
    captureMeta.append(note);
  }
  head.append(captureMeta);
  if (annotation.title)
    head.append(node("p", "Original title: " + record.title, "source-details"));
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
    const header = node("div", "", "message-header");
    const tags = node("div", "", "message-tags");
    const model = message.model?.trim();
    const modelKnown =
      !!model && !["unknown", "model unknown"].includes(model.toLowerCase());
    const tagClass = "metadata-tag " + (modelKnown ? "model-known" : "model-unknown");
    const modelTag = node("span", modelKnown ? model : "Model unknown", tagClass);
    modelTag.title = modelKnown ? "Captured model name / ID" : "Model not captured";
    tags.append(modelTag);
    header.append(node("span", message.role, "role " + message.role), tags);
    section.append(
      header,
      node("p", date(message.timestamp), "message-meta"),
      messageContent(message.text),
    );
    transcript.append(section);
  }
  reader.append(head, details, transcript);
  if (!reader.open) reader.showModal();
  if (messageId) {
    const message = [...transcript.children].find(
      (item) => item.dataset.messageId === messageId,
    );
    if (message) transcript.scrollTop = message.offsetTop - transcript.offsetTop;
  }
}
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
  mapBaseDocuments = [],
  mapZoom = 1,
  panX = 0,
  panY = 0,
  dragging,
  moved = false,
  mapPositions = [],
  selectedMapKeys = new Set(),
  mapGroup = "",
  mapExpanded = false,
  mapShowAllGroups = false,
  mapListLimit = 40,
  mapRequest = 0,
  mapHandoff;
const mapPalette = [
  "#8eb5ff",
  "#79d4bb",
  "#e5a77d",
  "#b9a0f4",
  "#f18fb8",
  "#e0d780",
  "#79cedf",
  "#b1cd8a",
];
function mapKey(item) {
  return JSON.stringify([item.source, item.id]);
}
function mapColor(group) {
  if (!group || group === "unclustered") return "#a0a7b6";
  const groups = Object.keys(mapData?.groups || {})
    .filter((key) => key !== "unclustered")
    .sort();
  const index = Math.max(0, groups.indexOf(group));
  return mapPalette[index] || `hsl(${(index * 137.5) % 360}, 65%, 70%)`;
}
function mapFilters() {
  return {
    query: $("map-query").value.trim(),
    mode: $("map-search-mode").value,
    source: $("map-source").value,
    project: $("map-project").value,
    group: mapGroup,
    after: $("map-after").value,
    before: $("map-before").value,
    sort: $("map-sort").value,
  };
}
function mapViewFilters() {
  return {
    ...mapFilters(),
    query: mapData?.search?.query || "",
    mode: mapData?.search?.mode || "keyword",
  };
}
async function loadMap() {
  const request = ++mapRequest;
  const filters = mapFilters();
  $("map-summary").textContent = "Loading conversation map…";
  for (const id of [
    "map-assistant",
    "map-export-data",
    "map-export-image",
    "map-select-visible",
  ])
    $(id).disabled = true;
  $("map-handoff").hidden = true;
  const parameters = new URLSearchParams({
    q: filters.query,
    mode: filters.mode,
    source: filters.source,
    project: filters.project,
  });
  try {
    const data = await api("map?" + parameters);
    if (request !== mapRequest) return;
    mapData = data;
  } catch (error) {
    if (request === mapRequest) {
      // Do not leave results from the previous query masquerading as this search.
      mapData = null;
      visibleMapDocuments = [];
      $("map-list").replaceChildren();
      $("map-legend").replaceChildren();
      $("map-summary").textContent =
        "Map search failed. Choose text search or configure local models in Setup & handoff.";
      selectedMapKeys.clear();
      updateMapSelection();
      drawMap();
    }
    throw error;
  }
  const selected = $("map-project").value;
  $("map-project").replaceChildren(option("", "All projects"));
  for (const project of overview.projects)
    $("map-project").append(option(project.id, project.name));
  $("map-project").value = selected;
  filterMap();
}
function filterMap() {
  if (!mapData) return;
  const filters = mapFilters();
  if (filters.after && filters.before && filters.after > filters.before) {
    notice("The start date must be on or before the end date.");
  }
  mapBaseDocuments = (mapData.documents || []).filter(
    (item) =>
      (!filters.project || item.projects.includes(filters.project)) &&
      (!filters.source || item.source === filters.source) &&
      (!filters.after || item.date >= filters.after) &&
      (!filters.before || (item.date && item.date <= filters.before)) &&
      ($("map-noise").checked || item.group !== "unclustered"),
  );
  if (mapGroup && !mapBaseDocuments.some((item) => item.group === mapGroup))
    mapGroup = "";
  visibleMapDocuments = mapBaseDocuments.filter(
    (item) => !mapGroup || item.group === mapGroup,
  );
  visibleMapDocuments.sort((a, b) => {
    if (filters.sort === "title") return a.title.localeCompare(b.title);
    if (filters.sort === "newest")
      return (b.date || "").localeCompare(a.date || "");
    return (
      (a.rank ?? 0) - (b.rank ?? 0) ||
      (b.date || "").localeCompare(a.date || "")
    );
  });
  const visible = new Set(visibleMapDocuments.map(mapKey));
  selectedMapKeys = new Set(
    [...selectedMapKeys].filter((key) => visible.has(key)),
  );
  mapListLimit = 40;
  $("map-handoff").hidden = true;
  $("map-summary").textContent =
    `${visibleMapDocuments.length} of ${mapData.mapped_total ?? mapData.documents.length} mapped conversations · Built ${date(mapData.checked_at)} · ${mapData.freshness_note || "Freshness unverified."}`;
  $("map-search-note").textContent = mapData.search?.note || "";
  $("map-method").textContent =
    `${mapData.method || "Experimental representation"} ${mapData.limits || ""} Labels: distinctive source phrases; sampled text, not verified summaries. Projection quality (neighbor retention): ${mapData.neighbor_retention_5 == null ? "not measured" : Math.round(mapData.neighbor_retention_5 * 100) + "%"}.`;
  renderMapLegend();
  renderMapResults();
  updateMapSelection();
  drawMap();
}
function renderMapLegend() {
  const legend = $("map-legend");
  legend.replaceChildren();
  const all = node(
    "button",
    "All topics · " + mapBaseDocuments.length,
    "topic-chip",
  );
  all.setAttribute("aria-pressed", String(!mapGroup));
  all.onclick = () => {
    mapGroup = "";
    filterMap();
  };
  legend.append(all);
  const counts = new Map();
  for (const item of mapBaseDocuments)
    counts.set(item.group, (counts.get(item.group) || 0) + 1);
  const groups = [...counts].sort((a, b) => b[1] - a[1]);
  for (const [group, count] of groups.filter(
    ([group], index) => mapShowAllGroups || index < 6 || group === mapGroup,
  )) {
    const button = node("button", "", "topic-chip");
    const swatch = node("span", "", "topic-dot");
    swatch.style.backgroundColor = mapColor(group);
    button.append(
      swatch,
      document.createTextNode(
        (mapData.groups[group] || "Mixed topics") + " · " + count,
      ),
    );
    button.setAttribute("aria-pressed", String(mapGroup === group));
    button.onclick = () => {
      mapGroup = mapGroup === group ? "" : group;
      filterMap();
    };
    legend.append(button);
  }
  if (groups.length > 6) {
    const more = node(
      "button",
      mapShowAllGroups ? "Fewer topics" : `+${groups.length - 6} more topics`,
      "topic-chip",
    );
    more.onclick = () => {
      mapShowAllGroups = !mapShowAllGroups;
      renderMapLegend();
    };
    legend.append(more);
  }
}
function renderMapResults() {
  const list = $("map-list");
  list.replaceChildren();
  if (!visibleMapDocuments.length)
    list.append(
      node(
        "p",
        "No conversations match this view. Clear filters or try another concept.",
        "muted",
      ),
    );
  for (const item of visibleMapDocuments.slice(0, mapListLimit)) {
    const card = node("article", "", "map-result");
    card.dataset.mapKey = mapKey(item);
    const selectLabel = node("label", "", "map-result-select");
    const select = node("input");
    select.type = "checkbox";
    select.checked = selectedMapKeys.has(mapKey(item));
    select.setAttribute("aria-label", "Select " + item.title);
    select.onchange = () => {
      if (select.checked) selectedMapKeys.add(mapKey(item));
      else selectedMapKeys.delete(mapKey(item));
      updateMapSelection();
      drawMap();
    };
    selectLabel.append(select);
    const body = node("div", "", "map-result-body");
    const topic = node(
      "span",
      mapData.groups[item.group] || "Mixed topics",
      "map-result-topic",
    );
    topic.style.color = mapColor(item.group);
    const open = node("button", item.title, "map-result-title");
    open.onclick = safely(() =>
      openChat(item.source, item.id, item.match?.message_id),
    );
    body.append(
      topic,
      open,
      node(
        "p",
        `${item.source} · ${item.date || "Date unknown"} · ${captureLabel(item.capture)}`,
        "muted",
      ),
      node(
        "p",
        item.match?.excerpt || item.excerpt || "No captured text preview.",
        "map-result-excerpt",
      ),
    );
    card.append(selectLabel, body);
    list.append(card);
  }
  $("map-more").hidden = mapListLimit >= visibleMapDocuments.length;
}
function updateMapSelection() {
  $("map-selected-count").textContent = selectedMapKeys.size
    ? `${selectedMapKeys.size} selected${selectedMapKeys.size > 200 ? " · select at most 200 for an assistant handoff" : ""}`
    : "No conversations selected";
  $("map-assistant").disabled =
    !selectedMapKeys.size || selectedMapKeys.size > 200;
  $("map-export-data").disabled = !visibleMapDocuments.length;
  $("map-export-image").disabled = !visibleMapDocuments.length;
  $("map-select-visible").disabled = !visibleMapDocuments.length;
  $("map-handoff").hidden = true;
  for (const card of document.querySelectorAll(".map-result"))
    card.classList.toggle("selected", selectedMapKeys.has(card.dataset.mapKey));
}
function drawMap() {
  if (currentView !== "map") return;
  const canvas = $("map-canvas"),
    context = canvas.getContext("2d"),
    docs = visibleMapDocuments,
    width = canvas.clientWidth,
    height = canvas.clientHeight,
    ratio = devicePixelRatio || 1;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.fillStyle = "#171b25";
  context.fillRect(0, 0, width, height);
  mapPositions = [];
  if (!mapData || !docs.length) {
    context.fillStyle = "#a2a6b6";
    context.font = "13px system-ui";
    context.fillText("No mapped conversations in this view", 24, 42);
    return;
  }
  const xs = docs.map((item) => item.x),
    ys = docs.map((item) => item.y),
    minX = Math.min(...xs),
    maxX = Math.max(...xs),
    minY = Math.min(...ys),
    maxY = Math.max(...ys),
    scale =
      Math.min(
        (width - 120) / (maxX - minX || 1),
        (height - 110) / (maxY - minY || 1),
      ) * mapZoom;
  const radii = { compact: 3, balanced: 5, comfortable: 8 },
    radius = radii[$("map-density").value] || 5;
  const centers = new Map();
  for (const item of docs) {
    const x = width / 2 + (item.x - (minX + maxX) / 2) * scale + panX,
      y = height / 2 - (item.y - (minY + maxY) / 2) * scale + panY;
    context.beginPath();
    context.arc(x, y, radius, 0, Math.PI * 2);
    context.fillStyle = mapColor(item.group);
    context.fill();
    if (selectedMapKeys.has(mapKey(item))) {
      context.strokeStyle = "#fff";
      context.lineWidth = 2;
      context.stroke();
    }
    mapPositions.push({ x, y, item });
    const center = centers.get(item.group) || { x: 0, y: 0, count: 0 };
    center.x += x;
    center.y += y;
    center.count++;
    centers.set(item.group, center);
  }
  if ($("map-labels").checked) {
    context.font = "600 12px system-ui";
    const placed = [];
    for (const [group, center] of [...centers].sort(
      (a, b) => b[1].count - a[1].count,
    )) {
      if (group === "unclustered") continue;
      const raw = mapData.groups[group] || "Mixed topics",
        text = raw.length > 40 ? raw.slice(0, 39) + "…" : raw;
      const w = Math.min(context.measureText(text).width + 16, width - 16),
        h = 25;
      const x = Math.max(
        8,
        Math.min(width - w - 8, center.x / center.count - w / 2),
      );
      let y = center.y / center.count - 34;
      for (
        let attempt = 0;
        attempt < 5 &&
        placed.some(
          (p) => x < p.x + p.w && x + w > p.x && y < p.y + h && y + h > p.y,
        );
        attempt++
      )
        y += 30;
      if (
        y < 8 ||
        y + h > height - 8 ||
        placed.some(
          (p) => x < p.x + p.w && x + w > p.x && y < p.y + h && y + h > p.y,
        )
      )
        continue;
      context.fillStyle = "#171b25e8";
      context.fillRect(x, y, w, h);
      context.fillStyle = mapColor(group);
      context.fillText(text, x + 8, y + 17, w - 16);
      placed.push({ x, y, w });
    }
  }
}
function zoom(factor) {
  mapZoom = Math.max(0.25, Math.min(20, mapZoom * factor));
  drawMap();
}
function downloadMapFile(blob, filename) {
  const url = URL.createObjectURL(blob),
    link = node("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function mapSnapshot() {
  const documents = selectedMapKeys.size
    ? visibleMapDocuments.filter((item) => selectedMapKeys.has(mapKey(item)))
    : visibleMapDocuments;
  return {
    schema_version: 1,
    kind: "map_results",
    exported_at: new Date().toISOString(),
    filters: mapViewFilters(),
    map_built_at: mapData?.checked_at,
    map_generation: mapData?.generation,
    method: mapData?.method,
    label_method: mapData?.label_method,
    freshness_note: mapData?.freshness_note,
    selection: documents.map((item) => ({
      source: item.source,
      id: item.id,
      title: item.title,
      path: item.path,
      topic: mapData.groups[item.group],
      group: item.group,
      date: item.date,
      capture: item.capture,
      x: item.x,
      y: item.y,
      evidence: item.match || {
        message_id: item.message_id,
        excerpt: item.excerpt,
      },
    })),
    limits:
      "Exported metadata and preview excerpts, not full transcripts. Topic labels are suggestions. No chats were transmitted.",
  };
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
      ? point.item.title +
        " · " +
        (mapData.groups[point.item.group] || "Mixed topics")
      : "Select a point to highlight its conversation below. Drag to pan; scroll to zoom.";
    return;
  }
  const dx = event.clientX - dragging.x,
    dy = event.clientY - dragging.y;
  moved ||= Math.abs(dx) + Math.abs(dy) > 4;
  panX = dragging.panX + dx;
  panY = dragging.panY + dy;
  drawMap();
};
canvas.onpointerup = () => {
  if (!moved && dragging) {
    const point = mapPositions.find(
      (point) =>
        (point.x - (dragging.x - canvas.getBoundingClientRect().left)) ** 2 +
          (point.y - (dragging.y - canvas.getBoundingClientRect().top)) ** 2 <
        144,
    );
    if (point) {
      const key = mapKey(point.item);
      if (selectedMapKeys.has(key)) selectedMapKeys.delete(key);
      else selectedMapKeys.add(key);
      mapListLimit = Math.max(
        mapListLimit,
        visibleMapDocuments.indexOf(point.item) + 1,
      );
      renderMapResults();
      updateMapSelection();
      drawMap();
      const card = [...document.querySelectorAll(".map-result")].find(
        (card) => card.dataset.mapKey === key,
      );
      card?.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }
  dragging = null;
};
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
$("map-expand").onclick = () => {
  mapExpanded = !mapExpanded;
  $("map-surface").classList.toggle("expanded", mapExpanded);
  $("map-expand").textContent = mapExpanded ? "Collapse map" : "Expand map";
  $("map-expand").setAttribute("aria-pressed", String(mapExpanded));
  drawMap();
};
$("map-export-image").onclick = () =>
  $("map-canvas").toBlob((blob) => {
    if (blob) downloadMapFile(blob, "chatos-map.png");
  });
$("map-export-data").onclick = () =>
  downloadMapFile(
    new Blob([JSON.stringify(mapSnapshot(), null, 2)], {
      type: "application/json",
    }),
    "chatos-map-results.json",
  );
$("map-select-visible").onclick = () => {
  selectedMapKeys = new Set(visibleMapDocuments.map(mapKey));
  renderMapResults();
  updateMapSelection();
  drawMap();
};
$("map-clear-selection").onclick = () => {
  selectedMapKeys.clear();
  renderMapResults();
  updateMapSelection();
  drawMap();
};
$("map-more").onclick = () => {
  mapListLimit += 40;
  renderMapResults();
};
$("map-search-form").onsubmit = safely(async (event) => {
  event.preventDefault();
  await loadMap();
});
$("map-clear").onclick = safely(async () => {
  for (const id of [
    "map-query",
    "map-source",
    "map-project",
    "map-after",
    "map-before",
  ])
    $(id).value = "";
  $("map-search-mode").value = "keyword";
  mapGroup = "";
  $("map-noise").checked = true;
  for (const id of ["map-source", "map-project", "map-search-mode"])
    $(id).dispatchEvent(new Event("choices-refresh"));
  await loadMap();
});
for (const id of ["map-project", "map-source"])
  $(id).onchange = safely(loadMap);
for (const id of ["map-after", "map-before", "map-sort", "map-noise"])
  $(id).onchange = filterMap;
for (const id of ["map-labels", "map-density"]) $(id).onchange = drawMap;
$("map-rebuild").onclick = safely(async () => {
  $("map-rebuild").disabled = true;
  notice(
    "Rebuilding the local semantic map… This may take a moment. Download an embedding model in Setup & handoff first if needed.",
  );
  try {
    await api("map/rebuild", "POST", {});
    await loadMap();
    notice("Semantic map rebuilt from current captured conversations.");
  } finally {
    $("map-rebuild").disabled = false;
  }
});
$("map-assistant").onclick = safely(async () => {
  $("map-assistant").disabled = true;
  try {
    const selection = visibleMapDocuments
      .filter((item) => selectedMapKeys.has(mapKey(item)))
      .map((item) => ({ source: item.source, id: item.id }));
    mapHandoff = await api("map/handoff", "POST", {
      selection,
      filters: mapViewFilters(),
      map_fingerprint: mapData.input_fingerprint,
      map_generation: mapData.generation,
    });
    $("map-handoff-prompt").value = mapHandoff.prompt;
    $("map-handoff").hidden = false;
  } finally {
    $("map-assistant").disabled =
      !selectedMapKeys.size || selectedMapKeys.size > 200;
  }
});
$("map-copy-prompt").onclick = safely(async () => {
  await navigator.clipboard.writeText($("map-handoff-prompt").value);
  notice("Assistant request copied.");
});
$("map-download-handoff").onclick = () => {
  if (mapHandoff)
    downloadMapFile(
      new Blob([JSON.stringify(mapHandoff.snapshot, null, 2)], {
        type: "application/json",
      }),
      "chatos-exploration-selection.json",
    );
};
window.addEventListener("resize", drawMap);
window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && mapExpanded) $("map-expand").click();
});

for (const button of document.querySelectorAll("[data-view]"))
  button.onclick = safely(async () => {
    await startup;
    await showView(button.dataset.view);
  });
let timer;
const navigationLabels = {chats: "Conversations", map: "Conversation map", context: "Skills & memory", health: "Health & sync", setup: "Setup & handoff"};
for (const button of document.querySelectorAll("[data-view]")) {
  button.setAttribute("aria-label", navigationLabels[button.dataset.view]);
  button.title = navigationLabels[button.dataset.view];
}
$("nav-toggle").onclick = () => {
  const collapsed = $("app-shell").classList.toggle("nav-collapsed");
  const label = collapsed ? "Expand navigation" : "Collapse navigation";
  $("nav-toggle").setAttribute("aria-expanded", String(!collapsed));
  $("nav-toggle").setAttribute("aria-label", label);
  $("nav-toggle").title = label;
};
$("show-previews").onchange = () => $("chat-list").classList.toggle("show-previews", $("show-previews").checked);
window.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    showView("chats").then(() => $("search").focus());
  }
});
$("search").oninput = () => {
  useReview = false;
  clearTimeout(timer);
  timer = setTimeout(
    safely(() => loadChats()),
    220,
  );
};
let reviewId = "", useReview = false, modelConfig;
function initializeSearchFilters() {
  const reset = $("reset-search-filters");
  // This component is absent from minimal startup fixtures.
  if (!document.querySelectorAll(".filter-menu").length) return;
  const filters = $("search-filters");
  const project = $("project");
  function updateProjectLabel() {
    $("selected-filter-project").textContent = project.selectedOptions[0]?.textContent || "All projects";
  }
  project.addEventListener("change", updateProjectLabel);
  reset.onclick = safely(() => {
    for (const id of ["source", "project"]) {
      $(id).value = "";
      $(id).dispatchEvent(new Event("choices-refresh"));
    }
    $("archived").checked = false;
    $("show-previews").checked = false;
    $("chat-list").classList.remove("show-previews");
    updateProjectLabel();
    useReview = false;
    return loadChats();
  });
  document.addEventListener("click", event => {
    if (!filters.contains(event.target)) filters.open = false;
  });
  filters.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      filters.open = false;
      $("search-tools-summary").focus();
    }
  });
}
initializeSearchFilters();
// Quick icons and the explanatory chooser share the existing search contract.
function initializeSearchModePicker() {
  const select = $("search-mode");
  const chooser = $("mode-chooser");
  if (!chooser) return;
  const buttons = document.querySelectorAll("[data-search-mode]");
  if (!buttons.length) return;
  function update() {
    for (const button of buttons)
      button.setAttribute("aria-pressed", String(button.dataset.searchMode === select.value));
    $("selected-search-mode").textContent = select.selectedOptions[0].textContent;
  }
  for (const button of buttons) button.onclick = () => {
    const changed = select.value !== button.dataset.searchMode;
    select.value = button.dataset.searchMode;
    const wasOpen = chooser.open;
    chooser.open = false;
    if (wasOpen) chooser.querySelector("summary").focus();
    update();
    if (changed) select.dispatchEvent(new Event("change", {bubbles: true}));
  };
  select.addEventListener("change", update);
  document.addEventListener("click", event => {
    if (!chooser.contains(event.target)) chooser.open = false;
  });
  chooser.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      chooser.open = false;
      chooser.querySelector("summary").focus();
    }
  });
  update();
}
initializeSearchModePicker();
$("search-mode").onchange = safely(() => { useReview = false; return loadChats(); });
$("chief-search").onclick = safely(async () => {
  const request = await api("search-review", "POST", {
    q: $("search").value, source: $("source").value,
    project: $("project").value, archived: $("archived").checked,
  });
  reviewId = request.id;
  $("chief-prompt").hidden = false;
  $("chief-prompt").value = request.prompt;
  $("chief-results").hidden = false;
  notice("Give this request to your Chief of Staff with local file access, then load its results here.");
});
$("chief-results").onclick = safely(async () => { useReview = true; await loadChats(); });
async function loadSearchModels() {
  const state = await api("search-models");
  modelConfig = state.settings;
  $("embedding-model").value = modelConfig.embedding.model_id;
  $("reranker-model").value = modelConfig.reranker.model_id;
  $("model-json").value = JSON.stringify(modelConfig, null, 2);
  $("model-status").textContent = (state.runtime_ready ? "Runtime ready. " : "Install optional semantic dependencies and restart the app in that environment. ") +
    "Embedding: " + (state.downloaded.embedding ? "downloaded" : "not downloaded") +
    "; reranker: " + (state.downloaded.reranker ? "downloaded" : "not downloaded");
}
$("save-models").onclick = safely(async () => {
  modelConfig.embedding.model_id = $("embedding-model").value.trim();
  modelConfig.reranker.model_id = $("reranker-model").value.trim();
  await api("search-models", "PUT", modelConfig);
  await loadSearchModels();
});
$("save-model-json").onclick = safely(async () => {
  await api("search-models", "PUT", JSON.parse($("model-json").value));
  await loadSearchModels();
});
for (const kind of ["embedding", "reranker"]) $("download-" + kind).onclick = safely(async () => {
  $("download-" + kind).disabled = true;
  notice("Downloading the saved " + kind + " model. This may take a few minutes.");
  try {
    await api("search-models/download", "POST", {kind});
    await loadSearchModels();
    notice("Model download complete.");
  } finally { $("download-" + kind).disabled = false; }
});
$("build-embeddings").onclick = safely(async () => {
  $("build-embeddings").disabled = true;
  notice("Indexing a batch of captured passages…");
  try {
    const state = await api("search-models/build", "POST", {});
    notice(state.current_vectors + " passages indexed; " + state.remaining + " remaining. Repeat to continue.");
  } finally { $("build-embeddings").disabled = false; }
});
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
  await startup;
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
// Queue navigation until the initial overview and default view are ready.
const startup = (async () => {
  await refreshOverview();
  await showView(overview.chats || overview.archived ? "chats" : "setup");
})();
startup.catch((error) => notice(error.message, true));

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



window.addEventListener(
  "hashchange",
  safely(async () => {
    if (!acceptLaunchToken()) return;
    await refreshOverview();
    await showView(currentView);
    notice("Reconnected to the local workspace.");
  }),
);

async function loadSetup() {
  await loadSearchModels();
  const status = await api("setup");
  $("setup-controls").hidden = !status.supported;
  $("setup-summary").textContent = status.supported
    ? `${quantity(status.records, "captured conversation")} · ${quantity(status.pending_context_ids.length, "artifact")} awaiting review · ${quantity(status.database_backups, "database backup")}. ${status.next_action}`
    : status.detail;
  if (!status.supported) return;
  $("skill-path").textContent = status.assistant_skill_ready
    ? `${overview.workspace}/shared_context/skills/chatos/SKILL.md`
    : "Prepare the skill to connect your Chief of Staff to this workspace.";
  $("codex-enabled").checked = status.codex_enabled;
  $("codex-path").value = status.codex_path || "";
  $("guide-path").textContent = status.assistant_guide_ready
    ? `${overview.workspace}/ASSISTANT.md`
    : "Create the optional guide when you want assistant access.";
  $("handoff-project").replaceChildren(
    ...overview.projects.map((p) => option(p.id, p.name)),
  );
  const selected = $("handoff-chat").value;
  const choices = [];
  for (const archived of [false, true]) {
    let offset = 0,
      page;
    do {
      page = await api(
        "chats?" + new URLSearchParams({ archived, offset, limit: 100 }),
      );
      choices.push(
        ...page.items.map((chat) =>
          option(
            `${chat.source}:${chat.id}`,
            `${chat.title} · ${chat.source}${archived ? " · archived" : ""}`,
          ),
        ),
      );
      offset += page.items.length;
    } while (page.items.length && offset < page.total);
  }
  $("handoff-chat").replaceChildren(...choices);
  const preferred = current
    ? `${current.record.source}:${current.record.id}`
    : selected;
  if (choices.some((choice) => choice.value === preferred))
    $("handoff-chat").value = preferred;
  const data = await api("artifacts");
  $("artifact-list").replaceChildren();
  if (!data.items.length)
    $("artifact-list").append(
      node("p", "No context artifacts imported yet.", "muted"),
    );
  for (const item of data.items) {
    const button = node(
      "button",
      `${item.kind} · ${item.review_status} · ${item.id.slice(0, 8)}`,
    );
    button.onclick = safely(() => reviewContext(item.id));
    $("artifact-list").append(button);
  }
  updateHandoffSelection();
}
async function reviewContext(identity) {
  const record = await api("artifact?" + new URLSearchParams({ id: identity }));
  const content = $("artifact-review");
  const artifact = record.artifact;
  content.replaceChildren(
    node("h3", `Review ${artifact.kind.replaceAll("_", " ")}`),
    node(
      "p",
      `${record.review_status} · Prepared ${date(artifact.created_at)} · ${artifact.generated_by}`,
    ),
    node("pre", artifact.body),
    node("h4", "Supporting sources"),
  );
  const references = node("ul");
  for (const reference of artifact.source_references)
    references.append(node("li", reference));
  if (!artifact.source_references.length)
    references.append(
      node(
        "li",
        "No supporting sources were supplied. Verify the claims independently.",
      ),
    );
  content.append(references, node("h4", "Uncertainty and scope"));
  const uncertainty = node("ul");
  for (const item of artifact.uncertainties)
    uncertainty.append(node("li", item));
  if (!artifact.uncertainties.length)
    uncertainty.append(
      node(
        "li",
        "No uncertainty was recorded. This does not establish completeness.",
      ),
    );
  content.append(uncertainty);
  if (record.review_history?.length || record.review_note) {
    content.append(node("h4", "Review history"));
    for (const review of record.review_history || [
      {
        review_status: record.review_status,
        reviewed_at: record.reviewed_at,
        review_note: record.review_note,
      },
    ]) {
      content.append(
        node(
          "p",
          `${review.status || review.review_status} · ${date(review.reviewed_at)} · ${review.review_note}`,
        ),
      );
    }
  }
  const provenance = node("details");
  provenance.append(
    node("summary", "Retained JSON and integrity metadata"),
    node("pre", JSON.stringify(record, null, 2)),
  );
  content.append(provenance);
  if (record.review_status === "accepted") {
    content.append(
      node(
        "p",
        "Accepted in this workspace. Review its scope again before using it for another task.",
      ),
    );
  }
  const retiring = record.review_status === "accepted";
  const form = node("form", "", "form-grid");
  const label = node(
      "label",
      retiring
        ? "Why should this context stop being reused?"
        : "Your review note",
    ),
    note = node("textarea");
  note.required = true;
  note.maxLength = 4000;
  note.placeholder =
    "What sources did you verify, and where should this context apply?";
  label.append(note);
  const submit = node(
    "button",
    retiring ? "Retire context" : "Accept reviewed context",
  );
  submit.type = "submit";
  form.append(label, submit);
  form.onsubmit = safely(async (event) => {
    event.preventDefault();
    submit.disabled = true;
    try {
      await api(retiring ? "artifact/retire" : "artifact/accept", "POST", {
        id: identity,
        review_note: note.value,
      });
      await loadSetup();
      await reviewContext(identity);
      notice(
        retiring
          ? "Context retired from retrieval and future bundles. Its source and review history are preserved."
          : "Context accepted and indexed for cited retrieval. No host instructions were installed.",
      );
    } finally {
      submit.disabled = false;
    }
  });
  content.append(form);
}
function updateHandoffSelection() {
  const selection = $("handoff-selection").value;
  $("handoff-chat-label").hidden = selection !== "chat";
  $("handoff-project-label").hidden = selection !== "project";
}
$("handoff-selection").onchange = updateHandoffSelection;
$("source-form").onsubmit = safely(async (event) => {
  event.preventDefault();
  const result = await api("source/codex", "POST", {
    enabled: $("codex-enabled").checked,
    path: $("codex-path").value,
  });
  await loadSetup();
  notice(result.detail);
});
$("make-guide").onclick = safely(async () => {
  const result = await api("guide", "POST", {});
  $("guide-path").textContent = result.path;
  notice(
    "Assistant guide ready. Give this local file to an assistant when you choose to use it.",
  );
});
$("artifact-file").onchange = safely(async () => {
  const input = $("artifact-file"),
    file = input.files[0];
  if (!file) return;
  try {
    if (file.size > 1024 * 1024)
      throw new Error("Context artifacts must be JSON files up to 1 MiB.");
    const result = await api(
      "artifact/import",
      "POST",
      JSON.parse(await file.text()),
    );
    await loadSetup();
    await reviewContext(result.id);
    notice(
      "Artifact received. Inspect its sources and uncertainty before accepting.",
    );
  } finally {
    input.value = "";
  }
});
$("handoff-form").onsubmit = safely(async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector("button[type=submit]");
  button.disabled = true;
  try {
    const selection = $("handoff-selection").value;
    const body = { with_context: $("handoff-context").checked };
    if (selection === "chat") {
      if (!$("handoff-chat").value)
        throw new Error("Import a conversation before exporting it.");
      body.conversations = [$("handoff-chat").value];
    } else if (selection === "project") {
      if (!$("handoff-project").value)
        throw new Error(
          "No project is registered yet. Select a conversation instead.",
        );
      body.project = $("handoff-project").value;
    } else body.all = true;
    const result = await api("bundle", "POST", body);
    $("handoff-result").replaceChildren(
      node("h3", "Portable bundle verified"),
      node(
        "p",
        `${quantity(result.conversations, "conversation")} · ${quantity(result.visible_messages, "message")} · ${quantity(result.context_files, "context file")}`,
      ),
      node("pre", result.directory),
      node(
        "p",
        "Open this folder on your computer and read START_HERE.md. Review the selected files before giving them to another app. Nothing has been uploaded.",
      ),
    );
    notice("Your selected portable bundle is ready locally.");
  } finally {
    button.disabled = false;
  }
});

$("make-skill").onclick = safely(async () => {
  await startup;
  const button = $("make-skill");
  button.disabled = true;
  try {
    const result = await api("assistant-skill", "POST", {});
    $("skill-path").textContent = result.entrypoint;
    notice(
      "ChatOS skill prepared. Give SKILL.md to your assistant or install the folder in its documented skill location, then verify discovery.",
    );
  } finally {
    button.disabled = false;
  }
});
