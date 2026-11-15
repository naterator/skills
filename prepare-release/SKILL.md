---
name: prepare-release
description: Validate and remediate a software project's final release readiness across all supported platforms, including current builds, TestFlight where applicable, store materials, repository documentation, and a final commit and push. Use for final validation or pre-submission preparation of mobile, desktop, or cross-platform apps. Never submits Apple review requests or publicly releases the software.
---

# Prepare Release

## Dependency preflight

Require the verified target source repository, relevant project instructions,
Git, and the documented tools/SDKs/inputs for each selected build or test route.
Signed artifacts need existing authorized signing inputs; uploads and live
store verification need compatible distribution tooling, credentials, and
connectivity. Physical acceptance needs the specified available device.
Verify prerequisites before each dependent phase. If a required item is absent,
stop that phase, report the blocker, and do not label the project fully ready.
Independent authorized phases may continue, but do not invent project scripts,
install toolchains, create signing identities, or substitute a private project.

Carry the selected project through final validation and remediation, then commit and push all eligible project changes. Finish the authorized work; report any remaining blockers precisely. Creating or editing this skill does not itself start a release run.

## Scope and hard boundaries

- An invocation for a project authorizes necessary fixes, serial builds, signing with existing credentials, TestFlight uploads and internal testing configuration where applicable, screenshots, factual store metadata updates, documentation, and the final commit and push. A narrower current request takes precedence.
- **Never submit any Apple review request.** This includes App Store review, external TestFlight/Beta App Review, in-app purchase review, and resubmission. Do not click or call anything that submits or automatically advances a review. Uploading a build is distinct from requesting review. Read [Apple preparation](references/apple-preparation.md) before Apple mutations.
- Do not publicly release a version, merge a release PR, deploy production services, withdraw a pending review, or change pricing, availability, release mode, or ownership just to complete this workflow. Existing separate authorization can cover a required production action; otherwise finish preparation and report that specific dependency. Do not invent legal, privacy, payment, or compliance facts or bypass native owner acceptance.
- Run **one build at a time across this invocation**, including subagents, archives, exports, and tests or screenshot jobs that compile. Keep one build coordinator. Parallelize read-only investigation and independent documentation reviews when useful. Do not resurrect the revoked CPU, memory-pressure, simulator, or workstation-wide workload restrictions.
- Preserve owner access: use connectors, APIs, CLIs, or browser-only automation. Do not start native desktop takeover, an agent UI locker, or equivalent screen/input control. Use CLI/simulator capture where supported; report native interactions that remain unavailable.

## 1. Establish the project and the current release contract

1. Use the named project or current checkout. Read applicable `AGENTS.md`, `README.md`, the durable project handoff, documentation index, release runbooks, scripts, and recent release evidence. Use [Project entrypoints](references/projects.md) to discover the actual owning sources. If a private Context collection has locator folders, keep detailed new facts in the source repository rather than duplicating them into those locators.
2. Inspect branch, worktree changes, remotes, and upstream state. Fetch the intended remote when possible and integrate newer relevant source changes using the project's documented workflow before freezing the release source. Preserve existing work and resolve ordinary integration issues within scope; do not reset, discard files, or force-push. Do not silently build an older checkout while describing it as latest. If the project cannot be inferred from available context, ask which project while continuing independent read-only discovery; do not run this across every known app by default.
3. Derive the supported platform and delivery matrix from actual targets, CI/build configuration, packaging, and current docs. Include applicable iPhone/iPad, macOS, tvOS, Android, Windows, Linux, web, client/server components, architectures, and release configurations; do not assume every app uses Apple tooling or that every example platform is supported. Distinguish a supported shipping target from an experiment or retired port.
4. Inspect build/upload/deploy wrappers and their hooks before running them. Confirm destinations and defaults; scripts named release, finalize, deliver, or distribute may also submit reviews or publish production. Use a narrower safe command if necessary.
5. Record an initial matrix: target, intended version/build ID, source provenance, local artifact and checks, expected distribution destination, live distribution state, and gaps. Mark truly inapplicable items with a reason. Historical notes and prior successful logs are leads, not proof of today's state.

## 2. Validate and remediate the final source

- Review the actual implementation and recent changes against the release contract. Fix relevant correctness, packaging, configuration, migration, compatibility, or documentation deviations. Keep changes within release readiness rather than adding unrelated features or launching a separate exhaustive audit.
- Run the repository's required checks and focused tests for changed or risky behavior. Include applicable core functionality, launch/navigation, persistence, network/error handling, purchases/restore, permissions, accessibility, and client/server compatibility. Use the project's acceptance checklist. A compile or simulated run does not prove physical-device, controller, purchase, or owner acceptance; record exactly what was exercised and what remains.
- Refresh documentation throughout the codebase wherever facts have changed: setup, dependencies, configuration, architecture, supported platforms, scripts, testing, known limitations, release procedure, product behavior, and dated release evidence. Search for conflicting or stale claims. Preserve clearly dated historical records rather than rewriting them as current results.
- Make `README.md` useful to a new engineer: what the app does, supported platforms, prerequisites, configuration without secrets, build/run/test steps, architecture and key directories, and links to deeper docs. Make `AGENTS.md` useful to a new LLM: canonical paths and sources of truth, effective commands, platform differences, release safeguards, credentials lookup conventions without values, verification expectations, and open acceptance/blockers. Keep detailed handoff and runbooks linked instead of duplicating everything into both files.
- Use the existing version/build policy; bump identifiers only when required for a replacement upload or the intended release. Preserve existing approved branding and edit source assets in their native form. Derive descriptions and screenshots from implemented features and the actual candidate.

## 3. Build every supported release target serially

1. Establish the final build inputs after remediation: commit plus any uncommitted changes, dependency locks, generated source/assets, build settings, version IDs, and relevant environment/toolchain. Use existing provenance tooling; otherwise record a reproducible source fingerprint and relevant artifact identities in the project's release evidence. Never include secrets in evidence. If tools require a committed source HEAD or embed its identity, create a source-freeze commit before building and retain that HEAD through dependent archive/export/upload phases. Later evidence-only commits can follow with the source ancestry and unchanged build inputs documented; do not create an endless rebuild/commit cycle.
2. Reuse an existing artifact only when reliable evidence proves it was built from these same relevant inputs, with the correct release configuration/signing and required checks. Names, timestamps, a matching version label, or an old green test result alone are insufficient. If provenance cannot be established, rebuild the affected target.
3. Complete each required build, archive/export/package, and its verification before starting the next. Follow project commands and signing conventions. Check the produced artifact's identity/version, supported devices/architectures, entitlements/capabilities, and applicable signatures and packaging; retain deliverables in the repository's established artifact location rather than committing large outputs by default.
4. Repair failures and rerun the affected checks. If code, bundled content, dependencies, settings, or embedded metadata changes afterward, invalidate and rebuild every affected platform; upload replacement builds as needed. Documentation-only edits that do not affect build inputs do not require repeated builds. Watch for generated version files, build hooks, or embedded Git IDs that make an apparent documentation/commit change relevant.
5. For non-Apple platforms, verify their actual packaging and release-preparation requirements too: e.g. signed Android artifacts, desktop packages, web production builds, server packages and protocol compatibility. Prepare the required artifacts and any already-authorized staging distribution. A TestFlight-only result does not satisfy the other platforms. Do not turn a build request into an unrequested public deployment or store publication.

## 4. Verify distribution and store readiness

For Apple targets, follow [Apple preparation](references/apple-preparation.md): inspect live state, upload missing or stale candidates, wait for processing, verify internal TestFlight availability and the intended build selection, and reconcile metadata and assets. For other targets, inspect their project's equivalent store/staging requirements and prepare them within scope.

Keep checking active uploads and processing in this chat using bounded waits. Avoid duplicate uploads when an earlier upload may have succeeded: query the exact app/platform/version/build first. Recover actionable failures, but stop identical retries after the cause is established. Consult existing project records before requesting owner-only facts or acceptance; if still missing, ask concisely while continuing independent work. If credentials, agreements, required owner facts, native acceptance, provider availability, or the no-review boundary blocks a step, complete unaffected work and record the exact blocker; do not label pending processing as success.

## 5. Reconcile evidence, commit, and push

1. Save a concise, dated release readiness record in the repository's established release-doc location. For each supported target, include source identity/fingerprint, version/build, artifact and verification evidence, distribution/build IDs and live states, store materials/metadata checked, and outstanding acceptance or blockers. Record the observation time and make local evidence distinguishable from service state. Explicitly state that no Apple review request was submitted by this run; existing historical submissions remain historical facts.
2. Recheck the final diff against the built inputs, documentation, selected store builds, and evidence. Recheck upstream before pushing; if relevant incoming changes appeared during the run or cause a push rejection, integrate them without discarding work and reopen affected validation/build/upload steps. Any relevant final change also reopens those steps. Ensure records refer to the final code and distinguish later documentation-only commits instead of falsely claiming an older binary embeds the final commit.
3. Inspect every modified, staged, deleted, and untracked file. The request to commit and push all files covers all eligible changes in the selected project, including pre-existing changes after review; do not silently omit them. Respect ignore rules, repository instructions, and secret/artifact exclusions. Do not commit credentials, private signing material, machine state such as a repo-root `.codex`, or bulk build output merely because it exists. Report excluded material that matters to the handoff.
4. Stage, inspect the staged diff and whitespace checks, commit with a sensible message derived from the actual changes, then push to the repository's intended remote/branch. Keep these mutations sequential. Respect the project's contribution policy; do not assume every project pushes to `origin/main`, create an empty commit, amend, force-push, or merge a PR without authorization. Do not rerun passed checks for unchanged inputs.
5. Verify the local commit equals the destination's actual remote branch tip (for example with `git ls-remote`) and inspect the remaining worktree state. If there were no changes, verify existing synchronization instead of creating an empty commit. If push or another requirement remains blocked, report the completed work and exact remaining action; never claim full completion.

## Completion response

Report briefly: project, version/build and platforms; key checks and artifact/distribution states; store and documentation readiness; commit and destination branch with push verification; and any concrete blockers or owner acceptance still required. Distinguish **ready to submit** from **not yet ready** using the recorded evidence. End with a clear statement that **no Apple review requests were submitted**. Never imply submission, approval, or public release from an upload or a prepared draft.

## Dependencies and portability

The release workflow and Apple/project-discovery references are bundled; no
other skill or particular private project is required. Execution needs the
target source repository, its supported build/test toolchains, Git, and relevant
SDKs/signing inputs. Upload/store verification also needs authorized distribution
APIs/CLIs or browser access and connectivity. Local validation can be reported
separately when services are unavailable. Reusable preflight/artifact-manifest
helpers and synthetic distribution fixtures could be added locally, but
toolchains, signing secrets, devices, and store services remain external.
