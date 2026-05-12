import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/client";
import FantasyLandscape from "../components/FantasyLandscape";
import PasswordInput from "../components/PasswordInput";

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/auth/register", form);
      const { data } = await api.post("/auth/login", form);
      localStorage.setItem("token", data.access_token);
      navigate("/create-character");
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка регистрации");
    }
  };

  return (
    <div className="auth-page">
      <FantasyLandscape />

      <div className="fantasy-card auth-card">
        <span className="corner tl"/><span className="corner tr"/>
        <span className="corner bl"/><span className="corner br"/>

        <h2>DnD Shop</h2>
        <p className="auth-subtitle">Начните своё приключение</p>
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
            placeholder="Пароль (мин. 6 символов)"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            minLength={6}
          />
          {error && <p className="error">⚠ {error}</p>}
          <button type="submit">Создать аккаунт</button>
        </form>

        <div className="auth-divider">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </div>
      </div>
    </div>
  );
}
