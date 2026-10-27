#pragma once
#include "core/actor_markers.hpp"
namespace rolo {
struct PlayerTriggerServices {
    virtual ~PlayerTriggerServices()=default;
    virtual std::uint16_t trigger_word(std::uint16_t identity,unsigned offset)=0;
    virtual std::uint8_t trigger_byte(std::uint16_t identity,unsigned offset)=0;
    virtual void release_trigger_restore_marker(std::uint16_t identity)=0; //4ADC preserves A1.
    virtual std::uint16_t consume_trigger(std::uint16_t identity)=0; //4AF4 returns A1 lowword, NOT preserved.
    virtual void dispatch_trigger(unsigned slot,std::uint16_t identity)=0;
};
// $925C..$92F2: sampled player coordinates, live links and original A1 mutation.
inline void scan_player_triggers(std::uint16_t player_x,std::uint16_t player_y,
        std::uint16_t reference_x,std::uint16_t reference_y,std::size_t max_visits,PlayerTriggerServices& services) {
    auto left=static_cast<std::uint16_t>(reference_x-0x170);
    const auto right=static_cast<std::uint16_t>(reference_x+0x420);
    const auto top=static_cast<std::uint16_t>(reference_y-0xf0),bottom=static_cast<std::uint16_t>(reference_y+0x2c0);
    auto identity=std::uint16_t{0x6a36};
    for(std::size_t visited=0;;++visited) {
        const auto next=services.trigger_word(identity,2);if(!next)return;
        if(visited>=max_visits)throw std::out_of_range("Unproved native trigger list extent");
        identity=next;const auto x=services.trigger_word(identity,4),y=services.trigger_word(identity,6);
        if(!marker_in_bounds(x,y,left,right,top,bottom)){services.release_trigger_restore_marker(identity);continue;}
        if(!marker_in_bounds(player_x,player_y,x,static_cast<std::uint16_t>(x+17),y,static_cast<std::uint16_t>(y+17)))continue;
        if(services.trigger_byte(identity,11))left=services.consume_trigger(identity);
        const auto offset=services.trigger_word(identity,8);
        if(offset%4||offset>68)throw std::out_of_range("Unproved native trigger dispatch domain");
        services.dispatch_trigger(offset/4,identity);
        // Next link is read from the same record AFTER consume/dispatch mutations.
    }
}
}
