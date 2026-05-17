import json
import os
from config.settings import TESTDATA_DIR


def load_json(filename: str) -> list | dict:
    filepath = os.path.join(TESTDATA_DIR, filename)
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def extract_items(response_data) -> list:
    """Достаёт список items из ответа — поддерживает и список, и пагинированный объект."""
    if isinstance(response_data, list):
        return response_data
    return response_data.get("items", [])


def filter_by_field(records: list, field: str, value) -> list:
    return [r for r in records if r.get(field) == value]


def get_field_values(records: list, field: str) -> list:
    return [r[field] for r in records if field in r]


def find_by_id(records: list, record_id: int) -> dict | None:
    for record in records:
        if record.get("id") == record_id:
            return record
    return None
