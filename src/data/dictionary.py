from __future__ import annotations

from src.data.schema import COLUMN_DEFINITIONS


def get_dictionary_rows() -> list[dict[str, str | bool]]:
    return [
        {
            "name": column.name,
            "dtype": column.dtype,
            "description": column.description,
            "nullable": column.nullable,
        }
        for column in COLUMN_DEFINITIONS
    ]
