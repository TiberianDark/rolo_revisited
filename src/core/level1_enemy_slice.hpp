#include "core/achievement_regions.hpp"
#include "core/achievement_attempt.hpp"
#include "core/companion_census.hpp"
#pragma once
#include "core/shared_player_frame.hpp"
#include "core/actor_bounce_motion.hpp"
#include "core/first_enemy_world.hpp"
#include "core/first_enemy_animation_data.hpp"
#include "core/first_enemy_definition_data.hpp"
#include "core/level1_player_animation_data.hpp"
#include "core/level1_world_data.hpp"
#include "core/player_data.hpp"
#include "core/player_input.hpp"
#include "core/player_frame_history.hpp"
#include "core/player_terrain_response.hpp"
#include "core/graphics_pool.hpp"
#include "core/terrain_camera_world.hpp"
#include "core/level1_terrain_patterns.hpp"
#include "core/native_level_assets.hpp"
#include "core/level2_actor_updates.hpp"
#include "core/forest_tile_animation.hpp"
#include "core/desert_tile_animation.hpp"
#include "core/cavern_tile_animation.hpp"
#include "core/suction_particles.hpp"
#include "core/actor_animation_list.hpp"
#include "core/actor_sprite.hpp"
#include "core/score_effect.hpp"
#include "core/actor_spawn_factory.hpp"
#include "core/player_contact_resolution.hpp"
#include "core/score_award.hpp"
#include "core/camera.hpp"
#include "core/level1_collectibles.hpp"
#include "core/level1_object_data.hpp"
#include "core/level1_object_animation_data.hpp"
#include "core/level1_startup.hpp"
#include "core/level1_key_actor.hpp"
#include "core/powerup_pickups.hpp"
#include "core/actor_common_callbacks.hpp"
#include "core/actor_direct_contact.hpp"
#include "core/actor_phase_cycle.hpp"
#include "core/actor_offscreen_retirement.hpp"
#include "core/actor_pursuit_family.hpp"
#include "core/actor_orbit_leap.hpp"
#include "core/actor_vertical_direction.hpp"
#include "core/animation_spawn_entries.hpp"
#include "core/actor_remaining_motion.hpp"
#include "core/actor_rescue_presentation.hpp"
#include "core/palette_entry_contracts.hpp"
#include "core/timed_projectile_phases.hpp"
#include "core/actor_injury_dispatch.hpp"
#include "core/actor_facing_emitter.hpp"
#include "core/actor_capture_phases.hpp"
#include "core/actor_graphic_phases.hpp"
#include "core/actor_corner_motion.hpp"
#include "core/actor_anchor_follow.hpp"
#include "core/linked_actor_families.hpp"
#include "core/player_trigger_capture.hpp"
#include "core/choreography_binding.hpp"
#include "core/actor_phase_mechanism.hpp"
#include "core/enemy_phase_entries.hpp"
#include "core/palette_flash.hpp"
#include "core/level1_progress.hpp"
#include "core/level1_companion_motion.hpp"
#include "core/actor_horizontal_collision.hpp"
#include "core/level1_hud.hpp"
#include "core/animation_object_spawning.hpp"
#include "core/level1_status_hud.hpp"
#include "core/level1_completion.hpp"
#include "core/level1_companion_selection.hpp"
#include "core/level1_companion_presentation.hpp"
#include "core/player_post_motion.hpp"
#include "core/platform_surface.hpp"
#include "core/actor_rider_platforms.hpp"
#include "core/actor_triggered_platforms.hpp"
#include "core/actor_platform_dispatch.hpp"
#include "core/actor_direction_result.hpp"
#include "core/dynamic_platform_data.hpp"
#include <vector>
#include <cstdio>
#include <string>
namespace rolo {
struct Level1TransportHooks {
    virtual ~Level1TransportHooks()=default;
    virtual bool transport_marker(const TerrainDescriptorRecord&)=0;
    virtual bool resume_transport_frame(std::uint8_t pressed)=0;
    virtual bool scan_transport_triggers()=0;
    virtual void transport_frame_returned()=0;
};
// An explicitly bounded interactive integration slice. Unbound level objects,
// triggers, full frame prefix/suffix and hardware queue timing are NOT simulated.
// Their encountered MAP records are retained for tracing, not discarded as done.
struct Level1EnemySlice final:ActorAllocationServices,PlayerLifecycleServices,
    PlayerPresentationServices,ActorCallbackServices,ActorAnimationSound,ScoreEffectServices,PlayerContactResolutionServices,Level1CollectibleServices,Level1CompanionServices,CompanionControlServices {
    static std::array<ActorDefinition,194> definitions;
    static bool definitions_ready;
    const NativeLevelAssets level_assets;
    ActorPool pool;GraphicsPool graphics;ActorReservationPool reservations;
    PlayerMovementState movement;PlayerInputPhaseState input;HeldObjectState held;
    PlayerInputMapping buttons;PlayerPresentationState presentation;
    std::array<std::uint8_t,16384> backing{};
    ActorTerrain terrain{backing,level_assets.terrain_bank().collision,player_data::shapes,0};
    std::uint16_t width=level_assets.width,sound{},frame{},previous_shift{};
    std::uint8_t slope{},f2bc{},surface_gate{},effect{},animation_gate{};
    std::array<std::uint8_t,16> actor_type_gates{}; // C5A8, distinct from world progress C558.
    std::uint8_t visited_c553{},platform_gate_f281{},platform_gate_f282{},spawner_landed_c5ce{};
    std::uint8_t linked_rescue_c5b6{},special_spawn_gate_c5cc{},capture_c521{};std::uint16_t capture_c526{};
    ActorPhaseGlobals phase_boss;
    std::uint8_t pursuit_sound_timer_f2b4{};
    LinkedActorGlobals ride_state{};ActorCaptureGlobals lift_state{};std::uint8_t lift_reload{},boss_scene_f283{};
    std::uint16_t flash_timer{};std::array<std::uint8_t,4> flash_gates{};
    bool death_requested{},game_over_requested{};std::uint32_t score{};
    ScoreAwardState awards;PlayerBlinkState blink;
    std::uint8_t exit_latch{},protection{},transition{};
    std::array<std::uint32_t,3> companions{};
    std::array<std::uint8_t,48> platform_definition_flags{};
    std::array<std::uint32_t,9> choreography_roster{};
    std::uint32_t enemy_key{},score_followup{};
    CameraState camera;
    Level1TransportHooks* transport_hooks{};
    std::array<std::uint16_t,64> palette=level1_terrain_data::palette_words;
    PlayerCheckpoint checkpoint;
    Level1ProgressState progress;
    AchievementBits achievement_events{};AchievementAttempt achievement_attempt{};CompanionAchievementAttempt achievement_companion{};bool achievement_completion_recorded{},achievement_debug_used{};std::array<std::uint8_t,80> achievement_previous_flags{};bool achievement_vacuum_obtained{};
    AchievementBits take_achievement_events(){const auto events=achievement_events;achievement_events=0;return events;}
    Level1CompanionState companion_state;
    std::uint32_t requested_state{};std::uint16_t next_level_selector{};std::uint8_t next_entry_selector{},level_transition_latch{};
    std::uint16_t target_x_c494{},target_y_c498{};
    std::uint16_t music_command{},music_argument{},hud_remaining{};
    Level1Hud hud;
    Level1StatusHud status_hud;
    Level1Completion completion;
    CompanionControlState control;
    CameraInput camera_input(){
        const auto& actor=pool.resolve(movement.controlled);
        return {actor.word(12),actor.word(16),actor.word(20),width,level_assets.height,
            movement.contact.hit_gate_c519!=0,movement.contact.hit_gate_c51a!=0,camera_data::modes[level_assets.selector],terrain.x_shift,frame};
    }
    PlayerFrameHistory history;ImmutablePlayerHistorySelector selectors{level1_terrain_data::history_selector_bytes};
    AnimationRandom random{3}; // $523E initializes shared C4BE.
    TerrainPatternStorage patterns;TerrainQuadMapping mapping{1};
    ForestTileAnimation tile_animation;
    DesertTileAnimation desert_tile_animation;
    CavernTileAnimation cavern_tile_animation;
    SuctionParticles suction_particles;
    TerrainMappedDisplay display{mapping};ActorState plane;TerrainCameraGlobals terrain_globals;
    std::array<std::uint8_t,8192> background_backing{};
    std::vector<std::uint8_t> background_map_storage=std::vector<std::uint8_t>(level_assets.background.size()+4);
    TerrainMappedDisplay background_display{mapping};ActorState background_plane;
    std::vector<TerrainDescriptorRecord> pending_markers;
    struct SpawnEvent {std::uint32_t marker,actor;std::uint16_t type,x,y;std::uint8_t facing;};
    std::vector<SpawnEvent> spawn_events;
    static constexpr std::uint32_t map_identity=0xffffcc44;
    // Search performs a terminal read before checking end. These four guard
    // bytes are never dispatched; original adjacent RAM bytes remain unproven.
    std::vector<std::uint8_t> map_storage=std::vector<std::uint8_t>(level_assets.map.size()+4);
    struct Macros final:TerrainDescriptorServices {
        Level1EnemySlice& world;explicit Macros(Level1EnemySlice& w):world(w){}
        TerrainMacroDefinition terrain_macro(std::uint8_t i)override{const auto m=world.level_assets.terrain_bank().macros;if(i>=m.size())throw std::out_of_range("Level macro bank extent");return m[i];}
        std::uint16_t terrain_macro_byte_count(std::uint8_t i)override{const auto m=terrain_macro(i);return static_cast<std::uint16_t>(m.width*m.height*2);}
        void terrain_special_descriptor(const TerrainDescriptorRecord& r,std::uint16_t)override{
            if(r.type>=0x2000&&r.type<0x4000&&((r.type>>8)>=32&&(r.type>>8)<=54)){world.spawn_log_platform(r);return;}
            if((r.type>>8)==0x17)return; // Every consumed-marker variant is class23 literalRTS.
            if(world.transport_hooks&&world.transport_hooks->transport_marker(r))return;
            if((r.type>>8)==4){
                const auto index=(r.type&0xfe)/2;
                if(index<level1_object_data::enemy_spawn_table.size()){
                    const auto key=level1_object_data::enemy_spawn_table[index];
                    if(std::any_of(definitions.begin(),definitions.end(),[&](const auto& d){return d.key==key;})){world.spawn_marker(r);return;}
                }
            }
            if((r.type>>8)==6||(r.type>>8)==0x12||(r.type>>8)==0x0b){world.spawn_marker(r);return;}
            if((r.type>>8)==13){
                if(!world.special_spawn_gate_c5cc&&world.visited_c553&&static_cast<std::int8_t>(world.progress.spawn_selector)<0)return;
                world.spawn_marker(r);return;
            }
            if((r.type>>8)==5){
                const auto index=(r.type&0xfe)/2;
                if(index<level1_object_data::generic_spawn_table.size()){
                    const auto key=level1_object_data::generic_spawn_table[index];
                    if(std::any_of(definitions.begin(),definitions.end(),[&](const auto& d){return d.key==key;})){world.spawn_marker(r);return;}
                }
            }
            if(std::none_of(world.pending_markers.begin(),world.pending_markers.end(),[&](const auto& old){return old.record_offset==r.record_offset;}))world.pending_markers.push_back(r);
        }
    } macros{*this};
    TerrainStreamingCameraServices streaming{backing,{map_storage},macros,display,true};
    struct BackgroundMacros final:TerrainDescriptorServices {
        Level1EnemySlice& world;explicit BackgroundMacros(Level1EnemySlice& w):world(w){}
        TerrainMacroDefinition terrain_macro(std::uint8_t i)override{const auto m=world.level_assets.terrain_bank().macros;if(i>=m.size())throw std::out_of_range("Level macro bank extent");return m[i];}
        std::uint16_t terrain_macro_byte_count(std::uint8_t i)override{const auto m=terrain_macro(i);return static_cast<std::uint16_t>(m.width*m.height*2);}
        void terrain_special_descriptor(const TerrainDescriptorRecord&,std::uint16_t)override{throw std::logic_error("Unexpected Level1 background actor marker");}
    } background_macros{*this};
    TerrainStreamingCameraServices background_streaming{background_backing,{background_map_storage},background_macros,background_display,false};
    PlayerActorWorld player{pool,reservations,movement,input,held,definitions,*this,sound,*this};
    struct AchievementEnemyWorld final:FirstEnemyAllocatedWorld {
        AchievementBits& events;
        AchievementEnemyWorld(ActorPool&p,ActorReservationPool&r,ContactGlobals&g,std::uint32_t&c,const ActorTerrain&t,std::uint16_t&width,std::span<const ActorDefinition>d,ActorAllocationServices&a,std::uint16_t&sound,AchievementBits&e):FirstEnemyAllocatedWorld(p,r,g,c,t,width,d,a,sound),events(e){}
        void defeat_contact_body(ActorState& actor)override{
            const auto previous=actor.longword(42);const auto hit=actor.word(74);const auto d=definition(actor);
            const bool water=hit&&pool.resolve(0xffff0000u|hit).longword(4)==0x140ca;
            FirstEnemyAllocatedWorld::defeat_contact_body(actor);
            if(water&&d.longword(22)==0&&d.word(32)&&previous!=inactive_actor_callback)events|=achievement_bit(48);
        }
    } enemy{pool,reservations,movement.contact,movement.controlled,terrain,width,definitions,*this,sound,achievement_events};
    struct KeyServices final:Level1KeyActorServices {
        Level1EnemySlice& w;explicit KeyServices(Level1EnemySlice& world):w(world){}
        ActorState* linked_actor(const ActorState& a)override{return w.enemy.linked_actor(a);}
        ActorState& controlled_actor()override{return w.enemy.controlled_actor();}
        void object_contact(ActorState& a)override{w.enemy.object_contact(a);}
        bool player_contact(ActorState& a)override{return w.enemy.player_contact(a);}
        void player_damage(ActorState& a)override{w.enemy.player_damage(a);}
        void land(ActorState& a)override{w.enemy.land(a);}
        void choose_direction(ActorState& a)override{w.enemy.choose_direction(a);}
        void key_actor_sound(std::uint16_t value)override{w.sound=value;}
        std::uint16_t reward_camera_x()override{return w.reward_camera_x();}
        std::uint16_t reward_camera_y()override{return w.reward_camera_y();}
        void increment_reward_byte(std::uint32_t address)override{w.increment_reward_byte(address);}
    } key_services{*this};
    struct SharedEnemyServices final:ActorPursuitServices {
        Level1EnemySlice& w;explicit SharedEnemyServices(Level1EnemySlice& v):w(v){}
        ActorState* linked_actor(const ActorState& a)override{return w.enemy.linked_actor(a);}
        ActorState& controlled_actor()override{return w.enemy.controlled_actor();}
        void object_contact(ActorState& a)override{w.enemy.object_contact(a);}
        bool player_contact(ActorState& a)override{return w.enemy.player_contact(a);}
        void player_damage(ActorState& a)override{w.enemy.player_damage(a);}
        void land(ActorState& a)override{w.enemy.land(a);}
        void choose_direction(ActorState& a)override{w.enemy.choose_direction(a);}
        bool select_vertical_direction(ActorState& a)override{return actor_select_vertical_direction(a,w.enemy,w.target_x_c494);}
        void hurt_controlled_actor(ActorState& a)override{(void)actor_direct_player_contact(a,w.enemy.controlled_actor(),w.movement.contact,w.enemy);}
    } shared_enemy{*this};
    struct ProbeServices final:ActorFacingEmitterServices {
        Level1EnemySlice& w;explicit ProbeServices(Level1EnemySlice& v):w(v){}
        ActorState* allocate(ActorState*&live,std::uint32_t d,std::uint32_t resource,std::uint32_t x,std::uint32_t y,std::uint8_t facing,std::uint8_t marker)override{
            const auto r=allocate_actor_chain(w.pool,{d,x,y,marker,resource,facing},w);if(r.tail)live=&w.pool.resolve(r.tail);return r.success?&w.pool.resolve(r.head):nullptr;
        }
        void object_contact(ActorState*& a)override{w.enemy.object_contact(*a);}
        bool player_contact(ActorState*& a)override{return w.enemy.player_contact(*a);}
        void damage(ActorState*& a)override{w.enemy.player_damage(*a);}
        void hurt(ActorState*& a)override{w.shared_enemy.hurt_controlled_actor(*a);}
        bool terrain(std::uint16_t x,std::uint16_t y)override{return player_wall_probe(w.terrain,x,y,true).found;}
        void vertical_direction(ActorState*& a)override{(void)actor_select_vertical_direction(*a,w.enemy,w.target_x_c494);}
        void horizontal_direction(ActorState*& a)override{w.enemy.choose_direction(*a);}
        ActorState& controlled()override{return w.enemy.controlled_actor();}
        ActorState& linked(std::uint32_t key)override{return w.pool.resolve(key);}
        void gravity(ActorState*& a)override{actor_gravity(*a);}
        void integrate(ActorState*& a)override{actor_integrate(*a);}
        void land(ActorState*& a)override{w.enemy.land(*a);}
    } probes{*this};
    struct RemainingServices final:RemainingActorServices {
        Level1EnemySlice& w;explicit RemainingServices(Level1EnemySlice& v):w(v){}
        void sound(std::uint16_t value,ActorState*&,PhaseEmitterContext&)override{w.sound=value;}
        ActorState* allocate(ActorState*& live,PhaseEmitterContext& c,const PhaseEmitterRequest& r)override{
            const auto result=allocate_actor_chain(w.pool,{r.definition,r.x,r.y,r.marker,r.resource,r.facing},w);
            c.resource=result.resource_context;if(result.tail)live=&w.pool.resolve(result.tail);
            return result.success?&w.pool.resolve(result.head):nullptr;
        }
        void object(ActorState*& a)override{w.enemy.object_contact(*a);}
        bool contact(ActorState*& a)override{return w.enemy.player_contact(*a);}
        void damage(ActorState*& a)override{w.enemy.player_damage(*a);}
        void hurt(ActorState*& a)override{w.shared_enemy.hurt_controlled_actor(*a);}
        ActorState& controlled()override{return w.enemy.controlled_actor();}
        ActorState& parent(std::uint32_t key)override{return w.pool.resolve(key);}
        void direction(ActorState*& a,PhaseEmitterContext&)override{w.enemy.choose_direction(*a);}
        void land(ActorState*& a)override{w.enemy.land(*a);}
        void horizontal(ActorState*& a)override{actor_horizontal_collision(*a,w.terrain);}
        void trunk(ActorState*& a,PhaseEmitterContext&)override{update_trunk_pull(ActorPool::key(a-w.pool.actors.data()),w);}
        void phase_target(ActorState*& a,std::uint32_t target)override{update_timed_projectile_phase(*a,target,w);}
    } remaining{*this};
    struct LinkedServices final:LinkedActorServices,ActorAnchorServices,PlayerAccelerationServices {
        Level1EnemySlice&w;explicit LinkedServices(Level1EnemySlice&v):w(v){}
        void sound(std::uint16_t v,ActorState*&a,PhaseEmitterContext&c)override{w.remaining.sound(v,a,c);}
        ActorState* allocate(ActorState*&a,PhaseEmitterContext&c,const PhaseEmitterRequest&r)override{return w.remaining.allocate(a,c,r);}
        void object(ActorState*&a)override{w.remaining.object(a);}
        bool contact(ActorState*&a)override{return w.remaining.contact(a);}
        void damage(ActorState*&a)override{w.remaining.damage(a);}
        void hurt(ActorState*&a)override{w.remaining.hurt(a);}
        ActorState& controlled()override{return w.remaining.controlled();}
        ActorState& parent(std::uint32_t k)override{return w.pool.resolve(k);}
        ActorState& linked(std::uint32_t k)override{return w.pool.resolve(k);}
        void direction(ActorState*&a,PhaseEmitterContext&c)override{w.remaining.direction(a,c);}
        void land(ActorState*&a)override{w.enemy.land(*a);}
        void land(ActorState&a)override{w.enemy.land(a);}
        void horizontal(ActorState*&a)override{w.remaining.horizontal(a);}
        void trunk(ActorState*&a,PhaseEmitterContext&c)override{w.remaining.trunk(a,c);}
        void phase_target(ActorState*&a,std::uint32_t t)override{w.remaining.phase_target(a,t);}
        std::uint8_t contact_mask(ActorState*&a)override{return w.enemy.player_contact(*a)?255:0;}
        void corner(ActorState*&a,ActorState&head,unsigned slot)override{update_actor_corner_motion(*a,head,w.terrain,slot>=2,slot==1||slot==3);}
        bool ride_query(ActorState*&a)override{
            const auto x=std::uint16_t(a->word(12)+half_signed_word(a->word(36))+8);
            const auto y=std::uint16_t(a->word(16)-half_signed_word(a->word(38))+a->word(34));
            const auto tile=actor_terrain_word(w.terrain,x,y);
            if(!(tile&0x2000)&&(tile&0xe00)==0xe00)return true;
            if(tile&0x4000){const auto at=(tile&511u)*8+4;return (w.terrain.read(w.terrain.collision,at+1)&63)!=0;}
            return false;
        }
        void mount(ActorState*&a,LinkedActorGlobals&g)override{
            if(ride_query(a))return;const auto&c=controlled();if((c.byte(122)&128)||!(c.byte(124)&16))return;
            if(!w.progress_exit_contact(*a,32,16))return;g.contains=255;a->byte(50,255);w.movement.contact.action_gate_c511=0;
        }
        PlayerSlopeMotion slope_motion(std::uint8_t slot,bool reverse)override{const auto&t=reverse?level1_object_data::ride_slope_reverse:level1_object_data::ride_slope_forward;return {t[slot*2],t[slot*2+1]};}
        void ride_input(RideInputStep step,ActorState*&a,LinkedActorGlobals&g)override{
            switch(step){
            case RideInputStep::Friction:player_horizontal_drag(*a,g.drive);w.movement.drag=g.drive;break;
            case RideInputStep::Horizontal:player_acceleration(*a,*this);break;
            case RideInputStep::Acceleration:player_slope_vertical_motion(*a,w.movement.c514);break;
            case RideInputStep::Jump:update_player_jump(*a,{w.buttons.mapped[6],w.buttons.physical[6],w.movement.c514,w.movement.controlled_type},w.player);break;
            }
        }
        ActorAnchorFloor floor(std::uint16_t x,std::uint16_t y)override{auto f=actor_floor_probe(w.terrain,x,y);return {std::uint16_t(f.found?0:0xffff),f.y};}
        void probe_child(ActorState*&a,ActorState&root,bool second,LinkedActorGlobals&g)override{
            ActorAnchorPair pair{g.anchor_x1,g.support1,g.anchor_x2,g.support2};
            if(second)update_actor_second_anchor(*a,root,pair,*this);else update_actor_first_anchor(*a,root,pair,*this);
            g.anchor_x1=pair.first_x;g.anchor_y1=pair.first_y;g.support1=pair.first_y;g.anchor_x2=pair.second_x;g.anchor_y2=pair.second_y;g.support2=pair.second_y;
        }
        void chain_flag(ActorState&a,bool hidden,LinkedActorGlobals&)override{const auto key=ActorPool::key(&a-w.pool.actors.data());if(hidden)actor_chain_flag<ActorChainFlag::set>(w.pool,key);else actor_chain_flag<ActorChainFlag::clear>(w.pool,key);}
    } linked_services{*this};
    struct BossServices final:ActorInjuryServices,EnemyPhaseServices,PaletteFlashServices {
        Level1EnemySlice& w;explicit BossServices(Level1EnemySlice& v):w(v){}
        bool contact(ActorState*& a)override{return w.enemy.player_contact(*a);}
        bool damage_negative(ActorState*& a)override{return actor_player_damage(*a,w.enemy.controlled_actor(),w.movement.contact,w.enemy)<0;}
        std::uint32_t spawn(std::uint32_t d,std::uint32_t x,std::uint32_t y)override{const auto r=allocate_actor_chain(w.pool,{d,x,y,0,0,0},w);return r.success?r.head:0;}
        void reveal(ActorState*& live)override{
            if(w.progress.selector==29){w.achievement_events|=1u<<7;w.achievement_events|=achievement_bit(26);w.achievement_events|=w.achievement_attempt.boss(30);}
            if(w.progress.selector==33){w.achievement_events|=1u<<15;w.achievement_events|=achievement_bit(27);w.achievement_events|=w.achievement_attempt.boss(31);}
            const auto n=static_cast<std::int8_t>(w.progress.spawn_selector);const unsigned index=n<0?unsigned(-int(n)):unsigned(n);
            if(index>=w.progress.flags.size())throw std::out_of_range("Boss reward index");
            auto& flag=w.progress.flags[index];const bool already=flag&1;flag|=1;if(already)return;
            const auto& c=w.enemy.controlled_actor();const auto r=allocate_actor_chain(w.pool,{0x14482,c.longword(12),c.longword(16),0,0,0},w);
            if(r.tail)live=&w.pool.resolve(r.tail);if(!r.success)return;live=&w.pool.resolve(r.head);live->word(70,4);start_reward_curve(*live,296,41,0xffffc551,w);
        }
        void spawn_scene(ActorState*& live,std::uint32_t d,std::uint32_t x,std::uint32_t y,std::uint32_t context,std::uint8_t marker,std::uint8_t facing)override{
            const auto r=allocate_actor_chain(w.pool,{d,x,y,marker,context,facing},w);if(r.tail)live=&w.pool.resolve(r.tail);
        }
        void phase(ActorState*& a,std::uint32_t target)override{
            switch(target){
            case 0xea98:enemy_spawn_burst(w.pool,ActorPool::key(a-w.pool.actors.data()),*this);break;
            case 0xeb1a:enemy_burst_pause(*a,w.frame,w.sound);break;
            case 0xeb4a:enemy_burst_blink(*a,w.sound);break;
            case 0xeb9e:enemy_burst_end(*a,w.sound);break;
            case 0xebc8:update_actor_long_pause(*a);break;
            case 0xed72:actor_short_phase_wait(*a);break;
            case 0xed90:{PhaseEmitterContext c{};update_actor_phase_jump(a,c,w.remaining);break;}
            case 0xee18:{PhaseEmitterContext c{};update_actor_phase_emission(a,c,w.remaining);break;}
            case 0xf060:capture_descend(w.pool,ActorPool::key(a-w.pool.actors.data()),w.lift_state);break;
            case 0xf0e2:capture_open(w.pool,ActorPool::key(a-w.pool.actors.data()),w.lift_state);break;
            case 0xf12c:capture_launch(w.pool,ActorPool::key(a-w.pool.actors.data()),w.lift_state);break;
            case 0xf1ae:capture_wait(w.pool,ActorPool::key(a-w.pool.actors.data()),w.lift_state);break;
            case 0xf25e:capture_close(w.pool,ActorPool::key(a-w.pool.actors.data()),w.lift_state);break;
            case 0xf2a0:capture_ascend(w.pool,ActorPool::key(a-w.pool.actors.data()),w.lift_state);break;
            default:throw std::out_of_range("Unbound boss phase");}
        }
        void gravity(ActorState*& a)override{actor_gravity(*a);}
        void integrate(ActorState*& a)override{actor_integrate(*a);}
        void land(ActorState*& a)override{w.enemy.land(*a);}
        bool floor_nonnegative(std::uint16_t x,std::uint16_t y)override{return actor_floor_probe(w.terrain,x,y).found;}
        void floor_contact(ActorState& a)override{w.enemy.land(a);}
        void palette_flash_transfer(unsigned bank,bool original,std::uint16_t)override{
            for(unsigned i=0;i<15;++i)w.palette[bank*16+i+1]=original?w.level_assets.target_palette[bank*16+i+1]:level1_object_data::common_flash_palette[i];
        }
    } boss_services{*this};
    struct GraphicServices final:GraphicPhaseServices {
        Level1EnemySlice&w;explicit GraphicServices(Level1EnemySlice&v):w(v){}
        void sound(std::uint16_t v,ActorState*&a,PhaseEmitterContext&c)override{w.remaining.sound(v,a,c);}
        ActorState* allocate(ActorState*&a,PhaseEmitterContext&c,const PhaseEmitterRequest&r)override{return w.remaining.allocate(a,c,r);}
        bool contact(ActorState*&a,PhaseEmitterContext&)override{return w.enemy.player_contact(*a);}
        bool damage_negative(ActorState*&a,PhaseEmitterContext&)override{return w.boss_services.damage_negative(a);}
        void hurt(ActorState*&a,PhaseEmitterContext&)override{w.shared_enemy.hurt_controlled_actor(*a);}
        ActorState& controlled()override{return w.enemy.controlled_actor();}
    } graphic_services{*this};
    struct PhaseBossServices final:ActorPhaseServices {
        Level1EnemySlice&w;explicit PhaseBossServices(Level1EnemySlice&v):w(v){}
        bool object_contact(ActorState*&a)override{return actor_object_contact(*a,w.enemy);}
        ActorState& controlled()override{return w.enemy.controlled_actor();}
        void reveal(ActorState*&a)override{w.boss_services.reveal(a);}
        void spawn_scene(ActorState*&a,std::uint32_t d,std::uint32_t x,std::uint32_t y,std::uint32_t c,std::uint8_t m,std::uint8_t f)override{w.boss_services.spawn_scene(a,d,x,y,c,m,f);}
        void sound(std::uint16_t v)override{w.sound=v;}
        void emit(ActorState*&a)override{
            const auto phase=a->byte(48);if(phase<1||phase>4)throw std::out_of_range("D77C phase");const auto at=(phase-1)*2;
            const auto r=allocate_actor_chain(w.pool,{0x147f6,a->longword(12)+level1_object_data::phase_boss_offsets[at],a->longword(16)+level1_object_data::phase_boss_offsets[at+1],0,0,0},w);
            if(r.success){w.pool.resolve(r.head).byte(48,phase);a->byte(48,0);w.sound=44;}
        }
    } phase_boss_services{*this};
    struct RescueServices final:ActorRescueServices {
        Level1EnemySlice&w;explicit RescueServices(Level1EnemySlice&v):w(v){}
        bool object_contact(ActorState*&a)override{return actor_object_contact(*a,w.enemy);}
        bool player_contact(ActorState*&a)override{return w.enemy.player_contact(*a);}
        void damage(ActorState*&a)override{w.enemy.player_damage(*a);}
        ActorState& linked_word(std::uint16_t key)override{return w.pool.resolve(0xffff0000u|key);}
        bool type_is_56(ActorState&a)override{return w.definition(a.longword(4)).word(10)==56;}
        void replace_type_56(ActorState*&,std::uint32_t callback)override{for(unsigned i=0;i<w.active.count;++i){auto&a=w.pool.resolve(w.active.keys[i]);if(type_is_56(a))a.longword(42,callback);}}
    } rescue_services{*this};
    struct PowerupServices final:PowerupPickupServices {
        Level1EnemySlice& w;explicit PowerupServices(Level1EnemySlice& v):w(v){}
        void powerup_sound(std::uint16_t v)override{w.sound=v;}
        DefeatDefinition defeat_definition(const ActorState& a)override{return w.enemy.defeat_definition(a);}
        void spawn_secondary(std::uint32_t d,std::uint32_t x,std::uint32_t y)override{w.enemy.spawn_secondary(d,x,y);}
        ActorState* next_linked_actor(const ActorState& a)override{return w.enemy.linked_actor(a);}
    } powerups{*this};
    PlayerDefinedTerrainCollisionServices collision{pool,movement.controlled,terrain,slope,definitions};
    ActiveActorList active;ActorScheduleState schedule;
    DeferredMarkerPool deferred;std::uint16_t contact_root_word{};
    struct Lifetime final:ActiveActorServices {
        Level1EnemySlice& w;explicit Lifetime(Level1EnemySlice& world):w(world){}
        void clear_contact_root_word()override{w.contact_root_word=0;}
        void release_completed_actor_reservations()override{w.reservations.release_completed(w.pool);}
        ActorLifetimeDefinition lifetime_definition(const ActorState& a)override{
            const auto& d=w.definition(a.longword(4));const auto flags=dynamic_platform_data::is_definition(d.key)?w.platform_definition_flags.at(&a-w.pool.actors.data()):d.byte(26);return {d.key,d.word(10),d.byte(7),flags};
        }
        std::uint8_t lifetime_progress_flag(std::int16_t index)override{return w.callback_override_flag(index);}
        void release_ram_definition(std::uint32_t key)override{if(dynamic_platform_data::is_definition(key))return;throw std::logic_error("RAM definition lifetime outside slice");}
        std::uint16_t disposal_resource_units(const ActorState& a)override{return w.definition(a.longword(4)).word(4);}
        void release_actor_graphics(std::uint32_t start,std::uint16_t size)override{w.graphics.release(start,size);}
        void restore_marker(std::uint32_t key,std::uint16_t value)override{w.marker_word(key,value);}
    } lifetime{*this};
    std::array<ActorChainDefinition,std::tuple_size_v<decltype(definitions)>> allocations{};
    explicit Level1EnemySlice(const std::array<std::uint8_t,80>* campaign_flags=nullptr,std::uint32_t campaign_score=0,std::uint8_t campaign_lives=3,std::uint16_t selector=1,const PlayerCheckpoint* restart_checkpoint=nullptr,std::uint8_t startup_selector=0,bool lift_entry=false)
        :level_assets(native_level_assets(selector)){
        if(!definitions_ready){
            std::size_t n=0;
            for(const auto& d:level1_world_data::definitions)definitions[n++]=d;
            for(const auto& d:level1_object_data::definitions)definitions[n++]=d;
            definitions[n++]=level1_hud_data::definition;
            for(const auto& d:dynamic_platform_data::definitions)definitions[n++]=d;
            definitions_ready=true;
        }
        progress.selector=selector;achievement_attempt.entry_score=campaign_score;achievement_attempt.eligible=restart_checkpoint==nullptr;
        player.standard_shallow_ground=selector==18;
        std::copy(level_assets.target_palette.begin(),level_assets.target_palette.end(),palette.begin());
        for(unsigned index=2;index<=5;++index)actor_type_gates[index]=255; // $6384.
        if(campaign_flags)progress.flags=*campaign_flags;
        else progress.flags[1]=1; // $6384 initially makes selector1 available.
        progress.spawn_selector=level_assets.reward_selector; // $37EA -> F26F, consumed by $D32A.
        progress.rescued_c552=(progress.flags[progress.selector]&2)?255:0; // $523E samples before the later census.
        visited_c553=(progress.flags[progress.selector]&4)?255:0;progress.flags[progress.selector]|=4; // $523E.
        movement.contact.action_gate_c511=255;
        for(std::size_t i=0;i<allocations.size();++i)allocations[i]=definitions[i].allocation();
        mapping=initialize_native_terrain_patterns(patterns,level_assets);
        pool.initialize_free_stack();graphics.initialize(mapping.next_pattern);reservations.initialize();deferred.initialize();buttons.previous_complement=255;
        movement.controlled_type=4;movement.bounds={width,level_assets.height,0};movement.c51d=campaign_lives;presentation.idle_countdown=250;
        score=awards.total=campaign_score;
        const auto spawn=allocate_actor_chain(pool,{0x13ecc,420u<<16,200u<<16,0,0,0},*this);
        if(!spawn.success)throw std::logic_error("Rolo allocation failed");
        movement.controlled=input.base_key=held.base=spawn.head;input.main_state=0x1c6c;
        control.controlled=control.base=spawn.head;
        const TerrainMapView initial_map{level_assets.map};
        count_level_companions(initial_map,progress.selector,progress.remaining_c556,progress.flags);
        pool.resolve(spawn.head).word(68,0);
        select_player_startup_marker(initial_map,startup_selector,pool.resolve(spawn.head),checkpoint,
            [&]{initialize_camera(camera,camera_input());});
        std::copy(level_assets.map.begin(),level_assets.map.end(),map_storage.begin());
        std::copy(level_assets.background.begin(),level_assets.background.end(),background_map_storage.begin());
        plane.word(4,64);plane.word(6,6);plane.word(8,0x1f80);plane.word(10,0x3f0);
        plane.word(12,0x1f80);plane.word(14,0x2000);plane.word(22,0xffff);plane.word(40,level_assets.height);
        background_plane.word(4,32);background_plane.word(6,2);background_plane.word(8,0xf80);background_plane.word(10,0x1f0);
        background_plane.word(12,0xf80);background_plane.word(14,0x1000);background_plane.word(22,0xffff);
        background_plane.word(40,TerrainMapView{background_map_storage}.word(6));
        if(restart_checkpoint)checkpoint=*restart_checkpoint;
        restore_player_checkpoint(pool.resolve(spawn.head),checkpoint);
        if(lift_entry){
            // Original608A/3E2C: first accepted class5 variant14/15, x+8,y=row*16+17.
            // 4CB8 returns screen-x+120 (nonzero), so the scanner stops here.
            bool found=false;const TerrainMapView map{map_storage};
            for(unsigned row=0;row<map.word(6)/16&&!found;++row){
                for(unsigned at=map.word(8+row*2);at<map.word(10+row*2);at+=4){
                    const auto record=map.record(at);if((record.type&0xfffe)!=0x0514)continue;
                    auto&c=pool.resolve(movement.controlled);const auto x=std::uint16_t(record.x+8);c.word(12,x);c.longword(16,0);
                    const auto r=allocate_actor_chain(pool,{0x152b8,std::uint32_t(x)<<16,0,map_identity+at,0,0},*this);
                    if(r.success){auto&a=pool.resolve(r.head);a.longword(42,0xf046);a.word(54,std::uint16_t(row*16+17));}
                    found=true;break;
                }
            }
            if(!found)throw std::logic_error("Lift arrival requires original class5 entry marker");
        }
        // Original startup scan consumes miner-hat markers across the whole map,
        // so the attachment exists even when entry is far from its marker.
        {const TerrainMapView map{map_storage};
         for(unsigned row=0;row<level_assets.height/16;++row)
          for(unsigned at=map.word(8+row*2);at<map.word(10+row*2);at+=4){
           const auto record=map.record(at);if((record.type>>8)!=5)continue;
           const auto index=(record.type&0xfe)/2;
           if(index<level1_object_data::generic_spawn_table.size()&&level1_object_data::generic_spawn_table[index]==0x148e4)spawn_marker(record);
          }
        }
        initialize_camera(camera,camera_input());
        stream(camera.foreground_x,camera.foreground_y);
        list();animate();progress_hud_update();achievement_previous_flags=progress.flags;
        publish_level1_status_hud(status_hud,movement.c51d,score,progress,[&](auto command){sound=command;});
    }
    Level1EnemySlice(const Level1EnemySlice&)=delete;
    Level1EnemySlice& operator=(const Level1EnemySlice&)=delete;
    const ActorDefinition& definition(std::uint32_t key)const{
        for(const auto& d:definitions)if(d.key==key)return d;
        throw std::logic_error("Unbound slice definition");
    }
    const ActorChainDefinition& allocation_definition(std::uint32_t key)override{
        for(const auto& d:allocations)if(d.initial.key==key)return d;
        throw std::logic_error("Unbound slice allocation");
    }
    GraphicsAllocation allocation_graphics(std::uint16_t count)override{return graphics.allocate(count,*this);}
    std::uint32_t allocation_failures{},allocation_palette_writes{},last_allocation_context{};
    void allocation_diagnostic(std::uint32_t context)override{
        ++allocation_failures;last_allocation_context=context;
        // $5998 returns to the allocator. Replace its colour-port burst with
        // synchronous native palette requests; never turn capacity into exit.
        struct Burst final:PaletteBurstServices {
            Level1EnemySlice& w;explicit Burst(Level1EnemySlice& v):w(v){}
            void enter_critical()override{}
            void control_word(std::uint16_t)override{}
            void control_long(std::uint32_t)override{}
            void colour_word(std::uint16_t value)override{w.palette[0]=value;++w.allocation_palette_writes;}
            void leave_critical()override{}
        } burst(*this);
        publish_allocation_failure_palette(static_cast<std::uint16_t>(context),burst);
    }

    std::uint16_t marker_word(std::uint32_t key)override{
        if(key<map_identity||key-map_identity+2>map_storage.size())throw std::out_of_range("Marker outside foreground MAP");
        const auto at=key-map_identity;return static_cast<std::uint16_t>((map_storage[at]<<8)|map_storage[at+1]);
    }
    void marker_word(std::uint32_t key,std::uint16_t value)override{
        (void)marker_word(key);const auto at=key-map_identity;
        map_storage[at]=static_cast<std::uint8_t>(value>>8);map_storage[at+1]=static_cast<std::uint8_t>(value);
    }
    std::uint8_t callback_override_flag(std::int16_t index)override{
        if(index<0||static_cast<std::size_t>(index)>=actor_type_gates.size())throw std::out_of_range("Original C5A8 actor type gate domain");
        return actor_type_gates[index];
    }
    void player_death_transition()override{achievement_attempt.died();game_over_requested=true;death_requested=false;}
    void player_companion_action(std::uint16_t type,ActorPool& actors,std::uint32_t& key)override{
        const auto& actor=actors.resolve(key);
        const bool wall_action=type==8&&(actor.byte(124)&1)&&
            (actor.byte(124)&((actor.byte(118)&8)?2:4));
        update_companion_action(actors.resolve(key),type,terrain);
        if(type==8&&!wall_action){
            key=input.base_key; // $7AB4 changes the live A0 actor before returning.
            rolo_action_release(actors.resolve(key));
        }
    }
    std::uint32_t head_offset_for_selector(std::int16_t selector)override{
        if(selector<0||selector%4||selector/4>=6)throw std::logic_error("Unbound head-offset domain");
        return level1_world_data::head_offsets[selector/4];
    }
    void alternate_player_presentation()override{
        auto& base=pool.resolve(input.base_key);auto& head=pool.resolve(base.longword(84));
        AlternateCompanionPresentationState state{}; // F280 is zero outside the FCD4 animation loop.
        state.c512=movement.contact.override_c512;state.c511=movement.contact.action_gate_c511;
        update_level1_alternate_presentation(pool.resolve(movement.controlled),movement.controlled,base,head,state);
        movement.contact.override_c512=state.c512;movement.contact.action_gate_c511=state.c511;
    }
    const ActorDefinition& companion_control_definition(const ActorState& actor)override{return definition(actor.longword(4));}
    bool choose_companion(std::uint16_t choice){
        const auto accepted=select_level1_companion_menu_choice(choice,pool,companion_state,progress,control,*this);
        if(!accepted)return false;
        movement.controlled=control.controlled;movement.controlled_type=control.type;movement.c510=progress.action_c510;
        movement.c50f=companion_state.c50f;companions=companion_state.slots;
        return true;
    }
    void actor_animation_sound(std::uint16_t value)override{sound=value;}
    std::uint32_t score_effect_value(const ActorState& actor)override{return definition(actor.longword(4)).longword(28);}
    void add_score(std::uint32_t amount)override{award_score(awards,amount,movement.c51d);score=awards.total;}
    void contact_resolution_sound(std::uint16_t value)override{sound=value;}
    void contact_exit_transition()override{throw std::logic_error("Level exit transition outside slice");}
    void contact_rolo_death_transition()override{achievement_attempt.died();if(!game_over_requested)death_requested=true;}
    void contact_companion_death_transition()override{
        // $9642..$96C6 actor/control branch. Fade, VRAM publication and device
        // frame suffix remain separate pending presentation contracts.
        const auto dying=movement.controlled;
        if(companion_state.c50f>1)throw std::logic_error("Unbound companion death follow mode");
        if(!choose_companion(static_cast<std::uint16_t>(3+companion_state.c50f)))
            throw std::logic_error("Companion death failed to restore Rolo");
        auto& actor=pool.resolve(dying);actor.byte(116,255);actor.byte(125,actor.byte(125)|4);
        detach_level1_companion(actor,companion_state,pool);companions=companion_state.slots;
        initialize_camera(camera,camera_input());stream(camera.foreground_x,camera.foreground_y);
        movement.contact.hit_gate_c51a=0;movement.bounds.c516=0;movement.contact.action_latch_c517=0;
    }
    bool collectible_contact(ActorState& a)override{return actor_player_contact(a,pool.resolve(movement.controlled));}
    const ActorDefinition& collectible_definition(const ActorState& a)override{return definition(a.longword(4));}
    void collectible_score(std::uint32_t amount)override{add_score(amount);}
    std::uint8_t& collectible_lives()override{return movement.c51d;}
    void collectible_sound(std::uint16_t value)override{sound=value;}
    AnimationRandom& collectible_random()override{return random;}
    std::uint16_t reward_camera_x()override{return camera.foreground_x;}
    std::uint16_t reward_camera_y()override{return camera.foreground_y;}
    void increment_reward_byte(std::uint32_t address)override{
        if(address==0xffffc550){++progress.key_c550;return;}
        if(address==0xffffc551){++progress.piece_c551;achievement_events|=achievement_bit(45);return;}
        throw std::logic_error("Unbound reward completion byte");
    }
    ActorPool& companion_pool()override{return pool;}
    ActorState& companion_controlled()override{return pool.resolve(movement.controlled);}
    ActorState& companion_base()override{return pool.resolve(input.base_key);}
    const ActorTerrain& companion_terrain()override{return terrain;}
    PlayerFrameHistory& companion_history()override{return history;}
    void companion_land(ActorState& a)override{enemy.land(a);}
    bool companion_contact(ActorState& a)override{return actor_player_contact(a,pool.resolve(movement.controlled));}
    void companion_horizontal_collision(ActorState& a)override{actor_horizontal_collision(a,terrain);}
    std::uint8_t companion_c514()override{return movement.c514;}
    std::uint8_t companion_f2bc()override{return f2bc;}
    std::uint8_t companion_c520()override{return input.action.c520;}
    void companion_restore_inactive(ActorState& a)override{
        const auto index=static_cast<std::uint16_t>((history.cursor-a.word(50))&1023);
        const auto x=companion_history_word(history,index,0);
        if(signed_word(x)<=signed_word(camera.foreground_x)||signed_word(x)>=signed_word(static_cast<std::uint16_t>(camera.foreground_x+320)))
            throw std::logic_error("Inactive companion early-X-reject incoming D2 domain unbound");
        restore_level1_inactive_companion(a,companion_state,*this,0);
    }
    ActorState& progress_actor(std::uint32_t key)override{return pool.resolve(key);}
    void progress_sound(std::uint16_t command)override{sound=command;}
    std::uint32_t progress_spawn(std::uint32_t d,std::uint32_t x,std::uint32_t y)override{return allocate_actor_chain(pool,{d,x,y,0,0,0},*this).returned_key;}
    void progress_hud_update()override{
        if(progress.rescued_c552)return;
        if(!hud.actor){
            const auto result=allocate_actor_chain(pool,{0x1476e,160u<<16,0,0,0,0},*this);
            if(!result.success)return;
            hud.actor=result.head;auto& a=pool.resolve(hud.actor);
            a.byte(126,a.byte(126)|16);a.byte(48,2);a.byte(50,50);a.word(36,56);a.word(38,16);
            a.longword(28,0x5854524e);a.longword(8,0x5854524e);a.word(32,0);a.word(34,0);
        }else{
            auto& a=pool.resolve(hud.actor);a.byte(50,50);
            if(static_cast<std::int8_t>(a.byte(48))<0){a.byte(48,static_cast<std::uint8_t>(0u-a.byte(48)));a.byte(49,0);a.word(46,static_cast<std::uint16_t>(a.word(46)+2));}
        }
        publish_level1_rescue_counter(hud,pool.resolve(hud.actor).word(2),progress.remaining_c556);
        hud_remaining=progress.remaining_c556;
    }
    bool progress_exit_contact(ActorState& a,std::uint16_t width_shrink,std::uint16_t height_shrink)override{
        const auto width=a.word(36),height=a.word(38);
        a.word(36,static_cast<std::uint16_t>(width-width_shrink));a.word(38,static_cast<std::uint16_t>(height-height_shrink));
        (void)actor_player_contact(a,pool.resolve(movement.controlled));a.word(36,width);a.word(38,height);
        return a.byte(123)!=0;
    }
    void progress_state_transition(std::uint32_t state)override{requested_state=state;}
    void progress_music(std::uint16_t command,std::uint16_t argument)override{music_command=command;music_argument=argument;}
    void invoke_actor_callback(std::uint32_t key,std::uint32_t callback)override{
        if(callback==0xbe4e&&dynamic_platform_data::is_definition(pool.resolve(key).longword(4))){update_log_platform(key);return;}
        if(callback==0xa84c)return;
        if(callback==0xf194||callback==0xf046){
            auto*a=&pool.resolve(key);lift_state.controlled=movement.controlled;lift_state.frozen=movement.c524;lift_state.action_gate=movement.contact.action_gate_c511;lift_state.reward=progress.spawn_selector;
            if(callback==0xf194)update_actor_facing_phase_dispatch(a,boss_services);else update_actor_replacement_dispatch(a,boss_services);
            movement.c524=lift_state.frozen;movement.contact.action_gate_c511=lift_state.action_gate;
            if(lift_state.exit_latch){transition=255;lift_reload=255;level_transition_latch=255;next_level_selector=std::uint16_t((progress.selector&0xff00)|lift_state.next_reward);next_entry_selector=0;}
            return;
        }
        if(callback==0xed18||callback==0xecc4){auto*a=&pool.resolve(key);ActorInjuryGlobals g{flash_gates[3],flash_timer};if(callback==0xed18)update_actor_injury_motion(a,g,boss_services);else update_actor_injury_transition(a,g,boss_services);flash_gates[3]=g.gate;flash_timer=g.timer;return;}
        if(callback==0xef3c){update_actor_integer_hit_motion(pool.resolve(key),flash_gates[3],shared_enemy);return;}
        if(callback==0xf394){auto*a=&pool.resolve(key);PhaseEmitterContext c{};GraphicPhaseGlobals g{flash_gates[3],0,flash_timer,std::uint16_t(frame)};update_actor_graphic_contact(a,c,g,graphic_services);flash_gates[3]=g.gate;flash_timer=g.timer;if(g.scene){boss_scene_f283=g.scene;if(progress.selector==38){achievement_events|=1u<<16;achievement_events|=achievement_bit(29);achievement_events|=achievement_attempt.boss(33);}}return;}
        if(callback==0xf7c4){update_actor_rotating_pursuit(pool.resolve(key),shared_enemy);return;}
        if(callback==0xf856){update_actor_contact_corner(pool.resolve(key),shared_enemy);return;}
        if(callback==0xf62a){auto*a=&pool.resolve(key);update_actor_chain_visual(a,linked_services);return;}
        if(callback==0xddf4){auto*a=&pool.resolve(key);ride_state.hit=movement.contact.hit_gate_c519;ride_state.contains=f2bc;ride_state.action=movement.c510;ride_state.down=buttons.mapped[1];update_actor_ride_coordinator(a,ride_state,linked_services);f2bc=ride_state.contains;if(f2bc&&pool.resolve(key).byte(50)&&pool.resolve(key).longword(4)==0x14a7c)achievement_attempt.rode_cart=true;return;}
        if(callback==0xdc2c){
            auto*a=&pool.resolve(key);
            // Native integration baseline: ROM's retained D2/D3 high WORDs are
            // not yet proven at this caller. Zero subpixels are NOT a fidelity certificate.
            ActorEmitterContext context{0,0,0};update_actor_facing_emitter(a,context,probes);return;
        }
        if(callback==0xdcda){auto*a=&pool.resolve(key);update_actor_chain_throw(a,probes);return;}

        if(callback==0xd57e||callback==0xd624||callback==0xd6c6){
            const bool was_completed=phase_boss.completed;auto*a=&pool.resolve(key);phase_boss.frame=frame;phase_boss.gates=flash_gates;phase_boss.timer=flash_timer;
            if(callback==0xd57e)update_actor_phase_completion(a,phase_boss,phase_boss_services);
            else if(callback==0xd624)update_actor_phase_first(a,phase_boss,phase_boss_services);
            else update_actor_phase_second(a,phase_boss,phase_boss_services);
            // $D4CC publishes F268 and F330 as shared terrain/camera state.
            // Keeping them only in the boss context detached the truck from its actors.
            if(phase_boss.display){terrain.x_shift=phase_boss.offset;width=phase_boss.display;movement.bounds.width=width;}
            if(!was_completed&&phase_boss.completed){achievement_events|=achievement_attempt.boss(32);achievement_events|=achievement_bit(28);}
            surface_gate=phase_boss.completed; // Shared C5E8 disables $9250 truck terrain damage after victory.
            flash_gates=phase_boss.gates;flash_timer=phase_boss.timer;return;
        }
        if(callback==0xd7e6){update_actor_contact_diagonal(pool.resolve(key),enemy);return;}

        if(callback==0xe712){const bool previous=linked_rescue_c5b6;auto*a=&pool.resolve(key);update_actor_linked_rescue(a,linked_rescue_c5b6,rescue_services);if(!previous&&linked_rescue_c5b6&&progress.selector==9)achievement_events|=achievement_bit(3);return;}
        if(callback==0xe776){auto&a=pool.resolve(key);if(a.byte(124)&1){a.byte(122,255);a.longword(62,0x30000);}actor_gravity(a);actor_integrate(a);enemy.land(a);return;}

        if(callback==0xba64||callback==0xba9e){update_choreography_actor(*this,key,callback==0xba9e);return;}
        if(callback==0xf8aa){
            auto* a=&pool.resolve(key);PhaseEmitterContext c{};LinkedActorGlobals g{};g.live_count=active.count;g.camera_x=reward_camera_x();g.camera_y=reward_camera_y();g.alternate=movement.contact.override_c512;g.sound_timer=pursuit_sound_timer_f2b4;
            update_actor_random_pursuit(a,c,g,random,std::span<const std::uint8_t>(reinterpret_cast<const std::uint8_t*>(timed_projectile_wave.data()),timed_projectile_wave.size()),remaining);pursuit_sound_timer_f2b4=g.sound_timer;return;
        }

        if(callback==0xb8ee){
            auto& a=pool.resolve(key);if(!a.byte(50)){a.byte(50,255);spawner_landed_c5ce=0;a.byte(53,100);a.byte(52,100);}
            if(static_cast<std::int8_t>(spawner_landed_c5ce)>=3){if(a.word(16))a.word(16,std::uint16_t(a.word(16)-1));return;}
            const auto old=a.byte(52);a.byte(52,std::uint8_t(old-1));if(old)return;
            auto rate=a.byte(53);if(static_cast<std::int8_t>(rate)<=40)rate=41;rate=std::uint8_t(rate-2);a.byte(53,rate);a.byte(52,rate);
            (void)allocate_actor_chain(pool,{0x1474c,a.longword(12),a.longword(16),0,0,0},*this);return;
        }
        if(callback==0xb956){
            auto& a=pool.resolve(key);
            if(!a.byte(46)){a.byte(46,255);a.byte(121,level1_object_data::spawner_directions[random.between(0,6)]);a.longword(58,std::uint32_t(random.between(1,5))<<15);a.byte(122,255);a.longword(62,0x80000);return;}
            if(a.byte(124)&1){if(static_cast<std::int8_t>(spawner_landed_c5ce)>=3){a.longword(42,0xb7c0);a.byte(46,0);}return;}
            actor_gravity(a);actor_integrate(a);enemy.land(a);if(a.byte(124)&1)++spawner_landed_c5ce;
            (void)enemy.player_contact(a);if(!a.byte(123))return;
            a.longword(42,0xb7c0);a.word(70,4);a.byte(46,0);
            const auto d=level1_object_data::spawner_rewards[random.between(0,17)];const auto r=allocate_actor_chain(pool,{d,a.longword(12),a.longword(16),0,0,0},*this);if(r.success)pool.resolve(r.head).longword(42,0xb726);return;
        }

        if(callback==0xefa8){
            auto& base=pool.resolve(input.base_key);auto& head=pool.resolve(base.longword(84));
            const bool helmet_start=pool.resolve(key).longword(4)==0x14928&&!pool.resolve(key).byte(46);
            AlternateCompanionPresentationState state{};state.f280=animation_gate;state.c512=movement.contact.override_c512;state.c511=movement.contact.action_gate_c511;
            update_level1_alternate_presentation(pool.resolve(key),key,base,head,state);
            if(helmet_start&&state.f280&&state.c512&&pool.resolve(key).byte(46)&&!debug_free_flight)achievement_events|=1u<<17;
            movement.contact.override_c512=state.c512;movement.contact.action_gate_c511=state.c511;if(state.f280)contact_root_word=state.held_actor_low_word;return;
        }

        if(callback==0xea4c){auto* a=&pool.resolve(key);ActorInjuryGlobals g{flash_gates[3],flash_timer};update_actor_injury_phase(a,g,boss_services);flash_gates[3]=g.gate;flash_timer=g.timer;return;}
        if(callback==0xea20){if(!flash_gates[3])invoke_actor_callback(key,0xb702);return;}
        if(callback==0xebf6){auto* a=&pool.resolve(key);update_parent_linked_part(a,level1_object_data::boss29_part_offsets,remaining,0xec94);return;}

        if(callback==0xb714){update_actor_bounce_restart(key,*this);return;}
        if(callback==0xb726){update_actor_bounce_landing(key,*this);return;}
        if(callback==0xb566){update_first_enemy(pool.resolve(key),enemy);return;}
        if(callback==0xb702){
            auto& a=pool.resolve(key);const auto handler=definition(a.longword(4)).longword(22);
            if(handler==0x989c){
                if(!collectible_contact(a))return;
                TriggerCaptureState state{input.action.c520,capture_c521,movement.c513,movement.c524,capture_c526,movement.controlled_type};
                capture_controlled_player(a,pool.resolve(movement.controlled),a.longword(84)?&pool.resolve(a.longword(84)):nullptr,state);
                if(!input.action.c520&&state.c520)achievement_events|=1u<<4;
                input.action.c520=state.c520;capture_c521=state.c521;movement.c513=state.c513;movement.c524=state.c524;capture_c526=state.c526;return;
            }
            if(handler==0x9916){
                if(!collectible_contact(a))return;sound=64;collect_level1_scored_item(a,definition(a.longword(4)),*this);
                const auto& base=pool.resolve(input.base_key);const auto r=allocate_actor_chain(pool,{0x14928,base.longword(12),base.longword(16),0,0,0},*this);
                score_followup=r.returned_key;if(score_followup)movement.contact.override_c512=255;return;
            }
            if(handler==0x976c){if(collectible_contact(a))shared_enemy.hurt_controlled_actor(a);return;}
            if(handler==0x9800){
                if(!collectible_contact(a))return;sound=64;
                achievement_vacuum_obtained=true;
                if(input.action.c51c!=3)++input.action.c51c;
                a.byte(125,a.byte(125)|4);(void)actor_hit_counter_zero(a,enemy);return;
            }
            if(handler==0x9826){if(collectible_contact(a)){collect_float_power(a,movement.c513,input.action.c520,powerups);if(movement.c513)achievement_events|=1u<<11;}return;}
            if(handler==0x984a){
                if(collectible_contact(a)){auto& base=pool.resolve(input.base_key);collect_stored_projectiles(a,held.stored_definition,held.stored_count,pool.resolve(base.longword(84)),powerups);if(held.stored_count&&held.stored_definition==0x140ca)achievement_events|=1u<<5;}return;
            }
            if(handler==0x9a1a){if(collectible_contact(a)){collect_level1_piece(a,progress,*this);achievement_events|=achievement_bit(45);if(progress.selector==3&&a.longword(88)==map_identity+300&&movement.controlled_type==4&&achievement_attempt.eligible&&!debug_free_flight)achievement_events|=achievement_bit(8);}return;}
            const auto marker=a.longword(88);update_level1_collectible(a,*this);if(handler==0x99e2&&a.longword(42)==0xb7c0&&progress.selector==19&&(marker==map_identity+128||marker==map_identity+132))achievement_events|=achievement_bit(12);return;
        }
        if(callback==0xb47c){update_offscreen_retirement(pool.resolve(key));return;}
        if(callback==0xda72){
            auto& base=pool.resolve(input.base_key);auto& head=pool.resolve(base.longword(84));ActorHeldPublication publication{contact_root_word,0};
            update_actor_held_presentation(pool.resolve(key),base,head,static_cast<std::uint16_t>(key),animation_gate,movement.contact.override_c512,publication);contact_root_word=publication.actor;return;
        }
        if(callback==0xdd36){actor_scroll_relative_motion(pool.resolve(key),terrain.x_shift);return;}
        if(callback==0xe5d0){auto* a=&pool.resolve(key);update_actor_vertical_probe(a,probes);return;}
        if(callback==0xe14e){update_actor_contact_only(pool.resolve(key),enemy);return;}
        if(callback==0xe11a){update_actor_flipped_phase_cycle(pool.resolve(key),shared_enemy);return;}
        if(callback==0xe478){update_actor_hit_fall(pool.resolve(key),shared_enemy);return;}
        if(callback==0xe1bc){update_actor_hit_walk(pool.resolve(key),shared_enemy);return;}
        if(callback==0xe48c){update_actor_flying_pursuit(pool.resolve(key),enemy);return;}
        if(callback==0xe15e){update_actor_parent_jump(pool,key,shared_enemy);return;}
        if(callback==0xe6d8){update_actor_contact_settle(pool.resolve(key),shared_enemy);return;}
        if(callback==0xe300){
            auto& a=pool.resolve(key);if(a.byte(117))return;update_actor_contact_only(a,enemy);actor_integer_x_step(a,1);enemy.choose_direction(a);
            const auto timer=static_cast<std::uint16_t>(a.word(46)-1);a.word(46,timer);
            if(signed_word(timer)<0){a.word(46,100);(void)allocate_actor_chain(pool,{0x14d46,a.longword(12),a.longword(16),0,0,0},*this);}return;
        }
        if(callback==0xe342){auto* a=&pool.resolve(key);PhaseEmitterContext context{};update_contact_phase_dispatch(a,context,remaining);return;}
        if(callback==0xf9ee){const auto previous=pool.resolve(key).word(48);auto* a=&pool.resolve(key);PhaseEmitterContext context{};RemainingActorGlobals globals{visited_c553};update_limited_child_emitter(a,context,globals,remaining);if(progress.selector==63&&pool.resolve(key).longword(4)==0x157c4&&pool.resolve(key).word(48)>previous)achievement_events|=achievement_bit(25);return;}
        if(callback==0xe1f6){auto* a=&pool.resolve(key);PhaseEmitterContext context{};update_split_child_emitter(a,context,remaining);return;}
        if(callback==0xd830){update_actor_ground_hopper(pool.resolve(key),enemy);return;}
        if(callback==0xda22){update_actor_contact_six_step(pool.resolve(key),enemy);return;}
        if(callback==0xd8be){update_actor_orbit_patrol(pool.resolve(key),shared_enemy);return;}
        if(callback==0xdbbe){update_actor_contact_return_jump(pool.resolve(key),shared_enemy);return;}
        if(callback==0xe0c2){update_actor_proximity_fall(pool.resolve(key),shared_enemy);return;}
        if(callback==0xe5a4){update_actor_contact_ground_walk(pool.resolve(key),enemy);return;}
        if(callback==0xd960||callback==0xdb44||callback==0xe620){
            auto* a=&pool.resolve(key);
            if(callback==0xd960)update_actor_pause_orbit(a,probes);
            else if(callback==0xdb44)update_actor_table_patrol(a,probes);
            else update_actor_range_leap(a,probes);return;
        }
        if(callback==0xd89e){update_actor_contact_walk(pool.resolve(key),enemy);return;}
        if(callback==0xe1ce){update_actor_contact_facing(pool.resolve(key),enemy);return;}
        if(callback==0xe120){update_actor_phase_cycle(pool.resolve(key),shared_enemy);return;}
        if(callback==0xb3c4){update_passive_enemy(key,*this);return;}
        if(callback==0xb3f2){update_roaming_enemy(key,*this);return;}
        if(callback==0xb440){update_captured_enemy(pool.resolve(key),*this);return;}
        if(callback==0xb498||callback==0xb51e){update_thrown_enemy(key,*this,callback==0xb51e);return;}
        if(callback==0xb7c0){update_collected_item(pool.resolve(key),random);return;}
        if(callback==0xb2e6){update_level1_key_proximity(pool.resolve(key),key_services);return;}
        if(callback==0xb314){update_level1_key_actor(pool.resolve(key),key_services);return;}
        if(callback==0xb386){update_reward_curve(pool.resolve(key),*this);return;}
        if(callback==0xa8bc){const auto before=progress.remaining_c556;const auto type=definition(pool.resolve(key).longword(4)).word(10);update_level1_waiting_companion(key,companion_state,progress,*this);
            if(before&&progress.remaining_c556<before){const unsigned index=type==16?34:type==20?35:type==8?36:type==12?37:50;if(index<50)achievement_events|=achievement_bit(index);}return;}
        if(callback==0xa84e){
            if(key!=input.base_key)throw std::logic_error("Uncontrolled Rolo callback requires original base identity");
            update_level1_uncontrolled_rolo(key,companion_state,progress,movement.c513,*this,[&]{
                auto base_presentation=presentation;
                base_presentation.selector.c510=base_presentation.selector.c519=base_presentation.selector.c51b=0;
                update_player_presentation(pool,input.base_key,input.base_key,base_presentation,*this);
                presentation.idle_countdown=base_presentation.idle_countdown;
            });return;
        }
        if(callback==0xab28){update_level1_ground_companion(pool.resolve(key),progress,*this);return;}
        if(callback==0xa9b0||callback==0xaa4a){update_level1_air_companion(pool.resolve(key),companion_state,*this,callback==0xaa4a);return;}
        if(callback==0xa92e){update_level1_stacked_companion(pool.resolve(key),companion_state,*this);return;}
        if(callback==0xadd0){update_level1_detached_companion(pool.resolve(key),*this);return;}
        if(callback==0xb2d2){update_level1_companion_container(pool.resolve(key),*this);return;}
        if(callback==0xb7b8){update_released_companion_container(pool.resolve(key),random);return;}
        if(callback==0xe528){update_level1_exit(pool.resolve(key),progress,frame,*this);return;}
        if(callback==0xd452){update_level1_rescue_counter(pool.resolve(key),hud);return;}
        if(callback==0xef68){update_score_effect(pool.resolve(key),first_enemy_definition_data::score_wave,*this);return;}
        throw std::logic_error("Unbound slice actor callback");
    }
    void list(){
        // $29EE reads F362/F366, the actor camera before mode6's F268
        // terrain shift. Otherwise visible shots are marked offscreen and retired.
        rebuild_active_actor_list(pool,deferred,active,camera.x,camera.y,lifetime);
    }
    void animate(){
        struct AnimationServices final:ActorAnimationListServices,ActorAnimationSpawnServices {
            Level1EnemySlice& w;explicit AnimationServices(Level1EnemySlice& world):w(world){}
            std::uint16_t d2_high=0xffff,d3_high=0; // $4F3A/$4F3C normal Mode3 camera tail.
            void actor_animation_spawn_inherited(ActorState& parent,std::uint32_t definition)override{
                AnimationSpawnCursor cursor{};(void)animation_inherited_spawn(parent,definition,cursor,w.pool,w);
            }
            void actor_animation_spawn_random(ActorState& parent,std::uint32_t definition,std::uint16_t range,AnimationRandom& random)override{
                const auto position=random_animation_spawn_position(parent,range,random,d2_high,d3_high);
                w.target_x_c494=position.target_x_c494;w.target_y_c498=position.target_y_c498;
                (void)spawn_random_animation_actor(parent,definition,position,w.pool,w);
                d2_high=static_cast<std::uint16_t>(position.x>>16);d3_high=static_cast<std::uint16_t>(position.y>>16);
            }
            const ActorDefinition& animation_definition(std::uint32_t key)override{return w.definition(key);}
            void animation_callback(std::uint32_t key,std::uint32_t callback)override{w.invoke_actor_callback(key,callback);}
            void animate_actor(std::uint32_t,ActorState& a,const ActorDefinition& d)override{
                const bool object=std::any_of(level1_object_data::definitions.begin(),level1_object_data::definitions.end(),[&](const auto& item){return item.key==d.key;});
                const auto& data=d.key==0x13ecc||d.key==0x13eee?level1_player_animation_data::data:object?level1_object_animation_data::data:first_enemy_animation_data::data;
                const auto status=update_actor_animation_from_definition(a,d.key,data,&w,&w.random,this,&w.movement.c524);
                if(status!=AnimationResult::Ok&&status!=AnimationResult::Retired){
                    std::fprintf(stderr,"Native animation definition %06x selector %u status %u\n",d.key,a.word(70),static_cast<unsigned>(status));
                    std::fprintf(stderr,"Actor callback %06x slot %u controlled %08x base %08x companions %08x/%08x/%08x\n",a.longword(42),a.byte(47),w.movement.controlled,w.input.base_key,w.companion_state.slots[0],w.companion_state.slots[1],w.companion_state.slots[2]);
                    throw std::logic_error("Unbound slice animation");
                }
            }
        } services(*this);
        update_actor_animation_list(pool,active,animation_gate,services);
    }
    void spawn_log_platform(const TerrainDescriptorRecord& record){
        const TerrainMapView map{map_storage};unsigned row=0;for(;row<level_assets.height/8;row+=2)if(record.record_offset>=map.word(8+row)&&record.record_offset<map.word(10+row))break;
        if(row>=level_assets.height/8)throw std::logic_error("Log marker outside MAP");
        const auto macro=level_assets.terrain_bank().macros[record.type&255];
        const unsigned width=macro.width*16,height=macro.height*16;
        const auto result=allocate_actor_chain(pool,{dynamic_platform_data::definition_key(level_assets.bank,record.type&255),std::uint32_t(std::uint16_t(record.x+width/2))<<16,std::uint32_t(std::uint16_t(row*8+height))<<16,map_identity+record.record_offset,map_identity+record.record_offset,0},*this);
        if(!result.success)return;auto&a=pool.resolve(result.head);a.word(36,static_cast<std::uint16_t>(width));a.word(38,static_cast<std::uint16_t>(height));a.word(40,static_cast<std::uint16_t>(width*height/2));a.longword(46,record.type&255);a.word(54,std::uint16_t(((record.type&0xff00)>>6)-128));a.longword(28,0x5854524e);a.longword(8,0x5854524e);
        platform_definition_flags.at((result.head-ActorPool::first_key)/ActorPool::stride)=definition(a.longword(4)).byte(26);
        spawn_events.push_back({map_identity+record.record_offset,result.head,record.type,a.word(12),a.word(16),0});
    }
    void update_log_platform(std::uint32_t key){
        struct Services final:ActorPlatformContactServices,PlatformDirectionService,PlatformDirectionFlagsService,PlatformObjectContactService,ChainPlatformServices{
            Level1EnemySlice&w;std::uint32_t platform;Services(Level1EnemySlice&v,std::uint32_t key):w(v),platform(key){}
            void object_contact(ActorState&a)override{w.enemy.object_contact(a);}
            void choose_direction(ActorState&a)override{w.enemy.choose_direction(a);}
            bool choose_direction_nonzero(ActorState&a)override{return actor_choose_direction_nonzero(a,w.enemy);}
            void restore_platform_actor(std::uint32_t rider)override{PlatformPositionCache cache;const auto m=w.level_assets.terrain_bank().macros[w.pool.resolve(w.pool.resolve(rider).longword(98)).longword(46)];restore_actor_platform_surface(w.pool,rider,cache,{m.width,m.tiles},{w.level_assets.terrain_bank().collision,player_data::shapes});}
            std::uint8_t& definition_flags26(std::uint32_t)override{return w.platform_definition_flags.at((platform-ActorPool::first_key)/ActorPool::stride);}
            std::uint32_t allocate_platform_chain(std::uint32_t d,std::uint32_t x,std::uint32_t y,std::uint32_t context)override{const auto r=allocate_actor_chain(w.pool,{d,x,y,0,context,0},w);return r.success?r.head:0;}
        }services(*this,key);
        ActorPlatformRoster roster{input.base_key,movement.controlled,companion_state.slots};update_platform_roster_contact(pool,key,roster,services);auto&a=pool.resolve(key);const auto&controlled=pool.resolve(movement.controlled);
        if(a.word(54)==0)update_actor_rider_sinking_platform(a,controlled,key,services);
        // Original BF54 retains the incoming D3 high WORD. Zero is an explicit
        // native baseline pending caller provenance, not a verified ROM value.
        else if(a.word(54)==4)update_actor_bounce_platform(a,pool.resolve(movement.controlled),key,0);
        else if(a.word(54)==8||a.word(54)==12)update_actor_rider_accelerating_platform(a,controlled,key,a.word(54)==12,services);
        else if(a.word(54)==16)update_actor_rider_spring_platform(a,controlled,key);
        else if(a.word(54)>=20&&a.word(54)<=32)update_actor_wave_platform(a,(a.word(54)-20)/4);
        else if(a.word(54)==36||a.word(54)==40)update_actor_ellipse_platform(a,controlled,key,a.word(54)==40);
        else if(a.word(54)==60)update_actor_grid_platform(a,controlled,key,services);
        else if(a.word(54)==52||a.word(54)==56)update_actor_rider_reversing_platform(a,controlled,key,a.word(54)==56,services);
        else if(a.word(54)==44||a.word(54)==48)update_actor_chain_platform(pool,key,a.word(54)==48,0,services); // First graphics request replaces resource context; failure port timing remains outside native scope.
        else if(a.word(54)==64)update_actor_triggered_platform(a,controlled,key,platform_gate_f281,reward_camera_y(),0,services);
        else if(a.word(54)==68||a.word(54)==72)update_actor_triggered_platform(a,controlled,key,platform_gate_f282,reward_camera_x(),a.word(54)==68?1:2,services);
        else if(a.word(54)==76||a.word(54)==80)update_actor_retracting_platform(a,platform_gate_f281,a.word(54)==76?reward_camera_x():reward_camera_y(),a.word(54)==80);
        else if(a.word(54)==84||a.word(54)==88)update_actor_retracting_platform(a,platform_gate_f282,a.word(54)==84?reward_camera_x():reward_camera_y(),a.word(54)==88);
        else throw std::logic_error("Log motion selector");
        transfer_platform_displacement(pool,key,roster);
    }
    void spawn_marker(const TerrainDescriptorRecord& record){
        const TerrainMapView map{map_storage};std::uint16_t row=0;
        for(;row<level_assets.height/8;row=static_cast<std::uint16_t>(row+2))
            if(record.record_offset>=map.word(8+row)&&record.record_offset<map.word(10+row))break;
        if(row>=level_assets.height/8)throw std::out_of_range("Spawn marker outside MAP row spans");
        const auto type=record.type>>8;const bool collectible=type==6;
        if(type==0x0b){
            const auto parameter=record.type&255;
            if(level1_progress_flag(progress,static_cast<std::uint16_t>(parameter))&1)return;
            constexpr std::array<std::uint32_t,1> piece_definition{0x14482};
            const auto request=actor_spawn_factory_request({0,record.x,row,pool.resolve(movement.controlled).word(12),map_identity+record.record_offset},piece_definition);
            const auto result=allocate_actor_chain(pool,request,*this);
            if(result.success){pool.resolve(result.head).byte(50,static_cast<std::uint8_t>(parameter));
                spawn_events.push_back({request.marker,result.head,record.type,static_cast<std::uint16_t>(request.x>>16),static_cast<std::uint16_t>(request.y>>16),request.facing});}
            return;
        }
        auto request=actor_spawn_factory_request({static_cast<std::uint16_t>((record.type&255)*((collectible||type==13)?2:1)),record.x,row,
            pool.resolve(movement.controlled).word(12),map_identity+record.record_offset},
            collectible?std::span<const std::uint32_t>(level1_object_data::collectible_spawn_table):type==13?std::span<const std::uint32_t>(level1_object_data::special_spawn_table):type==5?std::span<const std::uint32_t>(level1_object_data::generic_spawn_table):std::span<const std::uint32_t>(level1_object_data::enemy_spawn_table));
        if(type==0x12){
            const auto index=record.type&255;
            if(index>=level1_object_data::companion_spawn_table.size())throw std::out_of_range("Companion marker parameter");
            request.definition=level1_object_data::companion_spawn_table[index];request.facing=0;
        }
        const auto result=allocate_actor_chain(pool,request,*this);
        if(result.success){
            if(type==4&&!enemy_key)enemy_key=result.head;
            if(type==0x12&&progress.rescued_c552){const auto linked=pool.resolve(result.head).longword(84);if(linked)pool.resolve(linked).byte(116,255);}
            spawn_events.push_back({request.marker,result.head,record.type,static_cast<std::uint16_t>(request.x>>16),static_cast<std::uint16_t>(request.y>>16),request.facing});
        }
    }
    void stream(std::uint16_t x,std::uint16_t y){
        plane.word(18,x);plane.word(20,y);update_foreground_terrain_camera(plane,terrain_globals,streaming);
        background_plane.word(18,camera.background_x);background_plane.word(20,camera.background_y);
        // Mode6 (fire engine) scrolls the background MAP with the camera.
        // A forced static flag kept only the initial upper curtain rows loaded.
        update_background_terrain_camera(background_plane,camera.background_flag,terrain_globals,background_streaming);
    }
    bool debug_free_flight{};
    void step(std::uint8_t pressed){
        if(!debug_free_flight){step_normal(pressed);return;}
        achievement_attempt.debug();achievement_debug_used=true;
        const auto life=movement.c51d,frozen=movement.c524;
        auto& a=pool.resolve(movement.controlled);const int speed=(pressed&64)?8:4;
        const auto x=std::uint16_t(std::clamp(int(a.word(12))+((pressed&8)?speed:0)-((pressed&4)?speed:0),24,std::max(24,int(width)-24)));
        const auto y=std::uint16_t(std::clamp(int(a.word(16))+((pressed&2)?speed:0)-((pressed&1)?speed:0),48,std::max(48,int(level_assets.height)-16)));
        const auto place=[&]{auto& c=pool.resolve(movement.controlled);c.longword(12,std::uint32_t(x)<<16);c.longword(16,std::uint32_t(y)<<16);c.longword(58,0);c.longword(62,0);c.longword(98,0);c.byte(124,0);c.byte(126,c.byte(126)&~2u);c.byte(125,c.byte(125)&~2u);};
        const auto protect=[&]{movement.c51d=life;movement.contact.hit_gate_c519=movement.contact.hit_gate_c51a=movement.contact.hit_gate_c51b=0;movement.contact.action_latch_c517=0;death_requested=false;game_over_requested=false;};
        protect();place();movement.c524=255;
        for(auto& c:pool.actors)if(c.longword(42)==0xddf4)c.byte(50,0);
        f2bc=0;step_normal(0);movement.c524=frozen;protect();place();achievement_events=0;
        update_camera(camera,camera_input());stream(camera.foreground_x,camera.foreground_y);list();animate();
        publish_level1_status_hud(status_hud,movement.c51d,score,progress,[&](auto command){sound=command;});
    }
    void step_normal(std::uint8_t pressed){
        if(death_requested||game_over_requested)return;
        if(!debug_free_flight&&(progress.selector==62||progress.selector==63))achievement_events|=achievement_bit(24);
        if(transport_hooks&&transport_hooks->resume_transport_frame(pressed))return;
        update_palette_flashes(flash_timer,flash_gates,boss_services); // Original Mode3 frame prefix $2F3C.
        map_player_input(buttons,pressed);input.direction.mapped=buttons.mapped;
        movement.c481=buttons.mapped[1]; // C481 aliases mapped Down; buoyancy uses it to descend.
        movement.camera_y=plane.word(20);player_movement_phase(pool,movement,player);
        if(game_over_requested)return; // $7840 changes the next main-state dispatcher.
        struct Phases final:SharedPlayerFrameServices {
            Level1EnemySlice& w;
            explicit Phases(Level1EnemySlice& world):w(world){}
            void player_post_motion()override{w.post_motion_terrain();}
            void scan_active_actors()override{
                w.progress.action_c510=w.movement.c510;
                w.companions=w.companion_state.slots;w.schedule.secondary=w.companion_state.slots;
                w.list();w.schedule.controlled=w.movement.controlled;w.schedule.base=w.input.base_key;
            }
            void update_actors()override{update_actor_callbacks(w.pool,w.schedule,w.active,w);}
            void post_collision()override{
                record_player_frame_history(w.history,w.input.main_state,w.pool.resolve(w.input.base_key),w.selectors);
            }
            void player_link_phase()override{
                player_airborne_count(w.pool.resolve(w.movement.controlled),w.movement.c524);++w.frame;
            }
            void contact_phase()override{
                BoundPlayerTerrainResponseServices surfaces(w.movement.controlled_type,w.frame,w.surface_gate,w.movement.bounds.c516,w.movement.contact);
                update_player_terrain_response(w.pool.resolve(w.movement.controlled),w.terrain,
                    {w.movement.drag,w.input.direction.override_acceleration,w.previous_shift},surfaces);
            }
            void post_presentation()override{
                if(w.transport_hooks&&w.transport_hooks->scan_transport_triggers())return;
                w.finish_after_presentation();
            }
        } phases(*this);
        shared_player_frame_after_movement(pool,movement,player,f2bc,collision,presentation,*this,phases);
    }

    void post_motion_terrain(){
        // F32C is the foreground MAP base; streamed metadata already stores
        // offsets from that base. Display and collision share the same backing.
        struct Services final:NativePostMotionStorageServices {
            std::uint16_t& command;
            Services(Level1EnemySlice& w,const std::size_t& origin)
                :NativePostMotionStorageServices(level1_terrain_data::post_motion_table_bytes,
                    w.backing,w.map_storage,origin,w.display),command(w.sound){}
            void post_motion_sound(std::uint16_t value)override{command=value;}
        };
        // External-resource equality checked during initialization.
        // External-resource equality checked during initialization.
        // External-resource equality checked during initialization.
        // External-resource equality checked during initialization.
        const std::size_t origin=0;Services services(*this,origin);
        const auto bank=map_storage.at(3); // MAP header bank, original F2F8.
        player_post_motion_terrain(pool.resolve(movement.controlled),movement.controlled_type,bank,services);
    }
    void finish_after_presentation(){
        if(achievement_vacuum_obtained&&pool.resolve(input.base_key).byte(52)&&input.action.c51c){achievement_events|=1u<<2;achievement_vacuum_obtained=false;}
        update_camera(camera,camera_input()); //1CB8/4D54 before948A andFCD4
        update_player_contact_blink(pool,movement.controlled,f2bc,movement.contact,blink);
        animate();
        if(level_assets.bank==1)tile_animation.step(patterns,mapping); // $1CC6 -> $FAA0, after sprite animation.
        if(level_assets.bank==6)cavern_tile_animation.step(patterns,mapping); // Original bank6 table at FC66.
        if(level_assets.bank==4)desert_tile_animation.step(patterns,mapping); // Same original publisher, bank4 table at $FC32.
        const auto& base=pool.resolve(input.base_key);
        suction_particles.step(base,pool.resolve(base.longword(84)),input.action.c51c,
            movement.contact.hit_gate_c519,movement.contact.hit_gate_c51a,movement.contact.hit_gate_c51b,camera.foreground_x,camera.foreground_y);
        update_deferred_markers(deferred,plane.word(18),plane.word(20),lifetime);
        stream(camera.foreground_x,camera.foreground_y); //1CDC/7292, before1CE8/9534
        finish_frame();
        publish_level1_status_hud(status_hud,movement.c51d,score,progress,[&](auto command){sound=command;});
        if(requested_state==0x1a6e)request_level1_world_handoff(completion,progress);
        if(completion.requested&&!achievement_completion_recorded){achievement_events|=achievement_attempt.completed(score);if(progress.selector==35&&achievement_attempt.eligible&&!achievement_attempt.life_lost&&achievement_attempt.rode_cart)achievement_events|=achievement_bit(49);achievement_completion_recorded=true;}
        if(!debug_free_flight&&achievement_attempt.eligible){const auto& controlled=pool.resolve(movement.controlled);achievement_events|=achievement_attempt.creek(progress.selector,movement.controlled_type,controlled,score);const auto tile=actor_terrain_word(terrain,controlled.word(12),controlled.word(16));achievement_events|=achievement_companion.observe(movement.controlled_type,controlled,(tile&0x2e00)==0x2200);}
        if(!debug_free_flight)achievement_events|=regional_achievement_events(achievement_previous_flags,progress.flags);achievement_previous_flags=progress.flags;
        if(transport_hooks)transport_hooks->transport_frame_returned();
    }
    // Original9534 is aftercamera/terrain publication at1CE8. Host must call this
    // after stream(), not inside the movement/animation portion above.
    void finish_frame(){
        if((movement.bounds.c516&&!movement.contact.hit_gate_c519)||(!protection&&!movement.contact.action_gate_c511&&movement.contact.action_latch_c517))achievement_attempt.hurt();
        if(achievement_attempt.damaged||!achievement_attempt.eligible)achievement_events&=~(achievement_bit(30)|achievement_bit(31)|achievement_bit(32)|achievement_bit(33));
        companions=companion_state.slots; // $9534 reads the live slots after callback attachments.
        if(resolve_player_contact(pool,{movement.contact,movement.bounds.c516,exit_latch,protection,transition,movement.c524,
            companions,movement.controlled_type,movement.controlled},*this))requested_state=0x1cee;
        companion_state.slots=companions; // $95DE injury removes the same shared C500..C508 slot.
    }
};
inline std::array<ActorDefinition,194> Level1EnemySlice::definitions{};
inline bool Level1EnemySlice::definitions_ready=false;

}





