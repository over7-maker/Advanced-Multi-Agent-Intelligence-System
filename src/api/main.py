\"\"\"Test-facing API entrypoint.

This module exposes the main FastAPI ``app`` instance so that tests which
import ``src.api.main`` get the real AMAS application rather than a mock.
\"\"\"

from src.amas.api.main import app  # noqa: F401


