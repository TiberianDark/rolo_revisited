#pragma once
#include <array>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <string>
namespace rolo {
struct LocalAchievement {const char* title;const char* description;unsigned points;bool detectable;};
inline constexpr std::array<LocalAchievement,50> local_achievement_list{{
{"I'm Ready for Anything","Reach 50 lives.",25,true},
{"High Score","Reach 5,000,000 points.",10,true},
{"Rolo the Vacuuderm","Obtain and use the vacuum cleaner.",3,true},
{"Mommy the Hedgehog","Help the hedgehog mother.",10,true},
{"Tumble Dry Ro-Low","Enter the washing machine.",5,true},
{"Rolo Used Hydro Pump","Obtain the water bazooka.",3,true},
{"Forest Maze","Collect every forest map piece.",25,true},
{"Strongman Runs Away to the Circus","Defeat the strongman.",10,true},
{"When I See An Elephant FLY","Collect the high jigsaw in forest stage 3.",5,true},
{"Ranger Joe's Call of Duty","Rescue every forest animal.",25,true},
{"Featherweight","Reach the last creek platform without scoring.",10,true},
{"Oh The Huge Elephantee","Obtain helium.",4,true},
{"Using the Magic Feather","Reach the high life pickup in desert stage 2.",5,true},
{"To the Promised Land","Rescue every desert animal.",25,true},
{"Desert Fever","Collect every desert map piece.",25,true},
{"Faster than a knife!","Defeat the knife thrower.",10,true},
{"Wash This","Defeat the hurricane truck.",10,true},
{"Legendary Helmet","Equip the invulnerability helmet.",5,true},
{"Red Rolo Redemption","Rescue every Wild West animal.",25,true},
{"It's Round Up Time","Collect every Wild West map piece.",25,true},
{"Rolo to the rescue","Rescue every village animal.",25,true},
{"Modernism","Collect every village map piece.",25,true},
{"Bed Time Story","Finish with 100% completion.",50,true},
{"Bad Time Story","Finish with the bad ending.",25,true},
{"ApRollo 13","Visit the moon.",5,true},
{"Intergalactic Agent","Greet James Pond on the moon.",5,true},
{"Forest Escape","Complete the forest zone.",35,true},
{"Desert Crossing","Complete the desert zone.",35,true},
{"Westward Rolo","Complete the Wild West zone.",35,true},
{"Village Hero","Complete the village zone.",35,true},
{"Strong Without a Scratch","Defeat the strongman without damage.",40,true},
{"Knife-Proof","Defeat the knife thrower without damage.",40,true},
{"Fireproof Elephant","Defeat the fire engine without damage.",40,true},
{"Spotless Wash","Defeat the hurricane truck without damage.",40,true},
{"A Squirrel Friend","Rescue your first squirrel.",15,true},
{"A Rabbit Friend","Rescue your first rabbit.",15,true},
{"A Mole Friend","Rescue your first mole.",15,true},
{"A Beaver Friend","Rescue your first beaver.",15,true},
{"Tree Climber","Attach the squirrel to a climbable wall.",20,true},
{"High Hopper","Land 32 pixels higher using a rabbit jump.",20,true},
{"Tunnel Team","Use the mole's digging action.",20,true},
{"River Rescue","Cross between banks using the beaver.",20,true},
{"Untouchable","Finish a level without taking damage.",30,true},
{"Nothing to Declare","Finish a level without scoring.",30,true},
{"Five Alive","Finish five different levels without losing a life.",30,true},
{"Piece by Piece","Collect your first jigsaw piece.",10,true},
{"Millionaire","Reach 1,000,000 points.",15,true},
{"A Quarter Century","Reach 25 lives.",15,true},
{"Splashdown","Defeat an enemy with a water shot.",10,true},
{"On the Rails","Complete the minecart route without losing a life.",20,true},
}};

// Local native milestones, not RetroAchievements account submissions or trigger emulation.
inline constexpr unsigned achievement_count=50,achievement_pages=(achievement_count+5)/6;
using AchievementBits=std::uint64_t;
inline constexpr AchievementBits achievement_bit(unsigned i){return AchievementBits{1}<<i;}
inline constexpr AchievementBits threshold_achievements=3|achievement_bit(46)|achievement_bit(47);
struct LocalAchievements {
 AchievementBits unlocked=0,blocked=0;bool dirty=false;
 std::array<bool,80> clean_levels{};
 bool earned(unsigned i)const{return i<achievement_count&&(unlocked&achievement_bit(i));}
 unsigned count()const{unsigned n=0;for(unsigned i=0;i<achievement_count;++i)n+=earned(i);return n;}
 unsigned points()const{unsigned n=0;for(unsigned i=0;i<achievement_count;++i)if(earned(i))n+=local_achievement_list[i].points;return n;}
 void reset(){unlocked=0;blocked=threshold_achievements;clean_levels={};dirty=true;}
 void award_events(AchievementBits events){
  AchievementBits admitted=0;for(unsigned i=2;i<achievement_count;++i)if(local_achievement_list[i].detectable)admitted|=achievement_bit(i);
  const auto before=unlocked;unlocked|=events&admitted&~threshold_achievements;dirty|=before!=unlocked;
 }
 void observe(unsigned lives,std::uint32_t score){
  const auto previous=unlocked,old_blocked=blocked;AchievementBits eligible=0;
  if(lives>=50&&lives<128)eligible|=1;if(score>=5000000)eligible|=2;
  if(score>=1000000)eligible|=achievement_bit(46);if(lives>=25&&lives<128)eligible|=achievement_bit(47);
  blocked&=eligible;unlocked|=eligible&~blocked;dirty|=previous!=unlocked||old_blocked!=blocked;
 }
 void lose_life(){for(auto b:clean_levels)if(b){clean_levels={};dirty=true;break;}}
 void clean_completion(unsigned selector){if(selector>=80)return;if(!clean_levels[selector]){clean_levels[selector]=true;dirty=true;}
  unsigned n=0;for(auto b:clean_levels)n+=b;if(n>=5)award_events(achievement_bit(44));}
 bool load(const std::filesystem::path& path){
  std::ifstream in(path);std::string signature,bits,blocked_bits,levels,extra;if(!(in>>signature>>bits))return false;
  const bool modern=signature=="ROLO-LOCAL-ACHIEVEMENTS-3";const unsigned size=modern?achievement_count:26;
  if(modern||signature=="ROLO-LOCAL-ACHIEVEMENTS-2"){if(!(in>>blocked_bits))return false;}
  else if(signature=="ROLO-LOCAL-ACHIEVEMENTS-1")blocked_bits=std::string(26,'0');else return false;
  if(modern){if(!(in>>levels)||levels.size()!=80)return false;}else levels=std::string(80,'0');
  if(bits.size()!=size||blocked_bits.size()!=size||(in>>extra))return false;
  AchievementBits value=0,suppressed=0;std::array<bool,80> clean{};
  for(unsigned i=0;i<size;++i){if((bits[i]!='0'&&bits[i]!='1')||(blocked_bits[i]!='0'&&blocked_bits[i]!='1'))return false;if(bits[i]=='1')value|=achievement_bit(i);if(blocked_bits[i]=='1')suppressed|=achievement_bit(i);}
  for(unsigned i=0;i<80;++i){if(levels[i]!='0'&&levels[i]!='1')return false;clean[i]=levels[i]=='1';}
  unlocked=value;blocked=suppressed;clean_levels=clean;dirty=!modern;return true;
 }
 bool save(const std::filesystem::path&path){
  if(!dirty)return true;auto temporary=path;temporary+=".tmp";
  {std::ofstream out(temporary,std::ios::trunc);out<<"ROLO-LOCAL-ACHIEVEMENTS-3\n";for(unsigned i=0;i<achievement_count;++i)out<<(earned(i)?'1':'0');out<<'\n';for(unsigned i=0;i<achievement_count;++i)out<<((blocked&achievement_bit(i))?'1':'0');out<<'\n';for(auto b:clean_levels)out<<(b?'1':'0');out<<'\n';out.close();if(!out)return false;}
  std::error_code error;std::filesystem::rename(temporary,path,error);if(error)return false;dirty=false;return true;
 }
};
}
