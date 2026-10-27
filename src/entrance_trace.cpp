#include "core/entrance.hpp"
#include <iostream>

int main() {
    rolo::EntranceState state;
    std::cout << "tick,definition,x_fixed,y_fixed,selector,descriptor,counter,period,rng_seed,draw_x,draw_y\n";
    // $C494 starts at $352 (850). The following dispatcher enters palette/state transition.
    for (int tick=0;tick<850;++tick) {
        if (rolo::update_entrance(state)!=rolo::AnimationResult::Ok) {
            std::cerr << "Unresolved animation data at tick " << tick+1 << '\n';return 1;
        }
        for (const auto& object:state.objects) {
            const auto draw=rolo::entrance_draw(object,state);
            std::cout << state.tick << ',' << object.definition << ',' << object.x << ',' << object.y << ','
                << object.selector << ',' << rolo::entrance_data::frames[object.animation.current].descriptor << ','
                << static_cast<unsigned>(object.animation.counter) << ',' << static_cast<unsigned>(object.animation.period) << ','
                << state.random.seed << ',' << draw->x << ',' << draw->y << '\n';
        }
    }
}
