import authFetch from "./axios";

// create_experiment
export const createExperiment = async (
  projectId,
  title,
  description,
  trafficSplit,
  successMetric,
) => {
  try {
    const res = await authFetch.post("/experiments", {
      project_id: projectId,
      title: title,
      description: description,
      traffic_split: trafficSplit,
      success_metric: successMetric,
    });
    return res.data;
  } catch (e) {
    console.log("Failed to create new experiment");
  }
};

// start_experiment
export const startExperiment = async (experimentId) => {
  try {
    const res = await authFetch.post(`/experiments/${experimentId}/start`);
    return res.data;
  } catch (e) {
    console.log("Failed to start experiment");
  }
};

// stop_experiment
export const stopExperiment = async (experimentId) => {
  try {
    const res = await authFetch.post(`/experiments/${experimentId}/stop`);
    return res.data;
  } catch (e) {
    console.log("Failed to stop experiment");
  }
};

// get_all_experiments
export const getAllExperiments = async (projectId) => {
  try {
    const res = await authFetch.get(`/experiments/project/${projectId}`);
    return res.data;
  } catch (e) {
    console.log("Failed to load all experiments");
  }
};

// get_experiment
export const getExperiment = async (experimentId) => {
  try {
    const res = await authFetch.get(`/experiments/${experimentId}`);
    return res.data;
  } catch (e) {
    console.log("Failed to load experiment");
  }
};

// get_result
export const getResult = async (experimentId) => {
  try {
    const res = await authFetch.get(`/experiments/${experimentId}/result`);
    return res.data;
  } catch (e) {
    console.log("Failed to load experiment");
  }
};
