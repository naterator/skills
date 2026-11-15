# Agent Skills

Reusable workflows for OpenCode, Codex, and compatible agents. Each
skill directory contains a `SKILL.md` entrypoint and its bundled local
instructions, templates, helpers, and references.

**Self-contained instructions do not mean dependency-free execution.** Every
skill needs a host agent. Some also operate on applications, services, or
toolchains that cannot be replaced by copying their instructions into Git.
No skill requires another skill or a private companion scripts directory.
Each entrypoint declares a **Dependency preflight**: verify the selected route's
tools, files, permissions, and runtime inputs before executing it. If a required
dependency is missing, stop that operation and report the blocker. Do not
silently substitute another tool/product, use example paths as real targets,
or install/download prerequisites. Alternative or reduced scopes need the
user's agreement; optional checks remain explicitly optional.

## Skills, dependencies, and local integration options

“Host tools” means the agent's existing file, search, editing, image-reading,
or command-execution capabilities. User documents, target projects, accounts,
and live application state are runtime inputs, not resources to publish here.
Suggestions below are proposed work, not features already implemented.

| Skill | External prerequisites beyond the host agent | What can be made local |
| --- | --- | --- |
| [`analyze-school-newsletters`](analyze-school-newsletters/SKILL.md) | Supplied materials; document/vision/OCR support for non-text input; browsing only for relevant live links. Plain-text analysis needs no extra package. | Configuration, briefing template, and academic rules are bundled. Add a format-extraction adapter with synthetic fixtures; keep real family data private. |
| [`city-news-sweep`](city-news-sweep/SKILL.md) | Web search/browsing, network access, and accessible news/official sources for a live sweep. | Strategies and report template are bundled. Add feed/search adapters and synthetic HTML/feed fixtures; local archives cannot establish live completeness. |
| [`codex-cache-refresh`](codex-cache-refresh/SKILL.md) | Python 3.9+ with SQLite, compatible Codex desktop catalog, file permissions; `lsof` for automatic discovery. | Helper/tests are bundled. An independently verified `--db` path avoids `lsof`; keep real catalogs external and test with synthetic SQLite fixtures. |
| [`codex-cleanup`](codex-cleanup/SKILL.md) | Python 3.9+ with SQLite, scoped Codex data/runtime, filesystem and process/open-file inspection; macOS APIs for live pause/resume. | Audit, preservation, and fingerprint helpers are bundled. Add platform process adapters or a tested bounded watchdog; prefer offline maintenance when no watchdog is available. |
| [`context`](context/SKILL.md) | Python 3.9+, host file access, and the selected collection, assumed to be `~/Documents/Context` unless overridden; host directory switching only for loads. | Helpers, tests, and synthetic behavioral fixtures are bundled. Stop if the selected collection is unavailable; do not silently create it or choose another root. |
| [`create-chill-house-music`](create-chill-house-music/SKILL.md) | A DAW/renderer, licensed sounds or synthesis, audio validation and listening. Logic/GarageBand, AVFAudio/macOS, `afinfo`, or FFmpeg tools depend on the chosen route. | Guidance and the Python 3.9+ CAF inspector are bundled. Add an original WAV renderer/synthesizer and synthetic validation fixtures; never vendor proprietary loops or instruments. |
| [`file-cabinet-rename`](file-cabinet-rename/SKILL.md) | Host filesystem rename or OS `mv`; document/OCR support only when content cannot otherwise be read. | All naming rules are bundled. Add a standard-library preflight/rename helper; universal PDF/image/office extraction still needs additional support. |
| [`find-new-work`](find-new-work/SKILL.md) | Host file/search/edit tools and a target repository; its toolchain only when executing its checks/fixes. | The complete audit workflow is bundled. Synthetic project fixtures could test behavior without including a private project. |
| [`git-commit-with-message-and-push`](git-commit-with-message-and-push/SKILL.md) | Git, target repo, and an authorized remote; connectivity/authentication for nonlocal push. SSH tools/Keychain are conditional. | Formatting/review rules are bundled. Add a preflight wrapper and temporary local bare-remote tests; Git itself and remote hosting remain external. |
| [`git-repo-and-gitea-storage-reduce`](git-repo-and-gitea-storage-reduce/SKILL.md) | Python 3.10+, compatible Git; configured OpenPGP signing for rewrites; authenticated `tea`/Gitea admin access and verified datastore tools for the selected server route. | Read-only auditor, guarded dry-run rewrite helper, and synthetic Git/GPG tests are bundled. Keys, projects and servers stay external; pruning, force-pushes and global jobs require scoped approval. |
| [`gitea-issue`](gitea-issue/SKILL.md) | `tea`, an authorized Gitea account/repository, and connectivity for live operations. Supplied JSON can be inspected offline. | Add a standard-library REST adapter with mock-server tests to replace `tea`; Gitea and credentials must remain external. |
| [`latex-handbook`](latex-handbook/SKILL.md) | Python 3.9+, Pandoc; XeLaTeX or Tectonic plus TeX packages and Latin Modern fonts for PDFs. Poppler tools are optional verification dependencies. | Template/style/build wrapper are bundled. Pre-provision or vendor a licensed, checksummed toolchain/font/package bundle for offline builds; no such distribution is currently vendored. |
| [`leeloo-dallas-multiplan`](leeloo-dallas-multiplan/SKILL.md) | Configured independent reviewer CLIs/APIs, models and authentication; connectivity unless models run locally. | Slug and synthesis rules are bundled. Add a local reviewer adapter/config schema and mock reviewers. Local models still require a runtime/weights; single-agent output is not multi-model evidence. |
| [`little-snitch-unblock`](little-snitch-unblock/SKILL.md) | Python 3.9+, macOS APIs/system tools, licensed Little Snitch/CLI, existing Terminal access, and authorized privilege elevation for writes. | The helper is bundled. Add synthetic CLI export/readback tests; proprietary software and real firewall models are not distributable dependencies to merge. |
| [`lock-screen`](lock-screen/SKILL.md) | Python 3.9+, macOS Security/login APIs, `launchctl`, `ioreg`, process inspection, GUI session, and permissions. Optional legacy resources also need Swift. | The primary helper is bundled and does not need a personal installed command or Swift. Add mocked OS-boundary tests; private Apple frameworks remain OS components. |
| [`new-todo`](new-todo/SKILL.md) | macOS, Things 3, authorized [`things3-cli`](https://github.com/ossianhempel/things3-cli), and the current source-chat link. | User setup: `brew install ossianhempel/tap/things3-cli`, or follow upstream source-build instructions. The executable is `things`; stop if it or required readback permissions are missing. |
| [`plan-title-create`](plan-title-create/SKILL.md) | Only plan text and the host language model; no additional tools, packages, accounts, or network. | The full workflow and examples are bundled. A slug validator could be added, but is not required. |
| [`prepare-release`](prepare-release/SKILL.md) | Target project/toolchains/SDKs, Git, signing inputs and devices as applicable; authorized store/distribution tooling and connectivity for live verification. | Workflow/references are bundled. Add generic preflight/artifact-manifest helpers and synthetic distribution fixtures; never vendor signing keys, private projects, accounts, or store services. |
| [`wordpress-version-check`](wordpress-version-check/SKILL.md) | PHP, trusted WP-CLI, scoped WordPress files/database, current release/vendor metadata; SSH/Docker/Dokku only for relevant deployments. | Bundle a license-reviewed pinned WP-CLI PHAR with checksum/provenance and synthetic site fixtures. PHP, real site state, and live release sources remain external. |

All bundled Python helpers use the standard library plus other bundled local
modules, not pip-installed packages. System binaries, proprietary applications,
model runtimes/weights, and online services are **not** silently bundled,
installed, downloaded, or emulated. External documentation links are references,
not a substitute for the included workflow or a guarantee of current APIs.

## Installation

Copy a selected skill's **whole directory** into the agent's configured skills
directory, such as `~/.config/opencode/skills/` or `~/.codex/skills/`.
Review existing installed copies before replacing them. Resolve each bundled
helper relative to that installed skill's `SKILL.md`, not the chat directory.
The repository-level checker below is for maintainers and is not required to
use an individual skill.

Honor the host's permissions and available tools. Missing prerequisites should
produce a clear limitation, not trigger automatic installation, a permission
bypass, fabricated live results, or a silent switch to a different product.
Do not run a lock, firewall mutation, cleanup, upload, or other live action to
test installation.

## Privacy and anonymity

Published configuration is blank or illustrative. No family identities,
personal schedules, school/campus profile, private project names, infrastructure
inventory, listening history, real conversation IDs, credentials, or personal
source documents belong here. All fixture subjects are synthetic.

Keep real configuration, documents, Context collections, application databases,
recordings, generated reports, firewall exports, and release evidence outside
this repository. Use reserved example domains and explicit placeholders in
examples. The copyright holder's name in `LICENSE` is an intentional exception
to anonymization; the license terms remain unchanged.

This policy and the checker cover the **current source tree**, including
filenames and bundled resources. They do not anonymize `.git` history, author
metadata, remotes, GitHub account ownership, forks, caches, or previously
published versions. Removing an identifier from a working file does not remove
it from history. History rewriting/publication requires separate review and
authorization. Automated checks flag common patterns and known supplied terms;
they cannot prove that arbitrary prose contains no identifying information.

## Repository maintenance

Use Git history for skill maintenance; do not create or update per-skill
changelog files or entries. Repair obsolete links by using existing resources,
not by restoring deleted maintenance logs or creating empty placeholders. This does not
disable a skill's functional changelog requirements for external user data,
such as a context topic's history. See [repository guidance](AGENTS.md).

## Offline checks

The repository checker and tests use Python 3.9+ standard-library modules.
From the repository root:

```sh
python3 -B .scripts/check_repository.py
python3 -B -m unittest discover -s .scripts -v
python3 -B -m unittest discover -s context/tests -v
python3 -B -m unittest discover -s codex-cache-refresh/scripts -p 'test_*.py' -v
python3 -B -m unittest discover -s git-repo-and-gitea-storage-reduce/tests -v
```

The checker verifies local Markdown links, entrypoint/dependency-preflight-section
structure, per-skill resource boundaries, absence of top-level per-skill
maintenance changelogs, script syntax/import locations, and common privacy/credential or
machine-artifact patterns. It does not install dependencies, read live apps,
fetch external URLs, or execute bundled operational helpers.

These checks do not establish end-to-end agent compatibility, successful
authentication, deployment health, or behavior of external applications.
The storage-reduction fixtures require Git; signing cases use only temporary
synthetic keys and skip when `gpg`/`gpgconf` are unavailable. They never run
maintenance against a real repository or Gitea server.

## License

[BSD 3-Clause License](LICENSE).
