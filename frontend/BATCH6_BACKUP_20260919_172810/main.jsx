import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App";
import {
  AuthProvider,
} from "./context/AuthContext";

import "./index.css";
import "./styles/premium-ui.css";
import "./styles/batch5-core.css";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>
);




