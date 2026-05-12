import json
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Item, Equipment

DB_URL = "postgresql://dnd_user:dnd_password@localhost:5432/dnd_shop"


def seed():
    json_path = Path(__file__).parent.parent / "scraper" / "items.json"
    if not json_path.exists():
        print(f"Файл не найден: {json_path}")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        items_data = json.load(f)

    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.query(Item).count()
        if existing > 0:
            print(f"В базе уже есть {existing} предметов. Пропускаю.")
            return

        items = [
            Item(
                title=item["title"],
                title_en=item.get("title_en", ""),
                link=item.get("link", ""),
                type=item.get("type", ""),
                rarity=item.get("rarity", ""),
                rarity_tag=item.get("rarity_tag", ""),
                icon=item.get("icon", ""),
                description=item.get("description", ""),
                params=json.dumps(item.get("params", []), ensure_ascii=False),
                image_url=item.get("image_url", ""),
            )
            for item in items_data
        ]

        session.add_all(items)
        session.commit()
        print(f"Загружено {len(items)} предметов в базу данных.")


def seed_equipment():
    json_path = Path(__file__).parent.parent / "scraper" / "equipment.json"
    if not json_path.exists():
        print(f"Файл не найден: {json_path}")
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.query(Equipment).count()
        if existing > 0:
            print(f"В базе уже есть {existing} предметов снаряжения. Пропускаю.")
            return

        records = [
            Equipment(
                id=int(item["id"]),
                title=item["title"],
                title_en=item.get("title_en", ""),
                link=item.get("link", ""),
                category=item.get("category", ""),
                filter_tags=json.dumps(item.get("filter_tags", {}), ensure_ascii=False),
                type=item.get("type", ""),
                price=item.get("price", ""),
                weight=item.get("weight", ""),
                damage=item.get("damage", ""),
                armor_class=item.get("armor_class", ""),
                tool_stat=json.dumps(item.get("tool_stat", []), ensure_ascii=False),
                properties=json.dumps(item.get("properties", []), ensure_ascii=False),
                description=item.get("description", ""),
                image_url=item.get("image_url", ""),
            )
            for item in data
        ]

        session.add_all(records)
        session.commit()
        print(f"Загружено {len(records)} предметов снаряжения в базу данных.")


if __name__ == "__main__":
    seed()
    seed_equipment()
