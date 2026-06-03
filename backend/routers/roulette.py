import random
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from dependencies import get_current_user
from models import User, RouletteHistory, InventoryItem, ItemTypeEnum

SPIN_COST_GOLD = 500
SPIN_COST_COPPER = SPIN_COST_GOLD * 100

router = APIRouter(prefix="/roulette", tags=["roulette"])


def _today_utc_start() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)


def _next_reset_utc() -> datetime:
    return _today_utc_start() + timedelta(days=1)


def _unclaimed_spin(db: Session, character_id: int) -> RouletteHistory | None:
    return (
        db.query(RouletteHistory)
        .filter(RouletteHistory.character_id == character_id, RouletteHistory.is_claimed == False)
        .order_by(RouletteHistory.spun_at.desc())
        .first()
    )


def _spun_today(db: Session, character_id: int) -> bool:
    today = _today_utc_start()
    return (
        db.query(RouletteHistory)
        .filter(RouletteHistory.character_id == character_id, RouletteHistory.spun_at >= today)
        .first()
    ) is not None


def _item_details(db: Session, item_id: int, item_type: str) -> dict:
    if item_type == "magic_item":
        row = db.execute(
            text("SELECT id, title, title_en, type, rarity_tag, image_url FROM items WHERE id=:id"),
            {"id": item_id},
        ).fetchone()
        if not row:
            return {}
        return {
            "id": row.id, "title": row.title, "title_en": row.title_en,
            "type": row.type, "rarity": row.rarity_tag,
            "image_url": row.image_url or "", "item_type": "magic_item",
            "category": None,
        }
    else:
        row = db.execute(
            text("SELECT id, title, title_en, category, type, image_url FROM equipment WHERE id=:id"),
            {"id": item_id},
        ).fetchone()
        if not row:
            return {}
        return {
            "id": row.id, "title": row.title, "title_en": row.title_en,
            "type": row.type, "rarity": None,
            "image_url": row.image_url or "", "item_type": "equipment",
            "category": row.category,
        }


def _pick_random_item(db: Session) -> tuple[int, str]:
    total_magic = db.execute(text("SELECT COUNT(*) FROM items")).scalar() or 0
    total_equip = db.execute(text("SELECT COUNT(*) FROM equipment")).scalar() or 0
    total = total_magic + total_equip
    if total == 0:
        raise HTTPException(status_code=500, detail="Нет предметов в базе")

    idx = random.randint(0, total - 1)
    if idx < total_magic:
        row = db.execute(
            text("SELECT id FROM items ORDER BY id LIMIT 1 OFFSET :off"),
            {"off": idx},
        ).fetchone()
        return row.id, "magic_item"
    else:
        row = db.execute(
            text("SELECT id FROM equipment ORDER BY id LIMIT 1 OFFSET :off"),
            {"off": idx - total_magic},
        ).fetchone()
        return row.id, "equipment"


@router.get("/status")
def roulette_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    unclaimed = _unclaimed_spin(db, char.id)
    spun_today = _spun_today(db, char.id)
    can_spin = not spun_today and unclaimed is None

    unclaimed_item = None
    if unclaimed:
        unclaimed_item = {"spin_id": unclaimed.id, **_item_details(db, unclaimed.item_id, unclaimed.item_type)}

    return {
        "can_spin": can_spin,
        "spun_today": spun_today,
        "unclaimed_item": unclaimed_item,
        "next_reset": _next_reset_utc().isoformat() + "Z",
        "spin_cost_gold": SPIN_COST_GOLD,
    }


@router.post("/spin")
def spin_roulette(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    if char.gold < SPIN_COST_GOLD:
        raise HTTPException(status_code=400, detail=f"Недостаточно золота. Нужно {SPIN_COST_GOLD} зм")

    if _unclaimed_spin(db, char.id):
        raise HTTPException(status_code=400, detail="Сначала заберите предыдущий выигрыш")

    if _spun_today(db, char.id):
        next_reset = _next_reset_utc()
        raise HTTPException(
            status_code=403,
            detail=f"Уже крутили сегодня. Следующий спин в {next_reset.strftime('%H:%M')} UTC",
        )

    char.gold -= SPIN_COST_GOLD

    item_id, item_type = _pick_random_item(db)

    spin = RouletteHistory(
        character_id=char.id,
        item_id=item_id,
        item_type=item_type,
    )
    db.add(spin)
    db.commit()
    db.refresh(spin)

    return {"spin_id": spin.id, **_item_details(db, item_id, item_type)}


@router.post("/claim")
def claim_item(spin_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    spin = db.get(RouletteHistory, spin_id)
    if not spin or spin.character_id != char.id:
        raise HTTPException(status_code=404, detail="Спин не найден")
    if spin.is_claimed:
        raise HTTPException(status_code=400, detail="Предмет уже забран")

    existing = db.query(InventoryItem).filter(
        InventoryItem.character_id == char.id,
        InventoryItem.item_type == ItemTypeEnum(spin.item_type),
        InventoryItem.shop_item_id == spin.item_id,
        InventoryItem.custom_name == None,
    ).first()

    if existing:
        existing.quantity += 1
    else:
        db.add(InventoryItem(
            character_id=char.id,
            item_type=ItemTypeEnum(spin.item_type),
            shop_item_id=spin.item_id,
            quantity=1,
        ))

    spin.is_claimed = True
    spin.claimed_at = datetime.utcnow()
    db.commit()

    return {"detail": "Предмет добавлен в инвентарь"}


@router.get("/history")
def roulette_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    spins = (
        db.query(RouletteHistory)
        .filter(RouletteHistory.character_id == char.id)
        .order_by(RouletteHistory.spun_at.desc())
        .limit(30)
        .all()
    )
    result = []
    for s in spins:
        details = _item_details(db, s.item_id, s.item_type)
        result.append({
            "spin_id": s.id,
            "spun_at": s.spun_at.isoformat() + "Z",
            "is_claimed": s.is_claimed,
            "claimed_at": s.claimed_at.isoformat() + "Z" if s.claimed_at else None,
            **details,
        })
    return result
