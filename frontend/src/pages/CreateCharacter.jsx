import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

const COIN_FIELDS = [
  { key: "platinum", label: "Платина (пп)" },
  { key: "gold", label: "Золото (зм)" },
  { key: "electrum", label: "Электрум (эм)" },
  { key: "silver", label: "Серебро (см)" },
  { key: "copper", label: "Медь (мм)" },
];

export default function CreateCharacter() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "", race: "", age: "", description: "",
    platinum: 0, gold: 0, electrum: 0, silver: 0, copper: 0,
  });
  const [error, setError] = useState("");

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/characters", { ...form, age: Number(form.age) });
      navigate("/character");
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка создания персонажа");
    }
  };

  return (
    <div className="page">
      <div className="card" style={{ maxWidth: 600, margin: "40px auto" }}>
        <h2>Создать персонажа</h2>
        <form onSubmit={submit} className="form-grid">
          <input placeholder="Имя *" value={form.name} onChange={(e) => set("name", e.target.value)} required />
          <input placeholder="Раса *" value={form.race} onChange={(e) => set("race", e.target.value)} required />
          <input type="number" placeholder="Возраст *" value={form.age} onChange={(e) => set("age", e.target.value)} min={1} required />
          <textarea
            placeholder="Описание персонажа..."
            value={form.description}
            onChange={(e) => set("description", e.target.value)}
            rows={5}
          />
          <div className="coins-row">
            {COIN_FIELDS.map(({ key, label }) => (
              <label key={key}>
                <span>{label}</span>
                <input
                  type="number" min={0} value={form[key]}
                  onChange={(e) => set(key, Number(e.target.value))}
                />
              </label>
            ))}
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit">Создать</button>
        </form>
      </div>
    </div>
  );
}
