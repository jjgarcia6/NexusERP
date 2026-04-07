from __future__ import annotations

from enum import Enum


def _is_all_digits(value: str, expected_length: int) -> bool:
    return len(value) == expected_length and value.isdigit()


def _validate_province_code(code: int) -> bool:
    return 1 <= code <= 24


def validate_cedula(cedula: str) -> bool:
    """
    Validate Ecuadorian personal identification (cedula).

    Rules:
    - Exactly 10 digits.
    - Province code between 01 and 24.
    - Third digit must be less than 6.
    - Check digit (position 10) follows modulo-10 algorithm.
    """
    if not _is_all_digits(cedula, 10):
        return False

    province = int(cedula[:2])
    if not _validate_province_code(province):
        return False

    third_digit = int(cedula[2])
    if third_digit >= 6:
        return False

    coefficients = (2, 1, 2, 1, 2, 1, 2, 1, 2)
    total = 0
    for index, coefficient in enumerate(coefficients):
        digit = int(cedula[index]) * coefficient
        if digit >= 10:
            digit -= 9
        total += digit

    verifier = 0 if total % 10 == 0 else 10 - (total % 10)
    return verifier == int(cedula[9])


def _validate_ruc_private_company(ruc: str) -> bool:
    coefficients = (4, 3, 2, 7, 6, 5, 4, 3, 2)
    total = sum(int(ruc[index]) * coefficient for index, coefficient in enumerate(coefficients))
    remainder = total % 11
    verifier = 0 if remainder == 0 else 11 - remainder
    if verifier == 11:
        verifier = 0
    return verifier == int(ruc[9])


def _validate_ruc_public_entity(ruc: str) -> bool:
    coefficients = (3, 2, 7, 6, 5, 4, 3, 2)
    total = sum(int(ruc[index]) * coefficient for index, coefficient in enumerate(coefficients))
    remainder = total % 11
    verifier = 0 if remainder == 0 else 11 - remainder
    if verifier == 11:
        verifier = 0
    return verifier == int(ruc[8])


def validate_ruc(ruc: str) -> bool:
    """
    Validate Ecuadorian RUC.

    Supported cases:
    - Natural person RUC: first 10 digits must be a valid cedula.
    - Private company RUC: third digit is 9 and check digit at position 10.
    - Public entity RUC: third digit is 6 and check digit at position 9.

    In all cases, establishment code (last 3 digits) must be >= 001.
    """
    if not _is_all_digits(ruc, 13):
        return False

    province = int(ruc[:2])
    if not _validate_province_code(province):
        return False

    establishment = int(ruc[10:13])
    if establishment < 1:
        return False

    third_digit = int(ruc[2])
    if third_digit < 6:
        return validate_cedula(ruc[:10])

    if third_digit == 9:
        return _validate_ruc_private_company(ruc)

    if third_digit == 6:
        return _validate_ruc_public_entity(ruc)

    return False


def validate_identification(identification: str, customer_type: object) -> bool:
    """
    Validate identification number according to customer type.

    - persona_natural -> cedula
    - juridica -> ruc
    """
    if identification is None:
        return False

    customer_type_value: str
    if isinstance(customer_type, Enum):
        customer_type_value = str(customer_type.value)
    else:
        customer_type_value = str(customer_type)

    if customer_type_value == "persona_natural":
        return validate_cedula(identification)

    if customer_type_value == "juridica":
        return validate_ruc(identification)

    return False
