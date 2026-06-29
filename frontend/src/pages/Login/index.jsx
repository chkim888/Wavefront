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
    <div className="min-h-screen bg-[#0f1117] flex items-center justify-center">
      <div className="card p-8 w-full max-w-md">
        <h1 className="text-white text-2xl font-bold mb-6">Wavefront</h1>
        <form onSubmit={handleSubmit}>
          <label className="block text-[#64748b] text-sm mb-1">
            Username:
            <input
              className="w-full bg-[#0f1117] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 mb-4 focus:outline-none focus:border-[#6d28d9]"
              type="text"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)} // updating username with event changes
            />
          </label>
          <label className="block text-[#64748b] text-sm mb-1">
            Password:
            <input
              className="w-full bg-[#0f1117] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 mb-4 focus:outline-none focus:border-[#6d28d9]"
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          <button
            className="w-full bg-[#6d28d9] text-white py-2 rounded-lg hover:bg-[#6d28d9] hover:shadow-[0_0_16px_rgba(124,58,237,0.4)] active:scale-95 cursor-pointer transition-all"
            type="submit"
          >
            Login
          </button>
        </form>
        <div className="text-center mt-4">
          <p className="text-[#64748b] text-sm text-center mt-4">
            Not a registered user?
          </p>
          <Link
            className="text-[#6d28d9] text-sm hover:underline"
            to="/register"
          >
            Register here
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
