from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping, Sequence


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


def read_area_symbol_values(path: Path | str | None = None) -> list[str]:
    """
    Read the JSON file and return all values in a single list.
    """
    area_symbols = load_area_symbols(path)
    return flatten_area_symbols(area_symbols)
