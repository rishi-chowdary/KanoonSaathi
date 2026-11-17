import React, { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api";

export const AuthContext = createContext({
  user: null,
  token: null,
  loading: true,
  isAuthenticated: false,
  login: async () => {},
  register: async () => {},
  logout: () => {},
  updateProfile: async () => {},
});

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("lexilegal_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const storedToken = localStorage.getItem("lexilegal_token");
      if (!storedToken) {
        setLoading(false);
        return;
      }

      try {
        const response = await api.get("/users/me");
        setUser(response.data);
      } catch (err) {
        localStorage.removeItem("lexilegal_token");
        setToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    loadUser();
  }, []);

  const login = async (email, password) => {
    const response = await api.post("/auth/login", { email, password });
    const { token: jwtToken, user: userData } = response.data;
    localStorage.setItem("lexilegal_token", jwtToken);
    setToken(jwtToken);
    setUser(userData);
    return userData;
  };

  const register = async (email, password, fullName) => {
    const response = await api.post("/auth/register", { email, password, fullName });
    const { token: jwtToken, user: userData } = response.data;
    localStorage.setItem("lexilegal_token", jwtToken);
    setToken(jwtToken);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch {
      // Ignored: client-side discard is primary
    }
    localStorage.removeItem("lexilegal_token");
    setToken(null);
    setUser(null);
  };

  const updateProfile = async (fullName, password) => {
    const payload = { fullName };
    if (password && password.trim() !== "") {
      payload.password = password;
    }
    const response = await api.put("/users/me", payload);
    setUser(response.data);
    return response.data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

