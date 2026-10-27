#pragma once
#include "core/camera_data.hpp"
#include <array>
#include <cstdint>
namespace rolo {
namespace camera_word {
inline std::uint16_t w(int value) {return static_cast<std::uint16_t>(value);}
inline int s(std::uint16_t value) {return value<32768?value:static_cast<int>(value)-65536;}
inline std::uint16_t add(std::uint16_t a,int b) {return w(static_cast<int>(a)+b);}
inline std::uint16_t asr(std::uint16_t a,int n) {const int v=s(a),scale=1<<n;return w(v>=0?v/scale:-((-v+scale-1)/scale));}
}
struct CameraState {
    std::uint16_t x{},y{},left{},right{},top{},bottom{};
    std::uint16_t foreground_x{},foreground_y{},background_x{},background_y{};
    std::uint16_t phase{}; // $FFC5C2, mode 5 increments this word.
    std::uint16_t x_fraction{},y_fraction{}; // Low words used by $9F2A/$9F30.
    std::uint8_t background_flag{},scroll_mode{};
    std::array<std::uint16_t,32> row_scroll{}; // $FF7440..$FF747F
};
struct CameraInput {
    std::uint16_t player_x{},player_y{},previous_player_x{},map_width{},map_height{};
    bool freeze_519{},freeze_51a{};
    std::uint8_t background_mode{};
    std::uint16_t foreground_shift{},vblank_counter{}; // $FFF268 / $FFC490
};
// $4EAA..$505E: data transforms used by all ten background dispatch entries.
inline void update_camera_layers(CameraState& c,const CameraInput& in) {
    using namespace camera_word;
    c.foreground_x=c.x;c.foreground_y=c.y;
    auto x=c.x,y=c.y;c.background_flag=0;c.scroll_mode=0;
    switch(in.background_mode) {
    case 0:x>>=1;y>>=1;break;
    case 1:x>>=1;y>>=1;c.background_flag=255;break;
    case 2:break;
    case 3:x>>=1;y=0;c.background_flag=255;break;
    case 4:c.background_flag=255;break;
    case 5: {
        const auto index=static_cast<unsigned>(w(-static_cast<int>(c.phase))*2)&1023;
        c.phase=add(c.phase,1);
        const auto sample=[&](unsigned byte_offset) {
            const int product=static_cast<int>(camera_data::sine[(byte_offset&1023)/2])*400;
            return product>=0?product/65536:-((-product+65535)/65536);
        };
        x=w(sample(index+256)+400);y=w(sample(index)+400);c.background_flag=255;break;
    }
    case 6:c.foreground_x=add(c.foreground_x,in.foreground_shift);break;
    case 7: {
        std::size_t at=32;auto value=asr(x,1);
        const auto put=[&](int count,std::uint16_t v) {while(count--)c.row_scroll[--at]=v;};
        put(14,value);value=asr(value,1);put(3,value);
        value=asr(value,1);put(2,value);value=asr(value,1);put(1,value);put(12,0);
        x=0;y=0;c.background_flag=255;c.scroll_mode=2;break;
    }
    case 8: {
        std::size_t at=32;const auto put=[&](int count,std::uint16_t v) {while(count--)c.row_scroll[--at]=v;};
        const auto value=asr(x,1);put(16,value);put(12,asr(value,2));
        put(2,asr(in.vblank_counter,1));put(2,in.vblank_counter);
        x=in.vblank_counter;y=0;c.background_flag=255;c.scroll_mode=2;break;
    }
    case 9: {
        std::size_t at=32;const auto put=[&](int count,std::uint16_t v) {while(count--)c.row_scroll[--at]=v;};
        auto value=asr(x,1);put(24,value);value=asr(value,1);put(8,value);
        x=value;y=0;c.background_flag=255;c.scroll_mode=2;break;
    }
    default:return; // Only 0..9 occur in the extracted 80-entry selector table.
    }
    c.background_x=x;c.background_y=y;
}
// $4D54..$4EA4. All arithmetic stays at the ROM's word width; unsigned branches
// (BLS/BCC/BCS) and signed branches are deliberately distinct.
inline void update_camera(CameraState& c,const CameraInput& in) {
    using namespace camera_word;
    if(!in.freeze_519&&!in.freeze_51a) {
        auto target=in.player_x;
        auto delta=w(static_cast<int>(target)-in.previous_player_x);
        const auto direction=delta;
        if(s(delta)<0)delta=w(-s(delta));
        auto step=add(delta,delta);if(step>15)step=15;
        const auto screen=w(static_cast<int>(target)-c.x);
        if(s(direction)<0) {
            if(screen>c.left) {
                if(screen<120) {c.left=add(c.left,step);c.right=add(c.right,step);target=add(target,-120);}
                else step=0;
            } else {
                c.left=add(c.left,step);c.right=add(c.right,step);
                if(c.right>320) {c.left=200;c.right=320;}
                target=add(target,-static_cast<int>(c.left));
            }
        } else {
            if(screen<c.right) {
                if(screen>=200) {c.left=add(c.left,-static_cast<int>(step));c.right=add(c.right,-static_cast<int>(step));target=add(target,-200);}
                else step=0;
            } else {
                c.right=add(c.right,-static_cast<int>(step));c.left=add(c.left,-static_cast<int>(step));
                if(s(c.left)<0) {c.left=0;c.right=120;}
                target=add(target,-static_cast<int>(c.right));
            }
        }
        if(s(target)<0)target=0;
        const auto max_x=add(in.map_width,-320);if(target>max_x)target=max_x;
        if(step) {
            delta=w(static_cast<int>(target)-c.x);
            if(s(delta)<0) {step=w(-static_cast<int>(step));if(delta>step)step=delta;}
            else if(delta<step)step=delta;
            c.x=add(c.x,step);
        }
        const auto upper=add(c.y,c.top),lower=add(c.y,c.bottom);
        auto y=in.player_y;
        if(s(y)<s(upper)) {y=add(y,-static_cast<int>(c.top));if(s(y)<0)y=0;c.y=y;}
        else if(s(y)>s(lower)) {y=add(y,-static_cast<int>(c.bottom));const auto max_y=add(in.map_height,-224);if(s(y)>s(max_y))y=max_y;c.y=y;}
    }
    update_camera_layers(c,in);
}
// $4CB8..$4D52, including its call to $4D54 BEFORE the tracking bands are set.
// Callers supply the existing RAM state, just as the original routine does.
inline void initialize_camera(CameraState& c,const CameraInput& in) {
    using namespace camera_word;
    auto x=add(in.player_x,-176);if(s(x)<0)x=0;
    const auto max_x=add(in.map_width,-320);if(s(x)>s(max_x))x=max_x;c.x=x;
    auto y=add(in.player_y,-160);
    if(s(y)<0)y=0;else {const auto max_y=add(in.map_height,-224);if(s(y)>s(max_y))y=max_y;}c.y=y;
    update_camera(c,in);
    auto left=add(w(static_cast<int>(in.player_x)-c.x),-60);if(s(left)<0)left=0;
    c.left=left;c.right=add(left,120);c.top=134;c.bottom=154;
}
struct ScriptedCameraInput {
    std::uint16_t player_x{},player_y{},alternate_x{},alternate_y{},map_width{},map_height{};
    bool alternate_target{}; // $FFF270 selects $FFC5BA rather than $FFC4E0.
};
inline std::array<std::uint16_t,2> scripted_camera_target(const ScriptedCameraInput& in,bool select_alternate) {
    using namespace camera_word;
    auto x=add(select_alternate?in.alternate_x:in.player_x,-160);
    auto y=add(select_alternate?in.alternate_y:in.player_y,-112);
    if(s(x)<=224)x=224;if(s(y)<=224)y=224;
    const auto max_x=add(in.map_width,-544),max_y=add(in.map_height,-448);
    if(s(x)>=s(max_x))x=max_x;if(s(y)>=s(max_y))y=max_y;
    return {x,y};
}
// $9E3A: immediate world-map camera placement; leaves low coordinate words intact.
inline void initialize_scripted_camera(CameraState& c,const ScriptedCameraInput& in) {
    const auto target=scripted_camera_target(in,false);
    c.x=target[0];c.y=target[1];c.background_flag=0;
}
// $9E98..$9F5E and $63A6: target selection, integer vector ratios, distance speed
// table at $9F60, and 16.16 accumulation. This is separate from level tracking.
inline void update_scripted_camera(CameraState& c,const ScriptedCameraInput& in) {
    using namespace camera_word;
    const auto target=scripted_camera_target(in,in.alternate_target);
    const auto raw_x=w(static_cast<int>(target[0])-c.x),raw_y=w(static_cast<int>(target[1])-c.y);
    const bool negative_x=s(raw_x)<0,negative_y=s(raw_y)<0;
    auto dx=negative_x?w(-static_cast<int>(raw_x)):raw_x;
    auto dy=negative_y?w(-static_cast<int>(raw_y)):raw_y;
    const bool swap=s(dy)>s(dx);if(swap) {const auto temp=dx;dx=dy;dy=temp;}
    std::uint32_t vx=0,vy=0;
    if(dx) {
        const std::uint32_t ratio=(static_cast<std::uint32_t>(dy)<<16)/dx;
        vx=65536;vy=ratio>65535?65536:ratio;
        if(swap) {const auto temp=vx;vx=vy;vy=temp;}
        if(negative_x)vx=0u-vx;if(negative_y)vy=0u-vy;
    }
    const unsigned shift=s(dx)<=10?0:s(dx)<=20?1:s(dx)<=40?2:3;
    const std::uint32_t fixed_x=(static_cast<std::uint32_t>(c.x)<<16)|c.x_fraction;
    const std::uint32_t fixed_y=(static_cast<std::uint32_t>(c.y)<<16)|c.y_fraction;
    const auto next_x=fixed_x+(vx<<shift),next_y=fixed_y+(vy<<shift);
    c.x=static_cast<std::uint16_t>(next_x>>16);c.x_fraction=static_cast<std::uint16_t>(next_x);
    c.y=static_cast<std::uint16_t>(next_y>>16);c.y_fraction=static_cast<std::uint16_t>(next_y);
    c.foreground_x=c.background_x=c.x;c.foreground_y=c.background_y=c.y;
}
}
