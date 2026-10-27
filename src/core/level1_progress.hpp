#pragma once
#include "core/level1_reward_curve.hpp"
#include <array>
namespace rolo {
struct Level1ProgressState {
    std::array<std::uint8_t,80> flags{}; // C558, world/spawn selector indexed.
    std::uint16_t selector=1,remaining_c556{};
    std::uint8_t spawn_selector{},rescued_c552{},key_c550{},piece_c551{},exit_ready_f2bd{},action_c510{};
};
struct Level1ProgressServices:RewardCurveServices {
    virtual ActorState& progress_actor(std::uint32_t key)=0;
    virtual void progress_sound(std::uint16_t)=0;
    virtual std::uint32_t progress_spawn(std::uint32_t definition,std::uint32_t x,std::uint32_t y)=0;
    virtual void progress_hud_update()=0; // $54A0, called with C552 temporarily zero.
    virtual bool progress_exit_contact(ActorState&,std::uint16_t width_shrink,std::uint16_t height_shrink)=0;
    virtual void progress_state_transition(std::uint32_t state)=0;
    virtual void progress_music(std::uint16_t command,std::uint16_t argument)=0;
};
inline std::uint8_t& level1_progress_flag(Level1ProgressState& state,std::uint16_t selector) {
    if(selector>=state.flags.size())throw std::out_of_range("Unbound progress flag selector");
    return state.flags[selector];
}
// $D32A..$D3FE: releasing a linked companion container, including generated
// score and piece. Allocation failure does not roll back flag changes.
inline void release_level1_companion(ActorState& actor,Level1ProgressState& state,Level1ProgressServices& services) {
    services.progress_sound(27);
    const auto link=actor.longword(84);if(!link)return;
    (void)services.progress_spawn(0x140ec,actor.longword(12),actor.longword(16));
    services.progress_actor(link).longword(42,0xb7b8);
    state.remaining_c556=static_cast<std::uint16_t>(state.remaining_c556-1);
    if(!state.remaining_c556){
        auto& current=level1_progress_flag(state,state.selector);current|=2;state.rescued_c552=255;current|=8;
        // MOVE.B replaces only D0 low byte after MOVE.W selector. Keep high byte.
        const auto reward_selector=static_cast<std::uint16_t>((state.selector&0xff00)|state.spawn_selector);
        auto& reward=level1_progress_flag(state,reward_selector);const bool already=reward&1;reward|=1;
        if(!already){
            const auto key=services.progress_spawn(0x14482,actor.longword(12),actor.longword(16));
            if(key){auto& piece=services.progress_actor(key);piece.word(70,4);start_reward_curve(piece,296,41,0xffffc551,services);}
        }
    }
    if(signed_word(state.remaining_c556)<=2){
        const auto saved=state.rescued_c552;state.rescued_c552=0;
        services.progress_hud_update();state.rescued_c552=saved;
    }
}
// $9A1A..$9A5E for definition14482 when collected through its default handler.
inline void collect_level1_piece(ActorState& actor,Level1ProgressState& state,Level1ProgressServices& services) {
    services.progress_sound(64);level1_progress_flag(state,state.selector)|=8;
    const auto index=static_cast<std::uint16_t>((state.selector&0xff00)|actor.byte(50));
    level1_progress_flag(state,index)|=1;actor.word(70,4);start_reward_curve(actor,296,41,0xffffc551,services);
}
// $E528..$E5A4: exit marker readiness, blinking linked graphic and contact.
inline void update_level1_exit(ActorState& actor,Level1ProgressState& state,
        std::uint16_t blink_counter,Level1ProgressServices& services) {
    state.exit_ready_f2bd=0;const auto key=actor.longword(84);if(!key)return;
    auto& graphic=services.progress_actor(key);graphic.byte(125,graphic.byte(125)|2);
    if(!state.rescued_c552&&state.remaining_c556&&!(level1_progress_flag(state,state.selector)&8))return;
    state.exit_ready_f2bd=255;if(blink_counter&32)graphic.byte(125,graphic.byte(125)&~2u);
    if(state.action_c510||!services.progress_exit_contact(actor,20,28))return;
    services.progress_state_transition(0x1a6e);services.progress_music(23,0);
}
}
