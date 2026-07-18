import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).parent.resolve()
if str(AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(AGENTS_DIR))
