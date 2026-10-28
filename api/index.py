import sys
import os
from pathlib import Path

# Add the backend directory to sys.path so 'app' and its submodules are discoverable
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["VERCEL"] = "1"

from app.main import app

