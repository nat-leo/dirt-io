import json
import os
import sys
from pathlib import Path

import pytest

# Make backend modules importable alongside soil tests.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from area_symbol_utils import (
    flatten_area_symbols,
    load_area_symbols,
    read_area_symbol_values,
)


def test_flatten_area_symbols_returns_ordered_flat_list():
    mock_data = {
        "CA": ["CA001", "CA002"],
        "KS": ["KS010"],
    }
    assert flatten_area_symbols(mock_data) == ["CA001", "CA002", "KS010"]


def test_load_area_symbols_rejects_non_object(tmp_path):
    bad_file = tmp_path / "area-symbols.json"
    bad_file.write_text(json.dumps(["not", "an", "object"]))

    with pytest.raises(ValueError):
        load_area_symbols(bad_file)


def test_read_area_symbol_values_from_file(tmp_path):
    sample_file = tmp_path / "area-symbols.json"
    payload = {
        "WA": ["WA001"],
        "OR": ["OR014", "OR015"],
    }
    sample_file.write_text(json.dumps(payload))

    values = read_area_symbol_values(sample_file)

    assert values == ["WA001", "OR014", "OR015"]


def test_flatten_area_symbols_rejects_invalid_entry():
    with pytest.raises(ValueError):
        flatten_area_symbols({"CA": "CA001"})
