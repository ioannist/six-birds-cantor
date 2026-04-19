import { RouterProvider } from "react-router-dom";
import { router } from "./app/router";
import "./theme/theme.css";

export default function App() {
  return <RouterProvider router={router} />;
}
