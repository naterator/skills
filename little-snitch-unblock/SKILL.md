---
name: little-snitch-unblock
description: Diagnose and unblock Little Snitch connection prompts that stall CLI commands, including commands run remotely over SSH. Add a scoped executable/host/port exception through Little Snitch's CLI and verify the original command. Use for Little Snitch exceptions, not general network or npm troubleshooting without evidence of a firewall prompt.
---

# Little Snitch unblock

## Dependency preflight

Require macOS, Python 3.9+, the bundled helper, and a compatible Little Snitch
CLI at `/Applications/Little Snitch.app/Contents/Components/littlesnitch`.
Its Terminal-access setting and required sudo authorization must already be
available. Alert inspection also requires readable CoreGraphics/CoreFoundation
window metadata; applying a rule requires the verified target executable and
destination. If a required file, API, permission, or setting is missing, stop
that route and report it. Do not assume an alternate private helper, enable
security settings, or create a broad firewall exception as a workaround.

Use the bundled [little-snitch-allow](scripts/little-snitch-allow) script with Python 3. Resolve it relative to this skill's `SKILL.md`, not the chat's working directory. A separately installed copy is optional, not required. Run it as the normal user: it uses sudo only for Little Snitch's protected CLI commands. It requires macOS, Little Snitch's CLI, and sudo. Little Snitch's **Settings > Security > Allow access via Terminal** must already be enabled. If disabled, explain that prerequisite; do not bypass it.

## Diagnose and scope

Inspect the stalled command, its latest relevant log, and process executable/network sockets. A request stalled on its first network fetch is suggestive, not proof of Little Snitch blocking it. Prefer current evidence:

```sh
python3 scripts/little-snitch-allow --alerts
```

This reads window titles through CoreGraphics, without screenshots, simulated input, a screen locker, or a computer-use session. Titles can reveal a connection alert even behind the normal macOS lock screen. Missing titles do not prove there is no alert; screen metadata can be unavailable to a remote session. Do not initialize native computer use to inspect or accept the alert, change GUI-scripting security settings, or bypass macOS authentication. Agent-locker recovery is outside this skill: report the blocker and stop rather than requiring another skill or guessing which processes to stop.

For Little Snitch CLI inspection, the executable is:

```sh
LS='/Applications/Little Snitch.app/Contents/Components/littlesnitch'
sudo "$LS" --user "$USER" list-preferences
sudo "$LS" --user "$USER" log --last 10m
```

Logs can omit pending decisions. Network tests from a different parent app do not reproduce the original process pair. In particular, a rule for **Ghostty via Node** does not necessarily cover **Node launched through SSH**. Determine the actual process/helper pair from the alert and current model, not merely the command's script name. Prefer an exact executable and hostname; use a domain or executable-version wildcard only when the requested scope supports it.

## Preview, apply, verify

For a standalone Node process contacting the npm registry:

```sh
python3 scripts/little-snitch-allow \
  --process /opt/homebrew/bin/node --host registry.npmjs.org
python3 scripts/little-snitch-allow \
  --process /opt/homebrew/bin/node --host registry.npmjs.org --apply
```

The script resolves ordinary executable symlinks to the current executable. A path rule for that version may need a new exception after an executable update. To intentionally cover Homebrew Node versions, use the quoted Little Snitch identity:

```sh
python3 scripts/little-snitch-allow \
  --process 'path.opt/homebrew/Cellar/node/*/bin/node' \
  --domain npmjs.org --apply
```

`--domain` includes subdomains; `--host` matches the exact hostname. `--address` takes one literal IP. TCP port 443 is the default; choose `--port` and `--protocol tcp|udp` when the observed connection differs. Rules are permanent and apply across profiles. `--user` overrides the owner inferred from sudo's invoking user. Use an explicit `--user` when the execution environment does not preserve `SUDO_USER`; never accidentally create a root rule.

For an alert showing **parent app via helper**, specify the parent's executable as `--process` and the helper as `--via`. App paths refer to the executable inside `App.app/Contents/MacOS/`, not the app directory. Existing `identifier.TEAM_ID/CODE_ID` identities are accepted too.

If the user asks to unblock an identified connection, apply the narrow exception within that authorization; do not add an extra approval conversation. Diagnosis alone does not authorize creating an exception. Respect the execution environment's escalation requirements. Never switch off filtering, change silent mode, or allow every process/host as a shortcut.

The script serializes its own writers, exports a fresh model, saves a private backup, checks for concurrent edits, adds one rule, and imports through Little Snitch's supported CLI. It reads back and compares the configuration, ignoring documented defaults and traffic counters. Identical active exceptions are no-ops. A profile-limited, disabled, or grouped rule is not treated as an identical global exception.

Backups live under the executing user's `~/Library/Application Support/little-snitch-allow/backups/`, in private change directories containing `before.json`, `requested.json`, and after a completed readback, `after.json`. These files contain private configuration; do not publish them or include them in a public skills repository. The script prints a manual recovery command. Full restore can overwrite newer edits, so inspect current state before using it. It does not automatically restore an entire old snapshot on verification failure.

Some Little Snitch versions can discard obsolete preference keys during import, including `monitorMaxConnectionsInModel`, `GeoViewMyLocationLatitude`, and `GeoViewMyLocationLongitude`. The script refuses that cleanup by default. If found, describe the affected keys without exposing stored location values, and use `--allow-legacy-cleanup` only when their removal is authorized; do not retry writing unsupported preferences. Any other unexpected change causes a verification failure and a retained backup, not a success report. Import/readback timeouts leave state uncertain: inspect before retrying.

Finally, verify the **original command** progressed/completed and, when useful, its installed result/version. A saved rule or a successful curl from another app is insufficient. Report remaining failures separately. Do not start a second package installation while the user's original installation is still running.

## Sources

- [Little Snitch CLI: export/edit/restore workflow](https://help.obdev.at/littlesnitch7/admin-command-line)
- [Rule format: processes, helpers, exact hosts, domains, ports](https://help.obdev.at/littlesnitch7/admin-lsrules-file-format)

## Maintain the standalone command

The bundled `scripts/little-snitch-allow` is authoritative for this distribution. A user may choose to install a standalone private copy elsewhere; that copy is not a prerequisite. Repository maintenance does not authorize inspecting or modifying an installed copy outside this repository. Update such a copy only when that separate scope is requested.

Keep the installed command owner-executable (mode `0700`). Never replace it with a symlink, wrapper, or runtime import/source from a skill, workspace, `.codex`, or `.agents` directory. Embed required helper logic; normal system tools and the documented installed runtime remain prerequisites. Replace files atomically, compare their bytes, and check permissions and that neither copy is a symlink.

Validate with syntax checks, `--help`, and credential-free mocks or explicitly read-only diagnostics. Skill maintenance does not itself authorize a live lock/unlock, credential change, or firewall write. Report any runtime acceptance still pending.

## Dependencies and portability

The Python 3.9+ standard-library helper is bundled. Live actions require macOS
system APIs/tools (`sudo`, CoreGraphics and CoreFoundation), a licensed Little
Snitch application/CLI, and its existing Terminal-access setting. The target
process/application and its network destination are runtime inputs. No other
skill, personal scripts folder, private firewall model, or backup is needed.
Mock CLI exports can support local tests; proprietary software and real
firewall state must remain external.
