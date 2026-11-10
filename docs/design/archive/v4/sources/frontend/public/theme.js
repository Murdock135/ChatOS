(function () {
  const storageKey = "smriti-theme";
  const root = document.documentElement;
  if (!root) return;

  function savedTheme() {
    try {
      const value = localStorage.getItem(storageKey);
      return value === "light" || value === "dark" ? value : null;
    } catch {
      return null;
    }
  }

  function systemTheme() {
    return typeof matchMedia === "function" && matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }

  function applyTheme(theme) {
    root.dataset.theme = theme;
    root.style.colorScheme = theme;
    const button = document.getElementById("theme-toggle");
    if (button) {
      const target = theme === "light" ? "dark" : "light";
      button.textContent = target === "light" ? "Light mode" : "Dark mode";
      button.setAttribute("aria-label", "Switch to " + target + " mode");
      button.setAttribute("aria-pressed", String(theme === "light"));
    }
    window.dispatchEvent(new Event("smriti-theme-change"));
  }

  applyTheme(savedTheme() || systemTheme());

  function bindThemeButton() {
    const button = document.getElementById("theme-toggle");
    if (!button) return;
    applyTheme(root.dataset.theme);
    button.addEventListener("click", function () {
      const nextTheme = root.dataset.theme === "light" ? "dark" : "light";
      applyTheme(nextTheme);
      try {
        localStorage.setItem(storageKey, nextTheme);
      } catch {
        // The current session still works when browser storage is unavailable.
      }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bindThemeButton, { once: true });
  else bindThemeButton();
})();
