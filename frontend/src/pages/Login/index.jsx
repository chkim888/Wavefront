import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { loginUser } from "@/api/auth";

function Login() {
  // set states for input values
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); // stops the browser from executing the default option (page reload)
    try {
      // Check if the input values are null
      if (!username || !password) {
        console.log("Username or password is empty");
        return;
      }
      // make API call
      const res = await loginUser(username, password);
      // call login() with the token
      login(res.access_token);
      // After successful login, navigate to the buzz monitor page
      navigate("/manage");
    } catch (error) {
      console.error(error);
    }
  };

  return (
    // JSX form
    <>
      <form onSubmit={handleSubmit}>
        <label>
          Username:
          <input
            type="text"
            name="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)} // updating username with event changes
          />
        </label>
        <label>
          Password:
          <input
            type="text"
            name="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <button type="submit">Login</button>
      </form>
      <p>Not a registered user?</p>
      <Link to="/register">Register here</Link>
    </>
  );
}

export default Login;
