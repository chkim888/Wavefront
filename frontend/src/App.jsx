import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";
import BuzzMonitor from "./pages/BuzzMonitor";
import ExperimentManager from "./pages/ExperimentManager";

function App() {
  return (
    <Routes>
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
