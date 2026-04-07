from __future__ import annotations

from reports.utils.masking import mask_identification


def test_should_mask_identification_keeping_last_four_digits() -> None:
    assert mask_identification("0912345678") == "***5678"


def test_should_return_four_asterisks_when_identification_is_too_short() -> None:
    assert mask_identification("1234") == "****"
