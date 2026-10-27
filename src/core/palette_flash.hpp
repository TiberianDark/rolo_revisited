#pragma once
#include "core/actor_state.hpp"
namespace rolo {
struct PaletteFlashServices {
    virtual ~PaletteFlashServices()=default;
    // $2468 handoff: 15 words, leaving palette index0 untouched.
    // original=true selects C5EE+bank*32; false selects common4B7CA.
    virtual void palette_flash_transfer(unsigned bank,bool original,std::uint16_t destination_byte)=0;
};
// $2F3C..$2FF6, including last-bank fallthrough into2FE8 transfer helper.
inline void update_palette_flashes(std::uint16_t& countdown,std::array<std::uint8_t,4>& counters,
        PaletteFlashServices& services){
    countdown=static_cast<std::uint16_t>(countdown-1);
    if(signed_word(countdown)>=0)return;
    countdown=10;
    for(unsigned bank=0;bank<4;++bank){
        const auto value=counters[bank];if(!value)continue;
        counters[bank]=static_cast<std::uint8_t>(value-1);
        const bool original=(counters[bank]&1)==0;
        services.palette_flash_transfer(bank,original,static_cast<std::uint16_t>(2+bank*32));
        // 2FE4 BSR returns to2FE8 itself: bank3 repeats the same transfer.
        if(bank==3)services.palette_flash_transfer(bank,original,98);
    }
}
}
