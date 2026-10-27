# Rolo Revisited

Private staging repository for the ROM-free native Windows build of Rolo to the Rescue.

## Project goal

The intended Windows package contains a precompiled native game and a first-run launcher. The player selects their own supported ROM; the launcher validates it, extracts the runtime data locally, and starts the game. The repository and release must not contain the ROM or extracted game assets.

## Current status

This repository is a setup checkpoint and does not yet contain the game source or release files.

A clean local source stage rebuilt the x64 Release game executable with runtime asset copying disabled. The build succeeded. A limited scan found zero known 64-byte fingerprints from the resource pack in that executable. The executable was not run; the scan does not prove that transformed or otherwise derived ROM data is absent.

The candidate is not ready to distribute: the latest native parity run was blocked by Windows Application Control, the unsigned game executable is blocked by this PC's current policy, and provenance review remains for 19 small static tables.

A project-wide license has not been selected. No release or copyright-clearance claim is made.
