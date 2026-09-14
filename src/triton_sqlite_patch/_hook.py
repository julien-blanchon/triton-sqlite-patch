import importlib.abc
import os
import sys

from . import check_compatibility


class RegistrationFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != "triton":
            return None
        backend = os.environ.get("TRITON_CACHE_BACKEND", "file")
        if backend == "file":
            return None
        if backend != "sqlite":
            raise ImportError(f"Unknown TRITON_CACHE_BACKEND: {backend!r}")
        check_compatibility()
        manager = "triton_sqlite_patch.backend:SQLiteCacheManager"
        current = os.environ.get("TRITON_CACHE_MANAGER")
        if current not in (None, manager):
            raise ImportError(f"TRITON_CACHE_MANAGER is already configured: {current}")
        os.environ["TRITON_CACHE_MANAGER"] = manager
        return None


def install():
    if not any(isinstance(finder, RegistrationFinder) for finder in sys.meta_path):
        sys.meta_path.insert(0, RegistrationFinder())
