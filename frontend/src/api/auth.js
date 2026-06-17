import authFetch from "./axios";

// Register new user
export const registerUser = async (email, username, password) => {
  try {
    const res = await authFetch.post("/auth/register", {
      email: email,
      username: username,
      password: password,
    });
    return res.data;
  } catch (e) {
    console.log("Register attempt failed" + e);
  }
};

// Log in a user
export const loginUser = async (username, password) => {
  try {
    const res = await authFetch.post("/auth/login", {
      username: username,
      password: password,
    });
    return res.data;
  } catch (e) {
    console.log("Login attempt failed" + e);
  }
};
