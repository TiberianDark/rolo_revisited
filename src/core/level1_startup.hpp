#pragma once
#include "core/terrain_record_search.hpp"
#include "core/actor_state.hpp"
namespace rolo {
struct PlayerCheckpoint {std::uint16_t x{},y{};};
// $3FE0 within $3F3E's ordered MAP scan. Every matching class11 marker
// repositions the controlled actor; later matches overwrite earlier ones.
template<class CameraInitialize>
void select_player_startup_marker(TerrainMapView map,std::uint8_t selector,
        ActorState& controlled,PlayerCheckpoint& checkpoint,CameraInitialize&& camera_initialize){
    const auto rows=static_cast<std::uint16_t>(map.word(6)>>4);
    for(std::uint16_t row=0;row<rows;++row){
        const auto start=map.word(8+row*2),end=map.word(10+row*2);
        if(end<start||(end-start)%4)throw std::invalid_argument("Startup MAP row extent");
        for(std::uint32_t at=start;at<end;at+=4){
            const auto record=map.record(at);
            if((record.type&0xff00)!=0x1100||static_cast<std::uint8_t>(record.type)!=selector)continue;
            controlled.word(12,static_cast<std::uint16_t>(record.x+8));controlled.word(14,0);
            controlled.word(16,static_cast<std::uint16_t>(row<<4));controlled.word(18,0);
            checkpoint={controlled.word(12),controlled.word(16)};camera_initialize();
        }
    }
}
// $7730 deliberately copies integer words only, retaining current fractions.
inline void restore_player_checkpoint(ActorState& controlled,PlayerCheckpoint checkpoint){
    controlled.word(12,checkpoint.x);controlled.word(16,checkpoint.y);
}
}
