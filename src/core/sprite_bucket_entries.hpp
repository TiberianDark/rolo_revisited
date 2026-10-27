#pragma once
#include "core/actor_sprite.hpp"
#include "core/macro_graphics_entries.hpp"
namespace rolo {
struct SpriteBucketState{std::vector<std::uint8_t>sat,packets;std::uint8_t count=0;std::uint16_t transfer_words=0,pending_count=0,camera_x=0,camera_y=0;};
struct SpriteBucketServices{virtual ~SpriteBucketServices()=default;virtual ActorState& sprite_actor(std::uint32_t)=0;virtual std::uint16_t sprite_definition_flags(std::uint32_t)=0;};
inline void finish_sprite_capacity(SpriteBucketState&state){if(state.sat.size()<8)throw std::out_of_range("Sprite terminator extent");state.sat[state.sat.size()-5]=0;auto words=state.transfer_words?state.transfer_words:4;macro_write_word(state.packets,0x9300|(words&255));macro_write_word(state.packets,0x9400|(words>>8));macro_write_word(state.packets,0x95de);macro_write_word(state.packets,0x96e4);macro_write_word(state.packets,0x977f);macro_write_long(state.packets,0x74000083);}
// $3440 enters the word bucket at its next item. A zeroWORD ends that
// bucket; nonzero words are sign-extended keys in the original FFFF bank.
// Returns true only on the original global capacity escape at$3470.
inline bool consume_sprite_bucket(std::span<const std::uint16_t>bucket,SpriteBucketState&state,SpriteBucketServices&s){
 for(auto key:bucket){if(!key){state.pending_count=0;return false;}auto&a=s.sprite_actor(0xffff0000u|key);if(a.byte(125)&2||!a.longword(28))continue;
  if(a.longword(28)!=a.longword(8)){a.longword(8,a.longword(28));auto words=a.word(40)>>1;macro_write_word(state.packets,0x9300|(words&255));macro_write_word(state.packets,0x9400|(words>>8));auto source=std::uint32_t(signed_long(a.longword(28))>>1);macro_write_word(state.packets,0x9500|(source&255));macro_write_word(state.packets,0x9600|((source>>8)&255));macro_write_word(state.packets,0x9700|((source>>16)&255));auto dest=std::uint16_t(a.word(2)<<5);macro_write_long(state.packets,(std::uint32_t(dest&0x3fff)<<16)|(dest>>14)|0x40000080);}
  auto view=actor_sprite_view(a,state.camera_x,state.camera_y);std::uint16_t x=std::uint16_t(view.x+128),y=std::uint16_t(view.y+128),width=view.width,height=view.height,tile=a.word(2);if(!width||!height||width%8||height%8||width>=32768||height>=32768)throw std::out_of_range("Sprite chunk dimensions");auto attr=std::uint16_t(s.sprite_definition_flags(a.longword(4))&0xff00);int dx=32,dy=32;if(view.flip_x){x=std::uint16_t(x+width-32);dx=-32;attr|=0x800;}if(view.flip_y){y=std::uint16_t(y+height-32);dy=-32;attr|=0x1000;}
  unsigned remaining_y=height;do{auto row_x=x;unsigned remaining_x=width;unsigned h=remaining_y>=32?32:remaining_y;if(h<32&&view.flip_y)y=std::uint16_t(y+32-h);do{unsigned w=remaining_x>=32?32:remaining_x;if(w<32&&view.flip_x)row_x=std::uint16_t(row_x+32-w);auto size=std::uint8_t(((w/8-1)<<2)|(h/8-1));if(signed_word(row_x)>=96&&signed_word(row_x)<=448&&signed_word(y)>=96&&signed_word(y)<=352){state.count=std::uint8_t(state.count+1);if(state.count==81){finish_sprite_capacity(state);return true;}macro_write_word(state.sat,y);state.sat.push_back(size);state.sat.push_back(state.count);macro_write_word(state.sat,tile|attr);macro_write_word(state.sat,row_x);state.transfer_words=std::uint16_t(state.transfer_words+4);}row_x=std::uint16_t(row_x+dx);tile=std::uint16_t(tile+(w/8)*(h/8));remaining_x-=w;}while(remaining_x);y=std::uint16_t(y+dy);remaining_y-=h;}while(remaining_y);
 }
 throw std::out_of_range("Unterminated sprite bucket");
}
}
