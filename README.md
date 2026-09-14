# Triton SQLite cache patch

An automatically enabled local compiler cache with SQLite persistence, using
Triton's existing `TRITON_CACHE_MANAGER` hook. Install and run normally; no
launcher or application edits are needed. No installed Triton sources are modified.
Currently tested and supported: **Triton 3.8.0**, Python 3.10 or newer. Other
versions are rejected, including development releases, until validated.

```sh
pip install git+https://github.com/julien-blanchon/triton-sqlite-patch.git
export TRITON_CACHE_DIR=/path/to/local/cache/triton
export TMPDIR=/path/to/local/runtime
python train.py
```

A wheel-installed `.pth` hook defaults `TRITON_CACHE_BACKEND` to `sqlite` and
registers the cache manager when Triton is first imported. Fresh Python workers
activate automatically too. Set `TRITON_CACHE_BACKEND=file` before starting Python
to opt out. An existing custom manager is rejected rather than replaced. The
proposed upstream backend instead defaults to files and requires explicit opt-in.
This package does not install or upgrade Triton for you.

Normal Python `site` initialization is required (`python -S` disables startup
hooks). Restart notebook kernels after installation. Use a regular `pip install .`
for development; editable-install startup hooks are not supported.

Artifacts live in `TRITON_CACHE_DIR/cache-v1.sqlite3`. The default cache directory
still follows `TRITON_HOME`. Text uses UTF-8; binary payloads remain bytes. Group
metadata stores names rather than ephemeral paths and is published only when
all members exist. Database errors are reported, with no automatic file fallback.

Triton's current API requires actual paths. Files are materialized below Python's
temporary directory (`TMPDIR` on Unix) and kept until normal process exit. Runtime
inode use scales with artifacts touched by a live process; it is **not bounded**.
Abnormal termination can leave `triton-sqlite-*` directories: remove only those
whose processes have stopped. Put the runtime directory on storage with sufficient
temporary inodes, outside the quota-limited persistent cache. Do not remove live
materializations: loaded modules, profiling hooks, and debuggers can still need them.

Use local storage for both the database and runtime files. A database shared
across hosts over NFS, Lustre, or similar filesystems is unsupported. The backend
uses SQLite's rollback journal, transactions, and a 30-second busy timeout, with
connections closed after each operation. There is no eviction, TTL, size cap,
remote synchronization, or migration of old file entries. `TRITON_STORE_BINARY_ONLY`
still applies. Dump and override directories retain their file behavior.

To clear the database, stop all users and delete `cache-v1.sqlite3` and any
associated journal files in the configured directory. Old filesystem cache
entries can be removed separately after stopping their users.

To disable, set `TRITON_CACHE_BACKEND=file` and restart Python. Remove with
`pip uninstall triton-sqlite-patch` and restart Python. Once upstream supports
this backend, uninstall the package, remove any explicitly configured custom
manager variable, and set `TRITON_CACHE_BACKEND=sqlite` for upstream.

## Development

```sh
pip install '.[test]'
pytest -s --tb=short tests
```

`backend.py` follows the proposed upstream `triton/runtime/sqlite_cache.py`, with
only its imports and compatibility check adapted. Keep the two synchronized.
Upstream implementation: [feat-sqlite-cache](https://github.com/julien-blanchon/triton/tree/feat-sqlite-cache),
commit `31a579484`.

## Storage microbenchmark

Run `python benchmarks/cache.py --entries 2000 --directory /path/to/local/storage`.
For 2,000 synthetic kernels (10,000 logical records including groups), one local
run measured:

| Backend | Persistent objects | Write seconds | Restart-read seconds | Peak temporary objects |
| --- | ---: | ---: | ---: | ---: |
| File | 12,000 | 0.75 | 0.20 | 0 |
| SQLite | 1 | 6.44 | 1.29 | 16,003 |

Temporary objects returned to zero after normal process exit. Counts exclude the
benchmark's containing directories. Timings exclude imports and GPU compilation;
these are storage-only measurements, not an end-to-end performance claim. SQLite
transaction durability and materialization have measurable costs. Re-run on the
intended local filesystem.
