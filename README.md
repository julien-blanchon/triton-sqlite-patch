# Triton SQLite patch

Install: `pip install git+https://github.com/julien-blanchon/triton-sqlite-patch.git`
Run Python normally; SQLite activates automatically. Supports Triton 3.8.0.
Set `TRITON_CACHE_BACKEND=file` before starting Python to disable it.
Cache location follows `TRITON_CACHE_DIR`; existing file caches are not migrated.
Use writable node-local cache storage and `TMPDIR`; live temporary inode use is not bounded.
Shared writable databases and full read-only compiler caches are unsupported.
Remove with `pip uninstall triton-sqlite-patch` and restart Python.
[Storage details and limitations](https://github.com/julien-blanchon/triton/blob/feat-sqlite-cache/docs/getting-started/cache.rst).
