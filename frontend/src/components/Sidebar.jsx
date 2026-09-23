import {
  BarChart3,
  Bot,
  CalendarDays,
  CreditCard,
  FileText,
  Home,
  KeyRound,
  LayoutGrid,
  LineChart,
  Settings,
  Sparkles,
  Users,
  Video,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const groups = [
  {
    label: "WORKSPACE",
    items: [
      ["/app", "Dashboard", Home],
      ["/app/create", "Create", Sparkles],
      ["/app/workflows", "Workflows", LayoutGrid],
      ["/app/research", "Research", FileText],
      ["/app/analytics", "Analytics", BarChart3],
      ["/app/growth", "Growth", LineChart],
    ],
  },
  {
    label: "PUBLISH",
    items: [
      ["/app/youtube", "YouTube", Video],
      ["/app/accounts", "Connected Accounts", Users],
      ["/app/schedules", "Scheduler", CalendarDays],
    ],
  },
  {
    label: "SYSTEM",
    items: [
      ["/app/assistant", "N1MOX Assistant", Bot],
      ["/app/byok", "Bring Your Own API", KeyRound],
      ["/app/billing", "Billing & Plans", CreditCard],
      ["/app/settings", "Settings", Settings],
    ],
  },
];

export default function Sidebar({ sidebarOpen = true }) {
  return (
    <aside className={`nm-sidebar ${sidebarOpen ? "is-open" : "is-closed"}`}>

      <div className="nm-sidebar-brand">
        <span className="nm-brand-mark">N</span>

        {sidebarOpen && (
          <div>
            <strong>N1MOX30</strong>
            <small>Creator OS</small>
          </div>
        )}
      </div>

      <nav className="nm-sidebar-nav">

        {groups.map((group) => (
          <div className="nm-nav-group" key={group.label}>

            {sidebarOpen && (
              <span className="nm-nav-label">
                {group.label}
              </span>
            )}

            {group.items.map(([to, label, Icon]) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/app"}
                className={({ isActive }) =>
                  `nm-nav-link ${isActive ? "active" : ""}`
                }
              >
                <Icon size={18} strokeWidth={1.8} />

                {sidebarOpen && (
                  <span>{label}</span>
                )}
              </NavLink>
            ))}

          </div>
        ))}

      </nav>
    </aside>
  );
}

