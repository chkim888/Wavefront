import React, { useState } from "react";
import { Outlet, NavLink } from "react-router-dom";

function Layout() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="flex h-screen">
      <button
        type="button"
        className="md:hidden fixed top-4 left-4 z-[60] text-white bg-[#1e2130] p-2 rounded-lg border border-[#2a2d3e]"
        onClick={() => setDrawerOpen(!drawerOpen)}
      >
        <svg
          className="h-6 w-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M4 6h16M4 12h16M4 18h16"
          />
        </svg>
      </button>
      {drawerOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setDrawerOpen(false)}
        />
      )}
      {/* Sidebar */}
      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          w-60 bg-[#1a1d27] flex flex-col p-6 pt-20 md:pt-6 border-r border-[#2a2d3e]
          transform transition-transform duration-200
          ${drawerOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}
        `}
      >
        {" "}
        <h1 className="text-white text-xl font-bold">Wavefront</h1>
        <nav className="flex flex-col gap-2 mt-8">
          <NavLink
            to="/alerts"
            className={({ isActive }) =>
              isActive
                ? "text-white bg-[#2a2d3e] px-4 py-2 rounded-lg"
                : "text-[#64748b] hover:text-white hover:bg-[#2a2d3e] px-4 py-2 rounded-lg transition-colors"
            }
          >
            Alerts
          </NavLink>
          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              isActive
                ? "text-white bg-[#2a2d3e] px-4 py-2 rounded-lg"
                : "text-[#64748b] hover:text-white hover:bg-[#2a2d3e] px-4 py-2 rounded-lg transition-colors"
            }
          >
            Analytics
          </NavLink>
          <NavLink
            to="/buzz"
            className={({ isActive }) =>
              isActive
                ? "text-white bg-[#2a2d3e] px-4 py-2 rounded-lg"
                : "text-[#64748b] hover:text-white hover:bg-[#2a2d3e] px-4 py-2 rounded-lg transition-colors"
            }
          >
            Buzz Monitor
          </NavLink>
          <NavLink
            to="/manage"
            className={({ isActive }) =>
              isActive
                ? "text-white bg-[#2a2d3e] px-4 py-2 rounded-lg"
                : "text-[#64748b] hover:text-white hover:bg-[#2a2d3e] px-4 py-2 rounded-lg transition-colors"
            }
          >
            Experiment Manager
          </NavLink>
        </nav>
      </aside>
      <main className="flex-1 bg-[#0f1117] overflow-auto p-8 pt-20 md:pt-8">
        {/* Outlet is the placeholder where the matched child route components will be rendered */}
        <Outlet />
      </main>
    </div>
  );
}
export default Layout;
