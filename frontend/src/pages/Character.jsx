import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import CoinConverter from "../components/CoinConverter";
import CityLandscape from "../components/CityLandscape";

const COIN_FIELDS = [
  { key: "platinum", label: "Платина (пп)" },
  { key: "gold",     label: "Золото (зм)" },
  { key: "electrum", label: "Электрум (эм)" },
  { key: "silver",   label: "Серебро (см)" },
  { key: "copper",   label: "Медь (мм)" },
];

const ALLOWED_FORMATS = "JPG, JPEG, PNG, GIF, WEBP";

export default function Character() {
  const navigate = useNavigate();
  const [char, setChar] = useState(null);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({});
  const [error, setError] = useState("");
  const [picError, setPicError] = useState("");
  const fileRef = useRef();

  useEffect(() => {
    api.get("/characters/me")
      .then(({ data }) => { setChar(data); setForm(data); })
      .catch(() => navigate("/create-character"));
  }, []);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const save = async () => {
    setError("");
    try {
      const { data } = await api.put("/characters/me", form);
      setChar(data);
      setEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка сохранения");
    }
  };

  const uploadPic = async (file) => {
    setPicError("");
    const fd = new FormData();
    fd.append("file", file);
    try {
      const { data } = await api.post("/characters/me/userpic", fd);
      setChar(data);
    } catch (err) {
      setPicError(err.response?.data?.detail || "Ошибка загрузки");
    }
  };

  const exchangeCoins = async (fromCoin, toCoin, amount) => {
    const { data } = await api.post("/characters/me/exchange", {
      from_coin: fromCoin,
      to_coin: toCoin,
      amount,
    });
    setChar(data);
  };

  if (!char) return <div className="page"><p>Загрузка...</p></div>;

  return (
    <div className="page character-page">
      <CityLandscape />
      {/* Левая колонка */}
      <div className="char-left">
        <div
          className="userpic"
          onClick={() => editing && fileRef.current.click()}
          title={editing ? "Нажмите чтобы загрузить фото" : ""}
        >
          {char.userpic
            ? <img src={char.userpic} alt="avatar" />
            : <div className="userpic-placeholder">👤</div>
          }
          {editing && <div className="userpic-hint">Поменять фото</div>}
        </div>
        <input
          ref={fileRef} type="file" style={{ display: "none" }}
          accept=".jpg,.jpeg,.png,.gif,.webp"
          title={`Допустимые форматы: ${ALLOWED_FORMATS}`}
          onChange={(e) => e.target.files[0] && uploadPic(e.target.files[0])}
        />
        {picError && <p className="error">{picError}</p>}
        {editing && <p className="hint">Форматы: {ALLOWED_FORMATS}</p>}

        {/* Монеты */}
        <div className="money-block">
          <h4>Монеты</h4>
          {COIN_FIELDS.map(({ key, label }) => (
            <div key={key} className="coin-row">
              <span>{label}</span>
              {editing
                ? <input type="number" min={0} value={form[key] ?? 0} onChange={(e) => set(key, Number(e.target.value))} />
                : <span>{char[key]}</span>
              }
            </div>
          ))}
        </div>

        <CoinConverter onExchange={exchangeCoins} />
      </div>

      {/* Правая колонка */}
      <div className="char-right">
        <div className="char-header">
          <h2>{editing
            ? <input value={form.name} onChange={(e) => set("name", e.target.value)} />
            : char.name
          }</h2>
          {editing
            ? <button onClick={save}>Сохранить</button>
            : <button onClick={() => setEditing(true)}>Редактировать</button>
          }
          {editing && <button className="btn-secondary" onClick={() => { setEditing(false); setForm(char); }}>Отмена</button>}
          {!editing && (
            <button className="btn-secondary" onClick={() => { localStorage.removeItem("token"); navigate("/login"); }}>
              Выйти
            </button>
          )}
        </div>

        <div className="char-field">
          <label>Раса</label>
          {editing
            ? <input value={form.race} onChange={(e) => set("race", e.target.value)} />
            : <span>{char.race}</span>
          }
        </div>

        <div className="char-field">
          <label>Возраст</label>
          {editing
            ? <input type="number" min={1} value={form.age} onChange={(e) => set("age", Number(e.target.value))} />
            : <span>{char.age}</span>
          }
        </div>

        <div className="char-field char-field--desc">
          <label>Описание</label>
          {editing
            ? <textarea value={form.description} onChange={(e) => set("description", e.target.value)} />
            : <div className="description-box">{char.description || <em>Нет описания</em>}</div>
          }
        </div>

        {error && <p className="error">{error}</p>}

        <div className="char-buttons">
          <button onClick={() => navigate("/inventory")}>Инвентарь</button>
          <button onClick={() => navigate("/shop")}>Магазин</button>
        </div>
      </div>
    </div>
  );
}
