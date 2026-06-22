import { getAlertsByProject } from "@/api/alerts";
import { getAllProjects } from "@/api/projects";
import { getAllTopics } from "@/api/topics";
import { useEffect, useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";

function Alerts() {
  // set state variables
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [topics, setTopics] = useState([]);
  
  // for websocket
  const newAlert = useWebSocket(selectedProject?.id);
  useEffect(() => {
    if (!newAlert?.message) return; // run only after first mount
    setAlerts((prev) => [newAlert, ...prev]);
  }, [newAlert]); // happens every time change happens for newAlert

  // on initial load
  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getAllProjects();
        setProjects(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, []);

  // on project select
  useEffect(() => {
    const fetch = async () => {
      try {
        if (!selectedProject) return;
        const projectId = selectedProject.id;
        const a = await getAlertsByProject(projectId);
        setAlerts(a);
        const t = await getAllTopics(projectId);
        setTopics(t);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedProject]);

  // For coloring
  const selectClass =
    "bg-[#1e2130] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 focus:outline-none focus:border-[#6366f1] w-full md:w-auto";
  const cardClass = "bg-[#1e2130] border border-[#2a2d3e] rounded-xl p-6";

  return (
    <>
      {/* Project selector */}
      <h1 className="text-white text-2xl font-bold mb-6">Alerts</h1>

      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <select
          className={selectClass}
          value={selectedProject?.name ?? ""}
          onChange={(e) => {
            setSelectedProject(projects.find((p) => p.name === e.target.value));
          }}
        >
          <option value="" disabled hidden>
            Choose a project...
          </option>
          {projects?.map((project) => (
            <option key={project.id} value={project.name}>
              {project.name}
            </option>
          ))}
        </select>
      </div>

      {/* A list of alerts */}
      {selectedProject && (
        <div className={cardClass}>
          {alerts.length === 0 ? (
            <p className="text-[#64748b]">No alerts for this project yet.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                {/* topic, time, message */}
                <tr className="text-[#64748b] border-b border-[#2a2d3e]">
                  <th className="text-left py-2 font-normal">Topic</th>
                  <th className="text-left py-2 font-normal">Time</th>
                  <th className="text-left py-2 font-normal">Message</th>
                </tr>
              </thead>
              <tbody className="text-white">
                {/* Maps one row per alert */}
                {alerts?.map((alert, index) => {
                  const topic = topics.find((t) => t.id === alert.topic_id);
                  return (
                    <tr
                      key={alert.id ?? index}
                      className="border-b border-[#2a2d3e]"
                    >
                      <td className="py-3 text-[#a5b4fc]">
                        {topic?.title ?? "—"}
                      </td>
                      <td className="py-3 text-[#64748b]">
                        {new Date(alert.triggered_at).toLocaleString()}
                      </td>
                      <td className="py-3">{alert.message}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  );
}

export default Alerts;
