import {
  BarChart3,
  Bot,
  BrainCircuit,
  CalendarDays,
  CreditCard,
  FileClock,
  FolderKanban,
  Gauge,
  KeyRound,
  LayoutDashboard,
  Settings,
  Sparkles,
  TrendingUp,
  Video,
  Workflow,
  Send,
  UserRound,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import "../styles/n30-fast-ui.css";

const groups = [
  {
    label: "WORKSPACE",
    items: [
      ["Dashboard", "/app", LayoutDashboard, true],
      ["N1MOX Assistant", "/app/assistant", Bot],
      ["Create", "/app/create", Sparkles],
      ["Workflows", "/app/workflows", Workflow],
    ],
  },
  {
    label: "INTELLIGENCE",
    items: [
      ["Intelligence", "/app/intelligence", BrainCircuit],
      ["Research", "/app/research", FolderKanban],
      ["Analytics", "/app/analytics", BarChart3],
      ["Growth", "/app/growth", TrendingUp],
    ],
  },
  {
    label: "PUBLISH",
    items: [
      ["YouTube", "/app/youtube", Video],
      ["Publishing Center", "/app/publishing", Send],
      ["Scheduler", "/app/schedules", CalendarDays],
      ["AI Studio", "/app/ai-studio", Gauge],
      ["History", "/app/ai-history", FileClock],
    ],
  },
  {
    label: "ACCOUNT",
    items: [
      ["Connected Accounts", "/app/accounts", UserRound],
      ["BYOK / API Keys", "/app/byok", KeyRound],
      ["Billing & Plans", "/app/billing", CreditCard],
      ["Settings", "/app/settings", Settings],
    ],
  },
];

export default function Sidebar({ sidebarOpen }) {
  return (
    <aside className={`sidebar n30-sidebar ${sidebarOpen ? "sidebar-open" : "closed"}`}>
      <div className="n30-side-brand">
        <div className="n30-side-mark">N</div>
        {sidebarOpen && (
          <div>
            <strong>N1MOX30</strong>
            <span>Creator Operating System</span>
          </div>
        )}
      </div>

      <nav className="nav-menu n30-nav-menu">
        {groups.map((group) => (
          <div className="n30-nav-group" key={group.label}>
            {sidebarOpen && <div className="n30-nav-label">{group.label}</div>}
            {group.items.map(([name, path, Icon, end]) => (
              <NavLink
                key={name}
                to={path}
                end={end === true}
                title={!sidebarOpen ? name : undefined}
                className={({ isActive }) =>
                  `nav-item n30-nav-item ${isActive ? "active" : ""}`
                }
              >
                <Icon size={17} strokeWidth={1.8} />
                {sidebarOpen && <span>{name}</span>}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {sidebarOpen && (
        <div className="n30-side-status">
          <span />
          <div>
            <strong>N1MOX Engine</strong>
            <small>Systems operational</small>
          </div>
        </div>
      )}
    </aside>
  );
}
