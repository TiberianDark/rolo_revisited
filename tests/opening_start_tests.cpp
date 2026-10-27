#include "core/resource_bindings.hpp"
#include "core/opening_sequence.hpp"
#include <iostream>
#include <stdexcept>

void check(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
int main(int argc,char** argv){try{
 check(argc==2,"Expected external resource folder");
 rolo::resources::initialize(argv[1]);
 for(auto phase:{rolo::OpeningSequence::Phase::EA,rolo::OpeningSequence::Phase::Copyright,
                rolo::OpeningSequence::Phase::Entrance,rolo::OpeningSequence::Phase::Photo}){
  rolo::OpeningSequence opening;
  opening.phase=phase;opening.phase_ticks=75;
  opening.colours.begin_black();
  check(!opening.press_start(),"Intro Start must not launch gameplay");
  check(opening.phase==rolo::OpeningSequence::Phase::Title,"Intro Start must reveal title");
  check(opening.phase_ticks==0,"Title prompt timer must reset");
  for(unsigned tick=0;tick<60;++tick)opening.step();
  check(opening.phase==rolo::OpeningSequence::Phase::Title,"Title must remain displayed");
  check(opening.colours.colours==rolo::opening_data::photo,"Skipped intro must retain title palette");
  check(opening.press_start(),"Start on title must allow gameplay");
 }
 rolo::OpeningSequence title;
 title.phase=rolo::OpeningSequence::Phase::Title;
 check(title.press_start(),"Naturally reached title must start on first press");
 std::cout<<"PASS: four intro phases reveal stable title, next Start launches; existing title starts immediately.\n";
 return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
