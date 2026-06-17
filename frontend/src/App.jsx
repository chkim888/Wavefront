import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";
import BuzzMonitor from "./pages/BuzzMonitor";
import ExperimentManager from "./pages/ExperimentManager";
import Login from "./pages/Login";
import Register from "./pages/Register";

function App() {
  return (
    <Routes>
      {/* Default homepage is the login page */}
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route element={<Layout />}>
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/buzz" element={<BuzzMonitor />} />
        <Route path="/manage" element={<ExperimentManager />} />
      </Route>
    </Routes>
  );
}

export default App;
