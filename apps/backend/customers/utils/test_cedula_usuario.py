import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from identification import validate_cedula

def test_cedula_usuario():
    cedula = "0920275229"
    assert validate_cedula(cedula), f"La cédula {cedula} no pasó la validación"
