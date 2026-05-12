import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function Inventory() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [customName, setCustomName] = useState("");
  const [customQty, setCustomQty] = useState(1);
  const [error, setError] = useState("");
  const [characters, setCharacters] = useState([]);
  const [transferItem, setTransferItem] = useState(null);
  const [transferTo, setTransferTo] = useState("");
  const [transferQty, setTransferQty] = useState(1);

  const load = () => api.get("/inventory").then(({ data }) => setItems(data));

  useEffect(() => {
    load();
    api.get("/characters").then(({ data }) => setCharacters(data));
  }, []);

  const addCustom = async () => {
    if (!customName.trim()) return;
    setError("");
    try {
      await api.post("/inventory", { item_type: "custom", custom_name: customName.trim(), quantity: customQty });
      setCustomName("");
      setCustomQty(1);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка");
    }
  };

  const remove = async (id) => {
    await api.delete(`/inventory/${id}`);
    load();
  };

  const doTransfer = async () => {
    if (!transferTo) return;
    try {
      await api.post("/characters/me/transfer/item", {
        to_character_id: Number(transferTo),
        inventory_item_id: transferItem.id,
        quantity: transferQty,
      });
      setTransferItem(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка передачи");
    }
  };

  const label = (item) => item.custom_name || `#${item.shop_item_id} (${item.item_type})`;

  return (
    <div className="page">
      <div className="card">
        <div className="page-header">
          <button className="btn-back" onClick={() => navigate("/character")}>← Назад</button>
          <h2>Инвентарь</h2>
        </div>

        {/* Добавить кастомный предмет */}
        <div className="custom-item-form">
          <h4>Добавить предмет вручную</h4>
          <div className="row">
            <input
              placeholder="Название (мышиное дерьмо, крыло баклана...)"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
            />
            <input type="number" min={1} value={customQty} onChange={(e) => setCustomQty(Number(e.target.value))} style={{ width: 70 }} />
            <button onClick={addCustom}>Добавить</button>
          </div>
          {error && <p className="error">{error}</p>}
        </div>

        {/* Список */}
        <div className="inventory-list">
          {items.length === 0 && <p>Инвентарь пуст</p>}
          {items.map((item) => (
            <div key={item.id} className="inventory-item">
              <span className="item-name">{label(item)}</span>
              <span className="item-qty">× {item.quantity}</span>
              <button onClick={() => { setTransferItem(item); setTransferQty(1); }}>Передать</button>
              <button className="btn-danger" onClick={() => remove(item.id)}>✕</button>
            </div>
          ))}
        </div>

        {/* Модал передачи */}
        {transferItem && (
          <div className="modal-overlay" onClick={() => setTransferItem(null)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>Передать «{label(transferItem)}»</h3>
              <select value={transferTo} onChange={(e) => setTransferTo(e.target.value)}>
                <option value="">Выберите персонажа</option>
                {characters.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <input type="number" min={1} max={transferItem.quantity} value={transferQty}
                onChange={(e) => setTransferQty(Number(e.target.value))} />
              <button onClick={doTransfer}>Передать</button>
              <button onClick={() => setTransferItem(null)}>Отмена</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
