import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { RarityBadge, PLACEHOLDER_SVGS, getPlaceholderKind } from "../utils/itemUtils";

const TABS = [
  { key: "magic_item", label: "✦ Волшебные предметы" },
  { key: "equipment",  label: "⚔ Снаряжение" },
  { key: "custom",     label: "📦 Прочее" },
];

export default function Inventory() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [tab, setTab] = useState("magic_item");
  const [customName, setCustomName] = useState("");
  const [customQty, setCustomQty] = useState(1);
  const [error, setError] = useState("");
  const [characters, setCharacters] = useState([]);
  const [transferItem, setTransferItem] = useState(null);
  const [transferTo, setTransferTo] = useState("");
  const [transferQty, setTransferQty] = useState(1);
  const [detailItem, setDetailItem] = useState(null);

  const load = () => api.get("/inventory").then(({ data }) => setItems(data)).catch(() => {});

  useEffect(() => {
    load();
    api.get("/characters").then(({ data }) => setCharacters(data)).catch(() => {});
  }, []);

  const addCustom = async () => {
    if (!customName.trim()) return;
    setError("");
    try {
      await api.post("/inventory", { item_type: "custom", custom_name: customName.trim(), quantity: Number(customQty) });
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
    setError("");
    try {
      await api.post("/characters/me/transfer/item", {
        to_character_id: Number(transferTo),
        inventory_item_id: transferItem.id,
        quantity: Number(transferQty),
      });
      setTransferItem(null);
      load();
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка передачи");
    }
  };

  const tabItems = items.filter(i => i.item_type === tab);
  const counts = {
    magic_item: items.filter(i => i.item_type === "magic_item").length,
    equipment:  items.filter(i => i.item_type === "equipment").length,
    custom:     items.filter(i => i.item_type === "custom").length,
  };

  return (
    <div className="inv-page">
      <div className="shop-bg-glow" />

      <div className="shop-header">
        <button className="btn-back" onClick={() => navigate("/character")}>← Назад</button>
        <h2>Инвентарь</h2>
        <div className="shop-wallet">
          <span>{items.length} предм.</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="shop-tabs">
        {TABS.map(t => (
          <button key={t.key} className={`shop-tab ${tab === t.key ? "active" : ""}`} onClick={() => setTab(t.key)}>
            {t.label}
            {counts[t.key] > 0 && <span className="inv-tab-count">{counts[t.key]}</span>}
          </button>
        ))}
      </div>

      {/* Add custom item (only on Прочее tab) */}
      {tab === "custom" && (
        <div className="inv-add-form">
          <div className="row">
            <input
              placeholder="Название предмета..."
              value={customName}
              onChange={e => setCustomName(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addCustom()}
            />
            <input type="number" min={1} value={customQty}
              onChange={e => setCustomQty(e.target.value)} style={{ width: 70 }} />
            <button onClick={addCustom}>Добавить</button>
          </div>
          {error && <p className="error">{error}</p>}
        </div>
      )}
      {error && tab !== "custom" && <p className="error" style={{ margin: "0 0 12px" }}>{error}</p>}

      {/* Items grid */}
      {tabItems.length === 0 ? (
        <div className="inv-empty">
          {tab === "magic_item" && "Волшебных предметов нет — загляни в магазин"}
          {tab === "equipment"  && "Снаряжения нет — загляни в магазин"}
          {tab === "custom"     && "Добавь предметы вручную"}
        </div>
      ) : (
        <div className={tab === "custom" ? "inv-custom-list" : "shop-grid"}>
          {tabItems.map(item => tab === "custom"
            ? <CustomRow key={item.id} item={item} onRemove={remove}
                onTransfer={() => { setTransferItem(item); setTransferTo(""); setTransferQty(1); }} />
            : <InvCard key={item.id} item={item}
                onClick={() => setDetailItem(item)}
                onRemove={remove}
                onTransfer={() => { setTransferItem(item); setTransferTo(""); setTransferQty(1); }} />
          )}
        </div>
      )}

      {/* Detail modal */}
      {detailItem && (
        <DetailModal item={detailItem} onClose={() => setDetailItem(null)}
          onTransfer={() => { setTransferItem(detailItem); setTransferTo(""); setTransferQty(1); setDetailItem(null); }}
          onRemove={() => { remove(detailItem.id); setDetailItem(null); }} />
      )}

      {/* Transfer modal */}
      {transferItem && (
        <div className="modal-overlay" onClick={() => setTransferItem(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3>Передать «{transferItem.title}»</h3>
            <select value={transferTo} onChange={e => setTransferTo(e.target.value)}>
              <option value="">Выберите персонажа</option>
              {characters.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <input type="number" min={1} max={transferItem.quantity} value={transferQty}
              onChange={e => setTransferQty(e.target.value)} />
            <div style={{ display: "flex", gap: 10, marginTop: 4 }}>
              <button onClick={doTransfer}>Передать</button>
              <button className="btn-secondary" onClick={() => setTransferItem(null)}>Отмена</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Inventory card (shop items) ───────────────────────────────────────────────
function InvCard({ item, onClick, onRemove, onTransfer }) {
  const [imgOk, setImgOk] = useState(!!item.image_url);
  const kind = getPlaceholderKind(item, item.item_type === "magic_item" ? "magic" : "equipment");

  return (
    <div className="shop-item-card inv-card" onClick={onClick}>
      <div className="item-img-wrap">
        {imgOk ? (
          <img src={item.image_url} alt={item.title} loading="lazy" onError={() => setImgOk(false)} />
        ) : (
          <div className="item-img-placeholder">{PLACEHOLDER_SVGS[kind]}</div>
        )}
        <span className="inv-qty-badge">×{item.quantity}</span>
      </div>
      <div className="item-card-body">
        <div className="item-card-title">{item.title}</div>
        {item.rarity && <RarityBadge rarity={item.rarity} />}
        {!item.rarity && (
          <div className="item-card-meta">
            {item.category && <span className="item-tag">{item.category}</span>}
            {item.damage && <span className="item-tag">{item.damage}</span>}
            {item.armor_class && <span className="item-tag">КД {item.armor_class}</span>}
          </div>
        )}
        <div className="inv-card-actions" onClick={e => e.stopPropagation()}>
          <button className="btn-secondary btn-small inv-btn" onClick={onTransfer}>⇄ Передать</button>
          <button className="btn-danger btn-small inv-btn" onClick={() => onRemove(item.id)}>✕</button>
        </div>
      </div>
    </div>
  );
}

// ── Custom item row ───────────────────────────────────────────────────────────
function CustomRow({ item, onRemove, onTransfer }) {
  return (
    <div className="inventory-item">
      <span className="item-name">{item.title}</span>
      <span className="item-qty">× {item.quantity}</span>
      <button className="btn-secondary" style={{ fontSize: 12, padding: "5px 12px" }} onClick={onTransfer}>⇄ Передать</button>
      <button className="btn-danger" onClick={() => onRemove(item.id)}>✕</button>
    </div>
  );
}

// ── Detail modal ──────────────────────────────────────────────────────────────
function DetailModal({ item, onClose, onTransfer, onRemove }) {
  const [imgOk, setImgOk] = useState(!!item.image_url);
  const kind = getPlaceholderKind(item, item.item_type === "magic_item" ? "magic" : "equipment");

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal item-modal" onClick={e => e.stopPropagation()}>
        <button className="item-modal-close" onClick={onClose}>✕</button>
        <div className="item-modal-top">
          <div className="item-modal-img">
            {imgOk
              ? <img src={item.image_url} alt={item.title} onError={() => setImgOk(false)} />
              : <div className="item-modal-placeholder">{PLACEHOLDER_SVGS[kind]}</div>}
          </div>
          <div className="item-modal-info">
            <h3 className="item-modal-title">{item.title}</h3>
            {item.title_en && <div className="item-modal-en">{item.title_en}</div>}
            <div className="item-modal-tags">
              {item.rarity && <RarityBadge rarity={item.rarity} />}
              {item.type && <span className="item-tag">{item.type}</span>}
              {item.category && <span className="item-tag">{item.category}</span>}
              {item.damage && <span className="item-tag">⚔ {item.damage}</span>}
              {item.armor_class && <span className="item-tag">🛡 КД {item.armor_class}</span>}
            </div>
            <div className="item-modal-price">× {item.quantity} шт.</div>
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <button className="btn-secondary item-modal-btn" onClick={onTransfer}>⇄ Передать</button>
              <button className="btn-danger item-modal-btn" onClick={onRemove}>Выбросить</button>
            </div>
          </div>
        </div>
        {item.description && <div className="item-modal-desc">{item.description}</div>}
      </div>
    </div>
  );
}
