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
- [Quality-of-life improvements](#quality-of-life-improvements)
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

## Quality-of-life improvements

The latest local portable build is **beta 0.1.11**. The GitHub release linked below
is still **v0.1-beta**; the later improvements listed here have been implemented
and checked locally but are not yet included in that uploaded release.

### Saves and completion

- **Three independent save slots (0.1.9).** Press Enter/Start at the title to open
  three wooden save boxes. Choose with the keyboard, controller or mouse.
  Each slot has its own campaign progress and local achievements.
- **Completion at a glance (0.1.9).** Every slot shows jigsaw, animal-rescue and
  overall completion percentages: 70 campaign jigsaw nodes and 168 animal
  placements. Overall completion gives equal weight to the two totals.
- **Unique rescue tracking (0.1.9).** Partial level rescues count, and rescuing the
  same cage again does not inflate your total.
- **Continue your existing campaign (0.1.9).** The previous single save imports
  into Save 1 while the original file is retained. Unreadable slots are protected
  from accidental replacement.
- **Map checkpoint saves.** F5/F9 save and load world-map progress; automatic map
  checkpoints use the selected profile. These are campaign saves, not instant
  saves of any gameplay frame.
- **Keep playing after the ending (0.1.8).** After either ending, return to the
  world map with progress, score and lives preserved. Revisit levels to collect
  missing jigsaw pieces and rescue remaining animals instead of starting over.
- **Portable resources and saves (0.1 beta).** Extracted resources and campaign
  saves live in `resources-v1` beside the EXE. Keep that folder when updating or
  moving your installation.

### Rewind

- **Hold to rewind (0.1.6).** Hold **LB/L1** on a controller or **Backspace** on
  the keyboard to rewind up to 300 gameplay frames, about five seconds at 60 Hz.
  Release the button to resume play.
- **Undo recent mistakes.** Rewind restores actors, projectiles, score, lives,
  terrain changes and transport state, including a recent death or Game Over
  while history is available. Animal-rescue statistics rewind too.
- **Stable scenery (0.1.10).** Fixed widescreen backgrounds retain their position
  through rewind and same-level respawns.

Rewind history clears when opening the companion menu or changing levels/entering
transitions. Music is muted during rewind. Saved files and achievements already
unlocked are not rolled back.

### Picture and controls

- **Widescreen and display options.** F8 provides widescreen, fullscreen, VSync
  and graphics-renderer selection; F11 toggles fullscreen directly.
- **Wider companion menu (0.1.4).** The green jigsaw background fills the
  widescreen menu area while its panels remain centred.
- **Wider fixed-room scenery (0.1.5).** Decorative scenery extends into the
  side gaps inside the wooden frame, including the final-boss arena.
- **Optional CRT appearance (0.1.7, enhanced in 0.1.11).** Choose **Off**,
  **Light** or **Classic** in F8. Light adds gentle softness; Classic adds wider
  pixel blending, a stronger beam/mask effect and glow. Off stays sharp.
  The choice is remembered in `crt-settings.txt` beside the EXE.
- **Clear menus and frame (0.1.11).** Save-slot, companion and settings menus
  stay clear with CRT enabled, as do the wooden frame, logo and host controls.
  Software rendering uses the sharp picture.
- **Keyboard and controller support.** SDL gamepads support movement, actions,
  menu navigation and the rewind shoulder button.
- **Local achievements.** View achievements with F7; the three-slot build keeps
  them separate for each campaign.

The CRT effect is an SDL rendering adaptation inspired by Timothy Lottes'
public-domain CRT work, rather than an exact shader port.

### Restored presentation and gameplay fixes

- **Final-boss head hits (0.1.1).** Corrected publication of the boss's vulnerable
  animation frame so head hits can damage him.
- **Final-boss electric attack (0.1.3).** Corrected a reversed terrain check that
  kept the first electric attack too high in the arena.
- **Game Over screen (0.1.2).** Replaced the placeholder with the game font,
  score, completion display and restart/load prompts.
- **Ending artwork and story (0.1.8).** Restored the original complete-ending
  bedroom illustration and large story font, extracted from the player's ROM,
  with complete and partial ending branches.
- **Reliable menu redraw (0.1.11).** Fixed the first companion-menu redraw being
  cropped on Direct3D 12 after leaving a narrow arena.

### Easier setup

- **Launch the precompiled EXE.** First run opens a Windows file picker for your
  supported ROM, validates it and extracts the required resources automatically.
  Later launches reuse those resources.
- **No local build or separate Python installation.** The portable package
  includes the setup runtime.
- **Save-preserving resource upgrades.** The newer extractor can add the ending
  artwork while retaining existing campaign saves.

Local checks cover save-slot isolation and migration, completion counts,
deterministic rewind/replay across five levels, recent-death restoration, both
ending branches and return-to-map progress. CRT checks passed on Direct3D 11,
Direct3D 12 and Vulkan. Controller rewind was checked with an SDL virtual
controller; broader physical-controller testing and full-game parity remain open.

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

- **CRT effect:** inspired by [Timothy Lottes' CRT-Lottes shader](https://github.com/libretro/slang-shaders/blob/master/crt/shaders/crt-lottes.slang), released into the public domain. Rolo uses an SDL rendering adaptation of its Gaussian beam and phosphor-mask approach, with its own Light and Classic presets. The attribution notice is included in portable builds as `LICENSES/CRT-Lottes-NOTICE.txt`.

No project-wide open-source licence or trusted-publisher signature is claimed.

