#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct TerrainCameraGlobals {
    std::uint16_t f2ca{},f2cc{},f2ce{},f2d0{},f372{},f374{};
    std::uint8_t up{},down{},left{},right{}; // F36E..F371.
};
struct TerrainCameraServices {
    virtual ~TerrainCameraServices()=default;
    virtual void camera_clear_backing(ActorState&,TerrainCameraGlobals&)=0;
    virtual void camera_full_refill(ActorState&,TerrainCameraGlobals&)=0;
    virtual void camera_row_update(ActorState&,TerrainCameraGlobals&,bool bottom)=0;
    virtual void camera_column_update(ActorState&,TerrainCameraGlobals&,bool right)=0;
};
inline void terrain_camera_ring_coordinates(const ActorState& plane,TerrainCameraGlobals& g) {
    g.f372=static_cast<std::uint16_t>((plane.word(18)&0x3f0)>>3);
    g.f374=static_cast<std::uint16_t>((plane.word(20)&plane.word(10))<<3);
}
// $72D0..$743C plus $7588 and the $75B0 refill prefix/tail handoff.
inline void update_terrain_camera(ActorState& plane,TerrainCameraGlobals& g,TerrainCameraServices& services) {
    g.f2ca=plane.word(12);g.f2cc=plane.word(14);g.f2ce=g.f2d0=0;
    g.up=g.down=g.left=g.right=0;
    auto finish=[&]{plane.word(26,static_cast<std::uint16_t>(0-plane.word(18)));plane.word(28,plane.word(20));};
    auto refill=[&]{services.camera_clear_backing(plane,g);plane.word(24,static_cast<std::uint16_t>(plane.word(20)>>4));terrain_camera_ring_coordinates(plane,g);services.camera_full_refill(plane,g);finish();};
    auto current=static_cast<std::uint16_t>(plane.word(18)>>4),previous=plane.word(22);
    plane.word(22,current);
    if(signed_word(previous)<0){refill();return;}
    auto delta=static_cast<std::uint16_t>(current-previous);
    if(delta) {
        if(signed_word(delta)>=0)g.right=255;
        else {g.left=255;delta=static_cast<std::uint16_t>(0-delta);}
        if(delta>2){refill();return;}
        g.f2ce=static_cast<std::uint16_t>((delta-1)<<4);
    }
    current=static_cast<std::uint16_t>(plane.word(20)>>4);previous=plane.word(24);plane.word(24,current);
    delta=static_cast<std::uint16_t>(current-previous);
    if(delta) {
        if(signed_word(delta)>=0)g.down=255;
        else {g.up=255;delta=static_cast<std::uint16_t>(0-delta);}
        if(delta>2){refill();return;}
        g.f2d0=static_cast<std::uint16_t>((delta-1)<<4);
    }
    auto axis=[&](bool vertical,bool negative) {
        auto& remaining=vertical?g.f2d0:g.f2ce;const unsigned field=vertical?20:18;
        plane.word(field,static_cast<std::uint16_t>(negative?plane.word(field)+remaining:plane.word(field)-remaining));
        for(;;) {
            terrain_camera_ring_coordinates(plane,g);
            if(vertical)services.camera_row_update(plane,g,!negative);
            else services.camera_column_update(plane,g,!negative);
            if(signed_word(remaining)<=0)break;
            plane.word(field,static_cast<std::uint16_t>(negative?plane.word(field)-remaining:plane.word(field)+remaining));
            remaining=static_cast<std::uint16_t>(remaining-16);
        }
    };
    if(g.up)axis(true,true);else if(g.down)axis(true,false);
    if(g.left)axis(false,true);else if(g.right)axis(false,false);
    finish();
}
// $7292/$72A2: explicit plane selection replaces F302's active descriptor pointer.
inline void update_foreground_terrain_camera(ActorState& foreground,TerrainCameraGlobals& g,TerrainCameraServices& services) {
    update_terrain_camera(foreground,g,services);
}
inline void update_background_terrain_camera(ActorState& background,std::uint8_t c546,
        TerrainCameraGlobals& g,TerrainCameraServices& services) {
    if(!c546){update_terrain_camera(background,g,services);return;}
    if(signed_word(background.word(22))<0) {
        const auto saved=background.longword(18);
        background.longword(18,0);
        update_terrain_camera(background,g,services);
        background.longword(18,saved);
    }
    background.word(26,static_cast<std::uint16_t>(0-background.word(18)));
    background.word(28,background.word(20));
}
}
