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

  // JSX
  return (
    <>
      {/* Project selector */}
      <select
        value={selectedProject?.name ?? ""}
        onChange={(e) => {
          setSelectedProject(projects.find((p) => p.name === e.target.value));
        }}
      >
        <option value="" disabled hidden>
          Choose a project...
        </option>
        {projects.map((project) => (
          <option key={project.id} value={project.name}>
            {project.name}
          </option>
        ))}
      </select>

      {/* A list of alerts */}
      {selectedProject && (
        <>
          <table>
            <thead>
              <tr>
                {/* topic, time, message */}
                <th>Topic</th>
                <th>Time</th>
                <th>Message</th>
              </tr>
            </thead>
            <tbody>
              {/* Maps one row per alert */}
              {alerts.map((alert) => {
                const topic = topics.find((t) => t.id === alert.topic_id);
                return (
                  <tr key={alert.id}>
                    <td>{topic?.title}</td>
                    <td>{alert.triggered_at}</td>
                    <td>{alert.message}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </>
      )}
    </>
  );
}
export default Alerts;
