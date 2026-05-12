import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CreateCharacter from "./pages/CreateCharacter";
import Character from "./pages/Character";
import Inventory from "./pages/Inventory";
import Shop from "./pages/Shop";

function RequireAuth({ children }) {
  return localStorage.getItem("token") ? children : <Navigate to="/login" />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/create-character" element={<RequireAuth><CreateCharacter /></RequireAuth>} />
        <Route path="/character" element={<RequireAuth><Character /></RequireAuth>} />
        <Route path="/inventory" element={<RequireAuth><Inventory /></RequireAuth>} />
        <Route path="/shop" element={<RequireAuth><Shop /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/character" />} />
      </Routes>
    </BrowserRouter>
  );
}
