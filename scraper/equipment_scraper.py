import json
import time
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://next.dnd.su"
LIST_URL = f"{BASE_URL}/equipment/"
OUTPUT_FILE = "equipment.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_equipment_list():
    print("Загружаю список снаряжения...")
    response = requests.get(LIST_URL, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    content = response.text

    # Парсим filterItems — теги фильтрации для каждого предмета
    filter_items = {}
    idx = content.find("window.filterItems = ")
    if idx != -1:
        chunk = content[idx + len("window.filterItems = "):]
        depth = 0
        end = 0
        for i, ch in enumerate(chunk):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        filter_items = json.loads(chunk[:end])

    cards = []
    for div in soup.find_all("div", class_="list-item__spell"):
        item_id = div.get("data-id", "")
        data_search = div.get("data-search", "")
        category = div.get("data-letter", "")

        # data-search = "Название RU,Name EN,"
        parts = [p.strip() for p in data_search.split(",") if p.strip()]
        title = parts[0] if len(parts) > 0 else ""
        title_en = parts[1] if len(parts) > 1 else ""

        a = div.find("a")
        link = a["href"] if a else ""

        cards.append({
            "id": item_id,
            "title": title,
            "title_en": title_en,
            "link": link,
            "category": category,
            "filter_tags": filter_items.get(item_id, {}),
        })

    print(f"Найдено снаряжения: {len(cards)}")
    return cards


def fetch_equipment_detail(relative_link):
    url = BASE_URL + relative_link
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    result = {
        "type": "",
        "price": "",
        "weight": "",
        "damage": "",
        "armor_class": "",
        "tool_stat": [],
        "properties": [],
        "description": "",
        "image_url": "",
    }

    params_list = soup.find("ul", class_="params")
    if params_list:
        for li in params_list.find_all("li", recursive=False):
            classes = li.get("class", [])

            if "size-type-alignment" in classes:
                result["type"] = li.get_text(strip=True)

            elif "price" in classes:
                text = li.get_text(strip=True)
                result["price"] = text.replace("Стоимость:", "").strip()

            elif "weight" in classes:
                text = li.get_text(strip=True)
                result["weight"] = text.replace("Вес:", "").strip()

            elif "weapons" in classes:
                result["damage"] = li.get_text(strip=True).replace("Урон:", "").strip()

            elif "armors" in classes:
                result["armor_class"] = li.get_text(strip=True).replace("Класс защиты:", "").strip()

            elif "tools" in classes:
                result["tool_stat"].append(li.get_text(strip=True))

            elif "desc" in classes:
                result["description"] = li.get_text(separator=" ", strip=True)

            elif not classes or classes == ["card-img__block"]:
                text = li.get_text(separator=" ", strip=True)
                if text:
                    result["properties"].append(text)

    img = soup.find("img", src=re.compile(r"/storage/"))
    if img and "default.png" not in img["src"]:
        result["image_url"] = BASE_URL + img["src"]

    return result


def scrape_all(limit=None, delay=0.3):
    cards = fetch_equipment_list()

    if limit:
        cards = cards[:limit]

    items = []
    for i, card in enumerate(cards):
        print(f"[{i + 1}/{len(cards)}] {card['title']}")

        item = {
            "id": card["id"],
            "title": card["title"],
            "title_en": card["title_en"],
            "link": BASE_URL + card["link"],
            "category": card["category"],
            "filter_tags": card["filter_tags"],
        }

        try:
            detail = fetch_equipment_detail(card["link"])
            item.update(detail)
        except Exception as e:
            print(f"  Ошибка при загрузке {card['link']}: {e}")
            item.update({
                "type": "", "price": "", "weight": "",
                "damage": "", "armor_class": "", "tool_stat": [],
                "properties": [], "description": "", "image_url": "",
            })

        items.append(item)
        time.sleep(delay)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Сохранено {len(items)} предметов в {OUTPUT_FILE}")
    return items


if __name__ == "__main__":
    scrape_all()
