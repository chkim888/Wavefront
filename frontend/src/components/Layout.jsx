import React from "react";
import { Outlet, Link, NavLink } from "react-router-dom";

function Layout() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-60 bg-[#1a1d27] flex flex-col p-6 border-r border-[#2a2d3e]">
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
      <main className="flex-1 bg-[#0f1117] overflow-auto p-8">
        {/* Outlet is the placeholder where the matched child route components will be rendered */}
        <Outlet />
      </main>
    </div>
  );
}
export default Layout;
