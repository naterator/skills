# Apple preparation without review submission

Read this before changing App Store Connect or running upload/distribution tooling. Use the repository's authenticated API/CLI tools or connectors first; browser-only automation can fill a capability gap. Inspect current tool help and official Apple documentation when endpoint semantics or current asset requirements are uncertain.

## Inspect before mutating

- Resolve the exact team, app ID/bundle ID, marketing version, platform, build numbers, TestFlight groups, and intended App Store version. Snapshot current server state and preserve the project's established release policy.
- Inspect helper implementations, config, hooks, and CI triggers for submission, automatic review, auto-distribution to external testers, public release, or production deployment. Disable/avoid those paths for this run. Do not invoke a broad release helper just because upload is one of its actions.
- A build attached to a version that is already submitted, waiting for review, in review, approved, or released can constrain changes. Do not cancel, withdraw, reject, resubmit, or replace a published version to bypass that state. Finish safe checks and record the constraint; do not invent a new marketing version merely to evade it.
- Check upload/internal TestFlight restrictions separately from the ability to change a version's selected App Store build. Do not assume a locked Store version also prevents a permitted newer TestFlight candidate. Finish safe independent uploads and internal testing preparation even when Store build selection remains blocked.

## Builds and TestFlight

- For each supported Apple platform, match the correct signed release artifact to its proven build inputs and distribution record. Verify build identity, platform, minimum OS/device coverage, entitlements, required privacy manifests and applicable validation/export results.
- Upload missing/stale candidates using the existing credentials and monotonic build policy. An upload receipt is not processing success. Query the exact build until processing reaches a usable state or a concrete failure occurs; inspect the error rather than repeatedly re-uploading.
- Complete export-compliance/encryption and beta metadata only from code, existing verified answers, and owner-provided facts. A legal agreement or unknown declaration is an explicit blocker, not permission to guess.
- Verify the intended latest candidate is processed, valid, unexpired, and available to the project's intended **internal** TestFlight group/testers where applicable. Check both build state and tester/group association. Record platform-specific state rather than inferring all platforms from one build.
- If external testing requires Beta App Review, leave it pending and report the boundary. Do not submit it, even if a CLI labels the operation simply distribute. Do not change tester membership or send invitations beyond the project's existing testing setup unless separately authorized.
- Confirm the intended App Store version selects the correct platform build when its state allows preparation. Preserve existing selection/state if it cannot be safely changed and report the discrepancy.

## Product page and review materials

Inspect local source assets **and live App Store Connect contents** for each supported platform/localization and currently required device class. Check current Apple requirements if dimensions or required slots are unclear.

- Screenshots/previews: required sets present, correct ordering and dimensions, legible, current UI/product naming, correct device/platform, no debug overlays or private data, and uploads fully processed. Prefer reproducible project capture/composition scripts. Visually inspect the final images, rather than accepting filenames or API counts alone. Use existing sample/demo data when appropriate.
- Icons and branding: correct product name, bundle/display names, catalog icons, macOS packaging, tvOS layers/brand assets where applicable, and the icon actually extracted from the uploaded build. Many icons come from the binary; if wrong, fix the source and rebuild/re-upload rather than claiming a metadata edit fixed them.
- Text: accurate description, subtitle, keywords, promotional text, What's New for updates, copyright, categories, and all maintained localizations. Avoid claims about absent features or unsupported platforms. Keep support, marketing, and privacy URLs current and verify the relevant pages are reachable and describe the app accurately.
- Submission details: applicable age rating, privacy disclosures versus actual SDK/data behavior, content rights, export-compliance answers, review notes, contact details, demo credentials/sample-mode instructions, attachments, and purchase/restore instructions. Preserve unknown business/legal answers as blockers. Never put private review credentials in public documentation or logs.
- Monetization if present: check product identifiers, in-app purchase/subscription metadata, localized text and review screenshots, entitlement mapping, product readiness and attachment to the version as applicable. Verify the purchase/restore path only to the extent the environment supports it. Do not create/change pricing or submit products for review as a shortcut.

Prepare editable drafts and associations within scope; distinguish a local asset from one actually uploaded and processed. If this platform, version, or localization needs no change, retain the verified materials instead of churning them.

## Submission boundary and final state

Do not perform any action whose purpose or side effect is requesting Apple review, including App Store versions, external beta builds, purchases, subscriptions, or rejected items. Do not use submit-for-review commands or create/advance review submission requests, even if the UI offers a final readiness check. Read-only inspection and safe local validation are sufficient to report readiness with explicit evidence limits.

Re-query build processing, internal TestFlight association, version/build selection, and materials after mutations. Record concrete states and IDs. A complete editable draft can be ready to submit while still awaiting the owner's submission action; a missing build, required screenshot, unresolved declaration, native acceptance gate, or blocked external-beta requirement remains a stated limitation. No upload, draft, validation, or TestFlight availability proves Apple approval.
