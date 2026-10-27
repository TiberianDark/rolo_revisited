#pragma once
#include "core/player_trigger_scan.hpp"
namespace rolo {
// Resumable $925C/$926C caller: retain sampled registers across a blocking
// trigger handler, then load the live next link from that SAME node.
struct PlayerTriggerContinuation {
    std::uint16_t player_x{},player_y{},left{},right{},top{},bottom{},identity=0x6a36;
    std::size_t max_visits{},visited{};
    bool done=true;
    void begin(std::uint16_t x,std::uint16_t y,std::uint16_t reference_x,
            std::uint16_t reference_y,std::size_t limit){
        player_x=x;player_y=y;left=static_cast<std::uint16_t>(reference_x-0x170);
        right=static_cast<std::uint16_t>(reference_x+0x420);
        top=static_cast<std::uint16_t>(reference_y-0xf0);
        bottom=static_cast<std::uint16_t>(reference_y+0x2c0);
        identity=0x6a36;max_visits=limit;visited=0;done=false;
    }
    template<class Suspended>
    bool advance(PlayerTriggerServices& services,Suspended&& suspended){
        if(done)return true;
        if(suspended())return false;
        for(;;){
            const auto next=services.trigger_word(identity,2);
            if(!next){done=true;return true;}
            if(visited>=max_visits)throw std::out_of_range("Unproved native trigger list extent");
            ++visited;identity=next;
            const auto x=services.trigger_word(identity,4),y=services.trigger_word(identity,6);
            if(!marker_in_bounds(x,y,left,right,top,bottom)){
                services.release_trigger_restore_marker(identity);continue;
            }
            if(!marker_in_bounds(player_x,player_y,x,static_cast<std::uint16_t>(x+17),
                    y,static_cast<std::uint16_t>(y+17)))continue;
            if(services.trigger_byte(identity,11))left=services.consume_trigger(identity);
            const auto offset=services.trigger_word(identity,8);
            if(offset%4||offset>68)throw std::out_of_range("Unproved native trigger dispatch domain");
            services.dispatch_trigger(offset/4,identity);
            if(suspended())return false;
        }
    }
};
}
