import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/client";
import FantasyLandscape from "../components/FantasyLandscape";
import PasswordInput from "../components/PasswordInput";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const { data } = await api.post("/auth/login", form);
      localStorage.setItem("token", data.access_token);
      navigate("/character");
    } catch (err) {
      setError(err.response?.data?.detail || "Неверный логин или пароль");
    }
  };

  return (
    <div className="auth-page">
      <FantasyLandscape />

      <div className="fantasy-card auth-card">
        <span className="corner tl"/><span className="corner tr"/>
        <span className="corner bl"/><span className="corner br"/>

        <h2>DnD Shop</h2>
        <p className="auth-subtitle">Войдите в свой аккаунт, искатель приключений</p>
        <div className="ornament">⸺ ✦ ⸺</div>

        <form onSubmit={submit}>
          <input
            type="email"
            placeholder="Ваш email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
          <PasswordInput
            placeholder="Пароль"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          {error && <p className="error">⚠ {error}</p>}
          <button type="submit">Войти</button>
        </form>

        <div className="auth-divider">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </div>
      </div>
    </div>
  );
}
