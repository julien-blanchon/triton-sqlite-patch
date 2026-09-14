import os
import subprocess
import sys
from unittest import mock

import pytest

from triton_sqlite_patch import check_compatibility


@pytest.mark.parametrize("backend", [None, "file", "sqlite"])
def test_automatic_startup(tmp_path, backend):
    script = """
import os
from pathlib import Path
from triton.runtime.cache import get_cache_manager
m = get_cache_manager('ab')
assert Path(m.put(b'payload', 'x.bin')).read_bytes() == b'payload'
assert (Path(os.environ['TRITON_CACHE_DIR']) / 'cache-v1.sqlite3').exists() == (os.environ['TRITON_CACHE_BACKEND'] == 'sqlite')
"""
    env = dict(os.environ, TRITON_CACHE_BACKEND=backend, TRITON_CACHE_DIR=str(tmp_path))
    if backend is None:
        env.pop("TRITON_CACHE_BACKEND", None)
    env.pop("TRITON_CACHE_MANAGER", None)
    subprocess.run([sys.executable, "-c", script], env=env, check=True, timeout=60)


def test_unsupported_version_rejected():
    with mock.patch("importlib.metadata.version", return_value="3.7.0"):
        with pytest.raises(RuntimeError, match="supports Triton 3.8.0"):
            check_compatibility()


def test_manager_conflict_rejected():
    env = dict(os.environ, TRITON_CACHE_BACKEND="sqlite", TRITON_CACHE_MANAGER="custom:Manager")
    result = subprocess.run([sys.executable, "-c", "import triton"], env=env, capture_output=True, text=True, timeout=60)
    assert result.returncode != 0
    assert "already configured" in result.stderr
