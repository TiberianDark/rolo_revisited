#pragma once
#include "core/actor_allocation.hpp"
namespace rolo {
struct ActorReservationPool {
    struct Node {std::uint16_t next{},actor{};};
    static constexpr std::uint32_t first_key=0xffff6bbcu;
    std::array<Node,8> nodes{};
    std::array<std::uint32_t,9> free_keys{};
    std::size_t cursor{};
    std::uint16_t head{};
    Node& resolve(std::uint16_t low) {
        const auto key=0xffff0000u|low,delta=key-first_key;
        if(key<first_key||delta%4||delta/4>=nodes.size())throw std::out_of_range("Native reservation identity");
        return nodes[delta/4];
    }
    // $2888..$28B0: node contents survive initialization.
    void initialize() {
        cursor=0;head=0;
        for(std::size_t i=0;i<nodes.size();++i)free_keys[i]=first_key+static_cast<std::uint32_t>(4*i);
        free_keys.back()=0;
    }
    // $8E3A..$8E6C. Full pool leaves actor and cursor untouched.
    void reserve(ActorPool& actors,std::uint32_t identity) {
        auto& actor=actors.resolve(identity);
        if(actor.byte(126)&8)return;
        if(cursor>=free_keys.size())throw std::out_of_range("Native reservation cursor");
        const auto key=free_keys[cursor];if(!key)return;
        ++cursor;auto& node=resolve(static_cast<std::uint16_t>(key));
        node.next=head;node.actor=static_cast<std::uint16_t>(identity);
        head=static_cast<std::uint16_t>(key);actor.byte(126,static_cast<std::uint8_t>(actor.byte(126)|8));
    }
    // $8E6C..$8EAA: old bit2 decides removal, bit2 is cleared on every visit.
    void release_completed(ActorPool& actors) {
        auto* predecessor=&head;std::size_t visits=0;
        while(*predecessor) {
            if(++visits>nodes.size())throw std::logic_error("Native reservation cycle");
            const auto key=*predecessor;auto& node=resolve(key);
            auto& actor=actors.resolve(0xffff0000u|node.actor);
            const auto flags=actor.byte(126);actor.byte(126,static_cast<std::uint8_t>(flags&~4u));
            if(!(flags&4)){predecessor=&node.next;continue;}
            actor.byte(126,static_cast<std::uint8_t>(actor.byte(126)&~8u));
            *predecessor=node.next;
            if(!cursor)throw std::out_of_range("Native reservation free-stack underflow");
            free_keys[--cursor]=0xffff0000u|key;
        }
    }
};
}
