#pragma once
#include "core/actor_allocation.hpp"
#include <vector>
namespace rolo {
inline std::uint16_t macro_read_word(std::span<const std::uint8_t>b,std::size_t at){if(at>b.size()||b.size()-at<2)throw std::out_of_range("Macro data word");return (b[at]<<8)|b[at+1];}
inline std::uint32_t macro_read_long(std::span<const std::uint8_t>b,std::size_t at){return (std::uint32_t(macro_read_word(b,at))<<16)|macro_read_word(b,at+2);}
inline void macro_write_word(std::vector<std::uint8_t>&b,std::uint16_t w){b.push_back(w>>8);b.push_back(w);}
inline void macro_write_long(std::vector<std::uint8_t>&b,std::uint32_t w){macro_write_word(b,w>>16);macro_write_word(b,w);}
struct MacroPublishState{std::vector<std::uint8_t> packets;std::uint16_t budget=128;};
struct MacroGraphicsServices{
 virtual ~MacroGraphicsServices()=default;
 virtual ActorState* allocate(const ActorAllocationRequest&,ActorState*&live)=0;
 virtual ActorState& actor(std::uint32_t)=0;
 virtual ActorState& definition(std::uint32_t)=0;
 virtual void flush(MacroPublishState&)=0; //260A drain followed by8F02; reset budget128, restore caller registers.
};
// $4B2E: original two-macro-row packing, with a compact final odd row.
// Width is a positive multiple of16; height is a nonnegative multiple of16.
inline void publish_macro_graphics(const ActorState&a,std::span<const std::uint8_t>cells,std::span<const std::uint8_t>quads,MacroPublishState&q,MacroGraphicsServices&s){
 const auto width=a.word(36),height=a.word(38);if(!width||width%16||height%16||width>=32768||height>=32768)throw std::out_of_range("Macro publish dimensions");
 unsigned columns=width/16,rows=height/16;std::size_t source=0;std::uint16_t destination=std::uint16_t(a.word(2)<<5);
 for(unsigned row=0;row<rows;){const unsigned group_rows=rows-row>=2?2:1,stride=group_rows==2?128:64;auto group_base=destination;
  for(unsigned r=0;r<group_rows;++r){auto out=std::uint16_t(group_base+r*64);for(unsigned col=0;col<columns;++col){auto cell=macro_read_word(cells,source)&511;source+=2;auto at=cell*8;
    q.budget=std::uint16_t(q.budget-4);if(signed_word(q.budget)<=0){s.flush(q);q.budget=std::uint16_t(q.budget-4);if(signed_word(q.budget)<=0)throw std::out_of_range("Macro flush failed to replenish budget");}
    for(unsigned k=0;k<4;++k){auto tile=macro_read_word(quads,at+k*2)&2047;auto dest=std::uint16_t(out+(k&1?stride:0)+(k&2?32:0));macro_write_long(q.packets,0x93209400);macro_write_word(q.packets,0x9500|((tile<<5)&255));macro_write_word(q.packets,0x9600|(tile>>3));macro_write_word(q.packets,0x97c0);macro_write_long(q.packets,(std::uint32_t(dest&0x3fff)<<16)|(dest>>14)|0xc0);}
    out=std::uint16_t(out+stride*2);
  }}destination=std::uint16_t(group_base+columns*stride*2);row+=group_rows;
 }
 // Typed packets omit the terminating zeroLONG from their payload; this is
 // appended when publishing the native queue, including the zero-height case.
}
struct DynamicMacroPool{std::span<std::uint32_t> free;std::size_t cursor=0;};
struct MacroSpawnInput{std::uint16_t parameter=0,record_x=0,row=0,graphics_word=0;std::uint32_t marker=0;};
struct MacroSpawnResult{ActorState* actor=nullptr;bool negative=true;};
inline MacroSpawnResult spawn_dynamic_macro(MacroSpawnInput in,DynamicMacroPool&pool,std::span<const std::uint8_t>table,std::uint32_t table_key,std::span<const std::uint8_t>quads,MacroPublishState&q,MacroGraphicsServices&s,ActorState*&live){
 if(pool.cursor>=pool.free.size())throw std::out_of_range("Dynamic definition free stack");auto key=pool.free[pool.cursor];if(!key)return {}; ++pool.cursor;
 auto&def=s.definition(key);auto offset=signed_word(macro_read_word(table,6+(in.parameter&255)*2));if(offset<0)throw std::out_of_range("Macro table offset");auto at=std::size_t(offset);if(at+2>table.size())throw std::out_of_range("Macro header");auto width=std::uint16_t(table[at]*16),height=std::uint16_t(table[at+1]*16);auto product=std::uint16_t(std::uint32_t(width)*height);auto units=std::uint16_t(signed_word(product)>>1);auto graphic_index=std::uint16_t((in.graphics_word>>6)-128);
 def.longword(0,0);def.word(4,units);def.byte(6,0);def.byte(7,2);def.word(8,0x3ac8);def.word(10,24);def.longword(12,0xbe4e);def.word(16,0);def.byte(27,255);def.longword(18,0);def.byte(26,0);
 auto x=std::uint16_t(in.record_x+width/2),y=std::uint16_t((in.row<<3)+height);auto*child=s.allocate({key,std::uint32_t(x)<<16,std::uint32_t(y)<<16,in.marker,in.marker,0},live);
 if(!child){if(!pool.cursor)throw std::out_of_range("Dynamic free stack rollback");pool.free[--pool.cursor]=key;return {};}
 child->word(32,0);child->word(34,0);child->word(36,width);child->word(38,height);child->word(40,def.word(4));child->longword(28,0x5854524e);child->longword(8,0x5854524e);child->longword(46,table_key+std::uint32_t(at)+2);child->word(54,graphic_index);publish_macro_graphics(*child,table.subspan(at+2),quads,q,s);return {child,false};
}
struct MacroBranchGlobals{std::uint8_t override_mode=0,visited=0,exclusion=0,hide_companion=0;};
inline MacroSpawnResult spawn_breakable_macro(MacroSpawnInput in,MacroBranchGlobals g,DynamicMacroPool&pool,std::span<const std::uint8_t>rom,std::span<const std::uint8_t>table,std::uint32_t table_key,std::span<const std::uint8_t>quads,MacroPublishState&q,MacroGraphicsServices&s,ActorState*&live){
 if(!g.override_mode&&g.visited&&(g.exclusion&128))return {};auto offset=signed_word(std::uint16_t(in.parameter*8));auto at=std::size_t(0x48c8+offset);if(at>rom.size()||rom.size()-at<8)throw std::out_of_range("Breakable record");auto index=rom[at];in.parameter=index;auto result=spawn_dynamic_macro(in,pool,table,table_key,quads,q,s,live);if(result.negative)return result;auto&a=*result.actor;a.longword(42,0xb80a);a.byte(54,rom[at+1]);a.byte(55,rom[at+2]);a.longword(50,macro_read_long(rom,at+4));s.definition(a.longword(4)).word(10,52);return result;
}
inline ActorState* spawn_companion_macro(MacroSpawnInput in,MacroBranchGlobals g,std::span<const std::uint8_t>rom,MacroGraphicsServices&s,ActorState*&live){
 auto definition=macro_read_long(rom,0x4948+(in.parameter&255)*4);auto x=std::uint16_t(in.record_x+8),y=std::uint16_t(((in.row+2)<<3)+1);auto*child=s.allocate({definition,std::uint32_t(x)<<16,std::uint32_t(y)<<16,in.marker,in.marker,0},live);if(g.hide_companion){if(!live)throw std::out_of_range("Companion live actor");auto next=live->longword(84);if(next)s.actor(next).byte(116,255);}return child;
}
}


