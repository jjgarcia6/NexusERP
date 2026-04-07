import pytest
import sys
from pathlib import Path

# Añadir el directorio actual a sys.path para importación directa
sys.path.append(str(Path(__file__).parent))
from identification import validate_cedula

# Cédulas válidas (deben ser True)
VALID_CEDULAS = [
    "1710034065",  # Quito
    "1104680136",  # Loja
    "0106415392",  # Azuay
    "1004443885",  # Ejemplo válido
    "0931811364",  # Ejemplo válido
]

# Cédulas inválidas (deben ser False)
INVALID_CEDULAS = [
    "1710034064",  # Dígito verificador incorrecto
    "0926687850",  # Dígito verificador incorrecto
    "0000000000",  # Provincia inválida
]

def test_validate_cedula_valid():
    for cedula in VALID_CEDULAS:
        assert validate_cedula(cedula), f"Cédula válida falló: {cedula}"

def test_validate_cedula_invalid():
    for cedula in INVALID_CEDULAS:
        assert not validate_cedula(cedula), f"Cédula inválida pasó: {cedula}"
