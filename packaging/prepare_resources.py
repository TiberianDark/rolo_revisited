"""Extract an external resource pack from the player's validated ROM."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

import verify_pack

ROM_SHA256 = "9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9"
MANIFEST_SHA256 = "c1d41a485c8e3f383d7a3745b409d12bb66450865648c8453c635aa87d3ce95e"
ASSETS = (
    "entrance-assets.rla", "player-assets.rla", "level1-player-assets.rla",
    "first-enemy-assets.rla", "level1-object-assets.rla",
    "world-cursor-assets.rla", "world-bunny-assets.rla", "forest-log-assets.rla",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_ready(root):
    if digest(root / "manifest.json") != MANIFEST_SHA256:
        raise ValueError("Resource manifest differs from this engine version")
    result = verify_pack.verify(root)
    for name in ASSETS:
        path = root / name
        with path.open("rb") as resource:
            if path.stat().st_size <= 12 or resource.read(8) != b"RLOAS01\0":
                raise ValueError("Invalid external game asset: " + name)
    return result


def prepare(rom, destination):
    rom = rom.resolve(strict=True)
    destination = destination.resolve()
    if rom.stat().st_size != 524288 or digest(rom) != ROM_SHA256:
        raise ValueError("Unsupported ROM: expected the verified 512 KiB Rolo revision")
    try:
        verify_ready(destination)
        print("Saved resources already verified.", flush=True)
        return
    except (OSError, ValueError, KeyError):
        pass

    app_root = Path(__file__).resolve().parent
    template = app_root / "ExtractorTemplate"
    destination.parent.mkdir(parents=True, exist_ok=True)
    staged_pack = destination.parent / ("resources-v1-new-" + uuid.uuid4().hex)
    try:
        with tempfile.TemporaryDirectory(prefix="RoloExtract-", dir=destination.parent) as temporary:
            stage = Path(temporary)
            for name in ("assets", "bin", "docs", "local", "migration"):
                (stage / name).mkdir()
            for name in ("src", "tools"):
                shutil.copytree(template / name, stage / name,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for name in ("run_initial_exporters.py", "run_array_exporters.py",
                         "build_runtime_pack.py", "extract_last_runtime_arrays.py",
                         "migrate.py", "verify_pack.py"):
                shutil.copy2(template / name, stage / name)
            shutil.copy2(template / "manifest.json", stage / "migration/manifest.json")
            local_rom = stage / "local/rolo.md"
            shutil.copyfile(rom, local_rom)
            if digest(local_rom) != ROM_SHA256:
                raise ValueError("ROM changed while it was being read")

            environment = dict(os.environ, ROLO_PYTHON=sys.executable, PYTHONUTF8="1")

            def run(script, *arguments):
                print("EXTRACT:", script, flush=True)
                subprocess.run([sys.executable, str(stage / script), *map(str, arguments)],
                               cwd=stage, env=environment, check=True)

            run("tools/inventory_rom.py", local_rom, "--project", stage)
            run("tools/dump_images.py", local_rom, "--out", stage / "assets/extracted")
            run("tools/inventory_assets.py", local_rom, "--out", stage / "assets/extracted/catalog")
            run("tools/inventory_first_level.py", local_rom, "--project", stage)
            run("tools/inventory_animations.py", local_rom, "--out", stage / "assets/extracted/catalog/animations")
            run("tools/bulk_extract_levels.py", "--project", stage, "--rom", local_rom)
            run("tools/rebuild_connected_level_assets.py")
            run("tools/export_player.py", local_rom, "--project", stage)
            run("tools/export_world_cursor.py")
            run("tools/export_world_bunny.py")
            run("tools/export_first_enemy.py", local_rom, "--project", stage)
            run("tools/export_enemy_preview_assets.py")
            run("tools/export_entrance.py", local_rom, "--out", stage / "src/core/entrance_data.hpp")
            run("tools/export_preview.py", local_rom, "--header", stage / "src/core/entrance_data.hpp",
                "--out", stage / "bin/entrance-assets.rla")
            run("tools/export_ending_assets.py")
            run("tools/export_forest_log.py")
            run("tools/export_opening.py", local_rom, "--project", stage)
            run("run_initial_exporters.py", stage)
            run("run_array_exporters.py", stage)
            run("extract_last_runtime_arrays.py", stage)
            run("tools/export_direct_runtime_tables.py", local_rom, stage / "src", stage / "migration/manifest.json")
            run("build_runtime_pack.py", stage / "src", stage / "migration/manifest.json", staged_pack)
            for name in ASSETS:
                shutil.copy2(stage / "bin" / name, staged_pack / name)
            result = verify_ready(staged_pack)
            print("VERIFIED:", result, flush=True)
            previous = None
            if destination.exists():
                previous = destination.with_name(destination.name + ".previous-" + uuid.uuid4().hex)
                destination.rename(previous)
            try:
                staged_pack.rename(destination)
            except OSError:
                if previous is not None:
                    previous.rename(destination)
                raise
    finally:
        if staged_pack.exists() and staged_pack.parent.resolve() == destination.parent.resolve():
            shutil.rmtree(staged_pack)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", required=True, type=Path)
    parser.add_argument("--resource-root", required=True, type=Path)
    arguments = parser.parse_args()
    try:
        prepare(arguments.rom, arguments.resource_root)
    except Exception as error:
        print("Rolo setup failed:", error, file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
