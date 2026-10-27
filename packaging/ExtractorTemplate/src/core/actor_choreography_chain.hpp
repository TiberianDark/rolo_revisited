#pragma once
#include "core/actor_allocation.hpp"
#include "core/actor_wave_motion.hpp"
namespace rolo {
inline std::array<std::int8_t,18> choreography_offsets{};
inline void advance_choreography_phase(ActorState&a,unsigned delay){a.byte(50,std::uint8_t(a.byte(50)+1));if(delay)a.byte(51,std::uint8_t(delay));}
inline void tick_choreography_phase(ActorState&a,unsigned delay){a.byte(51,std::uint8_t(a.byte(51)-1));if(!a.byte(51))advance_choreography_phase(a,delay);}
inline void move_choreography_chain(ActorPool&pool,std::uint32_t head,bool reverse){auto&a=pool.resolve(head);tick_choreography_phase(a,0);if(reverse&&a.byte(51)==0){a.byte(52,1);a.byte(53,1);}auto key=head;
 for(unsigned i=0;i<9;++i){auto&part=pool.resolve(key);const auto dx=int(choreography_offsets[i*2])*(reverse?-1:1),dy=int(choreography_offsets[i*2+1])*(reverse?-1:1);part.word(12,std::uint16_t(part.word(12)+dx));part.word(16,std::uint16_t(part.word(16)+dy));key=part.longword(84);}
}
inline void move_choreography_roster(ActorPool&pool,std::uint32_t head,const std::array<std::uint32_t,9>&roster,bool down){tick_choreography_phase(pool.resolve(head),down?0:50);for(const auto key:roster)if(key){auto&a=pool.resolve(key);a.word(16,std::uint16_t(a.word(16)+(down?1:-1)));}}
inline void retire_choreography_roster(ActorPool&pool,std::uint32_t head,const std::array<std::uint32_t,9>&roster){advance_choreography_phase(pool.resolve(head),64);for(const auto key:roster)if(key)pool.resolve(key).byte(116,255);}
inline void rotate_choreography_chain(ActorPool&pool,std::uint32_t head){auto key=head;for(unsigned i=0;i<8;++i)key=pool.resolve(key).longword(84);for(unsigned i=0;i<8;++i){auto&a=pool.resolve(key);const auto parent=a.longword(80);a.word(32,pool.resolve(parent).word(32));a.word(34,pool.resolve(parent).word(34));key=parent;}
 auto&root=pool.resolve(key);const auto vector=actor_wave_vector(std::uint16_t(root.byte(51)*2),root.byte(52),1);root.word(32,std::uint16_t(vector.x>>16));root.word(34,std::uint16_t(vector.y>>16));if(root.byte(52)==80)root.byte(53,std::uint8_t(0-root.byte(53)));
 if(root.byte(52)){root.byte(52,std::uint8_t(root.byte(52)+root.byte(53)));root.byte(51,std::uint8_t(root.byte(51)+10));return;}advance_choreography_phase(root,64);
 for(unsigned i=0;i<8;++i){auto&a=pool.resolve(key);auto next=a.longword(84);pool.resolve(next).word(32,a.word(32));pool.resolve(next).word(34,a.word(34));key=next;}
}
}

