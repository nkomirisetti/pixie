print("DEBUG: Loading src.apps package")
try:
    from . import clock_app
    from . import weather_app
    print("DEBUG: Successfully imported apps")
except Exception as e:
    print(f"DEBUG: Failed to import apps: {e}")
