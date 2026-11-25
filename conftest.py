"""Make the standalone FastAPI backend importable by all tests."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
