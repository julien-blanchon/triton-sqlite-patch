# Triton SQLite patch

## Problem

Triton's file cache stores multiple artifacts per compiled kernel, including
intermediate representations, binaries, and metadata. Specializations multiply
these files and directories, potentially exhausting inode quotas on shared
cluster filesystems such as GPFS or Lustre even when disk space remains.

## Solution

This temporary patch registers a SQLite backend through Triton's cache-manager
hook. Artifacts and group metadata share one persistent database; artifacts are
materialized into temporary files when callers need paths.

Supports **Triton 3.8.0**. Installation enables SQLite automatically in new Python
processes, without changing your training script or installed source files.

## Usage

Install into the environment containing Triton:

```sh
pip install git+https://github.com/julien-blanchon/triton-sqlite-patch.git
```

Choose writable node-local directories, then run normally:

```sh
export TRITON_CACHE_DIR=/path/to/local/cache/triton
export TMPDIR=/path/to/local/runtime  # Must already exist.
python train.py
```

The database is `triton-cache-v1.sqlite3` inside the configured cache directory.
Without `TRITON_CACHE_DIR`, the existing default location is used; ensure it is
local. Existing file-cache entries are not migrated. If you already configure
`TRITON_CACHE_MANAGER`, disable this patch or remove that setting before use.

- **Disable:** set `TRITON_CACHE_BACKEND=file` before starting Python.
- **Remove:** `pip uninstall triton-sqlite-patch`, then restart Python.

Shared writable SQLite databases and fully read-only compiler caches are
unsupported. For multi-node reuse, stage a consistent snapshot into each node's
writable local cache. Live temporary inode use is not bounded.
See [storage, snapshot, and cleanup details](https://github.com/julien-blanchon/triton/blob/feat-sqlite-cache/docs/getting-started/cache.rst).
