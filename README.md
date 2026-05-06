<div align="center">

# DX7 SysEx Generator Skill

> *Generate audible Yamaha DX7 / Dexed `.syx` files by starting from known-good voices, not by guessing fragile packed parameters.*

<br>

**A practical OpenClaw AgentSkill for inspecting, validating, copying, and safely generating DX7 / Dexed compatible SysEx banks.**

<br>

Built from a real debugging session: several hand-written DX7 voices imported into Dexed but produced silence.  
The reliable solution was to seed generation from an existing audible bank, modify gradually, and always recalculate checksum.

[English](#english) · [中文](#中文说明) · [Usage](#usage) · [Workflow](#safe-workflow) · [Repository Structure](#repository-structure)

</div>

---

## English

### What this skill does

This skill helps agents work with Yamaha DX7 / Dexed `.syx` files without falling into the common trap of generating valid-looking but silent patches.

It provides a deterministic helper script for:

| Command | Purpose |
|---|---|
| `inspect` | Read and summarize a standard DX7 32-voice bank |
| `copy-voice` | Copy one known-good voice into a new 32-slot bank |
| `meow` | Generate a simple cat-meow style FM patch from a working seed voice |

The key idea is simple:

```text
Known-good audible bank → copy one voice → modify a few safe fields → recalc checksum → test in Dexed
```

This is safer than building DX7 packed voice data from scratch.

---

## Why this exists

A standard DX7 32-voice bank can be structurally valid but still silent.

During testing:

```text
Hand-built SysEx file      → Dexed imported it → no sound
Copied known-good voice    → Dexed imported it → sound worked
Modified copied voice      → Dexed imported it → sound worked
```

So this skill encodes the proven workflow:

> **Do not trust checksum alone. First prove the seed voice is audible.**

---

## Usage

### Inspect a bank

```bash
python3 scripts/dx7_syx_tool.py inspect Dexed_01.syx
```

Example output:

```text
DX7 32-voice bank: Dexed_01.syx
size=4104 checksum=88
01. 'Say Again.' alg=32 fb=7 sync=1 outs(op6..op1)=[99, 99, 99, 99, 99, 99]
```

### Copy one working voice into a new bank

```bash
python3 scripts/dx7_syx_tool.py copy-voice Dexed_01.syx copytest.syx --voice 1 --name COPYTEST
```

Use this as the first safety check. Import `copytest.syx` into Dexed and confirm it makes sound.

### Generate a cat-meow style patch

```bash
python3 scripts/dx7_syx_tool.py meow Dexed_01.syx cat_meow.syx --voice 1 --name CATMEOWV3
```

Then import `cat_meow.syx` into Dexed and test it.

---

## Safe workflow

### 1. Start from a known-good bank

Use a `.syx` file that has already been tested in Dexed and makes sound.

### 2. Inspect it

```bash
python3 scripts/dx7_syx_tool.py inspect Dexed_01.syx
```

Check:

- File size is `4104` bytes
- Header is DX7 bank format
- Checksum is valid
- At least one voice has meaningful operator output levels

### 3. Generate a copy-test

```bash
python3 scripts/dx7_syx_tool.py copy-voice Dexed_01.syx copytest.syx --voice 1 --name COPYTEST
```

If the copy-test is silent, stop. The problem is likely import routing, Dexed setup, MIDI input, output volume, or the selected cartridge slot.

### 4. Modify gradually

Only after copy-test works, change a small number of fields:

- Voice name
- Pitch envelope
- LFO / vibrato
- Feedback
- Limited operator levels or ratios

### 5. Test every generated file

A valid checksum means the SysEx container is valid. It does **not** mean the patch is musically audible.

---

## DX7 bank facts

A standard DX7 32-voice bank is:

```text
F0 43 00 09 20 00 [4096 bytes voice data] [checksum] F7
```

| Field | Meaning |
|---|---|
| `4104 bytes` | Total file size |
| `32 × 128` | 32 voices, each 128 bytes |
| `voice[118:128]` | 10-byte voice name |
| `voice[110]` | Algorithm, zero-based: `0..31` means algorithm `1..32` |
| `voice[111]` | Feedback and oscillator sync |
| `voice[102:110]` | Pitch envelope |
| `voice[112:118]` | LFO / transpose area |
| checksum | `(-sum(voice_data)) & 0x7F` |

---

## Requirements

- Python 3
- Dexed or another DX7-compatible synth
- A known-good DX7 / Dexed `.syx` bank as seed input

No third-party Python packages are required.

---

## Repository structure

```text
dx7-syx-generator-skill/
├── README.md
├── SKILL.md
└── scripts/
    └── dx7_syx_tool.py
```

---

## 中文说明

### 这个技能能做什么

这是一个用于 Yamaha DX7 / Dexed `.syx` 文件的 OpenClaw AgentSkill，重点不是“从零创造任意 DX7 参数”，而是**稳定生成能发声的 SysEx bank**。

它提供一个确定性的 Python 工具：

| 命令 | 用途 |
|---|---|
| `inspect` | 检查标准 DX7 32 音色 bank |
| `copy-voice` | 从已知能响的 bank 中复制一个音色到新的 32 槽 bank |
| `meow` | 基于有效 seed voice 生成一个简单猫叫风格 FM 音色 |

核心流程是：

```text
已确认能响的 bank → 复制一个有效 voice → 少量修改安全字段 → 重算 checksum → Dexed 测试
```

这比凭记忆手写 DX7 packed voice 参数可靠得多。

---

## 为什么要做这个技能

DX7 `.syx` 文件有一个坑：**外层格式正确、checksum 正确，不代表音色一定会响。**

实际测试中出现过：

```text
手写 SysEx 文件       → Dexed 能导入 → 没声音
复制已知有效 voice    → Dexed 能导入 → 有声音
修改复制出来的 voice  → Dexed 能导入 → 有声音
```

所以这个技能把经验固化成规则：

> **不要只相信 checksum。先确认 seed voice 本身能发声。**

---

## 使用方法

### 检查 bank

```bash
python3 scripts/dx7_syx_tool.py inspect Dexed_01.syx
```

示例输出：

```text
DX7 32-voice bank: Dexed_01.syx
size=4104 checksum=88
01. 'Say Again.' alg=32 fb=7 sync=1 outs(op6..op1)=[99, 99, 99, 99, 99, 99]
```

### 复制一个已确认能响的音色

```bash
python3 scripts/dx7_syx_tool.py copy-voice Dexed_01.syx copytest.syx --voice 1 --name COPYTEST
```

先把 `copytest.syx` 导入 Dexed，确认有声音。这个步骤是安全基线。

### 生成猫叫风格音色

```bash
python3 scripts/dx7_syx_tool.py meow Dexed_01.syx cat_meow.syx --voice 1 --name CATMEOWV3
```

然后把 `cat_meow.syx` 导入 Dexed 测试。

---

## 推荐流程

### 1. 从已知有效 bank 开始

使用一个已经在 Dexed 中确认能发声的 `.syx` 文件作为种子。

### 2. 先 inspect

```bash
python3 scripts/dx7_syx_tool.py inspect Dexed_01.syx
```

重点看：

- 文件大小是否为 `4104` bytes
- 是否是 DX7 bank header
- checksum 是否正确
- 是否有 operator output level 不为 0 的音色

### 3. 生成 copy-test

```bash
python3 scripts/dx7_syx_tool.py copy-voice Dexed_01.syx copytest.syx --voice 1 --name COPYTEST
```

如果 copy-test 都不响，先不要继续生成复杂音色。优先检查 Dexed 导入位置、MIDI 输入、输出音量、cartridge 是否选中。

### 4. 小步修改

copy-test 确认能响之后，再逐步修改：

- 音色名
- Pitch envelope
- LFO / vibrato
- Feedback
- 少量 operator level 或 ratio

### 5. 每次都测试

checksum 正确只说明 SysEx 容器合法，**不保证音色能发声**。

---

## 许可证

MIT — free to use, modify, and adapt.

<div align="center">

*Generate first. Verify always.*

</div>
