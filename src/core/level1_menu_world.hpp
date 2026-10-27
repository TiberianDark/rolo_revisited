#pragma once
#include "core/level1_enemy_slice.hpp"
#include "core/level1_companion_menu.hpp"
#include "core/level1_companion_menu_raster.hpp"
#include "core/actor_pattern_upload.hpp"
#include "core/actor_chain_flag.hpp"
namespace rolo {
// Host publication boundary. Original palette job/interrupt timing remains
// unbound; selection, actor mutation and window boundaries use native contracts.
struct Level1MenuWorld final:CompanionMenuServices {
    Level1EnemySlice& world;CompanionMenuState menu;
    bool active{},return_map{},palette_ready{};
    std::array<std::uint8_t,65536> patterns{};
    explicit Level1MenuWorld(Level1EnemySlice& w):world(w){}
    void begin(){active=true;begin_level1_companion_menu(menu,*this);}
    void step(std::uint8_t physical){update_level1_companion_menu(menu,physical,*this);}
    void companion_menu_begin()override{
        world.input.main_state=0x1e20;palette_ready=false;install_companion_menu_patterns(patterns);
        actor_chain_flag<ActorChainFlag::clear>(world.pool,world.input.base_key); // $9514
        const auto count=world.progress.rescued_c552?0:world.progress.remaining_c556;
        if(count>99)throw std::out_of_range("Menu rescue count digits");
        std::copy_n(level1_status_hud_data::digits.begin()+(count/10)*64,64,patterns.begin()+0xb200);
        std::copy_n(level1_status_hud_data::digits.begin()+(count%10)*64,64,patterns.begin()+0xb240);
        for(const auto companion:world.companion_state.slots)if(companion)install_actor_pattern_frame(patterns,world.pool.resolve(companion));
    }
    void companion_menu_slide(std::uint16_t value)override{
        if(value!=static_cast<std::uint16_t>(0x9200|menu.slide))throw std::logic_error("Menu window boundary mismatch");
    }
    void companion_menu_palette_in()override{palette_ready=true;}
    void companion_menu_highlight()override{if(menu.selector>=6)throw std::out_of_range("Menu highlight selector");}
    bool companion_menu_select(std::uint16_t choice)override{return world.choose_companion(choice);}
    void companion_menu_accept()override{
        initialize_camera(world.camera,world.camera_input());world.stream(world.camera.foreground_x,world.camera.foreground_y);
        publish_level1_status_hud(world.status_hud,world.movement.c51d,world.score,world.progress,[&](auto command){world.sound=command;});
    }
    void companion_menu_resume()override{world.input.main_state=0x1c6c;active=false;}
    void companion_menu_sound(std::uint16_t command)override{world.sound=command;}
    void companion_menu_exit()override{return_map=true;active=false;}
    std::array<CompanionMenuPortrait,3> portraits()const{
        std::array<CompanionMenuPortrait,3> result{};
        for(unsigned slot=0;slot<3;++slot){const auto key=world.companion_state.slots[slot];if(!key)continue;
            const auto& actor=world.pool.resolve(key);result[slot]={true,actor.word(2),actor.word(36),actor.byte(39)};
        }
        return result;
    }
};
}
