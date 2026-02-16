print("DEBUG: Loading src package")
try:
    from . import core
    print("DEBUG: Imported src.core")
except Exception as e:
    print(f"DEBUG: Failed to import src.core: {e}")

try:
    from . import apps
    print("DEBUG: Imported src.apps")
except Exception as e:
    print(f"DEBUG: Failed to import src.apps: {e}")
