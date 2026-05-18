import json  # standard library module for reading and parsing JSON files
import os  # standard library module for building file paths
from config.settings import TESTDATA_DIR  # import the path to the testdata folder from central config


def load_json(filename: str) -> list | dict:
    # Build the full path by joining the testdata directory with the given filename
    filepath = os.path.join(TESTDATA_DIR, filename)
    # Open the file with UTF-8 encoding to correctly handle special characters
    with open(filepath, encoding="utf-8") as f:
        # Parse the file content from JSON text into a Python list or dict and return it
        return json.load(f)


def extract_items(response_data) -> list:
    # Some API endpoints return a plain list: [item1, item2, ...]
    # Others return a paginated object: {"items": [...], "total": 100, "page": 1}
    # This function handles both cases so tests don't need to care about the format.

    if isinstance(response_data, list):  # if the response is already a list, return it as-is
        return response_data
    return response_data.get("items", [])  # otherwise extract the "items" key; return empty list if missing


def filter_by_field(records: list, field: str, value) -> list:
    # Iterate over every record in the list and keep only those where record[field] == value.
    # r.get(field) is used instead of r[field] to avoid a KeyError if the field is missing.
    return [r for r in records if r.get(field) == value]


def get_field_values(records: list, field: str) -> list:
    # Collect the value of a single field from every record that contains it.
    # Records that don't have the field are silently skipped (if field in r).
    return [r[field] for r in records if field in r]


def find_by_id(records: list, record_id: int) -> dict | None:
    for record in records:  # loop through every record one by one
        if record.get("id") == record_id:  # compare the record's "id" field to the target id
            return record  # return the first matching record immediately
    return None  # if the loop finishes without a match, return None
