#pragma once
#include "core/object_queues.hpp"
#include "core/actor_allocation.hpp"
#include <span>
#include <vector>
namespace rolo {
inline ObjectGroup original_sprite_group(std::uint16_t tag){switch(tag){case 0x32c8:return ObjectGroup::One;case 0x34c8:return ObjectGroup::Two;case 0x36c8:return ObjectGroup::Three;case 0x38c8:return ObjectGroup::Four;case 0x3ac8:return ObjectGroup::Five;case 0x3cc8:return ObjectGroup::Six;default:throw std::out_of_range("Native sprite priority tag");}}
inline ObjectQueues build_original_sprite_priority_lists(ActorPool&pool,std::span<const std::uint32_t>active,std::uint16_t counter,std::uint16_t&status){const unsigned count=unsigned(counter)+1;if(count>48||count>active.size())throw std::out_of_range("Original sprite list extent");const auto saved=status;status=0x2700;std::vector<ActiveObject>objects;objects.reserve(count);for(unsigned i=0;i<count;++i)objects.push_back({std::uint16_t(active[i]),original_sprite_group(pool.resolve(active[i]).word(0))});auto result=build_object_queues(objects);if(!result)throw std::out_of_range("Original sprite list capacity");status=saved;return *result;}
// Extraction evidence only. This byte buffer is never executable or invoked.
inline void copy_renderer_template_metadata(std::span<const std::uint8_t>rom,std::span<std::uint8_t>target){if(rom.size()<0x31b8||target.size()<102)throw std::out_of_range("Renderer metadata extent");for(unsigned i=0;i<102;++i)target[i]=rom[0x3152+i];}
struct OriginalChecksumFailure{virtual ~OriginalChecksumFailure()=default;virtual void control_word(std::uint16_t)=0;virtual void data_word(std::uint16_t)=0;virtual void halt_after_error()=0;};
inline std::uint32_t second_rom_checksum(std::span<const std::uint8_t>rom){if(rom.size()<0x7ffb0)throw std::out_of_range("Second ROM checksum extent");std::uint32_t sum=0;for(std::size_t i=0;i<0x7ffb0;i+=4){if(i==0x18c)continue;std::uint32_t word=0;for(unsigned j=0;j<4;++j)word=(word<<8)|rom[i+j];sum+=word;}return sum;}
inline void validate_second_rom_checksum(std::span<const std::uint8_t>rom,OriginalChecksumFailure&s){if(second_rom_checksum(rom)==0x32ea75c6)return;for(auto word:{0x8f02,0x8004,0x8700,0x8144,0xc000})s.control_word(std::uint16_t(word));for(unsigned i=0;i<64;++i)s.data_word(14);s.halt_after_error();throw std::logic_error("Original checksum fault service must not return");}
}
