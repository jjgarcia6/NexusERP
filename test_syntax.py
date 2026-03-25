import ast
import sys

try:
    with open(r'apps\backend\purchases\routers\suppliers_router.py', 'r') as f:
        code = f.read()
    ast.parse(code)
    print("✓ suppliers_router.py has valid Python syntax")
except SyntaxError as e:
    print(f"✗ SyntaxError: {e}")
    sys.exit(1)
