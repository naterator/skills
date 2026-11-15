# Project entrypoints

This public skill does not contain an owner's private repository inventory,
release history, signing configuration, or server layout. Discover those
details from the named project and current user-provided context.

## Locate the owning source

1. Start with the named checkout or current project. Read applicable ancestor
   and project `AGENTS.md`, `README.md`, the documentation index, and the durable
   engineering handoff.
2. If the user maintains a private Context collection, read its catalogue and
   the selected project's locator. Verify the canonical checkout and preserve
   any intentionally selected active worktree.
3. Keep detailed engineering and release facts in their owning Git repository.
   A Context locator should not become a second release-history store.
4. Ask for the repository only when current evidence cannot identify it.
   Never run the workflow across every discovered project by default.

## Find the current release contract

Look for supported-platform documents, release gates, testing/validation
guides, store-listing sources, distribution runbooks, build wrappers, and
dated release evidence. Names such as `docs/PROJECT_CONTEXT.md`,
`Docs/TESTING.md`, or `scripts/validate.py` are examples, not required paths.

- Re-derive platforms, architectures, build flavors, and package formats from
  actual targets and current documentation. Internal/account-free flavors
  must not accidentally reach a public distribution destination.
- Read build/export/upload helpers before execution. Check-only, unsigned,
  and local packaging results are not proof of a signed shipping artifact or
  successful upload.
- Preserve private signing keys, resource seeds, protected archives, and
  ignored distribution inputs. Do not bypass protection failures by bundling
  raw authoring content or changing loaders.
- Query distribution services before selecting replacement build identifiers.
  Local defaults and old release logs do not establish unused identifiers.
- Keep source identity, artifact hashes, upload receipts, remote processing
  state, store metadata, and physical-device acceptance distinct.
- Use existing project-specific validation and acceptance gates. Unit tests or
  simulator smoke checks do not prove native device, payment, controller,
  accessibility, or owner acceptance.
- Discover authoritative store copy, screenshots, icons, and privacy/support
  materials from the repository. A prepared local upload plan does not prove
  a remote metadata update succeeded.

Use [Apple preparation](apple-preparation.md) for Apple-specific safeguards.
Keep equivalent non-Apple packaging and distribution obligations in scope.
