from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import User, InventoryItem, ItemTypeEnum
from schemas import InventoryItemCreate, InventoryItemResponse

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("")
def get_inventory(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user.character:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    result = []
    for inv in user.character.inventory:
        itype = inv.item_type.value if hasattr(inv.item_type, "value") else inv.item_type
        entry = {
            "id": inv.id,
            "item_type": itype,
            "shop_item_id": inv.shop_item_id,
            "custom_name": inv.custom_name,
            "quantity": inv.quantity,
            "title": inv.custom_name or "",
            "image_url": "",
            "rarity": None,
            "type": None,
            "category": None,
            "damage": None,
            "armor_class": None,
        }
        if itype == "magic_item" and inv.shop_item_id:
            row = db.execute(
                text("SELECT title, title_en, type, rarity_tag, image_url FROM items WHERE id=:id"),
                {"id": inv.shop_item_id}
            ).fetchone()
            if row:
                entry.update({
                    "title": row.title, "title_en": row.title_en,
                    "type": row.type, "rarity": row.rarity_tag,
                    "image_url": row.image_url or "",
                })
        elif itype == "equipment" and inv.shop_item_id:
            row = db.execute(
                text("SELECT title, title_en, category, type, damage, armor_class, image_url FROM equipment WHERE id=:id"),
                {"id": inv.shop_item_id}
            ).fetchone()
            if row:
                entry.update({
                    "title": row.title, "title_en": row.title_en,
                    "category": row.category, "type": row.type,
                    "damage": row.damage or "", "armor_class": row.armor_class or "",
                    "image_url": row.image_url or "",
                })
        result.append(entry)
    return result


@router.post("", response_model=InventoryItemResponse, status_code=201)
def add_item(data: InventoryItemCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.character:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    if data.item_type not in ("magic_item", "equipment", "custom"):
        raise HTTPException(status_code=400, detail="Неверный тип предмета")

    if data.item_type == "custom":
        if not data.custom_name or not data.custom_name.strip():
            raise HTTPException(status_code=400, detail="Укажите название кастомного предмета")
    else:
        if not data.shop_item_id:
            raise HTTPException(status_code=400, detail="Укажите shop_item_id")

    # Если предмет уже есть в инвентаре — увеличиваем количество
    existing = db.query(InventoryItem).filter(
        InventoryItem.character_id == user.character.id,
        InventoryItem.item_type == data.item_type,
        InventoryItem.shop_item_id == data.shop_item_id,
        InventoryItem.custom_name == (data.custom_name.strip() if data.custom_name else None),
    ).first()

    if existing:
        existing.quantity += data.quantity
        db.commit()
        db.refresh(existing)
        return existing

    item = InventoryItem(
        character_id=user.character.id,
        item_type=ItemTypeEnum(data.item_type),
        shop_item_id=data.shop_item_id,
        custom_name=data.custom_name.strip() if data.custom_name else None,
        quantity=data.quantity,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def remove_item(item_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not user.character:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    item = db.get(InventoryItem, item_id)
    if not item or item.character_id != user.character.id:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    db.delete(item)
    db.commit()
