from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from customers.utils.identification import validate_cedula, validate_ruc


def _build_valid_cedula() -> str:
    coefficients = (2, 1, 2, 1, 2, 1, 2, 1, 2)
    province = f"{random.randint(1, 24):02d}"
    third_digit = str(random.randint(0, 5))
    body = province + third_digit + "123456"

    total = 0
    for index, coefficient in enumerate(coefficients):
        value = int(body[index]) * coefficient
        if value >= 10:
            value -= 9
        total += value

    verifier = 0 if total % 10 == 0 else 10 - (total % 10)
    return body + str(verifier)


def _build_valid_ruc_private_company() -> str:
    coefficients = (4, 3, 2, 7, 6, 5, 4, 3, 2)
    province = f"{random.randint(1, 24):02d}"
    third_digit = "9"
    body = province + third_digit + "123456"

    total = sum(int(body[index]) * coefficient for index, coefficient in enumerate(coefficients))
    remainder = total % 11
    verifier = 0 if remainder == 0 else 11 - remainder
    if verifier == 11:
        verifier = 0

    return body + str(verifier) + "001"


def test_should_validate_correct_cedula() -> None:
    valid_cedulas = [_build_valid_cedula() for _ in range(5)]

    assert all(validate_cedula(cedula) for cedula in valid_cedulas)


def test_should_reject_cedula_with_invalid_verifier_digit() -> None:
    valid = _build_valid_cedula()
    invalid = valid[:-1] + str((int(valid[-1]) + 1) % 10)

    assert validate_cedula(invalid) is False


def test_should_reject_cedula_with_invalid_province_code() -> None:
    invalid = "2512345678"

    assert validate_cedula(invalid) is False


def test_should_validate_correct_ruc_persona_natural() -> None:
    valid_ruc = _build_valid_cedula() + "001"

    assert validate_ruc(valid_ruc) is True


def test_should_validate_correct_ruc_sociedad_privada() -> None:
    valid_ruc = _build_valid_ruc_private_company()

    assert validate_ruc(valid_ruc) is True


def test_should_reject_ruc_with_invalid_length() -> None:
    assert validate_ruc("1790012345") is False
