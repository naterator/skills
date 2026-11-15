# Comprehensive school briefing template

Use for a full school update. Read `../config.yaml` for the current profile and preferences. Replace placeholders with supported information, using the student's supported current grade rather than retaining an old template label. Scale detail to the supplied material; omit empty subsections and say briefly when no information is supplied for a child. Do not create filler or invent dates to complete the template.

The executive summary is the first substantive section. Confidence and material source limitations should be visible near the beginning. Focused answers and timeline-only requests use the relevant subset instead of the entire template.

```markdown
# School Update — [Current date in the configured school timezone]

## 1. Executive Summary

[The most consequential academic developments, near-term assessments,
assignments, schedule changes, parent participation, or issues. Identify
New / Updated / Continuing / Reminder only with an accessible baseline.
Include child/audience, dates where known, and why each item matters.]

Confidence: [High / Moderate / Weak, with topic-specific differences when useful].
[For a material gap or conflict, identify the affected conclusion and next
verification step. If no baseline exists, note limited change detection.]

## 2. Upcoming Timeline

| Date / day / time | Event | Child / audience | Preparation / action | Status |
|---|---|---|---|---|
| [Supported date, verified weekday, time if given] | [Event with source] | [Student name / Multiple students / Schoolwide] | [Actual action or labeled suggestion] | [Confirmed / Tentative / Conflicting / Inferred] |

### Date Not Provided

[Relevant undated events or assignments, sources, and clarification needed.]

## 3. [First Student] — [Supported current grade] Academic Update

### [Relevant subject]

[Current module/chapter/unit and lessons; topic or essential question;
skills, concepts, vocabulary; completed and newly introduced material;
documented progression; assessment/practice resources and source citations.]

[Required homework / Optional school-provided practice / Suggested home
practice, where useful. Reserve detailed test/project analysis for section 5.]

## 4. [Next Student] — [Supported current grade] Academic Update

### [Relevant subject]

[Current classroom material, reading/phonics, writing/grammar, mathematics,
science, social studies, developmental/social-emotional learning, or other
documented subjects. Describe actual skills and supported progression.]

[Required homework / Optional school-provided practice / Suggested home
practice, where useful, with citations and no invented performance claims.]

## 5. Upcoming Tests, Projects, and Study Recommendations

### [Student — assessment or project name]

[Subject, unit, scheduled/due date and status, actual coverage or objective,
teacher instructions, linked materials actually examined, and specific
study actions or project requirements. Cite the supporting pages/sections.]

[For projects: grading/summative status if stated, completion formats,
components, school/home work, planning resources, rubric categories,
verified points/percentages where useful, limitations, and parent support.]

[If a project deadline is missing:
"Deadline not provided in the supplied materials."]

[For conflicting dates, mismatched materials, missing instructions, or
rubric inconsistencies: both claims/sources, affected conclusion,
provisional preparation advice if useful, and a focused clarification.]

## 6. Parent Action Items

### Urgent

- [ ] [Action — child/audience — known deadline — reason — source or labeled suggestion.]

### This Week

- [ ] [Meaningful near-term action, with the same details.]

### Upcoming

- [ ] [Planning action, with the same details.]

## 7. Important School Notes

- [Consequential operations, changes, unresolved procedures, schedule
  effects, or safety/technology issues; child/audience and precise source.]

### Uncertainties and Clarifications

[Unresolved issues not already adequately explained. Identify each claim
and source, what remains unconfirmed, and the practical next step.]

## 8. Miscellaneous Observations

- [Less urgent but useful educational activities, parent learning,
  technology resources, conversation starters, allowed fundraising,
  enrichment, curriculum connections, contacts, communication patterns,
  or stale sections. Include only material with practical value.]

## 9. What I Would Prioritize Right Now

1. [Highest-value supported priority, with child/audience and timing.]
2. [Next priority.]
3. [Next priority.]
[Use 3–5 priorities when supported; fewer when fewer are justified.]
```

## Presentation decisions

- Keep all children and schoolwide events in one chronological timeline; split near-term and later tables only if it improves readability. Put time in the date cell only when supplied. Include sources in the relevant event cells or precise source notes without adding an unnecessarily wide column.
- Use one row for a disputed event, with its competing dates and sources together; sort by the earliest current candidate. Explain explicitly superseded dates in the detailed history rather than adding them to the upcoming table. Include only events affecting the family; secondary-only notices can be clarified briefly in school notes if needed.
- **Confirmed** means the school states the date without a relevant unresolved conflict; it is not a guarantee the event will occur. Use **Tentative**, **Conflicting**, or **Inferred** when appropriate, with an explanation. Never use a confirmation label to erase a discrepancy.
- Exclude expired events from upcoming rows unless they still require follow-up; clearly identify any such row as a past date with unresolved action.
- Cover all supported relevant subjects without mixing students. Keep detailed coverage, question types, rubric interpretation, and study actions in the assessment/project section so academic updates remain readable.
- Summaries, timeline rows, and final priorities may briefly point to the same consequential item; avoid repeating its full explanation. Explain each conflict fully once, normally in its assessment/project entry, and refer to that explanation from other sections. The uncertainties subsection is for additional unresolved issues, not another copy of the same disputes. Other unchanged routine announcements usually do not need another mention.
- Label recommendations and optional events clearly, including suggested preparation and parent support in checklists. Preserve the distinction between optional activities suggested by the school and practice added by the assistant. Every checklist item should tell the parent what to do and why. Empty urgency groups may be omitted.
- Limit miscellaneous observations to useful information. Keep material limitations specific, with affected conclusions, instead of generic disclaimers.
- Apply configured exclusions to every section and any appended source inventory. Cite the included factual claims with precise source/page/section references.
