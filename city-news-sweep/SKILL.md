---
name: city-news-sweep
description: Perform an exhaustive, deduplicated public-news sweep for a city or other locality over a specified timeframe. Use for comprehensive recent-local-news requests that require mainstream, hyperlocal, official, public-safety, civic, institutional, incident, and community sources; do not use for a simple lookup of one known story.
---

# City News Sweep

## Dependency preflight

A live sweep requires functioning host web search/browsing, network access,
and public sources for the requested locality/timeframe. Verify these before
starting the sweep. If they are unavailable, stop and report the missing
dependency; do not present supplied archives or prior knowledge as live research.
Analyze an offline corpus only when that scope is requested or accepted by the
user. Individual inaccessible sources remain explicit coverage gaps.

Build the most complete defensible record of distinct public developments for the requested place and time. Browse live sources, reconcile event time with publication time, and make gaps explicit. Never claim literal completeness when inaccessible, unindexed, deleted, paywalled, login-only, or nonpublic material may exist.

## Inputs and defaults

Resolve these before searching:

- `location` (required): city/locality plus state, province, region, or country when needed for disambiguation.
- `timeframe` (required): an absolute start/end or a relative period such as `last 48 hours`.
- `geographic scope` (optional): `city proper`, selected neighboring jurisdictions, county, metro, or another user-defined boundary. Default to city proper, while retaining county or regional actions that directly affect it.
- `routine public events` (optional): `include` or `exclude`. Default to excluding ordinary calendar listings, entertainment listings, and recurring activities unless they caused a material development. Always include consequential public meetings, closures, warnings, disruptions, or institutional actions.

Translate relative times into exact local timestamps using the location's timezone and state the resulting inclusive window. Use the user's stated reference time when given; otherwise use the actual retrieval time. Ask only when the locality or timeframe cannot be resolved safely. State any geographic judgment calls.

Unless the user narrows the basis, use a hybrid inclusion rule:

1. Include events that occurred inside the window, even when first reported later.
2. Include material new developments published or officially recorded inside the window about events that began earlier.
3. Include future events only when their announcement, approval, cancellation, warning, or other newsworthy development fell inside the window.
4. Do not pull an old event into the main log merely because an article was cosmetically updated or republished inside the window.

## Research workflow

Read [references/source-strategies.md](references/source-strategies.md) before conducting the sweep. Read [references/report-format.md](references/report-format.md) before drafting the result.

### 1. Establish a source map

Identify the locality's actual outlets and agencies before treating search results as coverage. Cover every applicable family in the source-strategy reference. Record which sources were checked, their freshest visible update, and any access or indexing limitation.

Search in the locality's common languages and with relevant alternate names, abbreviations, neighborhoods, counties, landmarks, agencies, and demonyms. For recent windows, inspect source landing pages and feeds directly; general search results alone are insufficient.

### 2. Sweep broadly, then verify narrowly

Use aggregators, search engines, social search, and cross-source queries to discover candidates. Open the underlying story, official notice, agenda, docket, alert, or post whenever possible. Prefer direct and primary sources in citations; use an aggregator or search snippet as evidence only when the original is unavailable, label that limitation, and lower confidence.

Run date-aware and site-specific searches across the full window, plus a small buffer on each side to catch late reports, timezone mismatches, and updates to older incidents. Recheck high-velocity sources such as breaking-news feeds, public-safety alerts, road closures, weather warnings, and official social accounts near the end of the sweep.

Keep a candidate ledger while researching. For each candidate, capture:

- underlying event or action;
- precise location and geographic relevance;
- event time, first-known time, publication time, update time, and future scheduled time when available;
- sources and what unique facts each contributes;
- verification state and uncertainty;
- correct output section.

### 3. Apply time and evidence rules

Do not substitute publication time for event time. When either is unknown, say so. If sources conflict, report the conflict rather than manufacturing precision.

Treat police statements, court filings, arrest affidavits, bookings, charges, and allegations as claims or procedural actions, not proof of guilt. Distinguish a new arrest, filing, identification, recovery, ruling, or official correction from the older underlying incident.

Separate raw dispatch/CAD entries, scanner reports, crowdsourced maps, uncorroborated eyewitness posts, and community social posts from confirmed reporting. They may be useful leads, but do not merge them into a confirmed entry until corroborated. Do not infer an event from a code or terse dispatch label beyond what the source actually states.

### 4. Deduplicate by the underlying development

Merge reports when they describe the same real-world event or official action, using location, actors, time, incident identifiers, and narrative details—not headline similarity alone.

- Keep one entry for syndicated, rewritten, or repeatedly updated coverage of the same development.
- Preserve citations to the strongest source and any other source that contributes a distinct fact or independent corroboration.
- Split omnibus articles when they contain multiple unrelated events.
- Keep separate entries for materially distinct developments in the same case, such as an incident, later arrest, court filing, and sentencing.
- Do not collapse similar but separate calls, crashes, meetings, outages, or crimes.
- Note meaningful discrepancies in names, times, counts, locations, or status.

### 5. Assign confidence

Confidence describes evidentiary support, not importance or certainty about a person's guilt:

- **High:** a direct authoritative record/source, or multiple credible independent sources with consistent material facts.
- **Medium:** one credible local report with attributable sourcing, or an official statement that lacks enough detail or independent corroboration.
- **Low:** an inaccessible original represented only by a snippet/aggregator, a raw public record whose meaning is unclear, or an uncorroborated social/community report.

Do not inflate confidence merely because many outlets copied the same report.

### 6. Stop only after a coverage audit

An exhaustive sweep is ready to report when:

- every applicable source family has been checked or listed as a blind spot;
- multiple broad, source-specific, neighborhood/agency, and alternate-language queries stop producing unseen candidates;
- each candidate has been included, deduplicated, excluded with a reason, or placed in the raw/unverified section;
- the exact time and geographic boundaries have been applied consistently;
- high-velocity sources have received a final freshness check; and
- remaining access, indexing, data-extraction, language, and source-availability gaps are documented.

## Reporting requirements

Follow the report-format reference. Lead with the scope and exact cutoff, then provide a chronological deduplicated log. Use direct Markdown links as citations adjacent to the claims they support. Give each entry a confidence label and make event, publication/update, and scheduled times visibly distinct.

Always include separate sections for:

1. new developments inside the window about older events;
2. publications or announcements inside the window about future events;
3. raw or unverified public signals, when any were found; and
4. remaining blind spots and completeness limitations.

If a required section has no qualifying items, say `None found` rather than omitting it. Keep source-faithful detail, but do not repeat the same background in multiple entries. End with a calibrated completeness statement describing what the sweep did and did not cover.

## Dependencies and portability

Source strategies and report structure are bundled; no other skill is needed.
A live sweep requires host web search/browsing, network access, and accessible
public sources. Supplied local articles can be analyzed offline, but that is
an archive analysis, not a verified current sweep. A local feed/search adapter
and synthetic HTML/feed fixtures could reduce connector dependence; they
cannot provide new reporting without external sources.
