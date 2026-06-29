import { registerUser } from "@/api/auth";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Register() {
  // set different states
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); // prevent page refreshing on submission
    try {
      // check that all values are not null
      if (!email || !username || !password) {
        console.log("Null values not allowed for field values");
        return;
      }
      // Send API request to the backend register endpoint
      const res = await registerUser(email, username, password);
      if (!res) {
        console.log("Unsuccessful register attempt");
      }
      // redirect to login page after successful registration
      navigate("/login");
    } catch (e) {
      console.log(e);
    }
  };

  // return JSX
  return (
    <div className="min-h-screen bg-[#0f1117] flex items-center justify-center">
      <div className="card p-8 w-full max-w-md">
        <h1 className="text-white text-2xl font-bold mb-6">Wavefront</h1>
        <form onSubmit={handleSubmit}>
          <label className="block text-[#64748b] text-sm mb-1">
            Email:
            <input
              className="w-full bg-[#0f1117] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 mb-4 focus:outline-none focus:border-[#7c3aed]"
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          <label className="block text-[#64748b] text-sm mb-1">
            Username:
            <input
              className="w-full bg-[#0f1117] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 mb-4 focus:outline-none focus:border-[#7c3aed]"
              type="text"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </label>
          <label className="block text-[#64748b] text-sm mb-1">
            Password:
            <input
              className="w-full bg-[#0f1117] border border-[#2a2d3e] text-white rounded-lg px-4 py-2 mb-4 focus:outline-none focus:border-[#7c3aed]"
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          <button
            className="w-full bg-[#7c3aed] text-white py-2 rounded-lg hover:bg-[#6d28d9] hover:shadow-[0_0_16px_rgba(124,58,237,0.4)] active:scale-95 cursor-pointer transition-all"
            type="submit"
          >
            Register
          </button>
        </form>
        <div className="text-center mt-4">
          <p className="text-[#64748b] text-sm text-center mt-4">
            Already have an account?
          </p>
          <Link className="text-[#7c3aed] text-sm hover:underline" to="/login">
            Login here
          </Link>
        </div>
      </div>
    </div>
  );
}
export default Register;
