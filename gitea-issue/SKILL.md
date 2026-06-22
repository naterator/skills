---
name: gitea-issue
description: Work with open Gitea issues through the `tea` CLI from a project directory. Use when the user asks Codex to list open issues, fetch or read a specific issue by ID, inspect an issue's title/description/patch section, prioritize issues by adding or replacing a `[PX] ` title prefix, edit issue titles, close issues, or decide whether to apply an issue's markdown patch section to the current codebase.
---

# Gitea Issue

## Overview

Use `tea` from the current project directory to inspect and manage Gitea issues. Issue detail output is JSON; the important fields are the issue title and markdown description. Issue descriptions follow a fairly consistent format and end with a patch section that can be applied to the codebase if the user chooses to move forward.

## Commands

List open issues:

```bash
tea i ls -f index,title,url -o json --limit 100 -p PAGE
```

Fetch one issue as JSON:

```bash
tea i ISSUE_ID -o json
```

Close an issue:

```bash
tea i close ISSUE_ID
```

Edit an issue title:

```bash
tea i edit ISSUE_ID -t "TITLE"
```

## Listing Issues

When the user asks for a listing of issues, list open issues with page numbers starting at `1`. Use the `tea i ls` command with `--limit 100`; fetch more pages only when the user asks for more or the task requires it.

Present each issue by issue ID and existing title. Use the issue ID as the primary reference, not a sequential list number. Include the URL only when it is useful for the user request.

## Reading an Issue

When the user asks to inspect or pull in an issue, run:

```bash
tea i ISSUE_ID -o json
```

Parse the JSON structurally. Extract the title and description. Treat the description as markdown. Summarize the issue intent and identify the patch section at the bottom of the description. Do not apply the patch unless the user has asked to implement, apply, or move forward with the change.

Before applying a patch, compare it against the live codebase and existing worktree state. If the patch is stale or conflicts with current code, adapt the implementation to the current code rather than blindly applying text.

## Prioritizing Issues

Issue titles should ideally start with a priority prefix:

```text
[PX] Existing title
```

`X` is the priority integer chosen by the user. When the user asks to adjust an issue priority:

1. Fetch or use the current title.
2. If the title already starts with a `[PX] `-style prefix, replace only that prefix.
3. If the title has no priority prefix, prepend the new prefix.
4. Update the title with:

```bash
tea i edit ISSUE_ID -t "[PX] Title without old priority prefix"
```

Preserve the rest of the title exactly unless the user explicitly asks for wording changes.

## Closing Issues

When the user asks to close an issue, run:

```bash
tea i close ISSUE_ID
```

Only close issues the user explicitly identifies or clearly authorizes closing.
