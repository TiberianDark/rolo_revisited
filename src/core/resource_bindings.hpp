#pragma once
#include "resource_loader.hpp"
#include "world_map.hpp"
#include "timed_projectile_phases.hpp"
#include "status_hud_templates.hpp"
#include "startup_logo_raster.hpp"
#include "score_decimal.hpp"
#include "player_terrain_response.hpp"
#include "camera_data.hpp"
#include "actor_probe_patrol.hpp"
#include "actor_phase_emitter_data.hpp"
#include "actor_phase_cycle.hpp"
#include "actor_graphic_phase_data.hpp"
#include "actor_contact_family.hpp"
#include "actor_choreography_chain.hpp"
#include "actor_bounce_motion.hpp"
#include "actor_pattern_data.hpp"
#include "all_native_level_data.hpp"
#include "audio_bank_data.hpp"
#include "cavern_tile_animation_data.hpp"
#include "desert_tile_animation_data.hpp"
#include "dynamic_platform_data.hpp"
#include "ending_animation_data.hpp"
#include "ending_data.hpp"
#include "enemy_phase_entries.hpp"
#include "entrance_data.hpp"
#include "first_enemy_animation_data.hpp"
#include "first_enemy_definition_data.hpp"
#include "forest_level_data.hpp"
#include "forest_tile_animation_data.hpp"
#include "level1_companion_menu_data.hpp"
#include "level1_companion_presentation_data.hpp"
#include "level1_completion_data.hpp"
#include "level1_hud_data.hpp"
#include "level1_indexed_background_data.hpp"
#include "level1_object_animation_data.hpp"
#include "level1_object_data.hpp"
#include "level1_player_animation_data.hpp"
#include "level1_status_hud_data.hpp"
#include "level1_terrain_data.hpp"
#include "level1_world_data.hpp"
#include "level2_terrain_data.hpp"
#include "level3_terrain_data.hpp"
#include "level4_terrain_data.hpp"
#include "level8_terrain_data.hpp"
#include "music_sequence_data.hpp"
#include "opening_data.hpp"
#include "palette_effect_data.hpp"
#include "player_animation_data.hpp"
#include "player_data.hpp"
#include "sound_effect_data.hpp"
#include "spawn_branch_data.hpp"
#include "suction_particle_data.hpp"
#include "world_bunny_data.hpp"
#include "world_cursor_data.hpp"
#include "world_map_data.hpp"
#include "world_route_data.hpp"
#include "world_tile_animation_data.hpp"
namespace rolo::resources {
inline void initialize(const std::filesystem::path& root) {
    checked_bytes(root, "manifest.json", "c1d41a485c8e3f383d7a3745b409d12bb66450865648c8453c635aa87d3ce95e", 171219);
    load_numeric(root, "all_native_level_data/bank1_tiles.bin", "4849c82953fdf30f457ed7218871abcbabeac19692dce53262147f2180a16f58", rolo::all_native_level_data::bank1_tiles);
    load_numeric(root, "all_native_level_data/bank1_quads.bin", "3712121a1166650043028f226864bb82efd208373fadc8d774c21fba5610d311", rolo::all_native_level_data::bank1_quads);
    load_numeric(root, "all_native_level_data/bank1_patterns.bin", "66a00b3fba3caa446250ae5378f62a8e2d65f416be8891718dc3c2aa5e86d74c", rolo::all_native_level_data::bank1_patterns);
    load_numeric(root, "all_native_level_data/bank1_collision.bin", "414a331bb2ce9a6eb49cada69ebefce4caafb54eddffad26fc2a1dad01fdcbb2", rolo::all_native_level_data::bank1_collision);
    load_numeric(root, "all_native_level_data/bank2_tiles.bin", "8b86e989f670f22ffa9b0ed5b69362c46bee64500121c00fb03cd727cc5ed8b9", rolo::all_native_level_data::bank2_tiles);
    load_numeric(root, "all_native_level_data/bank2_quads.bin", "28a3962d17db23c390dd03d66b95242565120db59eb7a3b13d649ed289b34a72", rolo::all_native_level_data::bank2_quads);
    load_numeric(root, "all_native_level_data/bank2_patterns.bin", "7c4a2278d7730c7a27c522c8b5daec00f285dcec9c626232730fba24108f5064", rolo::all_native_level_data::bank2_patterns);
    load_numeric(root, "all_native_level_data/bank2_collision.bin", "940d938e6f70929265f307684329bd964b00c8adb9578c30303f8f8af9f7df50", rolo::all_native_level_data::bank2_collision);
    load_numeric(root, "all_native_level_data/bank3_tiles.bin", "79bcbd0be0a1f6f41e1abd0f1399e591bd8cdc49a0d1cbe0644f4485b012ecc6", rolo::all_native_level_data::bank3_tiles);
    load_numeric(root, "all_native_level_data/bank3_quads.bin", "56887a4ad2073d63a4400715d1d6cba29045d66e45ffe03ddfd531f575b5b23c", rolo::all_native_level_data::bank3_quads);
    load_numeric(root, "all_native_level_data/bank3_patterns.bin", "dc3ad5f554afb550cf386fc0b2a8554f3f30b55b982df00192e6c24c9877f3d1", rolo::all_native_level_data::bank3_patterns);
    load_numeric(root, "all_native_level_data/bank3_collision.bin", "4ec4393ee2dd834537594ee18a01aba0f62c2d74ebdfd7940f60bc7e2abcd277", rolo::all_native_level_data::bank3_collision);
    load_numeric(root, "all_native_level_data/bank4_tiles.bin", "d248955eddf8c864cae624373d166e60ce09c567292352920c6981e59907a817", rolo::all_native_level_data::bank4_tiles);
    load_numeric(root, "all_native_level_data/bank4_quads.bin", "a5acdc7472fad04f3ee9c480adf02cfbe725498566ce816a6e470a074a487dd1", rolo::all_native_level_data::bank4_quads);
    load_numeric(root, "all_native_level_data/bank4_patterns.bin", "baa8dfac658f67e20115e19e135ec918bd986c27407cf0b323dbedea96b142a0", rolo::all_native_level_data::bank4_patterns);
    load_numeric(root, "all_native_level_data/bank4_collision.bin", "46246b3b7d2d5c48c9c630252f08453c699fedef420afc69fbf808485e8d80a7", rolo::all_native_level_data::bank4_collision);
    load_numeric(root, "all_native_level_data/bank5_tiles.bin", "5761d601b1012a742a263942d20a7bd2c7dea3151bd8380cd05f8aed0b3f0985", rolo::all_native_level_data::bank5_tiles);
    load_numeric(root, "all_native_level_data/bank5_quads.bin", "224942a483dc2d6088b9ac0d762013afd138b970239772cf135cf6cbd4005783", rolo::all_native_level_data::bank5_quads);
    load_numeric(root, "all_native_level_data/bank5_patterns.bin", "d0d8691440c7cee18f75bfd9cd3feff0363556e58ca1e0af3f70a43cb8df660e", rolo::all_native_level_data::bank5_patterns);
    load_numeric(root, "all_native_level_data/bank5_collision.bin", "6b3df9cc6c584839d3072889180d4ad4aae42aef6fee8f17950caa15ce3309a8", rolo::all_native_level_data::bank5_collision);
    load_numeric(root, "all_native_level_data/bank6_tiles.bin", "00a9942df1a26ed8b5eac65cbf1d1b8e2aad0fcd0e235e75da92420b5ff9a01b", rolo::all_native_level_data::bank6_tiles);
    load_numeric(root, "all_native_level_data/bank6_quads.bin", "8f60405edbec59c6ddfd8c922aed66dc3bce34e04baf24a963db216ba5e852b6", rolo::all_native_level_data::bank6_quads);
    load_numeric(root, "all_native_level_data/bank6_patterns.bin", "754b005124b6a0af4a7273606319abd5a11b875e0d9e1b1718caa075152f8cc8", rolo::all_native_level_data::bank6_patterns);
    load_numeric(root, "all_native_level_data/bank6_collision.bin", "2ad9579641fe75dfda553e06b009c739c4fc620d74531c95b0a525e1906be5af", rolo::all_native_level_data::bank6_collision);
    load_numeric(root, "all_native_level_data/bank7_tiles.bin", "56c4fb0b8c5341fdc9279cbfc2f3e895fa1853746872a19f17d808e2c16b433e", rolo::all_native_level_data::bank7_tiles);
    load_numeric(root, "all_native_level_data/bank7_quads.bin", "9baa67a4c3792f8efc4ad08eca381747cc04d0b034ee3d62d8053ee2a303874b", rolo::all_native_level_data::bank7_quads);
    load_numeric(root, "all_native_level_data/bank7_patterns.bin", "b754eab08fcc8f484c6462d4569b77152d7933adaa39c0c9948d6937d3462d35", rolo::all_native_level_data::bank7_patterns);
    load_numeric(root, "all_native_level_data/bank7_collision.bin", "aa331c075a95bb6d3c19c7d04752a6c7db30e5f9aa580fe0b296041bde826cf7", rolo::all_native_level_data::bank7_collision);
    load_numeric(root, "all_native_level_data/level1_foreground.bin", "910c87a8643a649cae3f0eee7cf800a2f945fc7c519d8c73e7a83c0046b80512", rolo::all_native_level_data::level1_foreground);
    load_numeric(root, "all_native_level_data/level1_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level1_background);
    load_numeric(root, "all_native_level_data/level1_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level1_palette);
    load_numeric(root, "all_native_level_data/level2_foreground.bin", "fa9de87576cb3238458f36889e27dc6986ea85352643466ebbaa3f7e4f50f787", rolo::all_native_level_data::level2_foreground);
    load_numeric(root, "all_native_level_data/level2_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level2_background);
    load_numeric(root, "all_native_level_data/level2_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level2_palette);
    load_numeric(root, "all_native_level_data/level3_foreground.bin", "ffc57e472570a1272d64e3f3afdeaffde59405d0a4605771ee240394beeb2a24", rolo::all_native_level_data::level3_foreground);
    load_numeric(root, "all_native_level_data/level3_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level3_background);
    load_numeric(root, "all_native_level_data/level3_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level3_palette);
    load_numeric(root, "all_native_level_data/level4_foreground.bin", "e78c0c8755880ac542fb914acfe9da70ccfaa00cad5ebe842b38d969396e69ff", rolo::all_native_level_data::level4_foreground);
    load_numeric(root, "all_native_level_data/level4_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level4_background);
    load_numeric(root, "all_native_level_data/level4_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level4_palette);
    load_numeric(root, "all_native_level_data/level5_foreground.bin", "331a6635d8fc3a1521cb48c172d243b9d5a1c8064b3e65d1487992946d96993c", rolo::all_native_level_data::level5_foreground);
    load_numeric(root, "all_native_level_data/level5_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level5_background);
    load_numeric(root, "all_native_level_data/level5_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level5_palette);
    load_numeric(root, "all_native_level_data/level6_foreground.bin", "70e380e23428dbd7de275af99ca68eb2db3b8ba75e69596156cad39eb98a3a55", rolo::all_native_level_data::level6_foreground);
    load_numeric(root, "all_native_level_data/level6_background.bin", "e0fd7db59f9952326197d728ce8cd733e31956b1a067451cc14484e048199d16", rolo::all_native_level_data::level6_background);
    load_numeric(root, "all_native_level_data/level6_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level6_palette);
    load_numeric(root, "all_native_level_data/level7_foreground.bin", "4bb70da9f6161e632984510d9cd1687a5f9ebe75f8143ebf67ab3924f4364a14", rolo::all_native_level_data::level7_foreground);
    load_numeric(root, "all_native_level_data/level7_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level7_background);
    load_numeric(root, "all_native_level_data/level7_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level7_palette);
    load_numeric(root, "all_native_level_data/level8_foreground.bin", "4817fc80089b8a228c937f973792cb12141f7cae7cbcaeac4ad34ed36d3d9967", rolo::all_native_level_data::level8_foreground);
    load_numeric(root, "all_native_level_data/level8_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level8_background);
    load_numeric(root, "all_native_level_data/level8_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level8_palette);
    load_numeric(root, "all_native_level_data/level9_foreground.bin", "11892641df77a214b9da1e4221e8fabdcbb5505f8c1e0b973099713602b8bab1", rolo::all_native_level_data::level9_foreground);
    load_numeric(root, "all_native_level_data/level9_background.bin", "e0097ac57799c5fe0561973b248675106846f2187bd3bc652e5f118399191ab9", rolo::all_native_level_data::level9_background);
    load_numeric(root, "all_native_level_data/level9_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level9_palette);
    load_numeric(root, "all_native_level_data/level10_foreground.bin", "d89598feb2b4d336727a08ccab18eefa5866ec8754067cef1d9515117cd79292", rolo::all_native_level_data::level10_foreground);
    load_numeric(root, "all_native_level_data/level10_background.bin", "e0097ac57799c5fe0561973b248675106846f2187bd3bc652e5f118399191ab9", rolo::all_native_level_data::level10_background);
    load_numeric(root, "all_native_level_data/level10_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level10_palette);
    load_numeric(root, "all_native_level_data/level11_foreground.bin", "307d687b1196ebb0dbea287bf2336b7659f66aaed982843ed049869377103293", rolo::all_native_level_data::level11_foreground);
    load_numeric(root, "all_native_level_data/level11_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level11_background);
    load_numeric(root, "all_native_level_data/level11_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level11_palette);
    load_numeric(root, "all_native_level_data/level12_foreground.bin", "d02ad57dcf8b79ab8f335a1c9103dc4978bbbd2a1d0c5f7f60c6d179b5235cf6", rolo::all_native_level_data::level12_foreground);
    load_numeric(root, "all_native_level_data/level12_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level12_background);
    load_numeric(root, "all_native_level_data/level12_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level12_palette);
    load_numeric(root, "all_native_level_data/level13_foreground.bin", "fd6411f0be727ddc69ff1bc3aec3404ba25acc3ee82183dce541a08d6f40fe3f", rolo::all_native_level_data::level13_foreground);
    load_numeric(root, "all_native_level_data/level13_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::all_native_level_data::level13_background);
    load_numeric(root, "all_native_level_data/level13_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::all_native_level_data::level13_palette);
    load_numeric(root, "all_native_level_data/level14_foreground.bin", "651a8fc0f632f1b5b954ed90219e4bc57472667a9cc6105fb5324ab58a573d71", rolo::all_native_level_data::level14_foreground);
    load_numeric(root, "all_native_level_data/level14_background.bin", "1ae38e7f3e20a484b5c7229b487bb96f47586b9cd4201133b3018cfe0aef566a", rolo::all_native_level_data::level14_background);
    load_numeric(root, "all_native_level_data/level14_palette.bin", "acd57359ea506ae0a2f611bb935805f1ad1906f25647947c59761580d868987d", rolo::all_native_level_data::level14_palette);
    load_numeric(root, "all_native_level_data/level15_foreground.bin", "4c9eb9846513d3ad228851958211d302c3e3dcc0fd04216e2a3760e2563ca98d", rolo::all_native_level_data::level15_foreground);
    load_numeric(root, "all_native_level_data/level15_background.bin", "87339a2169ccca5696baef26ddda1bc7e8a6b9c7e5233e3288aef6290d902477", rolo::all_native_level_data::level15_background);
    load_numeric(root, "all_native_level_data/level15_palette.bin", "2849ef3c1739402dc7b1febf333410f8fe02e1f5b2d4f3a7631d2406cd4d4844", rolo::all_native_level_data::level15_palette);
    load_numeric(root, "all_native_level_data/level16_foreground.bin", "bc34df81b58d8e5f0eef216f5c74cb5979e9f566b66d1445e5950ffa23d8c339", rolo::all_native_level_data::level16_foreground);
    load_numeric(root, "all_native_level_data/level16_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level16_background);
    load_numeric(root, "all_native_level_data/level16_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level16_palette);
    load_numeric(root, "all_native_level_data/level17_foreground.bin", "bc34df81b58d8e5f0eef216f5c74cb5979e9f566b66d1445e5950ffa23d8c339", rolo::all_native_level_data::level17_foreground);
    load_numeric(root, "all_native_level_data/level17_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level17_background);
    load_numeric(root, "all_native_level_data/level17_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level17_palette);
    load_numeric(root, "all_native_level_data/level18_foreground.bin", "e90a533c01d42d9f74ab2b7cd5b32ccae159eab9f455e47b7adf6fa1dd20f234", rolo::all_native_level_data::level18_foreground);
    load_numeric(root, "all_native_level_data/level18_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level18_background);
    load_numeric(root, "all_native_level_data/level18_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level18_palette);
    load_numeric(root, "all_native_level_data/level19_foreground.bin", "a6da4ef99190ac9b5b662c7b501f8b1aa5e2118d16b09c681129d60c76c0154c", rolo::all_native_level_data::level19_foreground);
    load_numeric(root, "all_native_level_data/level19_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level19_background);
    load_numeric(root, "all_native_level_data/level19_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level19_palette);
    load_numeric(root, "all_native_level_data/level20_foreground.bin", "0678c7ee82ff7c6c03c1ceb7c7d1149b05db91bced48e7aef416ab81028f8fc6", rolo::all_native_level_data::level20_foreground);
    load_numeric(root, "all_native_level_data/level20_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level20_background);
    load_numeric(root, "all_native_level_data/level20_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level20_palette);
    load_numeric(root, "all_native_level_data/level21_foreground.bin", "21ca1061aa9e546932cd8ed0ec609466c1af8d8cc30f12e915bb93568a21dc67", rolo::all_native_level_data::level21_foreground);
    load_numeric(root, "all_native_level_data/level21_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level21_background);
    load_numeric(root, "all_native_level_data/level21_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level21_palette);
    load_numeric(root, "all_native_level_data/level22_foreground.bin", "c19543e9f0ba2f8f702799bbf2f2f4aadbdcf19e7201589e93eed2e944f24c31", rolo::all_native_level_data::level22_foreground);
    load_numeric(root, "all_native_level_data/level22_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level22_background);
    load_numeric(root, "all_native_level_data/level22_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level22_palette);
    load_numeric(root, "all_native_level_data/level23_foreground.bin", "f23c8b3da062d9c851995c1a9009514a0f71933605a72a070a937b05f462754a", rolo::all_native_level_data::level23_foreground);
    load_numeric(root, "all_native_level_data/level23_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level23_background);
    load_numeric(root, "all_native_level_data/level23_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level23_palette);
    load_numeric(root, "all_native_level_data/level24_foreground.bin", "6b401f1a4036c90a08e504bd6c2f0c99b850e8f17d3e93faaa1b8621aee50a8b", rolo::all_native_level_data::level24_foreground);
    load_numeric(root, "all_native_level_data/level24_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level24_background);
    load_numeric(root, "all_native_level_data/level24_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level24_palette);
    load_numeric(root, "all_native_level_data/level25_foreground.bin", "9b60bdbb1e10cf0625b92849385ff6a6a11465f8f8a2851d73b1a3c480a8fa40", rolo::all_native_level_data::level25_foreground);
    load_numeric(root, "all_native_level_data/level25_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level25_background);
    load_numeric(root, "all_native_level_data/level25_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level25_palette);
    load_numeric(root, "all_native_level_data/level26_foreground.bin", "d1cbfbac3d9260e705c1580be1dbfde94b3a9b93758476a62ff212447bd8cf02", rolo::all_native_level_data::level26_foreground);
    load_numeric(root, "all_native_level_data/level26_background.bin", "fc60b6497dee9ca3bd790052989ab1a26dfbb551f54fe3822ea6cb6cc899986b", rolo::all_native_level_data::level26_background);
    load_numeric(root, "all_native_level_data/level26_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level26_palette);
    load_numeric(root, "all_native_level_data/level27_foreground.bin", "68b13507643b80ef65c0d423fd4f55f790f7980a49ee70ab1c2c3bfd81b5359e", rolo::all_native_level_data::level27_foreground);
    load_numeric(root, "all_native_level_data/level27_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level27_background);
    load_numeric(root, "all_native_level_data/level27_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level27_palette);
    load_numeric(root, "all_native_level_data/level28_foreground.bin", "971c5c6f8e1276945b0118e8dbf96e0d7e80f754ede06f60950ee5c4d09e2aef", rolo::all_native_level_data::level28_foreground);
    load_numeric(root, "all_native_level_data/level28_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level28_background);
    load_numeric(root, "all_native_level_data/level28_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level28_palette);
    load_numeric(root, "all_native_level_data/level29_foreground.bin", "7666077d03619bca87243aeb2736f129cdd28b9e0247ce3b6e080d13d66d1527", rolo::all_native_level_data::level29_foreground);
    load_numeric(root, "all_native_level_data/level29_background.bin", "87339a2169ccca5696baef26ddda1bc7e8a6b9c7e5233e3288aef6290d902477", rolo::all_native_level_data::level29_background);
    load_numeric(root, "all_native_level_data/level29_palette.bin", "2849ef3c1739402dc7b1febf333410f8fe02e1f5b2d4f3a7631d2406cd4d4844", rolo::all_native_level_data::level29_palette);
    load_numeric(root, "all_native_level_data/level30_foreground.bin", "1f01603c29fabe0161439e0d2a86bf9cbe1bb9995baf0e3a34597881d4ed8819", rolo::all_native_level_data::level30_foreground);
    load_numeric(root, "all_native_level_data/level30_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level30_background);
    load_numeric(root, "all_native_level_data/level30_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level30_palette);
    load_numeric(root, "all_native_level_data/level31_foreground.bin", "b73042878b8a3b4245b450c64721a065a698298286725de1d6bf5bf3015c46d9", rolo::all_native_level_data::level31_foreground);
    load_numeric(root, "all_native_level_data/level31_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level31_background);
    load_numeric(root, "all_native_level_data/level31_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level31_palette);
    load_numeric(root, "all_native_level_data/level32_foreground.bin", "cb391283e15352ef68ca1dcc15d5629d2f6b900491a95d60ceb0685c5271caff", rolo::all_native_level_data::level32_foreground);
    load_numeric(root, "all_native_level_data/level32_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level32_background);
    load_numeric(root, "all_native_level_data/level32_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level32_palette);
    load_numeric(root, "all_native_level_data/level33_foreground.bin", "c24bdeb9626c38a75b40050ca0ae68d4b48aa62720415d607a1e3ce68014c0af", rolo::all_native_level_data::level33_foreground);
    load_numeric(root, "all_native_level_data/level33_background.bin", "87339a2169ccca5696baef26ddda1bc7e8a6b9c7e5233e3288aef6290d902477", rolo::all_native_level_data::level33_background);
    load_numeric(root, "all_native_level_data/level33_palette.bin", "2849ef3c1739402dc7b1febf333410f8fe02e1f5b2d4f3a7631d2406cd4d4844", rolo::all_native_level_data::level33_palette);
    load_numeric(root, "all_native_level_data/level34_foreground.bin", "3722f82fa3fcf1cf90642aad66f24a91a77a94b87ead501c382e2dc203f5fa08", rolo::all_native_level_data::level34_foreground);
    load_numeric(root, "all_native_level_data/level34_background.bin", "0eb544120999082f3129a07115b781375ee0dd3d310227c644ec1546dd25d0a3", rolo::all_native_level_data::level34_background);
    load_numeric(root, "all_native_level_data/level34_palette.bin", "9410d57772e047ddddc53ff624b21eb4a2c79166af53b37ef83ad05d4539fe31", rolo::all_native_level_data::level34_palette);
    load_numeric(root, "all_native_level_data/level35_foreground.bin", "9916bd3074b31620f5fbe40b99d6b329556bfd1c1445de9624d845f90efd51e1", rolo::all_native_level_data::level35_foreground);
    load_numeric(root, "all_native_level_data/level35_background.bin", "1ae38e7f3e20a484b5c7229b487bb96f47586b9cd4201133b3018cfe0aef566a", rolo::all_native_level_data::level35_background);
    load_numeric(root, "all_native_level_data/level35_palette.bin", "3cc9b35c5ffb76b4f2cc752884faa38fcb604af5df2f46a24b97194b9fe05f9b", rolo::all_native_level_data::level35_palette);
    load_numeric(root, "all_native_level_data/level36_foreground.bin", "f62a732275405e36e458aa15a7396a2c63b8a892112e6d1e7a4b7fbde7455308", rolo::all_native_level_data::level36_foreground);
    load_numeric(root, "all_native_level_data/level36_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level36_background);
    load_numeric(root, "all_native_level_data/level36_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level36_palette);
    load_numeric(root, "all_native_level_data/level37_foreground.bin", "6f7b2dbfdbc0289723db684a8ff698a8092426b0c44c3d5b8f02a53ab1a03e36", rolo::all_native_level_data::level37_foreground);
    load_numeric(root, "all_native_level_data/level37_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level37_background);
    load_numeric(root, "all_native_level_data/level37_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level37_palette);
    load_numeric(root, "all_native_level_data/level38_foreground.bin", "fc3afac8d419e5e54f81a1fae3aa392b2ac635d18d0226bc867f15a82d752545", rolo::all_native_level_data::level38_foreground);
    load_numeric(root, "all_native_level_data/level38_background.bin", "87339a2169ccca5696baef26ddda1bc7e8a6b9c7e5233e3288aef6290d902477", rolo::all_native_level_data::level38_background);
    load_numeric(root, "all_native_level_data/level38_palette.bin", "2849ef3c1739402dc7b1febf333410f8fe02e1f5b2d4f3a7631d2406cd4d4844", rolo::all_native_level_data::level38_palette);
    load_numeric(root, "all_native_level_data/level39_foreground.bin", "3e97640b309441871a6cb75f7ffb51e0dc17deb953beefe83021c1a5d4de157d", rolo::all_native_level_data::level39_foreground);
    load_numeric(root, "all_native_level_data/level39_background.bin", "0eb544120999082f3129a07115b781375ee0dd3d310227c644ec1546dd25d0a3", rolo::all_native_level_data::level39_background);
    load_numeric(root, "all_native_level_data/level39_palette.bin", "9410d57772e047ddddc53ff624b21eb4a2c79166af53b37ef83ad05d4539fe31", rolo::all_native_level_data::level39_palette);
    load_numeric(root, "all_native_level_data/level40_foreground.bin", "3780f76f622b68d414bf8f49ab5f63348df6dcf5971d8e299d78b9744675a09a", rolo::all_native_level_data::level40_foreground);
    load_numeric(root, "all_native_level_data/level40_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level40_background);
    load_numeric(root, "all_native_level_data/level40_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level40_palette);
    load_numeric(root, "all_native_level_data/level41_foreground.bin", "23d5845ff40378f2b0dc0a5b208d0d047d2b31ff006735a304395993b0683aed", rolo::all_native_level_data::level41_foreground);
    load_numeric(root, "all_native_level_data/level41_background.bin", "345cfe35e12f8d6d3226cfd0cda87918057b8abc6d2b971c4473516709b2229e", rolo::all_native_level_data::level41_background);
    load_numeric(root, "all_native_level_data/level41_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level41_palette);
    load_numeric(root, "all_native_level_data/level42_foreground.bin", "f1545c10002239c4d154d182cf06cc08d0ed59b4c4e8542f3d104711bbf1ac5b", rolo::all_native_level_data::level42_foreground);
    load_numeric(root, "all_native_level_data/level42_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level42_background);
    load_numeric(root, "all_native_level_data/level42_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level42_palette);
    load_numeric(root, "all_native_level_data/level43_foreground.bin", "2f083ea3c011192c8d66eaad7cf52b6971d5f84566026ec412839a7a5e401462", rolo::all_native_level_data::level43_foreground);
    load_numeric(root, "all_native_level_data/level43_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level43_background);
    load_numeric(root, "all_native_level_data/level43_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level43_palette);
    load_numeric(root, "all_native_level_data/level44_foreground.bin", "bc34df81b58d8e5f0eef216f5c74cb5979e9f566b66d1445e5950ffa23d8c339", rolo::all_native_level_data::level44_foreground);
    load_numeric(root, "all_native_level_data/level44_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level44_background);
    load_numeric(root, "all_native_level_data/level44_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level44_palette);
    load_numeric(root, "all_native_level_data/level45_foreground.bin", "8617f8748ac9cf99079abd3713812d17e518ca3335af113c713a64d813df3a6f", rolo::all_native_level_data::level45_foreground);
    load_numeric(root, "all_native_level_data/level45_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level45_background);
    load_numeric(root, "all_native_level_data/level45_palette.bin", "788dee8bea630e3a7091fe2d78787590647bb34fd2d57ca72c139dfe77eb0bf9", rolo::all_native_level_data::level45_palette);
    load_numeric(root, "all_native_level_data/level47_foreground.bin", "f253f0920e5f231ef6fb8dd0bffecbc811ced3c48ad4cf929e568d9df62a7a8d", rolo::all_native_level_data::level47_foreground);
    load_numeric(root, "all_native_level_data/level47_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level47_background);
    load_numeric(root, "all_native_level_data/level47_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level47_palette);
    load_numeric(root, "all_native_level_data/level48_foreground.bin", "d85662f8a7593bcff7dd8f94560b446f1dc6b6f97a9d7939db1088db4209f0cf", rolo::all_native_level_data::level48_foreground);
    load_numeric(root, "all_native_level_data/level48_background.bin", "84e1971b609c7a4ca9bc8e58f89fb6299c54a20e680862b9785d74c01fa8df05", rolo::all_native_level_data::level48_background);
    load_numeric(root, "all_native_level_data/level48_palette.bin", "854ca8839f8ecc1727c8a138bf1bef30b333abaccfa8d223ea5b8b26a3f356bf", rolo::all_native_level_data::level48_palette);
    load_numeric(root, "all_native_level_data/level49_foreground.bin", "bc34df81b58d8e5f0eef216f5c74cb5979e9f566b66d1445e5950ffa23d8c339", rolo::all_native_level_data::level49_foreground);
    load_numeric(root, "all_native_level_data/level49_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level49_background);
    load_numeric(root, "all_native_level_data/level49_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level49_palette);
    load_numeric(root, "all_native_level_data/level50_foreground.bin", "c83bf52422d0a50490102634e158dafbfd29e8e5b9a5a1cf1d3ec3b78e0d51d8", rolo::all_native_level_data::level50_foreground);
    load_numeric(root, "all_native_level_data/level50_background.bin", "345cfe35e12f8d6d3226cfd0cda87918057b8abc6d2b971c4473516709b2229e", rolo::all_native_level_data::level50_background);
    load_numeric(root, "all_native_level_data/level50_palette.bin", "9410d57772e047ddddc53ff624b21eb4a2c79166af53b37ef83ad05d4539fe31", rolo::all_native_level_data::level50_palette);
    load_numeric(root, "all_native_level_data/level51_foreground.bin", "5490843bdc673eca9fee687ca405aeae514bda457fd9e2f03dbaf3fc64982ba4", rolo::all_native_level_data::level51_foreground);
    load_numeric(root, "all_native_level_data/level51_background.bin", "1ae38e7f3e20a484b5c7229b487bb96f47586b9cd4201133b3018cfe0aef566a", rolo::all_native_level_data::level51_background);
    load_numeric(root, "all_native_level_data/level51_palette.bin", "acd57359ea506ae0a2f611bb935805f1ad1906f25647947c59761580d868987d", rolo::all_native_level_data::level51_palette);
    load_numeric(root, "all_native_level_data/level52_foreground.bin", "0818ac006467d48b4e6dfb14eaac2757d988f9ae5279759ef6581fa170c3c92a", rolo::all_native_level_data::level52_foreground);
    load_numeric(root, "all_native_level_data/level52_background.bin", "345cfe35e12f8d6d3226cfd0cda87918057b8abc6d2b971c4473516709b2229e", rolo::all_native_level_data::level52_background);
    load_numeric(root, "all_native_level_data/level52_palette.bin", "9410d57772e047ddddc53ff624b21eb4a2c79166af53b37ef83ad05d4539fe31", rolo::all_native_level_data::level52_palette);
    load_numeric(root, "all_native_level_data/level53_foreground.bin", "fa16e42400fc85f449257b3cbe6be344ad543d4ef763b519bc829f8f3e058830", rolo::all_native_level_data::level53_foreground);
    load_numeric(root, "all_native_level_data/level53_background.bin", "1ae38e7f3e20a484b5c7229b487bb96f47586b9cd4201133b3018cfe0aef566a", rolo::all_native_level_data::level53_background);
    load_numeric(root, "all_native_level_data/level53_palette.bin", "7df30fafb8a63de0cadf45ac6a39d43e9c34b801d0155c080285ddb16988e029", rolo::all_native_level_data::level53_palette);
    load_numeric(root, "all_native_level_data/level54_foreground.bin", "1c9c819f784f2e19b8bbefde499d00b8966e46a08fc1793416356891762968fd", rolo::all_native_level_data::level54_foreground);
    load_numeric(root, "all_native_level_data/level54_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level54_background);
    load_numeric(root, "all_native_level_data/level54_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level54_palette);
    load_numeric(root, "all_native_level_data/level55_foreground.bin", "dc624288d36f7936c101aedf916eb170504fdeb12df64028be8d7102567a8007", rolo::all_native_level_data::level55_foreground);
    load_numeric(root, "all_native_level_data/level55_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level55_background);
    load_numeric(root, "all_native_level_data/level55_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level55_palette);
    load_numeric(root, "all_native_level_data/level56_foreground.bin", "33198002a28af15832a853ae71e6feb6a9e6f49256c704385b024e28116bbb3e", rolo::all_native_level_data::level56_foreground);
    load_numeric(root, "all_native_level_data/level56_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level56_background);
    load_numeric(root, "all_native_level_data/level56_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level56_palette);
    load_numeric(root, "all_native_level_data/level57_foreground.bin", "0ccf3fa11d85e7ecde7389a76f38aa3430787f1a14377789a11fb56b36098ea3", rolo::all_native_level_data::level57_foreground);
    load_numeric(root, "all_native_level_data/level57_background.bin", "1ae38e7f3e20a484b5c7229b487bb96f47586b9cd4201133b3018cfe0aef566a", rolo::all_native_level_data::level57_background);
    load_numeric(root, "all_native_level_data/level57_palette.bin", "82bfaaa65a60f86ee412a1c506c7118a503945b42768a82f8d7456f43fa203fb", rolo::all_native_level_data::level57_palette);
    load_numeric(root, "all_native_level_data/level58_foreground.bin", "cee3c43748fd00b6af4efdb7edc45d3c9c79f2c585c332ffb6ff1315799bee21", rolo::all_native_level_data::level58_foreground);
    load_numeric(root, "all_native_level_data/level58_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level58_background);
    load_numeric(root, "all_native_level_data/level58_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level58_palette);
    load_numeric(root, "all_native_level_data/level59_foreground.bin", "8c6aafee4affa335bc51adeb130fd7ca2b6c3eecc6dc226dec9e5a8ef083237a", rolo::all_native_level_data::level59_foreground);
    load_numeric(root, "all_native_level_data/level59_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level59_background);
    load_numeric(root, "all_native_level_data/level59_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level59_palette);
    load_numeric(root, "all_native_level_data/level60_foreground.bin", "e2b822d969bf634fb39471684772ab1a2314fb4d1a8586500327badbc4543802", rolo::all_native_level_data::level60_foreground);
    load_numeric(root, "all_native_level_data/level60_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level60_background);
    load_numeric(root, "all_native_level_data/level60_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level60_palette);
    load_numeric(root, "all_native_level_data/level61_foreground.bin", "867a4e7e488fd51dcfdf8ed36391020c4424e71c062cebb78c57964d515aa732", rolo::all_native_level_data::level61_foreground);
    load_numeric(root, "all_native_level_data/level61_background.bin", "370c77d34bf6c2c928cf369ec2336db81cb3f7a2f3e630eb2ebbf7851817e40d", rolo::all_native_level_data::level61_background);
    load_numeric(root, "all_native_level_data/level61_palette.bin", "1896f72a99976aa29b95b3630411589644f9aef33d0d77abda0acd94a805fe79", rolo::all_native_level_data::level61_palette);
    load_numeric(root, "all_native_level_data/level62_foreground.bin", "aaf24dafb8e8cb10231917911b784ed3eda84a9d8aad8ec13b07c3da55c78225", rolo::all_native_level_data::level62_foreground);
    load_numeric(root, "all_native_level_data/level62_background.bin", "54aa25bf25985bd3b23515e636f876c5a9516af66b0f515830961b134090a3dd", rolo::all_native_level_data::level62_background);
    load_numeric(root, "all_native_level_data/level62_palette.bin", "702f67efdc8cf0494802e765342549ddce83cdfe7933d8435be39fb05c2013f8", rolo::all_native_level_data::level62_palette);
    load_numeric(root, "all_native_level_data/level63_foreground.bin", "406abc1fbccbcfe8ea0e7d836a65aa179c0bb421f91820777c3da12926513f80", rolo::all_native_level_data::level63_foreground);
    load_numeric(root, "all_native_level_data/level63_background.bin", "54aa25bf25985bd3b23515e636f876c5a9516af66b0f515830961b134090a3dd", rolo::all_native_level_data::level63_background);
    load_numeric(root, "all_native_level_data/level63_palette.bin", "702f67efdc8cf0494802e765342549ddce83cdfe7933d8435be39fb05c2013f8", rolo::all_native_level_data::level63_palette);
    load_numeric(root, "all_native_level_data/level64_foreground.bin", "4c7c0158acb56b341ea308a29c1d118ce50e17fac7dae85701ba864938f7856c", rolo::all_native_level_data::level64_foreground);
    load_numeric(root, "all_native_level_data/level64_background.bin", "00bf6c50fc1b61600ee19bbc857ecf8bf45193cc34c9be156c571b9a3a6db4a0", rolo::all_native_level_data::level64_background);
    load_numeric(root, "all_native_level_data/level64_palette.bin", "5111898b9bf7d5344acc259fcaf4b7b9539b6070620f5d12382635ce5575620c", rolo::all_native_level_data::level64_palette);
    load_numeric(root, "all_native_level_data/level65_foreground.bin", "5cdac982dad8fb67a5c6ca93c427bc7002e21cf2e19a3f811f314b3f0e1b1bf6", rolo::all_native_level_data::level65_foreground);
    load_numeric(root, "all_native_level_data/level65_background.bin", "15ac1fe714f28949ac034bc1e6cabbe9e79d43865bbcea18302168656d1a58f4", rolo::all_native_level_data::level65_background);
    load_numeric(root, "all_native_level_data/level65_palette.bin", "5111898b9bf7d5344acc259fcaf4b7b9539b6070620f5d12382635ce5575620c", rolo::all_native_level_data::level65_palette);
    load_numeric(root, "all_native_level_data/level66_foreground.bin", "ec11cbf2f6c84d04e1feaa583880786a0c3d30ae444e94c538dc9320a7be9d4c", rolo::all_native_level_data::level66_foreground);
    load_numeric(root, "all_native_level_data/level66_background.bin", "00bf6c50fc1b61600ee19bbc857ecf8bf45193cc34c9be156c571b9a3a6db4a0", rolo::all_native_level_data::level66_background);
    load_numeric(root, "all_native_level_data/level66_palette.bin", "5111898b9bf7d5344acc259fcaf4b7b9539b6070620f5d12382635ce5575620c", rolo::all_native_level_data::level66_palette);
    load_numeric(root, "all_native_level_data/level67_foreground.bin", "00929eab69f37c8d45253e715614ac12631dedce1115da407b5475f819b3e559", rolo::all_native_level_data::level67_foreground);
    load_numeric(root, "all_native_level_data/level67_background.bin", "00bf6c50fc1b61600ee19bbc857ecf8bf45193cc34c9be156c571b9a3a6db4a0", rolo::all_native_level_data::level67_background);
    load_numeric(root, "all_native_level_data/level67_palette.bin", "5111898b9bf7d5344acc259fcaf4b7b9539b6070620f5d12382635ce5575620c", rolo::all_native_level_data::level67_palette);
    load_numeric(root, "all_native_level_data/level68_foreground.bin", "b194c38b65e5769e5a1c0e03bee2dc90ba328d0703a55ccb256803b25839e5b3", rolo::all_native_level_data::level68_foreground);
    load_numeric(root, "all_native_level_data/level68_background.bin", "00bf6c50fc1b61600ee19bbc857ecf8bf45193cc34c9be156c571b9a3a6db4a0", rolo::all_native_level_data::level68_background);
    load_numeric(root, "all_native_level_data/level68_palette.bin", "5111898b9bf7d5344acc259fcaf4b7b9539b6070620f5d12382635ce5575620c", rolo::all_native_level_data::level68_palette);
    load_numeric(root, "all_native_level_data/level69_foreground.bin", "3928af290083253fe19e7572c863671a8492aa2cc811c69053d6e8cf55e11796", rolo::all_native_level_data::level69_foreground);
    load_numeric(root, "all_native_level_data/level69_background.bin", "4a9e2d92b9073ecea10afe591e069c469fbecb1b435923f7722914f1c7cb388d", rolo::all_native_level_data::level69_background);
    load_numeric(root, "all_native_level_data/level69_palette.bin", "33062fa1adcfb556e01393bb12fc79f2d0e7a8400c5218bb4b27b923034a58c2", rolo::all_native_level_data::level69_palette);
    load_numeric(root, "all_native_level_data/level70_foreground.bin", "4b1af9868e78c5e7691faa89e939d8792c11d36d08d9177fa141002f0fe520dc", rolo::all_native_level_data::level70_foreground);
    load_numeric(root, "all_native_level_data/level70_background.bin", "ee2b4aebbf831c827ca70386e5b5c7f24c757cc8faf28964dd178e177a46c8b2", rolo::all_native_level_data::level70_background);
    load_numeric(root, "all_native_level_data/level70_palette.bin", "77e1b6343df348200dbc479f976ed3f34bb4a75a585d3845dcd292c94ec5dc8c", rolo::all_native_level_data::level70_palette);
    load_numeric(root, "all_native_level_data/level71_foreground.bin", "8c77e9c350ed1466dbc50950765d49303aa0c72ba6ffe1ed48ffb6a89e72fb6a", rolo::all_native_level_data::level71_foreground);
    load_numeric(root, "all_native_level_data/level71_background.bin", "ee2b4aebbf831c827ca70386e5b5c7f24c757cc8faf28964dd178e177a46c8b2", rolo::all_native_level_data::level71_background);
    load_numeric(root, "all_native_level_data/level71_palette.bin", "77e1b6343df348200dbc479f976ed3f34bb4a75a585d3845dcd292c94ec5dc8c", rolo::all_native_level_data::level71_palette);
    load_numeric(root, "all_native_level_data/level72_foreground.bin", "6aeaa5c236274f9df69401cebd5e6deafcd7526ad6b362758bed116f2dc1c1c6", rolo::all_native_level_data::level72_foreground);
    load_numeric(root, "all_native_level_data/level72_background.bin", "00bf6c50fc1b61600ee19bbc857ecf8bf45193cc34c9be156c571b9a3a6db4a0", rolo::all_native_level_data::level72_background);
    load_numeric(root, "all_native_level_data/level72_palette.bin", "5111898b9bf7d5344acc259fcaf4b7b9539b6070620f5d12382635ce5575620c", rolo::all_native_level_data::level72_palette);
    load_numeric(root, "all_native_level_data/level73_foreground.bin", "bc34df81b58d8e5f0eef216f5c74cb5979e9f566b66d1445e5950ffa23d8c339", rolo::all_native_level_data::level73_foreground);
    load_numeric(root, "all_native_level_data/level73_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level73_background);
    load_numeric(root, "all_native_level_data/level73_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level73_palette);
    load_numeric(root, "all_native_level_data/level77_foreground.bin", "f253f0920e5f231ef6fb8dd0bffecbc811ced3c48ad4cf929e568d9df62a7a8d", rolo::all_native_level_data::level77_foreground);
    load_numeric(root, "all_native_level_data/level77_background.bin", "df831a9f2a8933a504a5ade260b22ff8bbee00ac2023378bee2aa2b59b3fe76a", rolo::all_native_level_data::level77_background);
    load_numeric(root, "all_native_level_data/level77_palette.bin", "c29df3cb01c258ced69d74021db2bf2f1c3d297fce82926e93329ed510e21162", rolo::all_native_level_data::level77_palette);
    load_numeric(root, "all_native_level_data/level78_foreground.bin", "a0a1310511d6dd72bf81a6e5acb37eaaeead0faed0fc93c3021ee74d74352d61", rolo::all_native_level_data::level78_foreground);
    load_numeric(root, "all_native_level_data/level78_background.bin", "00bf6c50fc1b61600ee19bbc857ecf8bf45193cc34c9be156c571b9a3a6db4a0", rolo::all_native_level_data::level78_background);
    load_numeric(root, "all_native_level_data/level78_palette.bin", "77e1b6343df348200dbc479f976ed3f34bb4a75a585d3845dcd292c94ec5dc8c", rolo::all_native_level_data::level78_palette);
    load_numeric(root, "all_native_level_data/selectors.bin", "72b1f1719fa22f5dcb6ec55271ed82d14399e2061bcfbba4b7813dea0a973e7e", rolo::all_native_level_data::selectors);
    load_numeric(root, "actor_pattern_data/bytes.bin", "8da5f9e8dda5b121115c5a888121d67a08fc2329ad0d2d30a1b62b93e685c6e4", rolo::actor_pattern_data::bytes);
    load_numeric(root, "opening_data/startup.bin", "117c91612f587d7f7b7aa322c7131f1b870a7b7b091b3ec8dbd5f152c0a269bf", rolo::opening_data::startup);
    load_numeric(root, "opening_data/font.bin", "57110bfb9428ff1a6e1beb579012d6a25b6388f6c4803431c209ea013692dea1", rolo::opening_data::font);
    load_numeric(root, "opening_data/colour.bin", "9a54db412f99f4779321580794321cf9fe5999bc216f38f51a2d047a396bd1a9", rolo::opening_data::colour);
    load_numeric(root, "opening_data/photo.bin", "26e87042ca5a37a01eb1d8ea3a141863a8905b2edfef9a999f80877d3429d6d0", rolo::opening_data::photo);
    load_numeric(root, "opening_data/back.bin", "9035f2f7a342f645bbccbc3a46e8808b1ce1cae88ee498ff6417384529c79192", rolo::opening_data::back);
    load_numeric(root, "opening_data/front.bin", "91f11bf99f06e42f2f7c6fdf67cd4e58e761b361014aa93e9387598d77382f14", rolo::opening_data::front);
    load_numeric(root, "opening_data/logo.bin", "5a3c5855ddb57042aaf95598fc227261aeecfd05dfdb9f614a34ecb875d9c78a", rolo::opening_data::logo);
    load_numeric(root, "opening_data/photo_back.bin", "abdda54efac906392660dbaca7ba22a23eb28f3cc4efc6d4b87fd4f6dc651858", rolo::opening_data::photo_back);
    load_numeric(root, "opening_data/photo_front.bin", "feff5ed5e9f42f8f61c46411cb238edf0f5028f941aecfbcb4d3ab0ae7aaa4a7", rolo::opening_data::photo_front);
    load_numeric(root, "opening_data/sprite_pixels.bin", "51845bc77264ed547df02fda9f18cab25929ac12e1817e7848c0e0381cd998cd", rolo::opening_data::sprite_pixels);
    load_numeric(root, "level1_indexed_background_data/pixels.bin", "cd2ca6f58527cceb4c93ce91314a98b596bb8f6a365385484019e1ef5cc99c42", rolo::level1_indexed_background_data::pixels);
    load_numeric(root, "music_sequence_data/bytes.bin", "08f2417ad1a07367883a8fbd56b810977b4c8c237c3024119d23490255cde878", rolo::music_bank::bytes);
    load_numeric(root, "music_sequence_data/offsets.bin", "1c0a60e6631db0485b25fb9fd8d1b19021969815707be7e0f28330c933be849f", rolo::music_bank::offsets);
    load_numeric(root, "music_sequence_data/level_pairs.bin", "46fe682d8812e42d7bcef43534c4c0eaf9bf0836b7a9e53dbb9afd4d9d331f49", rolo::music_bank::level_pairs);
    load_numeric(root, "music_sequence_data/cycle.bin", "8d78dd242650ea5e34fdaa48d74cba646a7442981fecd4e78900dc8602646101", rolo::music_bank::cycle);
    load_numeric(root, "music_sequence_data/delays.bin", "3f1532be6044f116b2deb2c6c886b2d1649060bb353083817f100cf604bb36c0", rolo::music_bank::delays);
    load_numeric(root, "level1_terrain_data/map_bytes.bin", "910c87a8643a649cae3f0eee7cf800a2f945fc7c519d8c73e7a83c0046b80512", rolo::level1_terrain_data::map_bytes);
    load_numeric(root, "level1_terrain_data/macro_tiles.bin", "4849c82953fdf30f457ed7218871abcbabeac19692dce53262147f2180a16f58", rolo::level1_terrain_data::macro_tiles);
    load_numeric(root, "level1_terrain_data/quad_words.bin", "3712121a1166650043028f226864bb82efd208373fadc8d774c21fba5610d311", rolo::level1_terrain_data::quad_words);
    load_numeric(root, "level1_terrain_data/bank_patterns.bin", "66a00b3fba3caa446250ae5378f62a8e2d65f416be8891718dc3c2aa5e86d74c", rolo::level1_terrain_data::bank_patterns);
    load_numeric(root, "level1_terrain_data/common_patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::level1_terrain_data::common_patterns);
    load_numeric(root, "level1_terrain_data/background_map_bytes.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::level1_terrain_data::background_map_bytes);
    load_numeric(root, "level1_terrain_data/palette_words.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::level1_terrain_data::palette_words);
    load_numeric(root, "level1_terrain_data/history_selector_bytes.bin", "ed136a6b46d88d73f131c933e4cc6cabe602497bb1ce359f9f27d4d0646f1ed2", rolo::level1_terrain_data::history_selector_bytes);
    load_numeric(root, "level1_terrain_data/post_motion_table_bytes.bin", "8ef55c1db31213a4548fecaf8e1033cad125e4a798d8cab156dfd849a57c183c", rolo::level1_terrain_data::post_motion_table_bytes);
    load_numeric(root, "level1_terrain_data/rolo_slope_forward.bin", "0f468319b361ab9fcf3be4e3d51ddfdcd87790da98076482edbc40605b64e638", rolo::level1_terrain_data::rolo_slope_forward);
    load_numeric(root, "level1_terrain_data/rolo_slope_reverse.bin", "6a709402e535d4ab7b33e8fc5f5f79ed463ea94047e621a7891fcb2d8b7b63c7", rolo::level1_terrain_data::rolo_slope_reverse);
    load_numeric(root, "level1_terrain_data/rolo_slope_run_forward.bin", "0534a91790a23416cde076a1035cd881072735a54a7fa5b6275c1f0de53bc156", rolo::level1_terrain_data::rolo_slope_run_forward);
    load_numeric(root, "level1_terrain_data/rolo_slope_run_reverse.bin", "89a3ba13620580d74a4e0813ab159a0e5efe628f5a8e2a31cc4d4b4a3847a816", rolo::level1_terrain_data::rolo_slope_run_reverse);
    load_numeric(root, "level2_terrain_data/map_bytes.bin", "fa9de87576cb3238458f36889e27dc6986ea85352643466ebbaa3f7e4f50f787", rolo::level2_terrain_data::map_bytes);
    load_numeric(root, "level2_terrain_data/macro_tiles.bin", "4849c82953fdf30f457ed7218871abcbabeac19692dce53262147f2180a16f58", rolo::level2_terrain_data::macro_tiles);
    load_numeric(root, "level2_terrain_data/quad_words.bin", "3712121a1166650043028f226864bb82efd208373fadc8d774c21fba5610d311", rolo::level2_terrain_data::quad_words);
    load_numeric(root, "level2_terrain_data/bank_patterns.bin", "66a00b3fba3caa446250ae5378f62a8e2d65f416be8891718dc3c2aa5e86d74c", rolo::level2_terrain_data::bank_patterns);
    load_numeric(root, "level2_terrain_data/common_patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::level2_terrain_data::common_patterns);
    load_numeric(root, "level2_terrain_data/background_map_bytes.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::level2_terrain_data::background_map_bytes);
    load_numeric(root, "level2_terrain_data/palette_words.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::level2_terrain_data::palette_words);
    load_numeric(root, "level2_terrain_data/history_selector_bytes.bin", "ed136a6b46d88d73f131c933e4cc6cabe602497bb1ce359f9f27d4d0646f1ed2", rolo::level2_terrain_data::history_selector_bytes);
    load_numeric(root, "level2_terrain_data/post_motion_table_bytes.bin", "8ef55c1db31213a4548fecaf8e1033cad125e4a798d8cab156dfd849a57c183c", rolo::level2_terrain_data::post_motion_table_bytes);
    load_numeric(root, "level2_terrain_data/rolo_slope_forward.bin", "0f468319b361ab9fcf3be4e3d51ddfdcd87790da98076482edbc40605b64e638", rolo::level2_terrain_data::rolo_slope_forward);
    load_numeric(root, "level2_terrain_data/rolo_slope_reverse.bin", "6a709402e535d4ab7b33e8fc5f5f79ed463ea94047e621a7891fcb2d8b7b63c7", rolo::level2_terrain_data::rolo_slope_reverse);
    load_numeric(root, "level2_terrain_data/rolo_slope_run_forward.bin", "0534a91790a23416cde076a1035cd881072735a54a7fa5b6275c1f0de53bc156", rolo::level2_terrain_data::rolo_slope_run_forward);
    load_numeric(root, "level2_terrain_data/rolo_slope_run_reverse.bin", "89a3ba13620580d74a4e0813ab159a0e5efe628f5a8e2a31cc4d4b4a3847a816", rolo::level2_terrain_data::rolo_slope_run_reverse);
    load_numeric(root, "level3_terrain_data/map_bytes.bin", "ffc57e472570a1272d64e3f3afdeaffde59405d0a4605771ee240394beeb2a24", rolo::level3_terrain_data::map_bytes);
    load_numeric(root, "level3_terrain_data/macro_tiles.bin", "4849c82953fdf30f457ed7218871abcbabeac19692dce53262147f2180a16f58", rolo::level3_terrain_data::macro_tiles);
    load_numeric(root, "level3_terrain_data/quad_words.bin", "3712121a1166650043028f226864bb82efd208373fadc8d774c21fba5610d311", rolo::level3_terrain_data::quad_words);
    load_numeric(root, "level3_terrain_data/bank_patterns.bin", "66a00b3fba3caa446250ae5378f62a8e2d65f416be8891718dc3c2aa5e86d74c", rolo::level3_terrain_data::bank_patterns);
    load_numeric(root, "level3_terrain_data/common_patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::level3_terrain_data::common_patterns);
    load_numeric(root, "level3_terrain_data/background_map_bytes.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::level3_terrain_data::background_map_bytes);
    load_numeric(root, "level3_terrain_data/palette_words.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::level3_terrain_data::palette_words);
    load_numeric(root, "level3_terrain_data/history_selector_bytes.bin", "ed136a6b46d88d73f131c933e4cc6cabe602497bb1ce359f9f27d4d0646f1ed2", rolo::level3_terrain_data::history_selector_bytes);
    load_numeric(root, "level3_terrain_data/post_motion_table_bytes.bin", "8ef55c1db31213a4548fecaf8e1033cad125e4a798d8cab156dfd849a57c183c", rolo::level3_terrain_data::post_motion_table_bytes);
    load_numeric(root, "level3_terrain_data/rolo_slope_forward.bin", "0f468319b361ab9fcf3be4e3d51ddfdcd87790da98076482edbc40605b64e638", rolo::level3_terrain_data::rolo_slope_forward);
    load_numeric(root, "level3_terrain_data/rolo_slope_reverse.bin", "6a709402e535d4ab7b33e8fc5f5f79ed463ea94047e621a7891fcb2d8b7b63c7", rolo::level3_terrain_data::rolo_slope_reverse);
    load_numeric(root, "level3_terrain_data/rolo_slope_run_forward.bin", "0534a91790a23416cde076a1035cd881072735a54a7fa5b6275c1f0de53bc156", rolo::level3_terrain_data::rolo_slope_run_forward);
    load_numeric(root, "level3_terrain_data/rolo_slope_run_reverse.bin", "89a3ba13620580d74a4e0813ab159a0e5efe628f5a8e2a31cc4d4b4a3847a816", rolo::level3_terrain_data::rolo_slope_run_reverse);
    load_numeric(root, "level4_terrain_data/map_bytes.bin", "e78c0c8755880ac542fb914acfe9da70ccfaa00cad5ebe842b38d969396e69ff", rolo::level4_terrain_data::map_bytes);
    load_numeric(root, "level4_terrain_data/macro_tiles.bin", "4849c82953fdf30f457ed7218871abcbabeac19692dce53262147f2180a16f58", rolo::level4_terrain_data::macro_tiles);
    load_numeric(root, "level4_terrain_data/quad_words.bin", "3712121a1166650043028f226864bb82efd208373fadc8d774c21fba5610d311", rolo::level4_terrain_data::quad_words);
    load_numeric(root, "level4_terrain_data/bank_patterns.bin", "66a00b3fba3caa446250ae5378f62a8e2d65f416be8891718dc3c2aa5e86d74c", rolo::level4_terrain_data::bank_patterns);
    load_numeric(root, "level4_terrain_data/common_patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::level4_terrain_data::common_patterns);
    load_numeric(root, "level4_terrain_data/background_map_bytes.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::level4_terrain_data::background_map_bytes);
    load_numeric(root, "level4_terrain_data/palette_words.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::level4_terrain_data::palette_words);
    load_numeric(root, "level4_terrain_data/history_selector_bytes.bin", "ed136a6b46d88d73f131c933e4cc6cabe602497bb1ce359f9f27d4d0646f1ed2", rolo::level4_terrain_data::history_selector_bytes);
    load_numeric(root, "level4_terrain_data/post_motion_table_bytes.bin", "8ef55c1db31213a4548fecaf8e1033cad125e4a798d8cab156dfd849a57c183c", rolo::level4_terrain_data::post_motion_table_bytes);
    load_numeric(root, "level4_terrain_data/rolo_slope_forward.bin", "0f468319b361ab9fcf3be4e3d51ddfdcd87790da98076482edbc40605b64e638", rolo::level4_terrain_data::rolo_slope_forward);
    load_numeric(root, "level4_terrain_data/rolo_slope_reverse.bin", "6a709402e535d4ab7b33e8fc5f5f79ed463ea94047e621a7891fcb2d8b7b63c7", rolo::level4_terrain_data::rolo_slope_reverse);
    load_numeric(root, "level4_terrain_data/rolo_slope_run_forward.bin", "0534a91790a23416cde076a1035cd881072735a54a7fa5b6275c1f0de53bc156", rolo::level4_terrain_data::rolo_slope_run_forward);
    load_numeric(root, "level4_terrain_data/rolo_slope_run_reverse.bin", "89a3ba13620580d74a4e0813ab159a0e5efe628f5a8e2a31cc4d4b4a3847a816", rolo::level4_terrain_data::rolo_slope_run_reverse);
    load_numeric(root, "level8_terrain_data/map_bytes.bin", "4817fc80089b8a228c937f973792cb12141f7cae7cbcaeac4ad34ed36d3d9967", rolo::level8_terrain_data::map_bytes);
    load_numeric(root, "level8_terrain_data/macro_tiles.bin", "4849c82953fdf30f457ed7218871abcbabeac19692dce53262147f2180a16f58", rolo::level8_terrain_data::macro_tiles);
    load_numeric(root, "level8_terrain_data/quad_words.bin", "3712121a1166650043028f226864bb82efd208373fadc8d774c21fba5610d311", rolo::level8_terrain_data::quad_words);
    load_numeric(root, "level8_terrain_data/bank_patterns.bin", "66a00b3fba3caa446250ae5378f62a8e2d65f416be8891718dc3c2aa5e86d74c", rolo::level8_terrain_data::bank_patterns);
    load_numeric(root, "level8_terrain_data/common_patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::level8_terrain_data::common_patterns);
    load_numeric(root, "level8_terrain_data/background_map_bytes.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::level8_terrain_data::background_map_bytes);
    load_numeric(root, "level8_terrain_data/palette_words.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::level8_terrain_data::palette_words);
    load_numeric(root, "level8_terrain_data/history_selector_bytes.bin", "ed136a6b46d88d73f131c933e4cc6cabe602497bb1ce359f9f27d4d0646f1ed2", rolo::level8_terrain_data::history_selector_bytes);
    load_numeric(root, "level8_terrain_data/post_motion_table_bytes.bin", "8ef55c1db31213a4548fecaf8e1033cad125e4a798d8cab156dfd849a57c183c", rolo::level8_terrain_data::post_motion_table_bytes);
    load_numeric(root, "level8_terrain_data/rolo_slope_forward.bin", "0f468319b361ab9fcf3be4e3d51ddfdcd87790da98076482edbc40605b64e638", rolo::level8_terrain_data::rolo_slope_forward);
    load_numeric(root, "level8_terrain_data/rolo_slope_reverse.bin", "6a709402e535d4ab7b33e8fc5f5f79ed463ea94047e621a7891fcb2d8b7b63c7", rolo::level8_terrain_data::rolo_slope_reverse);
    load_numeric(root, "level8_terrain_data/rolo_slope_run_forward.bin", "0534a91790a23416cde076a1035cd881072735a54a7fa5b6275c1f0de53bc156", rolo::level8_terrain_data::rolo_slope_run_forward);
    load_numeric(root, "level8_terrain_data/rolo_slope_run_reverse.bin", "89a3ba13620580d74a4e0813ab159a0e5efe628f5a8e2a31cc4d4b4a3847a816", rolo::level8_terrain_data::rolo_slope_run_reverse);
    load_numeric(root, "audio_bank_data/patches.bin", "075f902c200d46a60d1ce098f326a924bb6af49e289b97a8ef42031473b70c47", rolo::audio_data::patches);
    load_numeric(root, "audio_bank_data/registers.bin", "3caea3d8fc83dc9ebcfa56a73978ad924d0fe5699cc527b9677f01a9e4b848ca", rolo::audio_data::registers);
    load_numeric(root, "audio_bank_data/frequency_low.bin", "20f43548d49718c3612949fc40f66082172543e54760728139198b1403558994", rolo::audio_data::frequency_low);
    load_numeric(root, "audio_bank_data/frequency_high.bin", "af8dca1537ae8f9161ed0a5a72aea5846d7eb6b0a4e745693a9cf776347390be", rolo::audio_data::frequency_high);
    load_numeric(root, "cavern_tile_animation_data/patterns.bin", "49f29eaf33c30ce3bb91fbfb954b63ab39781a7f0c27ef097d5ac15f05497479", rolo::cavern_tile_animation_data::patterns);
    load_numeric(root, "cavern_tile_animation_data/sequences.bin", "ce3e629bab86bf40d5bdbe188fc527e5d89fb3971417029b62806e9622306d4f", rolo::cavern_tile_animation_data::sequences);
    load_numeric(root, "desert_tile_animation_data/patterns.bin", "edff3a14dc1e3fa2e30a9743c06adccff1327d4d8733140ffa41934080010632", rolo::desert_tile_animation_data::patterns);
    load_numeric(root, "desert_tile_animation_data/sequences.bin", "52592b227445a48c3e42a9a09709a35afedc191ff550ed4090144607f2bc918d", rolo::desert_tile_animation_data::sequences);
    load_numeric(root, "ending_data/pixels.bin", "661631b9e58c530efd80074a373982450f4acfaa991c9c37f83df9846858c784", rolo::ending_data::pixels);
    load_numeric(root, "first_enemy_definition_data/score_wave.bin", "e2c1fab77cf1cbebbc02d27edd963d78de586ead92ac501af9ad75da4ecc4544", rolo::first_enemy_definition_data::score_wave);
    load_numeric(root, "forest_level_data/level5_foreground.bin", "331a6635d8fc3a1521cb48c172d243b9d5a1c8064b3e65d1487992946d96993c", rolo::forest_level_data::level5_foreground);
    load_numeric(root, "forest_level_data/level5_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::forest_level_data::level5_background);
    load_numeric(root, "forest_level_data/level5_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level5_palette);
    load_numeric(root, "forest_level_data/level6_foreground.bin", "70e380e23428dbd7de275af99ca68eb2db3b8ba75e69596156cad39eb98a3a55", rolo::forest_level_data::level6_foreground);
    load_numeric(root, "forest_level_data/level6_background.bin", "e0fd7db59f9952326197d728ce8cd733e31956b1a067451cc14484e048199d16", rolo::forest_level_data::level6_background);
    load_numeric(root, "forest_level_data/level6_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level6_palette);
    load_numeric(root, "forest_level_data/level7_foreground.bin", "4bb70da9f6161e632984510d9cd1687a5f9ebe75f8143ebf67ab3924f4364a14", rolo::forest_level_data::level7_foreground);
    load_numeric(root, "forest_level_data/level7_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::forest_level_data::level7_background);
    load_numeric(root, "forest_level_data/level7_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level7_palette);
    load_numeric(root, "forest_level_data/level9_foreground.bin", "11892641df77a214b9da1e4221e8fabdcbb5505f8c1e0b973099713602b8bab1", rolo::forest_level_data::level9_foreground);
    load_numeric(root, "forest_level_data/level9_background.bin", "e0097ac57799c5fe0561973b248675106846f2187bd3bc652e5f118399191ab9", rolo::forest_level_data::level9_background);
    load_numeric(root, "forest_level_data/level9_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level9_palette);
    load_numeric(root, "forest_level_data/level10_foreground.bin", "d89598feb2b4d336727a08ccab18eefa5866ec8754067cef1d9515117cd79292", rolo::forest_level_data::level10_foreground);
    load_numeric(root, "forest_level_data/level10_background.bin", "e0097ac57799c5fe0561973b248675106846f2187bd3bc652e5f118399191ab9", rolo::forest_level_data::level10_background);
    load_numeric(root, "forest_level_data/level10_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level10_palette);
    load_numeric(root, "forest_level_data/level11_foreground.bin", "307d687b1196ebb0dbea287bf2336b7659f66aaed982843ed049869377103293", rolo::forest_level_data::level11_foreground);
    load_numeric(root, "forest_level_data/level11_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::forest_level_data::level11_background);
    load_numeric(root, "forest_level_data/level11_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level11_palette);
    load_numeric(root, "forest_level_data/level12_foreground.bin", "d02ad57dcf8b79ab8f335a1c9103dc4978bbbd2a1d0c5f7f60c6d179b5235cf6", rolo::forest_level_data::level12_foreground);
    load_numeric(root, "forest_level_data/level12_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::forest_level_data::level12_background);
    load_numeric(root, "forest_level_data/level12_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level12_palette);
    load_numeric(root, "forest_level_data/level13_foreground.bin", "fd6411f0be727ddc69ff1bc3aec3404ba25acc3ee82183dce541a08d6f40fe3f", rolo::forest_level_data::level13_foreground);
    load_numeric(root, "forest_level_data/level13_background.bin", "7bce6816205546540786278f98ddab3634a573fdf3da9ce8d18cc1bdc7f21a96", rolo::forest_level_data::level13_background);
    load_numeric(root, "forest_level_data/level13_palette.bin", "ac43be5f09359a3dc2f116a6e28b4b2106514c9f1134bf19e21a251c4e94523e", rolo::forest_level_data::level13_palette);
    load_numeric(root, "forest_tile_animation_data/patterns.bin", "601d741131e75bf454133b8915e715b9b28d893c3c82777a8e4aa24a03e9d9de", rolo::forest_tile_animation_data::patterns);
    load_numeric(root, "forest_tile_animation_data/sequences.bin", "f5aa5a0860fab93f0c7d583b2cc8b4e9ae2701feaaac0d9330ae7f8ac02b0161", rolo::forest_tile_animation_data::sequences);
    load_numeric(root, "level1_companion_menu_data/patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::level1_companion_menu_data::patterns);
    load_numeric(root, "level1_companion_menu_data/layout.bin", "d5ab051b250847333906da6c83cfcf4715cb79168ba635f48eab5324bd887d22", rolo::level1_companion_menu_data::layout);
    load_numeric(root, "level1_companion_menu_data/static_sprites.bin", "b179bd365bcae1a7cab51106c15f97ca4f7ce89093d46d9a6f75ef3294cc8223", rolo::level1_companion_menu_data::static_sprites);
    load_numeric(root, "level1_companion_menu_data/selection_sprites.bin", "7ea4e464350d46fa07f76fe947257dff0b339e4f36b714eb3a0855c3bf0ec350", rolo::level1_companion_menu_data::selection_sprites);
    load_numeric(root, "level1_companion_menu_data/companion_sprites.bin", "02e1495440e6e288f92bd05bafc18b9a71f6aae0fb2803b79f25f4e93204229c", rolo::level1_companion_menu_data::companion_sprites);
    load_numeric(root, "level1_companion_menu_data/inactive_sprites.bin", "7f7e430382b73404c9e61170fa225df3fec835cc123dc2f451e64bfff9f590ba", rolo::level1_companion_menu_data::inactive_sprites);
    load_numeric(root, "level1_companion_menu_data/palette.bin", "07a4d591de808b4e9b33d482abb5fcd28942f8d55fb0775f793408af7b3f9d1e", rolo::level1_companion_menu_data::palette);
    load_numeric(root, "level1_companion_presentation_data/head_x.bin", "ef47c979ea83ad394313f5d4f37391274928b02a6eb5e09bea58aa15a5a575d0", rolo::companion_presentation_data::head_x);
    load_numeric(root, "level1_completion_data/world_coordinate_bytes.bin", "332542ec347002542584571f723650312a5a50d3b9f4acb0bb879d57b0765332", rolo::world_coordinate_bytes);
    load_numeric(root, "level1_hud_data/wave.bin", "32945fa7c4a927bce5cc3226b0e3ae1b964e6fa0230b516d08a02a9ed643cbce", rolo::level1_hud_data::wave);
    load_numeric(root, "level1_hud_data/label.bin", "54ce7e672259c720cbb0bbcddbd6e82665fb457966cdff48931383723168b1e9", rolo::level1_hud_data::label);
    load_numeric(root, "level1_hud_data/blank.bin", "f5a5fd42d16a20302798ef6ed309979b43003d2320d9f0e8ea9831a92759fb4b", rolo::level1_hud_data::blank);
    load_numeric(root, "level1_hud_data/icon.bin", "4c3ec6163140243a4ad252ff29ce5ceecb5258dec9bf8fb773fad4076f8593a4", rolo::level1_hud_data::icon);
    load_numeric(root, "level1_hud_data/digits.bin", "424cca1bdebcb8e99601b81cf2d6522d54cefc17cb1f4286634a56de98ac704e", rolo::level1_hud_data::digits);
    load_numeric(root, "level1_object_data/collectible_spawn_table.bin", "13e6db91636be3f62cf3e9550e39d80992b19ca81f5dfc8b5797c060fb3edaa6", rolo::level1_object_data::collectible_spawn_table);
    load_numeric(root, "level1_object_data/enemy_spawn_table.bin", "e34ca276fcd6fbefc0a990678620da25936bbe0def79b02d94b6dcfe61e9d185", rolo::level1_object_data::enemy_spawn_table);
    load_numeric(root, "level1_object_data/special_spawn_table.bin", "c29cda263a304930f26aa19eb8d4f11ed43a0e5a2955092ac596a80096da8579", rolo::level1_object_data::special_spawn_table);
    load_numeric(root, "level1_object_data/generic_spawn_table.bin", "687a842407d441c8521138273456eac5a49e2facf5ba93c922e86515d72fddc6", rolo::level1_object_data::generic_spawn_table);
    load_numeric(root, "level1_object_data/companion_spawn_table.bin", "cd9ad0f8978478437b0ef26516d8ae3bf1bb9af5e3fb3f47719e52ba3ef7d76a", rolo::level1_object_data::companion_spawn_table);
    load_numeric(root, "level1_object_data/ride_slope_forward.bin", "26f9106f9ea9ede07fcf9931f78a817ac59b523223d25884ebec86b373247b7d", rolo::level1_object_data::ride_slope_forward);
    load_numeric(root, "level1_object_data/ride_slope_reverse.bin", "89a3ba13620580d74a4e0813ab159a0e5efe628f5a8e2a31cc4d4b4a3847a816", rolo::level1_object_data::ride_slope_reverse);
    load_numeric(root, "level1_object_data/phase_boss_offsets.bin", "b887b93f8536f80bc8aedbe3df610d93efc9b4803ec9f1b5ce4546633dd3c958", rolo::level1_object_data::phase_boss_offsets);
    load_numeric(root, "level1_object_data/choreography_spawn.bin", "1516d3fe86e7431439f893e83466f14aa0a4e0073a27d8192089d38b77cf0ab5", rolo::level1_object_data::choreography_spawn);
    load_numeric(root, "level1_object_data/choreography_permutations.bin", "b552be06ce0f3b2cde1f5aab484e71c709771cc043a5131dec3cfe91dd365346", rolo::level1_object_data::choreography_permutations);
    load_numeric(root, "level1_object_data/choreography_groups.bin", "7e3a71bd8af4a36eb15d6ea94400edf3fd9c54c8758f03dd2a1fec32c613118e", rolo::level1_object_data::choreography_groups);
    load_numeric(root, "level1_object_data/choreography_tiles.bin", "e1407ea4f2215fbf56632028100e36e299995dbd1af5b01fbeb0e67403569e2c", rolo::level1_object_data::choreography_tiles);
    load_numeric(root, "level1_object_data/spawner_rewards.bin", "6bf5eb0d9daa428c232332628db13e35fb44318eff3fae81352314d16ca81fca", rolo::level1_object_data::spawner_rewards);
    load_numeric(root, "level1_object_data/spawner_directions.bin", "4fe9f9290e0d4a6d6dcbceaf8e199e12c74d714ba31cc186eef9a4373bfebcbe", rolo::level1_object_data::spawner_directions);
    load_numeric(root, "level1_object_data/boss29_part_offsets.bin", "7cc96c91f28754f9f55a03020f1b3960b078c992013ffc19433e16bc0ae8dcd4", rolo::level1_object_data::boss29_part_offsets);
    load_numeric(root, "level1_object_data/common_flash_palette.bin", "06a48db0c38e60a6bfdeb325fdce4512b452d25366d0ce85f64e9d601a4c798e", rolo::level1_object_data::common_flash_palette);
    load_numeric(root, "level1_object_data/companion_menu_navigation.bin", "eae7df12821bd544bb04d751800332093f835e90d20d9522b6de24ab2c800fde", rolo::level1_object_data::companion_menu_navigation);
    load_numeric(root, "level1_status_hud_data/sprite_templates.bin", "46494a02801825f2a06b5d9028dc0a7d0aa3b52b62953ff33499b199269e90ed", rolo::level1_status_hud_data::sprite_templates);
    load_numeric(root, "level1_status_hud_data/portrait.bin", "dd725af96823cc6a30753fdc0f4c479487b6b6f9134a421ecab167b7aeacfe60", rolo::level1_status_hud_data::portrait);
    load_numeric(root, "level1_status_hud_data/life_label.bin", "4c3ec6163140243a4ad252ff29ce5ceecb5258dec9bf8fb773fad4076f8593a4", rolo::level1_status_hud_data::life_label);
    load_numeric(root, "level1_status_hud_data/digits.bin", "424cca1bdebcb8e99601b81cf2d6522d54cefc17cb1f4286634a56de98ac704e", rolo::level1_status_hud_data::digits);
    load_numeric(root, "level1_status_hud_data/key.bin", "69e74a3a48491615cd8cf6eaaf518f851063472333be04ae751fa9d21ecf11c1", rolo::level1_status_hud_data::key);
    load_numeric(root, "level1_status_hud_data/piece.bin", "5a750ba106e5ab83d15ae3c06d5fcf1a1cbc3402376bd7c7eb1ee750f23f1927", rolo::level1_status_hud_data::piece);
    load_numeric(root, "level1_world_data/head_offsets.bin", "69f2c534f0dd2049005dd4cbfe012f009415b36704e275e7ce99b7d7f66310fa", rolo::level1_world_data::head_offsets);
    load_numeric(root, "palette_effect_data/lookup.bin", "c2032bb86eea94ba949c8589be48906d0bf9f6ebacc28a07bb0ff88940f7a0c8", rolo::palette_effect_data::lookup);
    load_numeric(root, "player_data/grid.bin", "a2e89e414fcbc76eeeffd7c94a6ba0cf8183834f2248878bc7fda1dcc4525866", rolo::player_data::grid);
    load_numeric(root, "player_data/collision.bin", "414a331bb2ce9a6eb49cada69ebefce4caafb54eddffad26fc2a1dad01fdcbb2", rolo::player_data::collision);
    load_numeric(root, "player_data/shapes.bin", "85c60426080d9d33de81ea6eb183896e97425a1356af7dd32dba735b3b5d0fcb", rolo::player_data::shapes);
    load_numeric(root, "player_data/walk_forward.bin", "50f845afe7896d2317c34554967cd80fb6d3d596926c3162ad33df79330ded1c", rolo::player_data::walk_forward);
    load_numeric(root, "player_data/walk_reverse.bin", "114da6af44bb70920b902f174d9cecd6da822a73c11538ee4bd790ae298dc1dd", rolo::player_data::walk_reverse);
    load_numeric(root, "player_data/run_forward.bin", "08ed0c440e6d8febb1334cffa1a1e96df5872b1f351bbed0a2d152eea4ea2e32", rolo::player_data::run_forward);
    load_numeric(root, "player_data/run_reverse.bin", "85ce7e97d63a46112709baeee77248d514557c9dfc5a15106beb809f777b3428", rolo::player_data::run_reverse);
    load_numeric(root, "sound_effect_data/descriptors.bin", "617e8b4e32b2e81c0ee24c952268e450c8e0533b7a125472497b3c1f09341e9f", rolo::effect_bank::descriptors);
    load_numeric(root, "spawn_branch_data/kind4.bin", "e34ca276fcd6fbefc0a990678620da25936bbe0def79b02d94b6dcfe61e9d185", rolo::spawn_branch_data::kind4);
    load_numeric(root, "spawn_branch_data/kind5.bin", "687a842407d441c8521138273456eac5a49e2facf5ba93c922e86515d72fddc6", rolo::spawn_branch_data::kind5);
    load_numeric(root, "spawn_branch_data/kind6.bin", "13e6db91636be3f62cf3e9550e39d80992b19ca81f5dfc8b5797c060fb3edaa6", rolo::spawn_branch_data::kind6);
    load_numeric(root, "spawn_branch_data/kind13.bin", "c29cda263a304930f26aa19eb8d4f11ed43a0e5a2955092ac596a80096da8579", rolo::spawn_branch_data::kind13);
    load_numeric(root, "suction_particle_data/patterns.bin", "04404271a241f398bdd4fea693f93304af76d2308a7ad08cb1e36758afccd86a", rolo::suction_particle_data::patterns);
    load_numeric(root, "world_map_data/foreground.bin", "3d492372401a1c0ca7b712513ddc6ff66d593638f20838205f82b31029479a38", rolo::world_map_data::foreground);
    load_numeric(root, "world_map_data/graphics.bin", "ce277c8f09c420c8e223c567d62ea264685cfe4790885cc48d1708609ab603d8", rolo::world_map_data::graphics);
    load_numeric(root, "world_map_data/palette.bin", "7070fa5ef9caa4ae15278071782e4eee8f9cfcf7439dfdef6795aa2208022d7b", rolo::world_map_data::palette);
    load_numeric(root, "world_map_data/quads.bin", "65476c1bd62a294697aa46925dc08b1d85647a25c35e42e47ca5201619e708a7", rolo::world_map_data::quads);
    load_numeric(root, "world_map_data/macros.bin", "872e638d6e8a4cd17ba07ed8396b6f6f7475fa8e11fe7a855c5659f21734bdb0", rolo::world_map_data::macros);
    load_numeric(root, "world_map_data/common_quads.bin", "399d612fedcf4a7ea68a06982ff2f8ac22191352cb63734405987b6ecb76d908", rolo::world_map_data::common_quads);
    load_numeric(root, "world_map_data/common_patterns.bin", "81add834541283eadc58acea8ef68baa3d3053da1eb41707864ab16a9f5b9a75", rolo::world_map_data::common_patterns);
    load_numeric(root, "world_map_data/return_coordinates.bin", "332542ec347002542584571f723650312a5a50d3b9f4acb0bb879d57b0765332", rolo::world_map_data::return_coordinates);
    load_numeric(root, "world_map_data/completion_selectors.bin", "961e62b4c13b7e6a00cfe749a648fab43d74d13b296ef1b80403504ad7dcc742", rolo::world_map_data::completion_selectors);
    load_numeric(root, "world_map_data/completed_marker.bin", "912f33cf4f5a6cb2b8bf321360a5fb087d9076792f67910fbf943beb215ecbc3", rolo::world_map_data::completed_marker);
    load_numeric(root, "world_map_data/palette_cycle.bin", "fd5833cc132badbc04137bea0a8c5debb76efcfcf323b22253175164f5cdce3f", rolo::world_map_data::palette_cycle);
    load_numeric(root, "world_route_data/route_bytes.bin", "b40e031b0c53082e9936f5c953da8f940ceff84b7b1aaf08eb653eabc5014996", rolo::world_route_data::route_bytes);
    load_numeric(root, "world_tile_animation_data/patterns.bin", "ce5274fc64268f951a3fbba5115513f0aa985d08f3dd9ac62b2511f5090d204f", rolo::world_tile_animation_data::patterns);
    load_numeric(root, "world_tile_animation_data/sequences.bin", "a938f7bd6a904a9c024e8ff5dddc7e6d5d3e815b691c97ee12808405496c40f0", rolo::world_tile_animation_data::sequences);
    load_tracks(root, "cavern_tile_animation_data/tracks.bin", "596f8c5b6cbcc17a646753a56671990ee0e084fb8d90d15dd358d3644ebbcee6", rolo::cavern_tile_animation_data::tracks);
    load_tracks(root, "desert_tile_animation_data/tracks.bin", "1ead0a4209a618eb15e8e783d3d92991ff8c0af94d6f81f4c5c7e4c5d50ffb6e", rolo::desert_tile_animation_data::tracks);
    load_actor_definitions(root, "dynamic_platform_data/definitions.bin", "732e58d119f2c2ae4c2cdb2f004bc8c0c946127cffdce4c171f595711e2d47f0", rolo::dynamic_platform_data::definitions);
    load_animation_frames(root, "ending_animation_data/frames.bin", "45adf8f63f4718ef24b2a6e71e162fbeba4f170780c765fd09458781f3a3fb67", rolo::ending_animation_data::frames);
    load_animation_nodes(root, "ending_animation_data/nodes.bin", "17697a99370c5d491ff8f5348ea5584f950e565cb00637e60aada866a9135966", rolo::ending_animation_data::nodes);
    load_animation_programs(root, "ending_animation_data/programs.bin", "eedaa485f238143f390c093c84a745a2a87a7642bacb2544faed99ad7d9b8ce2", rolo::ending_animation_data::programs);
    load_sprites(root, "ending_data/sprites.bin", "8d24cd8f77825e05846281c841f1cccdbf8b0144ecde43e06bf1122c1f482fcb", rolo::ending_data::sprites);
    load_enemy_bursts(root, "enemy_phase_entries/enemy_burst_records.bin", "22bf765e6930120013014115055977db6e773a0a5984165962e9f81db7cd6941", rolo::enemy_burst_records);
    load_animation_frames(root, "entrance_data/frames.bin", "b89177beb9e4d97d7b3bf359d56fdad261a5a314ddabfd80d3da60ddf48b83b6", rolo::entrance_data::frames);
    load_animation_nodes(root, "entrance_data/nodes.bin", "62f0fe8d7ad4e32af3faa0722c7ab63a1bba087e49f9fe1ecd67e59ceb5e8dc9", rolo::entrance_data::nodes);
    load_animation_programs(root, "entrance_data/programs.bin", "5f870e6ef3a0d4994043007497e929446cfae86967a08a91bb85b44d4ad72cbb", rolo::entrance_data::programs);
    load_animation_frames(root, "first_enemy_animation_data/frames.bin", "ce3c2c81c407465257e4e53b0466643cbc2012d2de853ae1c723ed21fa88dfdb", rolo::first_enemy_animation_data::frames);
    load_animation_nodes(root, "first_enemy_animation_data/nodes.bin", "e7f25a1b81ef852552acc03b8a6e8bd836f7f984ab35c576e6414d3c4f7a1c4c", rolo::first_enemy_animation_data::nodes);
    load_animation_programs(root, "first_enemy_animation_data/programs.bin", "3fd3ec09be560bf5c21ad7ebaddbb633697c9a97a7c6c78f7a0f4df189974c38", rolo::first_enemy_animation_data::programs);
    load_actor_definitions(root, "first_enemy_definition_data/definitions.bin", "d9bad6f2e7399d783ba0f279b5423263b2da01bbffacec04445c9e261d248ff5", rolo::first_enemy_definition_data::definitions);
    load_tracks(root, "forest_tile_animation_data/tracks.bin", "cace202668aaacf00757b58d10cb2d9d0a3a8495621960ff681725bebebfae6d", rolo::forest_tile_animation_data::tracks);
    load_animation_frames(root, "level1_object_animation_data/frames.bin", "afb19029369b2081f2a6943adfb851c4f0abcd516849841af953f6165ab5a068", rolo::level1_object_animation_data::frames);
    load_animation_nodes(root, "level1_object_animation_data/nodes.bin", "f9f9ab45dfb0780d8636887fe671f84cd3ed341d0e2275b2dc9cea3e0dc23b64", rolo::level1_object_animation_data::nodes);
    load_animation_programs(root, "level1_object_animation_data/programs.bin", "5749851b45d5daa9c61ed084183dd4349b064abb0daa4e151010e2cac1c893b4", rolo::level1_object_animation_data::programs);
    load_actor_definitions(root, "level1_object_data/definitions.bin", "82671cf361f19d4a0b4930c9eee1166a4205648238297a834dfa9d88c241b45e", rolo::level1_object_data::definitions);
    load_animation_frames(root, "level1_player_animation_data/frames.bin", "9c3ee5b6d039d2bdec6dba48d026697ac967a7ab5eacfaf8e9318799fe453b42", rolo::level1_player_animation_data::frames);
    load_animation_nodes(root, "level1_player_animation_data/nodes.bin", "836ea0989d70f4713b3cada9be06cec85142ded12bc90646680e88ed2213b3a1", rolo::level1_player_animation_data::nodes);
    load_animation_programs(root, "level1_player_animation_data/programs.bin", "587aea8e492f754dad9015f52be86427d8f9b800e0600cfde6de3a8b1cf2baf4", rolo::level1_player_animation_data::programs);
    load_actor_definitions(root, "level1_world_data/definitions.bin", "ff9781a63ba827e06a62e12a26296032dbeda9ee6948980ff9b73bcff9b7d8c3", rolo::level1_world_data::definitions);
    load_animation_frames(root, "player_animation_data/frames.bin", "3a22a9c9055aaf484e417e1b066c607ec0e2d01582c58c597cdde1e79dee0342", rolo::player_animation_data::frames);
    load_animation_nodes(root, "player_animation_data/nodes.bin", "7fc1f612d3277957bc31233ee24dc69be818359475d2fe16a5bd441b049c92fc", rolo::player_animation_data::nodes);
    load_animation_programs(root, "player_animation_data/programs.bin", "91319f0da4a0a72b3ea91c7d01f4645afca80c694deb74705431cf51b639e2df", rolo::player_animation_data::programs);
    load_graphics(root, "suction_particle_data/graphics.bin", "ecae1144c60c6ea62ace2363c88fe4f2b5f9ffd1f016bcaa891a3ed1aef5eb0a", rolo::suction_particle_data::graphics);
    load_animation_frames(root, "world_bunny_data/frames.bin", "c44c222896493c9ebf9b13163f2f59bf86e722eff835ed14a6be1ae51e6d6ad4", rolo::world_bunny_data::frames);
    load_animation_nodes(root, "world_bunny_data/nodes.bin", "d58cec6903fdf277801d2346b0fccd7e027efc0b170bc439f876858f502478cb", rolo::world_bunny_data::nodes);
    load_animation_programs(root, "world_bunny_data/programs.bin", "fe91a73427db1d8373a3738d4070e2fa1e1a799a20d8017ffacbce2d624556e5", rolo::world_bunny_data::programs);
    load_animation_frames(root, "world_cursor_data/frames.bin", "4b9cec3c07e3704da5f12d5008b4df2f14b1d20d3106a959f22cdec7d9bfe348", rolo::world_cursor_data::frames);
    load_animation_nodes(root, "world_cursor_data/nodes.bin", "be4f1b3e1394f10da9a4272b9fc5b24b2fce1c9013e87ecbdadf02c7d88cdec2", rolo::world_cursor_data::nodes);
    load_animation_programs(root, "world_cursor_data/programs.bin", "6eca5e203db4f24a295d2a2d664ab401df9eb3578ba3258bcff30d2e3dff1bfe", rolo::world_cursor_data::programs);
    load_pieces(root, "world_map_data/pieces.bin", "3ade4b635c61193aff2caac912750e33e038dd0d1b9deb72f98f401cb1eb296e", rolo::world_map_data::pieces);
    load_descriptors(root, "world_route_data/descriptors.bin", "af2fed8cc1f25060ce9334f7a45584eb6c44288b6c8b28414ff2125444107066", rolo::world_route_data::descriptors);
    load_streams(root, "world_route_data/streams.bin", "d21a6dbeca62237a34b239ea79ab83d2591ba70af143f725a0e77cb8026b686b", rolo::world_route_data::streams);
    load_tracks(root, "world_tile_animation_data/tracks.bin", "0b7999eba5768e685219760e10b932a55a632041136520a5fe4ba2f328071455", rolo::world_tile_animation_data::tracks);
    load_macros(root, "all_native_level_data/bank1_macros.bin", "40ed35c2f4435680bd031d9f2fd0d222689eb4638b0e039b9ae4e28e778c8421", rolo::all_native_level_data::bank1_macros, rolo::all_native_level_data::bank1_tiles);
    load_macros(root, "all_native_level_data/bank2_macros.bin", "175e343439347ed0018c257eda00736f22fe247cd0d29e1e944e14f20216f3d5", rolo::all_native_level_data::bank2_macros, rolo::all_native_level_data::bank2_tiles);
    load_macros(root, "all_native_level_data/bank3_macros.bin", "bdeaa5b2eaba82ed22615edb602e3b3ec1919d1d84a8b55d15091a6a09b41990", rolo::all_native_level_data::bank3_macros, rolo::all_native_level_data::bank3_tiles);
    load_macros(root, "all_native_level_data/bank4_macros.bin", "bc60fc2b101f7dce338c76fc9f389616dcb53b12558e50d32c8149f6a69b1cd7", rolo::all_native_level_data::bank4_macros, rolo::all_native_level_data::bank4_tiles);
    load_macros(root, "all_native_level_data/bank5_macros.bin", "dce6ccb4658c263f108918334b3cea42fc2c7ff5bf3368904fac32ac290aa990", rolo::all_native_level_data::bank5_macros, rolo::all_native_level_data::bank5_tiles);
    load_macros(root, "all_native_level_data/bank6_macros.bin", "7dc962dc18122a6c903e93323fe48cd94871ce23471ef19ca1189090be003e96", rolo::all_native_level_data::bank6_macros, rolo::all_native_level_data::bank6_tiles);
    load_macros(root, "all_native_level_data/bank7_macros.bin", "efa068442829e113d57ff87f0861b60aa9f41262809f6214e713af8161d91ffb", rolo::all_native_level_data::bank7_macros, rolo::all_native_level_data::bank7_tiles);
    load_frames(root, "actor_pattern_data/frames.bin", "824d27f1705dd39578417d312b4f30abf7992836ae05ae6f7fb375b2ecae3074", rolo::actor_pattern_data::frames);
    load_sprites(root, "opening_data/sprites.bin", "5ea8a1007262877cbddd61628695e3594379f9806a414c38538241212b8bb4e9", rolo::opening_data::sprites);
    load_macros(root, "level1_terrain_data/macros.bin", "40ed35c2f4435680bd031d9f2fd0d222689eb4638b0e039b9ae4e28e778c8421", rolo::level1_terrain_data::macros, rolo::level1_terrain_data::macro_tiles);
    load_macros(root, "level2_terrain_data/macros.bin", "40ed35c2f4435680bd031d9f2fd0d222689eb4638b0e039b9ae4e28e778c8421", rolo::level2_terrain_data::macros, rolo::level2_terrain_data::macro_tiles);
    load_macros(root, "level3_terrain_data/macros.bin", "40ed35c2f4435680bd031d9f2fd0d222689eb4638b0e039b9ae4e28e778c8421", rolo::level3_terrain_data::macros, rolo::level3_terrain_data::macro_tiles);
    load_macros(root, "level4_terrain_data/macros.bin", "40ed35c2f4435680bd031d9f2fd0d222689eb4638b0e039b9ae4e28e778c8421", rolo::level4_terrain_data::macros, rolo::level4_terrain_data::macro_tiles);
    load_macros(root, "level8_terrain_data/macros.bin", "40ed35c2f4435680bd031d9f2fd0d222689eb4638b0e039b9ae4e28e778c8421", rolo::level8_terrain_data::macros, rolo::level8_terrain_data::macro_tiles);
    for(std::size_t i=0;i<3;++i) rolo::first_enemy_definition_data::allocations[i]=rolo::first_enemy_definition_data::definitions[i].allocation();
    if(!(level1_terrain_data::macro_tiles==level2_terrain_data::macro_tiles)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::quad_words==level2_terrain_data::quad_words)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::bank_patterns==level2_terrain_data::bank_patterns)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::background_map_bytes==level2_terrain_data::background_map_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::macro_tiles==level3_terrain_data::macro_tiles)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::quad_words==level3_terrain_data::quad_words)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::bank_patterns==level3_terrain_data::bank_patterns)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::background_map_bytes==level3_terrain_data::background_map_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::macro_tiles==level4_terrain_data::macro_tiles)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::quad_words==level4_terrain_data::quad_words)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::bank_patterns==level4_terrain_data::bank_patterns)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::background_map_bytes==level4_terrain_data::background_map_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::macro_tiles==level8_terrain_data::macro_tiles)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::quad_words==level8_terrain_data::quad_words)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::bank_patterns==level8_terrain_data::bank_patterns)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::background_map_bytes==level8_terrain_data::background_map_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::post_motion_table_bytes==level2_terrain_data::post_motion_table_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::post_motion_table_bytes==level3_terrain_data::post_motion_table_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::post_motion_table_bytes==level4_terrain_data::post_motion_table_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    if(!(level1_terrain_data::post_motion_table_bytes==level8_terrain_data::post_motion_table_bytes)) throw std::runtime_error("Shared terrain resource mismatch");
    load_numeric(root, "direct_runtime_tables/actor_bounce_motion/bounce_direction_bytes.bin", "4fe9f9290e0d4a6d6dcbceaf8e199e12c74d714ba31cc186eef9a4373bfebcbe", rolo::bounce_direction_bytes);
    load_numeric(root, "direct_runtime_tables/actor_choreography_chain/choreography_offsets.bin", "2120625b2560df6c4270e675e5197a697019788a482f7642afe5e48b6c8fcdd0", rolo::choreography_offsets);
    load_numeric(root, "direct_runtime_tables/actor_contact_family/actor_contact_speeds.bin", "e3e9a9ba8cbd2ff02455cc2212354072029f770f3b75f8ce3eaace1596b09313", rolo::actor_contact_speeds);
    load_numeric(root, "direct_runtime_tables/actor_contact_family/actor_contact_thresholds.bin", "2646b483c4e2b05c21957bdd48114893edc8209fb22a21aeb2ab4772d978b4c1", rolo::actor_contact_thresholds);
    load_numeric(root, "direct_runtime_tables/actor_contact_family/actor_contact_y_offsets.bin", "87628fa94daf5c08e3b08bfec2dd0df37cbccac1f035ca47d30919d26cb1aebe", rolo::actor_contact_y_offsets);
    load_numeric(root, "direct_runtime_tables/actor_graphic_phase_data/anchors.bin", "4d4e43a24c0985f5db2b6a8f26aea46bbad44e1d4590b945378d07649c5729aa", rolo::graphic_phase_data::anchors);
    load_numeric(root, "direct_runtime_tables/actor_graphic_phase_data/projectiles.bin", "05230b16246fd6b14e1880210707a3f370b659e2e5132303adce03bd40181f7f", rolo::graphic_phase_data::projectiles);
    load_numeric(root, "direct_runtime_tables/actor_phase_cycle/actor_phase_cycle_delays.bin", "9dcddd12ac0a43ae5048c9453cc6c443e07fe4ff8f1ab9961b8cdd0a6a5c1389", rolo::actor_phase_cycle_delays);
    load_numeric(root, "direct_runtime_tables/actor_phase_emitter_data/emit.bin", "f941bd70c62f64ffe1cc40c1f6e90fde5213b292daa3b3b5621f1e3176ea0a9e", rolo::phase_emitter_data::emit);
    load_numeric(root, "direct_runtime_tables/actor_phase_emitter_data/jump.bin", "c177ac6afb3991663c6af3a35a88e2376db2cbebaf7950868fca525268d5810b", rolo::phase_emitter_data::jump);
    load_numeric(root, "direct_runtime_tables/actor_probe_patrol/actor_probe_patrol_steps.bin", "515e51c37635f7779f46be4c3ba02a0285610b09fec88492c53e0ceb180e6ec5", rolo::actor_probe_patrol_steps);
    load_numeric(root, "direct_runtime_tables/camera_data/modes.bin", "608128748ff31d1b85e32b00bd39101eb255547c1adff67a8fd11b28a62e29be", rolo::camera_data::modes);
    load_numeric(root, "direct_runtime_tables/camera_data/sine.bin", "0e5e15faf1a892aea595c6a37b62a4b38064ad64f74f1d8a2f153de450aba806", rolo::camera_data::sine);
    load_numeric(root, "direct_runtime_tables/ending_data/bad_palette.bin", "bb575b83cd3ede049bfbc5fd16f529dfc646edcb7b5ace937dc7d9bb87c51ded", rolo::ending_data::bad_palette);
    load_numeric(root, "direct_runtime_tables/ending_data/bad_text.bin", "56d0e1078c2a95d08927284eea87beec99ca8661ad2a4cd994962a68776af65f", rolo::ending_data::bad_text);
    load_numeric(root, "direct_runtime_tables/ending_data/good_text.bin", "0623e0df9530b70e9913a70d7bbcd121b7ccbe7496d1e93db915499fd8e0a5ff", rolo::ending_data::good_text);
    load_numeric(root, "direct_runtime_tables/ending_data/white.bin", "c406d951f1a23ba02864c2168d6be964a7500f280f3861406a4fcb4d82c84c6e", rolo::ending_data::white);
    load_numeric(root, "direct_runtime_tables/player_terrain_response/player_terrain_bob.bin", "f16f6b7f1cd082e72284f88f0b05969cfa0431be25a05508e66cf60b3ea2cf63", rolo::player_terrain_bob);
    load_numeric(root, "direct_runtime_tables/score_decimal/score_decimal_divisors.bin", "652ca39e9310e001c2c4af271610032a5638c58598f727066ccf4e666d424cd4", rolo::score_decimal_divisors);
    load_numeric(root, "direct_runtime_tables/startup_logo_raster/caps.bin", "47b27af1478461bb204a61b5c2fe00044024b3396a73d97566c515739d1690aa", rolo::startup_logo_raster_data::caps);
    load_numeric(root, "direct_runtime_tables/startup_logo_raster/heights.bin", "310d320087f61d8da1012242cdc288e70ebc81d9a643ab16a35d66a0de52c86c", rolo::startup_logo_raster_data::heights);
    load_numeric(root, "direct_runtime_tables/startup_logo_raster/slopes.bin", "0ed1ad26b8f2107c08cfa7b44a40d15b3f50a836f7b2dd4072e9d73bfbea3779", rolo::startup_logo_raster_data::slopes);
    load_numeric(root, "direct_runtime_tables/status_hud_templates/status_hud_templates.bin", "46494a02801825f2a06b5d9028dc0a7d0aa3b52b62953ff33499b199269e90ed", rolo::status_hud_templates);
    load_numeric(root, "direct_runtime_tables/timed_projectile_phases/timed_projectile_wave.bin", "e2c1fab77cf1cbebbc02d27edd963d78de586ead92ac501af9ad75da4ecc4544", rolo::timed_projectile_wave);
    load_numeric(root, "direct_runtime_tables/world_map/world_map_absent_edges.bin", "54525cf242b94ee056c010fc32a0ee6c9b49f91a960d51ccfea24823fd66aaed", rolo::world_map_absent_edges);
    load_numeric(root, "direct_runtime_tables/world_map/world_map_missing_next_to_present.bin", "c7ab17b4da1526f7ffc68dda77bf678fecf7ec2840bb03dcba55f75949f066c0", rolo::world_map_missing_next_to_present);
    load_numeric(root, "direct_runtime_tables/world_map/world_map_present_next_to_missing.bin", "7456e0710a6b9d228a724e3108b3497b54da816239ee0584e016d672f4cb15e3", rolo::world_map_present_next_to_missing);
}
}
