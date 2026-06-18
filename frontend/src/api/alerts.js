import authFetch from "./axios";

export const getAlertsByProject = async (projectId) => {
  try {
    const res = await authFetch.get(`/alerts/${projectId}`);
    return res.data;
  } catch (e) {
    console.error(e);
  }
};
