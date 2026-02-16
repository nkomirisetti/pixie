print("DEBUG: Loading src.core package")
try:
    from . import app_manager
    print("DEBUG: Successfully imported app_manager in src.core")
except Exception as e:
    print(f"DEBUG: Failed to import app_manager in src.core: {e}")

try:
    from . import web_controller
    print("DEBUG: Successfully imported web_controller in src.core")
except Exception as e:
    print(f"DEBUG: Failed to import web_controller in src.core: {e}")
