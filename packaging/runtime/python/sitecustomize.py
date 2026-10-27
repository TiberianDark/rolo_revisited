"""Restore normal sibling script imports for the isolated embedded runtime."""
import sys
from pathlib import Path

if sys.argv and sys.argv[0] and not sys.argv[0].startswith("-"):
    sys.path.insert(0, str(Path(sys.argv[0]).resolve().parent))
