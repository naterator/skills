---
name: create-chill-house-music
description: Compose, arrange, produce, and revise chill-house music from a sonic brief or listening references, including Logic Pro and offline audio workflows. Use for creating or improving finished music; not for merely labeling a genre or adding an audio player.
---

# Create chill house music

## Dependency preflight

Audio production requires an available, authorized DAW or actual offline
renderer, usable licensed sounds or synthesis, and suitable output-validation
tools. The bundled Python 3.9+ CAF inspector is metadata-only, not a renderer.
A Logic/Apple route additionally needs the selected installed instruments,
loops, and applicable macOS/AVFAudio APIs; `afinfo`, `ffmpeg`, and `ffprobe`
are required only when the chosen route uses them. Verify the selected route
before rendering. If a required tool, asset, license, or capability is absent,
stop production and report it. Do not assume a private processor exists,
install/download replacements, or present a score as finished audio.

Make finished, listenable music with a relaxed house groove. A score, a MIDI export, an instrument inventory, and passing signal checks are supporting work; the principal deliverable is the rendered music.

## Establish the sound

Use the user's references and actual audition feedback as the brief. Genre definitions describe a range, not a formula that guarantees the requested sound. Preserve named favorites and concrete dislikes across revisions.

For genre interpretation or a project with prior failed attempts, read [genre and listening lessons](references/genre-and-listening-lessons.md). It includes reusable production lessons, not a past user's listening history or approvals for the current project. Obtain reference tracks from the current brief. Use the current user's actual feedback to preserve accepted instrumentation, pulse, beat foundation, and percussion balance; distinguish direction approval from completed-file verification.

When audio access permits, examine or audition authorized reference excerpts. Separate what was heard, what was measured, and what is inferred from metadata or descriptions. Never claim to have listened when only filenames, waveform statistics, or artist pages were available. Do not copy a reference recording, topline, lyric, or melody into the deliverable.

## Build a convincing production

- Start from a coherent groove: an unhurried four-on-the-floor kick, a solid, present snare/clap backbeat on two and four, rounded bass, restrained upper percussion, and a short melodic idea. Roughly 110–124 BPM is a useful starting range, not a mandatory genre boundary.
- Let atmosphere and space come from sustained harmony, performance detail, and a few complementary sounds. Extra notes, bright arpeggios, layered effects, or louder mastering cannot repair a weak musical idea.
- Use expressive instrument performances. Native multisampled instruments can help, but repeatedly pitching one guitar or piano sample does not recreate a player. Recorded phrases can supply articulation and musical continuity that a note grid lacks. Arrange and process licensed source material into a distinct musical work.
- Check actual harmonic compatibility between recorded parts. Matching key/tempo labels are useful search filters; they do not prove that bass and chords follow the same progression. Prefer project-matched verse/chorus families or related stems from one factory project when available; they are often a stronger starting point than unrelated loops in the same key. Still verify voicings, phrase starts, downbeats, and the actual verse/chorus role. A suffix such as `01` or `02` is not proof of verse, chorus, or any other section role.
- Make the main phrase feel intentional against the pulse. Offbeat hats and syncopated bass are normal house vocabulary. An accidentally late lead caused by slow attack, uncalibrated processing latency, or mismatched phrase starts is a different problem. Fix the demonstrated problem without flattening every part onto quarter notes.
- Keep a solid, present kick and backbeat when that is the requested house sound. Relaxed harmony and sparse upper percussion do not imply weak snare hits or a barely audible beat. Match foundation strength and decorative density separately; a sparse hat treatment must not weaken the kick or snare/clap body.
- Keep upper percussion subordinate to the requested mood. Continuous sixteenth-note hats/shakers can sound cheap or distracting; use fewer events, softer transients, less high-frequency energy, and actual gaps when the listener asks for a calmer pocket. Preserve a demonstrated accepted direction rather than assuming a past user's preference or banning every upbeat or syncopation.
- Preflight every drum variant used anywhere in the catalog before rendering: verify its raw source identity/hash, role mapping, routing, envelope/length, gain/headroom, and mono/phase behavior. Pin the raw drum hashes in provenance; a variant filename or number is not a substitute for inspection.
- Write an extended arrangement with real part-level dropouts, contrasting passages, and changed returns. A long file containing unchanged repetition or a global volume ramp is not a developed song. Carry harmony deliberately across section boundaries, and validate an actual section duty/dropout map rather than trusting layer names or metadata alone.

If using Logic, its factory content, Apple Loops, or a native/offline renderer, read [Logic and offline production](references/logic-and-offline-production.md). It covers source discovery, project-matched audio families, audio-versus-MIDI loop inspection, native API pitfalls, source hashes, mastering, and licensing. The standard-library helper `scripts/inspect_apple_loop.py <file.caf> ...` reports CAF format, musical metadata, decoded-frame duration, inferred tempo, audio/MIDI chunks, source channel count, whether the source is stereo, and SHA-256 without playback. Audio-only metadata does not prove a human performance, natural stereo width, or harmonic compatibility. Use a quiet native offline processor when possible; do not claim an offline EXS render was a Logic session or bounce.

## Iterate on sound, not descriptions

Create a few representative excerpts early when that will avoid scaling a rejected sound across a catalog. Include enough of the main groove and a contrast/return to reveal the production direction. Present usable audio files and identify the revision. React to feedback with audible changes to timbre, rhythm, performance, balance, or arrangement; renaming the style or changing a random seed is not a substantive revision.

When a preview is broadly accepted and one detail is criticized, preserve its accepted tempo, key, performance and balance while correcting that detail. The source loop’s native BPM is not automatically the right tempo for an already-liked mix. Continue a demonstrated accepted pulse, guitar/bass or riff identity, solid kick/backbeat, and percussion balance while building the remaining tracks. When feedback rejects the sound, revise that direction before mass-rendering more of it. Do not impose a new approval ceremony: continue independent composition and preparation within the authorized scope, and ask only for a sonic preference or audition judgment that materially guides the work.

## Render and verify

Preserve requested stereo format, duration, loop/crossfade behavior, loudness, filenames, and application resource contracts. A centered mono bass source is acceptable; judge the final mix/export by its required stereo output, not by the source loop's channel count. Derive exact decoded lengths, channel counts, and asset counts from the current project rather than copying a previous catalog's requirements. Stage replacements separately and verify the complete set before publication. Keep failed, superseded, and current renders distinguishable.

Check decoded output for finite samples, clipping/true-peak margin, loudness, channel balance, stereo compatibility, exact decoded length, silence, tails, and abrupt joins. Validate note gates and event tails at arbitrary block boundaries in procedural/native hosts. Use a small metadata fixture only when it is needed; a metadata helper check does not replace audio validation. Measurements establish technical properties, not musical quality or similarity to a reference.

Deliver the actual audio, useful editable material when appropriate, and concise provenance. Freeze source, configuration, processor/generator, and mastering hashes for a catalog run; pin raw drum hashes separately, reject stale or mixed-generation outputs, and do not combine revisions in one manifest. Record source and output hashes, tool/Logic versions, arrangement/render/mix settings, license notes, and every asset in one all-assets manifest. Publish the complete asset set and manifest atomically only after the complete set is verified; partial renders remain in progress. State whether a human audition occurred and what remains. Owner-reported listening is valid evidence even when your own workstation stayed muted; do not erase it or imply that you personally heard the audio. Do not describe MIDI/JSON or unreviewed renders as professionally produced solely because the files validate.

## Quiet work and authorization

Honor explicit quiet-work instructions. Verify the active system output is muted when asked, use a quiet native offline processor or otherwise render through an actually offline graph, and do not autoplay previews or restore/unmute audio without permission. Opening a DAW or starting a playback test may use hardware audio.

Follow the current workstation and project rules. Do not introduce CPU/memory gates, desktop takeover, external uploads, app releases, review submissions, or credential changes under the authority of a music task. Composition or catalog preparation does not itself authorize release or upload; obtain that authorization separately. In particular, CLI/native audio APIs do not imply permission to acquire screen/input control. A linked preview is for the user to play when ready.

## Dependencies and portability

Production guidance and the Python 3.9+ standard-library CAF inspector are
bundled. The inspector is not an audio renderer. Finished music needs an
available DAW or renderer, licensed sounds or synthesis, and audio validation/
audition tools. Logic/GarageBand, Apple Loops, AVFAudio/macOS, `afinfo`,
`ffmpeg`/`ffprobe`, and playback hardware are external route-specific tools.
No past user's samples, playlist, or production project is needed. An original
local WAV synthesizer/renderer with synthetic fixtures could provide a portable
baseline, but would not reproduce Logic instruments or replace human listening.
