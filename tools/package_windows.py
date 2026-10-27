"""Assemble an external-resource Windows package without a ROM input."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def copy_runtime(source, target, packaging):
    version = json.loads(subprocess.check_output(
        [str(source / "python.exe"), "-c", "import json,sys; print(json.dumps(list(sys.version_info[:2])))"],
        text=True))
    tag = "".join(map(str, version))
    target.mkdir(parents=True)
    for name in ("python.exe", "python3.dll", f"python{tag}.dll", "LICENSE.txt"):
        shutil.copy2(source / name, target / name)
    for library in source.glob("vcruntime*.dll"):
        shutil.copy2(library, target / library.name)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "site-packages", "test", "tests",
                                   "idlelib", "tkinter", "ensurepip", "_test*", "_tkinter*")
    paths = []
    standard_zip = source / f"python{tag}.zip"
    if standard_zip.is_file():
        shutil.copy2(standard_zip, target / standard_zip.name)
        paths.append(standard_zip.name)
    if (source / "Lib").is_dir():
        shutil.copytree(source / "Lib", target / "Lib", ignore=ignore)
        paths.append("Lib")
    if not paths:
        raise ValueError("Python runtime has neither Lib nor a standard-library ZIP")
    shutil.copytree(source / "DLLs", target / "DLLs", ignore=ignore)
    paths += ["DLLs", ".", "import site"]
    (target / f"python{tag}._pth").write_text("\n".join(paths) + "\n", encoding="utf-8")
    shutil.copy2(packaging / "runtime/python/sitecustomize.py", target / "sitecustomize.py")
    return ".".join(map(str, version))


def assemble(engine, packaging, output, python_runtime, sdl_dll=None):
    engine, packaging, output = engine.resolve(), packaging.resolve(), output.resolve()
    if output.exists():
        raise ValueError("Package destination must be a new directory")
    if not engine.is_file():
        raise ValueError("Built engine is missing")
    output.mkdir(parents=True)
    for name in ("prepare_resources.py", "verify_pack.py", "Start-Rolo.cmd", "README.txt"):
        shutil.copy2(packaging / name, output / name)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for name in ("ExtractorTemplate", "LICENSES"):
        shutil.copytree(packaging / name, output / name, ignore=ignore)
    shutil.copy2(engine, output / "RoloGame.exe")
    if sdl_dll is not None:
        shutil.copy2(sdl_dll, output / "SDL3.dll")
    version = copy_runtime(python_runtime.resolve(), output / "runtime/python", packaging)
    python = output / "runtime/python/python.exe"
    subprocess.run([str(python), "-B", str(output / "prepare_resources.py"), "--help"], check=True)
    subprocess.run([str(python), "-B", str(output / "ExtractorTemplate/tools/export_entrance.py"), "--help"], check=True)
    count = 0
    for path in output.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(output)
        if path.suffix.lower() in {".rom", ".bin", ".rla", ".sfc", ".smc", ".sav"}:
            raise ValueError("Unexpected ROM/resource payload: " + str(relative))
        if path.name == "RoloResources.path":
            raise ValueError("Machine-specific resource locator must not be packaged")
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(relative))
        count += 1
    information = {"kind": "development candidate", "python": version,
                   "engine_sha256": hashlib.sha256(engine.read_bytes()).hexdigest(),
                   "sdl_linkage": "shared" if sdl_dll is not None else "static",
                   "files_before_metadata": count, "rom_payload_extensions": 0,
                   "runtime_extraction_playthrough_tested_by_packaging": False}
    (output / "PACKAGE-INFO.json").write_text(json.dumps(information, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(information))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--packaging", type=Path, default=Path(__file__).resolve().parents[1] / "packaging")
    parser.add_argument("--python-runtime", type=Path, default=Path(sys.executable).parent)
    parser.add_argument("--sdl-dll", type=Path)
    args = parser.parse_args()
    assemble(args.engine, args.packaging, args.output, args.python_runtime, args.sdl_dll)


if __name__ == "__main__":
    main()
