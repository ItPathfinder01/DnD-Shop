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
