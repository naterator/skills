# Dokku WordPress maintenance

These are discovery patterns, not a host inventory. Obtain the actual SSH
alias, account, app scope, and repository instructions from the user or their
private deployment configuration. Do not assume a username, port, or network.

## Access and discovery

Use the owner's existing authorized SSH configuration. For example, after
replacing the illustrative alias:

```sh
ssh -o BatchMode=yes -o ConnectTimeout=15 wordpress-host
```

Enumerate scoped applications with the installed Dokku CLI's supported
`apps:list` format. Inspect current containers and selected mount fields,
not complete environment data. Discover WordPress roots from files and
configuration, not hostnames or the presence of a persistent mount alone.
Include stopped apps in the reported inventory without starting them.

Typical container names are `APP.web.1`. A PHP buildpack deployment may use
`/app/webroot` and `/app/.heroku/php/bin/php`; persistent named storage may
live under `/var/lib/dokku/data/storage/`. These are examples: verify the
actual paths, runtime UID/GID, and update-persistence model before use.

For larger operations, send a reviewed script on SSH stdin instead of
stacking shell quoting. Use subprocess argument arrays, bounded timeouts,
and checked producer exit codes. A successful `tee` does not prove that an
SSH/update command succeeded.

## Temporary WP-CLI setup (separate authorization)

A missing trusted WP-CLI stops the site's audit/update workflow. Provide the
official sources below as setup guidance; do not download or install them
automatically. Use these steps only for an explicitly authorized setup task,
then rerun the skill's dependency preflight before maintenance.

Official sources:

- PHAR: `https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar`
- SHA-512: `https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar.sha512`

Download outside the public webroot into a unique task directory. Accept a
bare digest or checksum-file response only after parsing and validating the
128-character hexadecimal SHA-512 value; compare it with the actual download
before execution.

Copy the verified PHAR to a unique container temporary path and run as the
application's normal user. Example command shape:

```sh
docker exec -w VERIFIED_WORDPRESS_ROOT VERIFIED_CONTAINER \
  VERIFIED_PHP_PATH /tmp/TASK-WP-CLI.phar \
  --path=VERIFIED_WORDPRESS_ROOT --no-color core version
```

Replace every placeholder with verified values. Do not make WP-CLI run as
root just to avoid permissions. A root-owned temporary file in sticky `/tmp`
may need privileged exact-file cleanup; remove only this run's tools.

Keep real warnings and exit codes visible. Vendor dependency deprecations
are not necessarily site failures; do not silence production PHP errors.

## Preserve the site's deployment and commerce policy

Read the owning repository's instructions before maintenance. First-party
themes and MU plugins are distinct from downloaded core/plugins. Determine
whether runtime state is persistent or image-baked; do not rebuild, deploy
unrelated custom code, or restart a healthy app merely to update WordPress.

Create backups only when separately authorized. Check existing backup
metadata if useful, but do not claim restore validation from metadata alone.
Preserve payment connections, launch/indexing settings, catalog organization,
accounts, owner content, activation, and auto-update choices.

After WooCommerce updates, run its supported database migration when needed
and verify no migration remains pending. A focused storefront check can
read the homepage, a product, cart, and contact page without writes.

## Directory version anomalies

A plugin reporting **version higher than expected** should not be
automatically downgraded. Compare its installed header/readme, official
directory API, version-specific checksum manifest, and official source
metadata. Published checksums may exist even if a versioned ZIP or directory
entry is temporarily unavailable. Preserve a newer verified version rather
than overwriting it to match stale metadata; report remaining uncertainty.
