import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from PIL import Image

from database import get_db
from dependencies import get_current_user
from models import User, Character
from schemas import CharacterCreate, CharacterUpdate, CharacterResponse, CharacterShort, MoneyTransfer, ItemTransfer, CoinExchange
from models import Transfer, TransferTypeEnum, InventoryItem

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
HINT_FORMATS = "JPG, JPEG, PNG, GIF, WEBP"

router = APIRouter(prefix="/characters", tags=["characters"])


def _check_name_unique(db: Session, name: str, exclude_id: int = None):
    name_lower = name.strip().lower()
    q = db.query(Character).filter(Character.name_lower == name_lower)
    if exclude_id:
        q = q.filter(Character.id != exclude_id)
    if q.first():
        raise HTTPException(status_code=400, detail="Персонаж с таким именем уже существует")


@router.post("", response_model=CharacterResponse, status_code=201)
def create_character(data: CharacterCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.character:
        raise HTTPException(status_code=400, detail="У вас уже есть персонаж")

    _check_name_unique(db, data.name)

    character = Character(
        user_id=user.id,
        name=data.name.strip(),
        name_lower=data.name.strip().lower(),
        race=data.race,
        age=data.age,
        description=data.description or "",
        platinum=data.platinum or 0,
        gold=data.gold or 0,
        electrum=data.electrum or 0,
        silver=data.silver or 0,
        copper=data.copper or 0,
    )
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.get("/me", response_model=CharacterResponse)
def get_my_character(user: User = Depends(get_current_user)):
    if not user.character:
        raise HTTPException(status_code=404, detail="Персонаж не создан")
    return user.character


@router.put("/me", response_model=CharacterResponse)
def update_character(data: CharacterUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    if data.name is not None:
        _check_name_unique(db, data.name, exclude_id=char.id)
        char.name = data.name.strip()
        char.name_lower = data.name.strip().lower()

    for field in ("race", "age", "description", "platinum", "gold", "electrum", "silver", "copper"):
        val = getattr(data, field)
        if val is not None:
            setattr(char, field, val)

    db.commit()
    db.refresh(char)
    return char


@router.post("/me/userpic", response_model=CharacterResponse)
def upload_userpic(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Формат не поддерживается. Допустимые форматы: {HINT_FORMATS}")

    # Проверяем что это реально картинка
    try:
        img = Image.open(file.file)
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Файл повреждён или не является изображением")

    file.file.seek(0)
    filename = f"{uuid.uuid4()}{ext}"
    save_path = os.path.join(UPLOADS_DIR, filename)
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(file.file.read())

    # Удаляем старый файл
    if char.userpic:
        old_path = os.path.join(UPLOADS_DIR, os.path.basename(char.userpic))
        if os.path.exists(old_path):
            os.remove(old_path)

    char.userpic = f"/uploads/{filename}"
    db.commit()
    db.refresh(char)
    return char


@router.get("", response_model=List[CharacterShort])
def list_characters(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Character).filter(Character.id != (user.character.id if user.character else -1)).all()


@router.post("/me/transfer/money", status_code=200)
def transfer_money(data: MoneyTransfer, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    to_char = db.get(Character, data.to_character_id)
    if not to_char:
        raise HTTPException(status_code=404, detail="Получатель не найден")
    if to_char.id == char.id:
        raise HTTPException(status_code=400, detail="Нельзя передать деньги самому себе")

    total = data.platinum + data.gold + data.electrum + data.silver + data.copper
    if total == 0:
        raise HTTPException(status_code=400, detail="Укажите количество монет для передачи")

    # Проверяем что у отправителя достаточно монет
    for coin in ("platinum", "gold", "electrum", "silver", "copper"):
        amount = getattr(data, coin)
        if getattr(char, coin) < amount:
            raise HTTPException(status_code=400, detail=f"Недостаточно монет: {coin}")
        setattr(char, coin, getattr(char, coin) - amount)
        setattr(to_char, coin, getattr(to_char, coin) + amount)

    transfer = Transfer(
        from_character_id=char.id,
        to_character_id=to_char.id,
        transfer_type=TransferTypeEnum.money,
        platinum=data.platinum,
        gold=data.gold,
        electrum=data.electrum,
        silver=data.silver,
        copper=data.copper,
    )
    db.add(transfer)
    db.commit()
    return {"detail": "Монеты переданы"}


@router.post("/me/transfer/item", status_code=200)
def transfer_item(data: ItemTransfer, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")

    to_char = db.get(Character, data.to_character_id)
    if not to_char:
        raise HTTPException(status_code=404, detail="Получатель не найден")

    inv_item = db.get(InventoryItem, data.inventory_item_id)
    if not inv_item or inv_item.character_id != char.id:
        raise HTTPException(status_code=404, detail="Предмет не найден в инвентаре")
    if inv_item.quantity < data.quantity:
        raise HTTPException(status_code=400, detail="Недостаточно предметов")

    inv_item.quantity -= data.quantity
    if inv_item.quantity == 0:
        db.delete(inv_item)

    # Добавляем предмет получателю
    existing = db.query(InventoryItem).filter(
        InventoryItem.character_id == to_char.id,
        InventoryItem.item_type == inv_item.item_type,
        InventoryItem.shop_item_id == inv_item.shop_item_id,
        InventoryItem.custom_name == inv_item.custom_name,
    ).first()

    if existing:
        existing.quantity += data.quantity
    else:
        db.add(InventoryItem(
            character_id=to_char.id,
            item_type=inv_item.item_type,
            shop_item_id=inv_item.shop_item_id,
            custom_name=inv_item.custom_name,
            quantity=data.quantity,
        ))

    transfer = Transfer(
        from_character_id=char.id,
        to_character_id=to_char.id,
        transfer_type=TransferTypeEnum.item,
        inventory_item_id=inv_item.id if inv_item in db else None,
        quantity=data.quantity,
    )
    db.add(transfer)
    db.commit()
    return {"detail": "Предмет передан"}


COIN_RATES = {"platinum": 1000, "gold": 100, "electrum": 50, "silver": 10, "copper": 1}


@router.post("/me/exchange", response_model=CharacterResponse)
def exchange_coins(data: CoinExchange, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    char = user.character
    if not char:
        raise HTTPException(status_code=404, detail="Персонаж не создан")
    if data.from_coin not in COIN_RATES or data.to_coin not in COIN_RATES:
        raise HTTPException(status_code=400, detail="Неверный тип монеты")
    if data.from_coin == data.to_coin:
        raise HTTPException(status_code=400, detail="Нельзя обменять монету на саму себя")
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Количество должно быть положительным")

    available = getattr(char, data.from_coin)
    if available < data.amount:
        raise HTTPException(status_code=400, detail=f"Недостаточно монет. Доступно: {available}")

    copper_value = data.amount * COIN_RATES[data.from_coin]
    to_rate = COIN_RATES[data.to_coin]
    if copper_value % to_rate != 0:
        raise HTTPException(status_code=400, detail="Обмен невозможен без потери монет")

    to_amount = copper_value // to_rate
    setattr(char, data.from_coin, available - data.amount)
    setattr(char, data.to_coin, getattr(char, data.to_coin) + to_amount)
    db.commit()
    db.refresh(char)
    return char
