# Conservative signed history rewriting

## Approval and backup

Explain before execution:

- Rewritten commits have new IDs and new signatures. Every retained original
  author/date/message remains historical metadata; the fresh signature is by
  the selected current signer, not a claim that another author signed today.
- Older checkouts can become incomplete when obsolete binary versions are
  removed. Do not promise every historical commit will still build.
- PR refs, tags, stashes, notes, other branches, checkpoints and clones can
  retain/reintroduce old objects. Inspect and obtain the correct scope.
- Current assets must remain, even when raw authoring audio and encrypted
  shipping resources look redundant.
- A normal filter-repo/filter-branch rewrite does not preserve valid commit
  signatures. A separate complete re-sign-and-verify step is necessary.
- Signed tags, mergetags, unusual encoding/extra commit headers, shared
  worktrees, partial/shallow clones and alternate object pools need an expert
  extension; stop rather than discard unsupported metadata.

Create the recovery bundle **outside** the repository and any path scheduled
for cleanup:

```sh
git bundle create <external>/before-rewrite.bundle --all
git bundle verify <external>/before-rewrite.bundle
```

Record its SHA-256, size, original refs, tip/tree and protected current inputs.
Inspect bundle prerequisites: an incremental bundle that only verifies
because the live repo has its base is not an independent recovery backup.
Verify a restore in a temporary repository where practical, then delete only
that task-owned restore fixture. Keep the bundle until the owner authorizes
its removal. Scratch storage is not a permanent/off-machine archive.

`--all` backs up referenced history, not ignored assets, every reflog-only
commit, or arbitrary unreachable objects. If those contain possible recovery
work, resolve its retention explicitly before garbage collection.

## Signing

Read the configured `user.signingkey`, `gpg.format` and signing program.
Prefer the configured program over an unrelated `gpg` on PATH; different
installations may use incompatible agents. Do not restart/kill the owner's
agent or import/export private keys to fix a tool mismatch.

Make a harmless detached-signature preflight in private scratch, using the
configured fingerprint, then verify it. If the key is locked/unavailable,
stop and ask for normal owner authentication; no unsigned fallback.

For rewritten commits, preserve tree ordering, parent order, author,
committer, author/committer timestamps and exact message bytes. Remove the
old embedded signature and use `git commit-tree -S<configured-key>` to create
a fresh one. Verify every result with `git verify-commit --raw` or equivalent;
match the validated fingerprint, not merely a “signed” indicator.
When GPG selects a signing subkey, verify its authenticated primary-key
binding to the configured fingerprint and record both fingerprints. That is
not permission to substitute an unrelated key.

## Bundled helper

`scripts/rewrite_signed_history.py` deliberately supports a limited common
case: one named local branch, at most its matching remote-tracking ref, and
explicitly approved auxiliary **tree** refs. It rejects tags, other branch
roots, stashes/notes/replace refs, shallow/partial/alternate/shared-worktree
repositories, dirty worktrees, submodules, and unsupported headers.
Do not weaken its checks to force through an unfamiliar repository.

The agent creates the following **owner-reviewed** JSON plan outside source.
A boolean in a repository file is not evidence of user approval.

```json
{
  "schema": 1,
  "repository": "/absolute/path/to/checkout",
  "branch": "main",
  "old_head": "<full-current-commit-id>",
  "remove_blob_ids": ["<obsolete-binary-blob-id>"],
  "auxiliary_tree_refs": [],
  "signing_key": "<configured-full-fingerprint>",
  "backup_bundle": "/external/before-rewrite.bundle",
  "backup_sha256": "<verified-bundle-sha256>"
}
```

Derive candidate IDs from a reviewed audit. A `binary_prefix` flag is a
candidate classifier, not consent or proof that losing the historical input
is acceptable. Reject IDs reachable from protected current tips.

Dry-run first:

```sh
python3 <skill-dir>/scripts/rewrite_signed_history.py \
  --plan <external>/rewrite-plan.json
```

After the actual approval:

```sh
python3 <skill-dir>/scripts/rewrite_signed_history.py \
  --plan <external>/rewrite-plan.json --apply \
  --expected-head <full-old-id> \
  --ack-rewrite-and-resign
```

The helper checks an independent complete bundle, configured signing
fingerprint, current index/files, ref scope and protected blobs. It creates
and verifies every new commit before an atomic expected-old-value ref update.
Reports and maps go beside the external plan, never inside tracked source.
It does **not** push, remove refs, expire reflogs, or garbage-collect.

On signing/verification failure, refs remain unchanged. New objects may
exist unreachable; retain the failure report and do not claim cleanup
completed. Investigate current processes/locks before resuming. Do not rerun
blindly or delete the owner's work to satisfy the preflight.

## Publish, document and reclaim

Verify the exact rewritten tip tree equals the old tip tree. Compare frozen
release input trees separately when old source IDs are used by signed
artifacts. Keep the original source IDs in original receipts and create an
old→new lookup map; do not forge new provenance for an existing binary.

A small signed documentation follow-up may record the rewrite, backup,
mapping and retired screenshot references. Prove any such changes are
documentation-only. A rewritten commit's source tree may differ from its
original precisely because obsolete historical assets were removed.

Immediately before the remote update, verify live heads/tags and the lease:

```sh
git push --force-with-lease=refs/heads/<branch>:<observed-old-id> \
  <remote> <branch>
```

If rejected, stop; do not disable protection, use a blind `--force`, or
overwrite another person's new commits. Do not mirror-push administrative
refs, notes, tags, or unrelated branches.

Once local and remote refs agree, perform the approved **local** ref/reflog
cleanup and GC described in `local-cleanup.md`. Scan `--all`, not only HEAD,
for retained obsolete blobs. Re-check the physical object inventory after
GC and verify a fresh remote clone, including signatures. Then continue to
the Gitea server phase; the server may still hold old reflogs and packs.
