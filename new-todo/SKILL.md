---
name: new-todo
description: Add a to-do or timed reminder to Things using the local things CLI, with a link to the originating Codex or ChatGPT chat in its notes. Use when the user asks to add an item to Things or invokes new-todo with an item and time. Untimed items go to Inbox; scheduled items appear in Today or Upcoming.
---

# New Todo

## Dependency preflight

Require macOS, an installed Things 3 app, and the `things` executable from
[ossianhempel/things3-cli](https://github.com/ossianhempel/things3-cli).
Verify `command -v things`, its current help/version, and authorized CLI
readback access before creating a task. Read commands require access to the
user's Things database, normally Full Disk Access for the terminal/agent host.
Updates additionally need the CLI's existing Things URL authorization.
Require a verified source-chat link as described below. If a dependency,
permission, or link is missing, stop before writing and report it; do not
silently use another task store, change permissions, or install software.

### Get the Things CLI

The upstream repository documents this Homebrew installation:

```sh
brew install ossianhempel/tap/things3-cli
```

Alternatively, follow its source-build instructions (`make install` from a
checkout, with the upstream build prerequisites). These are setup instructions
for the user, not commands to execute automatically during a reminder request.
After installation, verify that the `things` command is on `PATH` and that its
read commands work with the user's existing Things app and permissions.

Create the requested Things item using the installed `things` CLI. Include a link back to the originating chat in every item's notes. A request to create the item authorizes this action; do not ask for routine reconfirmation.

## Inputs and timing

- Extract the item from the user's words or clear conversation context. Accept natural requests such as `$new-todo review the draft at 4pm today`.
- Resolve the date and time against the current client clock and timezone. Use an explicit date and 24-hour time for the CLI. If the user provides a different timezone, convert to the Mac's local timezone because Things interprets its reminder times locally.
- With only a clock time, use today when that time is still ahead. Clarify if the intended time is already past or the date is materially ambiguous; do not silently move an explicitly requested "today" to tomorrow.
- If no schedule is requested, create an untimed Inbox item. If the user requests an alert but supplies no usable time or context, ask for the time.

## Placement in Things

By default, leave the item unfiled: do not choose a project, area, or tags unless requested.

Things adds an unscheduled, unfiled item to **Inbox**. Setting `--when` schedules it into **Today** or **Upcoming**, including when a reminder time is supplied. For a timed request, preserve the requested alert and briefly state the actual location. Do not promise that a timed item remains in Inbox. If the user specifically insists on keeping it in Inbox, explain the conflict and let them choose between Inbox placement and a timed alert.

## Link to the originating chat

- Use a known private conversation link or the app's current thread metadata. For a local Codex chat, read the current `CODEX_THREAD_ID` environment variable and use `codex://threads/THREAD_ID`. Resolve a missing or ambiguous identity through the available thread tools, matching the current chat; do not choose another chat merely because it is recent.
- For a ChatGPT conversation, use its observed conversation URL or the verified conversation ID in `https://chatgpt.com/c/CONVERSATION_ID`. Do not substitute a Codex thread ID into a ChatGPT URL. Prefer an existing app-provided link when available, especially for a remote chat.
- Add any concise context needed to recognize the task, followed by `Source chat: CHAT_TITLE` when the title is known, and the full chat URL on its own line. Keep user-supplied notes intact.
- Use a fresh originating link on each invocation; never reuse a previous conversation's ID. Do not create a public share link or publish a transcript to get a backlink. If the current chat cannot be identified reliably, ask for its link before creating the item.

## CLI-only workflow

Use `things` for **all Things reads and writes**. Do not use computer use, browser automation, AppleScript, or direct database access to operate or verify Things. The CLI itself may launch Things to deliver its command; this is expected.

1. Locate the executable with `command -v things`; do not assume an installation path or version. Consult `things add --help` and the relevant read command's help before relying on its flags or output schema.
2. Check for an existing item with the same title, chat link, and schedule before retrying an uncertain creation. Use `things search --json -- 'TITLE'` and inspect only relevant results. Preserve a deliberately requested separate item.
3. Create one item with `things add`, passing the notes and, for a timed request, `--when='YYYY-MM-DD HH:MM:SS'`. Omit `--when` for an Inbox item. Do not set a deadline as a substitute for a reminder.
4. Read back the result with `things search`, `things inbox`, `things today`, or `things upcoming`, using JSON and a title search. Record its UUID and check the exact title, source link, scheduled date, and actual list when exposed. A successful URL dispatch alone does not prove that Things saved the item. If the item is not visible yet, make a bounded readback retry before attempting another write.
5. Confirm the item, requested local reminder time, and actual location concisely. A Things link may use the verified UUID: `things:///show?id=UUID`.

Example command shapes, with values supplied safely:

```sh
things add --notes='NOTES_WITH_CHAT_LINK' -- 'ITEM'
things add --when='YYYY-MM-DD HH:MM:SS' --notes='NOTES_WITH_CHAT_LINK' -- 'ITEM'
things search --json -- 'ITEM'
things today --json --search='ITEM'
things upcoming --json --search='ITEM'
things inbox --json --search='ITEM'
```

Use argument arrays or correct shell quoting for real user text. The `--` before the title prevents titles from being interpreted as flags. The installed CLI accepts the space-separated date/time format above; its validation rejects `YYYY-MM-DD@HH:MM`, even though the underlying Things URL scheme documents that form.

## Verification limits and failures

- The current CLI's list JSON exposes the scheduled date and notes, but not the exact alarm time; `things show --json` is even more limited. Check any alarm field if a newer CLI exposes one. Otherwise confirm the submitted time and saved date without claiming an independently verified alarm time. Do not open the interface to fill this verification gap.
- If sandbox restrictions prevent the CLI from launching Things, use the normal permission mechanism for the same authorized CLI action. Before retrying an uncertain result, check whether the item already exists.
- If the CLI or Things is unavailable, or access is denied, report the concrete blocker. Do not install software, change permissions, write the database, or fall back to UI automation on your own.
- A follow-up correction to the item just created should use its verified UUID with `things update`, preserving unrelated notes. Consult its help and existing authorization setup; never print or embed an authorization token in the skill or tool output.
- Do not create a second reminder through Codex automations, Calendar, or another app unless requested.

Reference: [Things URL scheme](https://culturedcode.com/things/support/articles/2803573/) documents scheduling and Inbox behavior. Prefer the installed CLI's help for its accepted argument syntax.

## Dependencies and portability

Real task creation/readback requires macOS, Things, a compatible authorized
`things` CLI, and the current source-chat link supplied by the host/user.
No personal task database, conversation identifier, or other skill is bundled
or required in advance. A local adapter around Things' supported URL/automation
interfaces could replace the CLI only if it also provides adequate readback.
A local JSON task store would be a different destination and needs explicit
user agreement; it must not be presented as a Things reminder.
