"""Automatic SQLite persistence through Triton's cache-manager extension hook."""

import os


def check_compatibility():
    from importlib.metadata import version
    from packaging.version import Version

    installed = Version(version("triton"))
    if installed.base_version != "3.8.0" or installed.is_prerelease or installed.is_devrelease:
        raise RuntimeError(f"triton-sqlite-patch supports Triton 3.8.0; installed: {installed}")


def _bootstrap():
    if os.environ.setdefault("TRITON_CACHE_BACKEND", "sqlite") != "file":
        from ._hook import install

        install()
    elif os.environ.get("TRITON_CACHE_MANAGER") == "triton_sqlite_patch.backend:SQLiteCacheManager":
        os.environ.pop("TRITON_CACHE_MANAGER")
