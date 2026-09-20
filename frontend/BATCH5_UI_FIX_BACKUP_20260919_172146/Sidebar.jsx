import {
  BarChart3,
  Bot,
  BrainCircuit,
  CalendarDays,
  ChevronRight,
  Compass,
  FileClock,
  FolderKanban,
  Gauge,
  LayoutDashboard,
  Settings,
  Sparkles,
  TrendingUp,
  Video,
  Workflow,
  Send,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const groups = [
  {
    label: "WORKSPACE",
    items: [
      {
        name: "Dashboard",
        path: "/app",
        icon: LayoutDashboard,
        end: true,
      },
      {
        name: "N1MOX Assistant",
        path: "/app/assistant",
        icon: Bot,
      },
      {
        name: "Create",
        path: "/app/create",
        icon: Sparkles,
        accent: true,
      },
      {
        name: "Workflows",
        path: "/app/workflows",
        icon: Workflow,
      },
    ],
  },
  {
    label: "INTELLIGENCE",
    items: [
      {
        name: "Intelligence",
        path: "/app/intelligence",
        icon: BrainCircuit,
      },
      {
        name: "Research",
        path: "/app/research",
        icon: Compass,
      },
      {
        name: "Analytics",
        path: "/app/analytics",
        icon: BarChart3,
      },
      {
        name: "Growth",
        path: "/app/growth",
        icon: TrendingUp,
      },
    ],
  },
  {
    label: "PUBLISH",
    items: [
      {
        name: "Video",
        path: "/app/publishing",
        icon: Video,
      },
      {
        name: "Publishing Center",
        path: "/app/publishing",
        icon: Send,
      },
      {
        name: "Daily Workspace",
        path: "/app/daily",
        icon: CalendarDays,
      },
      {
        name: "Scheduler",
        path: "/app/schedules",
        icon: CalendarDays,
      },
      {
        name: "AI Studio",
        path: "/app/ai-studio",
        icon: Gauge,
      },
      {
        name: "History",
        path: "/app/ai-history",
        icon: FileClock,
      },
    ],
  },
  {
    label: "SYSTEM",
    items: [
      {
        name: "Notifications",
        path: "/app/notifications",
        icon: FolderKanban,
      },
      {
        name: "Accounts",
        path: "/app/accounts",
        icon: Video,
      },
      {
        name: "Settings",
        path: "/app/settings",
        icon: Settings,
      },
    ],
  },
];

function Sidebar({ sidebarOpen }) {
  return (
    <aside
      className={`sidebar ${
        sidebarOpen ? "sidebar-open" : "closed"
      }`}
      aria-label="N1MOX30 navigation"
    >
      <div className="brand">
        <div className="brand-logo" aria-hidden="true">
          N
        </div>

        {sidebarOpen && (
          <div className="brand-text">
            <h1>N1MOX30</h1>
            <span>Creator Operating System</span>
          </div>
        )}
      </div>

      <nav className="nav-menu" aria-label="Primary navigation">
        {groups.map((group) => (
          <div
            key={group.label}
            className="n1-nav-group"
          >
            {sidebarOpen && (
              <div className="n1-nav-label">
                {group.label}
              </div>
            )}

            {group.items.map((item) => {
              const Icon = item.icon;

              return (
                <NavLink
                  key={`${item.path}-${item.name}`}
                  to={item.path}
                  end={item.end === true}
                  title={
                    sidebarOpen
                      ? undefined
                      : item.name
                  }
                  className={({ isActive }) =>
                    [
                      "nav-item",
                      isActive ? "active" : "",
                      item.accent
                        ? "nav-create"
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" ")
                  }
                >
                  <Icon
                    size={18}
                    strokeWidth={2}
                  />

                  {sidebarOpen && (
                    <span>{item.name}</span>
                  )}

                  {sidebarOpen && (
                    <ChevronRight
                      className="n1-nav-arrow"
                      size={14}
                    />
                  )}
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      {sidebarOpen && (
        <div className="n1-sidebar-status">
          <span className="n1-status-pulse" />

          <div>
            <strong>N1MOX Engine</strong>
            <small>Systems operational</small>
          </div>
        </div>
      )}
    </aside>
  );
}

export default Sidebar;