# Gitea: built-in GC, scoped prune, counter refresh

## Separate the three measurements

1. A fresh clone transfers reachable history, not necessarily all server data.
2. The bare repository can retain obsolete objects through reflogs, hidden
   refs, cruft packs, age-based retention or outstanding writers.
3. Gitea's repository `size` API field is a stored counter (observed in KiB);
   it can remain stale after manual filesystem maintenance.

Check units against the installed API version. Measure both pack logical
bytes and filesystem-allocated `du` usage. ZFS/NFS snapshots, backups, LFS,
release assets, archives, packages and Actions artifacts are separate
storage; do not delete them as if they were unused Git blobs.

## Discover before any write

Use existing authenticated connectors/CLI. For an installed `tea`, check its
help before assuming flags. Never print its token/config.

```sh
tea api --login <login> --method GET repos/<owner>/<repo>
tea api --login <login> --method GET repos/<owner>/<repo>/git/refs
tea api --login <login> --method GET 'repos/<owner>/<repo>/pulls?state=all&limit=50'
tea api --login <login> --method GET admin/cron
```

Paginate refs/PRs if needed. Read the server version and its API/maintenance
documentation. API PR counts alone do not prove no hidden server refs.
Do not take a private repository's anonymous 404 as evidence it is missing.

On observed Gitea 1.26.4:

- The task is `git_gc_repos`.
- The admin dashboard is `/-/admin`, under Maintenance Operations.
- The built-in GC updates repository sizes after each successful repo GC.
- The task can be disabled while still available to run manually.
- Default GC need not remove recently orphaned objects, and reflogs can pin
  older history regardless of an otherwise successful rewrite.

These are versioned observations, not universal route/config defaults.
Do not permanently set global `--prune=now`, change retention, or enable
scheduled tasks unless requested.

## Step A — built-in GC first

Explain that this is **all-repository** maintenance, not a scoped repo call.
Get approval for the first run and a possible final size-refresh run.

```sh
tea api --login <login> --method POST admin/cron/git_gc_repos
```

Use a long, finite client timeout (for example five minutes), not a 10–45
second default for a server-wide maintenance job. Record start time and
task `prev`/`exec_times` plus target repo size before/after.

A timed-out POST is ambiguous. Do not immediately resubmit. Check the task
readback, server Git processes and locks, relevant error notices/logs, and
the actual repo state. An execution counter increment proves a run was
triggered/recorded, **not necessarily that every repository completed**.
Do not kill the server task because the local client exited.

## Step B — enter the correct datastore

Use the owner's explicitly supplied, verified access route. For example, a
Kubernetes deployment might be reached by SSH to a trusted administration
host, authorized sudo there, and k3s's kubectl subcommand. This is only an
illustration: a different deployment needs its own agreed route.

Sudo's secure PATH may not find a binary available in the login shell.
Discover the actual k3s binary rather than changing sudo/system PATH. The
following host and binary path are placeholders, not discovered targets:

```sh
ssh -o BatchMode=yes -o ConnectTimeout=10 admin-host.example.org \
  'sudo -n /usr/local/bin/k3s kubectl get pods -A -o json'
```

Parse pod JSON and print only namespace/name/image/status, not full
environment/config secrets. Choose the actual Gitea server, not an Actions
runner, and verify the selected container and persistent volume.
Do not assume a namespace, label, pod name or persistent-volume layout.

```sh
ssh admin-host.example.org 'sudo -n /usr/local/bin/k3s kubectl -n <ns> \
  exec <verified-pod> -c <gitea-container> -- id'
```

Check the running Gitea process's config-file path. Read only allowlisted
configuration fields such as `[repository] ROOT`; do not dump `app.ini`,
database passwords, environment variables, Kubernetes Secrets or key files.

An illustrative bare repository path is:

`/srv/gitea/repos/example-org/example-game.git`

Derive the current target from the configured root and owner/repo identity,
not that literal path. Verify ownership, canonical path, no symlink escape,
bare status, HEAD/default branch and live refs before mutation.

For a rootless container, verify its actual service user and UID/GID; `git`
with UID 1000 is a common example, not an instruction to assume ownership.
Use the verified service user for Git. Host root access does not justify root-owned
packs or `chmod -R`/`chown -R` on the datastore.

Do not bypass a failed SSH host-key check. Use verified existing host aliases
or obtain owner confirmation of the correct server key.

## Step C — scoped actual repository cleanup

Confirm the external recovery bundle still exists and the rewritten current
branch matches the validated local/remote ID. Record:

```sh
git -C <verified-bare-repo> rev-parse --is-bare-repository refs/heads/<branch>
git -C <verified-bare-repo> for-each-ref \
  --format='%(refname) %(objectname) %(objecttype)'
git -C <verified-bare-repo> count-objects -vH
git -C <verified-bare-repo> reflog show --all --format=%H
du -sk <verified-bare-repo>
```

Summarize long reflogs; do not dump hundreds of repeated commit IDs.
Inspect server processes and repo locks. Parse process **executable/comm**,
not a substring like `" git "` that also matches every process's Unix user.
Wait for built-in GC and any writer to finish. Establish a no-push window.
Do not stop unrelated Gitea workloads or edit cluster deployment settings.

For the explicitly approved repo/recovery scope, as its service UID:

```sh
git -C <verified-bare-repo> reflog expire \
  --expire=now --expire-unreachable=now --all
git -C <verified-bare-repo> gc --prune=now
git -C <verified-bare-repo> fsck --full --strict --no-progress
```

This stronger expiry discards that repo's reflog recovery. Use the narrower
policy from the local reference when approval did not cover all reflogs.
Run commands separately or in a bounded, checked script; avoid a shell chain
that reports success after an earlier failed command.

If non-main refs pin obsolete history, **stop for a ref retention decision**.
Do not delete PR refs, tags, branch refs, backups or other repositories to
make a size target happen.

After GC, verify:

- Exact refs/main/commit IDs and all retained commits are unchanged.
- Strict fsck succeeds and no task locks remain.
- Removed blob IDs are physically absent from all server objects.
- Ownership remains appropriate; capture actual/pack size and reflog count.
- Signatures remain the same because commit object IDs/bytes are unchanged.
  Do not copy private signing keys into a server container to verify them.

## Step D — refresh Gitea's size and finish

Manual `git gc` does not update the DB's size counter. Use the installed
version's supported size-refresh maintenance operation. A final approved
built-in GC can refresh the API-reported size after the scoped prune.
Wait for and verify the actual result; do not assume a runtime or size.

Recheck `repos/<owner>/<repo>` after that task completes. Do not assume
`check_repo_stats` recalculates Git bytes, invent a repo-specific API endpoint,
send a fake push, create an empty commit, modify hooks, or update SQL rows to
refresh a number. If a supported global refresh lacks approval, report the
actual disk result and stale-counter blocker, then ask.

Report both physical disk and Gitea-reported size with units. Save a small
receipt of commands, times, pod/container/path/user, before/after refs/sizes,
fsck/object checks and task runs without credentials. Confirm writers are
finished and pushes may resume. Leave normal GC scheduling/retention unchanged.

## Sources

Consult the installed-version equivalents, not blindly the latest main:

- https://git-scm.com/docs/git-gc — pruning grace and concurrent-write risk.
- https://git-scm.com/docs/git-reflog — expiry and recovery scope.
- https://docs.gitea.com/administration/config-cheat-sheet — GC configuration.
- https://raw.githubusercontent.com/go-gitea/gitea/v1.26.4/services/repository/check.go — built-in GC and `UpdateRepoSize`.
- https://raw.githubusercontent.com/go-gitea/gitea/v1.26.4/services/cron/tasks_extended.go — all-repository task and defaults.
