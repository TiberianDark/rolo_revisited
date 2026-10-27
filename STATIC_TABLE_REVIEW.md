# Static Table Review — 2026-10-27

Scope: the 19 array declarations reported by the preflight binary audit before the campaign-table cleanup. This is a technical provenance review, not a legal determination.

## Summary

- **8 regional achievement selector arrays:** game-specific indices for the regional jigsaw/animal achievement checks. They do not byte-match the ROM in the recorded scan, but their provenance is game-derived. Keep flagged until the selectors can be produced from the user-supplied ROM or the extraction/derivation is documented well enough to establish their source.
- **1 campaign percentage array:** eliminated. Its 70 values had exactly the same 70 distinct IDs as the four regional piece arrays; order differed, but percentage computation only counts set bits. The code now uses the regional lists as the single source.
- **10 remaining declarations:** ordinary translated runtime logic, native-authored metadata, zero initialization, or a deterministic math lookup; they are not resource payload arrays. Their detailed classification is below.
- Fresh Release build succeeded. The candidate scanner now reports **18** declarations, **0** known 64-byte resource fingerprints, and `release_ready: false`. The fingerprint scan is limited and does not prove absence of transformed data. Later checks verified byte-for-byte reserialization of all 514 external array resources and local direct startup. These checks do not establish complete gameplay parity or copyright clearance.

## Per-declaration decisions

| # | Declaration | Classification | Decision |
|---:|---|---|---|
| 1 | `achievement_regions.hpp::region0_pieces` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 2 | `achievement_regions.hpp::region0_animals` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 3 | `achievement_regions.hpp::region1_pieces` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 4 | `achievement_regions.hpp::region1_animals` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 5 | `achievement_regions.hpp::region2_pieces` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 6 | `achievement_regions.hpp::region2_animals` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 7 | `achievement_regions.hpp::region3_pieces` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 8 | `achievement_regions.hpp::region3_animals` | Game-specific map/object selectors | Remains provenance work; ROM-derived mapping, not raw asset bytes. |
| 9 | `actor_triggered_platforms.hpp::dxs` (paired with `dys`) | Movement behavior constants: `0, 2, 0, -2` and `-2, 0, 2, 0` | Keep as translated control logic; not extracted resource data. Audit sees only `dxs` because both arrays share one declaration line. |
| 10 | `campaign_percentage.hpp::campaign_percentage_nodes` | Duplicate of the regional piece selector set | **Removed.** Verified equal set and distinct count: 70/70. |
| 11 | `direction_vector_data.hpp::tables` | Deterministic fixed-point trig lookup | All 144 entries were verified as `bank * trunc(sin/cos(step * 5.625°) * 65536)` for banks 1–8 and steps 0–8 (with the final 45° pair duplicated by the source layout). This is math-derived, not unique resource content. Kept intact for exact runtime parity. |
| 12 | `level1_enemy_slice.hpp::piece_definition` | Actor definition ID `0x14482` | Translated dispatch/control value; not an asset byte array. |
| 13 | `local_achievements.hpp::local_achievement_list` | Native local achievement text, descriptions and point values | Locally authored feature metadata, not ROM extraction output. No exact resource fingerprint match. |
| 14 | `palette_effect_data.hpp::black` | Sixteen zero-valued colors | Zero initialization used as a palette target; not extracted resource data. |
| 15 | `player_input.hpp::order` | Input bit-to-slot mapping | Translated input logic; not resource data. |
| 16 | `spawn_branch_family.hpp::definitions` | Actor definition ID `0x14482` | Same dispatch/control value as #12; not an asset byte array. |
| 17 | `startup_animation_scene.hpp::attrs` | VDP attribute/control addresses | Translated startup routine constants; not uploaded image/tile data. |
| 18 | `startup_reset_entries.hpp::registers` | VDP register reset values | Translated device initialization logic; not resource data. |
| 19 | `world_route.hpp::reverse` | Direction transition mapping | Translated movement logic; not resource data. |

## Remaining action before release claims

The regional achievement selectors (#1–8) are the only items in this batch still marked as game-specific data rather than clearly generic logic or native-authored content. Exact-byte scanning is not enough to certify their provenance. The resource-free executable audit remains explicitly **not release-ready** until the broader review also covers generated scalar tables, strings, code-derived data, and the extraction output.

