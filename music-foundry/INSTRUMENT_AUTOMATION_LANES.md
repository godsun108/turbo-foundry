# Instrument and vocal automation lanes

Status: implemented in the canonical Music Foundry offline render path.

Automation remains non-destructive: source WAV stems and recorded takes are read-only. Each render uses its manifest/configuration and writes separate processed WAV files plus provenance metadata.

## Supported lanes

Keyframes use the same bounded shape across instrument stems and vocal takes:

```json
{ "param": "drive_db", "time_ms": 45000, "value": 6 }
```

Supported parameters:

| Parameter | Range | Purpose |
|---|---:|---|
| `gain_db` | -60 to +12 dB | Level rides |
| `lowpass_hz` | 500 to 20,000 Hz | Filter sweeps |
| `delay_wet` | 0 to 100% | Delay throws |
| `delay_feedback` | 0 to 75% | Feedback ramps |
| `drive_db` | 0 to 24 dB | Saturation / distortion automation |
| `pan` | -1 to +1 | Continuous left/right movement |

Each take or stem accepts at most 64 keyframes, with times from 0 to 180,000 ms. Values are linearly interpolated between keyframes. The current DSP chain applies drive automation during processing, filter and delay automation in their respective stages, gain automation during placement, and pan automation during stereo placement.

## Instrument stem example

The existing `warehouse_rave_v2_texture_a.example.json` now demonstrates drive and pan motion on the synth stem. Its filter and delay lanes remain intact. Run it through the existing processor:

```bash
python3 music-foundry/process_instrument_stems.py \
  --config music-foundry/warehouse_rave_v2_texture_a.example.json \
  --output music-foundry/output/warehouse-rave-texture-b
```

The source manifest and stem WAVs are never overwritten. Output contains stereo processed stems, a stereo mix, and `instrument_stem_manifest.json` with source checksums and the applied automation.

## Design boundary

This extends the existing Music Foundry DSP; it does not add a second DAW, sampler, cloud service, or model dependency. Automation is a reproducible mix/render control, not a replacement for listening and mix decisions. A later browser timeline can edit the same keyframe contract and send it to this offline renderer.
