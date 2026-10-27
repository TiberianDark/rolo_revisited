#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct PlayerSlopeMotion {std::uint32_t acceleration{},limit{};};
struct PlayerAccelerationServices {
    virtual ~PlayerAccelerationServices()=default;
    virtual PlayerSlopeMotion slope_motion(std::uint8_t slot,bool reverse)=0; // C502/C506 live tables.
};
// $7D3A..$7DC6.
inline void player_acceleration(ActorState& actor,PlayerAccelerationServices& services) {
    std::uint32_t limit=0x30000,acceleration=0,speed=actor.longword(58);
    bool start_from_slope=false;
    if(actor.byte(124)&1) {
        const auto slope=actor.byte(120);
        const bool reverse=((slope^actor.byte(121))&64)!=0;
        const auto motion=services.slope_motion(static_cast<std::uint8_t>(slope&63),reverse);
        limit=motion.limit;acceleration=motion.acceleration;
        if(acceleration&&!actor.byte(121)) {
            if(signed_long(acceleration)<0)acceleration=0u-acceleration;
            actor.byte(121,(slope&64)?255:1);speed=0;start_from_slope=true;
        }
    }
    if(!start_from_slope)acceleration+=actor.longword(46);
    if(start_from_slope||signed_long(acceleration)>=0) {
        if(signed_long(speed)>=signed_long(limit))return;
        speed+=acceleration;
        if(signed_long(speed)>=signed_long(limit))speed=limit;
    } else {
        speed+=acceleration;
        if(signed_long(speed)<0) {
            actor.byte(121,static_cast<std::uint8_t>(0u-actor.byte(121)));speed=0u-speed;
        }
    }
    actor.longword(58,speed);
}
// $7DC6..$7E58. Literal word multiply, SWAP and arithmetic long shift.
inline void player_slope_vertical_motion(ActorState& actor,std::uint8_t c514) {
    if(c514||!(actor.byte(124)&1)||(actor.byte(124)&16))return;
    const auto slope=actor.byte(120);const auto shape=static_cast<int>(slope&63)-1;
    if(shape<=0)return;
    const auto xor_flags=static_cast<std::uint8_t>((slope^actor.byte(121))<<1);
    auto amount=static_cast<std::uint32_t>(shape)*actor.word(58);
    amount=(amount<<16)|(amount>>16);
    amount=(amount>>4)|((amount&0x80000000u)?0xf0000000u:0);
    amount+=(xor_flags&128)?0u-0xa000u:0x1e000u;
    const auto direction=actor.byte(122);std::uint32_t speed=actor.longword(62);
    if(!direction) {
        speed=0;actor.byte(122,(xor_flags&128)?255:1);
    } else if((direction^xor_flags)&128) {
        speed-=amount;
        if(signed_long(speed)<0) {speed=0u-speed;actor.byte(122,static_cast<std::uint8_t>(0u-direction));}
        actor.longword(62,speed);return;
    }
    speed+=amount;if(signed_long(speed)>0xf0000)speed=0xf0000;
    actor.longword(62,speed);
}
}
