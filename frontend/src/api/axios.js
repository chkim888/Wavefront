import axios from "axios";

// Create an Axios instance
const authFetch = axios.create({
  baseURL: `${import.meta.env.VITE_API_URL}/api`, // configured in vite.config.js
  headers: {
    Accept: "application/json",
  },
});

// Insert the JWT token into request headers
authFetch.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error); // Axios is promise-based
  },
);

export default authFetch;
