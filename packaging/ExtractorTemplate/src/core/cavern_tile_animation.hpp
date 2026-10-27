#pragma once
#include "core/cavern_tile_animation_data.hpp"
#include "core/terrain_pattern_storage.hpp"
namespace rolo {
struct CavernTileAnimation {
    std::array<std::uint8_t,4> countdown{},sequence_cursor{};
    // $FAA0..$FB70: advance every track even when its cache entry isFFFF.
    // A 64-word transfer publishes four original pattern tiles to native storage.
    void step(TerrainPatternStorage& storage,const TerrainQuadMapping& mapping){
        namespace data=cavern_tile_animation_data;
        for(unsigned i=0;i<data::tracks.size();++i){
            countdown[i]=static_cast<std::uint8_t>(countdown[i]-1);
            if(!(countdown[i]&128))continue;
            const auto& track=data::tracks[i];countdown[i]=static_cast<std::uint8_t>(track.delay);
            auto cursor=sequence_cursor[i];if(cursor>=track.sequence_count)cursor=0;
            const auto frame=data::sequences[track.sequence_first+cursor];sequence_cursor[i]=static_cast<std::uint8_t>(cursor+1);
            // $B3CC is the bank-local quad cache ($B2EC + 28*8),
            // not the source-pattern cache at $998C.
            const auto destination=mapping.quads.at(28+track.cache_byte_offset/8).at((track.cache_byte_offset%8)/2);
            if(destination==0xffff)continue;
            const auto first=track.first+frame*128;
            if(first+128>track.first+track.bytes)throw std::out_of_range("Cavern animation frame extent");
            storage.copy_patterns(std::span<const std::uint8_t>(data::patterns).subspan(first,128),destination&2047);
        }
    }
};
}

