#pragma once
#include "core/actor_state.hpp"
#include <array>
#include <cstdint>
#include <stdexcept>
namespace rolo {
struct WorldRouteDescriptor {std::uint32_t pointer{};std::uint8_t negate_x{},negate_y{};};
struct WorldRouteState {
    std::uint8_t pause{},negate_x{},negate_y{};
    std::uint32_t pointer{};
    std::uint16_t anchor_x=280,anchor_y=472,snapshot_x=280,snapshot_y=472;
};
struct WorldRouteServices {
    virtual ~WorldRouteServices()=default;
    virtual std::uint16_t route_tile(std::uint16_t,std::uint16_t)=0; //8728
    virtual bool route_section_available(std::uint16_t,std::uint16_t)=0; //A368/C558 bit0
    virtual WorldRouteDescriptor route_descriptor(unsigned)=0; //A22C six-byte records
    virtual std::uint8_t route_byte(std::uint32_t)=0;
};
// A204: signed WORD rejection before DIVU remainder; not the quotient.
inline int world_route_group(std::uint16_t tile){
    const auto index=static_cast<std::uint16_t>((tile&511)-28);
    if(static_cast<std::int16_t>(index)<0||static_cast<std::int16_t>(index)>95)return -1;
    return (index%8)*24;
}
inline void load_world_route(WorldRouteState& state,const WorldRouteDescriptor& descriptor){
    state.pointer=descriptor.pointer;state.negate_x=descriptor.negate_x;state.negate_y=descriptor.negate_y;
}
// A18A checks the candidate group's permission, then loads fixed group0090.
// No byte is consumed in this call; the next substep performs movement.
inline void admit_world_route(ActorState& actor,WorldRouteState& state,
        const std::array<std::uint8_t,4>& directions,WorldRouteServices& services){
    auto x=static_cast<std::int16_t>(actor.word(12)),y=static_cast<std::int16_t>(actor.word(16));
    auto cell=[](std::int16_t value){return static_cast<std::uint16_t>(value>=0?value/16:-((-int(value)+15)/16));};
    auto cx=cell(x),cy=cell(y);int direction=-1;
    if(directions[0]){direction=0;--cy;}else if(directions[1]){direction=6;++cy;}
    else if(directions[2]){direction=12;--cx;}else if(directions[3]){direction=18;++cx;}
    if(direction<0)return;
    const auto group=world_route_group(services.route_tile(static_cast<std::uint16_t>(cx<<4),static_cast<std::uint16_t>(cy<<4)));
    if(group<0||!services.route_descriptor(static_cast<unsigned>(group+direction)).pointer)return;
    load_world_route(state,services.route_descriptor(static_cast<unsigned>(144+direction)));
}
// A0E8: both bytes are zero-extended. Only the FIRST byte has a negative
// terminator test; a Y byte80 is magnitude128, not a signed -128 delta.
inline void consume_world_route(ActorState& actor,WorldRouteState& state,
        const std::array<std::uint8_t,4>& directions,WorldRouteServices& services){
    state.anchor_x=actor.word(12);state.anchor_y=actor.word(16);
    if(!state.pointer){admit_world_route(actor,state,directions,services);return;}
    auto dx=std::uint16_t(services.route_byte(state.pointer));
    if(dx&128){actor.word(70,0);actor.word(48,0);state.pointer=0;return;}
    if(dx){actor.word(70,4);actor.byte(118,actor.byte(118)&~8u);
        if(state.negate_x){dx=static_cast<std::uint16_t>(-dx);actor.byte(118,actor.byte(118)|8);}}
    auto dy=std::uint16_t(services.route_byte(state.pointer+1));
    if(dy){actor.word(70,12);if(state.negate_y){dy=static_cast<std::uint16_t>(-dy);actor.word(70,8);}}
    state.pointer+=2;actor.word(12,static_cast<std::uint16_t>(actor.word(12)+dx));
    actor.word(16,static_cast<std::uint16_t>(actor.word(16)+dy));
    const auto desired=actor.word(70);if(desired==actor.word(48))return;
    actor.word(70,actor.word(48));actor.word(46,static_cast<std::uint16_t>(actor.word(46)-1));
    if(actor.word(46))return;
    actor.word(70,desired);actor.word(48,desired);actor.word(46,2);
}
// A02A: preserve BMI's subtraction N flag (including overflow), followed by
// BGT's signed comparison. X transitions take precedence over Y transitions.
inline void step_world_route(ActorState& actor,WorldRouteState& state,
        const std::array<std::uint8_t,4>& directions,WorldRouteServices& services){
    if(actor.byte(117))return;
    auto x=actor.word(12),y=actor.word(16);
    const auto cell_x=static_cast<std::uint16_t>(x&0xfff0),old_x=static_cast<std::uint16_t>(state.anchor_x&0xfff0);
    const auto cell_y=static_cast<std::uint16_t>(y&0xfff0),old_y=static_cast<std::uint16_t>(state.anchor_y&0xfff0);
    int direction=-1;
    if(static_cast<std::uint16_t>(cell_x-old_x)&0x8000)direction=12;
    else if(static_cast<std::int16_t>(cell_x)>static_cast<std::int16_t>(old_x))direction=18;
    else if(cell_y!=old_y)direction=(static_cast<std::uint16_t>(cell_y-old_y)&0x8000)?0:6;
    if(direction>=0){
        if(!services.route_section_available(x,y)){
            x=state.anchor_x;y=state.anchor_y;actor.word(12,x);actor.word(16,y);
            constexpr std::array<unsigned,4> reverse{6,0,18,12};direction=reverse[direction/6];
        }
        state.anchor_x=x;state.anchor_y=y;
        const auto group=world_route_group(services.route_tile(x,y));if(group<0)return;
        load_world_route(state,services.route_descriptor(static_cast<unsigned>(group+direction)));
    }
    consume_world_route(actor,state,directions,services);
}
// 9FEE: clear70 even when paused; run EXACTLY two calls, each with temporary
// integer Y-2 and subsequent snapshot. Fraction words14/18 are untouched.
inline void update_world_route(ActorState& actor,WorldRouteState& state,
        const std::array<std::uint8_t,4>& directions,WorldRouteServices& services){
    actor.word(70,0);if(state.pause)return;
    for(unsigned n=0;n<2;++n){actor.word(16,static_cast<std::uint16_t>(actor.word(16)-2));
        step_world_route(actor,state,directions,services);actor.word(16,static_cast<std::uint16_t>(actor.word(16)+2));
        state.snapshot_x=actor.word(12);state.snapshot_y=actor.word(16);}
}
}
