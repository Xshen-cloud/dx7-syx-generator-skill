---
name: dx7-syx-generator
description: Generate, inspect, validate, and safely modify Yamaha DX7 / Dexed compatible .syx files.
---

# DX7 / Dexed SysEx Generator

Use this skill when generating or editing `.syx` files for Yamaha DX7 or Dexed.

## Usage

### Inspect a bank

```bash
python3 scripts/dx7_syx_tool.py inspect /path/to/file.syx
```

### Copy one voice into a new 32-voice bank

```bash
python3 scripts/dx7_syx_tool.py copy-voice /path/to/seed.syx output.syx --voice 1 --name MYVOICE
```

### Generate a cat-meow style patch

```bash
python3 scripts/dx7_syx_tool.py meow /path/to/seed.syx output.syx --voice 1 --name CATMEOW
```

## Workflow

1. Use `SynprezFM_demo.syx` (included in this repo) as the seed bank.
2. Inspect the seed to find a voice with a similar character.
3. Use `copy-voice` to create a new bank from that voice.
4. Modify only these bytes for the new patch:
   - **Pitch EG**: bytes 102–109
   - **LFO**: bytes 112–116
   - **Voice name**: bytes 118–127
5. Keep all operator bytes (0–101) unchanged.
6. Write the bank with recalculated checksum.

## Recommended seed voices (SynprezFM_demo.syx)

| Voice | Name | Good for |
|-------|------|----------|
| #6 | CLARINET | wind, single melody |
| #14 | Flute 22 | siren, pure tones |
| #17 | LOG DRUM | percussion, plunk |
| #18 | PIANO 2 | keyboard |
| #19 | BABY CAT | animal FX, slides |
| #23 | LEAD SNYTH | lead synth |
| #30 | FANTOMES | pad, drone |
| #31 | Old Pond | nature FX, percussive |
| #4 | yanni | complex tones |

## Voice layout (128 bytes)

- **Bytes 0–101**: 6 operators × 17 bytes each (do not hand-write these)
- **Bytes 102–105**: Pitch EG rates
- **Bytes 106–109**: Pitch EG levels
- **Byte 110**: Algorithm (0-based: 0–31)
- **Byte 111**: Feedback (low 3 bits) + OSC sync (bit 3)
- **Bytes 112–116**: LFO settings
- **Byte 117**: Transpose
- **Bytes 118–127**: Voice name (10 chars, ASCII)
