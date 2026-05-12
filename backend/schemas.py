from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# --- Auth ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Пароль должен быть не менее 6 символов")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    is_superadmin: bool

    model_config = {"from_attributes": True}


# --- Character ---

class CharacterCreate(BaseModel):
    name: str
    race: str
    age: int
    description: Optional[str] = ""
    platinum: Optional[int] = 0
    gold: Optional[int] = 0
    electrum: Optional[int] = 0
    silver: Optional[int] = 0
    copper: Optional[int] = 0

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Имя не может быть пустым")
        if len(v) < 2:
            raise ValueError("Имя слишком короткое")
        return v

    @field_validator("age")
    @classmethod
    def age_positive(cls, v):
        if v <= 0:
            raise ValueError("Возраст должен быть положительным")
        return v


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    race: Optional[str] = None
    age: Optional[int] = None
    description: Optional[str] = None
    platinum: Optional[int] = None
    gold: Optional[int] = None
    electrum: Optional[int] = None
    silver: Optional[int] = None
    copper: Optional[int] = None


class CharacterResponse(BaseModel):
    id: int
    name: str
    race: str
    age: int
    description: str
    userpic: str
    platinum: int
    gold: int
    electrum: int
    silver: int
    copper: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CharacterShort(BaseModel):
    id: int
    name: str
    race: str
    userpic: str

    model_config = {"from_attributes": True}


# --- Inventory ---

class InventoryItemCreate(BaseModel):
    item_type: str  # "magic_item" | "equipment" | "custom"
    shop_item_id: Optional[int] = None
    custom_name: Optional[str] = None
    quantity: int = 1


class InventoryItemResponse(BaseModel):
    id: int
    item_type: str
    shop_item_id: Optional[int]
    custom_name: Optional[str]
    quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Transfer ---

class MoneyTransfer(BaseModel):
    to_character_id: int
    platinum: int = 0
    gold: int = 0
    electrum: int = 0
    silver: int = 0
    copper: int = 0

    @field_validator("platinum", "gold", "electrum", "silver", "copper")
    @classmethod
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("Количество монет не может быть отрицательным")
        return v


class ItemTransfer(BaseModel):
    to_character_id: int
    inventory_item_id: int
    quantity: int = 1


# --- Admin ---

class AdminUserResponse(BaseModel):
    id: int
    email: str
    is_superadmin: bool
    character: Optional[CharacterResponse]

    model_config = {"from_attributes": True}
