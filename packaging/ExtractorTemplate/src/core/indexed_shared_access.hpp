#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct JigsawOffsetWords{std::uint16_t minus12{},minus10{},minus4{},minus2{},plus6{};};
inline std::uint16_t jigsaw_neighbor_offset(unsigned mode,std::uint16_t row,const JigsawOffsetWords&w){switch(mode){case 0:return 1;case 1:return 65535;case 2:return std::uint16_t(w.minus4+w.minus2-(row? w.minus2:w.plus6));case 3:{const auto sum=row==3?std::uint16_t(w.minus12+w.minus10):std::uint16_t(w.minus4+w.minus2);return std::uint16_t(0-std::uint16_t(sum-w.minus2));}default:throw std::out_of_range("Jigsaw branch domain");}}
inline std::uint8_t read_jigsaw_neighbor(std::span<const std::uint8_t>flags,std::size_t base,unsigned mode,std::uint16_t row,const JigsawOffsetWords&w){const auto delta=jigsaw_neighbor_offset(mode,row,w);const auto offset=delta<32768?int(delta):int(delta)-65536;const auto at=std::int64_t(base)+offset-1;if(at<0||std::uint64_t(at)>=flags.size())throw std::out_of_range("Jigsaw flag extent");return flags[std::size_t(at)];}
inline std::uint32_t classify_plane_dimension(std::uint8_t dimension){return dimension==32?0:dimension==64?1:3;}
struct PlaneDimensionState{std::uint8_t width{},height{},packed{};};
inline void initialize_plane_dimensions(PlaneDimensionState&s,std::uint8_t d0,std::uint8_t d1){s.width=s.height=d0;s.packed=std::uint8_t((classify_plane_dimension(d1)<<4)|classify_plane_dimension(d0));}
struct ActorChainLookup{std::uint32_t actor{};std::uint16_t count{};};
inline ActorChainLookup actor_chain_nth(ActorPool&pool,std::uint32_t current,std::uint16_t count){for(;;){const auto next=pool.resolve(current).longword(84);if(!next)return {0,count};count=std::uint16_t(count-1);if(count==65535)return {next,count};current=next;}}
inline void toggle_actor_sixth_pair(ActorPool&pool,std::uint32_t head){const auto key=actor_chain_nth(pool,head,5).actor;if(!key)return;auto&a=pool.resolve(key);a.byte(125,a.byte(125)^2);const auto next=a.longword(84);if(next){auto&b=pool.resolve(next);b.byte(125,b.byte(125)^2);}}
}
