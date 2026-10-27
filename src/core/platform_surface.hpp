#pragma once
#include "core/actor_platform_contact.hpp"
namespace rolo {
struct PlatformTileMap {std::uint8_t width{};std::span<const std::uint16_t> tiles;};
// $8C06: unsigned row multiply after arithmetic WORD shifts; signed EA offset.
inline std::uint16_t platform_coordinate_tile(PlatformTileMap map,std::uint16_t x,std::uint16_t y){
 const auto column=static_cast<std::uint16_t>(signed_word(x)>>4),row=static_cast<std::uint16_t>(signed_word(y)>>4);
 const auto index=static_cast<std::uint16_t>(column+static_cast<std::uint16_t>(std::uint32_t(row)*map.width));
 const auto offset=static_cast<std::uint16_t>(index*2);
 if(offset&0x8000||offset/2>=map.tiles.size())throw std::out_of_range("Platform coordinate map extent");return map.tiles[offset/2];
}
struct PlatformSurfaceData {std::span<const std::uint8_t> collision,profiles;};
struct PlatformSurface {bool found{};std::uint16_t y{},tile{};std::uint8_t shape{};};
inline PlatformSurface platform_surface_at(PlatformTileMap map,PlatformSurfaceData data,std::uint16_t x,std::uint16_t y){
 const auto tile=platform_coordinate_tile(map,x,y);if(!(tile&0x4000))return {false,0,tile,0};
 const auto descriptor=(tile&511)*8+((tile&4096)?2:0);if(descriptor+1>=data.collision.size())throw std::out_of_range("Platform descriptor extent");
 const auto offset=data.collision[descriptor],shape=data.collision[descriptor+1];
 const auto column=(shape&64)?std::uint16_t(~x)&15:x&15;const unsigned profile=(shape&63)*16+column;
 if(profile>=data.profiles.size())throw std::out_of_range("Platform profile extent");const auto height=data.profiles[profile];if(height&128)return {false,0,tile,shape};
 const auto base=std::uint16_t(y&0xfff0);const auto surface=static_cast<std::uint16_t>((tile&4096)?base+31-offset-height:base+16-offset+height);
 return {true,surface,tile,shape};
}
struct PlatformPositionCache {std::uint16_t x{},y{};};
// $8A68: rider98 selects the platform; map data is immutable for this call.
inline void restore_actor_platform_surface(ActorPool& pool,std::uint32_t rider,PlatformPositionCache& cache,PlatformTileMap map,PlatformSurfaceData data){
 auto&a=pool.resolve(rider);auto&p=pool.resolve(a.longword(98));a.byte(124,a.byte(124)&0x9fu);a.byte(120,0);
 auto absolute=[](std::uint16_t v){return (v&0x8000)?std::uint16_t(0-v):v;};
 const auto reach=static_cast<std::uint16_t>(a.word(58)+a.word(62)+absolute(p.word(64))+absolute(p.word(60))+1);
 if((a.byte(122)&128)&&!(p.word(64)&0x8000))return;
 const auto left=static_cast<std::uint16_t>(p.word(12)-half_signed_word(p.word(36))),top=static_cast<std::uint16_t>(p.word(16)-p.word(38));
 const auto x=static_cast<std::uint16_t>(a.word(12)-left),y=static_cast<std::uint16_t>(a.word(16)-top);if((x|y)&0x8000)return;cache={x,y};
 for(const unsigned delta:{32u,16u,0u}){
  const auto local_y=static_cast<std::uint16_t>(cache.y-delta);if(delta&&(local_y&0x8000))continue;
  if(signed_word(local_y)>signed_word(p.word(38)))return;
  // The contact envelope includes the bottom edge and 16 pixels below it.
  // These are candidate probes, not guaranteed cells in the native macro.
  // Exhausted rows/columns have no surface; never index an adjacent allocation.
  if(!map.width||cache.x>=unsigned(map.width)*16||
      unsigned(local_y)/16>=map.tiles.size()/map.width)continue;
  const auto surface=platform_surface_at(map,data,cache.x,local_y);if(!surface.found)continue;
  const auto world_y=static_cast<std::uint16_t>(surface.y+p.word(16)-p.word(38));
  if(signed_word(reach)<signed_word(static_cast<std::uint16_t>(a.word(16)-world_y)))continue;
  if(world_y>a.word(16))return;a.word(16,world_y);a.word(18,0);
  a.byte(120,surface.shape^((surface.tile&4096)?64:0));a.byte(124,(a.byte(124)|33)&~16u);
  a.word(66,a.word(62));a.byte(122,0);a.longword(62,0);
  if(a.word(68)){a.word(68,0);a.byte(124,a.byte(124)|64);}return;
 }
}
}
