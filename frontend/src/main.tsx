import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";
import "./refinements.css";
import "./mobile-tables.css";

createRoot(document.getElementById("root")!).render(<App />);
