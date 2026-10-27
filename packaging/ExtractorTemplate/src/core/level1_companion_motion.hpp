#pragma once
#include "core/level1_companions.hpp"
namespace rolo {
// $86D6/$87BC ceiling surface, distinct from the floor descriptor pair.
inline FloorProbe companion_ceiling_probe(const ActorTerrain& t,std::uint16_t x,std::uint16_t y) {
    x=static_cast<std::uint16_t>(x+t.x_shift);const auto offset=ActorTerrain::ring_offset(x,y);
    const auto tile=static_cast<std::uint16_t>((t.read(t.ring,offset)<<8)|t.read(t.ring,offset+1));if(!(tile&0x4000))return {};
    const bool flipped=tile&0x1000;const auto pair=(tile&511)*8+(flipped?0:2);
    const auto bias=t.read(t.collision,pair),shape=t.read(t.collision,pair+1);
    const auto profile=t.read(t.profiles,(shape&63)*16+(((shape&64)?static_cast<std::uint16_t>(~x):x)&15));
    if(profile&128)return {};
    return {true,static_cast<std::uint16_t>(flipped?(y&0xfff0)+bias-profile:(y&0xfff0)-16+bias+profile),shape};
}
// $CECA. Signed reach comparison followed by unsigned bottom comparison.
inline void companion_ceiling_collision(ActorState& a,const ActorTerrain& terrain) {
    if(a.byte(117))return;a.byte(125,a.byte(125)&~128u);
    const auto reach=static_cast<std::uint16_t>(a.word(58)+a.word(62));
    auto probe=companion_ceiling_probe(terrain,a.word(12),static_cast<std::uint16_t>(a.word(16)-a.word(38)+16));
    auto usable=[&]{return probe.found&&signed_word(reach)>=signed_word(static_cast<std::uint16_t>(probe.y+a.word(38)-a.word(16)));};
    if(!usable()){probe=companion_ceiling_probe(terrain,a.word(12),static_cast<std::uint16_t>(a.word(16)-a.word(38)));if(!usable())return;}
    const auto y=static_cast<std::uint16_t>(probe.y+a.word(38));if(y<a.word(16))return;
    a.word(16,y);a.word(18,0);if(static_cast<std::int8_t>(a.byte(122))>0)return;
    a.byte(122,0);a.longword(62,0);a.byte(125,a.byte(125)|128);
}
// $AE86.
inline void companion_mirror_ground(ActorState& a){
    a.byte(124,a.byte(124)&~128u);const auto bit=a.byte(124)&1,old=a.byte(125)&1;
    a.byte(125,static_cast<std::uint8_t>((a.byte(125)&254)|bit));if(bit!=old)a.byte(124,a.byte(124)|128);
}
// $AF80. The controlled46 LONG test includes bytes47..49.
inline void companion_animation_selector(ActorState& a,const ActorState& controlled){
    const auto flags=a.byte(124);std::uint16_t selector;
    if(flags&16)selector=8;else if(!(flags&1))selector=12;
    else if(!(flags&6)&&!(a.byte(46)&2)&&a.longword(58))selector=4;
    else if(!(flags&6)&&(a.byte(46)&2)){
        if(a.byte(118)!=controlled.byte(118))selector=4;
        else if(controlled.word(70)==24)selector=24;
        else if(controlled.longword(46))selector=4;
        else selector=controlled.byte(121)?20:0;
    } else selector=controlled.word(70)==24?24:0;
    a.word(70,selector);
}
// $B0D6: conditional jump, then clear49 in both branches.
inline void companion_jump(ActorState& a){
    const auto flags=a.byte(124);
    if(!(flags&16)&&a.word(70)!=24&&!a.byte(49)&&(flags&129)){
        a.byte(122,255);a.longword(62,0x85000);a.byte(124,flags|16);
    }
    a.byte(49,0);
}
inline std::uint16_t companion_history_word(const PlayerFrameHistory& history,std::uint16_t at,unsigned field){
    return static_cast<std::uint16_t>((history.records.at(at+field)<<8)|history.records.at(at+field+1));
}
// $B00A. Forward floor query can adopt only integer Y; retries sampleY+16.
inline bool companion_forward_probe(ActorState& a,const ActorTerrain& terrain){
    auto step=a.word(58);if(static_cast<std::int8_t>(a.byte(121))<0)step=static_cast<std::uint16_t>(0u-step);
    const auto x=static_cast<std::uint16_t>(a.word(12)+step);auto y=a.word(16);
    auto probe=actor_floor_probe(terrain,x,y);if(!probe.found)probe=actor_floor_probe(terrain,x,static_cast<std::uint16_t>(y+16));
    if(!probe.found)return false;
    auto delta=static_cast<std::uint16_t>(probe.y-y);if(delta&0x8000)delta=static_cast<std::uint16_t>(0u-delta);
    if(signed_word(delta)>signed_word(a.word(58)))return false;a.word(16,probe.y);return true;
}
// $AEB4: history-radius walking with signed WORD speed and selective writes.
inline void companion_follow_speed(ActorState& a,const ActorState& controlled,const PlayerFrameHistory& history,std::uint16_t at){
    auto speed=static_cast<std::uint16_t>(controlled.word(58)+2);
    if(signed_word(speed)<=2)speed=2;else if(signed_word(speed)>15)speed=15;
    std::uint16_t target;
    if(static_cast<std::int8_t>(controlled.byte(122))>0&&!(controlled.byte(124)&1)){target=controlled.word(12);speed=controlled.word(62);}
    else if(controlled.byte(124)&32)target=controlled.word(12);
    else {
        target=companion_history_word(history,at,0);
        auto delta=static_cast<std::uint16_t>(a.word(16)-companion_history_word(history,at,2));
        if(delta&0x8000)delta=static_cast<std::uint16_t>(0u-delta);
        if((a.byte(124)&1)&&signed_word(delta)<=signed_word(a.word(52))){
            const auto radius_target=static_cast<std::uint16_t>((controlled.byte(118)&8)?controlled.word(12)+a.word(52):controlled.word(12)-a.word(52));
            if((controlled.byte(118)&8)?signed_word(target)<=signed_word(radius_target):signed_word(target)>=signed_word(radius_target)){
                target=radius_target;a.byte(46,a.byte(46)|4);
            }
        }
    }
    auto distance=static_cast<std::uint16_t>(target-a.word(12));
    if(signed_word(target)<signed_word(a.word(12))){a.byte(118,a.byte(118)|8);a.byte(121,255);distance=static_cast<std::uint16_t>(0u-distance);}
    else {a.byte(118,a.byte(118)&~8u);a.byte(121,1);}
    a.byte(46,a.byte(46)&~2u);
    if(signed_word(distance)<=signed_word(speed)){speed=distance;a.byte(118,controlled.byte(118));a.byte(46,a.byte(46)|2);}
    a.word(58,speed);a.word(60,0);
}
// $ACCE, whose CD8E caller preserves the history pointer/index.
inline void companion_follow_terrain(ActorState& a,Level1CompanionServices& services,std::uint16_t at){
    const auto& controlled=services.companion_controlled();const auto& history=services.companion_history();
    const auto delta=static_cast<std::uint16_t>(companion_history_word(history,at,2)-a.word(16));
    companion_follow_speed(a,controlled,history,at);const bool radius=a.byte(46)&4;a.byte(46,a.byte(46)&~4u);
    auto stop=[&]{a.byte(121,0);a.longword(58,0);a.byte(118,controlled.byte(118));};
    if(signed_word(delta)>-8&&signed_word(delta)<0){
        if(radius){
            // $ACF4 branches straight to $AD04: walls copy facing without
            // clearing speed. Only a failed forward probe clears movement.
            if(a.byte(124)&6)a.byte(118,controlled.byte(118));
            else if(!companion_forward_probe(a,services.companion_terrain()))stop();
            return;
        }
        if((a.byte(124)&6)||(controlled.word(16)<a.word(16)&&(a.byte(124)&129)==128))companion_jump(a);return;
    }
    if(signed_word(delta)>=0){
        if(radius){if(!companion_forward_probe(a,services.companion_terrain()))stop();return;}
        if(a.byte(124)&6)companion_jump(a);return;
    }
    if(radius){if(!companion_forward_probe(a,services.companion_terrain()))stop();return;}
    if(controlled.word(16)>=a.word(16))return;
    if(a.byte(124)&6){companion_jump(a);return;}
    if(static_cast<std::int8_t>(history.records.at(at+7))>0)return;
    if(signed_word(static_cast<std::uint16_t>(a.word(16)-companion_history_word(history,at,2)))<=18)return;
    auto dx=static_cast<std::uint16_t>(companion_history_word(history,at,0)-a.word(12));if(dx&0x8000)dx=static_cast<std::uint16_t>(0u-dx);
    if(signed_word(dx)<=132)companion_jump(a);
}
// $AB28/$AB3C: grounded history-copy path or explicit terrain fallback.
inline void update_level1_ground_companion(ActorState& a,Level1ProgressState& progress,Level1CompanionServices& services){
    companion_mirror_ground(a);a.byte(46,a.byte(46)&~8u);
    const auto& history=services.companion_history();const auto& controlled=services.companion_controlled();
    const auto at=static_cast<std::uint16_t>((history.cursor-a.word(50))&1023),prior=static_cast<std::uint16_t>((at-16)&1023);
    bool copy=!services.companion_c514()&&!services.companion_f2bc()&&!(history.records.at(at+14)&32);
    if(copy&&!(a.byte(124)&16)){
        auto abs=[](std::uint16_t v){return (v&0x8000)?static_cast<std::uint16_t>(0u-v):v;};
        copy=signed_word(abs(static_cast<std::uint16_t>(a.word(16)-controlled.word(16))))>signed_word(a.word(52))||
            signed_word(abs(static_cast<std::uint16_t>(a.word(12)-controlled.word(12))))>signed_word(a.word(52));
    }
    copy=copy&&companion_history_word(history,prior,0)==a.word(12)&&companion_history_word(history,prior,2)==a.word(16);
    if(copy){
        a.byte(46,a.byte(46)|8);for(const auto [dest,field]:{std::pair{12,0},std::pair{16,2},std::pair{70,4},std::pair{58,8},std::pair{62,10}})a.word(dest,companion_history_word(history,at,field));
        a.byte(121,history.records.at(at+6));a.byte(122,history.records.at(at+7));a.byte(118,history.records.at(at+12));
        a.byte(120,0); // Absolute ROM byte00000D, pinned revision value0, not history13.
        a.byte(124,history.records.at(at+14)&~32u);companion_mirror_ground(a);
        if(static_cast<std::int8_t>(services.companion_c520())<0&&!progress.action_c510)services.companion_horizontal_collision(a);
    }else{
        if(a.byte(117)){services.companion_restore_inactive(a);if(!(a.byte(46)&8))companion_animation_selector(a,controlled);return;}
        actor_gravity(a);companion_follow_terrain(a,services,at);actor_integrate(a);
        services.companion_horizontal_collision(a);companion_ceiling_collision(a,services.companion_terrain());services.companion_land(a);
    }
    if(!(a.byte(46)&8))companion_animation_selector(a,controlled);
}
// $C920. Return value is SGE BYTE converted to Boolean, used for facing copy.
inline bool companion_horizontal_target(ActorState& a,std::uint16_t target,std::uint16_t speed){
    auto delta=static_cast<std::uint16_t>(target-a.word(12));
    // SUB.W/BLT compares original signed endpoints, including subtraction overflow.
    if(signed_word(target)<signed_word(a.word(12))){a.byte(118,a.byte(118)|8);a.byte(121,255);delta=static_cast<std::uint16_t>(0u-delta);}
    else{a.byte(118,a.byte(118)&~8u);a.byte(121,1);}
    const bool far=signed_word(delta)>=signed_word(speed);if(!far)speed=delta;
    a.word(58,speed);a.word(60,0);return far;
}
// $C86C: mode-sensitive target pursuit and jump requests.
inline void companion_pursue_target(ActorState& a,const ActorState& controlled,std::uint16_t x,std::uint16_t y){
    const auto dy=static_cast<std::uint16_t>(y-a.word(16));
    if(!companion_horizontal_target(a,x,static_cast<std::uint16_t>(controlled.word(58)+2)))a.byte(118,controlled.byte(118));
    const auto flags=a.byte(124);const auto walls=flags&6;
    if(signed_word(dy)>-16&&signed_word(dy)<16){if(walls||(flags&129)==1||(flags&129)==128)companion_jump(a);return;}
    if(signed_word(dy)>=16){if(walls)companion_jump(a);return;}
    if(walls||(flags&129)==128){companion_jump(a);return;}
    auto distance=static_cast<std::uint16_t>(x-a.word(12));if(distance&0x8000)distance=static_cast<std::uint16_t>(0u-distance);
    if(signed_word(distance)<=100)companion_jump(a);
}
inline bool companion_target_landed(ActorState& a,const CompanionHistoryTarget& target,Level1CompanionState& state){
    if(static_cast<std::int8_t>(a.byte(122))<0||target.x!=a.word(12))return false;
    if(signed_word(target.y)>signed_word(a.word(16))||signed_word(target.y)<signed_word(static_cast<std::uint16_t>(a.word(16)-a.word(62))))return false;
    const auto slot=static_cast<std::uint8_t>(a.byte(47)-1);
    if(static_cast<std::int8_t>(slot)>static_cast<std::int8_t>(state.c50e))return false;
    state.c50e=static_cast<std::uint8_t>(slot+1);a.longword(42,0xa92e);return true;
}
// $A9B0 and $AA4A, terrain recovery to the stacked-history callback A92E.
inline void update_level1_air_companion(ActorState& a,Level1CompanionState& state,Level1CompanionServices& services,bool free_follow){
    if(a.byte(117)){services.companion_restore_inactive(a);return;}
    if(free_follow)a.byte(46,a.byte(46)&0xf1);
    const auto target=level1_companion_history_target(a,services.companion_base(),services.companion_history(),services.companion_pool(),state);
    if(free_follow){
        a.byte(49,255);const auto prior=static_cast<std::uint8_t>(a.byte(47)-1);
        if(static_cast<std::int8_t>(prior)<=static_cast<std::int8_t>(state.c50e)){
            const auto p1=companion_ceiling_probe(services.companion_terrain(),target.x,static_cast<std::uint16_t>(target.y-a.word(38)));
            if(!p1.found){const auto p2=companion_ceiling_probe(services.companion_terrain(),a.word(12),static_cast<std::uint16_t>(a.word(16)-a.word(38)-16));if(!p2.found)a.byte(49,0);}
        }
    }
    actor_gravity(a);
    if(free_follow){const bool jumping=a.byte(124)&16;companion_pursue_target(a,services.companion_controlled(),target.x,target.y);if(!jumping&&(a.byte(124)&16))services.progress_sound(10);}
    else(void)companion_horizontal_target(a,target.x,static_cast<std::uint16_t>(services.companion_controlled().word(58)+2));
    actor_integrate(a);services.companion_horizontal_collision(a);companion_ceiling_collision(a,services.companion_terrain());services.companion_land(a);
    companion_animation_selector(a,services.companion_controlled());
    if(!free_follow&&(a.byte(124)&1)){a.longword(42,0xaa4a);return;}
    (void)companion_target_landed(a,target,state);
}
// $A92E: stacked follower path, then mark itself and later slots for recovery.
inline void update_level1_stacked_companion(ActorState& a,Level1CompanionState& state,Level1CompanionServices& services){
    const auto& base=services.companion_base();const auto target=level1_companion_history_target(a,base,services.companion_history(),services.companion_pool(),state);
    a.word(12,target.x);a.word(16,target.y);a.byte(118,target.facing);a.word(70,target.selector);
    a.byte(121,base.byte(121));a.longword(58,base.longword(58));a.byte(122,base.byte(122));a.longword(62,base.longword(62));
    services.companion_horizontal_collision(a);companion_ceiling_collision(a,services.companion_terrain());
    if(!(a.byte(124)&6)&&!(a.byte(125)&128))return;
    const auto slot=a.byte(47);if(!slot||slot>3)throw std::out_of_range("Unbound stacked companion slot");
    state.c50e=static_cast<std::uint8_t>(slot-1);
    for(unsigned i=slot-1;i<3;++i)if(state.slots[i]){auto& follower=services.companion_pool().resolve(state.slots[i]);follower.longword(42,0xa9b0);follower.byte(124,follower.byte(124)&~1u);}
}
// $ADD0/$ADFC: overflow-slot detached companion still follows original escape AI.
inline void update_level1_detached_companion(ActorState& a,Level1CompanionServices& services){
    a.byte(116,a.byte(117)?255:0);actor_gravity(a);const auto& controlled=services.companion_controlled();
    const bool initialized=a.byte(46)&1;a.byte(46,a.byte(46)|1);
    if(!initialized){a.word(52,0);a.byte(124,static_cast<std::uint8_t>((a.byte(124)|1)&0xf9));a.byte(121,controlled.byte(121)^254);
        a.byte(118,a.byte(118)&~8u);if(static_cast<std::int8_t>(a.byte(121))<=0)a.byte(118,a.byte(118)|8);}
    auto speed=static_cast<std::uint16_t>(controlled.word(58)+2);if(signed_word(speed)>15)speed=15;a.word(58,speed);
    if(!(a.byte(124)&16)){
        bool jump=false;
        if(a.byte(124)&6){const auto previous=a.word(52);a.word(52,a.word(12));if(previous==a.word(12)){a.byte(121,static_cast<std::uint8_t>(0u-a.byte(121)));a.byte(118,a.byte(118)^8);}else jump=true;}
        if(jump||(a.byte(124)&129)==128)companion_jump(a);
    }
    actor_integrate(a);services.companion_horizontal_collision(a);companion_ceiling_collision(a,services.companion_terrain());services.companion_land(a);
    a.byte(46,a.byte(46)&0xf1);companion_animation_selector(a,controlled);
}
// $B058. Early X rejection writes the incoming D2 word to Y, not history Y.
// The caller must supply that preserved value; deriving it from a guessed Y
// would silently change original behaviour.
inline void restore_level1_inactive_companion(ActorState& a,Level1CompanionState& state,
        Level1CompanionServices& services,std::uint16_t incoming_d2){
    const auto& history=services.companion_history();const auto at=static_cast<std::uint16_t>((history.cursor-a.word(50))&1023);
    const auto x=companion_history_word(history,at,0);auto y=incoming_d2;
    auto camera=services.reward_camera_x();
    bool inside=signed_word(x)>signed_word(camera)&&signed_word(x)<signed_word(static_cast<std::uint16_t>(camera+320));
    if(inside){y=companion_history_word(history,at,2);camera=services.reward_camera_y();inside=signed_word(y)>signed_word(camera)&&signed_word(y)<signed_word(static_cast<std::uint16_t>(camera+224));}
    if(!inside){a.word(12,x);a.word(16,y);return;}
    if(!(a.byte(117)&14)&&!(a.byte(124)&1)){actor_gravity(a);actor_integrate(a);return;}
    a.longword(42,0xa8bc);detach_level1_companion(a,state,services.companion_pool());a.byte(125,a.byte(125)|4);
}
}
