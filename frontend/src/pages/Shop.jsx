import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { priceInGold, RarityBadge, PLACEHOLDER_SVGS, getPlaceholderKind } from "../utils/itemUtils";

// ── Roulette Panel ────────────────────────────────────────────────────────────
function RoulettePanel({ onWalletChange }) {
  const [status, setStatus]   = useState(null);
  const [spinning, setSpinning] = useState(false);
  const [result, setResult]   = useState(null);
  const [msg, setMsg]         = useState("");

  const fetchStatus = () =>
    api.get("/roulette/status").then(r => setStatus(r.data)).catch(() => {});

  useEffect(() => { fetchStatus(); }, []);

  async function doSpin() {
    setMsg(""); setResult(null); setSpinning(true);
    await new Promise(r => setTimeout(r, 1400));
    try {
      const { data } = await api.post("/roulette/spin");
      setResult(data);
      setStatus(s => ({ ...s, can_spin: false, spun_today: true, unclaimed_item: data }));
      onWalletChange();
    } catch (e) {
      setMsg(e.response?.data?.detail || "Ошибка");
    }
    setSpinning(false);
  }

  async function doClaim(spinId) {
    try {
      await api.post(`/roulette/claim?spin_id=${spinId}`);
      setMsg("Предмет добавлен в инвентарь!");
      setResult(null);
      fetchStatus();
    } catch (e) {
      setMsg(e.response?.data?.detail || "Ошибка");
    }
  }

  const pending = result || status?.unclaimed_item;
  const pendingKind = pending ? getPlaceholderKind(pending, pending.item_type === "magic_item" ? "magic" : "equipment") : "default";
  const imgOk = pending?.image_url;

  return (
    <div className="roulette-panel">
      <h3 className="roulette-title">🎰 Рулетка Удачи</h3>
      <div className="roulette-cost">500 зм · 1 раз в день</div>

      {spinning && (
        <div className="roulette-spin-anim">
          <div className="roulette-slot spinning">
            {PLACEHOLDER_SVGS.magic}
          </div>
          <div className="roulette-spin-text">Судьба решает...</div>
        </div>
      )}

      {!spinning && pending && (
        <div className="roulette-result">
          <div className="roulette-item-img">
            {imgOk
              ? <img src={pending.image_url} alt={pending.title} />
              : <div className="roulette-item-placeholder">{PLACEHOLDER_SVGS[pendingKind]}</div>
            }
          </div>
          <div className="roulette-item-name">{pending.title}</div>
          {pending.rarity && <RarityBadge rarity={pending.rarity} />}
          {pending.category && <span className="item-tag">{pending.category}</span>}
          <button className="btn-roulette-claim" onClick={() => doClaim(pending.spin_id)}>
            Забрать в инвентарь
          </button>
        </div>
      )}

      {!spinning && !pending && status && (
        <button
          className="btn-roulette-spin"
          disabled={!status.can_spin}
          onClick={doSpin}
          title={!status.can_spin && status.spun_today ? `Следующий спин: ${new Date(status.next_reset).toLocaleTimeString("ru", { hour: "2-digit", minute: "2-digit" })} UTC` : ""}
        >
          {status.can_spin ? "🎲 Крутить" : status.spun_today ? "Уже крутили сегодня" : "Сначала заберите выигрыш"}
        </button>
      )}

      {msg && <div className={`roulette-msg ${msg.includes("инвентарь") ? "success" : "error"}`}>{msg}</div>}
    </div>
  );
}

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
        <div className="shop-items-area" style={{gridColumn: "1"}}>
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

        <div className="shop-right-col">
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
        <RoulettePanel onWalletChange={() => {
          api.get("/characters/me").then(r => {
            const c = r.data;
            setWallet(c.platinum * 1000 + c.gold * 100 + c.electrum * 50 + c.silver * 10 + c.copper);
          }).catch(() => {});
        }} />
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
  const [open, setOpen] = useState(false);
  const [imgOk, setImgOk] = useState(!!item.image_url);
  const kind = getPlaceholderKind(item, section);

  return (
    <>
      <div className="shop-item-card" onClick={() => setOpen(true)}>
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
          <div className="item-card-footer">
            <span className="item-price">{priceInGold(item.price_copper)}</span>
            <button className="btn-add-cart" onClick={e => { e.stopPropagation(); onAdd(item); }}>
              + В корзину
            </button>
          </div>
        </div>
      </div>

      {open && (
        <ItemModal item={item} section={section} kind={kind} onAdd={onAdd} onClose={() => setOpen(false)} />
      )}
    </>
  );
}

// ── Item detail modal ─────────────────────────────────────────────────────────
function ItemModal({ item, section, kind, onAdd, onClose }) {
  const [imgOk, setImgOk] = useState(!!item.image_url);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal item-modal" onClick={e => e.stopPropagation()}>
        <button className="item-modal-close" onClick={onClose}>✕</button>

        <div className="item-modal-top">
          <div className="item-modal-img">
            {imgOk ? (
              <img src={item.image_url} alt={item.title} onError={() => setImgOk(false)} />
            ) : (
              <div className="item-modal-placeholder">{PLACEHOLDER_SVGS[kind]}</div>
            )}
          </div>

          <div className="item-modal-info">
            <h3 className="item-modal-title">{item.title}</h3>
            {item.title_en && <div className="item-modal-en">{item.title_en}</div>}

            <div className="item-modal-tags">
              {section === "magic" ? (<>
                {item.type && <span className="item-tag">{item.type}</span>}
                <RarityBadge rarity={item.rarity} />
              </>) : (<>
                {item.category && <span className="item-tag">{item.category}</span>}
                {item.type && <span className="item-tag">{item.type}</span>}
                {item.damage && <span className="item-tag">⚔ {item.damage}</span>}
                {item.armor_class && <span className="item-tag">🛡 КД {item.armor_class}</span>}
              </>)}
            </div>

            <div className="item-modal-price">{priceInGold(item.price_copper)}</div>

            <button className="btn-add-cart item-modal-btn" onClick={() => { onAdd(item); onClose(); }}>
              + В корзину
            </button>
          </div>
        </div>

        {item.description && (
          <div className="item-modal-desc">{item.description}</div>
        )}
      </div>
    </div>
  );
}
