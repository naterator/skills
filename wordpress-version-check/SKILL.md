---
name: wordpress-version-check
description: Check installed WordPress core and plugin versions against current stable releases on the user's scoped sites or Dokku host. Use to audit update status or bring WordPress sites up to date when updates are authorized, then verify integrity and site health.
---

# WordPress Version Check

## Dependency preflight

Require an authorized, verified site scope, accessible WordPress files/database,
the site's PHP runtime, and an existing compatible trusted WP-CLI. Remote
routes additionally require configured SSH access and any actual Docker/Dokku
tooling; illustrative buildpack/storage paths are not installation facts.
Latest-version and checksum checks need working official/vendor sources.
If a required tool, file, credential, endpoint, or permission is missing, stop
the affected site's operation and report it. Do not assume another host,
silently install/download WP-CLI, or treat cached/offline versions as current.

Discover the scoped WordPress installations, compare core and every installed
ordinary plugin with current stable releases, and report or resolve outstanding
updates according to the user's request. Never treat an unchecked or unreachable
site as current.

## Scope and authorization

- Use the user's explicitly scoped sites or configured Dokku host. If no scope
  can be established, ask before connecting or enumerating applications. Use
  SSH/CLI, not native desktop computer use. Read
  [the Dokku reference](references/dokku.md) for deployment discovery patterns;
  it contains examples, not a real host inventory.
- A bare invocation, version/status check, or audit-only request checks and
  reports without replacing code or migrating databases. Refreshing WordPress
  update transients is part of checking.
- A request to update, bring current, or **make sure the sites are up to date**
  authorizes ordinary stable core/plugin updates and their required database
  updates in the same run. Continue without asking again for that authorization.
  Honor explicit check-only wording and version constraints.
- Do not expand maintenance into theme updates, OS/PHP/Dokku upgrades, catalog
  refreshes, custom-code deployments, account changes, or scheduling unless
  requested. Preserve plugin activation, auto-update preferences, site settings,
  and first-party/MU plugins.
- Follow the site's backup instructions. Do not automatically create database
  dumps, archives, backup tags, or page copies without authorization. An audit
  or update request does not itself request a new backup. Existing backup
  metadata may be checked without launching a backup.

## Discover the actual installations

1. Enumerate all scoped Dokku apps, including stopped apps. Inspect current web
   containers, state, images, and mounts without printing environment variables
   or database credentials. A stopped app still needs a result or an explicit
   limitation; do not silently omit it or start it just to audit it.
2. Detect WordPress from its files (`wp-load.php`, `wp-includes/version.php`, and
   configuration location), not the hostname. Inspect both container files and
   persistent webroots so apps without mounts are not missed. Shared roots or
   databases should not receive duplicate updates. Discover nested/alternate
   document roots from the app's web configuration when necessary.
3. Confirm the root, PHP executable/version, runtime UID/GID, persistence, and
   canonical home URL. Read applicable repository/host instructions. For code
   baked into an image, use its source/deployment workflow; editing the running
   container alone does not establish a persistent update.
4. Use an existing trusted WP-CLI. If it is unavailable, stop and provide the
   official setup source; obtaining a PHAR requires a separate setup request
   and checksum verification before execution. Run it with the app's PHP, working
   directory, and runtime user. Temporary tools belong outside the public root;
   record their exact paths and remove only those tools after the run, including
   on failure. Files copied as root may require root for cleanup.

## Check current releases

Use a WP-CLI command prefix appropriate to the live app; the following commands
assume its working directory/path already points to WordPress:

```sh
wp core version
wp eval 'wp_clean_plugins_cache(); wp_update_plugins(); wp_version_check();'
wp core check-update --format=json
wp plugin list --fields=name,status,version,update,update_version,auto_update --format=json
wp plugin update --all --dry-run
```

- Include active, inactive, and network-active ordinary plugins. Identify MU,
  custom, premium, and private plugins separately. Do not use `--skip-plugins`
  for the authoritative update check: vendor update hooks may be needed. Use it
  only to diagnose a bootstrap failure, which remains a reported limitation.
- Determine the latest stable core from the live WordPress update response and
  [official version API](https://api.wordpress.org/core/version-check/1.7/) or
  [release archive](https://wordpress.org/download/releases/). Do not freeze a
  version number in this skill, choose a beta, or call an old branch's newest
  patch the latest overall release.
- Check core/plugin PHP and WordPress requirements against the actual runtime.
  If the latest release requires an out-of-scope runtime/deployment change,
  report the installed version, target, and exact blocker. Do not force an
  incompatible update or claim the site is fully current.
- No offered update is evidence from the configured update channel, not proof
  that an unlicensed/private plugin is current. Inspect vendor metadata or the
  owning source when needed; report unavailable checks accurately.
- Confirm that fresh update metadata was actually obtained. WordPress update
  functions can return after a failed HTTP request without a command failure;
  an empty/stale transient or a recent `last_checked` timestamp alone does not
  prove success. Inspect the response or compare directly with the official or
  vendor API when needed, and mark failed lookups inconclusive.
- A plugin reported as **version higher than expected** must not be downgraded
  automatically. Compare its header, official directory/API metadata, available
  packages, and version-specific checksum manifest. Published checksums can
  exist even when a versioned ZIP or directory metadata is missing. Report the
  discrepancy; do not infer tampering or overwrite a custom build from its
  version string alone.

## Apply authorized updates

Capture concise before versions, activation/auto-update state, a public page
health baseline, and any settings relevant to the affected site. These checks
are not permission to make a backup or collect customer records.

Before replacing code, verify the targeted core/plugin files against available
official checksums as described below. Investigate unexpected modifications
first. If a deployment, update lock, or maintenance operation is already active,
leave it intact and resolve that concurrency before changing the site. Preserve
maintenance mode that predates this run; remove only a mode left by this run.

Work through one site and update group at a time. Choose the update order from
compatibility and plugin dependencies. Apply only available, scoped updates.
Typical WP-CLI operations are:

```sh
wp plugin update PLUGIN_SLUG
wp core update
wp core update-db
```

Update inactive plugins too. `wp plugin update --all` is appropriate when all
offered updates are in scope and compatible. Omit `--minor` when the request is
for the latest stable core overall; honor an explicit branch/version constraint.
Use the appropriate network database update for multisite installations.

After a WooCommerce update, inspect its installed CLI and database update state.
Run `wp wc update` when required, then confirm the database version is current
and no WooCommerce database update remains pending. Plugin file replacement
alone does not complete a required database migration. Preserve store launch,
payment gateway, and search-indexing settings.

On an update failure or new fatal error, stop further changes to that site and
diagnose the failing step before any retry. Inspect live versions/state after a
timeout before rerunning a mutation. Report unresolved sites and continue with
independent sites when useful. Do not automatically roll back a database over
later orders or owner edits.

## Verify and report

- Refresh update metadata after changes; reread core and plugin versions and
  run the update dry run. Confirm core database schema status, any required
  plugin migration, and absence of leftover maintenance mode.
- Verify core with `wp core verify-checksums` and ordinary directory plugins
  with `wp plugin verify-checksums --all --strict`. For unchanged sites, one
  successful checksum check is enough. Recheck changed components after updates.
  Distinguish unsupported/private checksum sources from actual mismatches.
  Investigate unexplained changes before overwriting anything. A straightforward
  missing standard release file can be restored from the exact official release
  after checking its published checksum.
- Check each WordPress homepage and login page over HTTPS, following expected
  redirects. For an affected store, check a product, cart, and relevant contact
  page without submitting forms, creating orders, or exercising payments.
  Compare status/content with the baseline and inspect relevant errors if a
  regression appears; HTTP 200 alone is not sufficient when it contains a fatal,
  database, or maintenance message.
- Confirm app/container health, preserve plugin state and relevant settings,
  and remove temporary maintenance tools. Do not claim transactional, email,
  payment, or restore testing from these read-only health checks.

Report the number of scoped apps and WordPress installations, each site's core
version and update status, plugin before/after versions for applied updates,
verification results, and any blocked/unverifiable checks or version anomalies.
Keep the reply concise; save a detailed inventory only when useful. Do not call
the entire estate current while any scoped installation remains unchecked.

Official command references: [core update](https://developer.wordpress.org/cli/commands/core/update/),
[plugin update](https://developer.wordpress.org/cli/commands/plugin/update/),
[core checksums](https://developer.wordpress.org/cli/commands/core/verify-checksums/),
[plugin checksums](https://developer.wordpress.org/cli/commands/plugin/verify-checksums/).

## Dependencies and portability

The audit/update workflow and Dokku discovery reference are bundled. Execution
requires scoped WordPress files and database, PHP, a compatible trusted WP-CLI,
and current release/vendor metadata. SSH, Docker, and Dokku are conditional
deployment tools, not universal prerequisites. Checks against latest releases
need connectivity; offline snapshots cannot prove currentness. No private
server inventory or other skill is required. A licensed, version-pinned
WP-CLI PHAR with checksum/provenance and synthetic site fixtures could be
vendored; PHP, the real installation, and upstream release services remain
external.
