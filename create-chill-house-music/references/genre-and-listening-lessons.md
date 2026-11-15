# Chill-house production brief and listening lessons

This reference supports the `create-chill-house-music` skill. It is a
brief for making original music, not a transcription guide and not evidence
that any current render is successful.

## Central brief

Treat the target as a cross between chill-out and house:

- a relaxed, steady four-on-the-floor pulse;
- deep but controlled bass;
- warm, spacious harmony and soulful melodic ideas;
- funky groove and light human texture;
- organic sources (especially performed guitar and keys) blended with
  electronic drums, pads, and restrained synth color.

Keep the groove grounded enough for play, but leave air around the lead. A
track can be calm without becoming beatless, and it can be rhythmic without
becoming aggressive. Do not turn “chill” into a rule that removes every bright
synth, hat, upbeat, or syncopation.

## Genre sources

Use these as genre-definition references, not as material to copy:

- [Soave Records — What Is Chill House Music?](https://www.soaverecords.com/post/what-is-chill-house-music)
- [Wikipedia — Chill-out music](https://en.wikipedia.org/wiki/Chill-out_music)
- [Wikipedia — House music](https://en.wikipedia.org/wiki/House_music)
- [Melodigging — Chill House](https://www.melodigging.com/genre/chill-house)

Soave's description points toward smooth beats, deep bass, mellow synths,
soulful melody, funky grooves, and organic/electronic blending. Wikipedia's
genre context is useful for separating chill-out atmosphere from house's dance
groove. Melodigging emphasizes warm space over a rigidly busy arrangement:
roughly 110–124 BPM is a useful starting range, with light 2/4 claps,
controlled brightness, extended chords, simple bass, spacious reverb, and
gradual section changes. These are tendencies, not a checklist or a promise
that every reference track fits them.

Obtain listening references from the current user rather than retaining a
previous user's playlist. References need not share one tempo or arrangement.
Tempo estimates from short excerpts can have half/double-time ambiguity.
Use a range to begin a composition, then choose the tempo that gives its
groove and melody the right breathing room. No source recordings or previews
are needed merely to read this reference.

## Applying listening feedback

A direction can be closer to the brief while still sounding synthetic. Treat
an accidentally late lead, constant upper-percussion chatter, and a weak
backbeat as separate problems. Preserve an accepted guitar/bass/pulse or riff
while fixing the criticized detail; removing hats should not weaken the main
kick and snare/clap foundation.

Keep actual approvals, rejected revisions, and current delivery state in the
private project handoff. This reference does not grant permission to continue
a past catalog or establish that any current assets have been rendered,
verified, published, or heard. Early previews can guide a large render, but
they do not replace listening to finished arrangements.

## Rhythm and timing lessons

Normal intentional rhythm can include:

- four-on-the-floor kick with a soft, controlled pocket;
- a solid, present clap/snare backbeat on two and four, with adequate body;
- hats, shakers, and small percussion on upbeats;
- bass anticipation, held notes, and occasional syncopated answers;
- a lead that leaves rests and answers the groove.

Do not “fix” these choices by flattening every part to the same grid. The
problem may be lead placement, not the existence of syncopation.
Check the attack of the lead phrase against the beat and harmony: an intended
offbeat should sound intentional, while an attack that arrives late because of
an unsuitable sampler envelope, rendering latency, or a note-by-note fake
performance should be redesigned. Shorten a slow attack, change the phrase,
or use a more appropriate performed source before adding more quantization.

Lead parts should have a clear rhythmic reason for their entrances. A recorded
guitar or keyboard phrase can carry natural variation; a MIDI note list with
randomized timing is not automatically a convincing performance. Do not sell
MIDI/JSON scores as produced music.

For layered verse/chorus material, validate the actual role, key/progression,
phrase boundaries, pickup notes, and downbeats of every layer. A filename
suffix such as `01` or `02` is not proof that a part is verse or chorus; inspect
the source metadata and musical content instead.

## Production criteria

Favor:

- warmer lower-mid body and an audible human motif;
- steady house drums with a solid kick and backbeat; keep the arrangement relaxed without making the drum foundation timid;
- deep bass that remains centered and readable; a mono raw bass source is normal and can feed a stereo final mix;
- simpler bass movement when the harmony already carries complexity;
- extended chords, spacious reverb, and texture with controlled brightness;
- preflighted drum variants with pinned raw hashes, a solid kick and
  snare/clap foundation, and sparse upper percussion;
- extended arrangements with real part-level dropouts, breakdowns, and changed
  returns rather than unchanged loop repetition; validate the actual section
  duty/dropout variation, not only a layer list or global volume ramp;
- recorded/performed guitar and harmonic audio from project-matched
  verse/chorus families where the phrase needs human touch, with authored
  arrangement rather than pasted loops;
- synths as color, support, response, or atmosphere unless a track deliberately
  earns a synth lead.

The production may use native sampler instruments, recorded mono or stereo
one-shots, performed audio loops, EQ, delay, reverb, sidechain ducking, and
drum-bus compression. Higher-fidelity recorded sources improve the odds of a
natural result but do not guarantee one. Source quality, arrangement, timing,
envelope, mix balance, and listening all matter. Do not infer a live human
performance or stereo width from a file extension or channel count alone.

Use 110–124 BPM as a starting point, not a universal constraint. Faster
references can work when the groove remains relaxed; slower tracks can fail if
their lead has no pocket. Preserve hats and upbeat movement when they support
the groove.

## Evaluation discipline

Separate evidence types:

1. **Structure:** score data, section map, note roles, source inventory, and
   intended duration.
2. **Signal checks:** duration, finite samples, peaks, loudness, stereo, phase,
   and decoded-file integrity.
3. **Human listening:** whether the beat feels good, the lead is intentional,
   the source sounds natural, the arrangement stays engaging, and the track
   actually fits chill house.

Metrics can reveal clipping, mono collapse, a missing breakdown, or a lead that
is systematically late. They cannot prove that a track is soulful, relaxing,
fun to play with, or free of an AI-like feel. Audition representative full
arrangements when playback is permitted, on headphones and target speakers
when available. Respect an ongoing mute instruction; document what was
actually heard and what remains unauditioned.

## Source and workflow boundaries

Keep raw samples, reference previews, and installed-library paths outside Git
and outside the app bundle. Use generic machine-local roots such as an
installed Logic EXS library, the Apple Loops library, or a shared GarageBand
sample tree; never write personal home-directory paths into a reusable skill.
Pin source identities and hashes in a final manifest without redistributing raw
samples.

For a game catalog, preserve stable track IDs and access behavior while
staging replacements separately. Render early previews sequentially, react to
the owner's listening feedback, then expand only the direction that survives
that feedback. Establish the actual asset count, duration, and channel contract
from the current project. Record source, raw drum, configuration, processor/generator,
mastering, and output hashes in one all-assets manifest. Freeze those inputs
for the run and reject stale or mixed-generation outputs rather than combining
revisions.
Publish the complete replacement set and manifest atomically only after all
assets pass their checks; a partial catalog remains in progress. A quiet native
offline processor is preferred when the system must stay muted, and its output
still needs separate human-listening evidence. Do not claim that a pilot, a score file, or a passing signal test establishes
listening approval of a finished catalog. Uploads, releases, and review submissions require separate
user authorization.
