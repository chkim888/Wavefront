import authFetch from "./axios";

export const getAllProjects = async () => {
  try {
    // make the GET request
    const res = await authFetch.get("/projects/all-projects");
    return res.data;
  } catch (e) {
    console.log("Couldn't get all projects");
  }
};

