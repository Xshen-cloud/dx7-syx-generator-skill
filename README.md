<div align="center">

# DX7 SysEx Generator Skill

> *Generate audible Yamaha DX7 / Dexed `.syx` files by starting from known-good voices, not by guessing fragile packed parameters.*

<br>

**A practical OpenClaw AgentSkill for inspecting, validating, copying, and safely generating DX7 / Dexed compatible SysEx banks.**

<br>

Built from real debugging sessions: files with valid checksums but silent output due to invalid operator parameters.  
The reliable solution: seed from a proven audible bank, modify gradually, always test.

[English](#english) · [Install](#installation) · [中文](#中文说明) · [安装](#安装说明) · [Usage](#usage) · [Workflow](#safe-workflow) · [Repository Structure](#repository-structure)

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
Hand-built SysEx file        → Dexed imported it → no sound
Copied known-good voice      → Dexed imported it → sound worked
Modified copied voice        → Dexed imported it → sound worked
Valid checksum + bad params  → Dexed imported it → no sound (seed was garbage)
```

**Key lesson**: a valid checksum only proves the SysEx container is valid. It does **not** mean the operator parameters inside are audible. Some banks have operator byte values completely outside legal DX7 ranges (e.g. oscillator mode = 99, coarse frequency = 99) — they look structurally valid but produce silence.

So this skill encodes the proven workflow:

> **Do not trust checksum alone. First prove the seed voice is audible. Then modify minimally.**

---

## ⚠️ Seed Bank Guidelines

**Recommended seed**: `SynprezFM_demo.syx` — 32 voices, all confirmed audible.

**Do NOT use as seed** (valid checksum but garbage operator params):
- `dx7_audible_test_bank.syx` — OP byte 0/1/2/4 out of range
- `dx7_dexed01_copytest.syx` — same issue

---

## Usage

### Inspect a bank

```bash
python3 scripts/dx7_syx_tool.py inspect SynprezFM_demo.syx
```

Example output:

```text
DX7 32-voice bank: SynprezFM_demo.syx
size=4104 checksum=107
01. 'DL RHODES4' alg=05 fb=6 sync=0 outs(op6..op1)=[39, 99, 95, 99, 96, 91]
02. '<Vangelis>' alg=05 fb=0 sync=1 outs(op6..op1)=[90, 95, 90, 99, 70, 90]
...
```

### Copy one working voice into a new bank

```bash
python3 scripts/dx7_syx_tool.py copy-voice SynprezFM_demo.syx copytest.syx --voice 14 --name COPYTEST
```

Use this as the first safety check. Import `copytest.syx` into Dexed and confirm it makes sound.

### Generate a cat-meow style patch

```bash
python3 scripts/dx7_syx_tool.py meow SynprezFM_demo.syx cat_meow.syx --voice 1 --name CATMEOWV3
```

Then import `cat_meow.syx` into Dexed and test it.

---

## Safe workflow

### 1. Start from a known-good bank

Use `SynprezFM_demo.syx` or another `.syx` file that has been tested in Dexed and makes sound.

### 2. Inspect it

```bash
python3 scripts/dx7_syx_tool.py inspect SynprezFM_demo.syx
```

Check:

- File size is `4104` bytes
- Header is DX7 bank format
- Checksum is valid
- **Operator parameters are in legal ranges** (osc mode 0-63, coarse 1-31, etc.)

### 3. Generate a copy-test

```bash
python3 scripts/dx7_syx_tool.py copy-voice SynprezFM_demo.syx copytest.syx --voice 14 --name COPYTEST
```

If the copy-test is silent, stop. The problem is likely import routing, Dexed setup, MIDI input, output volume, or the selected cartridge slot.

### 4. Modify gradually

Only after copy-test works, change a small number of fields:

- Voice name
- Pitch envelope (bytes 102-109)
- LFO / vibrato (bytes 112-116)
- Feedback (byte 111, low 3 bits)
- Limited operator levels or ratios

**Never rewrite the full operator block (bytes 0-101) unless you have a proven reference.**

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
| `voice[102:110]` | Pitch envelope (rates + levels) |
| `voice[112:118]` | LFO / transpose area |
| checksum | `(-sum(voice_data)) & 0x7F` |

### Operator layout (per operator, 17 bytes)

Each operator occupies 17 bytes. For operator N (N=1..6), base offset = `(N-1) * 17`:

| Offset | Parameter | Legal Range | Notes |
|--------|-----------|------------|-------|
| +0 | oscillator mode | 0-63 | Frequency mode |
| +1 | coarse frequency | 1-31 | Ratio mode |
| +2 | fine_frequency | 0-15 | Fine tuning |
| +3 | detune | 0-99 | Detune amount |
| +4 | harmonic type | 0-31 | Fixed mode |
| +5-8 | EG Rates R1-R4 | 0-99 | Envelope rates |
| +9-12 | EG Levels L1-L4 | 0-99 | Envelope levels |
| +13 | velocity_sensitivity | 0-99 | Velocity response |
| +14 | output_level | 0-99 | Operator volume |
| +15 | mode_select | 1=ratio, 2=fixed | Frequency mode |
| +16 | key_scaling | 0-99 | Keyboard scaling |

---

## Requirements

- Python 3
- Dexed or another DX7-compatible synth
- A known-good DX7 / Dexed `.syx` bank as seed input

No third-party Python packages are required.

---

## Installation

### Install as an OpenClaw skill

Clone this repository into your OpenClaw workspace skills directory:

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/Xshen-cloud/dx7-syx-generator-skill.git \
  ~/.openclaw/workspace/skills/dx7-syx-generator
```

If the directory already exists, update it with:

```bash
cd ~/.openclaw/workspace/skills/dx7-syx-generator
git pull
```

After installation, start a new OpenClaw session or reload skills so the metadata in `SKILL.md` can be discovered.

### Use without installing

You can also use the helper script directly after cloning anywhere:

```bash
git clone https://github.com/Xshen-cloud/dx7-syx-generator-skill.git
cd dx7-syx-generator-skill
python3 scripts/dx7_syx_tool.py inspect /path/to/SynprezFM_demo.syx
```

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

这是一个用于 Yamaha DX7 / Dexed `.syx` 文件的 OpenClaw AgentSkill，重点不是"从零创造任意 DX7 参数"，而是**稳定生成能发声的 SysEx bank**。

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
手写 SysEx 文件            → Dexed 能导入 → 没声音
复制已知有效 voice         → Dexed 能导入 → 有声音
修改复制出来的 voice       → Dexed 能导入 → 有声音
checksum 正确但参数非法     → Dexed 能导入 → 没声音（种子库本身就是垃圾数据）
```

**核心教训**：校验和正确只证明 SysEx 容器合法，**不代表内部 operator 参数在合法范围内**。有些库的 operator byte 值完全超出 DX7 合法范围（例如 oscillator mode = 99，coarse frequency = 99），结构上合法但产生无声。

所以这个技能把经验固化成规则：

> **不要只相信 checksum。先确认 seed voice 本身能发声。然后最小化修改。**

---

## ⚠️ 种子库指南

**推荐种子**: `SynprezFM_demo.syx` — 32 个音色，全部确认能发声。

**不能用做种子**（校验和正确但参数非法）：
- `dx7_audible_test_bank.syx` — OP byte 0/1/2/4 超出合法范围
- `dx7_dexed01_copytest.syx` — 同上

---

## 使用方法

### 检查 bank

```bash
python3 scripts/dx7_syx_tool.py inspect SynprezFM_demo.syx
```

### 复制一个已确认能响的音色

```bash
python3 scripts/dx7_syx_tool.py copy-voice SynprezFM_demo.syx copytest.syx --voice 14 --name COPYTEST
```

先把 `copytest.syx` 导入 Dexed，确认有声音。这个步骤是安全基线。

### 生成猫叫风格音色

```bash
python3 scripts/dx7_syx_tool.py meow SynprezFM_demo.syx cat_meow.syx --voice 1 --name CATMEOWV3
```

然后把 `cat_meow.syx` 导入 Dexed 测试。

---

## 推荐流程

### 1. 从已知有效 bank 开始

使用 `SynprezFM_demo.syx` 或已经在 Dexed 中确认能发声的 `.syx` 文件。

### 2. 先 inspect

```bash
python3 scripts/dx7_syx_tool.py inspect SynprezFM_demo.syx
```

重点看：

- 文件大小是否为 `4104` bytes
- 是否是 DX7 bank header
- checksum 是否正确
- **operator 参数是否在合法范围内**（osc mode 0-63, coarse 1-31 等）

### 3. 生成 copy-test

```bash
python3 scripts/dx7_syx_tool.py copy-voice SynprezFM_demo.syx copytest.syx --voice 14 --name COPYTEST
```

如果 copy-test 都不响，先不要继续生成复杂音色。优先检查 Dexed 导入位置、MIDI 输入、输出音量、cartridge 是否选中。

### 4. 小步修改

copy-test 确认能响之后，再逐步修改：

- 音色名
- Pitch envelope（byte 102-109）
- LFO / vibrato（byte 112-116）
- Feedback（byte 111 低 3 位）
- 少量 operator level 或 ratio

**永远不要**在没有可靠参考的情况下重写整个 operator block（byte 0-101）。

### 5. 每次都测试

checksum 正确只说明 SysEx 容器合法，**不保证音色能发声**。

---

## 安装说明

### 安装为 OpenClaw skill

把仓库克隆到 OpenClaw workspace 的 skills 目录：

```bash
mkdir -p ~/.openclaw/workspace/skills
git clone https://github.com/Xshen-cloud/dx7-syx-generator-skill.git \
  ~/.openclaw/workspace/skills/dx7-syx-generator
```

如果已经安装过，用下面命令更新：

```bash
cd ~/.openclaw/workspace/skills/dx7-syx-generator
git pull
```

安装后，开启新的 OpenClaw 会话，或重新加载 skills，让系统发现 `SKILL.md` 里的技能元数据。

### 不安装，直接使用脚本

也可以把仓库克隆到任意目录后直接运行脚本：

```bash
git clone https://github.com/Xshen-cloud/dx7-syx-generator-skill.git
cd dx7-syx-generator-skill
python3 scripts/dx7_syx_tool.py inspect /path/to/SynprezFM_demo.syx
```

---

## 许可证

MIT — free to use, modify, and adapt.

<div align="center">

*Generate first. Verify always.*

</div>
