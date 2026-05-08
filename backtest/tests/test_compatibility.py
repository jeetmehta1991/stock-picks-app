"""Compatibility tests - DEC-503 pyramid layer (Pass 53 v8h+1 owner-approved 2026-05-08).

Compatibility = our code works across the supported Python / pandas / pyarrow
matrix. Catches subtle breakage from upgrades (e.g. pandas 2.x -> 3.x rename
of FreqStr).

In-process: we test the runtime version we're on. Cross-version matrix is
intended to be wired into CI via tox + pytest. For now, we lock the
versions we depend on + assert key APIs we use are still present.

Markers:
    pytest -m compatibility
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


pytestmark = pytest.mark.compatibility


# -- Compat 1: Python version supported ---------------------------------
def test_compat_python_version() -> None:
    """We support Python 3.13+. Anything older is a hard fail."""
    major, minor = sys.version_info[:2]
    assert (major, minor) >= (3, 13), (
        f"Python {major}.{minor} below supported floor 3.13"
    )


# -- Compat 2: pandas APIs we use -----------------------------------------
def test_compat_pandas_apis_present() -> None:
    """We rely on these pandas APIs; assert they exist on the installed
    version. Catches accidental upgrade breakage."""
    import pandas as pd
    required = [
        "DataFrame", "Series", "concat", "read_parquet", "read_csv",
        "to_datetime", "date_range",
    ]
    missing = [a for a in required if not hasattr(pd, a)]
    assert not missing, f"pandas missing required APIs: {missing}"


# -- Compat 3: pyarrow parquet roundtrip --------------------------------
def test_compat_pyarrow_parquet_roundtrip(tmp_path: Path) -> None:
    """Write + read a small parquet via pandas/pyarrow; assert round-trip
    integrity. This is the foundation under every cache file we have."""
    import pandas as pd
    df = pd.DataFrame({
        "ticker": ["AAPL", "MSFT", "GOOGL"],
        "value": [1.0, 2.5, 3.14],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
    })
    out = tmp_path / "compat.parquet"
    df.to_parquet(out, index=False)
    df2 = pd.read_parquet(out)
    assert list(df2.columns) == list(df.columns)
    assert len(df2) == len(df)
    assert df2["ticker"].tolist() == df["ticker"].tolist()


# -- Compat 4: numpy basic ops ------------------------------------------
def test_compat_numpy_apis_present() -> None:
    import numpy as np
    required = ["array", "where", "isnan", "nan", "ndarray"]
    missing = [a for a in required if not hasattr(np, a)]
    assert not missing, f"numpy missing required APIs: {missing}"


# -- Compat 5: requests works for HEAD --------------------------------
def test_compat_requests_head_available() -> None:
    """We use requests.head() for endpoint probing; assert it exists."""
    import requests
    assert hasattr(requests, "get")
    assert hasattr(requests, "head")
    assert hasattr(requests, "post")


# -- Compat 6: parquet compression='snappy' supported -----------------
def test_compat_pyarrow_snappy_compression(tmp_path: Path) -> None:
    """Cache files are SNAPPY-compressed. Verify pyarrow on this install
    can write/read SNAPPY parquet."""
    import pandas as pd
    df = pd.DataFrame({"x": list(range(100))})
    out = tmp_path / "snap.parquet"
    df.to_parquet(out, index=False, compression="snappy")
    df2 = pd.read_parquet(out)
    assert len(df2) == 100


# -- Compat 7: pandas datetime parsing handles common AAII format -----
def test_compat_pandas_datetime_aaii_format() -> None:
    """AAII Excel returns datetimes as Excel-native; parsing as pandas
    datetime must work and produce comparable values."""
    import pandas as pd
    samples = ["2026-05-07", "1987-06-26", pd.Timestamp("2024-01-15")]
    converted = pd.to_datetime(samples, errors="coerce")
    assert not converted.isna().any()
    assert converted[0].year == 2026


# -- Compat 8: subprocess capture_output=True works (used by dashboard) -
def test_compat_subprocess_capture_output() -> None:
    """build_dashboard_stage_2.py uses subprocess.run(capture_output=True);
    assert it works and produces .stdout / .stderr fields."""
    import subprocess
    r = subprocess.run([sys.executable, "-c", "print('hi'); import sys; sys.stderr.write('err\\n')"],
                       capture_output=True, text=True, timeout=10)
    assert "hi" in r.stdout
    assert "err" in r.stderr
