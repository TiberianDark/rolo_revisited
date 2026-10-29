# Rolo Revisited

[![Windows development build](https://github.com/nigelwhittaker98-glitch/rolo_revisited/actions/workflows/windows-preflight.yml/badge.svg)](https://github.com/nigelwhittaker98-glitch/rolo_revisited/actions/workflows/windows-preflight.yml)
![Platform: Windows x64](https://img.shields.io/badge/platform-Windows%20x64-0078D4)
![Status: in development](https://img.shields.io/badge/status-in%20development-orange)

A native Windows project for **Rolo to the Rescue**, the Mega Drive / Genesis game.
The game runs through C++ gameplay code, with SDL3 for the desktop window and input,
and YMFM for FM sound synthesis.

The aim is simple: open a precompiled program, choose your own ROM once, and play.
The EXE extracts the resources it needs on your PC and finds them automatically
on later launches. You do not compile anything to play a packaged build.

**This is an experimental development build.** Direct launching, ROM extraction,
the title screen, world-map entry and entering level 1 have been checked locally.
A full playthrough and complete parity with the original game are not established.

## Contents

- [Scale of the project](#scale-of-the-project)
- [What it includes](#what-it-includes)
- [Your own ROM](#your-own-rom)
- [Download and play](#download-and-play)
- [Controls](#controls)
- [Saved data](#saved-data)
- [Development status](#development-status)
- [Building from source](#building-from-source)
- [Reporting a problem](#reporting-a-problem)
- [Credits and licences](#credits-and-licences)

## Scale of the project

A 512 KiB cartridge holds a substantial amount of interconnected code and data.
The preserved analysis checkpoint maps **747 original routine entry points to
native C++ implementations across 205 implementation headers**. That work covers
startup, rendering, terrain streaming, cameras, actor management, movement,
collision, animation, companions, world-map routes, scoring and sound interfaces.

| Work recorded | Count |
|---|---:|
| Original routine entry points with native C++ source links | **747** |
| Decoded 68000 instructions in the analysis inventory | **16,191** |
| Recorded call sites | **1,438** |
| Actor definitions / distinct actor handlers | **192 / 65** |
| Catalogued animation-frame descriptors / graphics variants | **466 / 581** |
| Candidate animation programs catalogued | **332** |
| Decoded tile patterns / decoded graphics banks | **5,362 / 8** |
| Map layers catalogued and rendered / selector slots | **160 / 80** |
| Unique foreground/background layouts catalogued | **87** |
| Music-data sources catalogued | **31** |
| External runtime array resources / generated graphics packs | **514 / 8** |

The recorded verification checkpoint marks **745 payload contracts and two reviewed
native platform substitutions** as verified within their stated local scopes.
Its level-1 analysis subset contains **434 entries**, including 12 sound-interface
entries. The external array pack also passed byte-for-byte reserialization of all
514 resources.

These are counts from the tracked analysis and asset catalogues. Selector slots
include variants and screens; graphics variants can share artwork. Scoped routine
verification does not establish a completed playthrough or full-game fidelity.
See [the count definitions and evidence](docs/PROJECT_SCALE.md).

## What it includes

- **Direct EXE launch.** A Windows file picker asks for the supported ROM when
  resources are missing; extraction runs before the game opens.
- **The opening and title screen.** Enter during the intro reveals the title;
  another Enter starts the campaign.
- **Native world-map and level rendering.** Starting the game uses the external
  resource pack instead of searching the original project for preview BMP files.
- **Display options.** The desktop host includes widescreen, fullscreen, VSync
  and a choice of graphics renderer.
- **Keyboard and SDL gamepad input.** Controller mappings are provided through SDL3.
- **Local progress and achievements.** The current host can save world-map progress
  and record its local achievement state.

These describe the current implementation, not a guarantee that every scene or
gameplay path is complete. See the [status notes](docs/STATUS.md).

## Your own ROM

You must supply your own **512 KiB Mega Drive / Genesis Rolo to the Rescue ROM**.
Only the revision matching the following SHA-256 is currently supported:

```text
9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9
```

The file is checked by its contents, not its name. Renaming a different revision
will not make it compatible. The picker lists `.bin`, `.md` and `.gen` files.

No ROM or extracted runtime payload files are included in the development package.
The extractor reads the selected ROM, generates resources locally and leaves the
original file unchanged. Source provenance review is still in progress; this is
not a claim that every game-derived constant has been cleared for publication.

## Download and play

The first **[v0.1-beta portable Windows release](https://github.com/nigelwhittaker98-glitch/rolo_revisited/releases/tag/v0.1-beta)** is available to repository collaborators. The repository remains private.
Download `Rolo-Revisited-0.1-beta-portable-Windows-x64.zip` from its Assets section.
GitHub's automatic source-code archives are for development, not playing.

Additional development packages are available from [GitHub Actions](https://github.com/nigelwhittaker98-glitch/rolo_revisited/actions/workflows/windows-preflight.yml).

1. Download the portable Windows ZIP from the beta release's **Assets** section.
2. Extract the whole ZIP into a folder. Keep `runtime`, `ExtractorTemplate`,
   `prepare_resources.py` and the other supplied files beside the game.
3. Double-click **RoloGame.exe**. On first launch, choose your supported ROM and
   allow setup to finish. The game verifies 514 runtime resources and eight graphics
   packs before opening. No CMD launcher, PowerShell script or local rebuild is needed.
4. Press **Enter** to reveal the title screen, **Enter** on the title to start,
   then **Space** on the world map to enter a level.

Later launches reuse the verified resources. The bundled Python runtime is used
only for setup; players do not need to install Python separately.

Development binaries are unsigned. The current local build has run on Windows;
that does not establish reputation or acceptance on every Windows configuration.
The project does not require disabling Windows protections.

## Controls

| Action | Keyboard |
|---|---|
| Reveal title / start from title | Enter |
| Move / navigate world-map routes | Arrow keys |
| Jump / enter a level from the map | Space |
| Action input | X |
| Companion menu during gameplay | Enter |
| Pause during gameplay | P |
| Display options | F8 |
| Local achievements | F7 |
| Toggle fullscreen | F11 |
| Save / load world-map progress | F5 / F9 |

SDL gamepads use the D-pad or left stick for movement, the south face button for
Space, west/east face buttons for Z/X, and Start for Enter. Gamepad behaviour across
different devices still needs broader playtesting.

## Saved data

Portable builds save extracted resources beside **RoloGame.exe**:

```text
resources-v1\
```

Use a writable installation folder. Move the complete folder to keep its resources.
A fresh installation asks for your ROM even if another copy has saved data in AppData.

That folder also holds `rolo-progress.sav`, `rolo-achievements.sav` and diagnostic
logs generated by the host. A failed extraction writes `setup.log` in its parent
folder. Renderer preferences use SDL's `NativeRolo/RoloToTheRescue` preference folder.

Portable builds ignore the old AppData resource location and `RoloResources.path` locator.

## Development status

Local checks have verified fresh extraction, all 514 array resources reserialized
byte for byte, direct Windows launching, title input, the title-to-map handoff,
and entering level 1. The exact binary built by GitHub needs its own runtime check.

An extended level-1 completion test currently stops at **`Smoke exit missing`**:
it cannot find the expected exit actor. The previous EXE fails the same check.
Whether the fault is in gameplay or the test's assumptions remains unresolved.

Eight regional achievement-selector lists and the broader source provenance and
licensing review also remain open. A project-wide licence has not been selected.
The repository remains a private development checkpoint while that work continues.

See [docs/STATUS.md](docs/STATUS.md) for the tested scope and outstanding work.

## Building from source

The Windows build uses CMake, an MSVC C++20 toolchain and SDL3. The packaging step
adds the extractor and a CPython runtime; building the engine alone does not make
a complete first-run download.

See [docs/BUILDING.md](docs/BUILDING.md) for source-build and packaging instructions.
The [Windows workflow](.github/workflows/windows-preflight.yml) performs both steps
without supplying a ROM to the runner.

## Reporting a problem

Please include the build or commit, what you pressed, what you expected and the
exact error message. A screenshot and the relevant part of `setup.log` can help.
**Do not attach your ROM or extracted resource files.** Review logs before sharing
them because paths can contain your Windows account name.

## Credits and licences

*Rolo to the Rescue* was developed by Vectordean and published by Electronic Arts.
The original game's characters, artwork, music and other content belong to their
respective rights holders. This project is not affiliated with those rights holders.

Third-party components include:

- [SDL3](https://libsdl.org/) — zlib licence; text in [packaging/LICENSES/SDL3-LICENSE.txt](packaging/LICENSES/SDL3-LICENSE.txt).
- [YMFM](https://github.com/aaronsgiles/ymfm) by Aaron Giles — BSD 3-Clause; [licence text](third_party/ymfm/LICENSE).
- [CPython](https://www.python.org/) — Python Software Foundation licence; the runtime's licence is included in packaged builds.

No project-wide open-source licence or trusted-publisher signature is claimed.

