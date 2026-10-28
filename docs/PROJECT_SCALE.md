# Project scale and count definitions

Counts checked on 28 October 2026 against the preserved original-project analysis
reports and the current migrated C++ source tree. These describe the tracked
inventory and its recorded verification checkpoint; the full historical suite
was not rerun to make this documentation update.

## Code mapping

The analysis inventory contains **747 distinct routine-entry addresses**. Every
entry has a `native_sources` mapping. Together those mappings reference **205 C++
implementation headers**, all present in the current migrated source snapshot.
Several entries share a header; this is not a claim of 747 separate `.cpp` files
or one independent function for every original entry.

The same inventory records **16,191 decoded instructions**, **1,438 distinct call
sites**, **22 dispatch tables**, **192 actor definitions**, **65 distinct actor
handlers** and **2,033 object-field reference records**.

The preserved contract checkpoint records **747 scoped verified entries**:
**745 payload contracts** and **two reviewed native platform substitutions**.
Its level-1 subset is **434 entries**, comprising **422 non-audio entries and 12
sound-interface entries**. This subset overlaps the global total and must not be
added to it.

Verification applies to each record's stated inputs, state assumptions and local
behaviour. It does not establish complete caller integration, all reachable game
states or an end-to-end playthrough. In particular, the current level-completion
test issue remains open as documented in [STATUS.md](STATUS.md).

## Graphics, animation and map catalogues

| Inventory | Count and meaning |
|---|---|
| Graphics banks | Eight decoded banks, containing a total of **5,362 tile patterns** |
| Animation frames | **466 frame-descriptor records** |
| Graphics variants | **581 variant records** associated with those descriptors |
| Animation programs | **332 conservative candidate programs** catalogued from animation tables |
| Map layers | **160 foreground/background layer records** catalogued and rendered across 80 selector slots |
| Unique layouts | **87 unique foreground/background layouts** in the asset catalogue |
| Music | **31 music-data sources** in the catalogue |

Tile-pattern totals count entries across the decoded banks, not thousands of
independent finished illustrations. Frame descriptors and graphics variants can
refer to shared content. The animation candidate set includes conservative table
prefixes and is not proof that every candidate is admitted during gameplay.

Selector slots include variants, shared layouts and screens. They must not be
described as 80 distinct completed playable levels. The visual inventory separately
records **71 unique foreground layouts** and **70 world-map node selectors**.

## External resource work

The current first-run extractor generates **514 array resources**, totalling
**1,225,363 bytes**, and **eight external graphics packs** from the supported ROM.
All 514 loaded array resources passed byte-for-byte reserialization checks. The
graphics packs are additional files and are not included in that array-byte total.

This work includes explicit portable serialization for structured records and
resource validation, rather than relying on native pointers or compiler memory
layouts in files.

## Evidence used

The preserved analysis reports are generated locally from the user's ROM; this
document carries aggregate counts and definitions rather than their raw records.

| Preserved report | Evidence used |
|---|---|
| `docs/stage9/inventory.json` | Distinct entry addresses, C++ source links, instructions, calls, actors and dispatch tables |
| `docs/stage9/green-progress-current.json` | Recorded scoped-contract totals and level-1 subset |
| `docs/stage9/all-level-coverage.json` | Selector and rendered-layer totals |
| `assets/extracted/catalog/manifest.json` | Layouts, graphics banks, tile patterns and music sources |
| `assets/extracted/catalog/animations/manifest.json` | Frame descriptors, variants and candidate animation programs |
| `assets/extracted/visual-inventory.json` | Unique foreground layouts and world-map node selectors |
| Current runtime manifest and launch records | 514 resources, byte total, eight packs and current startup checks |

The relevant inventory and export tools are in
[`packaging/ExtractorTemplate/tools`](../packaging/ExtractorTemplate/tools/).
The older `latest-progress.json` predates the matching inventory/contract
checkpoint and was not used as the routine-mapping total.
