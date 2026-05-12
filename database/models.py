from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255))
    link = Column(String(500))
    type = Column(String(100))
    rarity = Column(String(100))
    rarity_tag = Column(String(50))
    icon = Column(String(100))
    description = Column(Text)
    params = Column(Text)
    image_url = Column(String(500))


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255))
    link = Column(String(500))
    category = Column(String(100))
    filter_tags = Column(Text)   # JSON
    type = Column(String(255))
    price = Column(String(100))
    weight = Column(String(100))
    damage = Column(String(100))
    armor_class = Column(String(100))
    tool_stat = Column(Text)     # JSON array
    properties = Column(Text)    # JSON array
    description = Column(Text)
    image_url = Column(String(500))
