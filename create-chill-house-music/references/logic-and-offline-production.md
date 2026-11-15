# Logic and offline production reference

This reference supports a chill-house music-making skill. It describes the
decisions that matter when turning local Logic Pro content into a finished
original soundtrack. It is not a license grant, a finished-music quality
claim, or a recipe to copy bundled material into a repository.

## Logic Pro versus native offline rendering

Logic Pro’s GUI is useful for browsing, auditioning with the owner’s approval,
arranging, editing, and final human review. It is not required for a repeatable
render once the sources and arrangement are known.

`AVAudioUnitSampler.loadInstrument(at:)` can load Logic/GarageBand EXS24
instruments as well as audio files. `AVAudioEngine` can run in manual offline
mode: configure a PCM format, call `renderOffline`, and write the resulting
buffer without connecting the engine to speakers. These are Apple’s references:

- [AVAudioUnitSampler.loadInstrument(at:)](https://developer.apple.com/documentation/avfaudio/avaudiounitsampler/loadinstrument%28at%3A%29)
- [AVAudioEngine](https://developer.apple.com/documentation/avfaudio/avaudioengine)
- [AVAudioEngine manual rendering modes](https://developer.apple.com/documentation/avfaudio/avaudioenginemanualrenderingmode)
- [Performing offline audio processing](https://developer.apple.com/documentation/avfaudio/performing-offline-audio-processing)

Use a quiet native offline processor for deterministic sampler proofs, batch
exports, and analysis when the system must remain muted. Do not imply that a
successful offline render was a human listening pass. The final arrangement
still needs intentional audition evidence when playback is authorized, and
offline processing must not acquire desktop or screen/input control.

## EXS and sampler failure modes

- Load one verified EXS instrument at a time and render a short proof before
  building a long arrangement. Record the instrument path, version, tuning,
  gain, and expected note range.
- Test note-on and note-off pairs. Overlapping or missing note-offs can create
  stacked voices, clicks, runaway tails, and an arrangement that sounds late
  even when event timestamps are correct.
- Render beyond the last musical event so release tails are preserved. A
  correct note sequence with a clipped tail is not a finished stem.
- Leave headroom through each layer and the master bus. Do not use the sampler
  proof to justify a loud final master; measure peaks and loudness after the
  actual mix.
- Do not assume General MIDI drum-note mappings. The installed kit may use a
  different layout. Verify the actual mapping from the selected kit, or use
  explicitly verified one-shots and document their pitch/routing.
- Preflight every drum variant used anywhere in the catalog before arranging
  or rendering: verify its raw identity/hash, role mapping, routing, envelope
  and tail, gain, channel/phase behavior, and any filtering or compression
  assumptions. Pin every raw drum hash in the manifest; a variant number or
  filename suffix is not a substitute for this check.
- A renderer can write two channels while its patch remains mono-like or has
  phase problems. Check mono compatibility and the low end before exporting.

## Prefer performed audio where it helps

Apple Loops can be audio recordings or software-instrument/MIDI loops. Treat
them differently. Audio loops are recorded phrases that can be edited as audio;
software-instrument loops contain MIDI and can render differently with another
patch. MIDI itself is not proof of a weak performance. See [Apple Loops in Logic
Pro](https://support.apple.com/en-ca/guide/logicpro/lgcp734a05f6/10.7/mac/11.0).

For performed harmony, curate coherent project-matched prefix/pack families
rather than mixing unrelated files by filename alone. Matching verse/chorus
stems from one factory project are a useful starting point because their
performance, voicing, and progression are more likely to belong together.
Choose families from the user's actually installed and licensed library.
Use artist/pack names only as source metadata; do not preserve a prior user's
library inventory or copy raw loops into a skill, source tree, or
distributable sample library.

For every candidate audio loop, inspect and record:

- source location, pack/artist, file hash, codec, sample rate, actual channel
  count, whether the source is stereo, and duration;
- key signature, key type, time signature, beat count, marker count, and the
  tempo derived from beats × 60 ÷ duration when no explicit tempo field exists;
- whether the CAF has a real `data` chunk and whether a `midi` chunk is absent;
- musical role (kick/topper, bass, chord, pad, guitar, piano, lead, texture),
  phrase length, and whether it is a verse, chorus, fill, transition, or loop.

Same key and BPM do not prove that chords are compatible. Check voicings,
register, harmonic rhythm, phrase boundaries, pickup notes, and the intended
role of each part. A matching key can still clash if one loop implies a
different chord at the downbeat. Do not infer verse/chorus roles from suffixes
such as `01` or `02`; validate the actual source metadata and musical phrase.
When layering a verse and chorus family, check that the selected parts share
compatible progression, downbeat, phrase length, and register before using
them in a long arrangement.

## CAF inspection and provenance

Use local metadata tools such as `afinfo` and `ffprobe`, plus a small read-only
CAF chunk inspector when Apple Loop metadata is not exposed by those tools.
Never infer “performed audio” from a `.caf` extension alone. Check audio data,
actual channel count, beat metadata, and any MIDI chunk before choosing a
candidate. One- or two-channel audio with absent MIDI identifies a baked audio
source; a mono bass source can be an intentional centered part and does not
need to be rejected. Record `stereo_source` separately from the actual channel
count; neither proves a live human performance or real stereo width.

Keep a provenance manifest with the generated work. Follow the project’s
existing manifest/bundle convention; metadata may be bundled when appropriate,
but raw source content must not be. It should include source identifiers and hashes, Logic and
tool versions, arrangement/render settings, mix/master settings, and the
license review date. Use generic library paths such as
`/Library/Audio/Apple Loops/Apple/<pack>/<file>.caf`; do not put personal home
directory paths or raw Apple content in a reusable skill.

## Licensing boundary

Read the license applicable to the installed Logic version and any third-party
pack before shipping. Apple’s current support explanation says bundled Sample
Content may be used royalty-free in an original soundtrack, while individual
assets may not be distributed standalone or repackaged as samples, sound
libraries, sound effects, or music beds. See [Apple’s commercial-use guidance
for Logic Pro content](https://support.apple.com/en-ie/101908) and the [Logic
Pro software license](https://www.apple.com/legal/sla/docs/LogicPro.pdf).

Ship only the finished soundtrack (or a permitted transformed asset), never the
raw Apple Loop, EXS instrument, sound pack, or a reconstruction that functions
as a substitute sample library. If a third-party pack has separate terms, keep
it out of distribution until those terms are confirmed. When the license is
ambiguous, stop and ask the owner to review it rather than guessing.

## Mix, export, and validation

Build the musical arrangement first, then mix around the kick and bass. Keep
bass centered, make pads wide without relying on phase cancellation, and leave
space for the lead. A mono raw bass may remain centered while the final mix is
stereo. Calibrate kick/backbeat presence separately from hat density: a sparse
groove can still need substantial snare body and attack. Check whether a
supposed snare is only a quiet clap. Role-specific filtering matters; a blanket
high-pass on every percussion source can thin the main backbeat. When layering,
let one sound provide the body and another provide the upper attack, and check
their timing/phase instead of stacking loudness blindly. Use automation and
section-level mute/dropout decisions to create movement. Avoid a constant wall
of compression or reverb.

Render a high-resolution intermediate, preserve tails, then encode the runtime
format. Verify every final track against the current project's exact decoded
length and channel requirements, regardless of whether any raw bass source
was mono. Do not reuse a previous catalog's contract. Check
that arrangements are genuinely distinct and contain real part-level changes:
record or inspect a section duty/dropout map and reject unchanged loop
repetition hidden behind a global gain ramp. Validate duration, stereo channels,
decoded loudness, true peak, clipping, silence, loop seam, and file readability;
signal statistics alone cannot prove that the music is good or that it matches
the requested style.

## Quiet and workstation boundaries

If the owner asks for silence, keep the requested system mute in force and
verify it with an approved host-level CLI/API; do not autoplay previews.
Do not unmute or change volume levels unless asked. A sandboxed `osascript`
may report a syntax error because Standard Additions cannot discover the
output device; that is not proof that the mute command itself is invalid.
Use the authorized host context for the same minimal command when needed:

```sh
osascript -e 'set volume output muted true' -e 'output muted of (get volume settings)'
```

Only open a DAW if the operation will not unexpectedly play audio and desktop
use is permitted. Quiet work does not itself revoke authorization to use a DAW;
manual offline rendering remains preferable when speaker audition is forbidden.

Do not start a native screen/input takeover or leave the owner behind an agent
locker. Follow the repository’s current `AGENTS.md` for build concurrency,
device access, and testing. This reference does not impose a generic one-build
rule on unrelated projects.

## Reproducible handoff

Before handing a soundtrack to an app project, provide all final files, source,
raw drum, configuration, processor/generator, mastering, and output hashes,
source/license notes, generator or arrangement revision, tool/Logic versions,
mix/master settings, and actual validation output in one all-assets manifest.
Freeze those identities for the run and reject stale or mixed-generation
outputs; never combine tracks rendered from different source/configuration or
mastering revisions. A partial catalog remains in progress until all requested assets are present
and verified. Stage the complete asset set and manifest separately, then
publish them atomically only after every asset is checked. Identify what was
rendered, what was listened to, and what remains unverified. Do not report a
music replacement as successful merely because a script completed or a
waveform has acceptable statistics. Preparing the handoff does not authorize
uploading, releasing, or submitting it for review; those actions require
separate user authorization.


## Delivery evidence

Keep project-specific asset inventories, build identifiers, distribution
states, and listening approvals in the owning project's private handoff.
Record technical validation and human listening separately: publication or
internal testing does not establish that every finished arrangement was heard
or liked. This reusable skill carries no historical delivery claims into a
new project.
