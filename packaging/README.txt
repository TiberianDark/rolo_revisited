Rolo to the Rescue - direct-launch ROM-free candidate

Extract the complete download into one folder and double-click RoloGame.exe.
Keep the runtime and ExtractorTemplate folders beside it.

On first launch the EXE opens a Windows ROM picker. It validates the supported
512 KiB ROM, extracts 514 runtime resources and eight graphics packs, verifies
the results, then opens the game. Subsequent launches find the saved resources
automatically. Start-Rolo.cmd is an optional shortcut to the same EXE.
No rebuilding or PowerShell script execution is required on the player's PC.

Enter during the intro reveals the title screen. Press Enter on the title
screen to start the campaign; Space enters a level from the world map.

Saved resources normally live in LocalAppData\RoloToTheRescue\resources-v1.
An optional local RoloResources.path file can point to an existing resource
folder. Distribution archives omit that machine-specific locator.

The native title-to-world-map handoff passed, preserving the same window and
renderer. Gameplay rendered and ran 200 updates using the external pack with
no project BMP files. A separate level-completion smoke assertion still fails
with "Smoke exit missing" in both the prior and updated game executables.
This existing completion issue has not been fixed by the startup changes.

Fresh extraction verified 514 resources totaling 1,225,363 bytes, plus all
eight graphics packs. The game and SDL3.dll are unsigned. The current local
EXE runs on Windows; the separately produced GitHub EXE still needs its own
runtime check. The Python runtime is CPython 3.13.16 from the Python Software
Foundation, with its license at runtime\python\LICENSE.txt.

This candidate contains no ROM or extracted resource payload files. Eight
game-specific regional selector lists and the broader provenance/licensing
review remain unresolved. This is not a cleared public release.

