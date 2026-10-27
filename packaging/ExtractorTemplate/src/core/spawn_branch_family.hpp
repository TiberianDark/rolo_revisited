#pragma once
#include "core/actor_spawn_factory.hpp"
#include "core/spawn_branch_data.hpp"
namespace rolo {
struct SpawnBranchState {std::uint8_t c5cc{},c553{},f26f{};};
struct TriggerSpawnRequest {std::uint16_t x,row,dispatch;std::uint8_t parameter,consume;std::uint32_t marker;};
struct SpawnBranchServices {
 virtual ~SpawnBranchServices()=default;
 virtual std::uint32_t allocate(const ActorAllocationRequest&)=0;
 virtual void trigger(const TriggerSpawnRequest&)=0;
 virtual std::uint8_t progress(std::uint16_t)=0;
 virtual void actor_parameter(std::uint32_t,std::uint8_t)=0;
};
inline bool spawn_branch_suppressed(SpawnBranchState s){return !s.c5cc&&s.c553&&(s.f26f&128);}
// $466C/$4670/$4674/$4690. Immutable tables must be admitted by the caller.
inline void spawn_table_branch(unsigned kind,ActorSpawnFactoryInput input,SpawnBranchState state,
 SpawnBranchServices& services){
 if(kind!=4&&kind!=5&&kind!=6&&kind!=13)throw std::out_of_range("Spawn branch kind");
 if((kind==6||kind==13)&&spawn_branch_suppressed(state))return;
 if(kind==6||kind==13)input.parameter=static_cast<std::uint16_t>(input.parameter*2);
 std::span<const std::uint32_t> definitions;
 switch(kind){case 4:definitions=spawn_branch_data::kind4;break;case 5:definitions=spawn_branch_data::kind5;break;case 6:definitions=spawn_branch_data::kind6;break;case 13:definitions=spawn_branch_data::kind13;break;}
 services.allocate(actor_spawn_factory_request(input,definitions));
}
// $4678..$4684: original trigger allocator receives unadjusted X and row.
inline void spawn_trigger_branch(unsigned kind,ActorSpawnFactoryInput input,SpawnBranchServices& services){
 const auto parameter=static_cast<std::uint8_t>(input.parameter);std::uint16_t dispatch;std::uint8_t flags=0,consume=0;
 switch(kind){case 7:dispatch=64;flags=parameter;break;case 8:dispatch=68;flags=parameter;break;
 case 9:dispatch=68;flags=parameter;consume=255;break;case 10:dispatch=static_cast<std::uint16_t>(parameter*4);break;
 default:throw std::out_of_range("Trigger spawn kind");}
 services.trigger({input.record_x,input.row_byte_index,dispatch,flags,consume,input.marker});
}
// $4688: progress gate precedes allocation; BYTE50 changes only on success.
inline void spawn_piece_branch(ActorSpawnFactoryInput input,SpawnBranchServices& services){
 const auto parameter=input.parameter;if(services.progress(parameter)&1)return;
 constexpr std::array<std::uint32_t,1> definitions{0x14482};input.parameter=0;
 const auto actor=services.allocate(actor_spawn_factory_request(input,definitions));
 if(actor)services.actor_parameter(actor,static_cast<std::uint8_t>(parameter));
}
// Nine slot aliases below reach literal RTS bodies, with no service calls.
inline void spawn_noop_branch(){}
}
