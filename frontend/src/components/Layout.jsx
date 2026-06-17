import React from "react";
import { Outlet, Link } from "react-router-dom";

function Layout() {
  return (
    <>
      <div>
        <nav>
          <Link to="/alerts">Alerts</Link>
          <Link to="/analytics">Analytics</Link>
          <Link to="/buzz">Buzz Monitor</Link>
          <Link to="/manage">Experiment Manager</Link>
        </nav>
      </div>
      <div>
        {/* Outlet is the placeholder where the matched child route components will be rendered */}
        <Outlet />
      </div>
    </>
  );
}
export default Layout;