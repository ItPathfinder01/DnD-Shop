import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

// ── Price helpers ─────────────────────────────────────────────────────────────
function priceInGold(copper) {
  if (!copper) return "—";
  const g = copper / 100;
  return g % 1 === 0 ? `${g} зм` : `${g.toFixed(1)} зм`;
}

// ── Placeholder icons ─────────────────────────────────────────────────────────
function getPlaceholderKind(item, section) {
  const t = (section === "magic"
    ? (item.type || "") + " " + (item.rarity || "")
    : (item.category || "") + " " + (item.type || "")
  ).toLowerCase();
  if (/оружие|меч|кинжал|топор|копь|лук|арбалет|дубин|булав|молот|серп|коса|праща|рапир|шпаг|сабл|фехт/.test(t)) return "weapon";
  if (/доспех|броня|кольчуг|латы|нагрудник|кираса/.test(t)) return "armor";
  if (/щит/.test(t)) return "shield";
  if (/зелье/.test(t)) return "potion";
  if (/свиток/.test(t)) return "scroll";
  if (/кольцо/.test(t)) return "ring";
  if (/волшебная палочка|жезл/.test(t)) return "wand";
  if (/посох/.test(t)) return "staff";
  if (/артефакт/.test(t)) return "artifact";
  if (/чудесный/.test(t)) return "wondrous";
  return "default";
}

const PLACEHOLDER_SVGS = (() => {
  const p = { fill: "none", stroke: "#c9a84c", strokeWidth: "1.5", strokeLinecap: "round", strokeLinejoin: "round", opacity: "0.45" };
  return {
    weapon: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <line x1="30" y1="7" x2="30" y2="44"/>
        <line x1="20" y1="27" x2="40" y2="27"/>
        <path d="M28 44 L30 53 L32 44"/>
        <circle cx="30" cy="7" r="2" fill="rgba(201,168,76,0.2)"/>
      </svg>
    ),
    armor: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M30 8 L42 14 L42 30 Q42 46 30 52 Q18 46 18 30 L18 14 Z"/>
        <path d="M30 8 Q30 20 30 52" strokeOpacity="0.4"/>
        <path d="M20 22 Q30 26 40 22" strokeOpacity="0.4"/>
      </svg>
    ),
    shield: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M30 7 L52 17 L52 35 Q52 50 30 56 Q8 50 8 35 L8 17 Z"/>
        <path d="M30 16 L43 22 L43 34 Q43 44 30 49 Q17 44 17 34 L17 22 Z" strokeOpacity="0.35"/>
      </svg>
    ),
    potion: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M24 22 L24 10 L36 10 L36 22 L46 40 Q50 55 30 55 Q10 55 14 40 Z"/>
        <line x1="22" y1="12" x2="38" y2="12"/>
        <ellipse cx="30" cy="42" rx="9" ry="5" fill="rgba(201,168,76,0.15)"/>
        <path d="M20 30 Q25 27 30 30" strokeOpacity="0.5"/>
      </svg>
    ),
    scroll: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M16 14 Q16 7 23 7 L50 7 Q57 7 57 14 L57 46 Q57 53 50 53 L23 53 Q16 53 16 46 L16 14 Z"/>
        <path d="M16 14 Q9 14 9 21 L9 46 Q9 53 16 53"/>
        <line x1="24" y1="20" x2="49" y2="20"/>
        <line x1="24" y1="28" x2="49" y2="28"/>
        <line x1="24" y1="36" x2="39" y2="36"/>
      </svg>
    ),
    ring: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <ellipse cx="30" cy="36" rx="15" ry="9"/>
        <ellipse cx="30" cy="27" rx="15" ry="9"/>
        <line x1="15" y1="27" x2="15" y2="36"/>
        <line x1="45" y1="27" x2="45" y2="36"/>
        <polygon points="30,10 36,22 24,22" fill="rgba(201,168,76,0.2)"/>
        <line x1="28" y1="22" x2="26" y2="27" strokeOpacity="0.4"/>
        <line x1="32" y1="22" x2="34" y2="27" strokeOpacity="0.4"/>
      </svg>
    ),
    wand: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <line x1="10" y1="50" x2="44" y2="16"/>
        <circle cx="47" cy="13" r="5" fill="rgba(201,168,76,0.15)"/>
        <line x1="47" y1="6" x2="47" y2="3"/>
        <line x1="52" y1="9" x2="55" y2="7"/>
        <line x1="54" y1="14" x2="57" y2="14"/>
        <line x1="52" y1="18" x2="54" y2="21"/>
        <line x1="42" y1="8" x2="40" y2="5"/>
      </svg>
    ),
    staff: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <line x1="30" y1="55" x2="30" y2="18"/>
        <circle cx="30" cy="13" r="7" fill="rgba(201,168,76,0.1)"/>
        <circle cx="30" cy="13" r="4" fill="rgba(201,168,76,0.2)"/>
        <path d="M23 32 Q30 27 37 32" strokeOpacity="0.5"/>
        <path d="M24 40 Q30 36 36 40" strokeOpacity="0.3"/>
      </svg>
    ),
    artifact: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <polygon points="30,4 35,22 53,22 39,33 44,51 30,40 16,51 21,33 7,22 25,22" fill="rgba(201,168,76,0.08)"/>
        <polygon points="30,13 33,23 43,23 35,29 38,39 30,33 22,39 25,29 17,23 27,23" fill="rgba(201,168,76,0.12)" strokeOpacity="0.5"/>
      </svg>
    ),
    wondrous: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <circle cx="30" cy="30" r="20"/>
        <circle cx="30" cy="30" r="13" strokeOpacity="0.4"/>
        <path d="M30 10 L30 16 M30 44 L30 50 M10 30 L16 30 M44 30 L50 30" strokeOpacity="0.6"/>
        <path d="M16 16 L20 20 M40 40 L44 44 M44 16 L40 20 M20 40 L16 44" strokeOpacity="0.4" strokeWidth="1"/>
        <circle cx="30" cy="30" r="4" fill="rgba(201,168,76,0.2)"/>
      </svg>
    ),
    default: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <polygon points="30,6 54,20 54,40 30,54 6,40 6,20" fill="rgba(201,168,76,0.06)"/>
        <polygon points="30,14 46,23 46,37 30,46 14,37 14,23" strokeOpacity="0.4"/>
        <circle cx="30" cy="30" r="5" fill="rgba(201,168,76,0.2)"/>
      </svg>
    ),
  };
})();

// ── Dice SVG ──────────────────────────────────────────────────────────────────
function D20Icon({ value, rolling }) {
  return (
    <div className={`d20-wrap ${rolling ? "rolling" : ""}`}>
      <svg viewBox="0 0 100 100" width="80" height="80">
        <polygon points="50,5 95,28 95,72 50,95 5,72 5,28" fill="#1a0f2e" stroke="#c9a84c" strokeWidth="2"/>
        <polygon points="50,5 95,28 50,42" fill="none" stroke="#c9a84c" strokeWidth="1" opacity="0.5"/>
        <polygon points="50,5 5,28 50,42" fill="none" stroke="#c9a84c" strokeWidth="1" opacity="0.5"/>
        <polygon points="5,28 5,72 50,58" fill="none" stroke="#c9a84c" strokeWidth="1" opacity="0.5"/>
        <polygon points="95,28 95,72 50,58" fill="none" stroke="#c9a84c" strokeWidth="1" opacity="0.5"/>
        <polygon points="50,95 5,72 50,58" fill="none" stroke="#c9a84c" strokeWidth="1" opacity="0.5"/>
        <polygon points="50,95 95,72 50,58" fill="none" stroke="#c9a84c" strokeWidth="1" opacity="0.5"/>
        <text x="50" y="56" textAnchor="middle" fill="#e8d080" fontFamily="Cinzel, serif" fontSize="22" fontWeight="bold">
          {rolling ? "?" : (value ?? "?")}
        </text>
      </svg>
    </div>
  );
}

// ── Rarity badge ──────────────────────────────────────────────────────────────
const RARITY_COLOR = {
  "обычный": "#b0a080", "обычное": "#b0a080", "обычная": "#b0a080",
  "необычный": "#4ec94e", "необычное": "#4ec94e", "необычная": "#4ec94e",
  "редкий": "#4a90e2", "редкое": "#4a90e2", "редкая": "#4a90e2",
  "очень редкий": "#9b59b6", "очень редкое": "#9b59b6", "очень редкая": "#9b59b6",
  "легендарный": "#e8a020", "легендарное": "#e8a020",
  "артефакт": "#ff4444",
  "редкость варьируется": "#a0a0a0",
};

function RarityBadge({ rarity }) {
  if (!rarity) return null;
  return (
    <span className="rarity-badge" style={{ borderColor: RARITY_COLOR[rarity] || "#7a6a50", color: RARITY_COLOR[rarity] || "#7a6a50" }}>
      {rarity}
    </span>
  );
}

// ── Cart item row ─────────────────────────────────────────────────────────────
function CartRow({ item, onRemove, multiplier }) {
  const finalPrice = Math.round(item.price_copper * multiplier) * item.qty;
  return (
    <div className="cart-row">
      <div className="cart-row-name">{item.title}</div>
      <div className="cart-row-meta">
        <span className="cart-qty">×{item.qty}</span>
        <span className="cart-price">{priceInGold(finalPrice)}</span>
        <button className="btn-remove" onClick={() => onRemove(item.key)}>✕</button>
      </div>
    </div>
  );
}

// ── Main Shop component ───────────────────────────────────────────────────────
export default function Shop() {
  const navigate = useNavigate();
  const [section, setSection] = useState("magic");
  const [filters, setFilters] = useState({ magic: {}, equip: {} });
  const [filterOpts, setFilterOpts] = useState({ magic: {}, equip: {} });
  const [search, setSearch] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [cart, setCart] = useState([]);
  const [showBargain, setShowBargain] = useState(false);
  const [bargainResult, setBargainResult] = useState(null);
  const [rolling, setRolling] = useState(false);
  const [multiplier, setMultiplier] = useState(1.0);
  const [bargainDone, setBargainDone] = useState(false);
  const [purchaseMsg, setPurchaseMsg] = useState("");
  const [wallet, setWallet] = useState(null);

  const pageRef    = useRef(1);
  const hasMoreRef = useRef(true);
  const loadingRef = useRef(false);
  const sentinelRef = useRef(null);

  useEffect(() => {
    api.get("/characters/me").then(r => {
      const c = r.data;
      setWallet(c.platinum * 1000 + c.gold * 100 + c.electrum * 50 + c.silver * 10 + c.copper);
    }).catch(() => {});
  }, [purchaseMsg]);

  useEffect(() => {
    api.get("/shop/magic-items/filters").then(r => setFilterOpts(p => ({ ...p, magic: r.data }))).catch(() => {});
    api.get("/shop/equipment/filters").then(r => setFilterOpts(p => ({ ...p, equip: r.data }))).catch(() => {});
  }, []);

  const doLoad = useCallback(async (reset = false) => {
    if (loadingRef.current) return;
    if (!reset && !hasMoreRef.current) return;
    loadingRef.current = true;
    setLoading(true);

    const p = reset ? 1 : pageRef.current;
    const params = { page: p, limit: 20 };
    if (search) params.search = search;

    let url;
    if (section === "magic") {
      url = "/shop/magic-items";
      if (filters.magic.type)   params.type   = filters.magic.type;
      if (filters.magic.rarity) params.rarity = filters.magic.rarity;
    } else {
      url = "/shop/equipment";
      if (filters.equip.category)        params.category        = filters.equip.category;
      if (filters.equip.weapon_property) params.weapon_property = filters.equip.weapon_property;
      if (filters.equip.weapon_mastery)  params.weapon_mastery  = filters.equip.weapon_mastery;
    }

    try {
      const res = await api.get(url, { params });
      const { items: newItems, pages } = res.data;
      setItems(prev => reset ? newItems : [...prev, ...newItems]);
      pageRef.current    = p + 1;
      hasMoreRef.current = p < pages;
      setHasMore(p < pages);
    } catch {/* ignore */} finally {
      loadingRef.current = false;
      setLoading(false);
    }
  }, [section, search, filters.magic.type, filters.magic.rarity,
      filters.equip.category, filters.equip.weapon_property, filters.equip.weapon_mastery]);

  // Reset + load page 1 when query changes
  useEffect(() => {
    pageRef.current    = 1;
    hasMoreRef.current = true;
    doLoad(true);
  }, [doLoad]);

  // Keep a fresh ref for the observer callback
  const doLoadRef = useRef(doLoad);
  useEffect(() => { doLoadRef.current = doLoad; }, [doLoad]);

  // Infinite scroll via IntersectionObserver
  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      entries => { if (entries[0].isIntersecting) doLoadRef.current(false); },
      { threshold: 0.1, rootMargin: "120px" }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  function addToCart(item) {
    const itype = section === "magic" ? "magic_item" : "equipment";
    const key = `${itype}_${item.id}`;
    setCart(prev => {
      const ex = prev.find(c => c.key === key);
      if (ex) return prev.map(c => c.key === key ? { ...c, qty: c.qty + 1 } : c);
      return [...prev, { key, item_type: itype, item_id: item.id, title: item.title, price_copper: item.price_copper, qty: 1 }];
    });
  }

  function removeFromCart(key) { setCart(prev => prev.filter(c => c.key !== key)); }

  const cartTotal = cart.reduce((s, c) => s + Math.round(c.price_copper * multiplier) * c.qty, 0);
  const cartCount = cart.reduce((s, c) => s + c.qty, 0);

  async function doBargain() {
    setShowBargain(true);
    setBargainResult(null);
    setBargainDone(false);
    setMultiplier(1.0);
    setRolling(true);
    setPurchaseMsg("");
    await new Promise(r => setTimeout(r, 900));
    try {
      const res = await api.post("/shop/bargain");
      setBargainResult(res.data);
      setMultiplier(res.data.multiplier);
    } catch {
      setBargainResult({ buyer_roll: "?", seller_roll: "?", multiplier: 1.0, result_text: "Ошибка" });
    }
    setRolling(false);
    setBargainDone(true);
  }

  async function doPurchase() {
    try {
      const res = await api.post("/shop/purchase", {
        cart: cart.map(c => ({ item_type: c.item_type, item_id: c.item_id, quantity: c.qty })),
        multiplier,
      });
      setPurchaseMsg(res.data.detail);
      setCart([]);
      setShowBargain(false);
      setBargainDone(false);
      setMultiplier(1.0);
    } catch (e) {
      setPurchaseMsg(e.response?.data?.detail || "Ошибка покупки");
    }
  }

  const setMagicFilter = (k, v) => setFilters(p => ({ ...p, magic: { ...p.magic, [k]: v } }));
  const setEquipFilter = (k, v) => setFilters(p => ({ ...p, equip: { ...p.equip, [k]: v } }));
  const { magic: magicF, equip: equipF } = filterOpts;
  const activeFilters = section === "magic" ? filters.magic : filters.equip;
  const hasActiveFilter = Object.values(activeFilters).some(Boolean) || !!search;

  return (
    <div className="shop-page">
      <div className="shop-bg-glow" />

      <div className="shop-header">
        <button className="btn-back" onClick={() => navigate("/character")}>← Назад</button>
        <h2>Лавка Приключенца</h2>
        <div className="shop-wallet">
          {wallet !== null && <span>Кошель: <b>{priceInGold(wallet)}</b></span>}
        </div>
      </div>

      <div className="shop-tabs">
        <button className={`shop-tab ${section === "magic" ? "active" : ""}`}
          onClick={() => { setSection("magic"); setSearch(""); }}>
          ✦ Волшебные предметы
        </button>
        <button className={`shop-tab ${section === "equipment" ? "active" : ""}`}
          onClick={() => { setSection("equipment"); setSearch(""); }}>
          ⚔ Снаряжение
        </button>
      </div>

      <div className="shop-filters">
        <input className="shop-search" placeholder="Поиск..." value={search} onChange={e => setSearch(e.target.value)} />
        {section === "magic" ? (<>
          <select value={filters.magic.type || ""} onChange={e => setMagicFilter("type", e.target.value)}>
            <option value="">Все типы</option>
            {(magicF.types || []).map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          <select value={filters.magic.rarity || ""} onChange={e => setMagicFilter("rarity", e.target.value)}>
            <option value="">Все редкости</option>
            {(magicF.rarities || []).map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </>) : (<>
          <select value={filters.equip.category || ""} onChange={e => setEquipFilter("category", e.target.value)}>
            <option value="">Все категории</option>
            {(equipF.categories || []).map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={filters.equip.weapon_property || ""} onChange={e => setEquipFilter("weapon_property", e.target.value)}>
            <option value="">Все свойства</option>
            {(equipF.weapon_properties || []).map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <select value={filters.equip.weapon_mastery || ""} onChange={e => setEquipFilter("weapon_mastery", e.target.value)}>
            <option value="">Все мастерства</option>
            {(equipF.weapon_masteries || []).map(m => <option key={m} value={m}>{m}</option>)}
          </select>
        </>)}
        {hasActiveFilter && (
          <button className="btn-secondary btn-small" onClick={() => {
            setSearch("");
            setFilters(p => ({ ...p, [section === "magic" ? "magic" : "equip"]: {} }));
          }}>Сбросить</button>
        )}
      </div>

      <div className="shop-layout">
        <div className="shop-items-area">
          {items.length === 0 && !loading && <div className="shop-empty">Ничего не найдено</div>}
          <div className="shop-grid">
            {items.map(item => (
              <ItemCard key={item.id} item={item} section={section} onAdd={addToCart} />
            ))}
          </div>
          <div ref={sentinelRef} className="shop-sentinel" />
          {loading && (
            <div className="shop-loading">
              <span className="shop-spinner" />
              Загрузка...
            </div>
          )}
          {!hasMore && items.length > 0 && (
            <div className="shop-end">✦ Конец каталога ✦</div>
          )}
        </div>

        <div className="shop-cart">
          <h3>Корзина {cartCount > 0 && <span className="cart-count">{cartCount}</span>}</h3>
          {cart.length === 0 ? (
            <p className="cart-empty">Корзина пуста</p>
          ) : (<>
            <div className="cart-items">
              {cart.map(c => <CartRow key={c.key} item={c} onRemove={removeFromCart} multiplier={multiplier} />)}
            </div>
            <div className="cart-total">
              Итого: <b>{priceInGold(cartTotal)}</b>
              {multiplier !== 1.0 && (
                <span className={`cart-mult ${multiplier < 1 ? "good" : "bad"}`}>
                  {multiplier < 1 ? `−${Math.round((1 - multiplier) * 100)}%` : `+${Math.round((multiplier - 1) * 100)}%`}
                </span>
              )}
            </div>
            <button className="btn-bargain" onClick={doBargain}>🎲 Торг</button>
            {bargainDone && (
              <button className="btn-buy" onClick={doPurchase}>
                Купить за {priceInGold(cartTotal)}
              </button>
            )}
          </>)}
          {purchaseMsg && (
            <div className={`purchase-msg ${purchaseMsg.includes("Куплено") ? "success" : "error"}`}>
              {purchaseMsg}
            </div>
          )}
        </div>
      </div>

      {showBargain && (
        <div className="modal-overlay" onClick={() => { if (!rolling) setShowBargain(false); }}>
          <div className="modal bargain-modal" onClick={e => e.stopPropagation()}>
            <h3>⚔ Торг с торговцем</h3>
            <div className="bargain-dice-row">
              <div className="bargain-side">
                <div className="bargain-label">Покупатель</div>
                <D20Icon value={bargainResult?.buyer_roll} rolling={rolling} />
              </div>
              <div className="bargain-vs">vs</div>
              <div className="bargain-side">
                <div className="bargain-label">Продавец</div>
                <D20Icon value={bargainResult?.seller_roll} rolling={rolling} />
              </div>
            </div>
            {!rolling && bargainResult && (
              <div className={`bargain-result ${bargainResult.multiplier < 1 ? "good" : bargainResult.multiplier > 1 ? "bad" : "neutral"}`}>
                {bargainResult.result_text}
              </div>
            )}
            <div className="bargain-actions">
              {rolling ? (
                <p className="bargain-rolling">Кубики в воздухе...</p>
              ) : (<>
                <button onClick={() => setShowBargain(false)}>
                  {bargainDone ? "Принять и закрыть" : "Закрыть"}
                </button>
                {bargainDone && (
                  <button className="btn-buy-modal" onClick={async () => { setShowBargain(false); await doPurchase(); }}>
                    Купить за {priceInGold(cartTotal)}
                  </button>
                )}
              </>)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Item card ─────────────────────────────────────────────────────────────────
function ItemCard({ item, section, onAdd }) {
  const [expanded, setExpanded] = useState(false);
  const [imgOk, setImgOk] = useState(!!item.image_url);
  const kind = getPlaceholderKind(item, section);

  return (
    <div className="shop-item-card" onClick={() => setExpanded(e => !e)}>
      <div className="item-img-wrap">
        {imgOk ? (
          <img src={item.image_url} alt={item.title} loading="lazy" onError={() => setImgOk(false)} />
        ) : (
          <div className="item-img-placeholder">
            {PLACEHOLDER_SVGS[kind]}
          </div>
        )}
      </div>
      <div className="item-card-body">
        <div className="item-card-title">{item.title}</div>
        {section === "magic" ? (
          <RarityBadge rarity={item.rarity} />
        ) : (
          <div className="item-card-meta">
            {item.category && <span className="item-tag">{item.category}</span>}
            {item.damage && <span className="item-tag">{item.damage}</span>}
            {item.armor_class && <span className="item-tag">КД {item.armor_class}</span>}
          </div>
        )}
        {expanded && item.description && (
          <div className="item-card-desc">{item.description}</div>
        )}
        <div className="item-card-footer">
          <span className="item-price">{priceInGold(item.price_copper)}</span>
          <button className="btn-add-cart" onClick={e => { e.stopPropagation(); onAdd(item); }}>
            + В корзину
          </button>
        </div>
      </div>
    </div>
  );
}
