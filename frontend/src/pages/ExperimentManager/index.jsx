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

  // get all experiments on project selection
  useEffect(() => {
    const fetch = async () => {
      try {
        if (!selectedProject) {
          return;
        }
        const res = await getAllExperiments(selectedProject.id);
        setExperiments(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedProject]);

  // get result on experiment selection
  useEffect(() => {
    const fetch = async () => {
      try {
        if (
          !selectedExperiment ||
          selectedExperiment.curr_status !== "COMPLETE"
        )
          return;
        const res = await getResult(selectedExperiment.id);
        setResult(res);
      } catch (e) {
        console.error(e);
      }
    };
    fetch();
  }, [selectedExperiment]);

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
      if (currStatus === "CREATED" || currStatus === "COMPLETE") {
        const res = await startExperiment(selectedExperiment.id);
      }
      if (currStatus === "RUNNING") {
        const res = await stopExperiment(selectedExperiment.id);
      }
      if (currStatus != "ARCHIVED") {
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

  return (
    <>
      {/* Project list & selector */}
      <select
        id="project-select"
        value={selectedProject?.name ?? ""}
        onChange={(e) =>
          setSelectedProject(projects.find((p) => p.name === e.target.value))
        }
      >
        {projects.map((project) => (
          <option key={project.id} value={project.name}>
            {project.name}
          </option>
        ))}
      </select>

      {/* Experiment list & selector */}
      {selectedProject && (
        <select
          id="experiment-select"
          value={selectedExperiment?.title ?? ""}
          onChange={(e) => {
            setSelectedExperiment(
              experiments.find((exp) => exp.title === e.target.value),
            );
          }}
        >
          {experiments.map((experiment) => (
            <option key={experiment.id} value={experiment.title}>
              {experiment.title}
            </option>
          ))}
        </select>
      )}

      {/* Button to go to experiment creation form */}
      {selectedProject && (
        <button onClick={() => setShowForm(true)}>
          Create a New Experiment
        </button>
      )}

      {/* Experiment creation form */}
      {showForm && (
        <form onSubmit={handleSubmit}>
          <label>
            Title:
            <input
              type="text"
              name="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
            Description:
            <input
              type="text"
              name="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            Traffic Split:
            <input
              type="number"
              name="traffic-split"
              value={trafficSplit}
              onChange={(e) => setTrafficSplit(e.target.value)}
            />
            Success Metric:
            <input
              type="text"
              name="success-metric"
              value={successMetric}
              onChange={(e) => setSuccessMetric(e.target.value)}
            />
          </label>
          <button type="submit">Create Experiment</button>
        </form>
      )}

      {/* start & stop experiment button */}
      {selectedExperiment && (
        <button onClick={toggleExperiment}>
          {selectedExperiment.curr_status === "RUNNING" && "Stop"}
          {selectedExperiment.curr_status === "CREATED" && "Start"}
          {selectedExperiment.curr_status === "COMPLETE" && "Re-run"}
        </button>
      )}

      {/* Result view */}
      {selectedExperiment?.curr_status === "COMPLETE" && (
        <>
          {result.winner === "INSUFFICIENT_DATA" ? (
            <p>Insufficient data to determine winner</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th></th>
                  <th>Control</th>
                  <th>Treatment</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Conversions</td>
                  <td>{result.control_conversions}</td>
                  <td>{result.treatment_conversions}</td>
                </tr>
                <tr>
                  <td>Conversion Rate</td>
                  <td>{(result.control_rate * 100).toFixed(1) + "%"}</td>
                  <td>{(result.treatment_rate * 100).toFixed(1) + "%"}</td>
                </tr>
                <tr>
                  <td>Lift</td>
                  <td>{(result.lift * 100).toFixed(1) + "%"}</td>
                  <td></td>
                </tr>
                <tr>
                  <td>Confidence</td>
                  <td>{(result.confidence * 100).toFixed(1) + "%"}</td>
                  <td></td>
                </tr>
                <tr>
                  <td>Winner</td>
                  <td>
                    {(result.winner === "TREATMENT" && "Treatment ✓") ||
                      "Control  ✓"}
                  </td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          )}
        </>
      )}
    </>
  );
}

export default ExperimentManager;
