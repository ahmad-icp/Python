"""Compatibility package that prevents duplicate ``app`` model imports.

The backend source package is named ``app``. Importing the same files through the
repository path as ``backend.app`` creates a second module graph while the model
files still import ``app.db.base``. SQLAlchemy then sees the same declarative
classes/tables registered twice. Alias ``backend.app`` to the canonical ``app``
package so both import styles resolve to one module identity and one Base.
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import app as _app

sys.modules.setdefault(__name__ + ".app", _app)
app = _app
