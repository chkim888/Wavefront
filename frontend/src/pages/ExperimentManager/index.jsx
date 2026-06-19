import {
  createExperiment,
  getAllExperiments,
  getResult,
  startExperiment,
  stopExperiment,
} from "@/api/experiments";
import { getAllProjects } from "@/api/projects";
import { useEffect, useState } from "react";

function ExperimentManager() {
  // set the state variables
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [selectedExperiment, setSelectedExperiment] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [result, setResult] = useState({});
  // these are for form
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [trafficSplit, setTrafficSplit] = useState(0);
  const [successMetric, setSuccessMetric] = useState("");
  // constants
  const CREATED = "created";
  const RUNNING = "running";
  const COMPLETE = "complete";
  const ARCHIVED = "archived";
  const INSUFFICIENT_DATA = "insufficient data";

  // on load, get all projects
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

  // on project selection
  useEffect(() => {
    const fetch = async () => {
      try {
        if (!selectedProject) {
          return;
        }
        const res = await getAllExperiments(selectedProject.id);
        setExperiments(res);
        // reset
        setSelectedExperiment(null);
        setShowForm(false);
        setResult({});
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedProject]);

  // on experiment selection
  useEffect(() => {
    if (selectedExperiment != null) {
      setShowForm(false);
    }
    const fetch = async () => {
      try {
        if (!selectedExperiment || selectedExperiment.curr_status !== COMPLETE)
          return;
        const res = await getResult(selectedExperiment.id);
        setResult(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedExperiment]);

  // on form
  useEffect(() => {
    // reset values when form shown
    if (showForm) {
      setTitle("");
      setDescription("");
      setSuccessMetric("");
      setTrafficSplit(0);
    }
  }, [showForm]);

  // handle when the experiment form is submitted
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (
        selectedProject &&
        title &&
        description &&
        trafficSplit &&
        successMetric
      ) {
        const res = await createExperiment(
          selectedProject.id,
          title,
          description,
          trafficSplit,
          successMetric,
        );
        setShowForm(false);
        const updated = await getAllExperiments(selectedProject.id);
        setExperiments(updated);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // start experiment
  const toggleExperiment = async () => {
    try {
      const currStatus = selectedExperiment.curr_status;
      // Run experiment if the experiment is created or complete (rerun)
      if (currStatus === CREATED || currStatus === COMPLETE) {
        const res = await startExperiment(selectedExperiment.id);
      }
      if (currStatus === RUNNING) {
        const res = await stopExperiment(selectedExperiment.id);
      }
      if (currStatus != ARCHIVED) {
        // update the list of experiments to reflect the changes in experiment status
        const updated = await getAllExperiments(selectedProject.id);
        setExperiments(updated);
        setSelectedExperiment(
          updated.find((exp) => exp.id === selectedExperiment.id),
        );
      }
    } catch (e) {
      console.error(e);
    }
  };

  // for styling
  const selectClass =
    "bg-[#1e2130] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 focus:outline-none focus:border-[#6366f1]";
  const inputClass =
    "w-full bg-[#0f1117] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 focus:outline-none focus:border-[#6366f1]";
  const labelClass = "block text-[#64748b] text-sm mb-1";

  const statusColors = {
    CREATED: "bg-gray-500/20 text-gray-300",
    RUNNING: "bg-[#6366f1]/20 text-[#a5b4fc]",
    COMPLETE: "bg-green-500/20 text-green-400",
  };

  return (
    <>
      <h1 className="text-white text-2xl font-bold mb-6">Experiment Manager</h1>

      <div className="flex gap-4 mb-6 items-center">
        {/* Project list & selector */}
        <select
          className={selectClass}
          id="project-select"
          value={selectedProject?.name ?? ""}
          onChange={(e) =>
            setSelectedProject(projects.find((p) => p.name === e.target.value))
          }
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

        {/* Experiment list & selector */}
        {selectedProject && (
          <select
            className={selectClass}
            id="experiment-select"
            value={selectedExperiment?.title ?? ""}
            onChange={(e) => {
              setSelectedExperiment(
                experiments.find((exp) => exp.title === e.target.value),
              );
            }}
          >
            <option value="" disabled hidden>
              Choose an experiment...
            </option>
            {experiments.map((experiment) => (
              <option key={experiment.id} value={experiment.title}>
                {experiment.title}
              </option>
            ))}
          </select>
        )}

        {/* Button to go to experiment creation form */}
        {selectedProject && !showForm && (
          <button
            onClick={() => {
              setShowForm(true);
              setSelectedExperiment(null);
            }}
            className="bg-[#6366f1] text-white px-4 py-2 rounded-lg hover:bg-[#4f46e5] active:scale-95 cursor-pointer transition-colors ml-auto"
          >
            Create a New Experiment
          </button>
        )}
      </div>

      {/* Experiment creation form */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-[#1e2130] border border-[#2a2d3e] rounded-xl p-6 mb-6 max-w-lg"
        >
          <h2 className="text-white text-lg font-semibold mb-4">
            New Experiment
          </h2>
          <div className="mb-4">
            <label className={labelClass}>Title</label>
            <input
              className={inputClass}
              type="text"
              name="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
          <div className="mb-4">
            <label className={labelClass}>Description</label>
            <input
              className={inputClass}
              type="text"
              name="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="mb-4">
            <label className={labelClass}>Traffic Split</label>
            <input
              className={inputClass}
              type="number"
              name="traffic-split"
              value={trafficSplit}
              onChange={(e) => setTrafficSplit(e.target.value)}
            />
          </div>
          <div className="mb-4">
            <label className={labelClass}>Success Metric</label>
            <input
              className={inputClass}
              type="text"
              name="success-metric"
              value={successMetric}
              onChange={(e) => setSuccessMetric(e.target.value)}
            />
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              className="bg-[#6366f1] text-white px-4 py-2 rounded-lg hover:bg-[#4f46e5] active:scale-95 cursor-pointer transition-colors"
            >
              Create Experiment
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="text-[#64748b] hover:text-white px-4 py-2 cursor-pointer transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* start & stop experiment button */}
      {selectedExperiment && (
        <div className="bg-[#1e2130] border border-[#2a2d3e] rounded-xl p-6 mb-6 max-w-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-white text-lg font-semibold">
              {selectedExperiment.title}
            </h2>
            <span
              className={`text-xs px-3 py-1 rounded-full ${statusColors[selectedExperiment.curr_status] ?? "bg-gray-500/20 text-gray-300"}`}
            >
              {selectedExperiment.curr_status}
            </span>
          </div>
          <p className="text-[#64748b] text-sm mb-4">
            {selectedExperiment.description}
          </p>
          <button
            onClick={toggleExperiment}
            className="bg-[#6366f1] text-white px-4 py-2 rounded-lg hover:bg-[#4f46e5] active:scale-95 cursor-pointer transition-colors"
          >
            {selectedExperiment.curr_status === RUNNING && "Stop"}
            {selectedExperiment.curr_status === CREATED && "Start"}
            {selectedExperiment.curr_status === COMPLETE && "Re-run"}
          </button>
        </div>
      )}

      {/* Result view */}
      {selectedExperiment?.curr_status === COMPLETE && (
        <div className="bg-[#1e2130] border border-[#2a2d3e] rounded-xl p-6 max-w-lg">
          <h2 className="text-white text-lg font-semibold mb-4">
            Experiment Result
          </h2>
          {result.winner === INSUFFICIENT_DATA ? (
            <p className="text-[#64748b]">
              Insufficient data to determine winner.
            </p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-[#64748b] border-b border-[#2a2d3e]">
                  <th className="text-left py-2 font-normal"></th>
                  <th className="text-left py-2 font-normal">Control</th>
                  <th className="text-left py-2 font-normal">Treatment</th>
                </tr>
              </thead>
              <tbody className="text-white">
                <tr className="border-b border-[#2a2d3e]">
                  <td className="py-2 text-[#64748b]">Conversions</td>
                  <td className="py-2">{result.control_conversions}</td>
                  <td className="py-2">{result.treatment_conversions}</td>
                </tr>
                <tr className="border-b-2 border-[#3a3d4e]">
                  <td className="py-2 text-[#64748b]">Conversion Rate</td>
                  <td className="py-2">
                    {(result.control_rate * 100).toFixed(1) + "%"}
                  </td>
                  <td className="py-2">
                    {(result.treatment_rate * 100).toFixed(1) + "%"}
                  </td>
                </tr>
                <tr className="border-b border-[#2a2d3e]">
                  <td className="py-2 text-[#64748b]">Lift</td>
                  <td className="py-2 text-right" colSpan={2}>
                    {(result.lift * 100).toFixed(1) + "%"}
                  </td>
                </tr>
                <tr className="border-b border-[#2a2d3e]">
                  <td className="py-2 text-[#64748b]">Confidence</td>
                  <td className="py-2 text-right" colSpan={2}>
                    {result.confidence + "%"}
                  </td>
                </tr>
                <tr>
                  <td className="py-2 text-[#64748b]">Winner</td>
                  <td
                    className="py-2 text-right text-green-400 font-medium"
                    colSpan={2}
                  >
                    {result.winner === "TREATMENT"
                      ? "Treatment ✓"
                      : "Control ✓"}
                  </td>
                </tr>
              </tbody>
            </table>
          )}
        </div>
      )}
    </>
  );
}

export default ExperimentManager;
