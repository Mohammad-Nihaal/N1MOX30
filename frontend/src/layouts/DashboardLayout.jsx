import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";

import Header from "../components/Header";
import Sidebar from "../components/Sidebar";

function DashboardLayout() {
  const location = useLocation();

  const [sidebarOpen, setSidebarOpen] =
    useState(() => {
      const saved =
        localStorage.getItem(
          "n1mox_sidebar_open"
        );

      if (saved === null) {
        return true;
      }

      return saved === "true";
    });

  useEffect(() => {
    localStorage.setItem(
      "n1mox_sidebar_open",
      String(sidebarOpen)
    );
  }, [sidebarOpen]);

  useEffect(() => {
    const pageTitles = {
      "/app": "Dashboard",
      "/app/assistant": "N1MOX Assistant",
      "/app/create": "Create",
      "/app/workflows": "Workflows",
      "/app/intelligence": "Intelligence",
      "/app/research": "Research",
      "/app/analytics": "Analytics",
      "/app/growth": "Growth",
      "/app/publishing": "Publishing Center",
      "/app/daily": "Daily Workspace",
      "/app/schedules": "Scheduler",
      "/app/ai-studio": "AI Studio",
      "/app/ai-history": "AI History",
      "/app/notifications": "Notifications",
      "/app/accounts": "Connected Accounts",
      "/app/settings": "Settings",
      "/app/usage": "Usage",
    };

    const pageTitle =
      pageTitles[location.pathname] ||
      "Creator Operating System";

    document.title = `${pageTitle} · N1MOX30`;
  }, [location.pathname]);

  return (
    <div
      className={`app ${
        sidebarOpen
          ? "sidebar-is-open"
          : "sidebar-is-closed"
      }`}
    >
      <Sidebar
        sidebarOpen={sidebarOpen}
      />

      <main className="main-content">
        <Header
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />

        <div
          key={location.pathname}
          className="dashboard-page-wrapper nm-page-enter"
        >
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default DashboardLayout;