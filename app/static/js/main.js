/**
 * LexiLegal AI — Vanilla Frontend Support
 * Theme toggle persistence & CSRF-aware fetch wrapper
 */

(function () {
  "use strict";

  // 1. Theme Toggle Persistence
  const THEME_STORAGE_KEY = "lexilegal_theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
      themeBtn.innerHTML = theme === "dark" ? "☀️ Light" : "🌙 Dark";
      themeBtn.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);
    }
  }

  function initTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light");
    applyTheme(initialTheme);

    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        localStorage.setItem(THEME_STORAGE_KEY, newTheme);
        applyTheme(newTheme);
      });
    }
  }

  // 2. CSRF Token Retrieval Helper
  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute("content") : "";
  }

  // Expose global helper for future AJAX calls
  window.LexiLegal = {
    getCsrfToken: getCsrfToken,
    fetchWithCsrf: function (url, options) {
      options = options || {};
      options.headers = options.headers || {};
      const token = getCsrfToken();
      if (token && !options.headers["X-CSRFToken"]) {
        options.headers["X-CSRFToken"] = token;
      }
      return fetch(url, options);
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
  });
})();
