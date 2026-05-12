from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, relationship
import enum


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    character = relationship("Character", back_populates="user", uselist=False)


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    name_lower = Column(String(100), unique=True, nullable=False)  # для проверки без учёта регистра
    race = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    description = Column(Text, default="")
    userpic = Column(String(500), default="")

    # Монеты
    platinum = Column(Integer, default=0)
    gold = Column(Integer, default=0)
    electrum = Column(Integer, default=0)
    silver = Column(Integer, default=0)
    copper = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="character")
    inventory = relationship("InventoryItem", back_populates="character", cascade="all, delete-orphan")
    transfers_sent = relationship("Transfer", foreign_keys="Transfer.from_character_id", back_populates="from_character")
    transfers_received = relationship("Transfer", foreign_keys="Transfer.to_character_id", back_populates="to_character")


class ItemTypeEnum(str, enum.Enum):
    magic_item = "magic_item"
    equipment = "equipment"
    custom = "custom"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    item_type = Column(SAEnum(ItemTypeEnum), nullable=False)
    shop_item_id = Column(Integer, nullable=True)    # id из таблицы items или equipment
    custom_name = Column(String(255), nullable=True) # для кастомных вещей
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    character = relationship("Character", back_populates="inventory")


class TransferTypeEnum(str, enum.Enum):
    money = "money"
    item = "item"


class Transfer(Base):
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    to_character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    transfer_type = Column(SAEnum(TransferTypeEnum), nullable=False)

    # Для денег — сколько каждой монеты
    platinum = Column(Integer, default=0)
    gold = Column(Integer, default=0)
    electrum = Column(Integer, default=0)
    silver = Column(Integer, default=0)
    copper = Column(Integer, default=0)

    # Для предметов
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    quantity = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)

    from_character = relationship("Character", foreign_keys=[from_character_id], back_populates="transfers_sent")
    to_character = relationship("Character", foreign_keys=[to_character_id], back_populates="transfers_received")
