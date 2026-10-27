# Development checkpoint — 27 October 2026

## Verified locally

- Release engine compile on Windows.
- Fresh extraction from the pinned 512 KiB ROM: 514 resources, 1,225,363 bytes,
  plus eight external graphics packs.
- Byte-for-byte reserialization of the 514 loaded array resources.
- Eleven synthetic extractor/codec checks, eight pack corruption/path checks and
  eight native loader checks at the recorded migration checkpoint.
- Direct EXE startup, native ROM picker and extraction without a PowerShell script.
- First Enter during the intro displays the title; Enter on the title starts the
  campaign. A focused check covers four intro phases and a naturally reached title.
- Windows UI checks reached the world map and entered level 1.
- Native title-to-map handoff preserves the existing window and renderer.

These checks establish the recorded paths, not whole-game parity or completion.

## Still open

- The extended level-1 completion check fails with `Smoke exit missing` in both
  the prior and updated engines. It expects an exit actor that is absent at the
  checked point. Gameplay and test assumptions need investigation.
- The exact GitHub-produced static engine and complete development artifact need
  runtime testing after download. A passing compile/package job is narrower evidence.
- The legacy debug art browser still references project preview files. Those files
  are not part of the runtime package; ordinary campaign entry no longer uses them.
- Eight regional achievement-selector lists remain under provenance review.
  The broader review of derived constants, strings and generated data is incomplete.
- A project-wide licence has not been selected. Existing third-party licences
  remain in place. No public-release clearance or publisher certificate is claimed.

## Windows launch correction

An older unsigned executable was blocked by Windows Application Control. Subsequent
exact local binaries were successfully launched and rendered the game. Therefore
the earlier blanket statement that signing prevented the current local EXE from
running was incorrect. Current builds remain unsigned; acceptance on another PC
has not been established, and no Windows protection needs to be disabled here.
