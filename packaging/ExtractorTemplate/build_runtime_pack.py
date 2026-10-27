"""Build the fixed v1 external pack from headers freshly generated from a ROM."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

import migrate

FORMATS = {
    "uint8_t": "B", "int8_t": "b", "uint16_t": "H", "int16_t": "h",
    "uint32_t": "I", "int32_t": "i",
}


def build(source: Path, manifest_path: Path, destination: Path) -> dict:
    source = source.resolve()
    manifest_path = manifest_path.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Destination must be a new directory")

    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest)
    if (manifest.get("format"), manifest.get("version"), manifest.get("encoding")) != (
        "rolo-resources", 1, "little-endian"
    ):
        raise ValueError("Unsupported resource manifest")
    entries = manifest.get("resources")
    if not isinstance(entries, list) or not entries:
        raise ValueError("Manifest has no resource entries")

    output_files = []
    seen_paths = set()
    for entry in entries:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError("Unsafe resource path: " + str(relative))
        normalized = relative.as_posix()
        if normalized in seen_paths:
            raise ValueError("Duplicate resource path: " + normalized)
        seen_paths.add(normalized)

        header_path = source / "core" / entry["header"]
        header_text = header_path.read_text(encoding="utf-8")
        declaration = migrate.declaration(header_text, entry["name"])
        kind = entry["type"]
        if kind in FORMATS:
            values = [int(value.strip(), 0) for value in declaration[3].split(",") if value.strip()]
            if len(values) != entry["count"]:
                raise ValueError(f"Array count mismatch: {entry['header']}:{entry['name']}")
            data = struct.pack("<" + FORMATS[kind] * len(values), *values)
        else:
            info = dict(entry)
            info["_resources"] = entries
            data, schema = migrate.pack_record(info, declaration[3], source / "core")
            if schema != entry.get("schema"):
                raise ValueError(f"Structured schema mismatch: {entry['header']}:{entry['name']}")

        if len(data) != entry["bytes"] or len(data) != entry["count"] * (
            struct.calcsize("<" + FORMATS[kind]) if kind in FORMATS
            else entry["schema"]["record_bytes"]
        ):
            raise ValueError(f"Resource size mismatch: {entry['header']}:{entry['name']}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            raise ValueError(f"Resource hash mismatch: {entry['header']}:{entry['name']}")
        output_files.append((relative, data))

    destination.mkdir(parents=True)
    for relative, data in output_files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (destination / "manifest.json").write_bytes(raw_manifest)
    return {
        "resources": len(output_files),
        "bytes": sum(len(data) for _, data in output_files),
        "manifest_sha256": hashlib.sha256(raw_manifest).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="ROM-generated project source root")
    parser.add_argument("manifest", type=Path, help="Pinned v1 manifest metadata")
    parser.add_argument("destination", type=Path, help="New resource pack directory")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.source, args.manifest, args.destination)))
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
