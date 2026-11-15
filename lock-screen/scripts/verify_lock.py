#!/usr/bin/env python3
"""Read macOS console lock state without activating computer control."""

import datetime
import json
import plistlib
import subprocess
import sys
import time


def lock_flag(data):
    roots = data if isinstance(data, list) else [data]
    values = [root["IOConsoleLocked"] for root in roots
              if isinstance(root, dict) and "IOConsoleLocked" in root]
    if len(values) == 1 and type(values[0]) is bool:
        return values[0]
    return None


def read_state():
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        result = subprocess.run(
            ["/usr/sbin/ioreg", "-n", "Root", "-d1", "-a"],
            capture_output=True, timeout=3, check=True,
        )
        flag = lock_flag(plistlib.loads(result.stdout))
        return {"time": timestamp, "locked": flag}
    except (OSError, subprocess.SubprocessError, ValueError,
            plistlib.InvalidFileException) as error:
        return {"time": timestamp, "locked": None,
                "error": type(error).__name__}


def summarize(samples):
    flags = [sample["locked"] for sample in samples]
    if flags and all(flag is True for flag in flags):
        return "locked", 0
    if flags and flags[-1] is False:
        return "unlocked", 1
    return "unverified", 2


def main():
    if sys.platform != "darwin":
        print(json.dumps({"state": "unverified", "error": "macOS required"}))
        return 2
    samples = []
    for index in range(3):
        if index:
            time.sleep(1)
        samples.append(read_state())
    state, status = summarize(samples)
    print(json.dumps({"state": state, "source": "IOConsoleLocked",
                      "temporary_lock_observed": any(s["locked"] is True for s in samples) and state != "locked",
                      "samples": samples}))
    return status


if __name__ == "__main__":
    sys.exit(main())
