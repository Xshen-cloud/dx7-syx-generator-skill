---
name: dx7-syx-generator
description: Generate, inspect, validate, and safely modify Yamaha DX7 / Dexed compatible .syx files. Use when creating FM patches, Dexed banks, cat-meow/effect patches, or debugging silent .syx output.
---

# DX7 / Dexed SysEx Generator

Use this skill when generating or editing `.syx` files for Yamaha DX7 or Dexed.

## Hard rule

Do **not** hand-build a DX7 voice from memory unless absolutely necessary. It is easy to create a file that imports but produces silence.

**校验和正确 ≠ 音色能发声。** 这是最核心的经验。

## ⚠️ 种子库黑名单

以下文件**不能**用作种子——它们校验和正确但内部 operator 参数是垃圾数据，生成后必然无声：

- `dx7_audible_test_bank.syx` — OP6 byte 0/1/2/4 超出合法范围，OP1-5 输出全为 0
- `dx7_dexed01_copytest.syx` — 同上，参数非法

**唯一推荐种子**: `SynprezFM_demo.syx` (32 voices，全部确认能发声)

路径: `/mnt/d/Workspace/Claw_work/SynprezFM_demo.syx`

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

## Operator 参数范围速查

每个 operator 占 17 bytes，offset = `op * 17`（op = 0..5）：

| Offset | 参数 | 合法范围 | 说明 |
|--------|------|---------|------|
| +0 | oscillator mode | 0-63 | 频率模式 |
| +1 | coarse frequency | 1-31 | 粗调频率（比例模式） |
| +2 | fine_frequency | 0-15 | 细调频率 |
| +3 | detune | 0-99 | 失谐量 |
| +4 | harm. type | 0-31 | 谐波类型（固定模式） |
| +5-8 | EG Rates R1-R4 | 0-99 | 包络速率 |
| +9-12 | EG Levels L1-L4 | 0-99 | 包络电平 |
| +13 | velocity_sensitivity | 0-99 | 力度响应 |
| +14 | output_level | 0-99 | 输出电平 |
| +15 | mode_select | 1=比例, 2=固定 | 频率模式 |
| +16 | key_scaling | 0-99 | 键盘跟随 |

**判断种子是否可用的关键**：检查 operator byte 0（osc mode）和 byte 1（coarse）是否在合法范围内。如果 byte 0 = 0x63 (99) 或 byte 1 = 99，大概率是无效参数。

## 致命陷阱：为什么手写 operator 字节会失败

在实际调试中发现两个致命问题：

### 陷阱 1：坏种子库
`dx7_audible_test_bank.syx` 校验和正确，但内部参数是垃圾数据。用它生成的文件必然无声。

### 陷阱 2：手写 operator 字节（byte 0-101）
DX7 SysEx 用的是压缩编码，不是直观的 0-99 数值。手写值极大概率超出合法范围：

- 手写 plunk 音色时，**15 个字节超出了 32 个正常音色的取值范围**
- **5 个字节设为 0**，但在任何正常音色中这些字节永远不会为 0
- 结果：文件能导入 Dexed，但无声

**结论：永远不要从头手写 operator 参数（byte 0-101）。**

## 生成规则

1. 从 `SynprezFM_demo.syx` 选一个风格接近的 voice 作为基础
2. **只改** Pitch EG (102-109)、LFO (112-116)、名字 (118-127)
3. **永远不要**重新写 operator block（byte 0-16, 17-33, ... 101）
4. 改完复制到 32 个 slot，重算 checksum

## 推荐种子 voice 速查

| Demo Voice | 名称 | 特点 | 适合改造成 |
|-----------|------|------|----------|
| #6 | CLARINET | 单 carrier + 木管质感 | 管乐、单音旋律 |
| #14 | Flute 22 | 干净正弦波基调 | 警笛、纯音效果 |
| #17 | LOG DRUM | 打击乐起音 | 打击乐、敲击音效、plunk |
| #18 | PIANO 2 | 钢琴类 | 键盘乐器 |
| #19 | BABY CAT | 猫叫声效果 | 动物音效、滑音效果 |
| #23 | LEAD SNYTH | 合成主音 | lead synth、电子音色 |
| #30 | FANTOMES | 全 carrier，氛围 | 氛围、pad、drone |
| #31 | Old Pond | 水滴/自然音效 | 自然音效、percussive、铜铃 |
| #4 | yanni | 全 operator 输出 | 复杂合成音色 |

## Recommended scripts

Use the bundled script:

```bash
python3 scripts/dx7_syx_tool.py inspect /path/to/file.syx
python3 scripts/dx7_syx_tool.py copy-voice /path/to/seed.syx /path/to/output.syx --voice 1 --name COPYTEST1
python3 scripts/dx7_syx_tool.py meow /path/to/seed.syx /path/to/output.syx --voice 1 --name CATMEOWV3
```

## Safe modification strategy

For expressive patches such as a cat-like FM meow or a siren:

1. **Keep the seed's operator blocks intact** — never rewrite bytes 0-101 for operators
2. Change pitch envelope to create a scoop:

```python
voice[102:106] = bytes([70, 42, 34, 45])  # rates
voice[106:110] = bytes([38, 78, 45, 50])  # levels
```

3. Add mild LFO pitch wobble:

```python
voice[112] = 45   # rate
voice[113] = 18   # delay
voice[114] = 18   # pitch mod depth
voice[115] = 0    # amp mod
voice[116] = 0    # wave (triangle)
# voice[117] = transpose, leave as-is
```

4. Keep algorithm and feedback from seed unless deliberately changing routing
5. Write the modified voice into all 32 bank slots, recalc checksum.

## Python 代码模板

```python
from pathlib import Path

HEADER = bytes([0xF0, 0x43, 0x00, 0x09, 0x20, 0x00])

def read_bank(path):
    b = path.read_bytes()
    return bytearray(b[6:-2])  # strip header + checksum + footer

def write_bank(path, data):
    checksum = (-sum(data)) & 0x7F
    path.write_bytes(HEADER + data + bytes([checksum, 0xF7]))

# Read seed
seed = read_bank(Path("/path/to/SynprezFM_demo.syx"))

# Pick a voice (e.g. voice 14 = index 13)
src = 13 * 128

# Copy to all 32 slots
out = bytearray(32 * 128)
for i in range(32):
    out[i*128:(i+1)*128] = seed[src:src+128]

# Modify voice 1 (offset 0) — ONLY pitch EG, LFO, name
# NEVER modify bytes 0-101 (operator data)
b = 0
out[b+102:106] = bytes([80, 50, 30, 35])  # pitch EG rates
out[b+106] = 99   # L1 max pitch up
out[b+107] = 99   # L2 sustain high
out[b+108] = 10   # L3 drop low
out[b+109] = 50   # L4 center
out[b+112] = 55   # LFO rate
out[b+113] = 10   # LFO delay
out[b+114] = 60   # LFO pitch mod
out[b+115] = 0    # no amp mod
out[b+116] = 0    # triangle wave
out[b+118:b+128] = b"SIREN     "

write_bank(Path("output.syx"), bytes(out))
```

## Debugging silent files

If a generated file imports but has no sound:

1. Inspect header, size, checksum.
2. Generate a copy-test from a known-good voice.
3. If copy-test is audible, the problem is the modified voice parameters.
4. If copy-test is silent, check Dexed import location, cartridge loading, MIDI input, output volume, and selected voice.
5. **Compare operator bytes 0-4 against a known-good bank** — if osc mode or coarse freq are out of range, the seed was bad.
6. **If you hand-wrote any operator byte (0-101)**, that's almost certainly the problem. Restart from a working seed.
7. Never assume a valid checksum means the patch is audible.
