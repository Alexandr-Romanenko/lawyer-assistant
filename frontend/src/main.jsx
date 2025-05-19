//import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import { BrowserRouter } from "react-router-dom";

createRoot(document.getElementById("root")).render(
  //<StrictMode> / temporary off for channel testing
    <BrowserRouter>
      <App />
    </BrowserRouter>
  //</StrictMode>
);
