#pragma once
#include "core/actor_allocation.hpp"
#include "core/player_frame_history.hpp"
#include "core/level1_progress.hpp"
#include "core/actor_motion.hpp"
#include "core/level1_collectibles.hpp"
#include "core/actor_terrain.hpp"
namespace rolo {
struct Level1CompanionState {std::array<std::uint32_t,3> slots{};std::uint8_t c50e{},c50f{};};
struct CompanionHistoryTarget {std::uint16_t x{},y{},selector{},offset{};std::uint8_t facing{};};
// $B114. Slot distances are sixteen-byte history records; prior companions'
// heights create vertical stacking. Base124bit5 overrides only X and Y.
inline CompanionHistoryTarget level1_companion_history_target(const ActorState& actor,
        const ActorState& base,const PlayerFrameHistory& history,ActorPool& pool,const Level1CompanionState& state) {
    const auto offset=static_cast<std::uint16_t>((history.cursor-(std::uint16_t(actor.byte(47))<<4))&1023);
    auto word=[&](unsigned at){return static_cast<std::uint16_t>((history.records.at(offset+at)<<8)|history.records.at(offset+at+1));};
    const auto slot=actor.byte(47);std::uint16_t stack=0;
    if(slot>=2){
        if(slot>4)throw std::out_of_range("Unbound companion history slot domain");
        for(unsigned i=0;i<unsigned(slot-1);++i)if(state.slots.at(i))stack=static_cast<std::uint16_t>(stack+pool.resolve(state.slots[i]).word(38)-4);
    }
    auto selector=word(4);if(selector!=24&&selector!=8&&selector!=12)selector=28;
    return {(base.byte(124)&32)?base.word(12):word(0),
        static_cast<std::uint16_t>(((base.byte(124)&32)?base.word(16):word(2))-base.word(38)+4-stack),
        selector,offset,history.records.at(offset+12)};
}
// $B1A8. The callback comes from D2, not a hardcoded follow mode.
inline void set_level1_companion_callbacks(Level1CompanionState& state,ActorPool& pool,std::uint32_t callback) {
    state.c50e=0;for(auto key:state.slots)if(key)pool.resolve(key).longword(42,callback);
}
// $B28E: detach and compact slots, retaining exact per-slot distance decrement.
inline void detach_level1_companion(ActorState& actor,Level1CompanionState& state,ActorPool& pool) {
    auto index=static_cast<std::uint8_t>(actor.byte(47)-1);if(index&128)return;
    actor.byte(47,0);if(index>=3)throw std::out_of_range("Unbound companion detach slot");
    unsigned at=index;
    while(at<2&&state.slots[at+1]) {
        const auto key=state.slots[at+1];auto& next=pool.resolve(key);
        next.byte(47,static_cast<std::uint8_t>(next.byte(47)-1));
        next.word(50,static_cast<std::uint16_t>(next.word(50)-192));next.word(52,static_cast<std::uint16_t>(next.word(52)-24));
        state.slots[at++]=key;
    }
    state.slots[at]=0;
}
// $B1D6: rescue first, then append; when full retire oldest to ADD0 and shift.
inline void attach_level1_companion(std::uint32_t key,ActorPool& pool,Level1CompanionState& state,
        Level1ProgressState& progress,Level1ProgressServices& services) {
    auto& actor=pool.resolve(key);release_level1_companion(actor,progress,services);
    unsigned at=0;while(at<3&&state.slots[at])++at;
    if(at==3){
        auto& first=pool.resolve(state.slots[0]);first.longword(42,0xadd0);first.byte(125,first.byte(125)|4);first.byte(47,0);
        for(unsigned i=0;i<2;++i){const auto next=state.slots[i+1];auto& follower=pool.resolve(next);
            follower.byte(47,static_cast<std::uint8_t>(i+1));follower.word(50,static_cast<std::uint16_t>((i+1)*192));
            follower.word(52,static_cast<std::uint16_t>((i+1)*24));state.slots[i]=next;}
        at=2;
    }
    state.slots[at]=key;actor.byte(47,static_cast<std::uint8_t>(at+1));
    actor.word(50,static_cast<std::uint16_t>((at+1)*192));actor.word(52,static_cast<std::uint16_t>((at+1)*24));
    actor.byte(114,0);actor.longword(42,state.c50f?0xaa4a:0xab28);
    actor.byte(124,static_cast<std::uint8_t>((actor.byte(124)|1)&0xf9));
}
struct Level1CompanionServices:Level1ProgressServices {
    virtual ActorPool& companion_pool()=0;
    virtual ActorState& companion_controlled()=0;
    virtual void companion_land(ActorState&)=0;
    virtual bool companion_contact(ActorState&)=0;
    virtual ActorState& companion_base()=0;
    virtual const ActorTerrain& companion_terrain()=0;
    virtual PlayerFrameHistory& companion_history()=0;
    virtual void companion_horizontal_collision(ActorState&)=0; // CE14 includes8488.
    virtual std::uint8_t companion_c514()=0;
    virtual std::uint8_t companion_f2bc()=0;
    virtual std::uint8_t companion_c520()=0;
    virtual void companion_restore_inactive(ActorState&)=0; // B058 with caller's preserved D2 domain.
};
// $A8BC..$A92E. The linked-definition CMPI flags are overwritten by TST C550.
inline void update_level1_waiting_companion(std::uint32_t key,Level1CompanionState& state,
        Level1ProgressState& progress,Level1CompanionServices& services) {
    auto& pool=services.companion_pool();auto& actor=pool.resolve(key);
    actor.byte(121,0);actor.longword(58,0);actor.word(70,0);if(actor.byte(117))return;
    actor_gravity(actor);actor_integrate(actor);services.companion_land(actor);
    if(!progress.rescued_c552&&actor.longword(84)&&!progress.key_c550)return;
    if(progress.action_c510||!services.companion_contact(actor))return;
    if(state.c50f&&static_cast<std::int8_t>(state.c50e)>=3)set_level1_companion_callbacks(state,pool,0xa9b0);
    attach_level1_companion(key,pool,state,progress,services);
}
// $B2D2: the container actor uses ordinary gravity, integration and landing.
inline void update_level1_companion_container(ActorState& actor,Level1CompanionServices& services) {
    if(actor.byte(117))return;actor_gravity(actor);actor_integrate(actor);services.companion_land(actor);
}
// $B7B8 falls through B7C0 after SNE retirement from117.
inline void update_released_companion_container(ActorState& actor,AnimationRandom& random) {
    actor.byte(116,actor.byte(117)?255:0);update_collected_item(actor,random);
}
// $A84E: base Rolo remains a live waiting actor while a companion is controlled.
// Presenter must perform8838 with temporary C4E0=base,C510/C519/C51B=zero,
// then restore those globals in the original order; no silent presentation stub.
template<class Presenter>
inline void update_level1_uncontrolled_rolo(std::uint32_t key,Level1CompanionState& state,
        Level1ProgressState& progress,std::uint8_t c513,Level1CompanionServices& services,Presenter&& presenter){
    update_level1_waiting_companion(key,state,progress,services);auto& actor=services.companion_pool().resolve(key);
    if(c513&&signed_long(actor.longword(62))>0x10000)actor.longword(62,0x10000);
    presenter();
}
}
