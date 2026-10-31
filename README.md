# Rolo Revisited

[![Windows build](https://github.com/nigelwhittaker98-glitch/rolo_revisited/actions/workflows/windows-preflight.yml/badge.svg)](https://github.com/nigelwhittaker98-glitch/rolo_revisited/actions/workflows/windows-preflight.yml)
![Platform: Windows x64](https://img.shields.io/badge/platform-Windows%20x64-0078D4)

A native Windows project for **Rolo to the Rescue**, the Mega Drive / Genesis game.
The game runs through C++ gameplay code, with SDL3 for the desktop window and input,
and YMFM for FM sound synthesis.

The aim is simple: open a precompiled program, choose your own ROM once, and play.
The EXE extracts the resources it needs on your PC and finds them automatically
on later launches. You do not compile anything to play a packaged build.

## Contents

- [Scale of the project](#scale-of-the-project)
- [What it includes](#what-it-includes)
- [Quality-of-life improvements](#quality-of-life-improvements)
- [Your own ROM](#your-own-rom)
- [Download and play](#download-and-play)
- [Controls](#controls)
- [Saved data](#saved-data)
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

These counts come from the project's analysis and asset catalogues. Selector slots
include variants and screens, and graphics variants can share artwork.
See [the count definitions and evidence](docs/PROJECT_SCALE.md).

## What it includes

- **Direct EXE launch.** A Windows file picker asks for the supported ROM when
  resources are missing; extraction runs before the game opens.
- **The opening and title screen.** Enter during the intro reveals the title;
  another Enter opens the save-slot selection.
- **Native world-map and level rendering.** Explore the campaign using resources
  extracted from your own ROM.
- **Display options.** The desktop host includes widescreen, fullscreen, VSync
  and a choice of graphics renderer.
- **Keyboard and SDL gamepad input.** Controller mappings are provided through SDL3.
- **Local progress and achievements.** Save world-map progress
  and track local achievements.

## Quality-of-life improvements

### Saves and completion

- **Three independent save slots.** Press Enter/Start at the title to open
  three wooden save boxes. Choose with the keyboard, controller or mouse.
  Each slot has its own campaign progress and local achievements.
- **Completion at a glance.** Every slot shows jigsaw, animal-rescue and
  overall completion percentages: 70 campaign jigsaw nodes and 168 animal
  placements. Overall completion gives equal weight to the two totals.
- **Unique rescue tracking.** Partial level rescues count, and rescuing the
  same cage again does not inflate your total.
- **Continue your existing campaign.** The previous single save imports
  into Save 1 while the original file is retained. Unreadable slots are protected
  from accidental replacement.
- **Map checkpoint saves.** F5/F9 save and load world-map progress; automatic map
  checkpoints use the selected profile. These are campaign saves, not instant
  saves of any gameplay frame.
- **Keep playing after the ending.** After either ending, return to the
  world map with progress, score and lives preserved. Revisit levels to collect
  missing jigsaw pieces and rescue remaining animals instead of starting over.
- **Portable resources and saves.** Extracted resources and campaign
  saves live in `resources-v1` beside the EXE. Keep that folder when updating or
  moving your installation.

### Rewind

- **Hold to rewind.** Hold **LB/L1** on a controller or **Backspace** on
  the keyboard to rewind up to 300 gameplay frames, about five seconds at 60 Hz.
  Release the button to resume play.
- **Undo recent mistakes.** Rewind restores actors, projectiles, score, lives,
  terrain changes and transport state, including a recent death or Game Over
  while history is available. Animal-rescue statistics rewind too.
- **Stable scenery.** Fixed widescreen backgrounds retain their position
  through rewind and same-level respawns.

Rewind history clears when opening the companion menu or changing levels/entering
transitions. Music is muted during rewind. Saved files and achievements already
unlocked are not rolled back.

### Picture and controls

- **Widescreen and display options.** F8 provides widescreen, fullscreen, VSync
  and graphics-renderer selection; F11 toggles fullscreen directly.
- **Wider companion menu.** The green jigsaw background fills the
  widescreen menu area while its panels remain centred.
- **Wider fixed-room scenery.** Decorative scenery extends into the
  side gaps inside the wooden frame, including the final-boss arena.
- **Optional CRT appearance.** Choose **Off**,
  **Light** or **Classic** in F8. Light adds gentle softness; Classic adds wider
  pixel blending, a stronger beam/mask effect and glow. Off stays sharp.
  The choice is remembered in `crt-settings.txt` beside the EXE.
- **Clear menus and frame.** Save-slot, companion and settings menus
  stay clear with CRT enabled, as do the wooden frame, logo and host controls.
  Software rendering uses the sharp picture.
- **Keyboard and controller support.** SDL gamepads support movement, actions,
  menu navigation and the rewind shoulder button.
- **Local achievements.** View achievements with F7; the three-slot build keeps
  them separate for each campaign.

The CRT effect is an SDL rendering adaptation inspired by Timothy Lottes'
public-domain CRT work, rather than an exact shader port.

### Restored presentation and gameplay fixes

- **Final-boss head hits.** Corrected publication of the boss's vulnerable
  animation frame so head hits can damage him.
- **Final-boss electric attack.** Corrected a reversed terrain check that
  kept the first electric attack too high in the arena.
- **Game Over screen.** Replaced the placeholder with the game font,
  score, completion display and restart/load prompts.
- **Ending artwork and story.** Restored the original complete-ending
  bedroom illustration and large story font, extracted from the player's ROM,
  with complete and partial ending branches.
- **Reliable menu redraw.** Fixed the first companion-menu redraw being
  cropped on Direct3D 12 after leaving a narrow arena.

### Easier setup

- **Launch the precompiled EXE.** First run opens a Windows file picker for your
  supported ROM, validates it and extracts the required resources automatically.
  Later launches reuse those resources.
- **No local build or separate Python installation.** The portable package
  includes the setup runtime.
- **Save-preserving resource upgrades.** The extractor can add the ending
  artwork while retaining existing campaign saves.

## Your own ROM

You must supply your own **512 KiB Mega Drive / Genesis Rolo to the Rescue ROM**.
Only the revision matching the following SHA-256 is currently supported:

```text
9478d47cc1883df42f3714ea485aedd71b541274eb45a3aa7c49f4a3518305e9
```

The file is checked by its contents, not its name. Renaming a different revision
will not make it compatible. The picker lists `.bin`, `.md` and `.gen` files.

No ROM or extracted runtime payload files are included in the download.
The extractor reads your selected ROM, generates resources on your PC and leaves
the original file unchanged.

## Download and play

1. Open [Releases](https://github.com/nigelwhittaker98-glitch/rolo_revisited/releases)
   and download the portable Windows ZIP from the release's **Assets** section.
   GitHub's automatic source-code archives are for development.
2. Extract the whole ZIP into a writable folder and keep all supplied files together.
3. Double-click **RoloGame.exe**. On first launch, choose your supported ROM and
   wait for extraction to finish. No compilation or separate Python installation is needed.
4. Press **Enter** to reveal the title, then **Enter/Start** to choose a save slot.
   Select an existing campaign or an empty slot, then press **Space** on the world
   map to enter a level.

Later launches reuse the extracted resources. To update, close the game, extract
the complete new package over your installation and keep `resources-v1` for your
resources and saves.

## Controls

| Action | Keyboard |
|---|---|
| Reveal title / open save slots / confirm | Enter |
| Move / navigate world-map routes | Arrow keys |
| Jump / enter a level from the map | Space |
| Action input | X |
| Companion menu during gameplay | Enter |
| Pause during gameplay | P |
| Hold to rewind gameplay | Backspace / controller LB or L1 |
| Back from save-slot selection | Escape / controller B |
| Display options | F8 |
| Local achievements | F7 |
| Toggle fullscreen | F11 |
| Save / load world-map progress | F5 / F9 |

SDL gamepads use the D-pad or left stick for movement, the south face button for
Space, west/east face buttons for Z/X, and Start for Enter.

## Saved data

Portable builds save extracted resources beside **RoloGame.exe**:

```text
resources-v1\
```

Use a writable installation folder. Move the complete folder to keep its resources.
A fresh installation asks for your ROM even if another copy has saved data in AppData.

Each save slot has its own campaign and achievement files:

- `rolo-slot-1.sav` through `rolo-slot-3.sav`
- `rolo-achievements-slot-1.sav` through `rolo-achievements-slot-3.sav`

An existing `rolo-progress.sav` imports into Save 1 without removing the original.
Back up `resources-v1` to keep your campaign progress.

The CRT preference is saved in `crt-settings.txt` beside the EXE. Renderer
preferences use SDL's preference folder. Setup errors are recorded in `setup.log`
beside the EXE.

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

