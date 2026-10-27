"""Restore the final small runtime tables from a validated Rolo ROM into generated headers."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

SUPPORTED_ROM_SHA256 = "9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9"

# Header, array, C++ element type, count, ROM offset, element width.
TABLES = [
    ("actor_bounce_motion.hpp", "bounce_direction_bytes", "uint8_t", 6, 0xB7B2, 1),
    ("actor_choreography_chain.hpp", "choreography_offsets", "int8_t", 18, 0xBE08, 1),
    ("actor_contact_family.hpp", "actor_contact_thresholds", "uint16_t", 8, 0xE10A, 2),
    ("actor_contact_family.hpp", "actor_contact_speeds", "uint8_t", 6, 0xDA6C, 1),
    ("actor_contact_family.hpp", "actor_contact_y_offsets", "int16_t", 4, 0xC60A, 2),
    ("actor_graphic_phase_data.hpp", "projectiles", "uint8_t", 18, 0xF590, 1),
    ("actor_graphic_phase_data.hpp", "anchors", "uint8_t", 18, 0xF618, 1),
    ("actor_phase_cycle.hpp", "actor_phase_cycle_delays", "uint8_t", 4, 0xE14A, 1),
    ("actor_phase_emitter_data.hpp", "jump", "uint8_t", 32, 0xEDF8, 1),
    ("actor_phase_emitter_data.hpp", "emit", "uint8_t", 112, 0xEEB8, 1),
    ("actor_probe_patrol.hpp", "actor_probe_patrol_steps", "uint8_t", 22, 0xDBA8, 1),
    ("camera_data.hpp", "sine", "int16_t", 512, 0x1582A, 2),
    ("camera_data.hpp", "modes", "uint8_t", 80, 0x4AEDA, 1),
    ("ending_data.hpp", "good_text", "uint8_t", 214, 0x13A10, 1),
    ("ending_data.hpp", "bad_text", "uint8_t", 261, 0x13AE6, 1),
    ("ending_data.hpp", "white", "uint16_t", 16, 0x4B7C8, 2),
    ("ending_data.hpp", "bad_palette", "uint16_t", 16, 0x4B5AA, 2),
    ("player_terrain_response.hpp", "player_terrain_bob", "uint8_t", 4, 0x9472, 1),
    ("score_decimal.hpp", "score_decimal_divisors", "uint32_t", 8, 0x71FA, 4),
    ("startup_logo_raster.hpp", "heights", "uint8_t", 9, 0xC46, 1),
    ("startup_logo_raster.hpp", "slopes", "uint8_t", 27, 0xC4F, 1),
    ("startup_logo_raster.hpp", "caps", "uint8_t", 9, 0xC73, 1),
    ("status_hud_templates.hpp", "status_hud_templates", "uint8_t", 40, 0x5216, 1),
    ("timed_projectile_phases.hpp", "timed_projectile_wave", "int8_t", 16, 0xE468, 1),
    ("world_map.hpp", "world_map_absent_edges", "uint16_t", 4, 0xA656, 2),
    ("world_map.hpp", "world_map_missing_next_to_present", "uint16_t", 4, 0xA65E, 2),
    ("world_map.hpp", "world_map_present_next_to_missing", "uint16_t", 4, 0xA666, 2),
]

FORMATS = {"uint8_t": "B", "int8_t": "b", "uint16_t": "H", "int16_t": "h", "uint32_t": "I"}


def values_from_rom(rom: bytes, kind: str, count: int, offset: int, width: int):
    raw = rom[offset:offset + count * width]
    if len(raw) != count * width:
        raise ValueError(f"ROM table out of range at 0x{offset:X}")
    fmt = {1: "b" if kind == "int8_t" else "B", 2: "h" if kind == "int16_t" else "H", 4: "I"}[width]
    return list(struct.unpack(">" + fmt * count, raw)), raw


def export(rom_path: Path, source: Path, manifest_path: Path, bootstrap: bool = False):
    rom = rom_path.read_bytes()
    if len(rom) != 524288 or hashlib.sha256(rom).hexdigest() != SUPPORTED_ROM_SHA256:
        raise ValueError("Unsupported ROM: expected the verified 512 KiB Rolo revision")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["resources"]
    by_key = {(e["header"], e["name"]): e for e in entries}
    changed = []
    for header, name, kind, count, offset, width in TABLES:
        values, raw = values_from_rom(rom, kind, count, offset, width)
        path = f"direct_runtime_tables/{header.removesuffix('.hpp')}/{name}.bin"
        data = struct.pack("<" + FORMATS[kind] * count, *values)
        digest = hashlib.sha256(data).hexdigest()
        entry = by_key.get((header, name))
        if entry is None:
            if not bootstrap:
                raise ValueError(f"Manifest is missing {header}:{name}")
            entry = {"header": header, "name": name, "type": kind, "count": count,
                     "bytes": len(data), "path": path, "sha256": digest}
            entries.append(entry)
            by_key[(header, name)] = entry
        if (entry["type"], entry["count"], entry["bytes"], entry["path"], entry["sha256"]) != (kind, count, len(data), path, digest):
            raise ValueError(f"ROM table differs from pinned manifest: {header}:{name}")
        p = source / "core" / header
        text = p.read_text(encoding="utf-8")
        pattern = re.compile(rf"((?:inline\s+)?(?:constexpr\s+)?(?:std::)?array\s*<\s*(?:std::)?{re.escape(kind)}\s*,\s*{count}\s*>\s*{re.escape(name)}\s*)\{{[^{{}}]*\}}")
        replacement = r"\g<1>{" + ",".join(str(v) for v in values) + "}"
        updated, n = pattern.subn(lambda m: m.group(1) + "{" + ",".join(map(str, values)) + "}", text)
        if n != 1:
            raise ValueError(f"Expected one source declaration for {header}:{name}; found {n}")
        p.write_text(updated, encoding="utf-8")
        changed.append({"header": header, "name": name, "rom_offset": offset,
                        "source_bytes": len(raw), "pack_sha256": digest})
    if bootstrap:
        manifest["resources"].sort(key=lambda e: (e["header"], e["name"]))
        manifest["resource_count"] = len(entries)
        manifest["total_binary_bytes"] = sum(e["bytes"] for e in entries)
        manifest["expanded_numeric_arrays"] = sum(
            e["type"] in FORMATS for e in entries
        )
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--bootstrap", action="store_true", help="append and pin the new table entries")
    args = parser.parse_args()
    print(json.dumps(export(args.rom, args.source, args.manifest, args.bootstrap), indent=2))


if __name__ == "__main__":
    main()
