import api from "./client";

export async function loginUser(email, password) {
  const response = await api.post("/auth/login", {
    email,
    password,
  });

  return response.data;
}

export async function registerUser(
  name,
  email,
  password
) {
  const response = await api.post("/auth/register", {
    full_name: name,
    email,
    password,
  });

  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get("/users/me");

  return response.data;
}