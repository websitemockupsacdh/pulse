import "@fontsource-variable/newsreader";
import "@fontsource-variable/plus-jakarta-sans";
import "@fontsource-variable/jetbrains-mono";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, HashRouter } from "react-router-dom";
import { installMock } from "./preview/mock";
import App from "./App";
import "./index.css";

const PREVIEW = import.meta.env.VITE_PREVIEW === "1";
if (PREVIEW) installMock();
const Router = PREVIEW ? HashRouter : BrowserRouter;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Router>
      <App />
    </Router>
  </React.StrictMode>,
);
