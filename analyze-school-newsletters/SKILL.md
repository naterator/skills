---
name: analyze-school-newsletters
description: "Analyze school communications, newsletters, teacher emails, calendars, and academic materials for a configured family. Use for school updates, upcoming tests or assignments, home study guidance, parent priorities, timeline or date lookups, or changes between communications."
---

# Analyze School Communications

## Dependency preflight

Before analysis, verify that supplied school materials are available and
readable with the host's file/text or document/vision tools. PDFs or images
require a working reader/OCR route; linked-source verification requires
authorized browsing and connectivity. If a required capability or source is
missing, stop the affected analysis and request usable input or access. Do not
invent its contents or silently substitute generic academic advice. Missing
optional sources may be reported as gaps while available materials are analyzed.

Turn school communications into an evidence-based parent briefing that explains classroom learning, upcoming assessments, assignments, schedule changes, and meaningful parent actions. Prioritize academic development and preparation; consolidate repeated announcements without losing distinctions or uncertainty.

## Configuration and scope

Read [config.yaml](config.yaml) on every invocation. It contains the family profile, the school-local timezone, reporting preferences, and persistent topic exclusions. Use the configured profile only for its stated school year. Follow clear newer documents or user corrections; do not automatically advance grades or treat old grades as current indefinitely. Ask a focused question if student, grade, campus, or year uncertainty affects the analysis, and continue work that does not depend on the answer.

The public configuration intentionally has no family profile or exclusions. Obtain missing details from the supplied materials or the user when they affect the answer. Save personal defaults only in a private installed copy, not in this public repository.

Honor exclusions throughout every user-visible output, including summaries, tables, citations, source lists, action items, and saved reports. Do not mention topics merely to announce their exclusion. A user's explicit request about an excluded topic overrides only the relevant exclusion for that request. Apply exclusions to the specific topic, not unrelated content in the same document; lunch procedures and academic enrichment can still matter.

If `sources.default_directory` is configured, inspect that directory for relevant new or updated school materials during an ordinary analysis, along with any materials supplied in the request. Report an unavailable configured directory when it affects coverage. An explicit source-only request limits the analysis to the named source or sources and leaves the configured directory out; an explicit read-only request may inspect configured sources but must not write or update anything.

Choose the requested scope:

- **Comprehensive school update:** use [references/briefing-template.md](references/briefing-template.md), repeating the child-specific sections for each relevant student and covering schoolwide information.
- **Focused question:** answer the requested test, subject, project, changes, or priorities without producing an unnecessary full briefing. Keep a short executive takeaway and a confidence assessment.
- **Timeline or date lookup:** use the configured shared date index when it is in scope, together with relevant current sources. For a particular date, include each applicable event, deadline, and covering date range with its audience and status.

Accept single documents or large batches of newsletters, emails, announcements, PDFs, calendars, policies, photographs, screenshots, assignments, rubrics, study guides, reviews, practice assessments, and answer keys. No naming convention is required. Use supplied files, accessible task materials, and relevant available prior reports. If no usable source is available, request the relevant materials. Never ask the parent to repeat configuration already recorded here.

## Analyze the materials

### 1. Inventory and read

Build a working inventory of every source in scope: filename or identifier, type, sender or author, publication date, audience, student/grade, subject or administrative category, new versus historical role, and embedded or linked resources. Establish relationships such as email → newsletter → review packet → answer key or project → rubric. Record whether a referenced resource was supplied, accessed through a link, or remains unavailable; a mention of a worksheet does not mean its contents were examined. Do not equate a file's modification date with its communication date.

Read every relevant document completely. Use extraction to navigate, then inspect images wherever tables, calendars, diagrams, question layouts, small print, scans, or handwriting could change the meaning. For PDFs, use the available PDF workflow, text extraction, and page rendering; record physical page numbers for citations. Read academic packets and rubrics beyond their first pages.

Inspect relevant linked resources when they materially affect dates, coverage, instructions, or requirements and access is available. A visible URL or an email's attachment description does not establish the linked document's contents. Identify inaccessible, expired, unreadable, or missing material precisely. Continue with available evidence; request re-upload only when the gap materially affects the requested answer. Do not assume attachments from another conversation remain accessible.

### 2. Extract facts and preserve provenance

Track facts with their source, page/section, student or audience, subject, unit/module/chapter/lesson, relevant date, uncertainty, and any required action. Organize them into schoolwide announcements, each child's academics, assessments, assignments/projects, calendar/events, parent responsibilities, procedures, optional observations, and unresolved issues. One document may support several categories.

Use the school's actual communications and academic materials as primary evidence. Interpret authority in context: a teacher email, grade newsletter, schoolwide notice, official calendar, assignment instructions, rubric, or study guide may be most specific for different questions. Recency and specificity help assess support but do not automatically resolve a disagreement.

Separate **school-stated facts**, **reasonable inferences**, and **assistant recommendations**. Cite consequential claims, especially test dates, deadlines, assignment components, scoring, schedule changes, procedures, and conflicts. Use available document citations; otherwise identify the exact filename/title and physical page or section, with a verified clickable file link where supported. Cite both sides of a conflict. Never fabricate page numbers, source identifiers, links, or citations.

Routine analysis should not depend on external research. Use it when requested or needed to verify relevant public information, such as an official calendar. Prefer primary official sources, cite them, and label externally verified information separately. Do not replace school instructions with general educational advice.

### 3. Consolidate and compare

Create one consolidated entry per actual event, assessment, assignment, or procedure, retaining all relevant supporting and conflicting sources. Match by student/audience, subject, unit, purpose, and instructions rather than title alone. Preserve distinct subjects, units, modules, lessons, quizzes, retests, and projects. Similar names do not establish that two assessments are the same or that a later email cancels an earlier one.

Compare with accessible earlier communications or prior analyses when available. Identify newly announced work/events, rescheduling, cancellation, postponement, curriculum progression, changed procedures, resolved or continuing issues, and repeated announcements. Verify claims from prior summaries against raw sources where available. Do not label an item **New** merely because it appears in this batch. With no historical baseline, say change detection is limited and use neutral wording such as "In the supplied materials."

For supported comparisons, label **New**, **Updated**, **Continuing**, or **Reminder** where useful. Remove stale repetition unless it remains consequential. If records are requested, save or update the requested report/timeline in the authorized destination and preserve provenance; do not imply hidden cross-chat tracking or create an ongoing monitor. Persistent skill configuration changes require a user request to update it.

### 4. Reconcile the timeline

Determine the current date at execution time using the client's date/time context and the configured school timezone. If the timezone is unknown and changes the answer, ask rather than assuming. Include the as-of date. Resolve relative dates against the communication date and context, not automatically against today. Do not invent missing years, dates, times, or deadlines; clearly label justified inferences and keep unresolved dates unknown.

Verify each weekday against its calendar date. Preserve and flag a source's mismatched weekday/date instead of silently repairing it. Cross-check the academic calendar for each relevant school and grade when available. Distinguish regular instruction, student holidays, staff-development days, intervention days, early release, grade-specific changes, and extended breaks. Do not assume a recurring weekday is a holiday or transfer one grade's rules to another.

Classify events as past, today, upcoming, tentative, undated, expired, or needing follow-up. Put known-date upcoming events in chronological order; separate undated items. Give one event one timeline row, even when its date is disputed: put competing dates and their sources in that row, order it by the earliest live candidate date, and explain the conflict in the detailed entry. Keep explicitly superseded dates in historical context rather than as current timeline candidates. Include only audiences relevant to the actual supplied family profile; do not assume students' ages or grades. Omit expired events from the upcoming timeline unless an unresolved responsibility still makes them relevant, in which case identify the past date and follow-up explicitly. A scheduled date passing does not prove the test occurred, work was submitted, or an action was completed.

When dates, instructions, calendar scope, or arithmetic conflict, present every relevant claim with its source and explain what remains uncertain. An explicit correction can establish an update; retain any still-unresolved conflict. Explain which evidence appears more directly supported without declaring it automatically correct. Recommend a concrete clarification, and when useful suggest preparing by the earliest plausible assessment date. Do not send the clarification or change a calendar without authorization.

### 5. Explain academics and parent implications

Keep each child's curriculum and obligations separate. Cover reading/ELA, writing, grammar, mathematics, science, social studies, social-emotional/developmental learning, and other relevant subjects only as supported. For each relevant subject identify the current unit and lessons, topic or essential question, skills, concepts/vocabulary, completed and introduced material, assessments, available resources, and useful home practice.

Explain documented progression between editions: how the new lessons build on previous material, not just a list of lesson numbers. Do not substitute generic grade expectations for classroom evidence or claim a child's mastery, difficulty, grades, or test results without actual records.

When assessment materials, answer keys, or substantial projects are present, read [references/academic-analysis.md](references/academic-analysis.md). Prioritize near-term assessments, actual coverage and question types, study actions, project components, rubric scoring, and missing instructions. Preserve the student's ownership of the work.

Label **Required homework**, **Optional school-provided practice**, and **Suggested home practice** distinctly. School-suggested optional reading or activities belong under optional school-provided practice; reserve suggested home practice for the assistant's additions. Tie recommendations to identified classroom material. Explain what the child should be able to do and why a practice activity helps. Never turn a recommendation or an optional activity into an obligation, including when it appears in a checklist.

Translate relevant facts into a parent checklist grouped **Urgent**, **This Week**, and **Upcoming**. Each item needs a meaningful action, child/audience, deadline if known, and reason. Label optional suggestions. Include changes or unresolved issues in attendance, absence reporting, arrival/dismissal, safety, school portals, dismissal systems, lunch ordering, visitors, daily materials, weather procedures, and schedules where consequential. Avoid action items for routine announcements needing no parent involvement.

## Shared date index

When `records.dates_file` is configured, expand `~` against the current host's home directory and read the resulting file at the start of date-aware analysis and date lookup when it is in scope. On an ordinary review, merge newly evidenced dates only when the user has configured the file for persistence and the request does not limit work to supplied sources or prohibit writes. A source-only request leaves the index untouched. A read-only request may read it when in scope but must not initialize or update it. If persistence is in scope and the file is missing, initialize it at the configured path when its parent directory is accessible and writable; if it cannot be read or written, report that limitation and provide supported date changes in the answer.

- Use ascending school-local ISO date headings (`YYYY-MM-DD · Weekday`) with applicable entries beneath each. Record inclusive multi-day periods once in **Date ranges**; for a particular date, check both its heading and all ranges covering it.
- For each entry, record the event or finding, student or shared audience, grade or school year when relevant, time if known, status, and a precise source. Include due dates, tests, classroom and campus events, schedule or procedure changes, and substantive dated findings. Distinguish event, deadline, and announcement dates. Record a meaningful announcement on its known date when the event date is missing. Keep genuinely undated items out of dated entries.
- Merge repeat notices by event and audience. Reread the current file before saving, preserve unrelated entries and credible history, and mark corrections, cancellations, or conflicting dates explicitly with their sources. A past date alone cannot establish occurrence, attendance, completion, or results.
- Apply configured exclusions to the persistent reference. Keep it at the configured location rather than moving it into a source folder or per-chat workspace. Leave it untouched when the review adds no new evidence.

## Report and verify

Start reports with an executive summary as the first substantive section. Keep dates and comparisons in readable Markdown tables, action items in checklists, and explanations in short paragraphs. Use restrained emphasis for imminent tests and deadlines. Be detailed enough to replace reading the whole batch, while letting the parent quickly find the important developments.

Assess confidence as **High**, **Moderate**, or **Weak**, based on document completeness, agreement, clear dates/requirements, readable extraction, available historical context, and material gaps. Confidence can differ by topic. Below High, name the affected conclusion, its specific uncertainty, and the verification step. Do not imply a whole briefing is unreliable because one test date conflicts.

Before delivering, verify:

- Every relevant supplied document was examined; any missing or unreadable source is disclosed without invented contents.
- Dates, weekdays, current/past status, student/grade scope, and tentative or conflicting instructions are represented correctly.
- Each child's subjects and materials remain separate; documented subjects, upcoming assessments, substantial assignments, answer-key relationships, and rubrics are covered at the requested scope.
- Deadlines, coverage, scoring, results, and parent obligations have source support; recommendations and optional activities are labeled.
- Repeated announcements are consolidated, distinct assessments remain distinct, and change labels have an accessible historical basis.
- Consequential facts and both sides of conflicts have precise, real citations; uncertainty and confidence are specific.
- All configured exclusions are absent throughout the report unless explicitly requested; unrelated relevant content remains included.
- The output fits the request, avoids boilerplate and unnecessary repetition, and a full briefing ends with 3–5 highest-value priorities (fewer if fewer are supported).

If evidence prevents a check from passing, state the practical limitation and continue with supported conclusions. Do not compensate with assumptions. Do not schedule reports, monitor communications, register for events, submit forms, make payments, or message teachers unless the user explicitly requests the relevant action.

## Reuse and maintenance

Invoke as `$analyze-school-newsletters` (the public skill ID remains stable) or request a matching school analysis; automatic selection remains enabled. Examples:

- "Use $analyze-school-newsletters to analyze these newsletters and teacher emails."
- "Use $analyze-school-newsletters to tell me what my child should study for science."
- "Use $analyze-school-newsletters to show what changed and update our upcoming timeline."
- "Use $analyze-school-newsletters to tell me what is happening on December 16."

To update defaults, edit this skill's `config.yaml` or ask Codex to update the optional source directory, shared date-index path, family profile, school year, reporting preferences, or exclusions. Keep the stated school year with each grade and preserve unrelated settings. Adjust report layout in `references/briefing-template.md` and academic procedures in `references/academic-analysis.md` when requested.

## Dependencies and portability

All templates, reporting rules, and blank configuration are bundled. Analysis
of supplied readable text needs only the host agent; another skill is not
required. PDFs/images need host document/vision support or an optional local
extractor/OCR tool. If unavailable, request readable text rather than pretending
the source was examined. Browsing is needed only for relevant linked/live
verification. Keep real family configuration outside this public repository.
