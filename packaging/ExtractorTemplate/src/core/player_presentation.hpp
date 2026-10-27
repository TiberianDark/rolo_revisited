#pragma once
#include "core/player_selector.hpp"
#include "core/actor_allocation.hpp"
namespace rolo {
struct PlayerPresentationState {PlayerSelectorGlobals selector;std::uint8_t c51a{},c512{};std::uint16_t idle_countdown{};};
struct PlayerPresentationServices {
    virtual ~PlayerPresentationServices()=default;
    virtual std::uint32_t head_offset_for_selector(std::int16_t)=0; // ROM table1045C, caller domain required.
    virtual void alternate_player_presentation()=0; // Native EFA8 tail call.
};
// $8838..$8934. Controlled and base actors are intentionally separate identities.
inline void update_player_presentation(ActorPool& pool,std::uint32_t controlled_key,
        std::uint32_t base_key,PlayerPresentationState& state,PlayerPresentationServices& services) {
    auto& controlled=pool.resolve(controlled_key);
    if(!(controlled.byte(126)&2)) {
        const auto flags124=controlled.byte(124),flags125=controlled.byte(125);
        controlled.word(70,player_animation_selector(controlled,state.selector,flags124,flags125));
    }
    auto& base=pool.resolve(base_key);auto& head=pool.resolve(base.longword(84));
    head.byte(125,static_cast<std::uint8_t>(head.byte(125)&~16u));
    head.word(12,base.word(12));head.word(16,base.word(16));
    for(const auto offset:{118,121,122})head.byte(offset,base.byte(offset));
    const auto combined=static_cast<std::uint8_t>(state.selector.c519+state.c51a+state.selector.c51b);
    bool reset_idle=false;
    if(combined) {head.word(70,base.word(70));reset_idle=true;}
    else {
        bool offsets=(head.byte(126)&2)!=0;
        if(!offsets) {
            head.word(70,base.word(70));
            if(!state.selector.c520) {
                if(head.byte(46)){head.word(70,56);offsets=true;}
                else if(base.byte(52)){head.word(70,52);offsets=true;}
            }
        }
        if(offsets) {
            head.byte(125,static_cast<std::uint8_t>(head.byte(125)|16));
            head.longword(32,services.head_offset_for_selector(signed_word(base.word(70))));
        }
        if(state.selector.c510)return;
        if(base.word(70)!=head.word(70)||base.word(70))reset_idle=true;
        else {
            state.idle_countdown=static_cast<std::uint16_t>(state.idle_countdown-1);
            if(signed_word(state.idle_countdown)<0) {
                base.word(70,60);head.word(70,60);state.idle_countdown=0;
            }
        }
    }
    if(reset_idle) {
        state.idle_countdown=250;
        if(state.c512)services.alternate_player_presentation();
    }
}
}
