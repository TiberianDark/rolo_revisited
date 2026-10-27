#pragma once
#include "core/actor_choreography_chain.hpp"
#include "core/animation.hpp"
namespace rolo {
inline constexpr std::array<std::uint32_t,9>choreography_spawn_definitions{0x1443e,0x14394,0x14460,0x14394,0x14460,0x1443e,0x14460,0x1443e,0x14394};
inline constexpr std::array<std::uint32_t,18>choreography_triplets{0x14460,0x14394,0x1443e,0x1443e,0x14394,0x14460,0x14394,0x14460,0x1443e,0x1443e,0x14460,0x14394,0x14394,0x1443e,0x14460,0x14460,0x1443e,0x14394};
inline void create_choreography_roster(ActorPool&pool,std::uint32_t source,std::array<std::uint32_t,9>&roster,ActorAllocationServices&services){auto&head=pool.resolve(source);head.byte(50,std::uint8_t(head.byte(50)+1));head.byte(51,16);for(unsigned i=0;i<9;++i){auto&part=pool.resolve(source);const auto y=(part.longword(16)&0xffff0000u)|std::uint16_t(part.longword(16)+16);const auto result=allocate_actor_chain(pool,{choreography_spawn_definitions[i],part.longword(12),y,0,0,0},services);roster[i]=result.returned_key;if(result.success)pool.resolve(result.returned_key).longword(42,0xa84c);source=part.longword(84);}}
inline void initialize_choreography_triplets(ActorPool&pool,std::uint32_t source,std::array<std::uint32_t,9>&roster,AnimationRandom&random){for(unsigned group=0;group<3;++group){const auto selection=random.between(0,6);for(unsigned n=0;n<3;++n){auto&a=pool.resolve(source);const auto index=group*3+n;roster[index]=source;a.word(20,std::uint16_t(index));a.longword(42,0xba9e);a.longword(46,0xbe3e);a.longword(50,choreography_triplets[selection*3+n]);a.byte(54,16);a.byte(55,3);a.word(56,0);source=a.longword(84);}}}
}
