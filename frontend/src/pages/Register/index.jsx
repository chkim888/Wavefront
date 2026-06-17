import { registerUser } from "@/api/auth";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

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
    <form onSubmit={handleSubmit}>
      <label>
        Email:
        <input
          type="email"
          name="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>
      <label>
        Username:
        <input
          type="text"
          name="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
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
      <button type="submit">Register</button>
    </form>
  );
}
export default Register;
