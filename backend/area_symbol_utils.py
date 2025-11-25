from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_AREA_SYMBOLS_PATH = Path(__file__).resolve().parent / "area-symbols.json"


def load_area_symbols(path: Path | str | None = None) -> Mapping[str, Sequence[str]]:
    """
    Load the JSON object from the area symbols file.
    """
    source_path = Path(path) if path else DEFAULT_AREA_SYMBOLS_PATH
    with source_path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError("Area symbol file must contain a JSON object")

    return data


def flatten_area_symbols(area_symbols: Mapping[str, Sequence[str]]) -> list[str]:
    """
    Convert the area symbol mapping into a flat list of values.
    """
    values: list[str] = []
    for symbol_list in area_symbols.values():
        if not isinstance(symbol_list, Sequence) or isinstance(symbol_list, (str, bytes)):
            raise ValueError("Each area symbol entry must be a sequence of strings")

        values.extend(symbol_list)

    return values


def build_sacatalog_date_query(symbols: Iterable[str]) -> str:
    """
    Construct the NRCS SQL query fetching saverest dates for the supplied area symbols.
    """
    cleaned: list[str] = []
    for sym in symbols:
        if not sym:
            continue
        stripped = sym.strip()
        if not stripped or stripped in cleaned:
            continue
        cleaned.append(stripped)
    unique_symbols = cleaned
    if not unique_symbols:
        raise ValueError("At least one symbol must be provided")

    quoted = ", ".join(f"'{sym}'" for sym in unique_symbols)
    return f"SELECT areasymbol, saverest FROM sacatalog WHERE areasymbol IN ({quoted});"


def parse_sacatalog_dates(response: Mapping[str, Any]) -> list[dict[str, str]]:
    """
    Convert the API response into a list of records with only the date portion.
    """
    table = response.get("Table")
    if not table:
        return []

    if not isinstance(table, list):
        raise ValueError("Expected 'Table' to be a list")

    results: list[dict[str, str]] = []
    for row in table:
        if not isinstance(row, list) or len(row) < 2:
            continue

        symbol, date_value = row[0], row[1]
        if not isinstance(symbol, str):
            continue

        date_str = ""
        if isinstance(date_value, str) and date_value.strip():
            date_str = date_value.strip().split(" ")[0]

        results.append({"area-symbol": symbol, "date": date_str})

    return results


def read_area_symbol_values(path: Path | str | None = None) -> list[str]:
    """
    Read the JSON file and return all values in a single list.
    """
    area_symbols = load_area_symbols(path)
    return flatten_area_symbols(area_symbols)
