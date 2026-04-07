from __future__ import annotations


def mask_identification(identification: str) -> str:
    if len(identification) <= 4:
        return "****"

    return f"***{identification[-4:]}"
