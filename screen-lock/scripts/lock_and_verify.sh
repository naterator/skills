#!/bin/sh
# Run only with the user's lock authorization and permitted host execution.
set -eu

if [ "$(/usr/bin/uname -s)" != Darwin ]; then
    echo 'This helper requires macOS.' >&2
    exit 2
fi

skill_script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
command -v python3 >/dev/null 2>&1 || {
    echo 'An existing Python 3 runtime is required; no lock attempted.' >&2
    exit 2
}
[ -x /usr/bin/swift ] || {
    echo 'An existing Swift runtime is required; no lock attempted.' >&2
    exit 2
}
skill_lock_cache=$(/usr/bin/mktemp -d "${TMPDIR:-/private/tmp}/codex-lock-cache.XXXXXX")
trap 'rm -rf -- "$skill_lock_cache"' EXIT HUP INT TERM

/usr/bin/swift -module-cache-path "$skill_lock_cache" "$skill_script_dir/lock_screen.swift"
python3 "$skill_script_dir/verify_lock.py"
