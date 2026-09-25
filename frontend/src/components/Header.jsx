import {
  Bell,
  Command,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Search,
  Sparkles,
  Sun,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import N1MOXVoiceControl from "./N1MOXVoiceControl";

import api from "../api/client";

function getInitialTheme() {
  const saved = localStorage.getItem("n1mox-theme");

  if (saved === "dark" || saved === "light") {
    return saved;
  }

  return "light";
}

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem("user") || "{}");
  } catch {
    return {};
  }
}

function Header({ sidebarOpen, setSidebarOpen }) {
  const navigate = useNavigate();

  const [theme, setTheme] = useState(getInitialTheme);
  const [creatorProfile, setCreatorProfile] = useState(null);

  const storedUser = getStoredUser();

  const [userName, setUserName] = useState(
    storedUser.full_name ||
      storedUser.fullName ||
      storedUser.name ||
      "Creator"
  );

  /* =========================================================
     LOAD CREATOR PROFILE
     ========================================================= */

  useEffect(() => {
    let mounted = true;

    async function loadCreatorProfile() {
      try {
        const response = await api.get("/creator-profile/me");

        if (!mounted) {
          return;
        }

        const profile = response.data || {};

        setCreatorProfile(profile);

        if (profile.creator_name?.trim()) {
          setUserName(profile.creator_name.trim());
        }
      } catch {
        /*
         * A creator profile may not exist yet.
         * Keep displaying the authenticated user's name.
         */
      }
    }

    loadCreatorProfile();

    return () => {
      mounted = false;
    };
  }, []);

  /* =========================================================
     THEME
     ========================================================= */

  useEffect(() => {
    document.documentElement.dataset.n1moxTheme = theme;
    localStorage.setItem("n1mox-theme", theme);
  }, [theme]);

  function changeTheme(nextTheme) {
    setTheme(nextTheme);
  }

  /* =========================================================
     CREATOR DISPLAY
     ========================================================= */

  const displayName =
    creatorProfile?.creator_name?.trim() ||
    userName ||
    "Creator";

  const initial =
    displayName.trim().charAt(0).toUpperCase() || "N";

  return (
    <header className="n1-header">
      {/* =====================================================
          LEFT
          ===================================================== */}

      <div className="n1-header-left">
        <button
          type="button"
          className="n1-sidebar-toggle"
          onClick={() => setSidebarOpen((value) => !value)}
          title={
            sidebarOpen ? "Collapse navigation" : "Expand navigation"
          }
          aria-label={
            sidebarOpen ? "Collapse navigation" : "Expand navigation"
          }
        >
          {sidebarOpen ? (
            <PanelLeftClose size={18} />
          ) : (
            <PanelLeftOpen size={18} />
          )}
        </button>
      </div>

      {/* =====================================================
          SEARCH
          ===================================================== */}

      <div className="n1-global-search">
        <Search size={16} />

        <input
          aria-label="Search N1MOX30"
          placeholder="Search content, workflows, insights..."
        />

        <span className="n1-search-key">
          <Command size={11} />
          K
        </span>
      </div>

      {/* =====================================================
          RIGHT ACTIONS
          ===================================================== */}

      <div className="n1-header-voice">
        <N1MOXVoiceControl />
      </div>
      <div className="n1-header-actions">
        {/* =================================================
            THEME
            ================================================= */}

        <div
          className="n1-theme-switcher"
          role="group"
          aria-label="Theme"
        >
          <button
            type="button"
            className={`n1-theme-option ${
              theme === "dark" ? "active" : ""
            }`}
            onClick={() => changeTheme("dark")}
            aria-pressed={theme === "dark"}
            title="Dark theme"
          >
            <Moon size={14} />
            <span>Dark</span>
          </button>

          <button
            type="button"
            className={`n1-theme-option ${
              theme === "light" ? "active" : ""
            }`}
            onClick={() => changeTheme("light")}
            aria-pressed={theme === "light"}
            title="Light theme"
          >
            <Sun size={14} />
            <span>Light</span>
          </button>
        </div>

        {/* =================================================
            ASSISTANT
            ================================================= */}

        <button
          type="button"
          className="n1-header-action"
          title="N1MOX Assistant"
          aria-label="N1MOX Assistant"
          onClick={() => navigate("/app/assistant")}
        >
          <Sparkles size={17} />
        </button>

        {/* =================================================
            NOTIFICATIONS
            ================================================= */}

        <button
          type="button"
          className="n1-header-action n1-notification-button"
          title="Notifications"
          aria-label="Notifications"
          onClick={() => navigate("/app/notifications")}
        >
          <Bell size={17} />
          <span />
        </button>

        {/* =================================================
            CREATE
            ================================================= */}

        <button
          type="button"
          className="n1-create-button"
          onClick={() => navigate("/app/create")}
        >
          <Plus size={16} />
          <span>Create</span>
        </button>

        {/* =================================================
            CREATOR PROFILE
            ================================================= */}

        <button
          type="button"
          className="n1-header-user n1-header-user-button"
          onClick={() => navigate("/app/profile")}
          title="Open creator profile"
          aria-label="Open creator profile"
        >
          <div className="n1-user-avatar">
            {initial}
          </div>

          <div className="n1-user-details">
            <strong>{displayName}</strong>
            <span>Creator workspace</span>
          </div>
        </button>
      </div>
    </header>
  );
}

export default Header;
