import json
import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from dependencies import get_current_user
from models import User, Character, InventoryItem, ItemTypeEnum

router = APIRouter(prefix="/shop", tags=["shop"])

# ── Валюта ──────────────────────────────────────────────────────────
COIN_ABBR = {"мм": 1, "см": 10, "эм": 50, "зм": 100, "пп": 1000}

RARITY_PRICE_ZM = {
    "обычный": 100, "обычное": 100, "обычная": 100,
    "необычный": 500, "необычное": 500, "необычная": 500,
    "редкий": 5000, "редкое": 5000, "редкая": 5000,
    "очень редкий": 50000, "очень редкое": 50000, "очень редкая": 50000,
    "легендарный": 500000, "легендарное": 500000,
    "артефакт": 1000000,
    "редкость варьируется": 1000,
}


def parse_price_copper(price_str: str) -> int:
    if not price_str:
        return 0
    s = price_str.strip().lower()
    for abbr, rate in COIN_ABBR.items():
        if abbr in s:
            try:
                num = float(s.replace(abbr, "").strip().replace(",", "."))
                return int(num * rate)
            except Exception:
                pass
    return 0


def copper_display(copper: int) -> str:
    """Форматирует медь в читаемый вид: 500 → '5 зм', 15000 → '150 зм'"""
    if copper == 0:
        return "0 мм"
    for rate, abbr in [(1000, "пп"), (100, "зм"), (50, "эм"), (10, "см"), (1, "мм")]:
        if copper >= rate and copper % rate == 0:
            return f"{copper // rate} {abbr}"
    zm = copper / 100
    return f"{zm:.2g} зм"


def char_total_copper(char: Character) -> int:
    return (char.platinum * 1000 + char.gold * 100
            + char.electrum * 50 + char.silver * 10 + char.copper)


def apply_coins_from_copper(char: Character, copper: int):
    char.platinum, r = divmod(copper, 1000)
    char.gold,     r = divmod(r, 100)
    char.electrum, r = divmod(r, 50)
    char.silver,   r = divmod(r, 10)
    char.copper = r


# ── Логика торга ─────────────────────────────────────────────────────
def bargain_multiplier(buyer: int, seller: int) -> float:
    if buyer == 1 and seller == 1:
        return 1.0
    if seller == 1 and buyer > 1:
        return 0.5
    if buyer == 1 and seller > 1:
        return 1.5
    if seller > buyer:
        return 1.0
    diff = buyer - seller
    if diff >= 18: return 0.6
    if diff >= 15: return 0.7
    if diff >= 10: return 0.8
    if diff >= 5:  return 0.9
    return 0.95


# ── Фильтры ──────────────────────────────────────────────────────────
@router.get("/magic-items/filters")
def magic_items_filters(db: Session = Depends(get_db)):
    types    = [r[0] for r in db.execute(text("SELECT DISTINCT type FROM items WHERE type IS NOT NULL AND type != '' ORDER BY type")).fetchall()]
    rarities = [r[0] for r in db.execute(text("SELECT DISTINCT rarity_tag FROM items WHERE rarity_tag IS NOT NULL AND rarity_tag != '' ORDER BY rarity_tag")).fetchall()]
    return {"types": types, "rarities": rarities}


@router.get("/equipment/filters")
def equipment_filters(db: Session = Depends(get_db)):
    categories = [r[0] for r in db.execute(text("SELECT DISTINCT category FROM equipment WHERE category IS NOT NULL ORDER BY category")).fetchall()]
    rows = db.execute(text("SELECT filter_tags FROM equipment WHERE filter_tags IS NOT NULL")).fetchall()
    props, masteries = set(), set()
    for (raw,) in rows:
        try:
            tags = json.loads(raw) if isinstance(raw, str) else raw
            props.update(tags.get("weapon_property", []))
            masteries.update(tags.get("weapon_mastery", []))
        except Exception:
            pass
    props.discard("")
    masteries.discard("")
    return {
        "categories": categories,
        "weapon_properties": sorted(props),
        "weapon_masteries": sorted(masteries),
    }


# ── Список предметов ──────────────────────────────────────────────────
@router.get("/magic-items")
def list_magic_items(
    type: Optional[str] = None,
    rarity: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(24, le=100),
    db: Session = Depends(get_db),
):
    where, params = ["1=1"], {}
    if type:
        where.append("type = :type");    params["type"] = type
    if rarity:
        where.append("rarity_tag = :rarity"); params["rarity"] = rarity
    if search:
        where.append("(LOWER(title) LIKE :s OR LOWER(title_en) LIKE :s)")
        params["s"] = f"%{search.lower()}%"

    cond = " AND ".join(where)
    total = db.execute(text(f"SELECT COUNT(*) FROM items WHERE {cond}"), params).scalar()
    rows  = db.execute(
        text(f"SELECT id, title, title_en, type, rarity_tag, image_url, description FROM items WHERE {cond} ORDER BY id LIMIT :lim OFFSET :off"),
        {**params, "lim": limit, "off": (page - 1) * limit}
    ).fetchall()

    items = []
    for r in rows:
        price_copper = RARITY_PRICE_ZM.get(r.rarity_tag, 100) * 100
        items.append({
            "id": r.id, "title": r.title, "title_en": r.title_en,
            "type": r.type, "rarity": r.rarity_tag,
            "image_url": r.image_url, "description": r.description or "",
            "price_copper": price_copper,
            "price_display": copper_display(price_copper),
        })
    return {"items": items, "total": total, "pages": (total + limit - 1) // limit}


@router.get("/equipment")
def list_equipment(
    category: Optional[str] = None,
    weapon_property: Optional[str] = None,
    weapon_mastery: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(24, le=100),
    db: Session = Depends(get_db),
):
    where, params = ["1=1"], {}
    if category:
        where.append("category = :cat"); params["cat"] = category
    if search:
        where.append("(LOWER(title) LIKE :s OR LOWER(title_en) LIKE :s)")
        params["s"] = f"%{search.lower()}%"

    cond = " AND ".join(where)
    all_rows = db.execute(
        text(f"SELECT id, title, title_en, category, price, damage, armor_class, type, filter_tags, image_url, description FROM equipment WHERE {cond} ORDER BY id"),
        params
    ).fetchall()

    # Фильтр по weapon_property / weapon_mastery (через JSON)
    def matches(row):
        if not weapon_property and not weapon_mastery:
            return True
        try:
            tags = json.loads(row.filter_tags) if isinstance(row.filter_tags, str) else (row.filter_tags or {})
        except Exception:
            return False
        if weapon_property and weapon_property not in tags.get("weapon_property", []):
            return False
        if weapon_mastery and weapon_mastery not in tags.get("weapon_mastery", []):
            return False
        return True

    filtered = [r for r in all_rows if matches(r)]
    total = len(filtered)
    page_rows = filtered[(page - 1) * limit: page * limit]

    items = []
    for r in page_rows:
        price_copper = parse_price_copper(r.price or "")
        items.append({
            "id": r.id, "title": r.title, "title_en": r.title_en,
            "category": r.category, "type": r.type,
            "price": r.price or "", "damage": r.damage or "",
            "armor_class": r.armor_class or "",
            "image_url": r.image_url or "",
            "description": r.description or "",
            "price_copper": price_copper,
            "price_display": r.price or "—",
        })
    return {"items": items, "total": total, "pages": (total + limit - 1) // limit}


# ── Торг ──────────────────────────────────────────────────────────────
@router.post("/bargain")
def bargain(_=Depends(get_current_user)):
    buyer  = random.randint(1, 20)
    seller = random.randint(1, 20)
    mult   = bargain_multiplier(buyer, seller)

    if mult < 1.0:
        pct = int((1 - mult) * 100)
        result_text = f"Скидка {pct}%!" if pct else "Базовая цена"
    elif mult > 1.0:
        pct = int((mult - 1) * 100)
        result_text = f"Наценка {pct}%!"
    else:
        result_text = "Базовая цена"

    return {"buyer_roll": buyer, "seller_roll": seller,
            "multiplier": mult, "result_text": result_text}


# ── Покупка ───────────────────────────────────────────────────────────
from pydantic import BaseModel
from typing import List as TList

class CartItem(BaseModel):
    item_type: str   # "magic_item" | "equipment"
    item_id: int
    quantity: int = 1

class PurchaseRequest(BaseModel):
    cart: TList[CartItem]
    multiplier: float = 1.0


@router.post("/purchase")
def purchase(req: PurchaseRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(404, "Персонаж не создан")

    if not (0.5 <= req.multiplier <= 1.5):
        raise HTTPException(400, "Недопустимый множитель цены")

    total_copper = 0
    resolved = []

    for ci in req.cart:
        if ci.item_type == "magic_item":
            row = db.execute(text("SELECT id, title, rarity_tag FROM items WHERE id=:id"), {"id": ci.item_id}).fetchone()
            if not row:
                raise HTTPException(404, f"Предмет {ci.item_id} не найден")
            base = RARITY_PRICE_ZM.get(row.rarity_tag, 100) * 100
            resolved.append({"type": "magic_item", "row": row, "base": base, "qty": ci.quantity})
        else:
            row = db.execute(text("SELECT id, title, price FROM equipment WHERE id=:id"), {"id": ci.item_id}).fetchone()
            if not row:
                raise HTTPException(404, f"Снаряжение {ci.item_id} не найдено")
            base = parse_price_copper(row.price or "")
            resolved.append({"type": "equipment", "row": row, "base": base, "qty": ci.quantity})

        total_copper += int(resolved[-1]["base"] * req.multiplier) * ci.quantity

    wallet = char_total_copper(char)
    if wallet < total_copper:
        raise HTTPException(400, f"Недостаточно монет. Нужно: {copper_display(total_copper)}, есть: {copper_display(wallet)}")

    apply_coins_from_copper(char, wallet - total_copper)

    for item in resolved:
        existing = db.query(InventoryItem).filter(
            InventoryItem.character_id == char.id,
            InventoryItem.item_type == ItemTypeEnum(item["type"]),
            InventoryItem.shop_item_id == item["row"].id,
        ).first()
        if existing:
            existing.quantity += item["qty"]
        else:
            db.add(InventoryItem(
                character_id=char.id,
                item_type=ItemTypeEnum(item["type"]),
                shop_item_id=item["row"].id,
                quantity=item["qty"],
            ))

    db.commit()
    return {"detail": f"Куплено на {copper_display(total_copper)}. Остаток: {copper_display(char_total_copper(char))}"}
