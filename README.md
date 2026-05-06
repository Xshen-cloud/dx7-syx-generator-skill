# DX7 SysEx Generator Skill

English | [中文](#中文说明)

## English

A small OpenClaw AgentSkill for inspecting, validating, copying, and safely generating Yamaha DX7 / Dexed compatible `.syx` files.

This skill was created after testing showed that hand-written DX7 packed voice data can import into Dexed but still produce silence. The safe workflow is to start from a known-good audible `.syx` bank, copy one working voice, then modify a small number of parameters and recalculate the checksum.

## What it includes

```text
SKILL.md
scripts/dx7_syx_tool.py
```

The Python helper supports:

- Inspecting a standard DX7 32-voice bank
- Copying one known-good voice into a new 32-slot bank
- Generating a simple cat-meow style patch from a known-good seed voice
- Recalculating the DX7 SysEx checksum automatically

## Requirements

- Python 3
- A known-good DX7/Dexed `.syx` bank file
- Dexed or another DX7-compatible synth for testing

No third-party Python packages are required.

## Usage

From the repository directory:

```bash
python3 scripts/dx7_syx_tool.py inspect Dexed_01.syx
```

Copy a known-good voice into all 32 slots:

```bash
python3 scripts/dx7_syx_tool.py copy-voice Dexed_01.syx copytest.syx --voice 1 --name COPYTEST
```

Generate a cat-meow style patch from voice 1:

```bash
python3 scripts/dx7_syx_tool.py meow Dexed_01.syx cat_meow.syx --voice 1 --name CATMEOWV3
```

Then import the output `.syx` file into Dexed and test it.

## Important workflow

1. First run `inspect` on the source `.syx` file.
2. Generate a `copy-voice` test file.
3. Confirm the copy-test file makes sound in Dexed.
4. Only then generate or modify more expressive patches.
5. If a generated patch is silent, go back to the copy-test stage.

A valid checksum does **not** guarantee that the patch is audible.

---

## 中文说明

这是一个用于检查、验证、复制和安全生成 Yamaha DX7 / Dexed 兼容 `.syx` 文件的 OpenClaw AgentSkill。

这个技能的核心经验是：手写 DX7 packed voice 参数很容易生成“能导入 Dexed、但没有声音”的文件。更稳妥的方式是：从一个已经确认能发声的 `.syx` bank 开始，复制其中一个有效音色，再少量修改参数并重新计算 checksum。

## 包含内容

```text
SKILL.md
scripts/dx7_syx_tool.py
```

Python 辅助脚本支持：

- 检查标准 DX7 32 音色 bank
- 从已验证能响的 bank 中复制一个音色到新的 32 槽 bank
- 基于有效 seed voice 生成简单的猫叫风格 FM 音色
- 自动重新计算 DX7 SysEx checksum

## 环境要求

- Python 3
- 一个已确认能在 Dexed 中发声的 DX7/Dexed `.syx` bank 文件
- Dexed 或其他 DX7 兼容合成器用于测试

不需要额外安装第三方 Python 包。

## 使用方法

在仓库目录下执行：

```bash
python3 scripts/dx7_syx_tool.py inspect Dexed_01.syx
```

把一个已知能响的音色复制到新的 32 槽 bank：

```bash
python3 scripts/dx7_syx_tool.py copy-voice Dexed_01.syx copytest.syx --voice 1 --name COPYTEST
```

基于第 1 个音色生成猫叫风格 patch：

```bash
python3 scripts/dx7_syx_tool.py meow Dexed_01.syx cat_meow.syx --voice 1 --name CATMEOWV3
```

然后把输出的 `.syx` 导入 Dexed 测试。

## 推荐流程

1. 先对源 `.syx` 执行 `inspect`。
2. 生成一个 `copy-voice` 测试文件。
3. 在 Dexed 中确认 copy-test 文件有声音。
4. 再继续生成或修改更复杂的音色。
5. 如果生成结果静音，回到 copy-test 阶段排查。

注意：checksum 正确只代表 SysEx 外层格式有效，**不代表音色一定会响**。
