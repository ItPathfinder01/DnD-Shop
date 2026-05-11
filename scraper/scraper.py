import json
import time
import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://next.dnd.su"
LIST_URL = f"{BASE_URL}/items/"
OUTPUT_FILE = "items.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def fetch_items_list():
    """Получаем список всех предметов со страницы /items/"""
    print("Загружаю список предметов...")
    response = requests.get(LIST_URL, headers=HEADERS)
    response.raise_for_status()

    content = response.text
    idx = content.find("LIST =")
    if idx == -1:
        raise RuntimeError("Не нашёл LIST в HTML — сайт мог поменяться")

    chunk = content[idx + 7:]
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

    data = json.loads(chunk[:end])
    cards = data["cards"]
    print(f"Найдено предметов: {len(cards)}")
    return cards


def fetch_item_detail(relative_link):
    """Получаем описание и картинку с детальной страницы предмета"""
    url = BASE_URL + relative_link
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Описание
    description = ""
    desc_block = soup.find("li", class_=lambda x: x and "desc" in x)
    if desc_block:
        description = desc_block.get_text(separator=" ", strip=True)

    # Параметры (тип, стоимость и т.д.)
    params = []
    params_list = soup.find("ul", class_="params")
    if params_list:
        for li in params_list.find_all("li"):
            text = li.get_text(strip=True)
            if text and "desc" not in li.get("class", []):
                params.append(text)

    # Картинка
    image_url = ""
    img = soup.find("img", src=re.compile(r"/storage/"))
    if img:
        image_url = BASE_URL + img["src"]

    return {
        "description": description,
        "params": params,
        "image_url": image_url,
    }


def scrape_all(limit=None, delay=0.3):
    """
    Основная функция: собирает все предметы.
    limit - сколько предметов обработать (None = все)
    delay - пауза между запросами в секундах
    """
    cards = fetch_items_list()

    if limit:
        cards = cards[:limit]

    items = []

    for i, card in enumerate(cards):
        title = card.get("title", "")
        print(f"[{i + 1}/{len(cards)}] {title}")

        item = {
            "title": title,
            "title_en": card.get("title_en", ""),
            "link": BASE_URL + card.get("link", ""),
            "type": card.get("type_order", ""),
            "rarity": card.get("rarity_order", ""),
            "rarity_tag": card.get("item_tags", {}).get("rarity", {}).get("tag_title", ""),
            "icon": card.get("item_icon_title", ""),
        }

        # Загружаем детальную страницу
        try:
            detail = fetch_item_detail(card["link"])
            item.update(detail)
        except Exception as e:
            print(f"  Ошибка при загрузке {card['link']}: {e}")
            item.update({"description": "", "params": [], "image_url": ""})

        items.append(item)
        time.sleep(delay)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Сохранено {len(items)} предметов в {OUTPUT_FILE}")
    return items


if __name__ == "__main__":
    # Для первого запуска берём только 10 предметов, чтобы проверить
    # Когда убедишься что всё работает — убери limit=10
    scrape_all(limit=10)
