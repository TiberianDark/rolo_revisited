#pragma once
#include "core/player_data.hpp"
#include "core/player_animation_data.hpp"
#include <algorithm>
#include <optional>

namespace rolo {
enum class SurfaceDirection {Floor,Ceiling,Left,Right};
struct Surface {int position;std::uint8_t slope;std::uint16_t tile;};
// $8728 + $879A..$880E and $85E8..$8726, over the extracted static map.
inline std::optional<Surface> player_surface(int x,int y,SurfaceDirection direction) {
    using namespace player_data;
    if(x<0||y<0||x>=width*16||y>=height*16) return std::nullopt;
    const auto tile=grid[static_cast<std::size_t>((y/16)*width+x/16)];
    if(!(tile&0x4000)) return std::nullopt;
    const bool flip=(tile&0x1000)!=0;
    int side=direction==SurfaceDirection::Floor?(flip?2:0):direction==SurfaceDirection::Ceiling?(flip?0:2):direction==SurfaceDirection::Left?6:4;
    const auto offset=static_cast<int>(collision[(tile&511)*8+side]);
    const auto slope=collision[(tile&511)*8+side+1];
    int coordinate=(direction==SurfaceDirection::Floor||direction==SurfaceDirection::Ceiling)?x:y;
    bool mirror=(slope&64)!=0;
    if(direction==SurfaceDirection::Left||direction==SurfaceDirection::Right) mirror=mirror!=flip;
    if(mirror) coordinate=~coordinate;
    const auto value=shapes[(slope&63)*16+(coordinate&15)];
    if(value>=128) return std::nullopt;
    int position=0;
    switch(direction) {
    case SurfaceDirection::Floor:position=(y&~15)+(flip?31-offset-value:15-offset+value);break;
    case SurfaceDirection::Ceiling:position=(y&~15)+(flip?offset-value:-16+offset+value);break;
    case SurfaceDirection::Left:position=(x&~15)-16+offset+value;break;
    case SurfaceDirection::Right:position=(x&~15)+15-offset+value;break;
    }
    return Surface{position,static_cast<std::uint8_t>(slope^(flip?64:0)),tile};
}
struct PlayerInput {bool left{},right{},run{},jump{};};
struct PlayerState {
    std::int32_t x{184*65536},y{752*65536},speed_x{},speed_y{};
    std::int8_t direction_x{},direction_y{};
    bool facing_left{},grounded{},jump_latched{},jumping{};
    std::uint8_t slope{};
    unsigned tick{},air_ticks{};
    std::int32_t drag{}; // $766A initializes zero; $9196 sets $3000 after the first update.
    std::uint16_t selector{};
    AnimationState body,head;AnimationRandom random;
    int pixel_x() const {return x/65536;}
    int pixel_y() const {return y/65536;}
};
inline void update_player(PlayerState& p,PlayerInput input) {
    // Normal Rolo path only: special powers, companions, damage and moving objects excluded.
    p.speed_x=std::max(0,p.speed_x-p.drag);if(!p.speed_x)p.direction_x=0;
    const bool started_jump=input.jump&&!p.jump_latched&&p.grounded;
    if(started_jump) {p.speed_y=0x65e00;p.direction_y=-1;p.grounded=false;p.jumping=true;}
    // $79D0..$79E8: mapped held-jump byte $FFC486 sustains an ascending jump.
    // The launch path returns at $7A5C, so this begins on the following update.
    else if(input.jump&&p.jumping&&p.direction_y<0)p.speed_y+=0x2ee0;
    p.jump_latched=input.jump;
    std::int32_t acceleration=0;
    const auto input_acceleration=input.run?0x10000:0x8000;
    if(input.left) {p.facing_left=true; if(p.direction_x>0)acceleration-=input_acceleration;else {p.direction_x=-1;acceleration+=input_acceleration;}}
    if(input.right) {p.facing_left=false;if(p.direction_x<0)acceleration-=input_acceleration;else {p.direction_x=1;acceleration+=input_acceleration;}}
    std::int32_t limit=0x30000;
    if(p.grounded) {
        const auto slot=p.slope&63;
        const bool reverse=((p.slope^static_cast<std::uint8_t>(p.direction_x))&64)!=0;
        const auto& table=input.run?(reverse?player_data::run_reverse:player_data::run_forward):(reverse?player_data::walk_reverse:player_data::walk_forward);
        if(slot<17) {acceleration+=table[slot*2];limit=table[slot*2+1];}
    }
    if(acceleration>=0) {if(p.speed_x<limit)p.speed_x=std::min(limit,p.speed_x+acceleration);}
    else {p.speed_x+=acceleration;if(p.speed_x<0) {p.speed_x=-p.speed_x;p.direction_x=static_cast<std::int8_t>(-p.direction_x);}}
    // $7DC6: convert horizontal whole-pixel speed along slopes into vertical motion.
    if(p.grounded&&(p.slope&63)>1) {
        const bool uphill=((p.slope^static_cast<std::uint8_t>(p.direction_x))&64)!=0;
        const auto amount=static_cast<std::int32_t>((p.slope&63)-1)*(p.speed_x>>16)*4096+(uphill?-0xa000:0x1e000);
        if(p.direction_y==0) {p.direction_y=uphill?-1:1;p.speed_y=std::min(0xf0000,amount);}
        else if((p.direction_y<0)!=uphill) {p.speed_y-=amount;if(p.speed_y<0) {p.speed_y=-p.speed_y;p.direction_y=static_cast<std::int8_t>(-p.direction_y);}}
        else p.speed_y=std::min(0xf0000,p.speed_y+amount);
    }
    // $8116: gravity uses a separate unsigned magnitude and signed direction.
    if(p.direction_y<=0) {p.speed_y-=0x6000;if(p.speed_y<0) {p.speed_y=-p.speed_y;p.direction_y=1;}}
    else p.speed_y=std::min(0xf0000,p.speed_y+0x6000);
    p.x+=p.direction_x*p.speed_x;p.y+=p.direction_y*p.speed_y;
    if(p.pixel_x()<16) {p.x=(16<<16)|(p.x&65535);p.speed_x=0;p.direction_x=0;}
    if(p.pixel_x()>=player_data::width*16-16) {p.x=((player_data::width*16-16)<<16)|(p.x&65535);p.speed_x=0;p.direction_x=0;}
    if(p.y<0)p.y=0;
    const int reach=(p.speed_x>>16)+(p.speed_y>>16)+1;
    // Ceiling probes: height 32 in this slice. $8376 probes bottom-to-top while ascending.
    const int x=p.pixel_x(),y=p.pixel_y();
    for(int probe=0;probe<3;++probe) {
        if(p.direction_y>0&&probe<2)continue;
        auto hit=player_surface(x,y-probe*16,SurfaceDirection::Ceiling);
        if(hit&&hit->position+32-y<=reach&&hit->position+32>=y) {
            p.y=(hit->position+33)*65536;p.speed_y=0;p.direction_y=0;break;
        }
    }
    // $84F4 clears ground flags; $8680 resolves the surface height and slope.
    p.grounded=false;p.slope=0;
    for(int probe=2;probe>=0;--probe) {
        if(p.direction_y<0&&probe==2&&p.speed_y>p.speed_x)continue;
        auto hit=player_surface(p.pixel_x(),p.pixel_y()-probe*16,SurfaceDirection::Floor);
        if(!hit||p.pixel_y()-hit->position>reach||hit->position>p.pixel_y())continue;
        if(p.direction_y<0&&(hit->slope&63)<(p.speed_x?((p.speed_y>>16)*16)/(p.speed_x>>16? p.speed_x>>16:1):0))continue;
        p.y=hit->position*65536;p.speed_y=0;p.direction_y=0;p.grounded=true;p.slope=hit->slope;p.jumping=false;break;
    }
    // $827A: side probes at y-8, offsets +/-8 from the anchor.
    auto wall=[&](bool right) {
        for(int offset:{right?-8:8,right?8:-8}) {
            auto hit=player_surface(p.pixel_x()+offset,p.pixel_y()-8,right?SurfaceDirection::Right:SurfaceDirection::Left);
            if(!hit)continue;
            const int boundary=hit->position+(right?-8:8);
            const int difference=right?p.pixel_x()-boundary:boundary-p.pixel_x();
            if(difference>=0&&difference<=reach) {p.x=boundary*65536;p.speed_x=0;p.direction_x=0;break;}
        }
    };
    if(p.direction_x<=0)wall(false);if(p.direction_x>=0)wall(true);
    p.air_ticks=p.grounded?0:p.air_ticks+1;
    p.selector=p.jumping?8:(!p.grounded&&p.air_ticks>=8)?12:acceleration?static_cast<std::uint16_t>(input.run?16:4):p.direction_x?20:0;
    update_animation(p.body,player_animation_data::data,0x13ecc,p.selector,static_cast<std::uint32_t>(p.speed_x),p.random,p.direction_y);
    update_animation(p.head,player_animation_data::data,0x13eee,p.selector,static_cast<std::uint32_t>(p.speed_x),p.random,p.direction_y);
    p.drag=0x3000;++p.tick;
}
} // namespace rolo
