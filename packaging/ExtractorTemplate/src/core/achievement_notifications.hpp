#pragma once
#include <array>
#include "core/local_achievements.hpp"
#include <cstdint>
#include <cmath>
#include <algorithm>
namespace rolo {
struct AchievementNotifications {
 std::array<unsigned,achievement_count> queue{};unsigned read=0,write=0;AchievementBits seen=0;std::uint64_t began=0;bool active=false,started=false;
 static constexpr std::uint64_t duration=5000;
 void enqueue(AchievementBits bits,std::uint64_t now){bits&=~seen;for(unsigned i=0;i<achievement_count;++i)if(bits&(achievement_bit(i))){queue[write++%achievement_count]=i;seen|=achievement_bit(i);}update(now);}
 void update(std::uint64_t now){if(active&&now-began>=duration){active=false;++read;}if(!active&&read<write){active=true;began=now;started=true;}}
 int current(std::uint64_t now){update(now);return active?int(queue[read%achievement_count]):-1;}
 bool take_started(){const bool v=started;started=false;return v;}
};
// Original three-note UI chime, generated locally; no third-party sample asset.
struct UnlockChime {
 static constexpr unsigned rate=53267,length=36222;unsigned cursor=length;
 void trigger(){cursor=0;}
 std::int16_t sample(){if(cursor>=length)return 0;const double t=double(cursor++)/rate;double v=0;const double frequencies[]{659.255,830.609,987.767};
  for(unsigned n=0;n<3;++n){const double age=t-n*0.12;if(age<0||age>=0.42)continue;const double envelope=std::min(age/0.008,1.0)*(1-age/0.42)*(1-age/0.42);const double phase=6.283185307179586*frequencies[n]*age;v+=envelope*(std::sin(phase)+0.18*std::sin(phase*2));}
  return std::int16_t(v*1600);
 }
};
}
