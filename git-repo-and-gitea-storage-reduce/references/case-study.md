# Illustrative walkthrough — synthetic

This example is invented to explain the workflow. Its repository, sizes,
commit counts, deployment and outcomes are not real operational evidence,
configuration defaults or authorization.

## Audit and protected inputs

An example game has a large ignored build directory and a 2 GiB Git database.
The owner first requests a read-only report, not immediate deletion.

The agent separates current signed archives, dSYMs, exports, final screenshots,
PCM masters, source assets, signing inputs and nested resource seeds from
older pilots, duplicate encodes, test results, caches and experiments.
It explains the loss of historical diagnostics before proposing removals.
Approved cleanup uses exact paths and retained-file hashes, not a recursive
delete of the mixed build directory.

## Local history and signatures

An object audit finds that most Git bytes belong to older music/image versions
or recovery objects rather than the current tree. The owner approves a
specific obsolete-blob list and a rewrite of one branch.

The agent verifies an external complete bundle, the configured GPG key,
current inputs and ref scope. It preserves the commit graph and metadata,
freshly signs and verifies each rewritten commit, and proves the current
tree is unchanged before an explicit old-OID force-with-lease push.
An auxiliary tool checkpoint is retained or explicitly remapped after review,
not blanket-deleted. Unknown stashes, tags and owner work remain protected.

Approved local ref/reflog expiry and actual garbage collection follow the
rewrite. A fresh remote clone verifies the small reachable history and its
signatures. The external bundle's separate disk usage is reported; old
images no longer exist in the compacted history.

## Gitea maintenance

The displayed Gitea size stays large even though a fresh clone is small.
The owner approves built-in all-repository GC, a scoped immediate prune,
and a final built-in refresh if needed.

After an ambiguous timeout, the agent checks actual task/process state
instead of blindly retrying. It discovers the correct server container,
allowlisted repository ROOT, service UID, refs and writer/lock state through
the owner's verified access route.

Old server reflogs still pin the original history. During a no-push window,
the agent expires only the approved recovery scope and runs prune-now on
only the verified example bare repository as its service user. It checks
strict fsck, object absence, unchanged signed commits and allocated disk use.

If the DB-backed size counter is stale, a final approved built-in GC refreshes
it. The agent reads the API again rather than editing SQL, changing retention,
creating a fake push or transferring a private signing key into the server.
It records actual results and confirms when pushes may resume.
