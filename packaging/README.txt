Rolo to the Rescue — ROM-free build candidate v2

This folder contains a precompiled native game engine and a first-run extractor. It does not include a ROM or extracted game resources. On first launch, Start-Rolo.cmd asks for the supported 512 KiB ROM, checks its length and SHA-256, extracts the runtime resources into the current Windows account's LocalAppData folder, verifies the complete 514-resource pack, then starts RoloGame.exe. The ROM is read directly and is never modified. Temporary working files are removed after setup. No compilation is performed on the player's computer.

The resource loader passed eight native checks. A native parity check loaded all 514 arrays from the external pack and reserialized them byte-for-byte. Eleven synthetic codec and extraction tests and eight pack corruption/path-safety tests also passed. The pack verifier confirmed 514 resources totaling 1,225,363 bytes.

The embedded extractor runtime is CPython 3.13.16 from the Python Software Foundation. Its official license is included at runtime\python\LICENSE.txt.

The game executable and SDL3.dll are unsigned. Windows Application Control blocked a prior game build before it ran; this exact executable has not been launched on that protected PC. The project still needs a trusted signing path for that Windows configuration. Eight game-specific regional selector arrays also need provenance review. The technical scan and successful resource parity test do not establish copyright clearance.

Files:
- RoloGame.exe and SDL3.dll: precompiled game runtime and SDL dependency.
- Start-Rolo.cmd and RoloLauncher.ps1: first-run selection, extraction, validation and launch.
- ExtractorTemplate: source and scripts used to extract resources from the ROM.
- runtime\python: trimmed PSF Python runtime, with license.
- verify_pack.py: resource integrity verification.

This is a test candidate, not a public release. It is unsigned and is not cleared for publication.
