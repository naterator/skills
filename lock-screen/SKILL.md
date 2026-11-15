---
name: lock-screen
description: Lock the user's macOS workstation when they ask to lock the screen, computer, or workstation, and verify the actual console lock state when available.
---

# Lock Screen

## Dependency preflight

Require macOS, Python 3.9+, the bundled primary helper, `/bin/launchctl`,
`/usr/sbin/ioreg`, `/dev/console`, and the logged-in owner's usable GUI session.
The Security framework and private login framework's `SACLockScreenImmediate`
symbol must be available with the existing permissions. Optional legacy helpers
add `/usr/bin/swift` and their shell utilities; they are not substitutes for
a missing primary-route OS capability. If any selected-route dependency or
ownership check fails, stop without requesting a lock and report the blocker.
Do not install helpers, change authentication, or acquire desktop control.

A lock request authorizes one attempt. Preserve the requested host and delay without asking again. Finish other GUI work before locking. Run as the logged-in Mac owner, without sudo.

## Lock without desktop control

Use the bundled standalone command as the final system action. Resolve it
relative to this skill's `SKILL.md`, not the chat's working directory:

```sh
python3 scripts/screen-lock
```

Use an existing Python 3 interpreter. No command installed in a personal scripts folder is required. The older `lock_and_verify.sh`, Swift helper, and verifier are optional legacy resources; they are not required and add a Swift-toolchain prerequisite. Do not prefer them over the bundled Python command. A direct native lock request from SSH may fail to reach the GUI session.

The standalone command verifies console ownership and routes one request through a temporary, one-shot job in that owner's GUI launchd domain. It calls the private `SACLockScreenImmediate` API with its return value checked, samples `IOConsoleLocked`, removes only its own job, and verifies both job and child-process cleanup. It installs no persistent agent. Compatibility with this private API is not guaranteed. If cleanup is uncertain, retain and report its diagnostic evidence; do not delete or terminate unrelated jobs.

Do not initialize native computer use, call `cua.getApp`, or launch an agent screen/input locker. Never obstruct the owner's login or local takeover. Do not use display sleep as a lock or change password requirements, automatic login/unlock, authentication, or security preferences.

Use the shell tool's permitted escalation if sandboxing blocks this exact action. Respect a rejection; do not substitute another tool, background process, or delayed job to evade it.

## Read-only checks and results

- `python3 scripts/screen-lock --check` samples console lock state only.
- `python3 scripts/screen-lock --diagnose` checks GUI-session routing and native API availability using the same temporary job, without requesting a lock. Verify routing and cleanup on the user's own Mac; that diagnostic alone does not prove a real lock persists.
- Exit `0` / `locked`: all three samples explicitly report locked. Report the sampled result, not indefinite persistence.
- Exit `1` / `unlocked`: the final sample reports unlocked. Do not claim success; `temporary_lock_observed` distinguishes a sampled temporary lock.
- Exit `2` / `unverified` or another concrete error: report the failure. Missing state is not evidence of an unlocked session.

A request accepted by the native API is not proof of locking. If it fails, briefly locks then unlocks, or cannot be verified, stop and report that outcome. Do not automatically retry or unlock the Mac to inspect it. Never use screenshots or desktop takeover merely to verify a lock.

## Maintain the standalone command

The bundled `scripts/screen-lock` is authoritative for this distribution. A user may choose to install a standalone private copy elsewhere; that copy is not a prerequisite. Repository maintenance does not authorize inspecting or modifying an installed copy outside this repository. Update such a copy only when that separate scope is requested.

Keep the installed command owner-executable (mode `0700`). Never replace it with a symlink, wrapper, or runtime import/source from a skill, workspace, `.codex`, or `.agents` directory. Embed required helper logic; normal system tools and the documented installed runtime remain prerequisites. Replace files atomically, compare their bytes, and check permissions and that neither copy is a symlink.

Validate with syntax checks, `--help`, and credential-free mocks or explicitly read-only diagnostics. Skill maintenance does not itself authorize a live lock/unlock, credential change, or firewall write. Report any runtime acceptance still pending.

## Dependencies and portability

The primary helper is bundled Python 3.9+ standard-library code. Actual locking
requires macOS Security/login APIs, `launchctl`, `ioreg`, process inspection,
the logged-in owner's GUI session, and existing permissions. No separate
installed command or other skill is needed. Legacy shell/Swift resources are
optional and require Swift if selected. OS locking cannot be made portable
by vendoring private Apple frameworks; mock those boundaries for tests.
