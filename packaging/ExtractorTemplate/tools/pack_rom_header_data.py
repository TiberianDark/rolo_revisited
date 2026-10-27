import argparse
import hashlib
import json
import re
import shutil
import struct
import tempfile
from pathlib import Path

HEADERS = [
    "all_native_level_data.hpp",
    "actor_pattern_data.hpp",
    "opening_data.hpp",
    "level1_indexed_background_data.hpp",
    "music_sequence_data.hpp",
    "level1_terrain_data.hpp",
    "level2_terrain_data.hpp",
    "level3_terrain_data.hpp",
    "level4_terrain_data.hpp",
    "level8_terrain_data.hpp",
]

FORMATS = {
    "uint8_t": ("B", 1, 255),
    "uint16_t": ("H", 2, 65535),
    "uint32_t": ("I", 4, 4294967295),
}

ARRAY = re.compile(
    r"inline\s+constexpr\s+std::array\s*"
    r"<\s*std::(uint8_t|uint16_t|uint32_t)\s*,\s*(\d+)\s*>"
    r"\s*(\w+)\s*\{\{(.*?)\}\}\s*;",
    re.DOTALL,
)

def parse_number(token):
    token = token.strip()
    token = re.sub(r"[uUlL]+$", "", token)
    if not re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|\d+)", token):
        raise ValueError(f"Unsupported numeric initializer: {token[:80]}")
    return int(token, 16 if token.lower().startswith("0x") else 10)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    parent = output.parent
    parent.mkdir(parents=True, exist_ok=True)

    staging = Path(tempfile.mkdtemp(prefix="rolo-pack-", dir=parent))

    manifest = {
        "format": "rolo-resources",
        "version": 1,
        "encoding": "little-endian",
        "description": "Numeric arrays extracted from ROM-generated headers",
        "resources": [],
        "excluded_structured_arrays": [],
    }

    try:
        total_bytes = 0

        for filename in HEADERS:
            header = source / "src" / "core" / filename

            if not header.is_file():
                raise FileNotFoundError(header)

            content = header.read_text(encoding="utf-8-sig")
            namespace = header.stem

            matches = list(ARRAY.finditer(content))

            print(f"\n{filename}: {len(matches)} numeric arrays")

            if not matches:
                raise RuntimeError(f"No numeric arrays found in {filename}")

            for match in matches:
                datatype, count_text, name, initializers = match.groups()
                count = int(count_text)

                # Remove C++ comments before parsing.
                initializers = re.sub(
                    r"/\*.*?\*/|//[^\r\n]*",
                    "",
                    initializers,
                    flags=re.DOTALL,
                )

                values = [
                    parse_number(value)
                    for value in initializers.split(",")
                    if value.strip()
                ]

                if len(values) != count:
                    raise ValueError(
                        f"{filename}:{name}: "
                        f"expected {count}, found {len(values)}"
                    )

                fmt, width, maximum = FORMATS[datatype]

                for value in values:
                    if value < 0 or value > maximum:
                        raise ValueError(
                            f"{filename}:{name}: value out of range: {value}"
                        )

                payload = struct.pack(
                    "<" + str(count) + fmt,
                    *values,
                )

                relative = Path(namespace) / (name + ".bin")
                target = staging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)

                # Verify the written file before recording it.
                if target.read_bytes() != payload:
                    raise RuntimeError(f"Write verification failed: {relative}")

                manifest["resources"].append({
                    "header": filename,
                    "name": name,
                    "type": datatype,
                    "count": count,
                    "bytes": count * width,
                    "path": relative.as_posix(),
                    "sha256": sha256(payload),
                })

                total_bytes += len(payload)

            # Record structured arrays not yet supported by this packer.
            structural = re.finditer(
                r"inline\s+constexpr\s+std::array\s*"
                r"<\s*([A-Za-z_]\w*)\s*,\s*(\d+)\s*>"
                r"\s*(\w+)\s*\{\{",
                content,
            )

            for item in structural:
                typename, count, name = item.groups()
                manifest["excluded_structured_arrays"].append({
                    "header": filename,
                    "name": name,
                    "type": typename,
                    "count": int(count),
                    "reason": "Requires explicit structured serialization",
                })

        manifest["resource_count"] = len(manifest["resources"])
        manifest["total_binary_bytes"] = total_bytes

        manifest_path = staging / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        # Verify all files against the generated manifest.
        for resource in manifest["resources"]:
            file_path = staging / resource["path"]
            data = file_path.read_bytes()

            if len(data) != resource["bytes"]:
                raise RuntimeError(
                    f"Resource size mismatch: {resource['path']}"
                )

            if sha256(data) != resource["sha256"]:
                raise RuntimeError(
                    f"Resource hash mismatch: {resource['path']}"
                )

        # Replace only this generated migration output.
        if output.exists():
            shutil.rmtree(output)

        staging.rename(output)

        print("\n======================================")
        print("ROLO RESOURCE PACK COMPLETED")
        print("======================================")
        print(f"Resource arrays: {manifest['resource_count']}")
        print(f"Binary bytes: {total_bytes:,}")
        print(
            "Structured arrays remaining: "
            f"{len(manifest['excluded_structured_arrays'])}"
        )
        print(f"Output: {output}")
        print(f"Manifest: {output / 'manifest.json'}")

    finally:
        if staging.exists():
            shutil.rmtree(staging)

if __name__ == "__main__":
    main()
