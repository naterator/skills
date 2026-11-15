---
name: git-repo-and-gitea-storage-reduce
description: >-
  Conservatively audit and reduce Git repository storage end to end: explain
  large builds, caches, tracked binaries, historical blobs, unreachable objects
  and refs; preserve current releases and regeneration inputs; optionally
  rewrite and GPG re-sign history; compact local Git; then clean the matching
  Gitea server repository and refresh its displayed size. Use for oversized
  repos or .git directories, deleted files still taking space, Gitea staying
  large after a force-push, and combined local/server storage cleanup.
compatibility: Python 3.10+, Git; configured OpenPGP signing for rewrites; authenticated tea and verified SSH/kubectl access for Gitea maintenance.
---

# Git repository and Gitea storage reduction

## Dependency preflight

All routes require the host agent's existing file/command tools, a verified
target repository and permissions for the selected scope. The bundled
helpers require Python 3.10+ and a compatible Git installation. Verify those
tools and the chosen repository read-only before invoking a helper.

History rewriting additionally requires a configured compatible OpenPGP
signer, the owner's available authorized key, external backup space and
approved remote access for publication. Fixture signing tests require `gpg`
and `gpgconf` and otherwise skip those tests.

Live Gitea operations require the intended instance/repository, working
authenticated `tea` access and admin authority for global maintenance.
Datastore maintenance requires the owner's verified access route and
service-user permissions; SSH, sudo, k3s/kubectl or container tooling are
conditional on that route. Verify its actual commands and privileges.

If a prerequisite is unavailable, stop the dependent phase and report the
blocker. Independent authorized inspection may continue. Do not install or
download prerequisites, create a signing identity, invent a datastore path,
or silently switch to a different client, product or access route.

Own the authorized workflow through **local cleanup, signed history rewrite
when approved, local reference/reflog cleanup, server maintenance, scoped
server prune, and Gitea size readback**. Do not stop at a successful force-push
or tell the user to run the server commands when working access is available.
Stop only at a real approval, access, safety, or capability boundary.

Creating this skill or quoting its commands is not a request to run cleanup.
An invocation without a clear action starts with the read-only audit.

## Safety and authority

Infer authorization from the current request, not historical approvals:

| Request | Authorized action |
| --- | --- |
| “What's taking space?”, “audit”, skill name alone | Inspect and explain; no deletions, pruning, ref changes, or server writes |
| “Delete these caches/old builds; keep the latest” | Delete the approved categories/paths after a protected-file inventory; not Git history |
| “Clean unreachable Git objects/reflogs” | Explicitly scoped local recovery-data cleanup; explain what recovery will be lost |
| “Rewrite old binary history” | Prepare/execute the agreed rewrite with an external verified backup and fresh signatures; remote replacement needs explicit agreement |
| “Do the complete local and Gitea cleanup” | Execute the agreed phases; explain and obtain approval for **all-repository** Gitea GC if approval only named one repository |

One informed approval can cover an explicit phase plan, including the first
built-in GC and a final built-in size-refresh GC. Do not ask repeatedly for
the same settled permission. Do not silently broaden it to other branches,
tags, repositories, backups, or permanent server configuration.

- Preserve dirty/untracked owner work; never reset, clean, stash, or stage it
  as a convenience. A dirty tree blocks the supplied rewrite helper.
- Treat ignored directories as **unclassified**, not disposable. They may
  contain private resource seeds, profiles, masters, source inputs and receipts.
- Never delete `.git`, object packs, shared object stores, or unknown refs by
  filesystem recursion. Use Git maintenance commands for valid Git objects.
- Protect other worktrees, alternate object stores, shallow/partial clones,
  replacement/graft mechanisms, submodules and multi-branch/tag histories.
  Use a tailored plan or stop when the supplied helper rejects them.
- Preserve the owner's keyboard, mouse, login and unlock access. No desktop takeover,
  agent locker, authentication bypass, SSH host-key bypass, or agent-wide kill.
- Use finite timeouts and track owned processes. A timeout is not proof of
  failure or permission to retry a mutation; inspect actual state first.
- Never export signing private keys, print tokens/config secrets, weaken TLS,
  change signing identity, alter branch protection, or edit Gitea's DB directly.

## Phase 1 — establish identity and report the storage

Read applicable repository instructions and current release/input records.
Keep the user's selected working directory, including a deliberate subfolder.
Resolve the Git/common directory, repository identity, branch/upstream,
worktrees, remote refs, existing changes and available signing configuration.

Run the bundled **read-only** audit:

```sh
python3 <skill-dir>/scripts/audit_git_storage.py --repo <checkout> \
  --output <private-scratch>/git-storage-audit.json
```

Add `--classify-binaries` when evaluating a rewrite. It inspects historical
blob prefixes; it does not remove them. Run normal filesystem size inventories
separately for the checkout, `.git`, builds, captures and source assets.
Inspect large buckets rather than dumping every filename or secret-bearing
configuration. Do not fetch full config files into the conversation.

Report these **separately**:

1. Working-tree source, authoring inputs and shipping assets.
2. Build products/caches, current releases, captures, tests and experiments.
3. Current-HEAD Git blobs.
4. Older main-history blobs, with candidate paths and version counts.
5. Objects reachable only through other refs, then only through reflogs.
6. Objects unreachable even from reflogs; identify recoverable commits.
7. Garbage/temp files and stale UI counters versus actual disk use.

Show logical sizes, allocated disk where practical, estimated reclaimable
space, confidence and retention rationale. Object disk sums can be affected
by delta bases, hard links and pack allocation; do not promise exact savings.
Explain backup disk usage and possible filesystem snapshots separately.

Use a table such as:

| Category/path | Size | Keep/remove/review | Reason and tradeoff |
| --- | ---: | --- | --- |

Offer the least destructive useful phase first. “Deleted from HEAD” does
not mean absent from history; ordinary GC cannot delete reachable history.

## Phase 2 — approved working-tree cleanup

Read [local cleanup](references/local-cleanup.md). Identify the latest actual
release using packaged plist/manifest/version evidence, not just directory
mtime or a source build-number default. Protect every supported platform's
latest signed archives, dSYMs and exported package, plus final captures and
their provenance.

Also protect original authoring assets, PCM/music masters, private resource
seed/material files **including nested rollback material**, signing inputs,
maintained recipes/tools/dependency pins and useful small receipts.

Produce an exact removal manifest. Check containment, symlinks, tracking,
protected-path overlaps and active task processes. Snapshot retained content
and Git state. Delete only the approved manifest, never a broad parent with
mixed data. Compare retained hashes/modes and Git state afterward.

Tracked media cleanup needs separate approval from cache cleanup. Keep text
guides coherent; preserve dated outcomes rather than inventing new passes.
Links to old commits will **not** remain a durable image archive if the
following phase purges those binaries from history.

## Phase 3 — local garbage and reference review

Inventory refs **before** deciding what is unused. Distinguish branches, tags,
remote-tracking refs, stashes, notes, replace refs, checkpoints, tool-managed
tree refs, and worktree-specific refs. Show each proposed deletion/remapping
with its old object ID, reachability effect and owner-approved reason.

“No unique objects” is useful evidence, not authorization to delete a ref.
Do not blanket-delete `refs/codex/*`, `refs/original/*`, stashes or tags.
Preserve or explicitly remap a tool-managed tree ref when it would otherwise
pin removed binaries. Use compare-and-swap ref updates, not `rm -rf .git/refs`.

For approved recovery-data pruning, establish a no-writer window, verify
backups where needed and run Git reflog expiry and `git gc --prune=now` in
the **verified common repository only**. Read the reference for the distinction
between expiring unreachable versus all reflog entries. Prune-now has a
concurrent-write corruption risk; never use it casually or with `--force`.
It removes every eligible unreachable object, not only the rewrite's selected
blob IDs. Preserve unrelated recovery data first. For a narrower expiry plan,
prevent GC's own default age-based reflog expiry from broadening that plan,
including any pattern-specific overrides.

Remove only positively identified non-Git garbage such as an unopened,
abandoned `tmp_obj_*` or Finder `.DS_Store` under refs. A bad ref name can make
`git fsck` fail; do not dismiss all integrity errors as harmless Finder junk.
Re-run strict fsck after fixing the specific problem.

## Phase 4 — optional signed history rewrite

Read [signed history](references/signed-history.md) in full before this phase.
Explain loss of old binary versions, changed commit IDs, broken old links,
re-cloning requirements, remote/PR refs and scope. Preserve current files and
all important release/regeneration inputs.

1. Inventory every ref and current tip; check live remote heads/tags.
2. Verify the configured OpenPGP key can sign **without exporting it**.
3. Create and verify a complete external recovery bundle, SHA-256, original
   refs and current-tree/input manifests. Do not keep a backup ref inside the
   repository you intend to compact. A bundle does not back up ignored files
   or arbitrary unreachable recovery data.
4. Approve exact obsolete **blob IDs**, never blanket `*.png`/`*.m4a` paths.
   A candidate must be absent from every protected current tip/index/worktree.
5. Use the guarded bundled helper, or an equivalently reviewed implementation
   for unsupported histories. Preserve all commits, parent order, authors,
   committers, dates and messages. **Freshly sign every rewritten commit and
   verify every signature against the configured fingerprint.**
6. Before updating refs, prove the rewritten tip tree is byte-identical and
   all selected blobs are absent from the new reachable graph.
7. Preserve a complete old→new map and original signed-release IDs. A small,
   signed documentation follow-up can explain mapping/recovery and retired
   screenshot URLs; prove its changes are documentation-only.
8. Verify current files/build inputs and the clean worktree. Push only the
   approved branch with an **explicit old-OID force-with-lease**.

Do not claim a normal filter-repo run retained signatures; typical rewriting
tools strip or invalidate them. Signed tags/mergetags need their own plan.
Never fall back to unsigned commits or a different key.

## Phase 5 — actually compact local Git after the rewrite

A successful push does not remove the old objects from the local database.

- Verify the remote and its local tracking ref now point to the new tip.
- Re-audit **all** refs for old-history retention; remap/delete only approved
  refs with expected-old-value checks.
- With the approved recovery bundle verified and writers stopped, expire the
  agreed reflogs, then run `git gc --prune=now`.
- Run strict fsck, object inventory, status/ref equality and size checks.
  Confirm the removed blob IDs are physically absent, not merely hidden.
- Verify an independent fresh remote clone, its tip/tree and **all** required
  signatures. Remove only that task-created temporary clone afterward.

If the remote moved, the lease fails, a signature is invalid, protected
content differs, or a hidden ref still retains history, stop and explain
instead of escalating to a blind force push or destructive reset.

## Phase 6 — complete the Gitea server cleanup

Read [Gitea server maintenance](references/gitea-server.md). Discover the
current server version, account/admin capabilities, repository ID/size, refs,
PRs, GC task state and **actual** datastore path.

The required sequence, when authorized, is:

1. Run Gitea's built-in GC first. Its admin task touches **all repositories**.
   Use a long but finite client timeout; record the before/after task state.
   After an uncertain POST, inspect task/process/size state instead of retrying.
2. Enter the verified datastore via the owner's supplied route. An illustrative
   Kubernetes route is **verified administration host → authorized sudo →
   discovered k3s/kubectl → Gitea container**. Do not assume this topology.
   Discover the actual pod/container, not a runner or stale pod name.
3. Verify bare repo path, service UID/ownership, rewritten main ID and refs;
   inspect GC/writer processes, locks, reflogs and object counts. Wait for the
   built-in GC to finish. Use a no-push window.
4. As the **Gitea service user**, expire the authorized reflogs and perform
   `git gc --prune=now` on **only the named bare repository**. Do not change
   cluster resources, global retention settings, permissions or other repos.
5. Verify strict fsck, identical main/refs and commit graph, absent obsolete
   blobs, no stale task locks, and actual filesystem/pack sizes.
6. Refresh Gitea's reported size through its supported maintenance path.
   On the observed version that means a final built-in GC; include this
   second global run in approval. Read back the repo API afterward.

Do not report completion while only the local clone is small or while the
server's actual objects/counter remain unverified. If access or global-task
approval is missing, report the exact completed phase and blocker, retaining
the plan for continuation.

## Final evidence and response

Keep small private receipts outside tracked source unless documentation was
requested. Do not auto-commit/push unrelated cleanup or change Context/memory.
Document historical source-ID translation when needed, but do not relabel
old signed-build receipts with new source IDs.

Report:

- Before/after **local Git**, working artifacts and **server actual/reported**
  sizes; distinguish each measurement and net backup cost.
- Removed categories and protected current releases/inputs.
- Commit count, signing fingerprint and verification results if rewritten.
- Local/remote tip equality, strict fsck, clean/preserved owner work.
- Recovery bundle location/size, scratch-storage limitations and re-clone
  advice. Do not delete the bundle without explicit permission.
- Whether Gitea's displayed size was refreshed, residual blockers and whether
  pushes can resume. GC does not alter the verified commit signatures.

## Maintenance and tests

Helpers default to read-only/dry-run. Live deletion, GPG signing, pruning,
force pushes and server jobs are not skill-installation tests.

Run `python3 -m unittest discover -s <skill-dir>/tests -v` for isolated fixture
tests. See the [fixture suite](tests/test_storage_workflow.py) and
[offline evaluation prompts](evals/evals.json).
The [synthetic walkthrough](references/case-study.md) illustrates the
workflow; its values and deployment shape are not measured evidence,
defaults or authorization.

## Dependencies and portability

All Python imports are from the standard library or another module bundled
in this skill. Git, an OpenPGP signer, Gitea, `tea`, network access, storage
and conditional SSH/container/cluster tools remain external dependencies.
No private repository, original machine paths, credentials, external skill,
or companion script directory is required.

Resolve helpers relative to this installed skill directory. Do not execute
illustrative hosts, paths or identifiers as real targets. Read-only audits
and isolated fixtures do not establish live-server access or maintenance.
