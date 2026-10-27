#pragma once
#include "core/entrance.hpp"
#include "core/actor_motion.hpp"
#include "core/text_tile_publication.hpp"
namespace rolo {
inline void walk_entrance_actor(ActorState&a,std::uint16_t stop,std::uint16_t idle){EntranceObject object;object.x=a.longword(12);walk_entrance(object,stop,idle);a.longword(12,object.x);a.word(70,object.selector);}
inline bool entrance_actor_ready(ActorState&a){auto delay=a.word(50);const auto ready=entrance_delay_ready(delay);a.word(50,delay);return ready;}
inline void step_entrance_elephant(ActorState&a){walk_entrance_actor(a,278,60);}
inline void step_entrance_rabbit(ActorState&a){if(entrance_actor_ready(a))walk_entrance_actor(a,320,0);}
inline void step_entrance_squirrel(ActorState&a){if(!entrance_actor_ready(a))return;actor_gravity(a);actor_integrate(a);a.word(70,12);if(signed_word(a.word(16))>=241){a.word(16,241);a.word(70,0);}}
inline void step_entrance_beaver(ActorState&a){if(!entrance_actor_ready(a))return;const auto x=a.longword(12)+a.longword(58);a.longword(12,x>=0x00ae0000u?0x00ae0000u:x);const auto y=a.longword(16)-a.longword(62);a.longword(16,y<=0x00ed0000u?0x00ed0000u:y);}
inline void reset_campaign_flags(std::span<std::uint8_t>flags,std::uint8_t unlock){if(flags.size()<80)throw std::out_of_range("Campaign flags extent");for(unsigned i=0;i<80;++i)flags[i]=unlock?1:0;flags[1]|=1;}
inline void publish_entrance_planes(std::span<const std::uint8_t>rom,TextTilePorts&p){for(unsigned layer=0;layer<2;++layer){const auto source=layer?0x2c3a0u:0x2bf40u;if(source+1120>rom.size())throw std::out_of_range("Entrance plane ROM extent");std::array<std::uint16_t,560>tiles;for(unsigned i=0;i<560;++i)tiles[i]=std::uint16_t((rom[source+i*2]<<8)|rom[source+i*2+1]);(void)publish_text_rectangle(tiles,layer?0xc300:0xe300,layer?0x80aa:0xaa,39,13,p);}}
}
