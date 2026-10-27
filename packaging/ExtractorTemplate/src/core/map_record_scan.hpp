#pragma once
#include "core/actor_state.hpp"
#include <span>
#include <stdexcept>
namespace rolo {
inline std::uint16_t record_scan_word(std::span<const std::uint8_t>map,std::size_t at){if(at+2>map.size())throw std::out_of_range("MAP scan word");return std::uint16_t((map[at]<<8)|map[at+1]);}
inline std::size_t record_scan_offset(std::uint16_t word,std::size_t extent){if(word>=32768||word>extent)throw std::out_of_range("MAP signed row offset");return word;}
struct MapMarkerCall{std::uint16_t parameter{},x{},y{};std::size_t record{};};
struct MapMarkerScanServices{virtual ~MapMarkerScanServices()=default;virtual std::uint16_t marker(MapMarkerCall)=0;};
inline bool scan_map_markers(std::span<const std::uint8_t>map,std::uint8_t type,MapMarkerScanServices&services){const auto height=record_scan_word(map,6)>>4;unsigned row=0;std::size_t table=8;
 do{const auto end=record_scan_offset(record_scan_word(map,table+2),map.size());auto cursor=record_scan_offset(record_scan_word(map,table),map.size());table+=2;
  if(cursor!=end){for(;;){if(cursor+4>map.size())throw std::out_of_range("MAP marker extent");if(map[cursor]==type){const auto parameter=map[cursor+1];const auto x=std::uint16_t(record_scan_word(map,cursor+2)+8);const auto y=std::uint16_t(std::uint16_t(std::uint16_t(row*2)+2)*8+1);if(services.marker({parameter,x,y,cursor}))return true;}cursor+=4;if(cursor>=end)break;}}
  ++row;
 }while(row<height);return false;
}
struct MapRestoreCursor{std::uint16_t row{},height{};std::size_t table{},record{},end{};};
struct MapRestoreServices{virtual ~MapRestoreServices()=default;virtual void allocate(std::uint32_t definition)=0;virtual void initialize_camera()=0;};
inline void resume_map_restore(std::span<std::uint8_t>map,MapRestoreCursor&c,std::span<const std::uint32_t>definitions,std::uint8_t start_selector,ActorState&controlled,std::uint16_t&saved_x,std::uint16_t&saved_y,MapRestoreServices&services){
 for(;;){while(c.record<c.end){const auto at=c.record;const auto type=record_scan_word(map,at);const auto x=record_scan_word(map,at+2);c.record+=4;if(type<0x400)continue;const auto group=type&0xff00,parameter=type&255;
  if(group==0x500){const auto index=(parameter&254)/2;if(index>=definitions.size())throw std::out_of_range("MAP generic definition table");const auto definition=definitions[index];if(definition==0x14906||definition==0x148c2||definition==0x148e4){map[at]=0x17;services.allocate(definition);}}
  else if(group==0x1100&&parameter==start_selector){controlled.word(12,std::uint16_t(x+8));controlled.word(14,0);controlled.word(16,std::uint16_t(c.row*16));controlled.word(18,0);saved_x=controlled.word(12);saved_y=controlled.word(16);services.initialize_camera();}
 }
 c.row=std::uint16_t(c.row+1);if(c.row>=c.height)return;c.end=record_scan_offset(record_scan_word(map,c.table+2),map.size());c.record=record_scan_offset(record_scan_word(map,c.table),map.size());c.table+=2;
 }
}
}
