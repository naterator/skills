# Working files, garbage and refs

## Classify before deleting

Inventory immediate and nested paths proportionally with `du`, Git status,
ignore rules, manifests and filename/content checks. Separate:

| Usually regenerable after approval | Often essential despite being ignored |
| --- | --- |
| Old Xcode DerivedData, module caches, Python bytecode | Current signed archives, dSYMs, exports, provisioning inputs |
| Old simulator/test compilation copies | Final release screenshots and capture provenance |
| Superseded package/export copies | Source models/audio and generated shipping resources |
| Re-creatable virtual environments with dependency pins | Original PCM masters, unique recorded inputs and production recipes |
| Old `.xcresult` and `.trace` files, after accepting diagnostic loss | Small receipts, source hash maps, final reports |
| Proven byte-identical export duplicates | Resource seeds/material, including nested rollback folders |

These are examples, not suffix-based deletion rules. Test results contain
diagnostics and sometimes original captures; retain extracted final evidence
before removing the bundle. Verify an export duplicate by its full checksum,
not equal name/length or decoded-sound similarity.

A higher-numbered local resource variant is not necessarily the latest
distributed build. Source defaults can lag signed delivery overrides.
Inspect actual archives/package identities on all supported platforms.

For a mixed directory, prune exact children while preserving important
descendants in place. Avoid relocating private regeneration material unless
needed; relocations require recording the new path and verifying consumers.
Removing a virtual environment should retain the maintained dependency pins;
record installed package versions when they contain useful reproducibility
information. Never include tokens or private key values in inventories.

## Deletion manifest and proof

1. Record the exact real repository path and baseline status/index/HEAD/refs.
2. List approved removal paths, category, expected byte count, rationale and
   paths they must not overlap.
3. Reject a candidate equal to the repository, `.git`, common Git directory,
   a broad source directory or any protected ancestor/descendant.
4. Check symlinks and resolved ancestors. Do not follow external links;
   reject surprising roots or unsafe mount/shared-store boundaries.
5. For cache-only work, prove no tracked file lies beneath a candidate.
   `git check-ignore` is a secondary check, not proof of disposability.
6. Snapshot retained file paths, modes, hashes and symlink targets. Exclude
   only the precise deletion manifest and task receipt from comparison.
   Do not follow symlinks or hash credentials into public output.
7. Check active compiler/app/cache consumers and task-owned processes. Do
   not kill an unrelated job to make cleanup convenient.
8. Delete the manifest only. Empty-parent removal, if desired, uses `rmdir`
   only when truly empty, not broad recursive removal.
9. Verify deleted paths are absent and every retained snapshot is identical.
   Preserve dirty/untracked owner work byte-for-byte. Record partial failure
   and completed paths; never retry the whole manifest blindly.

For tracked images/blobs, record the count/bytes and remove only approved
files. Fix current guides; preserve historical validation outcomes. If
linking historical images to a commit, warn that a later binary-history
purge will invalidate that archive. Do not silently move unwanted images
into another tracked directory.

## Git preflight

Useful read-only commands:

```sh
git status --short
git rev-parse --git-dir --git-common-dir --is-shallow-repository
git worktree list --porcelain
git for-each-ref --format='%(refname) %(objectname) %(objecttype)'
git count-objects -vH
git fsck --full --strict --no-progress
```

Suppress optional index refresh writes for audits with `GIT_OPTIONAL_LOCKS=0`.
Do not run `git fsck --lost-found` as a read-only check.

Git refs and reflogs are different:

- A branch/tag/note/stash/checkpoint ref is a reachability root.
- A remote-tracking ref can preserve obsolete history even after main changed.
- Reflogs can keep old tips alive after all ordinary refs point to new history.
- A stash or checkpoint can contain work absent from every branch.
- An auxiliary tree ref can pin large blobs without appearing as a branch.
- A root with no unique objects is not automatically unwanted.

Before pruning, show per-ref ownership and proposed keep/remap/delete
actions. Verify server refs before considering stale remote-tracking refs.
Do not use an indiscriminate `git update-ref -d` loop.

Compare-and-swap updates prevent overwriting concurrent owner changes:

```sh
git update-ref <approved-ref> <verified-new-object> <expected-old-object>
git update-ref -d <approved-obsolete-ref> <expected-old-object>
```

Use a single `git update-ref --stdin` transaction when several approved refs
must change together. Keep external maps/backup before dropping old roots.

## Garbage cleanup and expiry

Default GC normally retains recent unreachable objects; it also preserves
everything still reachable through refs/reflogs. Do not promise that running
`git gc` alone removes a deleted file's history.

Only proceed after the owner approved removal of the relevant recovery
history, backups are verified, and writers have stopped. Choose **one**
of the following expiry policies, not both.

### Narrower: selected logs, reachable entries preserved

Without `--expire=never`, the narrower command still inherits Git's normal
age limit for reachable entries.
Name the approved refs/logs (including `HEAD` when approved) rather than
silently widening a main-only request:

```sh
git reflog expire --expire=never --expire-unreachable=now <approved-ref>...
```

For the narrower policy, ordinary `git gc` can still expire unrelated old
reflogs itself. Inspect effective global/local and pattern-specific
`gc.*.reflogExpire*` rules. After resolving any overrides, a one-command
nonpersistent way to preserve the remaining logs is:

```sh
git -c gc.reflogExpire=never -c gc.reflogExpireUnreachable=never gc --prune=now
```

Those settings are not permission to override a pattern rule blindly. Use a
tailored invocation or stop if its effective scope is uncertain. Prune-now
discards every eligible unreachable object in the store, not just selected
binary IDs; preserve/approve unrelated recovery objects before proceeding.

### Stronger: all logs, only when explicitly approved

This discards all local reflog recovery in scope, including reachable entries.
`--all` can affect other worktrees sharing common storage; those need explicit
coordination rather than this simple recipe.

```sh
git reflog expire --expire=now --expire-unreachable=now --all
git gc --prune=now
```

For either approved policy, finish with:

```sh
git fsck --full --strict --no-progress
git count-objects -vH
```

`--prune=now` risks concurrent-write corruption. Do not add `--force`,
`--aggressive`, global retention changes or pack tuning as a routine fix.
Verify locks/processes and ensure no push, commit, fetch or GC is active.
Observe the finite command's exit result and cleanup; a timed-out GC might
still be running. Do not remove its lock until proving the process exited.

Abandoned non-Git files are a different case. Confirm the exact file's type,
age, ownership and lack of open users before removing it. Finder's
`refs/.DS_Store` causes bad-ref errors but legitimate corrupt objects or refs
must be investigated, not deleted to silence fsck.
