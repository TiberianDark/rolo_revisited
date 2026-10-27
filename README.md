# Rolo Revisited

Private development checkpoint for the native Windows Rolo to the Rescue project. This is not a finished release.

## Intended package

The goal is a precompiled game that asks the player for their own supported ROM on first launch, extracts runtime resources locally, then starts the game. The repository and release must not contain a ROM or extracted game assets.

## Current checkpoint

The uploaded snapshot contains the CMake build file, native source, bundled YMFM source and its BSD license, plus the preflight status and static-table review. It excludes the test suite, extraction tools, ROMs, extracted resources, compiled output and Python caches. The app can be compiled with `BUILD_TESTING=OFF`, but the first-run code currently validates and caches the selected ROM; the full extraction-and-launch flow is not finished and the preview still expects runtime resources.

The latest local Release compile succeeded. A limited audit found no known 64-byte fingerprints from the resource pack, but this does not prove that transformed or derived ROM data is absent. Eight regional achievement-selector arrays remain flagged. The fresh executable has not passed runtime parity and is blocked by this PC's Windows Application Control policy while unsigned.

The Windows preflight workflow now requests a static SDL3 build to remove SDL3.dll from the eventual game executable. The workflow only checks compilation; it does not sign a binary or create a release artifact.

A separate local ROM-free package candidate now includes the first-run extractor, a trimmed Python Software Foundation runtime, and the precompiled game engine. Its package verification and synthetic extractor checks pass, but it is not included in this source repository. The exact game build remains unsigned, runtime parity is unverified, and eight ROM-derived regional selector arrays still need provenance work, so this is not a public release.

## Licensing and signing

No project-wide license has been selected or approved. No copyright-clearance or release-readiness claim is made.

SignPath Foundation's free signing program requires an OSI-approved license for every component, a maintained and already released project, a documented download page, and verifiable builds from the repository. This private staging repository does not meet those conditions yet.