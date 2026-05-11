import json
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Item

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


if __name__ == "__main__":
    seed()
