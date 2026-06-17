import { createContext, useState, useContext } from "react";

// Initialize context
const AuthContext = createContext();

// Create a provider wrapper component -- supplies data to the component tree
export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("access_token"));

  const login = (token) => {
    setToken(token);
    localStorage.setItem("access_token", token);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("access_token");
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Create a custom hook -- for reading the data (auth, toggleAuth) from the child components
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
