import { createContext, useContext, useEffect, useState } from 'react';

import {
  getCurrentUser,
  loginUser,
  registerUser,
} from "../api/auth";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        localStorage.removeItem("access_token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    restoreSession();
  }, []);

  async function login(email, password) {
    const data = await loginUser(email, password);

    const token =
      data.access_token ||
      data.token;

    if (!token) {
      throw new Error(
        "Login succeeded but no access token was returned."
      );
    }

    localStorage.setItem(
      "access_token",
      token
    );

    try {
      const currentUser =
        await getCurrentUser();

      setUser(currentUser);
    } catch {
      setUser({
        email,
      });
    }

    return data;
  }

  async function register(name, email, password) {
    return registerUser(
      name,
      email,
      password
    );
  }

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: Boolean(user),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider."
    );
  }

  return context;
}


