# Report Format

Use this structure unless the user requests a different presentation. A table is useful for exact time mappings and deduplicated comparisons; use bullets instead when the result is very small or table cells would become unreadable.

## Scope and cutoff

State:

- named location and geographic boundary;
- exact inclusive start and end in the location's timezone, including UTC offset when useful;
- when the sweep was completed;
- whether routine public events were included;
- the hybrid inclusion rule: in-window events plus in-window new developments/publications about older or future events.

Briefly explain any retained county/metro item and any excluded boundary area.

## Chronological deduplicated log

This section is for underlying events that occurred inside the window. Order by event time, not article time.

Recommended columns:

| Event time (local) | Distinct event | Verified details and timing note | Sources | Confidence |
|---|---|---|---|---|

For each entry:

- Use the most precise supported event time; write `time not reported` when needed.
- Explicitly distinguish `occurred`, `reported`, `published`, and `updated`.
- Name the relevant neighborhood/street/agency when supported and appropriate.
- Consolidate repeated background; mention when multiple reports were merged only if it helps explain deduplication.
- Cite direct pages next to the facts they support. Include multiple sources only for independent corroboration or unique facts.
- Use `High`, `Medium`, or `Low` under the skill's evidence rubric.

If an event occurred inside the window but was first published after it, retain it here and state the later publication time.

## New developments about older events

Order by the time of the new in-window development. State the older event date separately. Qualifying examples include a new identification, arrest, charge, filing, ruling, official correction, recovery, damage assessment, reopening, or policy response.

Do not retell the entire older incident as though it happened inside the window. Include only enough background to understand the new development.

## Publications about future events

Order by the in-window publication/announcement time, then show the future scheduled time. Include announcements, approvals, cancellations, warnings, closures, meeting notices, and other material new information. Apply the user's routine-events preference.

Do not place an event here solely because an old calendar page remained online during the window.

## Raw or unverified public signals

Include only signals that are geographically and temporally in scope and potentially useful. Recommended columns:

| Signal time | What the public source says | Why it remains unverified | Source |
|---|---|---|---|

Use careful labels such as `raw call entry`, `uncorroborated community report`, or `official alert with details pending`. Never silently upgrade these into confirmed events.

If raw-data volume is too high to enumerate accurately, summarize counts/categories only when the portal supports a reliable export or query. Otherwise describe the inaccessible or unextractable dataset as a blind spot.

## Remaining blind spots

Name concrete gaps, such as:

- source blocked, paywalled, login-only, robots-restricted, or temporarily unavailable;
- searchable portal verified but query/export could not be executed;
- outlet lacks timestamps or has stale indexing;
- social platform results are incomplete or not publicly visible;
- deleted/unindexed pages, print/broadcast-only reports, private groups, or unpublished calls;
- language/translation limitations;
- court/jail/public-record access unavailable in the jurisdiction;
- ambiguous event time or geographic boundary;
- the search ended before a fast-moving event was resolved.

Explain how each gap affects completeness. Do not write a generic disclaimer when a specific one is known.

## Completeness statement

Close with a calibrated statement such as:

> This is a best-effort inventory of distinct, publicly accessible and discoverable developments for the stated scope and window, deduplicated across the source families described above. It is not a guarantee that every event, call, post, filing, or offline report has been captured; the remaining known gaps are listed above.

Adjust the wording to reflect actual coverage. Never claim `all news`, `100% complete`, or `every incident` without an authoritative complete dataset that was successfully queried and validated.
