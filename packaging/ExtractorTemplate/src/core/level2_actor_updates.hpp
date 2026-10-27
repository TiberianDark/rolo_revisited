#pragma once
#include "core/actor_motion.hpp"
#include "core/actor_horizontal_collision.hpp"
namespace rolo {
// $CD7A: signed LONG deceleration retains direction unless speed crosses zero.
inline void actor_decelerate(ActorState& actor){
    const auto speed=actor.longword(58)-0x3000u;
    if(signed_long(speed)<0){actor.longword(58,0);actor.byte(121,0);}
    else actor.longword(58,speed);
}
// $D1CA..$D2E0. Original trunk pull thresholds 32/64/96 and actor/head
// mutation; all positions and magnitude fields remain wrapped WORD values.
template<class World> void update_trunk_pull(std::uint32_t key,World& w){
    auto& a=w.pool.resolve(key);auto& base=w.pool.resolve(w.input.base_key);
    auto& head=w.pool.resolve(base.longword(84));if(!base.byte(52))return;
    const auto level=w.input.action.c51c;
    if(level<1||level>3)throw std::out_of_range("Original trunk strength table domain");
    const auto radius=static_cast<std::uint16_t>((level-1)*4);
    auto vertical=static_cast<std::uint16_t>(base.word(16)+head.word(34)-17);
    w.target_y_c498=vertical;vertical=static_cast<std::uint16_t>(vertical-radius);
    if(signed_word(a.word(16))<signed_word(vertical))return;
    auto upper=static_cast<std::uint16_t>(a.word(16)-a.word(38)+1);
    vertical=static_cast<std::uint16_t>(vertical+15+radius*2);
    if(signed_word(upper)>signed_word(vertical))return;
    std::uint16_t distance;
    if(!(base.byte(118)&8)){
        w.target_x_c494=static_cast<std::uint16_t>(base.word(12)+15+head.word(32));
        if(signed_word(a.word(12))<signed_word(w.target_x_c494))return; // SUB.W/BLT includes overflow.
        distance=static_cast<std::uint16_t>(a.word(12)-w.target_x_c494);
    }else{
        w.target_x_c494=static_cast<std::uint16_t>(head.word(12)-15-head.word(32));
        if(signed_word(w.target_x_c494)<signed_word(a.word(12)))return; // SUB.W/BLT includes overflow.
        distance=static_cast<std::uint16_t>(w.target_x_c494-a.word(12));
    }
    if(signed_word(distance)<14){
        if(signed_word(distance)<=-18||head.byte(46))return;
        head.byte(46,255);base.byte(52,0);a.byte(125,a.byte(125)|0x22);
        a.longword(42,0xb440);w.held.held=key;return;
    }
    if(signed_word(distance)>level*32)return;
    a.byte(121,(base.byte(118)&8)?1:255);a.word(58,3);
    auto speed=static_cast<std::uint16_t>(w.target_y_c498+14-a.word(16));
    std::uint8_t direction=1;
    if(signed_word(speed)<0){speed=2;direction=255;}
    a.byte(122,direction);a.word(62,speed);a.word(64,0);
}
// $B3C4..$B3F2: passive enemy. CD8E gravity precedes CFCE integration.
template<class World> void update_passive_enemy(std::uint32_t key,World& w){
    auto& a=w.pool.resolve(key);if(a.byte(117))return;
    w.enemy.object_contact(a);if(w.enemy.player_contact(a))w.enemy.player_damage(a);
    update_trunk_pull(key,w);actor_decelerate(a);actor_gravity(a);actor_integrate(a);w.enemy.land(a);
    actor_horizontal_collision(a,w.terrain);
}
// $B3F2..$B43E: roaming enemy, shared combat, trunk pull and motion order.
template<class World> void update_roaming_enemy(std::uint32_t key,World& w){
    auto& a=w.pool.resolve(key);if(a.byte(117))return;
    w.enemy.object_contact(a);if(w.enemy.player_contact(a))w.enemy.player_damage(a);
    if(signed_word(a.word(58))<=1){
        a.word(58,1);w.enemy.choose_direction(a);a.byte(121,(a.byte(118)&8)?255:1);
    }
    update_trunk_pull(key,w);actor_decelerate(a);actor_gravity(a);actor_integrate(a);w.enemy.land(a);
}
// $B440: captured enemy follows the original base head until released.
template<class World> void update_captured_enemy(ActorState& a,World& w){
    auto& base=w.pool.resolve(w.input.base_key);auto& head=w.pool.resolve(base.longword(84));
    auto x=static_cast<std::uint16_t>(head.word(32)+12);if(base.byte(118)&8)x=static_cast<std::uint16_t>(0-x);
    a.word(12,static_cast<std::uint16_t>(base.word(12)+x));
    a.word(16,static_cast<std::uint16_t>(base.word(16)+head.word(34)-3));a.byte(118,base.byte(118));
}
// $B498..$B564: thrown actor, wall turnaround and delayed callback restoration.
template<class World> void update_thrown_enemy(std::uint32_t key,World& w,bool waiting){
    auto& a=w.pool.resolve(key);
    if(waiting){
        update_trunk_pull(key,w);actor_decelerate(a);actor_integrate(a);actor_gravity(a);w.enemy.land(a);
        a.word(46,static_cast<std::uint16_t>(a.word(46)-1));
        if(!a.word(46)){a.longword(42,w.definition(a.longword(4)).longword(12));a.byte(119,a.byte(119)&~16u);return;}
        if(signed_word(a.word(46))<=50&&(a.byte(124)&1)){a.byte(122,255);a.word(62,2);}return;
    }
    if(a.byte(117))return;const auto& d=w.definition(a.longword(4));
    if(!(d.byte(26)&128))a.byte(119,a.byte(119)|16);
    bool turn=false;
    if(signed_word(a.word(12))<8){a.word(12,8);turn=true;}
    else if(signed_word(a.word(12))>signed_word(static_cast<std::uint16_t>(w.width-8))){a.word(12,static_cast<std::uint16_t>(w.width-8));turn=true;}
    else{actor_decelerate(a);actor_gravity(a);actor_integrate(a);w.enemy.land(a);actor_horizontal_collision(a,w.terrain);turn=(a.byte(124)&6)!=0;}
    if(turn)a.byte(121,static_cast<std::uint8_t>(0-a.byte(121)));
    if(a.byte(121))return;a.byte(126,a.byte(126)|4);
    if(d.byte(26)&128)a.longword(42,d.longword(12));
    else{a.longword(42,0xb51e);a.word(46,250);}
}
// $7C74/$7CA8: duck wall action and squirrel wall attachment.
inline void update_companion_action(ActorState& a,std::uint16_t type,const ActorTerrain& terrain){
    if(type==8){
        const auto wall=(a.byte(118)&8)?2:4;
        if((a.byte(124)&1)&&(a.byte(124)&wall)){a.byte(126,a.byte(126)|2);a.word(70,52);return;}
        if(a.byte(53)){const auto old=a.byte(126);a.byte(126,old&~2u);if(old&2)a.word(70,0);}return;
    }
    if(type!=16)throw std::out_of_range("Companion action type");
    if(a.byte(122)&128)return;
    const auto x=a.word(12),y=static_cast<std::uint16_t>(a.word(16)-8);const bool left=a.byte(118)&8;
    auto probe=player_wall_probe(terrain,static_cast<std::uint16_t>(left?x-8:x+8),y,left);
    if(!probe.found)probe=player_wall_probe(terrain,static_cast<std::uint16_t>(left?x-24:x+24),y,left);
    if(!probe.found)return;const auto target=static_cast<std::uint16_t>(left?probe.x+8:probe.x-8);
    const auto distance=static_cast<std::uint16_t>(left?x-target:target-x);
    if(signed_word(distance)<0||signed_word(distance)>2)return;
    a.word(12,target);a.byte(125,a.byte(125)|8);a.byte(124,(a.byte(124)&0xaf)|1);a.byte(122,0);a.longword(62,0);
}
}
