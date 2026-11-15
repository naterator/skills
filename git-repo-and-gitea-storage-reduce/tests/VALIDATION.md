# Public-copy validation — November 15, 2026

## Reproducible local checks

The bundled suite has 15 isolated regression tests. It uses only temporary
Git repositories and synthetic signing keys/homes, not a real project,
personal key, remote account or server.

On the date above, all 15 tests passed for this sanitized copy, and the
repository's source-tree checker reported no findings.

Coverage includes:

- Read-only audits and current/historical/recovery object classification.
- Dry-run invariants and refusal to remove current-HEAD blobs.
- Preservation of dirty owner files, unknown stashes, notes and tags.
- Refusal of redirected Git storage, invalid backups and wrong signers.
- Signing failure without unsigned fallback or ref changes.
- Protection of existing recovery receipts.
- Signed auxiliary-tree remapping and merge-parent ordering.
- Authenticated signing-subkey/primary-key verification.
- Narrow reflog expiry and GC that preserve old reachable recovery entries.
- Physical removal of an approved obsolete fixture blob and strict fsck.

Use the [skill's test instructions](../SKILL.md#maintenance-and-tests). Missing `gpg` or `gpgconf`
skips signing cases; a skipped case is not a pass of that signing capability.
Python helpers use only standard-library and bundled imports.

## Privacy and evidence boundaries

Personal paths, hosts, identities, organization/project names, deployment
inventory and private evidence locations are not part of this public copy.
The walkthrough is explicitly synthetic. Hostnames and repositories in the
offline planning prompts are illustrative, not runtime configuration.

The public-copy checks cover Python/JSON syntax, local links, portable
dependency declarations, source-tree privacy heuristics and isolated fixture
behavior. They do not establish live Gitea access, successful server cleanup,
universal agent compliance, or preservation of every possible Git extension.
No private evaluation workspace or proprietary evidence is required.

The synthetic planning prompts are bundled for future review; no private
baseline scores, model-performance claims or live-server test results are
published as validation of this copy.
