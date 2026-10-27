#pragma once
#include "core/actor_motion.hpp"
#include "core/actor_acceleration.hpp"
#include "core/animation.hpp"
#include <stdexcept>
namespace rolo {
// D06C/D094/D0BA/D0E2: direction/magnitude acceleration. Opposing direction
// retains its sign at zero until a subsequent subtraction becomes negative.
inline void accelerate_world_bunny(ActorState& actor,unsigned axis,bool positive){
    accelerate_actor_magnitude(actor,axis,positive,0x4000,0x20000);
}
inline void roll_world_bunny_direction(ActorState& actor,AnimationRandom& random){
    actor.byte(46,static_cast<std::uint8_t>(random.between(1,9)));
    actor.word(50,random.between(40,50));
}
inline void apply_world_bunny_direction(ActorState& actor,unsigned direction){
    auto up=[&]{accelerate_world_bunny(actor,1,false);};
    auto down=[&]{accelerate_world_bunny(actor,1,true);};
    auto left=[&]{actor.byte(118,actor.byte(118)|8);accelerate_world_bunny(actor,0,false);};
    auto right=[&]{actor.byte(118,actor.byte(118)&~8u);accelerate_world_bunny(actor,0,true);};
    switch(direction){
        case 1:up();break;case 2:up();right();break;case 3:right();break;case 4:down();right();break;
        case 5:down();break;case 6:down();left();break;case 7:left();break;case 8:up();left();break;
        default:throw std::out_of_range("Unproved world bunny direction table index");
    }
}
// E7BE callback. Integration precedes clamping/acceleration; no movement is
// performed by the newly selected acceleration until the next callback.
inline void update_world_bunny(ActorState& actor,bool paused,const std::array<std::uint8_t,4>& input,
        std::uint16_t width,std::uint16_t height,AnimationRandom& random){
    actor_integrate(actor);
    auto clamp=[&](unsigned coordinate,unsigned speed,std::uint16_t lower,std::uint16_t upper){
        auto value=static_cast<std::int16_t>(actor.word(coordinate));
        const auto low=static_cast<std::int16_t>(lower),high=static_cast<std::int16_t>(upper);
        if(value<low){actor.word(coordinate,lower);actor.longword(speed,0);actor.byte(46,0);}
        else if(value>high){actor.word(coordinate,upper);actor.longword(speed,0);actor.byte(46,0);}
    };
    clamp(12,58,264,static_cast<std::uint16_t>(width-264));clamp(16,62,272,static_cast<std::uint16_t>(height-256));
    auto up=[&]{accelerate_world_bunny(actor,1,false);};auto down=[&]{accelerate_world_bunny(actor,1,true);};
    auto left=[&]{actor.byte(118,actor.byte(118)|8);accelerate_world_bunny(actor,0,false);};
    auto right=[&]{actor.byte(118,actor.byte(118)&~8u);accelerate_world_bunny(actor,0,true);};
    if(paused){if(input[0])up();if(input[1])down();if(input[2])left();if(input[3])right();return;}
    actor.word(50,static_cast<std::uint16_t>(actor.word(50)-1));
    if(static_cast<std::int16_t>(actor.word(50))<0)actor.byte(46,0);
    if(!actor.byte(46))roll_world_bunny_direction(actor,random);
    apply_world_bunny_direction(actor,actor.byte(46));
}
}
