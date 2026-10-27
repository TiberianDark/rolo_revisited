#pragma once
#include "core/actor_allocation.hpp"
#include <algorithm>
#include <vector>
namespace rolo {
// $3152/$31D6 publishes buckets32C8,34C8, then the F2D8 held actor,
// followed by36C8,38C8,3AC8,3CC8. First SAT entry wins; SDL paints reverse.
inline std::vector<std::size_t> native_actor_paint_order(const ActorPool&pool,std::uint16_t held){
 auto rank=[&](std::size_t i){if(held&&std::uint16_t(ActorPool::key(i))==held)return 2;switch(pool.actors[i].word(0)){case 0x32c8:return 0;case 0x34c8:return 1;case 0x36c8:return 3;case 0x38c8:return 4;case 0x3ac8:return 5;case 0x3cc8:return 6;default:return -1;}};
 std::vector<std::size_t> order;for(std::size_t i=0;i<pool.actors.size();++i)if(signed_word(pool.actors[i].word(0))>=0&&rank(i)>=0)order.push_back(i);
 std::sort(order.begin(),order.end(),[&](auto a,auto b){const auto x=rank(a),y=rank(b);return x==y?a>b:x>y;});return order;
}
}
