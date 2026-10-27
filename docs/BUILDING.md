# Building Rolo Revisited on Windows

Players using a complete development ZIP do not need a compiler or Python.
These instructions are for building from the source repository.

## Requirements

- Windows x64 and Visual Studio with Desktop development with C++ and a Windows SDK.
- CMake 3.24 or newer.
- Git and [vcpkg](https://github.com/microsoft/vcpkg).
- CPython 3.13 from the [Python Software Foundation](https://www.python.org/) for packaging.
- Your own supported ROM when testing extraction or gameplay locally.

## Compile the engine

After bootstrapping vcpkg, run these commands in PowerShell, replacing the vcpkg
path with the location of your installation:

```powershell
& C:\tools\vcpkg\vcpkg.exe install sdl3:x64-windows-static
cmake -S . -B build -A x64 `
  -DCMAKE_TOOLCHAIN_FILE=C:/tools/vcpkg/scripts/buildsystems/vcpkg.cmake `
  -DVCPKG_TARGET_TRIPLET=x64-windows-static `
  -DROLO_SDL3_STATIC=ON `
  -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded `
  -DBUILD_TESTING=OFF `
  -DROLO_COPY_RUNTIME_PACKS=OFF
cmake --build build --config Release --target rolo_native
```

`build/Release/rolo_native.exe` is the engine. The static configuration links SDL3
into it. It still needs the setup tools beside it for a first launch without saved
resources. Do not distribute only this file as the complete game package.

The wider historical test suite is not completely mirrored in this staging repo,
so the engine workflow uses `BUILD_TESTING=OFF`.

## Assemble a complete package

Run this using the official CPython installation that should supply the packaged runtime:

```powershell
python tools/package_windows.py `
  --engine build/Release/rolo_native.exe `
  --output dist/rolo-revisited-windows-dev
```

The script copies the extractor template and licence notices, assembles an isolated
Python runtime from that installation, checks sibling-script imports and audits the
file list for ROM/resource payload extensions. No ROM is read during packaging.

For a locally built engine using shared SDL3, also pass `--sdl-dll path/to/SDL3.dll`.
GitHub's static build does not need this flag.

Extracting resources requires the complete folder. Run its `RoloGame.exe`, choose
the supported ROM, wait for setup and check the title screen, map and level entry.
Never commit the resulting resources, local locator or saved games.

## Focused title-input check

`tests/opening_start_tests.cpp` checks all four intro phases and the existing title
against an external resource pack. It requires a locally extracted pack and is not
an asset-free GitHub test. It does not prove a full gameplay playthrough.

## GitHub Actions

The Windows workflow builds the engine, runs the package assembler and uploads
`rolo-revisited-windows-dev`. Artifact upload is a development checkpoint, not a
GitHub Release, trusted signature or proof that a ROM-driven playthrough passed.
