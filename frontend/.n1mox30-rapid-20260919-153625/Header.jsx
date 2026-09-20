import {
  Bell,
  Command,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Search,
  Sparkles,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

function Header({ sidebarOpen, setSidebarOpen }) {
  const navigate = useNavigate();

  const userName = (() => {
    try {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      return user.full_name || user.fullName || user.name || "Creator";
    } catch {
      return "Creator";
    }
  })();

  const initial = userName.trim().charAt(0).toUpperCase() || "N";

  return (
    <header className="n1-header">
      <div className="n1-header-left">
        <button
          type="button"
          className="n1-sidebar-toggle"
          onClick={() => setSidebarOpen((value) => !value)}
          aria-label={
            sidebarOpen ? "Collapse navigation" : "Expand navigation"
          }
        >
          {sidebarOpen ? (
            <PanelLeftClose size={19} />
          ) : (
            <PanelLeftOpen size={19} />
          )}
        </button>
      </div>

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

      <div className="n1-header-actions">
        <button
          type="button"
          className="n1-header-action"
          title="N1MOX Assistant"
          aria-label="N1MOX Assistant"
          onClick={() => navigate("/app/assistant")}
        >
          <Sparkles size={17} />
        </button>

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

        <button
          type="button"
          className="n1-create-button"
          onClick={() => navigate("/app/create")}
        >
          <Plus size={16} />
          <span>Create</span>
        </button>

        <div className="n1-header-user">
          <div className="n1-user-avatar">{initial}</div>

          <div className="n1-user-details">
            <strong>{userName}</strong>
            <span>Creator workspace</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;