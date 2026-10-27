#pragma once
#include "core/terrain_streaming.hpp"
#include "core/terrain_display.hpp"
namespace rolo {
struct TerrainStreamingCameraServices:TerrainCameraServices {
    std::span<std::uint8_t> backing;TerrainMapView map;
    TerrainDescriptorServices& macros;TerrainDisplayServices& display;
    bool foreground;
    TerrainStreamingCameraServices(std::span<std::uint8_t> bytes,TerrainMapView view,
        TerrainDescriptorServices& m,TerrainDisplayServices& d,bool front):backing(bytes),map(view),macros(m),display(d),foreground(front){}
    void camera_clear_backing(ActorState&,TerrainCameraGlobals&) override {
        const std::size_t size=foreground?16384:8192;
        if(backing.size()<size)throw std::out_of_range("Native plane clear extent");
        for(std::size_t n=0;n<size;++n)backing[n]=0;
    }
    void camera_full_refill(ActorState& plane,TerrainCameraGlobals& g) override {
        fill_initial_terrain(plane,backing,map,g.f374,g.f2ca,macros);
        display_full_terrain(plane,g,backing,display);
    }
    void camera_row_update(ActorState& plane,TerrainCameraGlobals& g,bool bottom) override {
        stream_terrain_row(plane,backing,map,g.f374,g.f2ca,bottom,macros);
        display_terrain_row(plane,g,backing,bottom,display);
    }
    void camera_column_update(ActorState& plane,TerrainCameraGlobals& g,bool right) override {
        stream_terrain_column(plane,backing,map,g.f374,g.f2ca,right,macros);
        display_terrain_column(plane,g,backing,right,display);
    }
};
}
