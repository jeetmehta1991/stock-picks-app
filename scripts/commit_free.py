"""Free COMMIT, read in-process - the runbook Step 2.5 method (§4.9; S6-B3091).

Runbook Step 2.5 (formerly STEP 3.4): "Read commit availability via GlobalMemoryStatusEx, not
PowerShell counters. Under commit exhaustion PowerShell cannot start, so a
monitor built on it goes blind exactly when it matters. Report FREE COMMIT,
never physical RAM (L670)."

The runbook named the method and nothing implemented it, so every monitor fell
back to resource_sampler.py, which reads memory by spawning PowerShell. This
reads MEMORYSTATUSEX through ctypes in the calling process: no child process,
nothing to fail to start. ullTotalPageFile is the COMMIT LIMIT and
ullAvailPageFile the COMMIT AVAILABLE - the quantity an allocation actually
draws on (L670: the easy-to-read number is physical RAM, and it is the wrong
one).

    python scripts/commit_free.py            # one JSON line
"""
import ctypes
import json
import sys

GB = float(2 ** 30)


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def read() -> dict:
    """Commit and physical memory in GB. Raises OSError off Windows or when
    the call fails - an unreadable value must never render as a measured one
    (L580), so there is no fallback number."""
    if not hasattr(ctypes, "windll"):
        raise OSError("GlobalMemoryStatusEx is Windows-only")
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise OSError("GlobalMemoryStatusEx returned 0")
    return {"commit_limit_gb": round(m.ullTotalPageFile / GB, 2),
            "commit_free_gb": round(m.ullAvailPageFile / GB, 2),
            "commit_used_pct": round(100.0 * (1 - m.ullAvailPageFile
                                              / m.ullTotalPageFile), 1),
            "phys_total_gb": round(m.ullTotalPhys / GB, 2),
            "phys_free_gb": round(m.ullAvailPhys / GB, 2),
            "memory_load_pct": int(m.dwMemoryLoad),
            "source": "GlobalMemoryStatusEx (in-process, runbook Step 2.5)"}


def main() -> int:
    try:
        print(json.dumps(read()))
        return 0
    except OSError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
