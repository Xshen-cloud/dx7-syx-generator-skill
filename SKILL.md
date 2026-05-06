---
name: dx7-syx-generator
description: Generate, inspect, validate, and safely modify Yamaha DX7 / Dexed compatible .syx files. Use when creating FM patches, Dexed banks, cat-meow/effect patches, or debugging silent .syx output.
---

# DX7 / Dexed SysEx Generator

Use this skill when generating or editing `.syx` files for Yamaha DX7 or Dexed.

## Hard rule

Do **not** hand-build a DX7 voice from memory unless absolutely necessary. It is easy to create a file that imports but produces silence.

Preferred workflow:

1. Start from a known-good Dexed/DX7 `.syx` bank that already makes sound.
2. Copy one audible voice as the seed.
3. Modify only a few packed parameters at a time.
4. Rebuild a 32-voice bank.
5. Recalculate checksum.
6. Save and test in Dexed.

## Known-good bank structure

A standard DX7 32-voice bank is 4104 bytes:

```text
F0 43 00 09 20 00 [4096 bytes voice data] [checksum] F7
```

- 32 voices × 128 bytes = 4096 bytes
- checksum = `(-sum(voice_data)) & 0x7F`
- voice names are bytes `118:128` inside each 128-byte voice
- algorithm byte is `110`, stored zero-based: `0..31` means algorithm `1..32`
- feedback/sync byte is `111`; low 3 bits are feedback, bit 3 is osc sync
- pitch EG bytes are `102:110`
- LFO / transpose bytes are `112:118`

## Local proven facts

During testing, files generated entirely from hand-written packed voice parameters imported into Dexed but were silent. A copy made from an existing working bank (`Dexed_01.syx`) produced sound.

Therefore, for reliable generation:

- Use `Dexed_01.syx` or another confirmed-audible bank as a seed.
- First create a copy-test bank from the source voice.
- Only after the copy-test makes sound, change pitch EG, LFO, name, and limited operator values.

## Recommended scripts

Use the bundled script:

```bash
python3 scripts/dx7_syx_tool.py inspect /path/to/file.syx
python3 scripts/dx7_syx_tool.py copy-voice /path/to/seed.syx /path/to/output.syx --voice 1 --name COPYTEST1
python3 scripts/dx7_syx_tool.py meow /path/to/seed.syx /path/to/output.syx --voice 1 --name CATMEOWV3
```

## Safe modification strategy

For expressive patches such as a cat-like FM meow:

1. Keep the seed's operator blocks intact first.
2. Change pitch envelope to create a scoop:

```python
voice[102:106] = bytes([70, 42, 34, 45])
voice[106:110] = bytes([38, 78, 45, 50])
```

3. Add mild LFO pitch wobble:

```python
voice[112:118] = bytes([45, 18, 18, 0, 49, 24])
```

4. Keep algorithm audible unless deliberately changing routing:

```python
voice[110] = 31              # algorithm 32
voice[111] = (1 << 3) | 5    # sync on, feedback 5
```

5. Write the modified voice into all 32 bank slots, recalc checksum.

## Debugging silent files

If a generated file imports but has no sound:

1. Inspect header, size, checksum.
2. Generate a copy-test from a known-good voice.
3. If copy-test is audible, the problem is the modified voice parameters.
4. If copy-test is silent, check Dexed import location, cartridge loading, MIDI input, output volume, and selected voice.
5. Compare operator output levels and algorithm against a known-good bank.

Never assume a valid checksum means the patch is audible.
