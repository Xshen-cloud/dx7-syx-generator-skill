#!/usr/bin/env python3
"""Small DX7/Dexed 32-voice bank inspector and safe generator.

This intentionally starts from known-good voices instead of hand-building
full DX7 packed voice data from scratch.
"""
from __future__ import annotations

import argparse
from pathlib import Path

HEADER = bytes([0xF0, 0x43, 0x00, 0x09, 0x20, 0x00])
BANK_DATA_LEN = 32 * 128
BANK_TOTAL_LEN = 6 + BANK_DATA_LEN + 2


def read_bank(path: Path) -> bytearray:
    b = path.read_bytes()
    if len(b) != BANK_TOTAL_LEN:
        raise SystemExit(f"not a standard DX7 32-voice bank: {len(b)} bytes, expected {BANK_TOTAL_LEN}")
    if b[:6] != HEADER or b[-1] != 0xF7:
        raise SystemExit(f"bad DX7 bank header/footer: header={b[:6].hex(' ')} footer={b[-1]:02x}")
    data = b[6:-2]
    calc = (-sum(data)) & 0x7F
    if calc != b[-2]:
        raise SystemExit(f"bad checksum: file={b[-2]} calculated={calc}")
    return bytearray(data)


def write_bank(path: Path, data: bytes) -> None:
    if len(data) != BANK_DATA_LEN:
        raise ValueError(f"bank data must be {BANK_DATA_LEN} bytes")
    checksum = (-sum(data)) & 0x7F
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(HEADER + data + bytes([checksum, 0xF7]))


def voice_name(voice: bytes) -> str:
    return voice[118:128].decode("ascii", "replace")


def set_name(voice: bytearray, name: str) -> None:
    voice[118:128] = name[:10].ljust(10).encode("ascii", "replace")


def inspect(path: Path) -> None:
    data = read_bank(path)
    print(f"DX7 32-voice bank: {path}")
    print(f"size={BANK_TOTAL_LEN} checksum={((-sum(data)) & 0x7F)}")
    for i in range(32):
        v = data[i * 128 : (i + 1) * 128]
        alg = v[110] + 1
        fb = v[111] & 7
        sync = (v[111] >> 3) & 1
        outs = [v[o * 17 + 14] for o in range(6)]
        print(f"{i+1:02d}. {voice_name(v)!r} alg={alg:02d} fb={fb} sync={sync} outs(op6..op1)={outs}")


def get_seed_voice(seed: Path, voice_no: int) -> bytearray:
    data = read_bank(seed)
    if not (1 <= voice_no <= 32):
        raise SystemExit("--voice must be 1..32")
    return bytearray(data[(voice_no - 1) * 128 : voice_no * 128])


def make_bank_from_voice(voice: bytes) -> bytes:
    if len(voice) != 128:
        raise ValueError("voice must be 128 bytes")
    return bytes(voice) * 32


def copy_voice(seed: Path, out: Path, voice_no: int, name: str | None) -> None:
    voice = get_seed_voice(seed, voice_no)
    if name:
        set_name(voice, name)
    write_bank(out, make_bank_from_voice(voice))
    print(f"wrote copy-test bank: {out}")


def meow(seed: Path, out: Path, voice_no: int, name: str) -> None:
    voice = get_seed_voice(seed, voice_no)

    # Keep known-good operator blocks. Shape only global pitch/LFO and safe routing.
    voice[102:106] = bytes([70, 42, 34, 45])      # pitch EG rates
    voice[106:110] = bytes([38, 78, 45, 50])      # low -> high -> lower -> center
    voice[110] = 31                                # algorithm 32, safest all-carrier routing
    voice[111] = (1 << 3) | 5                      # osc sync on + feedback 5
    voice[112:118] = bytes([45, 18, 18, 0, 49, 24]) # mild LFO/pitch wobble + normal transpose
    set_name(voice, name)

    write_bank(out, make_bank_from_voice(voice))
    print(f"wrote meow bank: {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description="DX7/Dexed .syx inspector and safe generator")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inspect")
    p.add_argument("file", type=Path)

    p = sub.add_parser("copy-voice")
    p.add_argument("seed", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--voice", type=int, default=1)
    p.add_argument("--name")

    p = sub.add_parser("meow")
    p.add_argument("seed", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--voice", type=int, default=1)
    p.add_argument("--name", default="CATMEOWV3")

    args = ap.parse_args()
    if args.cmd == "inspect":
        inspect(args.file)
    elif args.cmd == "copy-voice":
        copy_voice(args.seed, args.out, args.voice, args.name)
    elif args.cmd == "meow":
        meow(args.seed, args.out, args.voice, args.name)


if __name__ == "__main__":
    main()
