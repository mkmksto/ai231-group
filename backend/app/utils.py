from pathlib import Path

BACKEND_PATH = Path(__file__).parent.parent
BACKEND_DIST_PATH = BACKEND_PATH / "dist"
print(f"BACKEND_PATH: {BACKEND_PATH}")
print(f"BACKEND_DIST_PATH: {BACKEND_DIST_PATH.resolve()}")
