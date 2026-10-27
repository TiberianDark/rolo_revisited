"""Regenerate the final two ROM-backed runtime arrays from an extracted ROM."""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROM_SHA256 = "9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9"
ENEMY_TABLE_OFFSET = 0xEAEA
ENEMY_RECORD_COUNT = 6
ENEMY_RECORD_BYTES = 8


def extract(project: Path) -> dict:
    project = project.resolve()
    rom_path = project / "local" / "rolo.md"
    rom = rom_path.read_bytes()
    digest = hashlib.sha256(rom).hexdigest()
    if digest != ROM_SHA256:
        raise ValueError(f"Unsupported ROM SHA-256: {digest}")
    sys.path.insert(0, str(project / "tools"))
    import export_level1_indexed_background as background

    _, pixels, _ = background.extract(project)
    expected_pixels = 512 * 272
    if len(pixels) != expected_pixels:
        raise ValueError(f"Unexpected indexed background size: {len(pixels)}")
    bg_digest = hashlib.sha256(pixels).hexdigest()
    if bg_digest != "cd2ca6f58527cceb4c93ce91314a98b596bb8f6a365385484019e1ef5cc99c42":
        raise ValueError(f"Unexpected indexed background hash: {bg_digest}")
    header = [
        "#pragma once", "#include <array>", "#include <cstdint>",
        "namespace rolo::level1_indexed_background_data {",
        "inline constexpr unsigned width=512,height=272;",
        f"inline constexpr std::array<std::uint8_t,{len(pixels)}> pixels{{{{",
    ]
    header += [",".join(map(str, pixels[i:i + 64])) + "," for i in range(0, len(pixels), 64)]
    header += ["}};", "}"]
    (project / "src/core/level1_indexed_background_data.hpp").write_text("\n".join(header) + "\n", encoding="utf-8")

    records = rom[ENEMY_TABLE_OFFSET:ENEMY_TABLE_OFFSET + ENEMY_RECORD_COUNT * ENEMY_RECORD_BYTES]
    if len(records) != ENEMY_RECORD_COUNT * ENEMY_RECORD_BYTES:
        raise ValueError("Enemy burst table is truncated")
    initializers = []
    for index in range(ENEMY_RECORD_COUNT):
        offset = index * ENEMY_RECORD_BYTES
        definition = struct.unpack_from(">I", records, offset)[0]
        fields = records[offset + 4:offset + 8]
        initializers.append("{0x%x,{%s}}" % (definition, ",".join(map(str, fields))))
    enemy_header = project / "src/core/enemy_phase_entries.hpp"
    text = enemy_header.read_text(encoding="utf-8")
    declaration = "inline constexpr std::array<EnemyBurstRecord,6> enemy_burst_records{{" + ",".join(initializers) + "}};"
    text, changed = re.subn(
        r"inline\s+(?:constexpr\s+)?std::array<EnemyBurstRecord,\s*6>\s*enemy_burst_records\s*(?:\{\{.*?\}\}|\{\})\s*;",
        declaration, text, count=1, flags=re.S,
    )
    if changed != 1:
        raise ValueError("Expected one enemy_burst_records declaration")
    enemy_header.write_text(text, encoding="utf-8")
    return {
        "rom_sha256": digest,
        "indexed_background": {"count": len(pixels), "sha256": bg_digest},
        "enemy_burst_records": {"count": ENEMY_RECORD_COUNT, "rom_offset": ENEMY_TABLE_OFFSET,
                                "rom_bytes": len(records), "serialization": "definition address big-endian in ROM; resource fields serialized by packer as little-endian <I4B>"},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="Isolated project copy containing local/rolo.md and tools/")
    args = parser.parse_args()
    print(json.dumps(extract(args.project), indent=2))


if __name__ == "__main__":
    main()

